#!/bin/bash
# create router container
YOURIP=8
MYIP=`expr ${YOURIP} + 1`
for i in {1..3}
do
for j in {1..2}
do
VLAN=103
LXC=c${j}site${i}cs3
OVS=pe${i}_ge0
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
    address 172.16.20.${i}${j}/24
    mtu 1500
iface eth0 inet6 static
    address fc00:dead:beef:aa20::1000:${i}${j}/64
EOF


echo "push configuration into node ${LXC}"
lxc file push interfaces  ${LXC}/etc/network/interfaces
lxc start ${LXC}

done
done


