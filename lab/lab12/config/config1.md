# configuration for ipv4/ipv6 with ISIS

## leaf1

### /etc/netplan/01_net.yaml

    vlans:
      vlan111:
        link: eth1
        id: 111
        addresses:
        - 192.168.111.1/24
        - fc00:Dead:Beef:a111::1/64
      vlan112:
        link: eth1
        id: 112
        addresses:
        - 192.168.112.1/24
        - fc00:Dead:Beef:a112::1/64

### /etc/frr/frr.conf

    interface vlan111
        ip router isis NET1
        ipv6 router isis NET1
    exit
    !
    interface vlan112
        ip router isis NET1
        ipv6 router isis NET1
    exit


## leaf2

### /etc/netplan/01_net.yaml

    vlans:
      vlan121:
        link: eth1
        id: 121
        addresses:
        - 192.168.121.1/24
        - fc00:Dead:Beef:a121::1/64
      vlan122:
        link: eth1
        id: 122
        addresses:
        - 192.168.122.1/24
        - fc00:Dead:Beef:a122::1/64

### /etc/frr/frr.conf

    interface vlan121
        ip router isis NET1
        ipv6 router isis NET1
    exit
    !
    interface vlan122
        ip router isis NET1
        ipv6 router isis NET1
    exit


## leaf3

### /etc/netplan/01_net.yaml

    vlans:
      vlan131:
        link: eth1
        id: 131
        addresses:
        - 192.168.131.1/24
        - fc00:Dead:Beef:a131::1/64
      vlan132:
        link: eth1
        id: 132
        addresses:
        - 192.168.132.1/24
        - fc00:Dead:Beef:a132::1/64

### /etc/frr/frr.conf

    interface vlan131
        ip router isis NET1
        ipv6 router isis NET1
    exit
    !
    interface vlan132
        ip router isis NET1
        ipv6 router isis NET1
    exit