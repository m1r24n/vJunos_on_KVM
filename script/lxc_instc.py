#!/usr/bin/env python3
import sys, pathlib, yaml, subprocess, json, os
from jinja2 import Template


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
        for j in d1['lxc'][i]['ports'].keys():
            br = d1['lxc'][i]['ports'][j]['bridge']
            if br not in o3 and br not in o4:
                o4.append(d1['lxc'][i]['ports'][j]['bridge'])
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
        output1 = result.stdout

def create_lxc(d1):
    cmd = ['lxc', 'ls','--format=json']
    result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output1 = result.stdout
    d0 = json.loads(output1)
    list_of_images = [i['name'] for i in d0]
    t0="""
{% for i in intf %}
auto {{i}}
{% if intf[i].ipv4 -%}
iface {{i}} inet static
    address {{ intf[i].ipv4 }}
{% else -%}
iface {{i}} inet dhcp
{% endif -%}
    {% if intf[i].gw4 -%}
    gateway {{ intf[i].gw4 }}
    {% endif -%}
    mtu 1500
{% if intf[i].ipv6 -%}
iface {{i}} inet6 static
    address {{ intf[i].ipv6 }}
    {% if intf[i].gw6 -%}
    gateway {{ intf[i].gw6 }}
    {% endif -%}
{% endif -%}
{% endfor -%}
    """
    frr0="""
ipv6 forwarding
!
interface eth1
ipv6 nd prefix {{nd_prefix}}
no ipv6 nd suppress-ra
exit
router bgp {{asn}}
no bgp ebgp-requires-policy
neighbor {{peerv4}} remote-as {{peerasn}}
neighbor {{peerv6}} remote-as {{peerasn}}
!
address-family ipv4 unicast
network {{advv4}}
exit-address-family
!
address-family ipv6 unicast
network {{advv6}}
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
    t1 = Template(t0)
    frr1 = Template(frr0)
    dns1 = Template(dns0)
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
            ports = d1['lxc'][i]['ports'].keys()
            #print(f"lxc {i} ports {ports}")
            data1 = ["devices:"]
            net_cfg1=["intf:"]
            for p in ports:
                net_cfg1.append(f"  {p}:")
                if 'ipv4' in d1['lxc'][i]['ports'][p].keys():
                    net_cfg1.append(f"     ipv4: {d1['lxc'][i]['ports'][p]['ipv4']}")
                if 'gw4' in d1['lxc'][i]['ports'][p].keys():
                    net_cfg1.append(f"     gw4: {d1['lxc'][i]['ports'][p]['gw4']}")
                if 'gw6' in d1['lxc'][i]['ports'][p].keys():
                    net_cfg1.append(f"     gw6: {d1['lxc'][i]['ports'][p]['gw6']}")
                if 'ipv6' in d1['lxc'][i]['ports'][p].keys():
                    net_cfg1.append(f"     ipv6: {d1['lxc'][i]['ports'][p]['ipv6']}")
                             
                data1.append(f"  {p}:")
                data1.append(f"    name: {p}") 
                data1.append(f"    nictype: bridged")
                if 'bridge' not in d1['lxc'][i]['ports'][p].keys():
                    print(f"bridge for lxc {i} port {p} is not defined")
                    exit(1)
                data1.append(f"    parent: {d1['lxc'][i]['ports'][p]['bridge']}")
                if 'vlan' in d1['lxc'][i]['ports'][p].keys():
                    data1.append(f"    vlan: '{d1['lxc'][i]['ports'][p]['vlan']}'")
                data1.append(f"    type: nic")
            net_cfg2 = "\n".join(net_cfg1)
            net_cfg3 = yaml.load(net_cfg2,Loader=yaml.FullLoader)
            data2 = "\n".join(data1)
            data3 = yaml.load(data2,Loader=yaml.FullLoader)
            data4 = json.dumps(data3)
            data5 = f"{data4}"
            # print(data5)
            print("change container configuration")
            cmd = ["lxc","query", "--request", "PATCH", f"/1.0/instances/{i}","--data",data5]
            result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output1 = result.stdout
            net_cfg4 = t1.render(net_cfg3)
            with open("interfaces.tmp","w") as f1:
                f1.write(net_cfg4)
            cmd = ["lxc", "file" , "push", "interfaces.tmp",  f"{i}/etc/network/interfaces"]
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
    

def check_arg(argv):
    list_of_cmd=["create","start","delete","stop","del","lbr"]
    if len(argv) < 3:
        print("lxc_client.py [command] <config_file>")
        exit(1)
    file1 = argv[2]
    cmd1 = argv[1]
    filepath = pathlib.Path(file1)
    if not filepath.exists() or not filepath.is_file():
        print(f"file {file1} is not a file or doesn't exist")
        exit(1)
    print(f"reading {file1}")
    with open(file1) as f1:
        d0 = f1.read()
    d1 = yaml.load(d0,Loader=yaml.FullLoader)
    if cmd1 not in list_of_cmd:
        print(f"command {cmd1} is not yet implemented")
        exit(1)
    d1['cmd']=cmd1
    return d1

# main function
d1 = check_arg(sys.argv)
if d1['cmd']=='create':
    create_lxc(d1)
if d1['cmd'] in ['del','delete']:
    delete_lxc(d1)
if d1['cmd']=='start':
    start_lxc(d1)
if d1['cmd']=='stop':
    stop_lxc(d1)
if d1['cmd']=='lbr':
    list_bridge(d1)
