# configuration for ipv4/ipv6 EVPN/VxLAN

## leaf1

### /etc/netplan/01_net.yaml
    cat << EOF | sudo tee -a /etc/netplan/01_net.yaml
        vlans:
            vlan111:
                link: eth1
                id: 111
        tunnels:
            vxlan1001:
                mode: vxlan
                local: 10.1.255.1
                id: 1001
                mac-learning: false
                port: 4789
            vxlan111:
                mode: vxlan
                local: 10.1.255.1
                id: 111
                mac-learning: false
                port: 4789
        bridges:
            br111:
                dhcp4: no
                dhcp6: no
                interfaces: 
                - vxlan1001
                - vxlan111
                - vlan111
                accept-ra: no
                addresses:
                - 192.168.111.1/24
                - fc00:dead:beef:a111::1/64
        vrfs:
            vrf1001:
                table: 1001
                addresses: [ 127.0.0.1/8 ]
                interfaces:
                - br111
    EOF

### /etc/frr/frr.conf

    cat << EOF | sudo tee -a /etc/frr/frr.conf
        vrf vrf1001
            vni 1001
        exit-vrf
        router bgp 4200000001
            neighbor fabric peer-group
            neighbor fabric update-source 10.1.255.1
            neighbor fabric capability extended-nexthop
            neighbor 10.1.255.11 remote-as 4200000001
            neighbor 10.1.255.11 peer-group fabric
            neighbor 10.1.255.12 remote-as 4200000001
            neighbor 10.1.255.12 peer-group fabric
            !
            address-family ipv4 unicast
                no neighbor 10.1.255.11 activate
                no neighbor 10.1.255.12 activate
            exit-address-family
            !
            address-family l2vpn evpn
                neighbor fabric activate
                advertise-all-vni
                advertise-svi-ip
                advertise ipv4 unicast
                advertise ipv6 unicast
                vni 111
                    rd 10.1.255.1:111
                    route-target import 1000:111
                    route-target export 1000:111
                exit-vni
            exit-address-family
            !
        exit
        router bgp 4200000001 vrf vrf1001
            !
            address-family ipv4 unicast
                redistribute connected
            exit-address-family
            !
            address-family ipv6 unicast
                
            exit-address-family
            !
            address-family l2vpn evpn
                advertise ipv4 unicast
                advertise ipv6 unicast
            exit-address-family
        exit
        !
    EOF



## leaf2

### /etc/netplan/01_net.yaml

    cat << EOF | sudo tee -a /etc/netplan/01_net.yaml
        vlans:
            vlan121:
                link: eth1
                id: 121
        tunnels:
            vxlan1001:
                mode: vxlan
                local: 10.1.255.2
                id: 1001
                mac-learning: false
                port: 4789
            vxlan121:
                mode: vxlan
                local: 10.1.255.2
                id: 121
                mac-learning: false
                port: 4789
        bridges:
            br121:
                dhcp4: no
                dhcp6: no
                interfaces: 
                - vxlan1001
                - vxlan121
                - vlan121
                accept-ra: no
                addresses:
                - 192.168.121.1/24
                - fc00:dead:beef:a121::1/64
        vrfs:
            vrf1001:
                table: 1001
                addresses: [ 127.0.0.1/8 ]
                interfaces:
                - br111
    EOF


### /etc/frr/frr.conf

    cat << EOF | sudo tee -a /etc/frr/frr.conf
        vrf vrf1001
            vni 1001
        exit-vrf
        router bgp 4200000001
            neighbor fabric peer-group
            neighbor fabric update-source 10.1.255.2
            neighbor fabric capability extended-nexthop
            neighbor 10.1.255.11 remote-as 4200000001
            neighbor 10.1.255.11 peer-group fabric
            neighbor 10.1.255.12 remote-as 4200000001
            neighbor 10.1.255.12 peer-group fabric
            !
            address-family ipv4 unicast
                no neighbor 10.1.255.11 activate
                no neighbor 10.1.255.12 activate
            exit-address-family
            !
            address-family l2vpn evpn
                neighbor fabric activate
                advertise-all-vni
                advertise-svi-ip
                advertise ipv4 unicast
                advertise ipv6 unicast
                vni 121
                    rd 10.1.255.2:121
                    route-target import 1000:121
                    route-target export 1000:121
                exit-vni
                exit-address-family
            exit
            !
            router bgp 4200000001 vrf vrf1001
                !
                address-family ipv4 unicast
                redistribute connected
                exit-address-family
                !
                address-family ipv6 unicast
                redistribute connected
                exit-address-family
                !
                address-family l2vpn evpn
                advertise ipv4 unicast
                advertise ipv6 unicast
                exit-address-family
        exit
        !
    EOF

# leaf 3
    cat << EOF | sudo tee -a /etc/netplan/01_net.yaml
        vlans:
            vlan111:
                link: eth1
                id: 111
        tunnels:
            vxlan111:
                mode: vxlan
                local: 10.1.255.3
                id: 111
                mac-learning: false
                port: 4789
        bridges:
            br111:
                dhcp4: no
                dhcp6: no
                interfaces: 
                - vxlan111
                - vlan111
                accept-ra: no
    EOF

    cat << EOF | sudo tee -a /etc/frr/frr.conf
        router bgp 4200000001
            neighbor fabric peer-group
            neighbor fabric update-source 10.1.255.3
            neighbor fabric capability extended-nexthop
            neighbor 10.1.255.11 remote-as 4200000001
            neighbor 10.1.255.11 peer-group fabric
            neighbor 10.1.255.12 remote-as 4200000001
            neighbor 10.1.255.12 peer-group fabric
            !
            address-family ipv4 unicast
                no neighbor 10.1.255.11 activate
                no neighbor 10.1.255.12 activate
            exit-address-family
            !
            address-family l2vpn evpn
                neighbor fabric activate
                advertise-all-vni
                vni 111
                    rd 10.1.255.3:111
                    route-target import 1000:111
                    route-target export 1000:111
                exit-vni
                advertise-svi-ip
            exit-address-family
        exit
    EOF

# leaf 4
    cat << EOF | sudo tee -a /etc/netplan/01_net.yaml
        vlans:
            vlan121:
                link: eth1
                id: 121
        tunnels:
            vxlan121:
                mode: vxlan
                local: 10.1.255.4
                id: 121
                mac-learning: false
                port: 4789
        bridges:
            br121:
                dhcp4: no
                dhcp6: no
                interfaces: 
                - vxlan121
                - vlan121
                accept-ra: no
    EOF

    cat << EOF | sudo tee -a /etc/frr/frr.conf
        router bgp 4200000001
            neighbor fabric peer-group
            neighbor fabric update-source 10.1.255.4
            neighbor fabric capability extended-nexthop
            neighbor 10.1.255.11 remote-as 4200000001
            neighbor 10.1.255.11 peer-group fabric
            neighbor 10.1.255.12 remote-as 4200000001
            neighbor 10.1.255.12 peer-group fabric
            !
            address-family ipv4 unicast
                no neighbor 10.1.255.11 activate
                no neighbor 10.1.255.12 activate
            exit-address-family
            !
            address-family l2vpn evpn
                neighbor fabric activate
                advertise-all-vni
                vni 121
                    rd 10.1.255.4:121
                    route-target import 1000:121
                    route-target export 1000:121
                exit-vni
                advertise-svi-ip
            exit-address-family
        exit
    EOF

## core1
### /etc/frr/frr.conf
    cat << EOF | sudo tee -a /etc/frr/frr.conf
        router bgp 4200000001
            neighbor fabric peer-group
            neighbor fabric update-source 10.1.255.11
            neighbor fabric capability extended-nexthop
            neighbor 10.1.255.1 remote-as 4200000001
            neighbor 10.1.255.1 peer-group fabric
            neighbor 10.1.255.2 remote-as 4200000001
            neighbor 10.1.255.2 peer-group fabric
            neighbor 10.1.255.3 remote-as 4200000001
            neighbor 10.1.255.3 peer-group fabric
            neighbor 10.1.255.4 remote-as 4200000001
            neighbor 10.1.255.4 peer-group fabric
            !
            !
            address-family ipv4 unicast
                no neighbor fabric activate
            exit-address-family
            !
            address-family l2vpn evpn
                neighbor fabric activate
                neighbor fabric route-reflector-client
            exit-address-family
        exit
    EOF




## core2
### /etc/frr/frr.conf
    cat << EOF | sudo tee -a /etc/frr/frr.conf
        router bgp 4200000001
            neighbor fabric peer-group
            neighbor fabric update-source 10.1.255.12
            neighbor fabric capability extended-nexthop
            neighbor 10.1.255.1 remote-as 4200000001
            neighbor 10.1.255.1 peer-group fabric
            neighbor 10.1.255.2 remote-as 4200000001
            neighbor 10.1.255.2 peer-group fabric
            neighbor 10.1.255.3 remote-as 4200000001
            neighbor 10.1.255.3 peer-group fabric
            !
            address-family ipv4 unicast
                no neighbor fabric activate
            exit-address-family
            !
            address-family l2vpn evpn
                neighbor fabric activate
                neighbor fabric route-reflector-client
            exit-address-family
        exit
    EOF