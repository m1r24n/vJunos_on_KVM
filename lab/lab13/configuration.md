# sw1
    set interfaces ge-0/0/0 vlan-tagging
    set interfaces ge-0/0/0 unit 111 vlan-id 111
    set interfaces ge-0/0/0 unit 111 family inet address 192.168.111.1/24
    set interfaces ge-0/0/0 unit 111 family iso
    set interfaces ge-0/0/0 unit 111 family inet6 address fc00:dead:beef:a111::1/64
    set interfaces ge-0/0/0 vlan-tagging
    set interfaces ge-0/0/0 unit 112 vlan-id 112
    set interfaces ge-0/0/0 unit 112 family inet address 192.168.112.1/24
    set interfaces ge-0/0/0 unit 112 family iso
    set interfaces ge-0/0/0 unit 112 family inet6 address fc00:dead:beef:a112::1/64
    set protocols isis interface ge-0/0/0.111
    set protocols isis interface ge-0/0/0.112
# sw2
    set interfaces ge-0/0/0 vlan-tagging
    set interfaces ge-0/0/0 unit 121 vlan-id 121
    set interfaces ge-0/0/0 unit 121 family inet address 192.168.121.1/24
    set interfaces ge-0/0/0 unit 121 family iso
    set interfaces ge-0/0/0 unit 121 family inet6 address fc00:dead:beef:a121::1/64
    set interfaces ge-0/0/0 vlan-tagging
    set interfaces ge-0/0/0 unit 122 vlan-id 122
    set interfaces ge-0/0/0 unit 122 family inet address 192.168.122.1/24
    set interfaces ge-0/0/0 unit 122 family iso
    set interfaces ge-0/0/0 unit 122 family inet6 address fc00:dead:beef:a122::1/64
    set protocols isis interface ge-0/0/0.121
    set protocols isis interface ge-0/0/0.122
