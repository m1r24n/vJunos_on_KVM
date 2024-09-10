#!/bin/bash
LXC=c1a
BR=ovs1
VLAN=103
echo "changing container ${LXC}"
lxc query --request PATCH /1.0/instances/${LXC} --data "{
  \"devices\": {
     \"eth0\" :{
       \"name\": \"eth0\",
       \"nictype\": \"bridged\",
       \"parent\": \"${BR}\",
       \"vlan\": \"${VLAN}\",
       \"type\": \"nic\"
   }
  }
}"
