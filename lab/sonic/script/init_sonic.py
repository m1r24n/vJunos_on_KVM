#!/usr/bin/env python3
import paramiko
import re
server="192.168.171.14"
username="admin"
password="YourPaSsWoRd"
hostname = 'spine1'
ssh_key_file='/home/irzan/.ssh/id_rsa.pub'
with open(ssh_key_file,"r") as f:
    ssh_key = f.read().strip()
ssh=paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname=server,username=username,password=password)
cmd1 = "show ip interfaces"
stdin, stdout, stderr = ssh.exec_command(cmd1, get_pty=True)
intf={}
for line in iter(stdout.readline, ""):
    if "Ethernet" in line or "Loopback" in line:
        l1 = line.strip().split()
        intf[l1[0]]=l1[1]

cmd1 = 'vtysh -c "show bgp summary"'
bgp_n=[]
stdin, stdout, stderr = ssh.exec_command(cmd1, get_pty=True)
for line in iter(stdout.readline, ""):
    if "Active" in line:
        bgp_n.append(line.strip().split()[0])
filename = "init_sonic.sh"
f_src = f"/tmp/{filename}"
f_dst = f"~/{filename}"
#print(f"source {f_src}, destination {f_dst}")
with open(f_src,"w") as f:
    for i in intf.keys():
        cmd1 = f"sudo config interface ip remove {i} {intf[i]}"
        #print(cmd1)
        #stdin, stdout, stderr = ssh.exec_command(cmd1, get_pty=True)
        f.write(f"echo {cmd1} \n")
        f.write(f"{cmd1} \n")
    for i in bgp_n:
        cmd1 = f"sudo config bgp remove neighbor {i}"
        f.write(f"echo {cmd1} \n")
        f.write(f"{cmd1} \n")
    f.write(f"sudo config hostname {hostname}\n")
    f.write("sudo config save -y\n")
    f.write("mkdir ~/.ssh\n")
    wr1 = f"""
cat << EOF | tee ~/.ssh/authorized_keys
{ssh_key}
EOF
"""
    f.write(wr1)
    f.write("")
sftp=ssh.open_sftp()
sftp.put(f_src,filename)

print("Done")
# ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# ssh.connect(hostname=server,username=username,password=password)
# stdin, stdout, stderr = ssh.exec_command(cmd1, get_pty=True)
# for line in iter(stdout.readline,""):
#     print(line.strip())
