#!/bin/bash
VM=svr2
DISK=/data1/vm/topo7/${VM}.img
CDROM=/data1/vm/seed.iso
virt-install --name ${VM} \
    --disk ${DISK},device=disk \
    --disk ${CDROM},device=cdrom \
    --ram 2048 --vcpu 1  \
    --osinfo ubuntu22.04 \
    --network=bridge:l3p2,model=e1000 \
    --network=bridge:l4p2,model=e1000 \
    --console pty,target_type=serial \
    --noautoconsole \
    --hvm --accelerate  \
    --vnc  \
    --virt-type=kvm  \
    --import \
    --boot hd

