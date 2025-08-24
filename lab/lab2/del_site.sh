#!/bin/bash
for i in {1..3}
do
lxc stop ce$i
lxc rm ce$i
sudo ip link set dev site$i down
sudo ip link del dev site$i 
done