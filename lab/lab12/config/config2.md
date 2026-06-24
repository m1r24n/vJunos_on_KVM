# configuration for ipv4/ipv6 EVPN/VxLAN

## leaf1

### /etc/netplan/01_net.yaml
    cat << EOF | sudo tee -a /etc/netplan/01_net.yaml
        vlans:
            vlan111:
                link: eth1
                id: 111
            vlan112:
                link: eth1
                id: 112
        tunnels:
            vxlan111:
                mode: vxlan
                local: 10.1.255.1
                id: 111
                mac-learning: false
                port: 4789
            vxlan112:
                mode: vxlan
                local: 10.1.255.1
                id: 112
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
            br112:
                dhcp4: no
                dhcp6: no
                interfaces: 
                - vxlan112
                - vlan112
                accept-ra: no
    EOF

### /etc/frr/frr.conf

    cat << EOF | sudo tee -a /etc/frr/frr.conf
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
                vni 112
                    rd 10.1.255.1:112
                    route-target import 1000:112
                    route-target export 1000:112
                exit-vni
                vni 111
                    rd 10.1.255.1:111
                    route-target import 1000:111
                    route-target export 1000:111
                exit-vni
                advertise-svi-ip
            exit-address-family
        exit
        !
    EOF



## leaf2

### /etc/netplan/01_net.yaml

    cat << EOF | sudo tee -a /etc/netplan/01_net.yaml
        vlans:
            vlan111:
                link: eth1
                id: 111
            vlan112:
                link: eth1
                id: 112
        tunnels:
            vxlan111:
                mode: vxlan
                local: 10.1.255.2
                id: 111
                mac-learning: false
                port: 4789
            vxlan112:
                mode: vxlan
                local: 10.1.255.2
                id: 112
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
            br112:
                dhcp4: no
                dhcp6: no
                interfaces: 
                - vxlan112
                - vlan112
                accept-ra: no
    EOF


### /etc/frr/frr.conf

    cat << EOF | sudo tee -a /etc/frr/frr.conf
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
                vni 112
                    rd 10.1.255.2:112
                    route-target import 1000:112
                    route-target export 1000:112
                exit-vni
                vni 111
                    rd 10.1.255.2:111
                    route-target import 1000:111
                    route-target export 1000:111
                exit-vni
                advertise-svi-ip
            exit-address-family
        exit
    EOF

## leaf3

### /etc/netplan/01_net.yaml

    cat << EOF | sudo tee -a /etc/netplan/01_net.yaml
        vlans:
            vlan111:
                link: eth1
                id: 111
            vlan112:
                link: eth1
                id: 112
        tunnels:
            vxlan111:
                mode: vxlan
                local: 10.1.255.1
                id: 111
                mac-learning: false
                port: 4789
            vxlan112:
                mode: vxlan
                local: 10.1.255.1
                id: 112
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
            br112:
                dhcp4: no
                dhcp6: no
                interfaces: 
                - vxlan112
                - vlan112
                accept-ra: no
    EOF



### /etc/frr/frr.conf

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
                vni 112
                    rd 10.1.255.2:112
                    route-target import 1000:112
                    route-target export 1000:112
                exit-vni
                vni 111
                    rd 10.1.255.2:111
                    route-target import 1000:111
                    route-target export 1000:111
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

