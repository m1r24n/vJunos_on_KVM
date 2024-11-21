#!/bin/bash
OVS=pe1_g0
VLAN=101
CONT=cl4
echo "changing container ${CONT}"
lxc query --request PATCH /1.0/instances/${CONT} --data "{
  \"devices\": {
    \"eth0\" :{
       \"name\": \"eth0\",
       \"nictype\": \"bridged\",
       \"parent\": \"${OVS}\",
       \"type\": \"nic\"
    }
  }
}"

echo "changing container ${CONT}"
cat << EOF | tee interfaces
auto eth0
iface eth0 inet static
    address 10.0.101.12/24
    gateway 10.0.101.1
    mtu 1500
EOF
echo "push configuration into node ${CONT}"
lxc file push interfaces ${CONT}/etc/network/interfaces

