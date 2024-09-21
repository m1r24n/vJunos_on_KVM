#!/bin/bash
OVS=pe2_g0
VLAN=101
CONT=client1
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
