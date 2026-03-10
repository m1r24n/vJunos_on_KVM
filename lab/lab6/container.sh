#!/bin/bash

export LXC_NAME=client2v12
export VLAN=12
export OVS=sw2_ge4
export IPv4=192.168.12.12/24
export GWv4=192.168.12.254
export IPv6=fc00:dead:beef:a012::1000:12/64
export GWv6=fc00:dead:beef:a012::1

echo "Creating VM ${LXC_NAME}"
lxc copy client ${LXC_NAME}
lxc query --request PATCH /1.0/instances/${LXC_NAME} --data "{
  \"devices\": {
    \"eth0\" :{
       \"name\": \"eth0\",
       \"nictype\": \"bridged\",
       \"parent\": \"${OVS}\",
       \"vlan\" : \"${VLAN}\",
       \"type\": \"nic\"
    }
  }
}"
echo "push configuration into node ${LXC_NAME}"
cat << EOF | tee ./interface.conf
auto eth0
iface eth0 inet static
    address ${IPv4}
    mtu 1500
    gateway ${GWv4}
iface eth0 inet6 static
    address ${IPv6}
EOF

lxc file push ./interface.conf ${LXC_NAME}/etc/network/interfaces
cat << EOF | tee ./resolv.conf
nameserver 8.8.8.8
nameserver 8.8.4.4
EOF
lxc file push ./resolv.conf ${LXC_NAME}/etc/resolv.conf
lxc start ${LXC_NAME}



lxc launch alpine --name client -n br0

passwd root 
apk add openssh iperf
rc-update add sshd
service sshd start
cat << EOF | tee -a /etc/ssh/sshd_config
PermitRootLogin yes
EOF


lxc query --request PATCH /1.0/instances/lxc --data "{
  \"devices\": {
    \"eth0\" :{
       \"name\": \"eth0\",
       \"nictype\": \"bridged\",
       \"parent\": \"br0\",
       \"type\": \"nic\"
    }
  }
}"