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
      addresses: [ 10.1.100.6/31]
      mtu: 9000
    eth2:
      dhcp4: false
      dhcp6: false
      addresses: [ 10.1.100.8/31]
      mtu: 9000
    eth3:
      dhcp4: false
      dhcp6: false
      addresses: [ 10.1.100.10/31]
      mtu: 9000
    lo:
      addresses: [ 10.1.255.2/32]
EOF

sudo netplan apply

sudo sysctl -f 
sudo sed -i -e "s/isisd=no/isisd=yes/"  /etc/frr/daemons
sudo sed -i -e "s/bgpd=no/bgpd=yes/"  /etc/frr/daemons
sudo systemctl restart frr

cat << EOF | tee frr.conf
router bgp 4200000002
 bgp router-id 10.1.255.2
 no bgp ebgp-requires-policy
 neighbor underlay peer-group
 neighbor 10.1.100.7 remote-as 4200000011
 neighbor 10.1.100.7 peer-group underlay
 neighbor 10.1.100.9 remote-as 4200000012
 neighbor 10.1.100.9 peer-group underlay
 neighbor 10.1.100.11 remote-as 4200000013
 neighbor 10.1.100.11 peer-group underlay
 neighbor fabric peer-group
 neighbor fabric update-source lo
 neighbor fabric ebgp-multihop 2
 neighbor fabric capability extended-nexthop
 neighbor 10.1.255.11 remote-as 4200000011
 neighbor 10.1.255.11 peer-group fabric
 neighbor 10.1.255.12 remote-as 4200000012
 neighbor 10.1.255.12 peer-group fabric
 neighbor 10.1.255.13 remote-as 4200000013
 neighbor 10.1.255.13 peer-group fabric
 !
 address-family ipv4 unicast
  neighbor underlay activate
  network 10.1.255.2/32
 address-family l2vpn evpn
  neighbor fabric activate
 exit-address-family
exit
!
end
EOF
sudo vtysh -c "copy frr.conf running-config"
sudo vtysh -c "write mem"

