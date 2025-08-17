#!/bin/bash
for i in 1 2 
do
ssh ubuntu@192.168.171.20${i} "sudo hostname s${i}; hostname | sudo tee /etc/hostname"
done

for i in 1 2 3
do
ssh ubuntu@192.168.171.21${i} "sudo hostname l${i}; hostname | sudo tee /etc/hostname"
done