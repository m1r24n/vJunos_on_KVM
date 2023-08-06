virt-install --name r2 \
    --disk /data1/vm/topo4/r2_re_0.img,device=disk,bus=ide,format=qcow2 \
    --disk /data1/vm/topo4/r2_re_1.img,device=disk,bus=ide,format=qcow2 \
    --disk /data1/vm/topo4/r2_re_2.img,device=disk,bus=ide,format=qcow2 \
    --cpu IvyBridge,+erms,+smep,+fsgsbase,+pdpe1gb,+rdrand,+f16c,+osxsave,+dca,+pcid,+pdcm,+xtpr,+tm2,+est,+smx,+vmx,+ds_cpl,+monitor,+dtes64,+pbe,+tm,+ht,+ss,+acpi,+ds,+vme \
    --ram 1024 --vcpu 1  \
    --osinfo freebsd13.0 \
    --network bridge=sw1,model=virtio,virtualport_type=openvswitch \
    --network bridge=r2Int,model=virtio \
    --xml './devices/interface[1]/target/@dev=r2fxp0' \
        --xml './devices/interface[1]/vlan/tag/@id=101' \
        --xml './devices/interface[]/target/@dev=r2Int' \
    --console pty,target_type=serial \
    --noautoconsole --hvm --accelerate  --vnc \
    --virt-type=kvm --boot hd --noreboot

