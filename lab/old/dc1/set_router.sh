#!/bin/bash
export LXC_NAME=gw
export INTBR=l5p2
export EXTBR=ovs1
export VLAN=111
export ETH0v4=192.168.255.0/31
export ETH0v6=fc00:deed:beef:ffff::0/127
export ETH1v4=192.168.111.201/24
export ETH1v6=fc00:dead:beef:a111::1000:f201/64 
export GWv4=192.168.111.254
export GWv6=fc00:dead:beef:a111::1


echo "Creating VM ${LXC_NAME}"
lxc copy router ${LXC_NAME}
lxc query --request PATCH /1.0/instances/${LXC_NAME} --data "{
  \"devices\": {
    \"eth0\" :{
       \"name\": \"eth0\",
       \"nictype\": \"bridged\",
       \"parent\": \"${INTBR}\",
       \"type\": \"nic\"
    },
    \"eth1\" :{
       \"name\": \"eth1\",
       \"nictype\": \"bridged\",
       \"parent\": \"${EXTBR}\",
       \"vlan\" : \"${VLAN}\",
       \"type\": \"nic\"
    }
  }
}"
echo "push configuration into node ${LXC_NAME}"
cat << EOF | tee ./interface.conf
auto eth0
auto eth0.1001
iface eth0.1001 inet static
    address ${ETH0v4}
    mtu 1500
    vlan-raw-device eth0
	vlan_id 1001
iface eth0.1001 inet6 static
    address ${ETH0v6}
    mtu 1500
    vlan-raw-device eth0
	vlan_id 1001
auto eth1
iface eth1 inet static
    address ${ETH1v4}
    mtu 1500
    gateway ${GWv4}
iface eth1 inet6 static
    address ${ETH1v6}
    mtu 1500
    gateway ${GWv6}
EOF

lxc file push ./interface.conf ${LXC_NAME}/etc/network/interfaces
cat << EOF | tee ./resolv.conf
nameserver 8.8.8.8
nameserver 8.8.4.4
EOF
lxc file push ./resolv.conf ${LXC_NAME}/etc/resolv.conf
