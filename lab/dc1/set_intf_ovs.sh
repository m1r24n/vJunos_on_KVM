#!/bin/bash
VM=svr4
MAC=52:54:00:17:9d:b1
IPv4=192.168.201.4/24
IPv6=fc00:dead:beef:a201::1000:4/64
GWv4=192.168.201.254
GWv6=fc00:dead:beef:a201::1
sudo hostname ${VM}
hostname | sudo tee /etc/hostname
cat << EOF | sudo tee /etc/netplan/50-cloud-init.yaml
network:
  ethernets:
    eth0:
      dhcp4: no
    eth0:
      dhcp4: no
  bonds:
    bond0:
      macaddress: ${MAC}
      interfaces:
        - ens1
        - ens2
      parameters:
         mode: 802.3ad
  bridges:
    ovs0:
      openvswitch: {}
      interfaces:
      - bond0
      addresses: [ ${IPv4} , ${IPv6}]
      routes:
      - to: 0.0.0.0/0
        via: ${GWv4}
      nameservers:
        addresses: [8.8.8.8,8.8.4.4]
EOF
uuidgen | sed -e "s/-//g" | sudo tee /etc/machine-id
sudo netplan apply