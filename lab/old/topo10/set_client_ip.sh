#!/bin/bash
#OVS=pe2_g0
#VLAN=101
CONT=client2
#echo "changing container ${CONT}"
#lxc query --request PATCH /1.0/instances/${CONT} --data "{
#  \"devices\": {
#    \"eth0\" :{
#       \"name\": \"eth0\",
#       \"nictype\": \"bridged\",
#       \"parent\": \"${OVS}\",
#       \"vlan\" : \"${VLAN}\",
#       \"type\": \"nic\"
#    }
#  }
#}"

echo "changing container ${CONT}"
cat << EOF | tee interfaces
auto eth0
iface eth0 inet static
    address 172.16.20.202/24
    gateway 172.16.20.1
    mtu 1500
EOF
echo "push configuration into node ${CONT}"
lxc file push interfaces ${CONT}/etc/network/interfaces
