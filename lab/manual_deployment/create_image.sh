#!/bin/bash
lxc image copy images:alpine/edge local: --alias alpine
lxc launch alpine client
lxc exec client sh
apk add merge-usr
merge-usr
apk del merge-usr
apk add openssh
passwd root
cat << EOF | tee -a /etc/ssh/sshd_config
PermitRootLogin yes
EOF
rc-update add sshd
service sshd restart
exit
lxc stop client
