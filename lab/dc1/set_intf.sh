#!/bin/bash
VM=svr3
MAC=52:54:00:03:7f:6f
IPv4=192.168.202.3/24
IPv6=fc00:dead:beef:a202::1000:3/64
GWv4=192.168.202.254
GWv6=fc00:dead:beef:a202::1
sudo hostname ${VM}
hostname | sudo tee /etc/hostname
cat << EOF | sudo tee /etc/netplan/50-cloud-init.yaml
network:
  ethernets:
    ens1:
      dhcp4: no
    ens2:
      dhcp4: no
  bonds:
    bond0:
      macaddress: ${MAC}
      interfaces:
        - ens1
        - ens2
      parameters:
         mode: 802.3ad
      addresses: [ ${IPv4} , ${IPv6}]
      routes:
      - to: 0.0.0.0/0
        via: ${GWv4}
#      - to: ::/0
#        via: ${GWv6}
      nameservers:
        addresses: [8.8.8.8,8.8.4.4]
EOF
uuidgen | sed -e "s/-//g" | sudo tee /etc/machine-id
sudo netplan apply