#!/usr/bin/env python3
from jnpr.junos import Device
from lxml import etree
hostname = "192.168.250.11"
junos_username = 'admin'
junos_password = 'pass01'
dev = Device(host=hostname, user=junos_username, passwd=junos_password)
try:
    dev.open()
    print("Successfully open connection")
    print(dev.facts)
    data = dev.rpc.get_config(options={'format':'set'})
    print (etree.tostring(data, encoding='unicode', pretty_print=True))
    # print (data)
except ConnectError as err:
    print ("Cannot connect to device: {0}".format(err))
    sys.exit(1)
except Exception as err:
    print (err)
    sys.exit(1)
