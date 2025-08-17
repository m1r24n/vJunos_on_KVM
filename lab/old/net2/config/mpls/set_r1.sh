sudo hostname r1
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
      addresses: [ 10.1.100.0/31]
      mtu: 9000
    eth3:
      dhcp4: false
      dhcp6: false
      addresses: [ 10.1.100.2/31]
      mtu: 9000
    lo:
      addresses: [ 10.1.255.1/32]
  vlans:
    eth1vlan101:
      link: eth1
      id: 101
      addresses: [ 10.1.111.1/24]
    eth1vlan102:
      link: eth1
      id: 102
      addresses: [ 10.1.121.1/24]
  vrfs:
    cust1:
      table: 1
      interfaces:
      - eth1vlan101
    cust2:
      table: 2
      interfaces:
      - eth1vlan102
EOF

sudo netplan apply


cat << EOF | sudo tee /etc/modules-load.d/mpls.conf
mpls_router
mpls_gso
mpls_iptunnel
EOF

sudo systemctl stop systemd-modules-load.service
sudo systemctl start systemd-modules-load.service


cat << EOF | sudo tee -a /etc/sysctl.conf
net.mpls.platform_labels=1048575
net.mpls.conf.lo.input=1
net.mpls.conf.eth2.input=1
net.mpls.conf.eth3.input=1
EOF

sudo sysctl -f 
sudo sed -i -e "s/isisd=no/isisd=yes/"  /etc/frr/daemons
sudo sed -i -e "s/bgpd=no/bgpd=yes/"  /etc/frr/daemons
sudo systemctl restart frr

cat << EOF | tee frr.conf
interface eth2
 ip router isis net1
 isis circuit-type level-2-only
 isis network point-to-point
 mpls enable
exit
!
interface eth3
 ip router isis net1
 isis circuit-type level-2-only
 isis network point-to-point
 mpls enable
exit
!
interface lo
 ip router isis net1
 isis circuit-type level-2-only
 isis passive
 mpls enable
exit
!
router isis net1
 net 49.0001.0001.0001.0001.00
exit
!
router bgp 4200000001
 bgp router-id 10.1.255.1
 neighbor 10.1.255.2 remote-as 4200000001
 neighbor 10.1.255.2 update-source lo
 !
 address-family ipv4 vpn
  neighbor 10.1.255.2 activate
 exit-address-family
exit
!
router bgp 4200000001 vrf cust1
 !
 address-family ipv4 unicast
  redistribute connected
  label vpn export auto
  rd vpn export 100:1
  rt vpn both 100:1
  export vpn
  import vpn
 exit-address-family
exit
!
router bgp 4200000001 vrf cust2
 !
 address-family ipv4 unicast
  redistribute connected
  label vpn export auto
  rd vpn export 100:2
  rt vpn both 100:2
  export vpn
  import vpn
 exit-address-family
exit
!
mpls ldp
 router-id 10.1.255.1
 !
 address-family ipv4
  discovery transport-address 10.1.255.1
  !
  interface eth2
  exit
  !
  interface eth3
  exit
  !
 exit-address-family
 !
exit
!
end
EOF
sudo vtysh -c "copy frr.conf running-config"
sudo vtysh -c "write mem"

