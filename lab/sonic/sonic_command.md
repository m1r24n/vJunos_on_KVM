# Learn how to use SONIC

## change password

    username/password: admin/YourPaSsWoRd
    sudo passwd admin

## Setting ip addresses on management Interface

    sudo config interface ip add eth0 192.168.201.11/24

## set hostname

    sudo config hostname r1

## remove interface
    Ethernet40 - Ethernet124

## setting ip address

### leaf1
sudo config interface ip Loopback0 10.1.255.11/32
sudo config interface ip Ethernet0 10.1.100.0/31
sudo config interface ip Ethernet4 10.1.100.2/31

### leaf2
sudo config interface ip Loopback0 10.1.255.12/32
sudo config interface ip Ethernet0 10.1.100.4/31
sudo config interface ip Ethernet4 10.1.100.6/31

### leaf3
sudo config interface ip Loopback0 10.1.255.13/32
sudo config interface ip Ethernet0 10.1.100.8/31
sudo config interface ip Ethernet4 10.1.100.10/31

### spine1
sudo config interface ip Loopback0 10.1.255.1/32
sudo config interface ip Ethernet0 10.1.100.0/31
sudo config interface ip Ethernet4 10.1.100.2/31

# add vlan
sudo config vlan add 10
sudo config vlan add 20
show vlan brief
sudo config vlan member add -u Ethernet8 

# configure vtep 
sudo config vxlan add vtep 10.1.255.11
sudo config vxlan add <vtep_name> <ip_Address_of_loopback>
sudo config vxlan evpn_nvo add nvo vtep
sudo config vxlan evpn_nvo add <nvo_name> <vtep_name>
sudo config vxlan  map add  vtep 11 62010
sudo config vxlan  map add  <vtep_name> <vlan_ID> <vni>

show vlxan tunnel
show vxlan interface

# Configure BGP
router bgp <as_number>
neighbour 10.1.100.1 remote-as <remote_as>
bgp router-id <loopback_ip>
bgp bestpath as-path multiple-relax

router bgp 65113
 bgp router-id 10.1.255.13
 no bgp ebgp-requires-policy
 bgp bestpath as-path multipath-relax
 neighbor 10.1.100.9 remote-as 65101
 neighbor 10.1.100.11 remote-as 65102
 !
 address-family ipv4 unicast
  network 10.1.255.13/32
 exit-address-family
exit
!

router bgp 65102
 bgp router-id 10.1.255.2
 no bgp ebgp-requires-policy
 bgp bestpath as-path multipath-relax
 neighbor 10.1.100.2 remote-as 65111
 neighbor 10.1.100.6 remote-as 65112
 neighbor 10.1.100.10 remote-as 65113
 !
 address-family ipv4 unicast
  network 10.1.255.2/32
 exit-address-family
exit



router bgp 65113
 bgp router-id 10.1.255.13
 no bgp ebgp-requires-policy
 bgp bestpath as-path multipath-relax

 neighbor 10.1.100.9 remote-as 65101
 neighbor 10.1.100.11 remote-as 65102
 neighbor 10.1.255.1 remote-as 65101
 neighbor 10.1.255.1 update-source 10.1.255.13
 neighbor 10.1.255.2 remote-as 65102
 neighbor 10.1.255.2 update-source 10.1.255.13
 !
 address-family ipv4 unicast
 network 10.1.255.13/32
  exit-address-family

 address-family l2vpn evpn
  neighbor 10.1.255.1 activate
  neighbor 10.1.255.2 activate
  advertise-all-vni
 exit-address-family
exit


router bgp 65102
 neighbor 10.1.255.11 remote-as 65111
 neighbor 10.1.255.11 ebgp-multihop 2
 neighbor 10.1.255.11 update-source 10.1.255.1
 neighbor 10.1.255.12 remote-as 65112
 neighbor 10.1.255.12 ebgp-multihop 2
 neighbor 10.1.255.12 update-source 10.1.255.1
 neighbor 10.1.255.13 remote-as 65113
 neighbor 10.1.255.13 ebgp-multihop 2
 neighbor 10.1.255.13 update-source 10.1.255.1
 !
 address-family l2vpn evpn
  neighbor 10.1.255.11 activate
  neighbor 10.1.255.12 activate
  neighbor 10.1.255.13 activate
  advertise-all-vni
 exit-address-family
exit


 neighbor 10.1.255.11 remote-as 65111
 neighbor 10.1.255.11 ebgp-multihop 2
 neighbor 10.1.255.11 update-source 10.1.255.2
 neighbor 10.1.255.12 remote-as 65112
 neighbor 10.1.255.12 ebgp-multihop 2
 neighbor 10.1.255.12 update-source 10.1.255.2
 neighbor 10.1.255.13 remote-as 65113
 neighbor 10.1.255.13 ebgp-multihop 2
 neighbor 10.1.255.13 update-source 10.1.255.2


