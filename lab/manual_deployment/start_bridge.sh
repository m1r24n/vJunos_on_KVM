#!/bin/bash
for i in link{1..4}
do
    sudo ip link add dev $i type bridge
    sudo ip link set dev $i up
done
