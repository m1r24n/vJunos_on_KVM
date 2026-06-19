#!/usr/bin/env python3
# by mochammad irzan m.irzan@gmail.com
import subprocess
import yaml
from jinja2 import Template
import os
import json
from passlib.hash import md5_crypt
from pathlib import Path
import xmltodict
import pprint
import pathlib
import shutil
import requests, urllib3
from jnpr.junos import Device
from lxml import etree

urllib3.disable_warnings()

def check_config(d1):
    if 'fabric' in d1.keys():
        num_link = len(d1['fabric']['topology'])
        # set bridge
        for i in range(num_link):
            br='ptp' + str(i)
            d1['fabric']['topology'][i].append(br)
        #pprint.pprint(d1['fabric']['topology'])
        for i in d1['fabric']['topology']:
            vm1 = i[0]
            intf1 = i[1]
            vm2 = i[2]
            intf2 = i[3]
            d1['vm'][vm1]['port'].update({intf1 : {'bridge' : i[5] }})
            d1['vm'][vm2]['port'].update({intf2 : {'bridge' : i[5] }})
        #pprint.pprint(d1['vm'])
        sort_port(d1)
        add_address2intf(d1)
        set_router_id(d1)
    add_ssh_key(d1)
    
def set_router_id(d1):
    for i in d1['vm'].keys():
        if 'lo0' in d1['vm'][i]['port'].keys():
            router_id = d1['vm'][i]['port']['lo0']['inet'].split('/')[0]
            #print(f"router-id {router_id}")
            d1['vm'][i].update({'router-id': router_id})	
def ipv4_to_int(ipv4):
    b1,b2,b3,b4 = ipv4.split('/')[0].split('.')
    retval = (int(b1) << 24) + (int(b2) << 16) + (int(b3) << 8) + int(b4)
    return retval

def bin2ip(ipbin):
    m1 = 255<<24
    m2 = 255<<16
    m3 = 255 << 8
    m4 = 255
    b1=str((ipbin & m1) >> 24)
    b2=str((ipbin & m2) >> 16)
    b3=str((ipbin & m3) >> 8)
    b4=str(ipbin & m4)
    retval = '.'.join((b1,b2,b3,b4))
    #print(retval)
    return retval

def add_address2intf(d1):
    #pprint.pprint(d1['vm'])
    # mask 
    # bit 0 : ipv4, 0b000000001, 0x1
    # bit 1 : ipv6, 0b000000010, 0x2
    # bit 2 : iso,  0b000000100, 0x4
    # bit 3 : isis  0b000001000, 0x8
    # bit 4 : ospf  0b000010000, 0x10
    # bit 5 : ospf3 0b000100000, 0x20
    # bit 6 : mpls, 0b001000000, 0x40
    # bit 7 : ldp,  0b010000000, 0x80
    # bit 8 : rsvp, 0b100000000, 0x100
    num_link_with_ipv4 = 0
    num_link_with_ipv6 = 0
    for i in d1['fabric']['topology']:
        if i[4] & 0x1:
            num_link_with_ipv4 +=1
        if i[4] & 0x2:
            num_link_with_ipv6 +=1
    #print("v4 and v6 link ",num_link_with_ipv4,num_link_with_ipv6)
    if num_link_with_ipv4 > 0:
        if 'ipv4_prefix' not in d1['fabric'].keys():
            print("ipv4 prefix is not defined on the configuration")
            exit()
        else:
            # print("ipv4 prefix is defined")
            pref_len = 32 - int(d1['fabric']['ipv4_prefix'].split('/')[1])
            #pref_len6 = 128 - int(d1['fabric']['subnet6'].split('/')[1])
            num_subnet = int( (2 **  pref_len) / 2)
            #num_subnet6 = int( (2 **  pref_len6) / 2)
            #print(f"num_link {num_link} num_subnet {num_subnet} num_subnet6 {num_subnet6}")
            #exit(1)
            if (num_link_with_ipv4 > num_subnet):
                print(f"not enough ip address for fabric link\nnum of link {num_link_with_ipv4}, num of subnet {num_subnet}" )
                exit(1)
            # elif check_ip(d1):
            # 	print("wrong subnet allocation")
            # 	print(f"subnet {d1['fabric']['subnet'].split('/')[0]} can't be used with prefix {d1['fabric']['subnet'].split('/')[1]}")
            # #elif not check_vm(d1):
            # #	print("number of VM on topology doesn't match with on configuration")
            else:
                #print(f"enough ip on the subnet link {num_link_with_ipv4}, num of subnet {num_subnet}")
                start_ip = ipv4_to_int(d1['fabric']['ipv4_prefix'])
                #print("start_ip ",start_ip,f"{bin2ip(start_ip)}/31")
                
                for i in d1['fabric']['topology']:
                    if i[4] & 0x1:
                        vm1 = i[0]
                        intf1 = i[1]
                        vm2 = i[2]
                        intf2 = i[3]
                        ip_vm1 = f"{bin2ip(start_ip)}/31"
                        start_ip +=1
                        ip_vm2 = f"{bin2ip(start_ip)}/31"
                        d1['vm'][vm1]['port'][intf1].update({'inet' : ip_vm1 })
                        d1['vm'][vm2]['port'][intf2].update({'inet' : ip_vm2 })
                        start_ip +=1
    if num_link_with_ipv6 > 0:
        if 'ipv6_prefix' not in d1['fabric'].keys():
            for i in d1['fabric']['topology']:
                if i[4] & 0x2:
                    vm1 = i[0]
                    intf1 = i[1]
                    vm2 = i[2]
                    intf2 = i[3]
                    d1['vm'][vm1]['port'][intf1].update({'inet6' : 1 })
                    d1['vm'][vm2]['port'][intf2].update({'inet6' : 1 })
        else:
            start_ipv6 = 0
            ipv6_address=d1['fabric']['ipv6_prefix'].split('/')[0]
            for i in d1['fabric']['topology']:
                if i[4] & 0x2:
                    vm1 = i[0]
                    intf1 = i[1]
                    vm2 = i[2]
                    intf2 = i[3]
                    ipv6 = str(hex(start_ipv6)).split('x')[1]
                    ipv6_vm1 = f"{ipv6_address}{ipv6}/127"
                    start_ipv6 += 1
                    ipv6 = str(hex(start_ipv6)).split('x')[1]
                    ipv6_vm2 = f"{ipv6_address}{ipv6}/127"
                    d1['vm'][vm1]['port'][intf1].update({'inet6' : ipv6_vm1 })
                    d1['vm'][vm2]['port'][intf2].update({'inet6' : ipv6_vm2  })
                    start_ipv6 += 1
    for i in d1['fabric']['topology']:
        vm1 = i[0]
        vm1_type = d1['vm'][vm1]['type']
        intf1 = i[1]
        vm2 = i[2]
        vm2_type = d1['vm'][vm2]['type']
        intf2 = i[3]
        prot1 = {
            'protocols' :
                {
                    'ospf' : 0,
                    'mpls' : 0,
                    'rsvp' : 0,
                    'ldp' : 0,
                    'ospf3' : 0,
                    'isis' : 0 
                }
        }
        d1['vm'][vm1].update(prot1)
        d1['vm'][vm2].update(prot1)

        if vm1_type in ['vjunosswitch','vjunosrouter','vjunosevolved','vsrx'] and vm2_type=='vaoscx':
            d1['vm'][vm1]['port'][intf1].update({'mtu' : 9014 })
            d1['vm'][vm2]['port'][intf2].update({'mtu' : 9000 })
        elif vm1_type=='vaoscx' and vm2_type in ['vjunosswitch','vjunosrouter','vjunosevolved','vsrx']:
            d1['vm'][vm1]['port'][intf1].update({'mtu' : 9000 })
            d1['vm'][vm2]['port'][intf2].update({'mtu' : 9014 })
        else:
            d1['vm'][vm1]['port'][intf1].update({'mtu' : 9000 })
            d1['vm'][vm2]['port'][intf2].update({'mtu' : 9000 })


        # mask 
        # bit 0 : ipv4, 0b000000vm1_type = d1['vm'][vm1]['type']001, 0x1
        # bit 1 : ipv6, 0b000000010, 0x2
        # bit 2 : iso,  0b000000100, 0x4
        # bit 3 : isis  0b000001000, 0x8
        # bit 4 : ospf  0b000010000, 0x10
        # bit 5 : ospf3 0b000100000, 0x20
        # bit 6 : mpls, 0b001000000, 0x40
        # bit 7 : ldp,  0b010000000, 0x80
        # bit 8 : rsvp, 0b100000000, 0x100
        if i[4] & 0x4:
            d1['vm'][vm1]['port'][intf1].update({'iso' : 1 })
            d1['vm'][vm2]['port'][intf2].update({'iso' : 1 })
        if i[4] & 0x8:
            d1['vm'][vm1]['port'][intf1].update({'isis' : 1 })
            d1['vm'][vm2]['port'][intf2].update({'isis' : 1 })
            d1['vm'][vm1]['protocols']['isis'] = 1
            d1['vm'][vm2]['protocols']['isis'] = 1

        if i[4] & 0x10:
            d1['vm'][vm1]['port'][intf1].update({'ospf' : 1 })
            d1['vm'][vm2]['port'][intf2].update({'ospf' : 1 })
            d1['vm'][vm1]['protocols']['ospf'] = 1
            d1['vm'][vm2]['protocols']['ospf'] = 1
        if i[4] & 0x20:
            d1['vm'][vm1]['port'][intf1].update({'ospf3' : 1 })
            d1['vm'][vm2]['port'][intf2].update({'ospf3' : 1 })
            d1['vm'][vm1]['protocols']['ospf3'] = 1
            d1['vm'][vm2]['protocols']['ospf3'] = 1
        if i[4] & 0x40:
            d1['vm'][vm1]['port'][intf1].update({'mpls' : 1 })
            d1['vm'][vm2]['port'][intf2].update({'mpls' : 1 })
            d1['vm'][vm1]['protocols']['mpls'] = 1
            d1['vm'][vm2]['protocols']['mpls'] = 1
        if i[4] & 0x80:
            d1['vm'][vm1]['port'][intf1].update({'ldp' : 1 })
            d1['vm'][vm2]['port'][intf2].update({'ldp' : 1 })
            d1['vm'][vm1]['protocols']['ldp'] = 1
            d1['vm'][vm2]['protocols']['ldp'] = 1
        if i[4] & 0x100:
            d1['vm'][vm1]['port'][intf1].update({'rsvp' : 1 })
            d1['vm'][vm2]['port'][intf2].update({'rsvp' : 1 })
            d1['vm'][vm1]['protocols']['rsvp'] = 1
            d1['vm'][vm2]['protocols']['rspv'] = 1
    #pprint.pprint(d1)
    # exit()


def num_link_with_ip(d1):
    retval4=0
    retval6=0
    for i in d1['fabric']['topology']:
        if i[4] & 0x1:
            retval4+=1
        if i[4] & 0x2:
            retval6+=1
    return retval4, retval6


def sort_port(d1):
    #print('function sort_port')
    for i in d1['vm'].keys():
        intf=sorted(d1['vm'][i]['port'].keys())
        t1 = {}
        #print(intf)
        for j in intf:
            t1.update({ j : d1['vm'][i]['port'][j]})
        d1['vm'][i]['port'] = t1
    
def set_bridge(d1):
    t1 = d1['vm'].keys()
    vm = []
    intf_list=[]
    bridge_list=[]
    for i in t1:
        if d1['vm'][i]['type'] in ['vjunosswitch','vjunosevolved','vjunosrouter','sonic','vaoscx']:
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
    
    # this part of the function is to hack the linux kernel to allow LLDP and LACP frame to be forwarded between vJunos VM
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
        # if d1['vm'][i]['type'] in ['vjunosswitch','vjunosevolved','vjunosrouter','sonic','ubuntu']:
        if d1['vm'][i]['type'] in ['vjunosswitch','vjunosevolved','vjunosrouter','sonic','vaoscx','vsrx']:
            #print(f"vm {i}")
            cmd=f"virsh dumpxml {i} | grep \"mac address\""
            a = subprocess.check_output(cmd,shell=True)
            mac = a.decode().split("\n")[0].split('=')[1].replace("'","").replace('/>',"")
            print(f"vm {i} mac {mac}")
            d1['vm'][i]['mac']=mac

def add_ssh_key(d1):
    if 'ssh_key_name' in d1['junos_login'].keys():
        key_file_priv = str(pathlib.Path.home()) + "/.ssh/" + d1['junos_login']['ssh_key_name']
    else:
        key_file_priv = str(pathlib.Path.home()) + "/.ssh/id_rsa"

    key_file = key_file_priv + ".pub"
    d1['junos_login']['ssh_key_priv']=key_file_priv
    # try:
    if os.path.exists(key_file):
        with open(key_file) as f:
            ssh_key = f.read()
        d1['junos_login']['ssh_key']=ssh_key.strip()
        
    # except Exception as e:
    # 	print(e)
    # 	exit()
    # adding configuration for loopback

def create_vm_dir(d1):
    vm_dir = d1['vm_dir']
    if os.path.exists(vm_dir):
        shutil.rmtree(vm_dir)
    dir_path = pathlib.Path(vm_dir)
    dir_path.mkdir(parents=True, exist_ok=True)

def create_netdev_config(d1):
    with open(d1['template']['junos']) as f:
        junos_template = f.read()
    with open(d1['template']['aoscx']) as f:
        aoscx_template = f.read()
    create_vm_dir(d1)
    p1 = {}
    p1['junos_user']=d1['junos_login']['user']
    p1['username']='admin'
    p1['password']=d1['junos_login']['password']
    # print(f"password : {d1['junos_login']['password']}")
    # print(f"password : {p1['password']}")
    p1['junos_passwd']=md5_crypt.hash(d1['junos_login']['password'])
    if 'ssh_key' in d1['junos_login'].keys():
        p1['ssh_key']=d1['junos_login']['ssh_key']
    for i in d1['vm'].keys():
        if d1['vm'][i]['type'] in ['vjunosswitch','vjunosevolved','vjunosrouter','vaoscx','vsrx']:
            print(f"vm {i}")
            p1['hostname']=i
            p1['type']= d1['vm'][i]['type']
            p1['ip_address']=f"{d1['vm'][i]['ip_address']}/{d1['ip_pool']['subnet'].split('/')[1]}"
            p1['gateway']=d1['ip_pool']['gateway']
            p1['protocols']=d1['vm'][i]['protocols']
            if 'router-id' in d1['vm'][i].keys():
                p1['router_id'] = d1['vm'][i]['router-id']
            if 'lo0' in d1['vm'][i]:
                p1['interfaces'] = {'lo0' : d1['vm'][i]['lo0']['family'] }
            else:
                p1['interfaces'] = {}
            #print(p1)
            for j in list(d1['vm'][i]['port'].keys()):
                 p1['interfaces'].update({j : d1['vm'][i]['port'][j]})
            #pprint.pprint(p1)
            if d1['vm'][i]['type'] == 'vaoscx':
                config1=Template(aoscx_template).render(p1)
            else:
                config1=Template(junos_template).render(p1)
            if not os.path.exists(d1['DEST_DIR']):
                os.makedirs(d1['DEST_DIR'])
            # else:
            # 	if not os.path.isdir(d1['DEST_DIR']):
            # 		os.remove(d1['DEST_DIR'])
            # 		os.makedirs(d1['DEST_DIR'])
            filename = f"{d1['DEST_DIR']}/{i}.conf"
            with open(filename,"w") as f:
                f.write(config1)
            if d1['vm'][i]['type'] == 'vsrx':
                create_vsrx_config(d1,i)
        
def create_vsrx_config(d1,i):
    iso_dir = f"{d1['DEST_DIR']}/iso"
    iso_file = f"{d1['DEST_DIR']}/iso"
    iso_dest = f"{d1['vm_dir']}/{i}_config.iso"
    src_file = f"{d1['DEST_DIR']}/{i}.conf"
    dst_file = f"{d1['DEST_DIR']}/iso/juniper.conf"
    dir_path = pathlib.Path(iso_dir)
    dir_path.mkdir(parents=True, exist_ok=True)
    shutil.copy(src_file, dst_file)
    cmd1=f"mkisofs -l -o {iso_dest} {iso_dir}"
    print("write vsrx config iso")
    subprocess.check_output(cmd1,shell=True)


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

def create_dhcp_config_v1(d1):
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
        # if d1['vm'][i]['type'] in  ['vjunosswitch','vjunosevolved','vjunosrouter','sonic','ubuntu']:
        if d1['vm'][i]['type'] in  ['vjunosswitch','vjunosevolved','vjunosrouter','sonic']:
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

def create_dhcp_config_v2(d1):
    # this is for kea-dhcp4-server configuration
    with open(d1['template']['kea4']) as f:
        j2 = f.read()
    p1 = {}
    p1['intf'] = d1['mgmt']['bridge']
    p1['subnet'] = d1['ip_pool']['subnet']
    p1['range_min'] = d1['ip_pool']['range']['min']
    p1['range_max'] = d1['ip_pool']['range']['max']
    p1['gateway'] = d1['ip_pool']['gateway']
    p1['option150'] = d1['ip_pool']['option-150']
    # cmd="resolvectl status | grep DNS| grep 'DNS Servers:'"
    # result = subprocess.check_output(cmd,shell=True)
    # dns = result.decode().strip().split()[2:][0]
    #print(dns)
    # p1['dns'] = dns
    p1['dns'] = d1['ip_pool']['dns']
    p1['vm'] = {}
    for i in d1['vm'].keys():
        # if d1['vm'][i]['type'] in  ['vjunosswitch','vjunosevolved','vjunosrouter','sonic','ubuntu']:
        if d1['vm'][i]['type'] in  ['vjunosswitch','vjunosevolved','vjunosrouter','sonic','vaoscx','vsrx']:
            if d1['vm'][i]['type'] == 'sonic':
                p1['vm'].update({i : {'hostname': i,'mac' : d1['vm'][i]['mac'],'ip' : d1['vm'][i]['ip_address'],'conf' : 0}})
            else:
                p1['vm'].update({i : {'hostname': i,'mac' : d1['vm'][i]['mac'],'ip' : d1['vm'][i]['ip_address'],'conf' : 1}})
    #print(p1)
    #print(j2)
    config1=Template(j2).render(p1)
    kea4=yaml.load(config1,Loader=yaml.FullLoader)
    kea4_json = json.dumps(kea4,indent=2)
    if not os.path.exists(d1['DEST_DIR']):
        os.makedirs(d1['DEST_DIR'])
    # else:
    # 	if not os.path.isdir(d1['DEST_DIR']):
    # 		os.remove(d1['DEST_DIR'])
    # 		os.makedirs(d1['DEST_DIR'])
    filename = f"{d1['DEST_DIR']}/kea-dhcp4.conf"
    with open(filename,"w") as f:
        f.write(kea4_json)

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
    create_dhcp_config = create_dhcp_config_v2
    #print(d1)
    print("getting mac address info")
    get_mac_fxp0(d1)
    #print(d1)
    print("writing configuration for the network devices")
    # create_netdev_config(d1)
    print("Creating dhcpd config")

    create_dhcp_config(d1)
    #create_apstra_dhcp_config(d1)
    print("files are created on directory ./result")
    print("upload file dhcpd.conf into dhcp server /etc/dhcpd/dhcpd.conf")
    print(f"upload junos configuration files ({junos_config(d1)}), into root directory of tftp server")
    print("Adding entries into  file ~/.ssh/config")
    add_to_ssh_config(d1)

def check_argv(argv):
    retval={}
    cmd_list=['addbr','create','start','config','del','stop','test','delbr','printdata','setbr','listbr','sshconfig','lxc-create','lxc-start','lxc-stop','lxc-delete','lxc-delete-only']
    if len(argv) == 1:
        print_syntax()
    else:
        if not os.path.isfile("./lab.yaml"):
            print("file lab.conf doesn't exist, please create one or define another file for configuration")
        else:
            # if argv[1] not in cmd_list:
            # 	print_syntax()
            # else:
            with open("lab.yaml") as f:
                d1 = f.read()	
            retval = yaml.load(d1,Loader=yaml.FullLoader)
            retval['cmd'] = argv[1]
            t1 = argv[0].split('/')
            _ = t1.pop()
            retval['template']={
                        'junos':f"{'/'.join(t1)}/junos.j2",
                        'dhcp':f"{'/'.join(t1)}/dhcpd.j2",
                        'kea4':f"{'/'.join(t1)}/kea-dhcp4.j2",
                        'vjunosswitch':f"{'/'.join(t1)}/vjunosswitch.j2",
                        'vjunosrouter':f"{'/'.join(t1)}/vjunosrouter.j2",
                        'vsrx':f"{'/'.join(t1)}/vsrx.j2",
                        'sonic':f"{'/'.join(t1)}/sonic.j2",
                        'vjunosevolved':f"{'/'.join(t1)}/vjunosevolved.j2",
                        'vaoscx':f"{'/'.join(t1)}/vaoscx.j2",
                        'aoscx':f"{'/'.join(t1)}/aoscx.j2",
                        "ssh_config" : f"{'/'.join(t1)}/ssh_config.j2"
            }
            retval['DEST_DIR'] = './result'
            ## checking if vjunosevolved is defined ?
            # this is for early release of vjunosevolved
            # for i in retval['vm'].keys():
            # 	if retval['vm'][i]['type'] == "vjunosevolved":
            # 		if 'vevo_old' in retval['vm'][i].keys(): 
            # 			temp_port = retval['vm'][i]['port']
            # 			retval['vm'][i]['port']={
            # 				'p1': f"{i}PFE",
            # 				'p2': f"{i}RPIO",
            # 				'p3': f"{i}RPIO",
            # 				'p4': f"{i}PFE"
            # 			}
            # 			retval['vm'][i]['port'].update(temp_port)
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
        for j in d1['vm'][i]['port'].keys():
            #print(j)
            if j != "lo0":
                if 'bridge' in d1['vm'][i]['port'][j].keys():
                    b1 = d1['vm'][i]['port'][j]['bridge']
                    if b1 not in list_bridge:
                        list_bridge.append(b1)
                else:
                    print(f"vm {i} interface {j} doesn't have bridge parameter")
                    exit()
    return list_bridge


# def list_bridge(d1):
# 	cmd="ip --json link list type bridge"
# 	t1 = json.loads(subprocess.check_output(cmd,shell=True).decode())
# 	list_br=[]
# 	for i in t1:
# 		list_br.append(i['ifname'])
# 	cmd="ip --json link list type openvswitch"
# 	t1 = json.loads(subprocess.check_output(cmd,shell=True).decode())
# 	for i in t1:
# 		list_br.append(i['ifname'])
# 	pprint.pprint(list_br)


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
                    if j != 'lo0':
                        t1=f"ge{j.split('/')[2]}"
                        if d1['vm'][i]['port'][j]['bridge'] in d1['ovs']:
                            data1['interfaces'][t1]={'bridge':d1['vm'][i]['port'][j]['bridge'],'index':p,'ovs':1}
                        else:
                            data1['interfaces'][t1]={'bridge':d1['vm'][i]['port'][j]['bridge'],'index':p,'ovs':0}
                        p+=1
                pprint.pprint(data1)
                with open(d1['template'][vm_type]) as f1:
                    template1 = f1.read()
                    cmd=Template(template1).render(data1)
            elif d1['vm'][i]['type'] == 'vsrx':
                #cmd="virsh capabilities"
                #cpu_model = xmltodict.parse(subprocess.check_output(cmd,shell=True).decode())['capabilities']['host']['cpu']['model'].split("-")[0]
                cpu_model = "IvyBridge"
                vm_type = d1['vm'][i]['type']
                data1['name']=i
                data1['disk']=disk
                data1['vcpu']=2
                data1['ram']=4096
                data1['cpu_model']=cpu_model
                data1['cdrom'] = f"{d1['vm_dir']}/{i}_config.iso"
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
                    if j != 'lo0':
                        t1=f"ge{j.split('/')[2]}"
                        if d1['vm'][i]['port'][j]['bridge'] in d1['ovs']:
                            data1['interfaces'][t1]={'bridge':d1['vm'][i]['port'][j]['bridge'],'index':p,'ovs':1}
                        else:
                            data1['interfaces'][t1]={'bridge':d1['vm'][i]['port'][j]['bridge'],'index':p,'ovs':0}
                        p+=1
                pprint.pprint(data1)
                with open(d1['template'][vm_type]) as f1:
                    template1 = f1.read()
                    cmd=Template(template1).render(data1)
            elif d1['vm'][i]['type'] in  ['vaoscx']:
                #cmd="virsh capabilities"
                #cpu_model = xmltodict.parse(subprocess.check_output(cmd,shell=True).decode())['capabilities']['host']['cpu']['model'].split("-")[0]
                cpu_model = "IvyBridge"
                vm_type = d1['vm'][i]['type']
                data1['name']=i
                data1['disk']=disk
                data1['vcpu']=2
                data1['ram']=4096
                data1['cpu_model']=cpu_model
                data1['interfaces']={}
                # print(f"vm {i}")
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
                    if j != 'lo0':
                        t1=f"ge{j.split('/')[2]}"
                        if d1['vm'][i]['port'][j]['bridge'] in d1['ovs']:
                            data1['interfaces'][t1]={'bridge':d1['vm'][i]['port'][j]['bridge'],'index':p,'ovs':1}
                        else:
                            data1['interfaces'][t1]={'bridge':d1['vm'][i]['port'][j]['bridge'],'index':p,'ovs':0}
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
                data1['vcpu']=2
                data1['ram']=4096
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
                    #t1=sonic_port(j)
                    t1 = j
                    if d1['vm'][i]['port'][j]['bridge'] in d1['ovs']:
                        data1['interfaces'][t1]={'bridge':d1['vm'][i]['port'][j]['bridge'],'index':p,'ovs':1}
                    else:
                        data1['interfaces'][t1]={'bridge':d1['vm'][i]['port'][j]['bridge'],'index':p,'ovs':0}
                    p+=1
                pprint.pprint(data1)
                with open(d1['template'][vm_type]) as f1:
                    template1 = f1.read()
                    cmd=Template(template1).render(data1)
            elif d1['vm'][i]['type'] == 'vjunosevolved':
                # disk_cfg = d1['vm_dir'] + f"/{i}_cfg.img"
                # cmd = f"cp {d1['disk']['vjunosevolved_config']} {disk_cfg}"
                # print(f"copying file from {d1['disk']['vjunosevolved_config']} to {disk_cfg}")
                # subprocess.check_output(cmd,shell=True)
                cmd="virsh capabilities"
                #cpu_model = xmltodict.parse(subprocess.check_output(cmd,shell=True).decode())['capabilities']['host']['cpu']['model'].split("-")[0]
                cpu_model = "IvyBridge"
                data1['name']=i
                data1['disk']=disk
                # data1['disk_config']=disk_cfg
                data1['vcpu']=4
                data1['ram']=8192
                if 'bx' in d1['vm'][i].keys():
                    data1['bx']=1
                # data1['ram']=16384
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
                        data1['interfaces'][j]={'bridge':d1['vm'][i]['port'][j]['bridge'],'index':p}	
                    else:
                        if j != 'lo0':
                            t1=f"et{j.split('/')[2]}"
                            # data1['interfaces'][t1]={'bridge':d1['vm'][i]['port'][j],'index':p}
                            if d1['vm'][i]['port'][j]['bridge'] in d1['ovs']:
                                data1['interfaces'][t1]={'bridge':d1['vm'][i]['port'][j]['bridge'],'index':p,'ovs':1}
                            else:
                                data1['interfaces'][t1]={'bridge':d1['vm'][i]['port'][j]['bridge'],'index':p,'ovs':0}
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
            # elif d1['vm'][i]['type'] == 'alpine':
            # 	data1['name']=i
            # 	data1['disk']=disk
            # 	data1['vcpu']=1
            # 	data1['ram']=512
            # 	data1['interfaces']={}
            # 	ports= list(d1['vm'][i]['port'].keys())
            # 	#_ =ports.sort()
            # 	for j in ports:
            # 		data1['interfaces'][j]={'bridge':d1['vm'][i]['port'][j]['bridge']}
            # 	with open(d1['template']['alpine']) as f1:
            # 		template1 = f1.read()
            # 		cmd=Template(template1).render(data1)
            # elif d1['vm'][i]['type'] == 'ubuntu':
            # 	data1['name']=i
            # 	data1['disk']=disk
            # 	data1['vcpu']=2
            # 	data1['ram']=4096
            # 	# data1['interfaces']={}
            # 	# ports= list(d1['vm'][i]['port'].keys())
            # 	# _ =ports.sort()
            # 	# for j in ports:
            # 	# 	data1['interfaces'][j]={'bridge':d1['vm'][i]['port'][j]}
            # 	# new section
            # 	data1['interfaces']={}
            # 	if 'type' in d1['mgmt'].keys():
            # 		if d1['mgmt']['type'] == 'ovs':
            # 			if 'vlan' in d1['mgmt'].keys():
            # 				vlantemp = d1['mgmt']['vlan']
            # 			else:
            # 				vlantemp = 0
            # 			data1['interfaces']['mgmt']={
            # 				'bridge' : d1['mgmt']['bridge'],
            # 				'index' : 1,
            # 				'vlan': vlantemp,
            # 				'ovs': '1' 
            # 			} 
            # 	else:
            # 		data1['interfaces']['mgmt']={
            # 			'bridge' : d1['mgmt']['bridge'],
            # 			'index' : 1,
            # 			'ovs':0
            # 		}
            # 	p=2
            # 	ports= list(d1['vm'][i]['port'].keys())
            # 	_ =ports.sort()
            # 	for j in ports:
            # 		#t1=sonic_port(j)
            # 		t1 = j
            # 		if d1['vm'][i]['port'][j]['bridge'] in d1['ovs']:
            # 			data1['interfaces'][t1]={'bridge':d1['vm'][i]['port'][j]['bridge'],'index':p,'ovs':1}
            # 		else:
            # 			data1['interfaces'][t1]={'bridge':d1['vm'][i]['port'][j]['bridge'],'index':p,'ovs':0}
            # 		p+=1
            # 	# end of new section
            # 	with open(d1['template']['ubuntu']) as f1:
            # 		template1 = f1.read()
            # 		cmd=Template(template1).render(data1)
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

def delete_known_hosts(d1):
    print("deleting entry from ~/.ssh/known_hosts")
    ip_list = []
    home_dir = Path.home()
    for i in d1['vm'].keys():
        ipaddr=d1['vm'][i]['ip_address']
        cmd1 = f"ssh-keygen -f '{home_dir}/.ssh/known_hosts' -R '{ipaddr}'"
        subprocess.check_output(cmd1,shell=True)

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
        list_vm.append(i)
    # print("list of vm ",list_vm)
    new_ssh_config.append("### add by vlab.py script ###")
    for i in list_vm:
        new_ssh_config.append(f"Host {i}")
        new_ssh_config.append(f"  hostname {d1['vm'][i]['ip_address']}")
        new_ssh_config.append(f"  user {d1['junos_login']['user']}")
        # ssh_key is disabled, related to  DSSKey class  that has been removed from paramiko modules
        # which make pyez doesn't work.
        # new_ssh_config.append(f"  IdentityFile {d1['junos_login']['ssh_key_priv']}")
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

def create_lxc(d1):
    cmd = ['lxc', 'ls','--format=json']
    result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output1 = result.stdout
    d0 = json.loads(output1)
    list_of_images = [i['name'] for i in d0]
    t0="""
{% for i in intf %}
auto {{i}}
{% if intf[i].inet -%}
iface {{i}} inet static
    address {{ intf[i].inet }}
{% else -%}
iface {{i}} inet dhcp
{% endif -%}
    {% if intf[i].gw4 -%}
    gateway {{ intf[i].gw4 }}
    {% endif -%}
    mtu 1500
{% if intf[i].inet6 -%}
iface {{i}} inet6 static
    address {{ intf[i].inet6 }}
    {% if intf[i].gw6 -%}
    gateway {{ intf[i].gw6 }}
    {% endif -%}
{% endif -%}
{% endfor -%}
    """
    u0="""
network:
  version: 2
  ethernets:
{% for i in intf %}
    {{ i }}:
{% if intf[i].inet %}
      addresses: 
      - {{ intf[i].inet }}
{% if intf[i].inet6 %}
      - {{ intf[i].inet6 }}
{% endif -%}
{% endif -%}
{% if intf[i].gw4 %}
      routes:
      - to: default
        via: {{ intf[i].gw4 }}
{% if intf[i].gw6 %}
      - to: default
        via: {{ intf[i].gw6 }}
{% endif -%}
{% endif -%}
{% endfor %}
    """
    frr0="""
ipv6 forwarding
!
interface eth1
{% if nd_prefix -%}
ipv6 nd prefix {{nd_prefix}}
no ipv6 nd suppress-ra
{% endif %}
exit
router bgp {{asn}}
no bgp ebgp-requires-policy
neighbor {{peerv4}} remote-as {{peerasn}}
neighbor {{peerv6}} remote-as {{peerasn}}
!
address-family ipv4 unicast
{% if advv4 -%}
network {{advv4}}
{% endif %}

exit-address-family
!
address-family ipv6 unicast
{% if advv6 -%}
network {{advv6}}
{% endif %}
neighbor {{peerv6}} activate
exit-address-family
exit
!
    """
    dns0="""
dhcp-range={{range}},255.255.255.0,2h
dhcp-option=option:router,{{router}}
dhcp-option=option:dns-server,{{dns}}
domain=local.lan
local=/local.lan/
    """
    resolve0=""""
nameserver {{dns}}
    """
    t1 = Template(t0)
    u1 = Template(u0)
    frr1 = Template(frr0)
    dns1 = Template(dns0)
    resolve1=Template(resolve0)
    # for i in d0:
    #     print(i['name'])
    # print(f"image {list_of_images}")
    list_of_lxc = d1['lxc'].keys()
    # checking image
    for i in list_of_lxc:
        cmd = ["lxc","copy",d1['lxc'][i]['type'],i]
        if d1['lxc'][i]['type'] not in list_of_images:
            print(f"image {d1['lxc'][i]['type']} for container {i} is not available")
        else:
            # src = {d1['lxc'][i]['type']} 
            #print(cmd)
            print(f"creating {i}")
            result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output1 = result.stdout
            ports = d1['lxc'][i]['port'].keys()
            #print(f"lxc {i} ports {ports}")
            data1 = ["devices:"]
            net_cfg1=["intf:"]
            for p in ports:
                net_cfg1.append(f"  {p}:")
                if 'inet' in d1['lxc'][i]['port'][p].keys():
                    net_cfg1.append(f"     inet: {d1['lxc'][i]['port'][p]['inet']}")
                if 'gw4' in d1['lxc'][i]['port'][p].keys():
                    net_cfg1.append(f"     gw4: {d1['lxc'][i]['port'][p]['gw4']}")
                if 'gw6' in d1['lxc'][i]['port'][p].keys():
                    net_cfg1.append(f"     gw6: {d1['lxc'][i]['port'][p]['gw6']}")
                if 'inet6' in d1['lxc'][i]['port'][p].keys():
                    net_cfg1.append(f"     inet6: {d1['lxc'][i]['port'][p]['inet6']}")
                             
                data1.append(f"  {p}:")
                data1.append(f"    name: {p}") 
                data1.append(f"    nictype: bridged")
                if 'bridge' not in d1['lxc'][i]['port'][p].keys():
                    print(f"bridge for lxc {i} port {p} is not defined")
                    exit(1)
                data1.append(f"    parent: {d1['lxc'][i]['port'][p]['bridge']}")
                if 'vlan' in d1['lxc'][i]['port'][p].keys():
                    data1.append(f"    vlan: '{d1['lxc'][i]['port'][p]['vlan']}'")
                data1.append(f"    type: nic")
            net_cfg2 = "\n".join(net_cfg1)
            net_cfg3 = yaml.load(net_cfg2,Loader=yaml.FullLoader)
            data2 = "\n".join(data1)
            data3 = yaml.load(data2,Loader=yaml.FullLoader)
            data4 = json.dumps(data3)
            data5 = f"{data4}"
            print(net_cfg3)
            # print(data5)
            print("change container configuration")
            cmd = ["lxc","query", "--request", "PATCH", f"/1.0/instances/{i}","--data",data5]
            result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output1 = result.stdout
            if d1['lxc'][i]['type'] == 'alpine':
                net_cfg4 = t1.render(net_cfg3)
                cmd = ["lxc", "file" , "push", "interfaces.tmp",  f"{i}/etc/network/interfaces"]
            elif d1['lxc'][i]['type'] == 'ubuntu':
                net_cfg4 = u1.render(net_cfg3)
                #cmd = ["lxc", "file" , "push", "interfaces.tmp",  f"{i}/etc/netplan/50-cloud-init.yaml"]
                cmd = ["lxc", "file" , "push", "interfaces.tmp",  f"{i}/etc/netplan/01_net.yaml"]
                #print(net_cfg4)
            with open("interfaces.tmp","w") as f1:
                f1.write(net_cfg4)
            # cmd = ["lxc", "file" , "push", "interfaces.tmp",  f"{i}/etc/network/interfaces"]
            result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output1 = result.stdout
            os.remove("interfaces.tmp")
            if d1['lxc'][i]['type'] == "router":
                frr_data = d1['lxc'][i]['bgp']
                frr_cfg = frr1.render(frr_data)
                with open("frr.conf","w") as f1:
                    f1.write(frr_cfg)
                cmd = ["lxc", "file" , "push", "frr.conf",  f"{i}/etc/frr/frr.conf"]
                result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                output1 = result.stdout
                os.remove("frr.conf")
                if 'dnsmasq' in d1['lxc'][i].keys():
                    dns_data = d1['lxc'][i]['dnsmasq']
                    dns_cfg = dns1.render(dns_data)
                    with open("dnsmasq.conf","w") as f1:
                        f1.write(dns_cfg)
                    cmd = ["lxc", "file" , "push", "dnsmasq.conf",  f"{i}/etc/dnsmasq.conf"]
                    result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    output1 = result.stdout
                    os.remove("dnsmasq.conf")

def delete_lxc(d1):
    cmd = ['lxc', 'ls','--format=json']
    result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output1 = result.stdout
    d0 = json.loads(output1)
    list_of_existing_lxc = [i['name'] for i in d0]
    list_of_lxc = d1['lxc'].keys()
    for i in list_of_lxc:
        if i not in list_of_existing_lxc:
            print(f"lxc {i} doesn't exist")
        else:
            cmd = ['lxc','rm',i]
            print(f"deleting {i}")
            result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output1 = result.stdout

def start_lxc(d1):
    list_bridge(d1)
    cmd = ['lxc', 'ls','--format=json']
    result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output1 = result.stdout
    d0 = json.loads(output1)
    list_of_existing_lxc = [i['name'] for i in d0]
    list_of_lxc = d1['lxc'].keys()
    for i in list_of_lxc:
        if i not in list_of_existing_lxc:
            print(f"lxc {i} doesn't exist")
        else:
            cmd = ['lxc','start',i]
            print(f"starting {i}")
            result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output1 = result.stdout


def stop_lxc(d1):
    cmd = ['lxc', 'ls','--format=json']
    result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output1 = result.stdout
    d0 = json.loads(output1)
    list_of_existing_lxc = [i['name'] for i in d0]
    list_of_lxc = d1['lxc'].keys()
    for i in list_of_lxc:
        if i not in list_of_existing_lxc:
            print(f"lxc {i} doesn't exist")
        else:
            cmd = ['lxc','stop',i]
            print(f"stoping {i}")
            result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output1 = result.stdout

def list_bridge(d1):
    # cmd = ["ip","link", "show","type","bridge","|","grep","UP"]
    cmd = ["ip","link", "show","type","bridge"]
    result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output1 = result.stdout
    o3 = []
    o2 = output1.split("\n")
    for i in o2:
        if "UP" in i:
            o3.append(i.replace(" ","").split(":")[1])
    cmd=["sudo", "ovs-vsctl","show"]
    result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output1 = result.stdout
    o2 = output1.split("\n")
    for i in o2:
        if "Bridge" in i:
            o3.append(i.replace("Bridge","").replace(" ",""))
    # print(output1)
    #print(o3)
    o4=[]
    for i in d1['lxc'].keys():
        for j in d1['lxc'][i]['port'].keys():
            br = d1['lxc'][i]['port'][j]['bridge']
            if br not in o3 and br not in o4:
                o4.append(d1['lxc'][i]['port'][j]['bridge'])
    if o4:
        print(f"creating bridge {o4}")
    for i in o4:
        cmd=["sudo", "ip", "link", "add", "dev", i,"type", "bridge"]
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output1 = result.stdout
        cmd=["sudo", "ip", "link", "set", "dev",i,"up"]
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output1 = result.stdout
        cmd=["sudo","sysctl","-w", f"net.ipv6.conf.{i}.disable_ipv6=1"]
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

def get_aoxcx_config(d1,i):
    ip_address = d1['vm'][i]['ip_address']
    url1=f"https://{ip_address}/rest/v10.18/login"
    data1 = {'username':d1['junos_login']['user'],'password':d1['junos_login']['password']}
    session=requests.session()
    login=session.post(url1,data=data1,verify=False)
    #print(f"status code : {login.status_code}")
    print(f"Successfully open connection to {i}")
    if login.status_code != 200:
        print(f"error accessing API of switch {i}")
    else:
        if not os.path.exists(d1['config_dir']):
            os.makedirs(d1['config_dir'])
        dest_file = f"{d1['config_dir']}/{i}.conf"
        #url2="https://192.168.250.12/rest/v10.18/system/interfaces"
        url2=f"https://{ip_address}/rest/v10.18/configs/running-config"
        #url2="https://192.168.250.12/rest/v10.18/configs"
        #headers1 = {"Accept": "application/json"}
        headers1 = {"Accept": "text/plain"}
        result= session.get(url2,verify=False,headers=headers1)
        # pprint.pprint(result.text)
        with open(dest_file,"w") as f1:
            f1.write(result.text)
        # d1 = result.text.split("\n")
        # #d1 = json.dumps(result.text)
        # for i in d1:
        #     print(i)
        # logout
        url3=f"https://{ip_address}/rest/v10.18/logout"
        logout=session.post(url3,verify=False)
        #print(logout)


def get_junos_config(d1,i):
    ip_address = d1['vm'][i]['ip_address']
    junos_username = d1['junos_login']['user']
    junos_password = d1['junos_login']['password']
    if not os.path.exists(d1['config_dir']):
        os.makedirs(d1['config_dir'])
    dest_file = f"{d1['config_dir']}/{i}.conf"
    dev = Device(host=ip_address, user=junos_username, passwd=junos_password, gather_facts=False)
    try:
        dev.open()
        print(f"Successfully open connection to {i}")
        #print(dev.facts)
        data = dev.rpc.get_config(options={'format':'set'})
        config1=etree.tostring(data, encoding='unicode', pretty_print=True).replace('<configuration-set>','').replace('</configuration-set>','')
        with open(dest_file,"w") as f1:
            f1.write(config1)
        # print (data)
    except ConnectError as err:
        print ("Cannot connect to device: {0}".format(err))
        sys.exit(1)
    except Exception as err:
        print (err)
        sys.exit(1)


def get_device_config(d1):
    for i in d1['vm'].keys():
        if d1['vm'][i]['type'] in ['vjunosevolved','vjunosrouter','vsrx','vjunosswitch']:
            get_junos_config(d1,i)
        elif d1['vm'][i]['type'] in ['vaoscx']:
            get_aoxcx_config(d1,i)