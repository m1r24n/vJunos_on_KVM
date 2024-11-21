# how to install vJunos on KVM

## Introduction
This repository contains my notes and python scripts to deploy multiple vJunos VMs on KVM.

Official information on vJunos can be found [here](https://www.juniper.net/us/en/dm/vjunos-labs.html)

Official documentations on how to install vJunos on KVM can be found [here](https://www.juniper.net/documentation/us/en/software/vJunos/vjunos-switch-deployment-guide-for-kvm/index.html)


## notes
This script is tested on ubuntu 24.04 + KVM + libvirt + python3 on supermicro E200-8d with 128G RAM


## How to use the scripts
1. Clone the this repository into the linux server where vjunos will run

       cd /home/git
       git clone git@github.com:m1r24n/vJunos_on_KVM.git

2. The python scripts used to deploy vJunos can be found under directory [./script](./script)

       cd /home/git/home/git/vJunos_on_KVM/

3. To deploy the vJunos, run script [vlab.py](script/vlab.py).
4. There other files inside directory [./script](./script), which is required for script to run. those files are :
    - lib1.py
    - dhcpd.j2
    - vjunosswitch.j2
    - vjunosrouter.j2
    - vjunosevolved.j2
    - apstra_ztp.j2
    - alpine.j2
    - ubuntu.j2

5. The script [vlab.py](script/vlab.py) requires input from file **lab.yaml**, which depend on the topology of the lab that will be created. 
6. sample of file **lab.yaml**, can be found under directory [./lab](./lab). There are several **lab.yaml** files for different topology that can be build.
7. An example for [lab.yaml](lab/topo1/lab.yaml)
8. File lab.yaml has several parts, and here are the explanations
9. This part is to define the disk file used for vJunos, Ubuntu linux VM , and Alpine Linux VM. **vm_dir** is the directory where the disk images for the VMs will be stored

       disk: 
         vjunosswitch: /disk2/images/vjunos-switch-23.1R1.8.qcow2
         alpine: /disk2/images/alpine.img
         ubuntu: /disk2/images/ubuntu.img
       vm_dir: /disk2/vm/vex

10. This part is to define the bridge where interface fxp0 (management interface of vJunos is connected to). It can be linux bridge or openvswitch. 

       mgmt:
         bridge: br0
            

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
