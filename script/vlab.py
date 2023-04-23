#!/usr/bin/env python3
import lib1
import yaml
import sys
## main function

d1=lib1.check_argv(sys.argv)
if d1:
    # print(d1)
    lib1.is_bridge_defined(d1)
    lib1.is_vm_defined(d1)
    if d1['cmd'] == 'config':
        lib1.create_dhcp_tftp_config(d1)
    elif d1['cmd'] == 'addbr':
        lib1.add_bridge(d1)
    elif d1['cmd'] == 'create':
        lib1.create_vm(d1)
    elif d1['cmd'] == 'start':
        lib1.start_vm(d1)
    elif d1['cmd'] == 'del':
        lib1.delete_vm(d1)
    elif d1['cmd'] == 'stop':
        lib1.stop_vm(d1)