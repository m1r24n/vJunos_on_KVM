sudo ip link add cust1 type vrf table 1
sudo ip link add cust2 type vrf table 2
sudo ip link set eth1vlan101 vrf cust1
sudo ip link set eth1vlan102 vrf cust2
sudo ip link set dev cust1 up
sudo ip link set dev cust2 up