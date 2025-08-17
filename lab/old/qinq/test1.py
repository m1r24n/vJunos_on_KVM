#!/usr/bin/env python3
import os
portname = 'sw1ge0'
file1=f"/sys/class/net/{portname}/brport/group_fwd_mask"
if os.path.exists(file1):
    print(f"file {file1} exist")
else:
    print(f"file {file1} doesn't exist")
