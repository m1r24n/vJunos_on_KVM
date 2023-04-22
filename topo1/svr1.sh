#!/bin/bash
VM=svr1a
DISK=/disk2/vm/vex/image/${VM}.img
virt-install --name ${VM} \
	--disk ${DISK},device=disk,bus=virtio \
	--ram 2048 --vcpu 1  --osinfo linux2020 \
	--network bridge=ge0,model=e1000 \
	--network bridge=ge1,model=e1000 \
	--console pty,target_type=serial \
	--noautoconsole \
	--hvm --accelerate  \
	--vnc  \
	--virt-type=kvm  \
	--boot hd
