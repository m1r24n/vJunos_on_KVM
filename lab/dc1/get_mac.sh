#!/bin/bash
for i in spine{1..2} leaf{1..5}
do
mac=`virsh dumpxml $i | grep -m 1 "mac address" | sed -e "s/<//" | sed -e "s/>//" | sed -e "s/\///" | cut -f 2 -d "="`
echo "${i} : ${mac}"
done

