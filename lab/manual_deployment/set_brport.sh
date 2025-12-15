#!/bin/bash
echo 0x4004 | sudo tee /sys/class/net/${1}/brport/group_fwd_mask
