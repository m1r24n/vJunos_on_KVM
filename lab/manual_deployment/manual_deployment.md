# steps to deploy vjunos 

## step 1, create bridge

    sudo ip link add dev wan1 type bridge
    sudo ip link set dev wan1 up
    sudo ip link add dev wan2 type bridge
    sudo ip link set dev wan2 up
    sudo ovs-vsctl add-br lan1
    sudo ovs-vsctl add-br lan2

## step 2, copy xml file for each node, and edit it

## step 3, copy disk image

    qemu-img create -b /disk2/vm/images/vJunos-router-26.2R1.7.qcow2 -f qcow2 -F qcow2 node1.qcow2
    qemu-img create -b /disk2/vm/images/vJunos-router-26.2R1.7.qcow2 -f qcow2 -F qcow2 node2.qcow2

## step 4, define the VM

    virsh define node1.xml
    virsh define node2.xml

## step 5, start the VM

    virsh start node1
    virsh start node2

## step 6, create client



### config for node1

    delete interfaces
    delete chassis
    delete protocols
    delete system processes
    set system host-name node1
    set system root-authentication encrypted-password "$6$KU9LTpxh$fnNqcTdZjxwdnp5miSHTSHTqwjpw118NBuH97U4LAH0y0YIgM0.LqDbGOIQzDlC.S/p1PoSh2f/M3A/WQmnzJ0"
    set system login user admin class super-user
    set system login user admin authentication encrypted-password "$6$lJpja7Uv$6yGwxclcFolThB6aQFNM5z6QLVDfEqnrkgjOXZm3TtblUSZxTL3zLZpK2/cKv3a9gAajwc2exR480Tgcdj1xH/"
    set system services ssh sftp-server
    set interfaces ge-0/0/1 mtu 9000
    set interfaces ge-0/0/1 unit 0 family inet address 10.0.0.0/31
    set interfaces ge-0/0/2 mtu 9000
    set interfaces ge-0/0/2 unit 0 family inet address 10.0.0.2/31
    set interfaces fxp0 unit 0 family inet address 192.168.250.11/24
    set protocols lldp interface ge-0/0/1
    set protocols lldp interface ge-0/0/2

### config for node1

    delete interfaces
    delete chassis
    delete protocols
    delete system processes
    set system host-name node2
    set system root-authentication encrypted-password "$6$KU9LTpxh$fnNqcTdZjxwdnp5miSHTSHTqwjpw118NBuH97U4LAH0y0YIgM0.LqDbGOIQzDlC.S/p1PoSh2f/M3A/WQmnzJ0"
    set system login user admin class super-user
    set system login user admin authentication encrypted-password "$6$lJpja7Uv$6yGwxclcFolThB6aQFNM5z6QLVDfEqnrkgjOXZm3TtblUSZxTL3zLZpK2/cKv3a9gAajwc2exR480Tgcdj1xH/"
    set system services ssh sftp-server
    set interfaces ge-0/0/1 mtu 9000
    set interfaces ge-0/0/1 unit 0 family inet address 10.0.0.1/31
    set interfaces ge-0/0/2 mtu 9000
    set interfaces ge-0/0/2 unit 0 family inet address 10.0.0.3/31
    set interfaces fxp0 unit 0 family inet address 192.168.250.12/24
    set protocols lldp interface ge-0/0/1
    set protocols lldp interface ge-0/0/2

### configure bridge for LLDP

    echo 65528 | sudo tee /sys/class/net/wan1/bridge/group_fwd_mask ## from 0x0
    echo 65528 | sudo tee /sys/class/net/wan2/bridge/group_fwd_mask

### configure bridge for LACP

    # node1
    set chassis aggregated-devices ethernet device-count 8
    set interfaces ge-0/0/1 gigether-options 802.3ad ae0
    set interfaces ge-0/0/2 gigether-options 802.3ad ae0
    set interfaces ae0 aggregated-ether-options lacp active
    set interfaces ae0 mtu 9000
    set interfaces ae0 unit 0 family inet address 10.0.0.0/31

    # node2
    set chassis aggregated-devices ethernet device-count 8
    set interfaces ge-0/0/1 gigether-options 802.3ad ae0
    set interfaces ge-0/0/2 gigether-options 802.3ad ae0
    set interfaces ae0 aggregated-ether-options lacp active
    set interfaces ae0 mtu 9000
    set interfaces ae0 unit 0 family inet address 10.0.0.1/31

    echo 16388 | sudo tee /sys/class/net/${i}/brport/group_fwd_mask ## from 0x0

    for i in vnet4 vnet5 vnet12 vnet13
    do
        echo 16388 | sudo tee /sys/class/net/${i}/brport/group_fwd_mask
    done

## remove all

    virsh destroy node1
    virsh undefine node1
    virsh destroy node2
    virsh destroy node2
    for i in 1 2 
    do
       sudo ip link set dev wan${i} down
       sudo ip link del dev wan${i}
       sudo ovs-vsctl del-br lan${i}
    done