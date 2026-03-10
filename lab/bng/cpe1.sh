#!/bin/bash
VM=cpe1
IMG=/disk2/vm/bng/${VM}.qcow2
virt-install --name ${VM} \
	--disk ${IMG},device=disk,bus=virtio \
	--ram 256 --vcpu 1  \
    --osinfo alpinelinux3.12 \
	--network bridge=cpe1_e0,model=virtio \
	--network bridge=bng1_ge0,model=virtio,virtualport_type=openvswitch \
    --xml './devices/interface[2]/vlan/tag/@id=1001' \
	--console pty,target_type=serial \
	--noautoconsole \
	--hvm --accelerate  \
	--vnc  \
	--virt-type=kvm  \
	--boot hd --import
