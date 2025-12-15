#!/bin/bash
# create client LXC with VLAN

echo "create client ${LXC} "
lxc copy client ${LXC}
echo "changing container ${LXC}"
lxc query --request PATCH /1.0/instances/${LXC} --data "{
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

echo "changing containers${LXC}"
cat << EOF | tee interfaces
auto eth0
iface eth0 inet static
    address $IPV4
    gateway $GW4
    mtu 1500
iface eth0 inet6 static
    address $IPV6
    gateway $GW6
EOF


echo "push configuration into node ${LXC}"
lxc file push interfaces  ${LXC}/etc/network/interfaces
lxc start ${LXC}
