# configuration for SW1

    set interfaces ge-0/0/0 unit 0 family inet address 10.1.0.0/31
    set interfaces ge-0/0/1 unit 0 family inet address 10.1.0.2/31
    set interfaces ge-0/0/4 unit 0 family ethernet-switching interface-mode trunk
    set interfaces ge-0/0/4 unit 0 family ethernet-switching vlan members all
    set interfaces irb unit 11 family inet address 10.1.11.1/24
    set interfaces irb unit 12 family inet address 10.1.12.1/24
    set interfaces lo0 unit 0 family inet address 10.1.255.1/32
    set policy-options policy-statement from_local term 1 from route-filter 10.1.11.0/24 orlonger
    set policy-options policy-statement from_local term 1 from route-filter 10.1.12.0/24 orlonger
    set policy-options policy-statement from_local term 1 then accept
    set routing-options autonomous-system 4200000001
    set protocols bgp group to_sw2 export from_local
    set protocols bgp group to_sw2 neighbor 10.1.0.1 peer-as 4200000002
    set protocols bgp group to_sw2 neighbor 10.1.0.3 peer-as 4200000002
    set protocols bgp multipath
    set vlans vlan11 vlan-id 11
    set vlans vlan11 l3-interface irb.11
    set vlans vlan12 vlan-id 12
    set vlans vlan12 l3-interface irb.12

# configuration SW2
    set interfaces ge-0/0/0 unit 0 family inet address 10.1.0.1/31
    set interfaces ge-0/0/1 unit 0 family inet address 10.1.0.3/31
    set interfaces ge-0/0/4 unit 0 family ethernet-switching interface-mode trunk
    set interfaces ge-0/0/4 unit 0 family ethernet-switching vlan members all
    set interfaces irb unit 21 family inet address 10.1.21.1/24
    set interfaces irb unit 22 family inet address 10.1.22.1/24
    set interfaces lo0 unit 0 family inet address 10.1.255.2/32
    set policy-options policy-statement from_local term 1 from route-filter 10.1.21.0/24 orlonger
    set policy-options policy-statement from_local term 1 from route-filter 10.1.22.0/24 orlonger
    set policy-options policy-statement from_local term 1 then accept
    set routing-options autonomous-system 4200000002
    set protocols bgp group to_sw1 export from_local
    set protocols bgp group to_sw1 neighbor 10.1.0.0 peer-as 4200000001
    set protocols bgp group to_sw1 neighbor 10.1.0.2 peer-as 4200000001
    set protocols bgp multipath
    set vlans vlan21 vlan-id 21
    set vlans vlan21 l3-interface irb.21
    set vlans vlan22 vlan-id 22
    set vlans vlan22 l3-interface irb.22


# configuration for SW3     

    sudo config interface ip add Ethernet0 10.1.0.4/31
    sudo config interface ip add Ethernet4 10.1.0.6/31
    sudo config interface ip remove Loopback0 10.1.0.1/32
    sudo config interface ip add Loopback0 10.1.255.3/32
    sudo config vlan add 31
    sudo config vlan add 32
    sudo config interface ip add Vlan31 10.1.31.1/24
    sudo config interface ip add Vlan32 10.1.32.1/24
    sudo config vlan  member add 31  Ethernet16
    sudo config vlan  member add 32  Ethernet16

    router bgp 4200000003
        no bgp ebgp-requires-policy
        neighbor 10.1.0.5 remote-as 4200000004
        neighbor 10.1.0.7 remote-as 4200000004
        !
        address-family ipv4 unicast
            network 10.1.31.0/24
            network 10.1.32.0/24
        exit-address-family
    exit


# configuration for SW4

    sudo config interface ip add Ethernet0 10.1.0.5/31
    sudo config interface ip add Ethernet4 10.1.0.7/31
    sudo config interface ip remove Loopback0 10.1.0.1/32
    sudo config interface ip add Loopback0 10.1.255.4/32
    sudo config vlan add 41
    sudo config vlan add 42
    sudo config interface ip add Vlan41 10.1.41.1/24
    sudo config interface ip add Vlan42 10.1.42.1/24
    sudo config vlan  member add 41  Ethernet16
    sudo config vlan  member add 42  Ethernet16

    router bgp 4200000004
        no bgp ebgp-requires-policy
        neighbor 10.1.0.4 remote-as 4200000003
        neighbor 10.1.0.6 remote-as 4200000003
        !
        address-family ipv4 unicast
            network 10.1.41.0/24
            network 10.1.42.0/24
        exit-address-family
    exit



service integrated-vtysh-config
!
no ip prefix-list DEFAULT_IPV4 seq 5 permit 0.0.0.0/0
no ip prefix-list PL_LoopbackV4 seq 5 permit 10.1.0.1/32
!
no ipv6 prefix-list DEFAULT_IPV6 seq 5 permit ::/0
!
no route-map ALLOW_LIST_DEPLOYMENT_ID_0_V4
!
no route-map ALLOW_LIST_DEPLOYMENT_ID_0_V6
!
no route-map CHECK_IDF_ISOLATION

!
no route-map FROM_BGP_PEER_V4
!
rno oute-map FROM_BGP_PEER_V4
!
no route-map FROM_BGP_PEER_V4 
no route-map FROM_BGP_PEER_V6
no route-map RM_SET_SRC
no route-map TO_BGP_PEER_V4
no route-map TO_BGP_PEER_V6
!
no bgp community-list standard allow_list_default_community
no ip protocol bgp route-map RM_SET_SRC
ip nht resolve-via-default
ipv6 nht resolve-via-default
