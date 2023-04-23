#!/usr/bin/env python3
import subprocess
import yaml
from jinja2 import Template
import os

DEST_DIR='./result'
def get_mac_fxp0(d1):
    vm = d1['vm'].keys()
    if d1['vm'][i]['type'] == 'vex':
        for i in vm:
		cmd=f"virsh dumpxml {i} | grep \"mac address\""
		a = subprocess.check_output(cmd,shell=True)
		mac = a.decode().split("\n")[0].split('=')[1].replace("'","").replace('/>',"")
		d1['vm'][i]['mac']=mac



def create_junos_config(d1):
    with open(d1['junos_template']) as f:
        j2 = f.read()
    p1 = {}
    for i in d1['vm'].keys():
		if d1['vm'][i]['type'] == 'vex':
			p1['hostname']=i
			p1['ip_address']=f"{d1['vm'][i]['ip_address']}/{d1['ip_pool']['subnet'].split('/')[1]}"
			p1['gateway']=d1['ip_pool']['gateway']
			config1=Template(j2).render(p1)
			if not os.path.exists(DEST_DIR):
				os.makedirs(DEST_DIR)
			else:
				if not os.path.isdir(DEST_DIR):
					os.remove(DEST_DIR)
					os.makedirs(DEST_DIR)
			filename = f"{DEST_DIR}/{i}.conf"
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
    with open(d1['dhcp_template']) as f:
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
        p1['vm_data'].update({i : {'mac' : d1['vm'][i]['mac']}})
    #print(p1)
    config1=Template(j2).render(p1)
    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)
    else:
        if not os.path.isdir(DEST_DIR):
            os.remove(DEST_DIR)
            os.makedirs(DEST_DIR)
    filename = f"{DEST_DIR}/dhcpd.conf"
    with open(filename,"w") as f:
        f.write(config1)
    #print(config1)
    #print(p1)

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

def create_dhcp_tftp_config(d1):
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

def check_argv(argv):
	retval={}
	cmd_list=['addbr','create','start','config']
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
				retval['junos_template'] = '/'.join(t1) + '/' + retval['junos_template'] 
				retval['dhcp_template'] = '/'.join(t1) + '/' + retval['dhcp_template'] 

	return retval

def add_bridge(d1):
	print("starting the bridges")

def create_vm(d1):
	print("add VMs to hypervisor")

def start_vm(d1):
	print("start VMs on hypervisor")