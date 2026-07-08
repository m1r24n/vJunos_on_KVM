#!/bin/bash
for i in lan{1..2} wan{1..2}
do
  sudo ip link add dev $i type bridge
  sudo ip link set dev $i up 
done
