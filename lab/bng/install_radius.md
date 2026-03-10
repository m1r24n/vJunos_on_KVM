# set ip adddress

cat << EOF | sudo tee /etc/netplan/01_net.yaml
network:
  version: 2
  ethernets:
    eth0:
        addresses: [ 192.168.251.100/24]
        routes:
        - to: 0.0.0.0/0
          via: 192.168.251.254
        nameservers:
          addresses: [ 192.168.1.1 ]
EOF
sudo netplan apply
sudo hostname radius
hostname | sudo tee /etc/hostname


# update system

sudo apt -y update && sudo apt -y upgrade


# install freeradius + postgres


sudo apt install freeradius postgresql freeradius-postgresql

# create admin user for postgres

sudo -s
su - postgres
createuser radius --no-superuser --no-createdb --no-createrole -P
createdb radius --owner=radius
exit


# load freeradius schema into postgres

sudo -s
cd /etc/freeradius/3.0/mods-config/sql/main/postgresql
psql -U radius -h localhost radius < schema.sql
psql -U radius -h localhost  radius < setup.sql
