# r1 
    set interfaces ge-0/0/0 vlan-tagging
    set interfaces ge-0/0/0 unit 111 vlan-id 111
    set interfaces ge-0/0/0 unit 111 family inet address 192.168.111.1/24
    set interfaces ge-0/0/0 unit 111 family iso
    set interfaces ge-0/0/0 unit 111 family inet6 address fc00:dead:beef:a111::1/64
# r3

    set interfaces ge-0/0/0 vlan-tagging
    set interfaces ge-0/0/0 unit 113 vlan-id 113
    set interfaces ge-0/0/0 unit 113 family inet address 192.168.113.1/24
    set interfaces ge-0/0/0 unit 113 family iso
    set interfaces ge-0/0/0 unit 113 family inet6 address fc00:dead:beef:a113::1/64
