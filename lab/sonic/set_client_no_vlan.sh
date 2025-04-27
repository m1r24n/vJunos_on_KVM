export LXC_NAME=pc2
export VLAN=1011
export OVS=l2p2
export IPv4=192.168.11.2/24
export GWv4=192.168.11.254
# export IPv6=192.168.11.102/24
# export GWv6=192.168.11.254


echo "Creating VM ${LXC_NAME}"
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
EOF

lxc file push ./interface.conf ${LXC_NAME}/etc/network/interfaces
cat << EOF | tee ./resolv.conf
nameserver 8.8.8.8
nameserver 8.8.4.4
EOF
lxc file push ./resolv.conf ${LXC_NAME}/etc/resolv.conf