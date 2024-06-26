#!/usr/bin/env python3
import yaml
from jinja2 import Template
import subprocess

vm1 = """---
name: sw1
disk: /data1/vm/vex/sw1.img
vcpu: 4
ram : 5120
cpu_model: IvyBridge
interfaces:
    mgmt:
        bridge: br0
        vlan: 101
        brtype: ovs
        index: 1
    ge0:
        bridge: link1
        index: 2
    ge1:
        bridge: link2
        index: 3
    ge2:
        bridge: link3
        index: 4
    ge4:
        bridge: link4
        index: 5
"""
d1 = yaml.load(vm1,Loader=yaml.FullLoader)
print(d1)

with open("vjunos.j2") as f1:
    template1 = f1.read()
    config1=Template(template1).render(d1)
    print(config1)
    subprocess.check_output(config1,shell=True)



