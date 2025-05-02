# node PE1

set services rpm rfc2544-benchmarking tests test-name test1 interface lo0.0
set services rpm rfc2544-benchmarking tests test-name test1 mode reflect
set services rpm rfc2544-benchmarking tests test-name test1 family inet
set services rpm rfc2544-benchmarking tests test-name test1 destination-udp-port 4001
set services rpm rfc2544-benchmarking tests test-name test1 test-interface lo0.0
set services rpm rfc2544-benchmarking tests test-name test1 destination-ipv4-address 10.1.255.1
set services rpm rfc2544-benchmarking tests test-name test1 source-ipv4-address 10.1.255.2
set interfaces ge-0/0/1 unit 0 family inet address 10.1.100.0/31
set interfaces ge-0/0/1 unit 0 family iso
set interfaces ge-0/0/2 unit 0 family inet address 10.1.100.2/31
set interfaces ge-0/0/2 unit 0 family iso
set interfaces lo0 unit 0 family inet address 10.1.255.1/32
set interfaces lo0 unit 0 family iso address 49.0001.0000.0000.0001.00
set protocols isis level 1 disable 
set protocols isis interface ge-0/0/1.0 point-to-point
set protocols isis interface ge-0/0/2.0 point-to-point
set protocols isis interface lo0.0 passive


## node P1

set interfaces ge-0/0/0 unit 0 family inet address 10.1.100.1/31
set interfaces ge-0/0/0 unit 0 family iso
set interfaces ge-0/0/1 unit 0 family inet address 10.1.100.6/31
set interfaces ge-0/0/1 unit 0 family iso
set interfaces ge-0/0/2 unit 0 family inet address 10.1.100.4/31
set interfaces ge-0/0/2 unit 0 family iso
set interfaces lo0 unit 0 family inet address 10.1.255.11/32
set interfaces lo0 unit 0 family iso address 49.0001.0000.0000.0011.00
set protocols isis interface ge-0/0/0.0 point-to-point
set protocols isis interface ge-0/0/1.0 point-to-point
set protocols isis interface ge-0/0/2.0 point-to-point
set protocols isis interface lo0.0 passive
set protocols isis level 1 disable

## node P2
set interfaces ge-0/0/0 unit 0 family inet address 10.1.100.3/31
set interfaces ge-0/0/0 unit 0 family iso
set interfaces ge-0/0/1 unit 0 family inet address 10.1.100.8/31
set interfaces ge-0/0/1 unit 0 family iso
set interfaces ge-0/0/2 unit 0 family inet address 10.1.100.5/31
set interfaces ge-0/0/2 unit 0 family iso4
set interfaces lo0 unit 0 family inet address 10.1.255.12/32
set interfaces lo0 unit 0 family iso address 49.0001.0000.0000.0012.00
set protocols isis interface ge-0/0/0.0 point-to-point
set protocols isis interface ge-0/0/1.0 point-to-point
set protocols isis interface ge-0/0/2.0 point-to-point
set protocols isis interface lo0.0 passive
set protocols isis level 1 disable


## node PE2
set interfaces ge-0/0/1 unit 0 family inet address 10.1.100.7/31
set interfaces ge-0/0/1 unit 0 family iso
set interfaces ge-0/0/2 unit 0 family inet address 10.1.100.9/31
set interfaces ge-0/0/2 unit 0 family iso
set interfaces ge-0/0/2 unit 0
set interfaces lo0 unit 0 family inet address 10.1.255.2/32
set interfaces lo0 unit 0 family iso address 49.0001.0000.0000.0002.00     
set protocols isis interface ge-0/0/1.0 point-to-point
set protocols isis interface ge-0/0/1.0
set protocols isis interface ge-0/0/2.0 point-to-point
set protocols isis interface ge-0/0/2.0
set protocols isis interface lo0.0 passive
set protocols isis interface lo0.0
set protocols isis level 1 disable


set services rpm rfc2544-benchmarking profiles test-profile throughput test-type throughput
set services rpm rfc2544-benchmarking profiles test-profile throughput packet-size 64
set services rpm rfc2544-benchmarking profiles test-profile throughput bandwidth-kbps 1000
set services rpm rfc2544-benchmarking tests test-name test1 test-profile throughput
set services rpm rfc2544-benchmarking tests test-name test1 mode initiate-and-terminate
set services rpm rfc2544-benchmarking tests test-name test1 family inet
set services rpm rfc2544-benchmarking tests test-name test1 destination-udp-port 4001
set services rpm rfc2544-benchmarking tests test-name test1 test-interface lo0.0
set services rpm rfc2544-benchmarking tests test-name test1 destination-ipv4-address 10.1.255.1
set services rpm rfc2544-benchmarking tests test-name test1 source-ipv4-address 10.1.255.2


