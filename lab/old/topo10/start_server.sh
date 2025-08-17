#!/bin/bash
OVS=pe1_g0
VLAN=101
CONT=server
echo "changing container ${CONT}"
lxc query --request PATCH /1.0/instances/${CONT} --data "{
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

echo "changing container ${CONT}"
cat << EOF | tee interfaces
auto eth0
iface eth0 inet static
    address 172.16.10.10/24
    gateway 172.16.10.1
    mtu 1500
EOF
echo "push configuration into node ${CONT}"
lxc file push interfaces ${CONT}/etc/network/interfaces
