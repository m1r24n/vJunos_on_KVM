# VLAN configuration 

## sw1

    set interfaces ge-0/0/0 unit 0 family ethernet-switching interface-mode trunk
    set interfaces ge-0/0/0 unit 0 family ethernet-switching vlan members vlan111
    set interfaces ge-0/0/0 unit 0 family ethernet-switching vlan members vlan112
    set interfaces irb unit 111 family inet address 192.168.111.1/24
    set interfaces irb unit 112 family inet address 192.168.112.1/24
    set protocols ospf area 0.0.0.0 interface irb.111
    set protocols ospf area 0.0.0.0 interface irb.112
    set vlans vlan111 vlan-id 111
    set vlans vlan111 l3-interface irb.111
    set vlans vlan112 vlan-id 112
    set vlans vlan112 l3-interface irb.112



## sw2
    vlan 121,122
    interface vlan 121
      ip address 192.168.121.1/24
      ip ospf 1 area 0.0.0.0
    interface vlan 122
      ip address 192.168.122.1/24
      ip ospf 1 area 0.0.0.0
    interface 1/1/1
      no routing
      vlan trunk allowed 121,122
