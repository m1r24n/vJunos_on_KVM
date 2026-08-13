# router configuration


## CRPD

    #!/usr/bin/env bash
    export NAME=$1
    export VER=$2
    if [ "${NAME}" == "" ];
    then
        echo "variable NAME is not defined"
        exit
    fi
    if [ "${VER}" == "" ];
    then
        echo "variable VER is not defined"
        exit
    fi
    sudo podman volume create ${NAME}-config
    sudo podman volume create ${NAME}-varlog
    sudo podman run --rm --detach --name ${NAME} -h ${NAME} \
        --net=host --privileged \
        -v ${NAME}-config:/config \
        -v ${NAME}-varlog:/var/log \
        -it localhost/crpd:${VER}
    

    chmod +x install_crpd.sh

    configure
    set routing-options autonomous-system 4200009001
    set protocols bgp group to_pe type internal
    set protocols bgp group to_pe local-address 10.1.255.15
    set protocols bgp group to_pe family inet any
    set protocols bgp group to_pe family inet6 labeled-unicast explicit-null
    set protocols bgp group to_pe family evpn signaling
    set protocols bgp group to_pe passive
    set protocols bgp group to_pe cluster 10.1.255.15
    set protocols bgp group to_pe allow 10.1.255.0/24
    set protocols isis interface enp2s0
    set protocols isis interface lo.0 passive
    set protocols isis level 1 disable
    set protocols isis level 2 wide-metrics-only
    set interfaces lo0 unit 0 family inet address 10.1.255.15/32
    set interfaces lo0 unit 0 family iso address 49.0001.0001.0015.00
    set routing-options rib inet.3 static route 0.0.0.0/0 discard
    set routing-options rib inet6.0 static route ::ffff:0.0.0.0/96 discard
    set routing-options rib inet6.3 static route ::/0 discard


## MPLS

### Routing

    R1 
    ----

    set interfaces ge-0/0/0 flexible-vlan-tagging
    set interfaces ge-0/0/0 encapsulation flexible-ethernet-services
    set interfaces ge-0/0/0 unit 101 vlan-id 101
    set interfaces ge-0/0/0 unit 101 family inet address 192.168.200.0/31
    set interfaces ge-0/0/0 unit 101 family inet6 address fc00:dead:beef:a200::0/127
    set interfaces ge-0/0/1 unit 0 family inet6
    set interfaces ge-0/0/2 unit 0 family inet6
    set policy-options policy-statement to_rr then next-hop self
    set routing-options autonomous-system 4200009001
    set protocols bgp group to_rr type internal
    set protocols bgp group to_rr local-address 10.1.255.1
    set protocols bgp group to_rr family inet any
    set protocols bgp group to_rr family inet6 labeled-unicast explicit-null
    set protocols bgp group to_rr family evpn signaling
    set protocols bgp group to_rr export to_rr
    set protocols bgp group to_rr neighbor 10.1.255.15
    set protocols bgp group to_ce1pe1 neighbor 192.168.200.1 peer-as 4200001001
    set protocols bgp group to_ce1pe1 neighbor fc00:dead:beef:a200::1 peer-as 4200001001
    set protocols mpls ipv6-tunneling

    R2
    ----
    set interfaces ge-0/0/0 flexible-vlan-tagging
    set interfaces ge-0/0/0 encapsulation flexible-ethernet-services
    set interfaces ge-0/0/0 unit 101 vlan-id 101
    set interfaces ge-0/0/0 unit 101 family inet address 192.168.200.2/31
    set interfaces ge-0/0/0 unit 101 family inet6 address fc00:dead:beef:a200::2/127

    set interfaces ge-0/0/1 unit 0 family inet6
    set interfaces ge-0/0/2 unit 0 family inet6
    set policy-options policy-statement to_rr then next-hop self
    set routing-options autonomous-system 4200009001
    set protocols bgp group to_rr type internal
    set protocols bgp group to_rr local-address 10.1.255.2
    set protocols bgp group to_rr family inet any
    set protocols bgp group to_rr family inet6 labeled-unicast explicit-null
    set protocols bgp group to_rr family evpn signaling
    set protocols bgp group to_rr export to_rr
    set protocols bgp group to_rr neighbor 10.1.255.15
    set protocols bgp group to_ce2pe2 neighbor 192.168.200.3 peer-as 4200001002
    set protocols bgp group to_ce2pe2 neighbor fc00:dead:beef:a200::3 peer-as 4200001002

    set protocols mpls ipv6-tunneling

    R3
    ----
    set interfaces ge-0/0/0 flexible-vlan-tagging
    set interfaces ge-0/0/0 encapsulation flexible-ethernet-services
    set interfaces ge-0/0/0 unit 101 vlan-id 101
    set interfaces ge-0/0/0 unit 101 family inet address 192.168.200.4/31
    set interfaces ge-0/0/0 unit 101 family inet6 address fc00:dead:beef:a200::4/127

    set interfaces ge-0/0/1 unit 0 family inet6
    set interfaces ge-0/0/2 unit 0 family inet6
    set policy-options policy-statement to_rr then next-hop self
    set routing-options autonomous-system 4200009001
    set protocols bgp group to_rr type internal
    set protocols bgp group to_rr local-address 10.1.255.3
    set protocols bgp group to_rr family inet any
    set protocols bgp group to_rr family inet6 labeled-unicast explicit-null
    set protocols bgp group to_rr family evpn signaling
    set protocols bgp group to_rr export to_rr
    set protocols bgp group to_rr neighbor 10.1.255.15
    set protocols bgp group to_ce2pe2 neighbor 192.168.200.5 peer-as 4200001003
    set protocols bgp group to_ce2pe2 neighbor fc00:dead:beef:a200::5 peer-as 4200001003

    set protocols mpls ipv6-tunneling



### L3VPN

    R1 
    ----

    set interfaces ge-0/0/0 unit 201 vlan-id 201
    set interfaces ge-0/0/0 unit 201 family inet address 192.168.200.0/31
    set interfaces ge-0/0/0 unit 201 family inet6 address fc00:dead:beef:a200::0/127
    set protocols bgp group to_rr family inet-vpn any
    set protocols bgp group to_rr family inet6-vpn any
    set routing-instances cust1 instance-type vrf
    set routing-instances cust1 protocols bgp group to_ce1pe1 neighbor 192.168.200.1 peer-as 4200002001
    set routing-instances cust1 protocols bgp group to_ce1pe1 neighbor fc00:dead:beef:a200::1 peer-as 4200002001
    set routing-instances cust1 vrf-table-label
    set routing-instances cust1 interface ge-0/0/0.201
    set routing-instances cust1 vrf-target target:65001:1001
    set routing-options route-distinguisher-id 10.1.255.1



    R2
    ----

    set interfaces ge-0/0/0 unit 201 vlan-id 201
    set interfaces ge-0/0/0 unit 201 family inet address 192.168.200.2/31
    set interfaces ge-0/0/0 unit 201 family inet6 address fc00:dead:beef:a200::2/127
    set protocols bgp group to_rr family inet-vpn any
    set protocols bgp group to_rr family inet6-vpn any
    set routing-instances cust1 instance-type vrf
    set routing-instances cust1 protocols bgp group to_ce1pe1 neighbor 192.168.200.3 peer-as 4200002002
    set routing-instances cust1 protocols bgp group to_ce1pe1 neighbor fc00:dead:beef:a200::3 peer-as 4200002002
    set routing-instances cust1 vrf-table-label
    set routing-instances cust1 interface ge-0/0/0.201
    set routing-instances cust1 vrf-target target:65001:1001
    set routing-options route-distinguisher-id 10.1.255.2

    R3
    ----

    set interfaces ge-0/0/0 unit 201 vlan-id 201
    set interfaces ge-0/0/0 unit 201 family inet address 192.168.200.4/31
    set interfaces ge-0/0/0 unit 201 family inet6 address fc00:dead:beef:a200::4/127
    set protocols bgp group to_rr family inet-vpn any
    set protocols bgp group to_rr family inet6-vpn any
    set routing-instances cust1 instance-type vrf
    set routing-instances cust1 protocols bgp group to_ce1pe1 neighbor 192.168.200.5 peer-as 4200002003
    set routing-instances cust1 protocols bgp group to_ce1pe1 neighbor fc00:dead:beef:a200::5 peer-as 4200002003
    set routing-instances cust1 vrf-table-label
    set routing-instances cust1 interface ge-0/0/0.201
    set routing-instances cust1 vrf-target target:65001:1001
    set routing-options route-distinguisher-id 10.1.255.3

### EVPN

    R1 
    ----

    set interfaces ge-0/0/0 unit 301 vlan-id 301
    set interfaces ge-0/0/0 unit 301 encapsulation vlan-bridge
    set interfaces ge-0/0/0 unit 301 family bridge
    set routing-instances evpn1 instance-type evpn
    set routing-instances evpn1 vlan-id 301
    set routing-instances evpn1 protocols evpn
    set routing-instances evpn1 interface ge-0/0/0.301
    set routing-instances evpn1 vrf-target target:65001:3001


    R2 
    ----

    set interfaces ge-0/0/0 unit 301 vlan-id 301
    set interfaces ge-0/0/0 unit 301 encapsulation vlan-bridge
    set interfaces ge-0/0/0 unit 301 family bridge
    set routing-instances evpn1 instance-type evpn
    set routing-instances evpn1 vlan-id 301
    set routing-instances evpn1 protocols evpn
    set routing-instances evpn1 interface ge-0/0/0.301
    set routing-instances evpn1 vrf-target target:65001:3001


    R2 (mac-vrf)
    set routing-instances evpn1 instance-type mac-vrf
    set routing-instances evpn1 protocols evpn encapsulation mpls
    set routing-instances evpn1 bridge-domains br1 vlan-id 301
    set routing-instances evpn1 bridge-domains br1 interface ge-0/0/0.301
    set routing-instances evpn1 service-type vlan-based
    set routing-instances evpn1 interface ge-0/0/0.301
    set routing-instances evpn1 vrf-target target:65001:3001


    R3
    ----

    set interfaces ge-0/0/0 unit 301 vlan-id 301
    set interfaces ge-0/0/0 unit 301 encapsulation vlan-bridge
    set interfaces ge-0/0/0 unit 301 family bridge
    set routing-instances evpn1 instance-type evpn
    set routing-instances evpn1 vlan-id 301
    set routing-instances evpn1 protocols evpn
    set routing-instances evpn1 interface ge-0/0/0.301
    set routing-instances evpn1 vrf-target target:65001:3001



### EVPN type 5

    R1 
    ----

    set interfaces ge-0/0/0 unit 211 vlan-id 211
    set interfaces ge-0/0/0 unit 211 family inet address 192.168.200.0/31
    set interfaces ge-0/0/0 unit 211 family inet6 address fc00:dead:beef:a200::0/127
    set routing-instances evpn2l3 instance-type vrf
    set routing-instances evpn2l3 protocols bgp group to_ce1pe1 neighbor 192.168.200.1 peer-as 4200003001
    set routing-instances evpn2l3 protocols bgp group to_ce1pe1 neighbor fc00:dead:beef:a200::1 peer-as 4200003001
    set routing-instances evpn2l3 vrf-table-label
    set routing-instances evpn2l3 interface ge-0/0/0.211
    set routing-instances evpn2l3 vrf-target target:65001:1211
    set routing-instances evpn2l3 protocols evpn ip-prefix-routes advertise direct-nexthop


    R2 / R3, EVPN type 2
    ----

    set interfaces ge-0/0/0 unit 211 vlan-id 211
    set interfaces ge-0/0/0 unit 211 encapsulation vlan-bridge
    set interfaces ge-0/0/0 unit 211 family bridge
    set routing-instances evpn2 instance-type evpn
    set routing-instances evpn2 vlan-id 211
    set routing-instances evpn2 protocols evpn
    set routing-instances evpn2 interface ge-0/0/0.211
    set routing-instances evpn2 vrf-target target:65001:3211

    R2/R3, EVPN type 5
    ---
    set interfaces irb unit 211 family inet address 172.16.102.1/24
    set interfaces irb unit 211 family inet6 address fc00:dead:Beef:a102::1/64
    set routing-instances evpn2l3 instance-type vrf
    set routing-instances evpn2l3 vrf-table-label
    set routing-instances evpn2l3 interface irb.211
    set routing-instances evpn2l3 vrf-target target:65001:1211
    set routing-instances evpn2l3 protocols evpn ip-prefix-routes advertise direct-nexthop
    set routing-instances evpn2 routing-interface irb.211

    




    
     






