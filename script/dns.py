#!/usr/bin/env python3
import subprocess
cmd="resolvectl status | grep DNS| grep 'DNS Servers:'"
# cmd="ip -6 route show  | grep default"
result = subprocess.check_output(cmd,shell=True)
dns = result.decode().strip().split()[2:][0]
#dns1 = [ x.strip() for x in dns] 
print(dns)
