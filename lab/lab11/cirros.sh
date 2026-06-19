#!/bin/bash
VM=cirros1
DISK=${VM}.img
# CDROM=/vm/images/ubuntu-24.04.1-live-server-amd64.iso
BRIDGE=sw1_ge0
VLAN=111
virt-install --name ${VM} \
    --disk ./${DISK},device=disk \
    --ram 256 --vcpu 1  \
    --osinfo cirros0.5.2 \
    --network=bridge:${BRIDGE},model=virtio,virtualport_type=openvswitch \
    --xml "./devices/interface/vlan/tag/@id=${VLAN}" \
    --xml "./devices/interface/target/@dev=${VM}_e0" \
    --console pty,target_type=serial \
    --noautoconsole \
    --hvm --accelerate  \
    --vnc  \
    --virt-type=kvm  \
    --import \
    --boot hd

    # --xml "./devices/interface/vlan/tag/@id=${VLAN}" \
