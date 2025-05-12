#!/bin/bash
export LXC_NAME=client1
export BR=ovs0
export VLAN=202
export ETH0v4=192.168.202.11/24
export ETH0v6=fc00:dead:beef:a202::1000:11/64
export GWv4=192.168.202.254
export GWv6=fc00:dead:beef:a202::1


echo "Creating VM ${LXC_NAME}"
lxc copy client ${LXC_NAME}
lxc query --request PATCH /1.0/instances/${LXC_NAME} --data "{
  \"devices\": {
    \"eth0\" :{
       \"name\": \"eth0\",
       \"nictype\": \"bridged\",
       \"parent\": \"${BR}\",
       \"vlan\" : \"${VLAN}\",
       \"type\": \"nic\"
    }
  }
}"
echo "push configuration into node ${LXC_NAME}"
cat << EOF | tee ./interface.conf
auto eth0
iface eth0 inet static
    address ${ETH0v4}
    mtu 1500
    gateway ${GWv4}
iface eth0 inet6 static
    address ${ETH0v6}
    mtu 1500
    # gateway ${GWv6}
EOF

lxc file push ./interface.conf ${LXC_NAME}/etc/network/interfaces
cat << EOF | tee ./resolv.conf
nameserver 8.8.8.8
nameserver 8.8.4.4
EOF
lxc file push ./resolv.conf ${LXC_NAME}/etc/resolv.conf
