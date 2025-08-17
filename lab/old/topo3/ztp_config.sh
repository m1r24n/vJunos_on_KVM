#!/bin/bash

cat << EOF  | sudo tee /etc/netplan/01-netcfg.yaml
network:
    version: 2
    # renderer: networkd
    ethernets:
        eth0:
            dhcp4: false
            addresses: [ 10.1.101.3/24]
            gateway4: 10.1.101.1
            nameservers:
                addresses: [ 192.168.10.1 ]
EOF

cat << EOF | sudo tee /containers_data/status/app/aos.conf
{
"ip": "10.1.101.2",
"user": "ztp",
"password": "J4k4rt4#01"
}
EOF

cat << EOF | sudo tee /containers_data/tftp/junos_custom1.sh
#!/bin/sh 
cli -c "configure; set system commit synchronize; set chassis evpn-vxlan-default-switch-support; commit and-quit"
EOF

sudo chmod +x /containers_data/tftp/junos_custom1.sh


grep -n "Step" < /containers_data/dhcp/dhcpd.conf
sed -i -e '8,29d' /containers_data/dhcp/dhcpd.conf
sed -i -e 's/dc1.yourdatacenter.com/vmmlab.juniper.net/' /containers_data/dhcp/dhcpd.conf
grep -n "name-server" < /containers_data/dhcp/dhcpd.conf
sed -i -e 's/10.1.2.13, 10.1.2.14/192.168.10.1/' /containers_data/dhcp/dhcpd.conf

cat ~/ztp_config.txt | sudo tee -a  /containers_data/dhcp/dhcpd.conf