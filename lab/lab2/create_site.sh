#!/bin/bash
# create router container
YOURIP=0
MYIP=`expr ${YOURIP} + 1`
for i in {1..3}
do
OVS=pe${i}_ge0
BR=site${i}
VLAN=101
LXC=ce${i}
echo "Creating bridge ${BR}"
sudo ip link add dev ${BR} type bridge 
sudo ip link set dev ${BR} up
sudo sysctl -w net.ipv6.conf.${BR}.disable_ipv6=1
echo "create router ${LXC} "
lxc copy router ${LXC}
echo "changing container ${LXC}"
lxc query --request PATCH /1.0/instances/${LXC} --data "{
  \"devices\": {
    \"eth0\" :{
       \"name\": \"eth0\",
       \"nictype\": \"bridged\",
       \"parent\": \"${OVS}\",
       \"vlan\" : \"${VLAN}\",
       \"type\": \"nic\"
    },
    \"eth1\" :{
       \"name\": \"eth1\",
       \"nictype\": \"bridged\",
       \"parent\": \"${BR}\",
       \"type\": \"nic\"
    }
  }
}"

echo "changing containers${LXC}"
cat << EOF | tee interfaces
auto eth0
iface eth0 inet static
    address 172.16.255.${MYIP}/31
    mtu 1500
auto eth1
iface eth1 inet static
    address 192.168.${i}.1/24
    mtu 1500
iface eth0 inet6 static
    address fc00:dead:beef:ffff::${MYIP}/127
iface eth1 inet6 static
    address fc00:dead:beef:a10${i}::1/64
EOF

cat << EOF | tee frr.conf 
frr defaults traditional
hostname ${LXC}
log syslog informational
ipv6 forwarding
service integrated-vtysh-config
!
interface eth1
ipv6 nd prefix fc00:dead:beef:a10${i}::/64
no ipv6 nd suppress-ra
exit
router bgp 420000000${i}
no bgp ebgp-requires-policy
neighbor 172.16.255.${YOURIP} remote-as 4200001000
neighbor fc00:dead:beef:ffff::${YOURIP} remote-as 4200001000
!
address-family ipv4 unicast
network 192.168.${i}.0/24
exit-address-family
!
address-family ipv6 unicast
network fc00:dead:beef:a10${i}::/64
neighbor fc00:dead:beef:ffff::${YOURIP} activate
exit-address-family
exit
!
EOF

echo "Creating dhcp configuration"
cat << EOF | tee dnsmasq.conf
dhcp-range=192.168.${i}.11,192.168.${i}.100,255.255.255.0,2h
dhcp-option=option:router,192.168.${i}.1
dhcp-option=option:dns-server,192.168.${i}.1
domain=local.lan
local=/local.lan/
EOF

YOURIP=`expr $MYIP + 1`
MYIP=`expr ${YOURIP} + 1`



echo "push configuration into node ${LXC}"
lxc file push interfaces  ${LXC}/etc/network/interfaces
lxc file push frr.conf  ${LXC}/etc/frr/frr.conf
lxc file push dnsmasq.conf ${LXC}/etc/dnsmasq.conf

done


