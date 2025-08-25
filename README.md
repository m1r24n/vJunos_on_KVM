# how to install vJunos on KVM

## Introduction
This repository contains my notes and python scripts to deploy multiple vJunos VMs on KVM on linux platform.

Official information on vJunos can be found [here](https://www.juniper.net/us/en/dm/vjunos-labs.html)

Official documentations on how to install vJunos on KVM :
- [vJunosRouter](https://www.juniper.net/documentation/us/en/software/vjunos-router/vjunos-router-kvm/index.html)
- [vJunosSwitch](https://www.juniper.net/documentation/us/en/software/vjunos/vjunos-switch-kvm/index.html)
- [vJunosEvolved](https://www.juniper.net/documentation/us/en/software/vJunosEvolved/vjunos-evolved-kvm/index.html)

The official documentation provide information on how to deploy individual vJunos VM on KVM using xml configuration file for libvirt and setup the bridge connection between vJunos VM manually.

The python script that I created, will perform the following tasks:
1. automatic deployment of bridges for connection between vJunos VMs
2. automatic deployment of multiple vJunos VM (vJunosRouter, vJunosSwitch or vJunosEvolved (virtual PTX10001-36MR)) 
3. initial configuration for vJunos VM which can be deployed using ZTP into the vJunos VM.
4. configuration file for kea-dhcp4-server required for ZTP process for vJunos initialization.

the initial configuration for vJunos VM will consist the following: 
1. Basic configuration, such as username/password for accessing the vJunos VM, ip address of management interface, enbling SSH server.
2. advance configuration, such as ipv4/ipv6 address for vJunos VM interfaces, routing protocol (for now only IS-IS), MPLS configuration (LDP/RSVP). SR-MPLS configuration, and SRv6 configuration.

## notes
This script is tested on ubuntu 24.04 + KVM + libvirt + python3 on supermicro E200-8d with 128G RAM and Intel NUC i7/64G RAM

## Preparing the host
1. Install base operating system. In my lab, I am using Ubuntu Linux 24.04
2. Install the following application 
   - kvm 
   - kea-dhcp4-server
   - tftpd-hpa
   - openswitch

       sudo apt install qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils openvswitch-switch openvswitch-common kea-dhcp4-server tftpd-hpa

3. Create linux bridge to provide connection to the management interface of vJunos VM. for example the following netplan configuration file will create bridge **br0** with ip address **192.168.254.254/24**

       irzan@home2:/etc/netplan$ sudo cat /etc/netplan/02_net.yaml 
       network:
         bridges:
           br0:
             addresses: [ 192.168.254.254/24]
       irzan@home2:/etc/netplan$ sudo netplan apply
       irzan@home2:/etc/netplan$ ip addr show br0
       10: br0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc noqueue state DOWN group default qlen 1000
       link/ether 4e:11:43:4c:7a:16 brd ff:ff:ff:ff:ff:ff
       inet 192.168.254.254/24 brd 192.168.254.255 scope global br0
              valid_lft forever preferred_lft forever
       irzan@home2:/etc/netplan$ 

4. Verify that ipv4 and ipv6 forwarding are enabled. Edit file /etc/sysctl.conf to make ipv4 and ipv6 forwarding persistent between reboot

       sudo sysctl -a | grep net.ipv6.conf.all.forwarding
       sudo sysctl -a | grep net.ipv4.ip_forward

       irzan@home2:/etc/netplan$ cat /etc/sysctl.conf | grep forward
       # Uncomment the next line to enable packet forwarding for IPv4
       net.ipv4.ip_forward=1
       # Uncomment the next line to enable packet forwarding for IPv6
       net.ipv6.conf.all.forwarding=1
       irzan@home2:/etc/netplan$ sudo sysctl -f /etc/sysctl.conf 
       net.ipv4.ip_forward = 1
       net.ipv6.conf.all.forwarding = 1
       irzan@home2:/etc/netplan$ 

5. Enable ipv4 NAT on the default interface

       sudo iptables -t nat -A POSTROUTING -o eno2 -j MASQUERADE

6. To make ipv4 NAT persistent, enable the following startup services. This NAT is required to install application on the LXC container.

       cat << EOF | sudo tee /etc/systemd/system/rc-local.service 
       [Unit]
       Description=/etc/rc.local Compatibility
       ConditionPathExists=/etc/rc.local


       [Service]
       Type=forking
       ExecStart=/etc/rc.local start
       TimeoutSec=0
       StandardOutput=tty
       RemainAfterExit=yes
       SysVStartPriority=99


       [Install]
       WantedBy=multi-user.target
       EOF

       sudo chmod +x /etc/systemd/system/rc-local.service

       cat << EOF | sudo tee /etc/rc.local
       #!/bin/bash 
       iptables -t nat -A POSTROUTING -o eno2 -j MASQUERADE
       exit 0
       EOF

       sudo chmod +x /etc/rc.local

       sudo systemctl enable rc-local.service
       sudo systemctl start rc-local.service

       sudo iptables -t nat -L -v -n


3. Install LXD. LXD is an open source solution for managing virtual machines and system containers. It will be used to deploy linux container which will emulate clients to generate traffic in the lab.

       sudo snap install lxd

4. Initialize lxd. Since dhcp server (kea-dhcp4-server) has been installed, then disable dnsmasq on LXD (by disabling bridge managed by LXD and use the bridge that was created on the previous step.)

       sudo lxd init

   ![lxd_bridge.png](images/lxd_bridge.png)

## Prepare python3 environment to run the script

1. Install python pip and python virtual environment

       sudo apt install python3-pip python3-venv

2. Create python virtual environment

       cd ~/
       python3 -m venv vlab

3. activate virtual environment **vlab**

       source ~/vlan/bin/activate


4. Clone the this repository into the linux server where vjunos will run

       cd ~/git
       git clone https://github.com/m1r24n/vJunos_on_KVM.git

5. Install the python packages required by the script

       cd ~/git/vJunos_on_KVM/script
       pip3 install -r requirements

## Anatomi of the script

1. The python scripts used to deploy vJunos can be found under directory [./script](./script)

       cd ~/git/vJunos_on_KVM/script

2. Files inside the directory **vJunos_on_KVM/script** are the following 
    - vlab.py  --> this is the main script to be executed when creating the topology
    - lib1.py  --> this python file contains all the function required to deploy vJunos VM on the host
    - kea-dhcp4-server.j2  --> jinja2 template to generate configuration file for kea-dhcp4-server
    - junos.j2 --> jinja2 template to generate initial configuration for vJunos VM
    - vjunosswitch.j2  --> jinja2 template to create script which will be used to deploy vJunosSwitch VM on the host
    - vjunosrouter.j2  --> jinja2 template to create script which will be used to deploy vJunosRouter VM on the host
    - vjunosevolved.j2 --> jinja2 template to create script which will be used to deploy vJunosEvolved VM on the host

3. To deploy the vJunos, run script [vlab.py](script/vlab.py).
4. The script [vlab.py](script/vlab.py) requires input from file **lab.yaml**, which define the topology of the lab, such as number of vJunos VMs, connection between vJunosVM, and initial configuration of vJunos VM.
6. sample of file **lab.yaml**, can be found under directory [./lab](./lab). There are several **lab.yaml** files for different topology that can be build.
7. Examples for [lab.yaml](lab/lab1/lab.yaml) or [lab.yaml](lab/lab2/lab.yaml)

## format of script's configuration files, lab.yaml
### File lab.yaml has several parts, and here are the explanations


1. Section **disk** specify the disk image files for vJunos VM:
       
       disk: 
         vjunosrouter: /disk3/vjunos/vJunos-router-25.2R1.9.qcow2
         vjunosswitch: /disk3/vjunos/vJunos-switch-25.2R1.9.qcow2
         vjunosevolved: /disk3/vjunos/vJunosEvolved-25.2R1.8-EVO.qcow2
         vjunosevolved_config: /disk3/vjunos/vjunosevolved_config.img

2. Section **vm_dir** specify the directory where the disk images for each vJunos VM will be stored

       vm_dir: /disk3/vm/lab2

3. Section **mgmt** specify the bridge where management interface of vJunos is connected to. It can be linux bridge or openvswitch.

       mgmt:
         bridge: br0

4. Section **ovs** specify which bridge that will be created by the script will be an openvswitch bridge. if the bridge is not defined on this section, it will be created as linux bridge.

       ovs:
       - pe1_ge0
       - pe2_ge0
       - pe3_ge0
            
4. Section **junos_login** specify the credential which will be put into junos configuration

       junos_login:
         user: admin
         password: pass01
         ssh_key: /home/irzan/.ssh/id_rsa

5. Section **ip_pool** specify the configuration required for the dhcp server (kea-dhcp4-server). change the ip address accordingly.

       ip_pool:
         subnet: 192.168.110.0/24
         gateway: 192.168.110.254
         option-150: 192.168.110.254
         range: 
           min: 192.168.110.1
           max: 192.168.110.200

6. Section **fabric** specify the topology of the lab, in this case the connection between vJunosVM, for example which port of VM1 connected to which port of VM2

       fabric:
         ipv4_prefix: 10.1.100.0/24
         #ipv6_prefix: fc00:dead:beef:ffff:ffff::/80
         topology:
          - [pe1,ge-0/0/1,p1,ge-0/0/0,0x1cd]
          - [pe1,ge-0/0/2,p2,ge-0/0/0,0x1cd]
          - [pe2,ge-0/0/1,p1,ge-0/0/1,0x1cd]
          - [pe2,ge-0/0/2,p2,ge-0/0/1,0x1cd]
          - [pe3,ge-0/0/1,p1,ge-0/0/2,0x1cd]
          - [pe3,ge-0/0/2,p2,ge-0/0/2,0x1cd]
          - [p1,ge-0/0/3,p2,ge-0/0/3,0x1cd]

       ipv4_prefix specify ipv4 subnet which will be used by the script to generate ipv4 address for each interface of the vJunos VM (interface ge-0/0/x or et-0/0/x)

       ipv6_prefix specify ipv6 subnet which will be used by the script to generate ipv6 address for each interface of the vJunos VM (interface ge-0/0/x or et-0/0/x). If ipv6_prefix is not defined, the local ipv6 address will be used.

       topology specify the connection between vJunos VM. for example [pe1,ge-0/0/1,p1,ge-0/0/0,0x1cd], define that port ge-0/0/1 of VM pe1 is connected to port ge-0/0/0 of VM p1, and the last field, in this example 0x1cd (hexadecimal number), define what will be configured on the interface.

       the meaning of the last field are the following

       bit 0 : ipv4, 0b000000001, 0x1
       bit 1 : ipv6, 0b000000010, 0x2
       bit 2 : iso,  0b000000100, 0x4
       bit 3 : isis  0b000001000, 0x8
       bit 4 : ospf  0b000010000, 0x10
       bit 5 : ospf3 0b000100000, 0x20
       bit 6 : mpls, 0b001000000, 0x40
       bit 7 : ldp,  0b010000000, 0x80
       bit 8 : rsvp, 0b100000000, 0x100

       for example, if it is 0x0, it means nothing will be configured on the interface
       if it is 0x1cd, the binary equivalent is 0b111001101, which means ipv6 will not be configured, but other like ipv4, iso, isis, mpls, ldp, rsvp will be configured on the junos configuration created by the script.
       as for now, the script will only generate configuration for IS-IS as the routing protocol, others such as ospf/ospf3 are not supported yet.

7. Section **vm**, specify the vJunos VM which will be created by the script.

       vm:
         pe1:
           type: vjunosrouter  
           ip_address: 192.168.110.11
           lo0:
             family:
               inet: 10.1.255.1
               iso: 49.0001.0001.0001.00
             protocol:
               isis: yes
           port:
             ge-0/0/0: 
               bridge: pe1_ge0
         pe2:
           type: vjunosrouter  
           ip_address: 192.168.110.12
           lo0:
             family:
               inet: 10.1.255.2
               iso: 49.0001.0001.0002.00
             protocol:
               isis: yes
             port:
               ge-0/0/0: 
                 bridge: pe2_ge0
       
       


11. This part is to define username/password which will be created by the script if vJunos is going to be preconfigure using ZTP. If other ZTP server is used, such as Juniper Aptra ZTP server, then this part is not used

        junos_login:
          user: admin
          password: pass01

12. This part is to define the ip pool for DHCP server used for ZTP process. if other ZTP server is used, such as Juniper Apstra ZTP server, then this part is not used.

        ip_pool:
          subnet: 10.1.101.0/24
          gateway: 10.1.101.1
          option-150: 10.1.101.2
          range: 
            min: 10.1.101.11
            max: 10.1.101.99

13. This part is to define the VM which will be deployed on the lab. Each VM will  have the following paramater 
    - **type** (vjunos, vjunosevolved, alpine VM, or ubuntu VM)
    - **ip_address** (on for vjunos and vjunosevolved) which will be used by the script to generate initial configuration for ZTP, and 
    - **port**, which consist of port-id and which bridge this port is connected to. 
    
    The topology of the lab is defined by assigning bridges between VMs. The script will automatically create and generate bridge and deploy VMs on the hypervisor.

        vm:
          sw1:
            type: vjunosswitch
            ip_address: 10.1.101.101
            port:
              ge-0/0/0: link1
              ge-0/0/1: link2
              ge-0/0/2: link3
              ge-0/0/3: link4
          sw2:
            type: vjunosswitch
            ip_address: 10.1.101.102
            port:
              ge-0/0/0: link5
              ge-0/0/1: link6
              ge-0/0/2: link3
              ge-0/0/3: link4
          svr1a:
            type: ubuntu
            port:
              eth0: link1
              eth1: link2
          svr2a:
            type: ubuntu
            port:
              eth0: link5
              eth1: link6

## ZTP for vJunos
1. To run ZTP for vJunos, requires DHCP server and TFTP Server. These two application can be run on other machine or VM or it can also run on the hypervisor
2. Install DHCP server and TFTP server. In my testing, isc-dhcp-server and tftpd-hpa are used. The dhcpd.conf for the dhcp server created by the script is for isc-dhcp-server. 
3. If you are using other dhcp server, then you need to modify the script.

## How to run the script
1. verify that file lab.yaml is avaiable on the local directory

       cd /home/git/home/git/vJunos_on_KVM/lab/topo1
       ls -la lab.yaml

2. verify that the lab.yaml contain the correct information, such as disk image for vEX and ubuntu VM, ip pool for dhcp, and topology of the lab

       cat lab.yaml

3. Verify that linux bridge and VMs are not yet configured and deployed

       ip link list type bridge
       virsh list --all

3. Run the scripts, with argument **create** to deploy the topology. The script will configure linux bridge, copy the disk image, and deploy virtual machines from the topology.

       ../../script/vlab.py create

4. Verify that linux bridge for connectivity between VMs has been created

       ip link list type bridge

5. Verify that VMs has been deployed on the hypervisor

       virsh list --all 

6. use the script to create ZTP configuration (dhcpd.conf and initial configuration for vEX) 

       ../../script/vlab.py config
       cd results
       scp * <ztp_server>:~/
       ssh <ztp_server>
       sudo cp dhcpd.conf /etc/dhcp/dhcpd.conf
       sudo systemctl restart isc-dhcp-server
       sudo cp *.conf /srv/tftp

7. Start all the VMs (vJunos and linux VM). All the vJunos VMs will go through ZTP proccess. It may take up to 5 minutes for the process to finish.

       ../../script/vlab.py start
        
8. Set the linux bridge and virtual interface on the KVM host to allow LLDP, 802.1X and LACP between virtual machines

       ../../script/vlab.py setbr

8. Ping management ip address of the vJunos VM to verify that vJunos are up and running
9. Open SSH session into vJunos to verify that it boot properly
10. Now you can start configuring the lab.


Screenshot recording of the previous steps can be found bellows

- [Deploying vJunos Part 1](https://asciinema.org/a/dVdKmAEUZZK6EXi6vXnaRtamm)
- [Deploying vJunos Part 2](https://asciinema.org/a/ZTGC9LoiQ695h7uMGfKqCUAmD)



# create client
1. On the linux host, install lxd

       sudo snap install lxd
       sudo lxd init

3. Download lxc image, for example alpine
       lxc image copy images:alpine/edge local: --alias alpine
       lxc image copy ubuntu: local: --alias ubuntu

4. Create client container using alpine image

       lxc launch client

5. Access container client and add the necessary software, such as openssh server, iperf, etc

       lxc exec client sh
       apk update
       apk upgrade
       apk add openssh iperf
       rc-update add sshd
       cat << EOF | tee -a /etc/ssh/sshd_config
       PermitRootLogin yes
       EOF
       passwd root
       service sshd start
       exit
       lxc stop client
6. Create container router, and install frr software
       lxc copy client router
       lxc start router
       lxc exec router sh
       apk add frr
       rc-update add frr iptables dnsmasq radvd
       sed -i -e "s/bgpd=no/bgpd=yes/" /etc/frr/daemons
       exit
       lxc stop router

7. Verify that there are two lxc container, client and router

       lxc list




       
