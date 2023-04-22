#!/bin/bash
for i in ge{0..5}
do
        #echo creating bridge $i
		#		sudo ip link add $i type bridge
        echo 0x400c | sudo tee  /sys/class/net/${i}/bridge/group_fwd_mask
        #sudo ip link set dev $i up
done

