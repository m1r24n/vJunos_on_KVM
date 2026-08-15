#!/bin/bash
VM=c1ubuntu
MAC=52:54:00:0e:75:f4
IPv4=10.0.10.11/24
IPv6=fc00:dead:beef:a010::1000:11/64
GWv4=10.0.10.1
GWv6=fc00:dead:beef:a010::1
sudo hostname ${VM}
hostname | sudo tee /etc/hostname
cat << EOF | sudo tee /etc/netplan/01_net.yaml
network:
  ethernets:
    eth0:
      dhcp4: no
    eth1:
      dhcp4: no
  bonds:
    bond0:
      macaddress: ${MAC}
      interfaces:
        - eth0
        - eth1
      parameters:
         mode: 802.3ad
      addresses: [ ${IPv4} , ${IPv6}]
      routes:
      - to: 0.0.0.0/0
        via: ${GWv4}
      nameservers:
        addresses: [8.8.8.8,8.8.4.4]
EOF
uuidgen | sed -e "s/-//g" | sudo tee /etc/machine-id
sudo netplan apply

