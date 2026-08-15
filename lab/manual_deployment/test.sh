#!/usr/bin/env bash
if [ "$#" -lt 3 ];
then 
    echo "No argument"
    exit
fi
VMNAME=$1
DISK=$2
shift
shift
echo VM Name $VMNAME
echo disk Name $DISK
for i in $@
do
    echo $i
done
