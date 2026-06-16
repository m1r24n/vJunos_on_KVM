# VLAN configuration 

## sw1

    set interfaces ge-0/0/4 unit 0 family ethernet-switching interface-mode trunk
    set interfaces ge-0/0/4 unit 0 family ethernet-switching vlan members vlan111
    set interfaces irb unit 111 family inet address 192.168.111.1/24
    set protocols ospf area 0.0.0.0 interface irb.111
    set vlans vlan111 vlan-id 111
    set vlans vlan111 l3-interface irb.111

    set interfaces ge-0/0/4 unit 0 family ethernet-switching interface-mode trunk
    set interfaces ge-0/0/4 unit 0 family ethernet-switching vlan members vlan112
    set interfaces irb unit 112 family inet address 192.168.112.1/24
    set protocols ospf area 0.0.0.0 interface irb.112
    set vlans vlan112 vlan-id 112
    set vlans vlan112 l3-interface irb.112

## sw5
    set interfaces ge-0/0/4 unit 0 family ethernet-switching interface-mode trunk
    set interfaces ge-0/0/4 unit 0 family ethernet-switching vlan members vlan151
    set interfaces irb unit 151 family inet address 192.168.151.1/24
    set protocols ospf area 0.0.0.0 interface irb.151
    set vlans vlan151 vlan-id 151
    set vlans vlan151 l3-interface irb.151

## sw3
    vlan 131
    interface vlan 131
      ip address 192.168.131.1/24
      ip ospf 1 area 0.0.0.0
    interface 1/1/5
      no routing
      vlan trunk allowed 131

## sw4
    vlan 141,142
    interface vlan 141
      ip address 192.168.141.1/24
      ip ospf 1 area 0.0.0.0
    interface vlan 142
      ip address 192.168.142.1/24
      ip ospf 1 area 0.0.0.0
    interface 1/1/5
      no routing
      vlan trunk allowed 141,142
