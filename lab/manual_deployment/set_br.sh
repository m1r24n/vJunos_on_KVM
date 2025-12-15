#!/bin/bash
echo 0xfff8 | sudo tee /sys/class/net/${1}/bridge/group_fwd_mask
