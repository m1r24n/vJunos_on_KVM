# config sw1
	set interfaces ge-0/0/0 unit 0 family ethernet-switching interface-mode trunk
	set interfaces ge-0/0/0 unit 0 family ethernet-switching vlan members vlan111
	set interfaces ge-0/0/0 unit 0 family ethernet-switching vlan members vlan112
	set interfaces irb unit 111 family inet address 192.168.111.1/24
	set interfaces irb unit 112 family inet address 192.168.112.1/24
	set protocols ospf area 0.0.0.0 interface irb.111
	set protocols ospf area 0.0.0.0 interface irb.112
	set vlans vlan111 vlan-id 111
	set vlans vlan111 l3-interface irb.111
	set vlans vlan112 vlan-id 112
	set vlans vlan112 l3-interface irb.112

# config fw1
	set chassis high-availability local-id 1
	set chassis high-availability local-id local-ip 10.1.255.11
	set chassis high-availability peer-id 2 peer-ip 10.1.255.12
	set chassis high-availability peer-id 2 interface lo0.0
	set chassis high-availability peer-id 2 liveness-detection minimum-interval 1000
	set chassis high-availability peer-id 2 liveness-detection multiplier 3
	set chassis high-availability services-redundancy-group 0 peer-id 2
	set security zones security-zone trust host-inbound-traffic system-services ping
	set security zones security-zone trust host-inbound-traffic system-services high-availability
	set security zones security-zone trust host-inbound-traffic system-services ssh
	set security zones security-zone trust host-inbound-traffic protocols ospf
	set security zones security-zone trust host-inbound-traffic protocols bfd
	set security zones security-zone trust interfaces ge-0/0/0.0
	set security zones security-zone trust interfaces ge-0/0/2.0
	set security zones security-zone trust interfaces lo0.0
	set security zones security-zone untrust host-inbound-traffic system-services ping
	set security zones security-zone untrust host-inbound-traffic protocols ospf
	set security zones security-zone untrust host-inbound-traffic protocols bfd
	set security zones security-zone untrust interfaces ge-0/0/1.0
	set system static-host-mapping fw2 inet 10.1.255.12
	
	set groups mnha-sync when peers fw1
	set groups mnha-sync when peers fw2
	set groups mnha-sync security policies from-zone trust to-zone trust policy default-permit match source-address any
	set groups mnha-sync security policies from-zone trust to-zone trust policy default-permit match destination-address any
	set groups mnha-sync security policies from-zone trust to-zone trust policy default-permit match application any
	set groups mnha-sync security policies from-zone trust to-zone trust policy default-permit then permit
	set groups mnha-sync security policies from-zone trust to-zone untrust policy default-permit match source-address any
	set groups mnha-sync security policies from-zone trust to-zone untrust policy default-permit match destination-address any
	set groups mnha-sync security policies from-zone trust to-zone untrust policy default-permit match application any
	set groups mnha-sync security policies from-zone trust to-zone untrust policy default-permit then permit
	set groups mnha-sync security policies from-zone untrust to-zone trust policy permit1 match source-address cl3sw2
	set groups mnha-sync security policies from-zone untrust to-zone trust policy permit1 match destination-address cl2sw1
	set groups mnha-sync security policies from-zone untrust to-zone trust policy permit1 match application junos-ping
	set groups mnha-sync security policies from-zone untrust to-zone trust policy permit1 match application junos-ssh
	set groups mnha-sync security policies from-zone untrust to-zone trust policy permit1 then permit
	set groups mnha-sync security policies from-zone untrust to-zone trust policy permit1 then log session-init
	set groups mnha-sync security policies from-zone untrust to-zone trust policy permit1 then count
	set groups mnha-sync security policies from-zone untrust to-zone trust policy default match source-address any
	set groups mnha-sync security policies from-zone untrust to-zone trust policy default match destination-address any
	set groups mnha-sync security policies from-zone untrust to-zone trust policy default match application any
	set groups mnha-sync security policies from-zone untrust to-zone trust policy default then reject
	set groups mnha-sync security policies from-zone untrust to-zone trust policy default then log session-init
	set groups mnha-sync security policies from-zone untrust to-zone trust policy default then count
	set groups mnha-sync security policies pre-id-default-policy then log session-close
	set groups mnha-sync security address-book global address cl3sw2 192.168.121.13/32
	set groups mnha-sync security address-book global address cl2sw1 192.168.112.11/32
	set apply-groups mnha-sync
	set system commit peers-synchronize
	set system commit peers fw2 user admin
	set system commit peers fw2 authentication "$9$OQCdBhreK87dsM8aZUDkq"
	deactivate security policies
	set security ssh-known-hosts fetch-from-server fw2


# config fw2

	set chassis high-availability local-id 2
	set chassis high-availability local-id local-ip 10.1.255.12
	set chassis high-availability peer-id 1 peer-ip 10.1.255.11
	set chassis high-availability peer-id 1 interface lo0.0
	set chassis high-availability peer-id 1 liveness-detection minimum-interval 1000
	set chassis high-availability peer-id 1 liveness-detection multiplier 3
	set chassis high-availability services-redundancy-group 0 peer-id 1
	set security zones security-zone trust host-inbound-traffic system-services ping
	set security zones security-zone trust host-inbound-traffic system-services high-availability
	set security zones security-zone trust host-inbound-traffic system-services ssh
	set security zones security-zone trust host-inbound-traffic protocols ospf
	set security zones security-zone trust host-inbound-traffic protocols bfd
	set security zones security-zone trust interfaces ge-0/0/0.0
	set security zones security-zone trust interfaces ge-0/0/2.0
	set security zones security-zone trust interfaces lo0.0
	set security zones security-zone untrust host-inbound-traffic system-services ping
	set security zones security-zone untrust host-inbound-traffic protocols ospf
	set security zones security-zone untrust host-inbound-traffic protocols bfd
	set security zones security-zone untrust interfaces ge-0/0/1.0
	set system static-host-mapping fw1 inet 10.1.255.11

	set groups mnha-sync when peers fw1
	set groups mnha-sync when peers fw2
	set apply-groups mnha-sync
	set system commit peers-synchronize
	set system commit peers fw1 user admin
	set system commit peers fw1 authentication "$9$OQCdBhreK87dsM8aZUDkq"
	deactivate security policies
	set security ssh-known-hosts fetch-from-server fw1

# config sw2 using aos-cx

	ssh server vrf mgmt
	vlan 1,121-122
	!
	interface 1/1/1
	    no shutdown
	    no routing
	    vlan trunk native 1
	    vlan trunk allowed 121-122
	!
	interface vlan 121
	    ip address 192.168.121.1/24
	    ip ospf 1 area 0.0.0.0
	!
	interface vlan 122
	    ip address 192.168.122.1/24
	    ip ospf 1 area 0.0.0.0

