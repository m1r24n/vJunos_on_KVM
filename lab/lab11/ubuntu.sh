#!/bin/bash
VM=ubuntu
DISK=${VM}.img
CDROM=/vm/images/seed.iso
# CDROM=/vm/images/ubuntu-24.04.1-live-server-amd64.iso
BRIDGE=ovs0
VLAN=111
virt-install --name ${VM} \
    --disk ./${DISK},device=disk \
    --disk ${CDROM},device=cdrom \
    --ram 4096 --vcpu 1  \
    --osinfo ubuntu24.04 \
	--boot uefi,loader_secure=no \
    --network=bridge:${BRIDGE},model=virtio,virtualport_type=openvswitch \
    --xml "./devices/interface/target/@dev=${VM}_e0" \
    --console pty,target_type=serial \
    --noautoconsole \
    --hvm --accelerate  \
    --vnc  \
    --virt-type=kvm  \
    --import \
    --boot hd

    # --xml "./devices/interface/vlan/tag/@id=${VLAN}" \
