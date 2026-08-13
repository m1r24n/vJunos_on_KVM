#!/usr/bin/env bash
echo seting $1 to $2
echo $2 | sudo tee cat /sys/class/net/$1/brport/group_fwd_mask
