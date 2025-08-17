#!/bin/bash
porte0=l3p3
porte1=l4p3
VM=svr3
for i in ${VM}_e{0..1}
do
echo "setting brport ${i}"
echo 16388 | sudo tee /sys/class/net/${i}/brport/group_fwd_mask
done

for i in ${porte0} ${porte1}
do
echo "setting brudge ${i}"
echo 65528 | sudo tee /sys/class/net/${i}/bridge/group_fwd_mask
done

