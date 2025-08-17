
sudo hostname svr1a
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
      macaddress: 52:54:00:08:a9:4d
      interfaces:
        - eth0
        - eth1
      parameters:
         mode: 802.3ad
      addresses: [ 10.1.11.10/24 ]
      gateway4: 10.1.11.1
EOF


sudo hostname svr2a
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
      macaddress: 52:54:00:91:5b:28
      interfaces:
        - eth0
        - eth1
      parameters:
         mode: 802.3ad
      addresses: [ 10.1.12.10/24 ]
      gateway4: 10.1.12.1
EOF