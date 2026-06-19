#!/usr/bin/env python3
from jnpr.junos import Device
from lxml import etree
import sys, os

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


d1 = {
    'junos_login': {
        'user':'admin',
        'password':'pass01'
        },
    'config_dir': "config",
    'vm': 
    {
        'sw1': {'ip_address':'192.168.250.11' },
        'sw2': {'ip_address':'192.168.250.12' }
    }
}
get_junos_config(d1,'sw1')