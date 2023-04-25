#!/usr/bin/env python3
# by mochammad irzan m.irzan@gmail.com
import subprocess
import yaml
from jinja2 import Template
import os
import json
from passlib.hash import md5_crypt

def get_mac_fxp0(d1):
	vm = d1['vm'].keys()
	for i in vm:
		if d1['vm'][i]['type'] == 'vex':
			cmd=f"virsh dumpxml {i} | grep \"mac address\""
			a = subprocess.check_output(cmd,shell=True)
			mac = a.decode().split("\n")[0].split('=')[1].replace("'","").replace('/>',"")
			d1['vm'][i]['mac']=mac

def create_junos_config(d1):
	with open(d1['template']['junos']) as f:
		j2 = f.read()
	p1 = {}
	for i in d1['vm'].keys():
		if d1['vm'][i]['type'] == 'vex':
			p1['hostname']=i
			p1['ip_address']=f"{d1['vm'][i]['ip_address']}/{d1['ip_pool']['subnet'].split('/')[1]}"
			p1['gateway']=d1['ip_pool']['gateway']
			p1['junos_user']=d1['junos_login']['user']
			p1['junos_passwd']=md5_crypt.hash(d1['junos_login']['password'])
			config1=Template(j2).render(p1)
			if not os.path.exists(d1['DEST_DIR']):
				os.makedirs(d1['DEST_DIR'])
			else:
				if not os.path.isdir(d1['DEST_DIR']):
					os.remove(d1['DEST_DIR'])
					os.makedirs(d1['DEST_DIR'])
			filename = f"{d1['DEST_DIR']}/{i}.conf"
			with open(filename,"w") as f:
				f.write(config1)
        
def prefix2netmask(prefs):
	i=0
	b=[]
	pref = int(prefs)
	for i in range(4):
		# print("pref ",pref)
		if pref >= 8:
			b.append(255)
		elif pref >= 0:
			b1=0
			f1=7
			for j in list(range(pref)):
				b1 +=  2 ** f1
				f1 -= 1
			b.append(b1)
		else:
			b.append(0)
		pref -= 8
	return str(b[0]) + "." + str(b[1]) + "." + str(b[2]) + "." + str(b[3])

def create_dhcp_config(d1):
	with open(d1['template']['dhcp']) as f:
		j2 = f.read()
	p1 = {}
	p1['subnet'] = d1['ip_pool']['subnet'].split('/')[0]
	p1['netmask'] = prefix2netmask(d1['ip_pool']['subnet'].split('/')[1])
	p1['range_min'] = d1['ip_pool']['range']['min']
	p1['range_max'] = d1['ip_pool']['range']['max']
	p1['gateway'] = d1['ip_pool']['gateway']
	p1['option150'] = d1['ip_pool']['option-150']
	p1['vm_data'] = {}
	for i in d1['vm'].keys():
		if d1['vm'][i]['type'] == 'vex':
			p1['vm_data'].update({i : {'mac' : d1['vm'][i]['mac']}})
    #print(p1)
	config1=Template(j2).render(p1)
	if not os.path.exists(d1['DEST_DIR']):
		os.makedirs(d1['DEST_DIR'])
	else:
		if not os.path.isdir(d1['DEST_DIR']):
			os.remove(d1['DEST_DIR'])
			os.makedirs(d1['DEST_DIR'])
	filename = f"{d1['DEST_DIR']}/dhcpd.conf"
	with open(filename,"w") as f:
		f.write(config1)

def junos_config(d1):
    f1=[]
    for i in d1['vm'].keys():
        f1.append(f"{i}.conf")
    return ','.join(f1)

def print_syntax():
	print("usage : vlab.py <command>")
	print("commands are : ")
	print("  addbr     : create linux bridge for VM interconnectivity ")
	print("  create    : to create VMs on the hypervisor")
	print("  start     : to start VMs on the hypervisor")
	print("  config    : create configuration for DHCPD and TFTPD")

def create_config(d1):
	#print(d1)
	print("getting mac address info")
	get_mac_fxp0(d1)
	#print(d1)
	print("writing junos config")
	create_junos_config(d1)
	print("Creating dhcpd config")
	create_dhcp_config(d1)
	print("files are created on directory ./result")
	print("upload file dhcpd.conf into dhcp server /etc/dhcpd/dhcpd.conf")
	print(f"upload junos configuration files ({junos_config(d1)}), into root directory of tftp server")
	print("Adding entries into  file ~/.ssh/config")
	add_to_ssh_config(d1)

def check_argv(argv):
	retval={}
	cmd_list=['addbr','create','start','config','del','stop','test','delbr']
	if len(argv) == 1:
		print_syntax()
	else:
		if not os.path.isfile("./lab.yaml"):
			print("file lab.conf doesn't exist, please create one or define another file for configuration")
		else:
			if argv[1] not in cmd_list:
				print_syntax()
			else:
				with open("lab.yaml") as f:
					vm = f.read()	
				retval = yaml.load(vm,Loader=yaml.FullLoader)
				retval['cmd'] = argv[1]
				t1 = argv[0].split('/')
				t2 = t1.pop()
				retval['template']={
							'junos':f"{'/'.join(t1)}/junos.j2",
							'dhcp':f"{'/'.join(t1)}/dhcpd.j2"
				}
				retval['DEST_DIR'] = './result'

	return retval

def is_vm_defined(d1):
	t1 = []
	for i in d1['vm'].keys():
		#if d1['vm'][i]['type'] == 'vex':
		t1.append(i)
	list_vm1=set(t1)
	cmd="virsh list --all"
	a = subprocess.check_output(cmd,shell=True)
	# vm = a.decode().split("\n")[0].split('=')[1].replace("'","").replace('/>',"")
	t1 = a.decode().split("\n")[2:]
	#print("list vm1 ",list_vm1)
	list_vm2=[]
	for i in t1:
		if i:
			list_vm2.append(i.strip().split()[1])
		#list_vm2.append(i.strip().split())
	#print("list_vm2 ",list_vm2)
	t2=[]
	for i in list_vm1:
		if i in list_vm2:
			t2.append(i)
	vm_ok = set(t2)
	retval = list_vm1 == vm_ok
	if not retval:
		diff1 = list(list_vm1.difference(vm_ok))
		#print(diff1)
		d1['vm_not_defined']=diff1
	else:
		d1['vm_not_defined']=[]
	return retval

def list_of_bridge(d1):
	list_bridge=[]
	for i in d1['vm'].keys():
		for j in d1['vm'][i]['port'].values():
			#print(j)
			if j not in list_bridge:
				list_bridge.append(j)
	return list_bridge

def is_bridge_defined(d1):
	cmd="ip --json link list type bridge"
	t1 = json.loads(subprocess.check_output(cmd,shell=True).decode())
	#t2 = json.loads(t1)
	#print(t1)
	#print(type(t1))
	d1['bridge_not_defined']=[]
	t2=list_of_bridge(d1)
	if not t1:
		d1['bridge_not_defined'] = t2
	else:
		t3 = []
		for i in t1:
			if 'ifname' in i.keys():
				t3.append(i['ifname'])
		for i in t2:
			if i not in t3:
				d1['bridge_not_defined'].append(i)	
		#print(t2)
	#print(d1['bridge_not_defined'])
		# print("t3 ",t3)
		# st2=set(t2)
		# st3=set(t3)
		# #print("st2 ",st2)
		# #print("st3 ",st3)
		# d1['bridge_not_defined'] = st3.difference(st2)

def add_bridge(d1):
	if d1['bridge_not_defined']:
		#print(f"bridges {d1['bridge_not_defined']}")
		print("starting the bridges")
		for i in d1['bridge_not_defined']:
			cmd = f"sudo ip link add dev {i} type bridge"
			subprocess.check_output(cmd,shell=True)
			# this is to hack the linux kernel to allow LLDP and LACP frame to be forwarded.
			# it can only works with modified linux kernel.
			cmd = f"echo 0x400c | sudo tee  /sys/class/net/{i}/bridge/group_fwd_mask"
			subprocess.check_output(cmd,shell=True)
			cmd = f"sudo ip link set dev {i} up"
			subprocess.check_output(cmd,shell=True)
	else:
		print("bridges are defined")

def del_bridge(d1):
	print("deleting bridge the bridges")
	list_bridge = list_of_bridge(d1)
	if 'bridge_not_defined' in d1.keys():
		not_defined = d1['bridge_not_defined']
	for i in list_bridge:
		if i not in not_defined:
			cmd = f"sudo ip link set dev {i} down"
			subprocess.check_output(cmd,shell=True)
			cmd = f"sudo ip link del dev {i} "
			subprocess.check_output(cmd,shell=True)

def define_vm(d1):
	if d1['vm_not_defined']:
		print("defining VM")
		for i in d1['vm_not_defined']:
			disk = d1['vm_dir'] + f"/{i}.img"
			disk_type = d1['vm'][i]['type']
			cmd = f"cp {d1['disk'][disk_type]} {disk}"
			print(f"copying file from {d1['disk'][disk_type]} to {disk}")
			subprocess.check_output(cmd,shell=True)
			if d1['vm'][i]['type'] == 'vex':
				cmd=f"""virt-install --name {i} --disk {disk},device=disk \
--cpu IvyBridge,+vmx --sysinfo system.product="VM-VEX" \
--ram 5120 --vcpu 4  \
--osinfo ubuntu22.04 """
				if d1['mgmt']['type'] == 'ovs':
					cmd += f"--network bridge={d1['mgmt']['bridge']},virtualport_type=openvswitch "
				else:
					cmd += f"--network bridge={d1['mgmt']['bridge']} "
				port = list(d1['vm'][i]['port'].keys())
				port.sort()
				for j in port:
					cmd += f"--network bridge={d1['vm'][i]['port'][j]} "
				cmd += f"--xml './devices/interface[1]/target/@dev={i}fxp0' "
				if 'vlan' in d1['mgmt'].keys():
					cmd += f"--xml './devices/interface[1]/vlan/tag/@id={d1['mgmt']['vlan']}' "
				k = 2
				l=0
				for j in port:
					cmd += f"--xml './devices/interface[{k}]/target/@dev={i}ge{l}' "
					cmd += f"--xml './devices/interface[{k}]/mtu/@size=9500' "
					k+=1
					l+=1
				cmd2 = """--console pty,target_type=serial \
--noautoconsole --hvm --accelerate  --vnc \
--virt-type=kvm --boot hd --noreboot"""
				cmd += cmd2
			elif d1['vm'][i]['type'] == 'alpine':
				cmd=f"""virt-install --name {i} --disk {disk},device=disk \
--ram 512 --vcpu 1 --osinfo alpinelinux3.15 \
	"""
				port = list(d1['vm'][i]['port'].keys())
				port.sort()
				for j in port:
					cmd += f"--network bridge={d1['vm'][i]['port'][j]},model=e1000 "
				cmd2 = """--console pty,target_type=serial \
--noautoconsole --hvm --accelerate  --vnc \
--virt-type=kvm --boot hd --noreboot"""
				cmd += cmd2
			elif d1['vm'][i]['type'] == 'ubuntu':
				cmd=f"""virt-install --name {i} --disk {disk},device=disk \
--ram 2048 --vcpu 1 --osinfo ubuntu22.04 \
	"""
				port = list(d1['vm'][i]['port'].keys())
				port.sort()
				for j in port:
					cmd += f"--network bridge={d1['vm'][i]['port'][j]},model=e1000 "
				cmd2 = """--console pty,target_type=serial \
--noautoconsole --hvm --accelerate  --vnc \
--virt-type=kvm --boot hd --noreboot"""
				cmd += cmd2
			print(f"installing VM {i} on the hypervisor")
			subprocess.check_output(cmd,shell=True)
	else:
		print("VMs are defined")


def create_vm(d1):
	print("add VMs to hypervisor")
	# is_bridge_defined(d1)
	if d1['bridge_not_defined']:
		print("not ok")
		print(f"these {d1['bridge_not_defined']} are not defined")
		add_bridge(d1)
	else:
		print("bridges are OK")
	# is_vm_defined(d1)
	if d1['vm_not_defined']:
		print("not ok")
		print(f"these {d1['vm_not_defined']} are not defined")
		define_vm(d1)
	else:
		print("VMs are OK")
	

def start_vm(d1):
	if d1['vm_not_defined']:
		add_bridge(d1)
		define_vm(d1)
	print("start VMs on hypervisor")
	for i in d1['vm'].keys():
		print(f"starting {i}")
		cmd = f"virsh start {i}"
		subprocess.check_output(cmd,shell=True)

def stop_vm(d1):
	print("stop VMs on hypervisor")
	for i in d1['vm'].keys():
		print(f"stopping {i}")
		cmd = f"virsh destroy {i}"
		subprocess.check_output(cmd,shell=True)

def delete_vm(d1):
	print("stopping VMs on hypervisor")
	for i in d1['vm'].keys():
		print(f"stop vm {i}")
		#cmd = f"virsh destroy {i}"
		#subprocess.check_output(cmd,shell=True)
		cmd = f"virsh undefine {i}"
		subprocess.check_output(cmd,shell=True)
		disk = d1['vm_dir'] + f"/{i}.img"
		print(f"deleting disk {disk}")
		cmd = f"rm {disk}"
		subprocess.check_output(cmd,shell=True)
	del_bridge(d1)

def create_ssh_config(d1):
	list_vm=[]
	new_ssh_config=[]
	for i in d1['vm'].keys():
		if d1['vm'][i]['type'] in 'vex':
			list_vm.append(i)
	# print("list of vm ",list_vm)
	new_ssh_config.append("### add by vlab.py script ###")
	for i in list_vm:
		new_ssh_config.append(f"Host {i}")
		new_ssh_config.append(f"  hostname {d1['vm'][i]['ip_address']}")
		new_ssh_config.append(f"  user {d1['junos_login']['user']}")
	return new_ssh_config

def add_to_ssh_config(d1):
	ssh_config = os.path.expanduser("~/.ssh/config")
	print("add to ssh_config")
	print(ssh_config)
	add_ssh_config=create_ssh_config(d1)
	with open(ssh_config) as f1:
		r1 = f1.read()
	r1_l = r1.split('\n')
	new_ssh_config=[]
	for i in r1_l:
		if i == "### add by vlab.py script ###":
			break
		else:
			new_ssh_config.append(i)
	new_ssh_config += add_ssh_config
	with open(ssh_config,"w") as f1:
		wr = '\n'.join(new_ssh_config)
		f1.write(wr)
