#!/bin/bash
for i in {1..3}
do
lxc stop ce${i}cs1
lxc rm ce${i}cs1
sudo ip link set dev site${i}cs1 down
sudo ip link del dev site${i}cs1 
done
