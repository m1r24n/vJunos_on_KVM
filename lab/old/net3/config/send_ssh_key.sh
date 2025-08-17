#!/bin/bash
for i in 01 02 11 12 13
do
ssh-copy-id ubuntu@192.168.171.2${i}
done
