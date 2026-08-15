#!/bin/bash
for i in $@
do
    result=`sudo cat /sys/class/net/${i}/bridge/group_fwd_mask`
    echo "bridge $i $result"
done
