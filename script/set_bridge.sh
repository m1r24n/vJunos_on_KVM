#!/bin/bash
virsh domiflist $1 | tail -n +4 > /tmp/vmbridgelist.txt
sed -i '/^$/d' /tmp/vmbridgelist.txt
# cat /tmp/vmbridgelist.txt
while IFS= read -r line
do
INTERFACE=`echo $line | awk '{ print $1 }'`
NTYPE=`echo $line | awk '{ print $2 }'`
BRIDGE=`echo $line | awk '{ print $3 }'`
if [ "$NTYPE" == "bridge" ]; then
# change MTU to higher value
RUNME="ip link set dev "$INTERFACE" mtu 9200"
echo $RUNME
eval $RUNME
# enable LLDP and 802.1x on bridge
RUNME="echo 65528 > /sys/class/net/"$BRIDGE"/bridge/group_fwd_mask"
echo $RUNME
eval $RUNME
# enable LACP on link
RUNME="echo 16388 > /sys/class/net/"$INTERFACE"/brport/group_fwd_mask"
echo $RUNME
eval $RUNME
fi
done < /tmp/vmbridgelist.txt
num=0
while IFS= read -r line
do
INTERFACE=`echo $line | awk '{ print $1 }'`
NTYPE=`echo $line | awk '{ print $2 }'`
BRIDGE=`echo $line | awk '{ print $3 }'`
if [ "$NTYPE" == "bridge" ]; then
MTU=`cat /sys/class/net/$BRIDGE/mtu`
if [ "$MTU" != "9200" ]; then
echo 'Warning! Bridge:'$BRIDGE' did not follow new MTU setting of
interface:'$INTERFACE' check other interfaces attached to same bridge and correct
please!'
num=1
fi
fi
done < /tmp/vmbridgelist.txt
exit $num
