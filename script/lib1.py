#!/usr/bin/env python3
# by mochammad irzan m.irzan@gmail.com
import subprocess
import yaml
from jinja2 import Template
import os
import json
from passlib.hash import md5_crypt
import xmltodict
import pprint


def set_bridge(d1):
	t1 = d1['vm'].keys()
	vm = []
	intf_list=[]
	bridge_list=[]
	for i in t1:
		if d1['vm'][i]['type'] in ['vjunosswitch','vjunosevolved','vjunosrouter','sonic']:
			vm.append(i)
	for i in vm:
		cmd = f"virsh domiflist {i} | tail -n +4"
		result = subprocess.check_output(cmd,shell=True)
		#print(f"VM {i}")
		lines = result.decode().split('\n')
		for x in lines:
			t1 = x.lstrip().split()
			if t1:
				#print(f"interface {t1[0]}, bridge {t1[2]}")
				if t1[0] not in intf_list:
					intf_list.append(t1[0])
				if t1[2] not in bridge_list:
					bridge_list.append(t1[2])

	# print(f"interface {intf_list}")
	# print(f"bridge {bridge_list}")
	# check intf_list
	new_intf_list=[]
	for i in intf_list:
		file1=f"/sys/class/net/{i}/brport/group_fwd_mask"
		if os.path.exists(file1):
			new_intf_list.append(i)
	new_bridge_list=[]
	for i in bridge_list:
		br1 = f"/sys/class/net/{i}/bridge/group_fwd_mask"
		if os.path.exists(br1):
			new_bridge_list.append(i)

	for i in new_intf_list:
		print(f"setting interface {i}")
		cmd=f"echo 16388 | sudo tee /sys/class/net/{i}/brport/group_fwd_mask"
		result = subprocess.check_output(cmd,shell=True)
	for i in new_bridge_list:
		print(f"setting bridge {i}")
		cmd=f"echo 65528 | sudo tee /sys/class/net/{i}/bridge/group_fwd_mask"
		result = subprocess.check_output(cmd,shell=True)

			
def get_mac_fxp0(d1):
	vm = d1['vm'].keys()
	for i in vm:
		if d1['vm'][i]['type'] in ['vjunosswitch','vjunosevolved','vjunosrouter','sonic','ubuntu']:
			#print(f"vm {i}")
			cmd=f"virsh dumpxml {i} | grep \"mac address\""
			a = subprocess.check_output(cmd,shell=True)
			mac = a.decode().split("\n")[0].split('=')[1].replace("'","").replace('/>',"")
			print(f"vm {i} mac {mac}")
			d1['vm'][i]['mac']=mac

def create_junos_config(d1):
	with open(d1['template']['junos']) as f:
		j2 = f.read()
	p1 = {}
	for i in d1['vm'].keys():
		if d1['vm'][i]['type'] in ['vjunosswitch','vjunosevolved','vjunosrouter']:
			p1['hostname']=i
			p1['type']= d1['vm'][i]['type']
			p1['ip_address']=f"{d1['vm'][i]['ip_address']}/{d1['ip_pool']['subnet'].split('/')[1]}"
			p1['gateway']=d1['ip_pool']['gateway']
			p1['junos_user']=d1['junos_login']['user']
			p1['junos_passwd']=md5_crypt.hash(d1['junos_login']['password'])
			config1=Template(j2).render(p1)
			if not os.path.exists(d1['DEST_DIR']):
				os.makedirs(d1['DEST_DIR'])
			# else:
			# 	if not os.path.isdir(d1['DEST_DIR']):
			# 		os.remove(d1['DEST_DIR'])
			# 		os.makedirs(d1['DEST_DIR'])
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
		if d1['vm'][i]['type'] in  ['vjunosswitch','vjunosevolved','vjunosrouter','sonic','ubuntu']:
			if d1['vm'][i]['type'] == 'sonic':
				p1['vm_data'].update({i : {'hostname': i,'mac' : d1['vm'][i]['mac'],'ip' : d1['vm'][i]['ip_address'],'conf' : 0}})
			else:
				p1['vm_data'].update({i : {'hostname': i,'mac' : d1['vm'][i]['mac'],'ip' : d1['vm'][i]['ip_address'],'conf' : 1}})
    #print(p1)
	config1=Template(j2).render(p1)
	if not os.path.exists(d1['DEST_DIR']):
		os.makedirs(d1['DEST_DIR'])
	# else:
	# 	if not os.path.isdir(d1['DEST_DIR']):
	# 		os.remove(d1['DEST_DIR'])
	# 		os.makedirs(d1['DEST_DIR'])
	filename = f"{d1['DEST_DIR']}/dhcpd.conf"
	with open(filename,"w") as f:
		f.write(config1)

def create_apstra_dhcp_config(d1):
	with open(d1['template']['apstra_ztp']) as f:
		j2 = f.read()
	p1 = {}
	p1['subnet'] = d1['ip_pool']['subnet'].split('/')[0]
	p1['netmask'] = prefix2netmask(d1['ip_pool']['subnet'].split('/')[1])
	p1['range_min'] = d1['ip_pool']['range']['min']
	p1['range_max'] = d1['ip_pool']['range']['max']
	p1['gateway'] = d1['ip_pool']['gateway']
	p1['ztp_server'] = d1['ip_pool']['option-150']
	p1['host'] = {}
	for i in d1['vm'].keys():
		if d1['vm'][i]['type'] in  ['vjunosswitch','vjunosevolved']:
			p1['host'].update({i : {'mac' : d1['vm'][i]['mac'],'ip' : d1['vm'][i]['ip_address']}})
    #print(p1)
	config1=Template(j2).render(p1)
	if not os.path.exists(d1['DEST_DIR']):
		os.makedirs(d1['DEST_DIR'])
	# else:
	# 	if not os.path.isdir(d1['DEST_DIR']):
	# 		os.remove(d1['DEST_DIR'])
	# 		os.makedirs(d1['DEST_DIR'])
	filename = f"{d1['DEST_DIR']}/ztp_config.txt"
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
	create_apstra_dhcp_config(d1)
	print("files are created on directory ./result")
	print("upload file dhcpd.conf into dhcp server /etc/dhcpd/dhcpd.conf")
	print(f"upload junos configuration files ({junos_config(d1)}), into root directory of tftp server")
	#print("Adding entries into  file ~/.ssh/config")
	#add_to_ssh_config(d1)

def check_argv(argv):
	retval={}
	cmd_list=['addbr','create','start','config','del','stop','test','delbr','printdata','setbr','listbr']
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
					d1 = f.read()	
				retval = yaml.load(d1,Loader=yaml.FullLoader)
				retval['cmd'] = argv[1]
				t1 = argv[0].split('/')
				_ = t1.pop()
				retval['template']={
							'junos':f"{'/'.join(t1)}/junos.j2",
							'dhcp':f"{'/'.join(t1)}/dhcpd.j2",
							'vjunosswitch':f"{'/'.join(t1)}/vjunosswitch.j2",
							'vjunosrouter':f"{'/'.join(t1)}/vjunosrouter.j2",
							'sonic':f"{'/'.join(t1)}/sonic.j2",
							'ubuntu': f"{'/'.join(t1)}/ubuntu.j2",
							'alpine': f"{'/'.join(t1)}/alpine.j2",
							'vjunosevolved':f"{'/'.join(t1)}/vjunosevolved.j2",
							'apstra_ztp':f"{'/'.join(t1)}/apstra_ztp.j2"
				}
				retval['DEST_DIR'] = './result'
				## checking if vjunosevolved is defined ?
				for i in retval['vm'].keys():
					if retval['vm'][i]['type'] == "vjunosevolved":
						if 'vevo_old' in retval['vm'][i].keys(): 
							temp_port = retval['vm'][i]['port']
							retval['vm'][i]['port']={
								'p1': f"{i}PFE",
								'p2': f"{i}RPIO",
								'p3': f"{i}RPIO",
								'p4': f"{i}PFE"
							}
							retval['vm'][i]['port'].update(temp_port)
				if 'ovs' not in retval.keys():
					retval['ovs']=[]
				if 'type' in retval['mgmt'].keys():
					if retval['mgmt']['type'] == 'ovs':
						retval['ovs'].append(retval['mgmt']['bridge'])
	return retval

def printdata(d1):
	d2 = yaml.dump(d1)
	print(d2)

def is_vm_defined(d1):
	t1 = []
	for i in d1['vm'].keys():
		#if d1['vm'][i]['type'] == 'vjunosswitch':
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


def list_bridge(d1):
	cmd="ip --json link list type bridge"
	t1 = json.loads(subprocess.check_output(cmd,shell=True).decode())
	list_br=[]
	for i in t1:
		list_br.append(i['ifname'])
	cmd="ip --json link list type openvswitch"
	t1 = json.loads(subprocess.check_output(cmd,shell=True).decode())
	for i in t1:
		list_br.append(i['ifname'])
	pprint.pprint(list_br)
def is_bridge_defined(d1):
	# cmd="ip --json link list type bridge"
	# t1 = json.loads(subprocess.check_output(cmd,shell=True).decode())
	#t2 = json.loads(t1)
	#print(t1)
	#print(type(t1))
	cmd="ip --json link list type bridge"
	t1 = json.loads(subprocess.check_output(cmd,shell=True).decode())
	list_br=[]
	for i in t1:
		list_br.append(i['ifname'])
	cmd="ip --json link list type openvswitch"
	t1 = json.loads(subprocess.check_output(cmd,shell=True).decode())
	for i in t1:
		list_br.append(i['ifname'])
	d1['bridge_not_defined']=[]
	t2=list_of_bridge(d1)
	if not t1:
		d1['bridge_not_defined'] = t2
	else:
		# t3 = []
		# for i in t1:
		# 	if 'ifname' in i.keys():
		# 		t3.append(i['ifname'])
		for i in t2:
			if i not in list_br:
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
			if i not in d1['ovs']:
				cmd = f"sudo ip link add dev {i} type bridge"
				subprocess.check_output(cmd,shell=True)
				# this is to hack the linux kernel to allow LLDP and LACP frame to be forwarded.
				# it can only works with modified linux kernel.
				# cmd = f"echo 0x400c | sudo tee  /sys/class/net/{i}/bridge/group_fwd_mask"
				# subprocess.check_output(cmd,shell=True)
				cmd = f"sudo ip link set dev {i} up"
				subprocess.check_output(cmd,shell=True)
				cmd = f"sudo sysctl -w \"net.ipv6.conf.{i}.disable_ipv6=1\""
				subprocess.check_output(cmd,shell=True)
			else:
				cmd = f"sudo ovs-vsctl add-br {i}"
				subprocess.check_output(cmd,shell=True)
				cmd = f"sudo sysctl -w \"net.ipv6.conf.{i}.disable_ipv6=1\""
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
			if i not in d1['ovs']:
				cmd = f"sudo ip link set dev {i} down"
				subprocess.check_output(cmd,shell=True)
				cmd = f"sudo ip link del dev {i} "
				subprocess.check_output(cmd,shell=True)
			else:
				cmd = f"sudo ovs-vsctl del-br {i}"
				subprocess.check_output(cmd,shell=True)

def define_vm(d1):
	if d1['vm_not_defined']:
		print("defining VM")
		for i in d1['vm_not_defined']:
			if not os.path.exists(d1['vm_dir']):
				os.makedirs(d1['vm_dir'])
			disk = d1['vm_dir'] + f"/{i}.img"
			disk_type = d1['vm'][i]['type']
			# cmd = f"cp {d1['disk'][disk_type]} {disk}"
			cmd = f"qemu-img create -b {d1['disk'][disk_type]} -f qcow2 -F qcow2 {disk}"
			print(f"copying file from {d1['disk'][disk_type]} to {disk}")
			data1={}
			subprocess.check_output(cmd,shell=True)
			if d1['vm'][i]['type'] in  ['vjunosswitch','vjunosrouter']:
				#cmd="virsh capabilities"
				#cpu_model = xmltodict.parse(subprocess.check_output(cmd,shell=True).decode())['capabilities']['host']['cpu']['model'].split("-")[0]
				cpu_model = "IvyBridge"
				vm_type = d1['vm'][i]['type']
				data1['name']=i
				data1['disk']=disk
				data1['vcpu']=4
				data1['ram']=5120
				data1['cpu_model']=cpu_model
				data1['interfaces']={}
				if 'type' in d1['mgmt'].keys():
					if d1['mgmt']['type'] == 'ovs':
						if 'vlan' in d1['mgmt'].keys():
							vlantemp = d1['mgmt']['vlan']
						else:
							vlantemp = 0
						data1['interfaces']['mgmt']={
							'bridge' : d1['mgmt']['bridge'],
							'index' : 1,
							'vlan': vlantemp,
							'ovs': '1' 
						} 
				else:
					data1['interfaces']['mgmt']={
						'bridge' : d1['mgmt']['bridge'],
						'index' : 1,
						'ovs':0
					}
				p=2
				ports= list(d1['vm'][i]['port'].keys())
				_ =ports.sort()
				for j in ports:
					t1=f"ge{j.split('/')[2]}"
					if d1['vm'][i]['port'][j] in d1['ovs']:
						data1['interfaces'][t1]={'bridge':d1['vm'][i]['port'][j],'index':p,'ovs':1}
					else:
						data1['interfaces'][t1]={'bridge':d1['vm'][i]['port'][j],'index':p,'ovs':0}
					p+=1
				pprint.pprint(data1)
				with open(d1['template'][vm_type]) as f1:
					template1 = f1.read()
					cmd=Template(template1).render(data1)
			elif d1['vm'][i]['type'] in  ['sonic']:
				#cmd="virsh capabilities"
				#cpu_model = xmltodict.parse(subprocess.check_output(cmd,shell=True).decode())['capabilities']['host']['cpu']['model'].split("-")[0]
				cpu_model = "IvyBridge"
				vm_type = d1['vm'][i]['type']
				data1['name']=i
				data1['disk']=disk
				data1['vcpu']=4
				data1['ram']=4096
				# data1['cpu_model']=cpu_model
				data1['interfaces']={}
				if 'type' in d1['mgmt'].keys():
					if d1['mgmt']['type'] == 'ovs':
						if 'vlan' in d1['mgmt'].keys():
							vlantemp = d1['mgmt']['vlan']
						else:
							vlantemp = 0
						data1['interfaces']['mgmt']={
							'bridge' : d1['mgmt']['bridge'],
							'index' : 1,
							'vlan': vlantemp,
							'ovs': '1' 
						} 
				else:
					data1['interfaces']['mgmt']={
						'bridge' : d1['mgmt']['bridge'],
						'index' : 1,
						'ovs':0
					}
				p=2
				ports= list(d1['vm'][i]['port'].keys())
				_ =ports.sort()
				for j in ports:
					#t1=sonic_port(j)
					t1 = j
					if d1['vm'][i]['port'][j] in d1['ovs']:
						data1['interfaces'][t1]={'bridge':d1['vm'][i]['port'][j],'index':p,'ovs':1}
					else:
						data1['interfaces'][t1]={'bridge':d1['vm'][i]['port'][j],'index':p,'ovs':0}
					p+=1
				pprint.pprint(data1)
				with open(d1['template'][vm_type]) as f1:
					template1 = f1.read()
					cmd=Template(template1).render(data1)
			elif d1['vm'][i]['type'] == 'vjunosevolved':
				disk_cfg = d1['vm_dir'] + f"/{i}_cfg.img"
				cmd = f"cp {d1['disk']['vjunosevolved_config']} {disk_cfg}"
				print(f"copying file from {d1['disk']['vjunosevolved_config']} to {disk_cfg}")
				subprocess.check_output(cmd,shell=True)
				cmd="virsh capabilities"
				#cpu_model = xmltodict.parse(subprocess.check_output(cmd,shell=True).decode())['capabilities']['host']['cpu']['model'].split("-")[0]
				cpu_model = "IvyBridge"
				data1['name']=i
				data1['disk']=disk
				data1['disk_config']=disk_cfg
				data1['vcpu']=4
				data1['ram']=8192
				data1['cpu_model']=cpu_model
				data1['interfaces']={}
				if 'type' in d1['mgmt'].keys():
					if d1['mgmt']['type'] == 'ovs':
						if 'vlan' in d1['mgmt'].keys():
							vlantemp = d1['mgmt']['vlan']
						else:
							vlantemp = 0
						data1['interfaces']['mgmt']={
							'bridge' : d1['mgmt']['bridge'],
							'index' : 1,
							'vlan': vlantemp,
							'ovs': '1' 
						} 
				else:
					data1['interfaces']['mgmt']={
						'bridge' : d1['mgmt']['bridge'],
						'index' : 1,
						'ovs':0
					}
				# data1['interfaces']['mgmt']={
				# 	'bridge' : d1['mgmt']['bridge'],
				# 	'index' : 1,
				# 	'vlan': d1['mgmt']['vlan'],
				# 	'ovs': '1'
				# }
				# data1['interfaces']['mgmt']={
				# 	'bridge' : d1['mgmt']['bridge'],
				# 	'index' : 1,
				# 	'ovs':0
				# }
				p=2
				ports= list(d1['vm'][i]['port'].keys())
				#_ =ports.sort()
				#print(ports)
				for j in ports:
					if j in ['p1','p2','p3','p4']:
						data1['interfaces'][j]={'bridge':d1['vm'][i]['port'][j],'index':p}	
					else:
						t1=f"et{j.split('/')[2]}"
						# data1['interfaces'][t1]={'bridge':d1['vm'][i]['port'][j],'index':p}
						if d1['vm'][i]['port'][j] in d1['ovs']:
							data1['interfaces'][t1]={'bridge':d1['vm'][i]['port'][j],'index':p,'ovs':1}
						else:
							data1['interfaces'][t1]={'bridge':d1['vm'][i]['port'][j],'index':p,'ovs':0}
					p+=1
				# for j in ports:
				# 	t1=f"ge{j.split('/')[2]}"
				# 	if d1['vm'][i]['port'][j] in d1['ovs']:
				# 		data1['interfaces'][t1]={'bridge':d1['vm'][i]['port'][j],'index':p,'ovs':1}
				# 	else:
				# 		data1['interfaces'][t1]={'bridge':d1['vm'][i]['port'][j],'index':p,'ovs':0}
				# 	p+=1
				#print(data1)
				with open(d1['template']['vjunosevolved']) as f1:
					template1 = f1.read()
					cmd=Template(template1).render(data1)
			elif d1['vm'][i]['type'] == 'alpine':
				data1['name']=i
				data1['disk']=disk
				data1['vcpu']=1
				data1['ram']=512
				data1['interfaces']={}
				ports= list(d1['vm'][i]['port'].keys())
				#_ =ports.sort()
				for j in ports:
					data1['interfaces'][j]={'bridge':d1['vm'][i]['port'][j]}
				with open(d1['template']['alpine']) as f1:
					template1 = f1.read()
					cmd=Template(template1).render(data1)
			elif d1['vm'][i]['type'] == 'ubuntu':
				data1['name']=i
				data1['disk']=disk
				data1['vcpu']=2
				data1['ram']=4096
				# data1['interfaces']={}
				# ports= list(d1['vm'][i]['port'].keys())
				# _ =ports.sort()
				# for j in ports:
				# 	data1['interfaces'][j]={'bridge':d1['vm'][i]['port'][j]}
				# new section
				data1['interfaces']={}
				if 'type' in d1['mgmt'].keys():
					if d1['mgmt']['type'] == 'ovs':
						if 'vlan' in d1['mgmt'].keys():
							vlantemp = d1['mgmt']['vlan']
						else:
							vlantemp = 0
						data1['interfaces']['mgmt']={
							'bridge' : d1['mgmt']['bridge'],
							'index' : 1,
							'vlan': vlantemp,
							'ovs': '1' 
						} 
				else:
					data1['interfaces']['mgmt']={
						'bridge' : d1['mgmt']['bridge'],
						'index' : 1,
						'ovs':0
					}
				p=2
				ports= list(d1['vm'][i]['port'].keys())
				_ =ports.sort()
				for j in ports:
					#t1=sonic_port(j)
					t1 = j
					if d1['vm'][i]['port'][j] in d1['ovs']:
						data1['interfaces'][t1]={'bridge':d1['vm'][i]['port'][j],'index':p,'ovs':1}
					else:
						data1['interfaces'][t1]={'bridge':d1['vm'][i]['port'][j],'index':p,'ovs':0}
					p+=1
				# end of new section
				with open(d1['template']['ubuntu']) as f1:
					template1 = f1.read()
					cmd=Template(template1).render(data1)
			print(f"installing VM {i} on the hypervisor")
			#print(cmd)
			subprocess.check_output(cmd,shell=True)
	else:
		print("VMs are defined")

def sonic_port(p1):
	if p1 == 'eth0':
		p2 = 'em1'
	elif p1 == 'eth4':
		p2 = 'em2'
	elif p1 == 'eth8':
		p2 = 'em3'
	elif p1 == 'eth12':
		p2 = 'em4'
	elif p1 == 'eth16':
		p2 = 'em5'
	elif p1 == 'eth20':
		p2 = 'em6'
	elif p1 == 'eth24':
		p2 = 'em7'
	elif p1 == 'eth28':
		p2 = 'em8'
	elif p1 == 'eth32':
		p2 = 'em9'
	elif p1 == 'eth36':
		p2 = 'em10'
	else:
		p2 = "em100"
	return p2

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
	print("deleting VMs on hypervisor")
	#stop_vm(d1)
	for i in d1['vm'].keys():
		print(f"stop vm {i}")
		#cmd = f"virsh destroy {i}"
		#subprocess.check_output(cmd,shell=True)
		cmd = f"virsh undefine --nvram {i}"
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
		if d1['vm'][i]['type'] in 'vjunosswitch':
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
