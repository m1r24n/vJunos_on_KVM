#!/bin/bash
for i in {1..2}
do
  sudo ip link add dev wan${i} type bridge
  sudo ip link set dev wan${i} up 
  sudo ovs-vsctl add-br lan${i}
done
