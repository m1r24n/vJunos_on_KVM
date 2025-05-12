#!/bin/bash
VM=svr5
MAC=52:54:00:51:fb:60
IPv4eth0=10.1.101.1/24
IPv6eth0=fc00:dead:beef:a101::1000:1/64
IPv4eth1=10.1.102.1/24
IPv6eth1=fc00:dead:beef:a102::1000:1/64
sudo hostname ${VM}
hostname | sudo tee /etc/hostname
cat << EOF | sudo tee /etc/netplan/50-cloud-init.yaml
network:
  ethernets:
    eth0:
      dhcp4: no
      addresses: [ ${IPv4eth0} , ${IPv6eth0}]
    eth1:
      dhcp4: no
      addresses: [ ${IPv4eth1} , ${IPv6eth1}]
EOF
uuidgen | sed -e "s/-//g" | sudo tee /etc/machine-id
sudo netplan apply
