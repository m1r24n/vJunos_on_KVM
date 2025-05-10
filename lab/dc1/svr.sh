#!/bin/bash
VM=svr3
DISK=/disk2/vm/dc1/${VM}.img
IMG=/disk2/images/debian-12-generic-amd64.qcow2
CDROM=/disk2/images/seed.iso
VLAN=111
porte0=l3p3
porte1=l4p3
qemu-img create -b ${IMG} -f qcow2 -F qcow2 ${DISK}
virt-install --name ${VM} \
    --disk ${DISK},device=disk \
    --disk ${CDROM},device=cdrom \
    --ram 2048 --vcpu 1  \
    --osinfo debian12 \
    --network=bridge:${porte0},model=e1000 \
    --network=bridge:${porte1},model=e1000 \
    --xml "./devices/interface[1]/target/@dev=${VM}_e0" \
    --xml "./devices/interface[2]/target/@dev=${VM}_e1" \
    --console pty,target_type=serial \
    --noautoconsole \
    --hvm --accelerate  \
    --vnc  \
    --virt-type=kvm  \
    --import \
    --boot hd

sleep 2
for i in ${VM}_e{0..1}
do
echo "setting brport ${i}"
echo 16388 | sudo tee /sys/class/net/${i}/brport/group_fwd_mask
done

for i in ${porte0} ${porte1}
do
echo "setting bridge ${i}"
echo 65528 | sudo tee /sys/class/net/${i}/bridge/group_fwd_mask
done


