sudo hostname r4
hostname | sudo tee /etc/hostname
cat << EOF | sudo  tee /etc/netplan/01_net.yaml
network:
  version: 2
  ethernets:
    eth0:
      dhcp4: true
      dhcp6: true
    eth1:
      dhcp4: false
      dhcp6: false
      addresses: [ 10.1.100.3/31]
      mtu: 9000
    eth2:
      dhcp4: false
      dhcp6: false
      addresses: [ 10.1.100.7/31]
      mtu: 9000
    eth3:
      dhcp4: false
      dhcp6: false
      addresses: [ 10.1.100.9/31]
      mtu: 9000
    lo:
      addresses: [ 10.1.255.4/32]
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
net.mpls.conf.eth1.input=1
net.mpls.conf.eth2.input=1
net.mpls.conf.eth3.input=1
EOF

sudo sysctl -f 
sudo sed -i -e "s/isisd=no/isisd=yes/"  /etc/frr/daemons
sudo sed -i -e "s/bgpd=no/bgpd=yes/"  /etc/frr/daemons
sudo systemctl restart frr

cat << EOF | tee frr.conf
interface eth1
 ip router isis net1
 isis circuit-type level-2-only
 isis network point-to-point
 mpls enable
exit
!
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
 net 49.0001.0001.0001.0004.00
exit
!
end
EOF
sudo vtysh -c "copy frr.conf running-config"
sudo vtysh -c "write mem"

