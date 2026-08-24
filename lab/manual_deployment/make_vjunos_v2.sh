#!/usr/bin/env bash
#!/usr/bin/env bash
if [ "$#" -lt 3 ];
then
    echo "make_vjunos.sh <vm_name> <disk_image> <br1> <br2> <br3> ..."
    exit
fi
VMNAME=$1
DISK=$2
shift
shift
# --cpu IvyBridge,+vmx \\
cat << EOF | tee start_vjunos.sh 
virt-install --name $VMNAME --disk $DISK,device=disk \\
    --cpu host-passthrough \\
    --ram 5120 --vcpu 4  \\
    --osinfo ubuntu22.04 \\
    --network=bridge:${1},model=virtio \\
    --xml "./devices/interface[1]/target/@dev=${VMNAME}_fxp0" \\
EOF

shift
j=2
k=0
for i in $@
do
cat << EOF | tee -a start_vjunos.sh
    --network=bridge:${i},model=virtio \\
    --xml "./devices/interface[${j}]/target/@dev=${VMNAME}_ge${k}" \\
EOF

j=`expr $j + 1`
k=`expr $k + 1`
done
cat << EOF | tee -a start_vjunos.sh
    --console pty,target_type=serial \\
    --noautoconsole --hvm --accelerate  --vnc \\
    --virt-type=kvm --boot hd  --import 
EOF

echo "Finish writing start_vjunos.sh"
