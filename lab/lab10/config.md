# node configuration 

## R1 configuration 

    root@r1:/etc/frr# cat /etc/netplan/01_net.yaml 
    network:
        version: 2
        ethernets:
            lo:
                addresses: [ 10.1.255.1/32, fc00:dead:Beef:ffff::1/128]
            eth0:
                dhcp4: false
                dhcp6: true
                addresses: [ 192.168.250.11/24]
            eth1:
                dhcp4: false
                dhcp6: false
            eth2:
                mtu: 9000
                addresses: [ 10.1.255.128/31, fc00:dead:Beef:ffff::80/127]
            eth3:
                mtu: 9000
                addresses: [ 10.1.255.130/31, fc00:dead:Beef:ffff::82/127]
        tunnels:
            vxlan101:
                mode: vxlan
                local: 10.1.255.1
                id: 101
                mac-learning: false
                port: 4789
        bridges:
            br-eth1:
                interfaces:
                    - vxlan101
                    - eth1

    root@r1:/etc/frr# cat /etc/frr/frr.conf
    frr version 10.5.1
    frr defaults traditional
    hostname r1
    log syslog informational
    service integrated-vtysh-config
    !
    router bgp 4200000001
        no bgp ebgp-requires-policy
        neighbor 10.1.255.2 remote-as 4200000002
        neighbor 10.1.255.2 ebgp-multihop
        neighbor 10.1.255.2 update-source 10.1.255.1
    exit
    !
    router ospf
        network 10.1.255.0/24 area 0
    exit
    !
    interface eth2
        ip ospf network point-to-point
    exit
    !
    interface eth3
        ip ospf network point-to-point
    exit
    !
    interface lo
        ip ospf passive
    exit


## R2 configuration 

    root@r2:/etc/frr# cat /etc/netplan/01_net.yaml 
    network:
        version: 2
        ethernets:
            lo:
                addresses: [ 10.1.255.2/32,fc00:dead:Beef:ffff::2/128]
            eth0:
                dhcp4: false
                dhcp6: true
                addresses: [ 192.168.250.12/24]
            eth1:
                dhcp4: false
                dhcp6: false
            eth2:
                mtu: 9000
                addresses: [ 10.1.255.132/31, fc00:dead:Beef:ffff::82/127]
            eth3:
                mtu: 9000
                addresses: [ 10.1.255.134/31, fc00:dead:Beef:ffff::84/127]
        tunnels:
            vxlan101:
                mode: vxlan
                local: 10.1.255.2
                id: 101
                mac-learning: false
                port: 4789
        bridges:
            br-eth1:
                interfaces:
                    - vxlan101
                    - eth1

    root@r2:/etc/frr# cat /etc/frr/frr.conf
    frr version 10.5.1
    frr defaults traditional
    hostname r2
    log syslog informational
    service integrated-vtysh-config
    !
    router bgp 4200000002
        no bgp ebgp-requires-policy
        neighbor 10.1.255.1 remote-as 4200000001
        neighbor 10.1.255.1 ebgp-multihop
        neighbor 10.1.255.1 update-source 10.1.255.2
    exit
    !
    router ospf
        network 10.1.255.0/24 area 0
    exit
    !
    interface eth2
        ip ospf network point-to-point
    exit
    !
    interface eth3
        ip ospf network point-to-point
    exit
    !
    interface lo
        ip ospf passive
    exit

    !

## R3 configuration 

    root@r3:/etc/frr# cat /etc/netplan/01_net.yaml 
    network:
        version: 2
        ethernets:
            lo:
                addresses: [ 10.1.255.3/32,fc00:dead:Beef:ffff::3/128]
            eth0:
                dhcp4: false
                dhcp6: true
                addresses: [ 192.168.250.11/24]
            eth1:
                mtu: 9000
                addresses: [ 10.1.255.129/31, fc00:dead:Beef:ffff::81/127]
            eth2:
                mtu: 9000
                addresses: [ 10.1.255.133/31, fc00:dead:Beef:ffff::83/127]
    

    root@r3:/etc/frr# cat /etc/frr/frr.conf
    frr version 10.5.1
    frr defaults traditional
    hostname r3
    log syslog informational
    service integrated-vtysh-config
    !
    router ospf
        network 10.1.255.0/24 area 0
    exit
    !
    interface eth1
        ip ospf network point-to-point
    exit
    !
    interface eth2
        ip ospf network point-to-point
    exit
    !
    interface lo
        ip ospf passive
    exit

    !

## R4 configuration 

    root@r3:/etc/frr# cat /etc/netplan/01_net.yaml 
    network:
        version: 2
        ethernets:
            lo:
                addresses: [ 10.1.255.4/32,fc00:dead:Beef:ffff::4/128]
            eth0:
                dhcp4: false
                dhcp6: true
                addresses: [ 192.168.250.14/24]
            eth1:
                mtu: 9000
                addresses: [ 10.1.255.131/31, fc00:dead:Beef:ffff::81/127]
            eth2:
                mtu: 9000
                addresses: [ 10.1.255.135/31, fc00:dead:Beef:ffff::83/127]

    root@r3:/etc/frr# cat /etc/frr/frr.conf
    frr version 10.5.1
    frr defaults traditional
    hostname r4
    log syslog informational
    service integrated-vtysh-config
    !
    router ospf
        network 10.1.255.0/24 area 0
    exit
    !
    interface eth1
        ip ospf network point-to-point
    exit
    !
    interface eth2
        ip ospf network point-to-point
    exit
    !
    interface lo
        ip ospf passive
    exit
