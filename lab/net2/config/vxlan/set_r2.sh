sudo hostname r2
hostname | sudo tee /etc/hostname
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
    eth2:
      dhcp4: false
      dhcp6: false
      addresses: [ 10.1.100.4/31]
      mtu: 9000
    eth3:
      dhcp4: false
      dhcp6: false
      addresses: [ 10.1.100.6/31]
      mtu: 9000
    lo:
      addresses: [ 10.1.255.2/32]
  vlans:
    eth1vlan101:
      link: eth1
      id: 101
      addresses: [ 10.1.112.1/24]
    eth1vlan102:
      link: eth1
      id: 102
      addresses: [ 10.1.122.1/24]
    eth1vlan103:
      link: eth1
      id: 103
    eth1vlan104:
      link: eth1
      id: 104
  vrfs:
    cust1:
      interfaces:
      - eth1vlan101
      table: 1
    cust2:
      interfaces:
      - eth1vlan102
      table: 2
  bridges:
    br103:
      interfaces:
        - vxlan2103
        - eth1vlan103
  tunnels:
    vxlan2103:
      mode: vxlan
      local: 10.1.255.2
      id: 2103
      mac-learning: false
      port: 4789
EOF
sudo netplan apply

sudo sysctl -f 
sudo sed -i -e "s/isisd=no/isisd=yes/"  /etc/frr/daemons
sudo sed -i -e "s/bgpd=no/bgpd=yes/"  /etc/frr/daemons
sudo systemctl restart frr

cat << EOF | tee frr.conf
!
interface eth2
 ip router isis net1
 isis circuit-type level-2-only
 isis network point-to-point
exit
!
interface eth3
 ip router isis net1
 isis circuit-type level-2-only
 isis network point-to-point
exit
!
interface lo
 ip router isis net1
 isis circuit-type level-2-only
 isis passive
exit
!
router bgp 4200000002
 bgp router-id 10.1.255.2
 no bgp ebgp-requires-policy
 neighbor 10.1.255.1 remote-as 4200000001
 neighbor 10.1.255.1 ebgp-multihop 16
 neighbor 10.1.255.1 update-source lo
 neighbor 10.1.255.1 capability extended-nexthop
 !
 address-family l2vpn evpn
  neighbor 10.1.255.1 activate
  advertise-all-vni
  vni 2103
   rd 10.1.255.2:103
   route-target import 2103:103
   route-target export 2103:103
  exit-vni
  advertise-svi-ip
 exit-address-family
exit
!
router isis net1
 net 49.0001.0001.0001.0002.00
exit
!
end
EOF
sudo vtysh -c "copy frr.conf running-config"
sudo vtysh -c "write mem"

