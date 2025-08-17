#!/bin/bash
source ../param.sh
VM=sw1
DEST=/disk2/vm/vex/image
DISK=${DEST}/${VM}.img
echo "Copying disk"
cp ${SOURCE} ${DISK}
echo "creating bridge"
for i in ge{0..5}
do
        echo creating bridge $i
				sudo ip link add $i type bridge
        # echo 0x400c | sudo tee  /sys/class/net/${i}/bridge/group_fwd_mask
        sudo ip link set dev $i up
done

# --cpu host-passthrough  \
virt-install --name ${VM} \
	--disk ${DISK},device=disk \
	--cpu IvyBridge,+vmx \
	--sysinfo system.product="VM-VEX" \
	--ram ${RAM} --vcpu ${VCPU}  \
	--osinfo ubuntu22.04 \
	--network bridge=br0,virtualport_type=openvswitch \
	--network bridge=ge0 \
	--network bridge=ge1 \
	--network bridge=ge2 \
	--network bridge=ge3 \
	--xml './devices/interface[1]/target/@dev=sw1fxp0' \
	--xml './devices/interface[1]/vlan/tag/@id=101' \
	--xml './devices/interface[2]/target/@dev=sw1ge0' \
	--xml './devices/interface[2]/mtu/@size=9500' \
	--xml './devices/interface[3]/target/@dev=sw1ge1' \
	--xml './devices/interface[3]/mtu/@size=9500' \
	--xml './devices/interface[4]/target/@dev=sw1ge2' \
	--xml './devices/interface[4]/mtu/@size=9500' \
	--xml './devices/interface[5]/target/@dev=sw1ge3' \
	--xml './devices/interface[5]/mtu/@size=9500' \
	--console pty,target_type=serial \
	--noautoconsole \
	--hvm --accelerate  \
	--vnc  \
	--virt-type=kvm  \
	--boot hd

VM=sw2
DISK=${DEST}/${VM}.img
echo "Copying disk"
cp ${SOURCE} ${DISK}

virt-install --name ${VM} \
	--disk ${DISK},device=disk \
	--cpu IvyBridge,+vmx \
	--sysinfo system.product="VM-VEX" \
	--ram ${RAM} --vcpu ${VCPU}  \
	--osinfo ubuntu22.04 \
	--network bridge=br0,virtualport_type=openvswitch \
	--network bridge=ge4 \
	--network bridge=ge5 \
	--network bridge=ge2 \
	--network bridge=ge3 \
	--xml './devices/interface[1]/target/@dev=sw2fxp0' \
	--xml './devices/interface[1]/vlan/tag/@id=101' \
	--xml './devices/interface[2]/target/@dev=sw2ge0' \
	--xml './devices/interface[2]/mtu/@size=9500' \
	--xml './devices/interface[3]/target/@dev=sw2ge1' \
	--xml './devices/interface[3]/mtu/@size=9500' \
	--xml './devices/interface[4]/target/@dev=sw2ge2' \
	--xml './devices/interface[4]/mtu/@size=9500' \
	--xml './devices/interface[5]/target/@dev=sw2ge3' \
	--xml './devices/interface[5]/mtu/@size=9500' \
	--console pty,target_type=serial \
	--noautoconsole \
	--hvm --accelerate  \
	--vnc  \
	--virt-type=kvm  \
	--boot hd
