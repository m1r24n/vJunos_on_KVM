#!/usr/bin/env python3
import subprocess,json
# cmd1 = ["sudo", "show", "runningconfiguration", "all"]
# result = subprocess.run(cmd1, capture_output=True, text=True, check=True)
# result1 = json.loads(result)
cmd="sudo show runningconfiguration all"
result=json.loads(subprocess.check_output(cmd,shell=True).decode())
intf  = result['INTERFACE']
bgp_neigh = result['BGP_NEIGHBOR']
list_intf = [ i for i in intf if '|' in i] 
for i in list_intf:
    intf,ipaddress = i.split('|')
    #cmd1=f"sudo config interface ip remove {intf} {ipaddress}"

    cmd1_list=["sudo", "config", "interface", "ip", "remove",intf,ipaddress]
    cmd1  = " ".join(cmd1_list)
    print(f"executing \"{cmd1}\"")
    result = subprocess.run(cmd1_list,check=True)
for i in bgp_neigh.keys():
    cmd1_list = ["sudo","config","bgp","remove","neighbor", i]
    cmd1  = " ".join(cmd1_list)
    print(f"executing \"{cmd1}\"")
    result = subprocess.run(cmd1_list,check=True)

# remove bgp neighbor sudo config bgp  remove neighbor

