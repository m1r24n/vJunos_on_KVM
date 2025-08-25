#!/bin/bash
for i in {1..3}
do
lxc stop ce${i}cs2
lxc rm ce${i}cs2
sudo ip link set dev site${i}cs2 down
sudo ip link del dev site${i}cs2 
done
