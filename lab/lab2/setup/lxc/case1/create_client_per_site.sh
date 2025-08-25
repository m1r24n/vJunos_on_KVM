#!/bin/bash
for i in {1..3}
do
for j in {1..2}
do
BR=site${i}cs1
LXC=c${j}${BR}
echo "create client ${LXC} "
lxc copy client ${LXC}
echo "changing container ${LXC}"
lxc query --request PATCH /1.0/instances/${LXC} --data "{
  \"devices\": {
    \"eth0\" :{
       \"name\": \"eth0\",
       \"nictype\": \"bridged\",
       \"parent\": \"${BR}\",
       \"type\": \"nic\"
    }
  }
}"
lxc start ${LXC}
done
done