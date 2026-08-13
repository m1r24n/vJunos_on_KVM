#!/usr/bin/env bash
echo checking $1
cat /sys/class/net/$1/brport/group_fwd_mask
