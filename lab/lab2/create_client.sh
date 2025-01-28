#!/bin/bash
export LXC_NAME=cust2-cl2-v1
export VLAN=1
export OVS=c2sw1
export IPv4=192.168.100.2/24
export GWv4=192.168.100.254
export IPv6=fc00:dead:beef:a100::ffff:2/64
export GWv6=fc00:Dead:beef:A100::1


echo "Creating VM ${LXC_NAME}"
#       \"vlan\" : \"${VLAN}\",
lxc copy client ${LXC_NAME}
lxc query --request PATCH /1.0/instances/${LXC_NAME} --data "{
  \"devices\": {
    \"eth0\" :{
       \"name\": \"eth0\",
       \"nictype\": \"bridged\",
       \"parent\": \"${OVS}\",
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
    gateway ${GWv6}
EOF

lxc file push ./interface.conf ${LXC_NAME}/etc/network/interfaces
cat << EOF | tee ./resolv.conf
nameserver 8.8.8.8
nameserver 8.8.4.4
EOF
lxc file push ./interface.conf ${LXC_NAME}/etc/resolv.conf


