#!/bin/bash
for i in $@
do
echo 0xfff8 | sudo tee /sys/class/net/${i}/bridge/group_fwd_mask
done
