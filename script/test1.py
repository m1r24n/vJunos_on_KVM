#!/usr/bin/env python3
import subprocess
import xmltodict
import json

cmd ="virsh capabilities"
# result = subprocess.check_output(cmd,shell=True)
#result1 = result.decode()
#print(xmltodict.parse(subprocess.check_output(cmd,shell=True).decode()).keys())
# result2 = json.loads(json.dumps(xmltodict.parse(result1)))
# result2 = json.loads(json.dumps(xmltodict.parse(result1)))
# print(result2['capabilities']['host']['cpu']['model'])
print(xmltodict.parse(subprocess.check_output(cmd,shell=True).decode())['capabilities']['host']['cpu']['model'])