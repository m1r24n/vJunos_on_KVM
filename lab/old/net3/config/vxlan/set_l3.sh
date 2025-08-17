#!/bin/bash
cat << EOF | sudo tee /etc/netplan/01_net.yaml
network:
  version: 2
  ethernets:
    eth0:
      dhcp4: true
      dhcp6: true
    eth1:
      dhcp4: false
      dhcp6: false
      mtu: 9000
      addresses: [ 10.1.100.5/31]
    eth2:
      dhcp4: false
      dhcp6: false
      addresses: [ 10.1.100.11/31]
      mtu: 9000
    eth3:
      dhcp4: false
      dhcp6: false
      mtu: 9000
    eth4:
      dhcp4: false
      dhcp6: false
      mtu: 9000
    eth5:
      dhcp4: false
      dhcp6: false
      mtu: 9000
    lo:
      addresses: [ 10.1.255.13/32]
  vlans:
    eth3vlan101:
      link: eth1
      id: 101
    eth3vlan102:
      link: eth1
      id: 102
  bridges:
    br101:
      interfaces:
        - vxlan1101
        - eth3vlan101
  tunnels:
    vxlan1101:
      mode: vxlan
      local: 10.1.255.13
      id: 1101
      mac-learning: false
      port: 4789
EOF

sudo netplan apply

sudo sysctl -f 
#sudo sed -i -e "s/isisd=no/isisd=yes/"  /etc/frr/daemons
sudo sed -i -e "s/bgpd=no/bgpd=yes/"  /etc/frr/daemons
sudo systemctl restart frr

cat << EOF | tee frr.conf
!
router bgp 4200000013
 bgp router-id 10.1.255.13
 no bgp ebgp-requires-policy
 neighbor underlay peer-group
 neighbor 10.1.100.4 remote-as 4200000001
 neighbor 10.1.100.4 peer-group underlay
 neighbor 10.1.100.10 remote-as 4200000002
 neighbor 10.1.100.10 peer-group underlay
 neighbor fabric peer-group
 neighbor fabric update-source lo
 neighbor fabric ebgp-multihop 2
 neighbor fabric capability extended-nexthop
 neighbor 10.1.255.1 remote-as 4200000001
 neighbor 10.1.255.1 peer-group fabric
 neighbor 10.1.255.2 remote-as 4200000002
 neighbor 10.1.255.2 peer-group fabric
 !
 address-family ipv4 unicast
  neighbor underlay activate
  network 10.1.255.13/32
 address-family l2vpn evpn
  neighbor fabric activate
  advertise-all-vni
  vni 110
   rd 10.1.255.11:101
   route-target import 1101:101
   route-target export 1101:101
  exit-vni
  advertise-svi-ip
 exit-address-family
exit
!
end
EOF
sudo vtysh -c "copy frr.conf running-config"
sudo vtysh -c "write mem"

