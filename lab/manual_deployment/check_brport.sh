#!/bin/bash
for i in $@
do
result=`sudo cat /sys/class/net/${1}/brport/group_fwd_mask`
echo "brport $i $result"
done
