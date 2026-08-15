#!/bin/bash
for i in $@
do
echo 0x4004 | sudo tee /sys/class/net/${i}/brport/group_fwd_mask
done
