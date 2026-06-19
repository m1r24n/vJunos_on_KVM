#!/usr/bin/env python3
import requests, pprint
data1 = {'username':'admin','password':'pass01'}
response = requests.post('https://192.168.250.12/rest/v10.04/login',data=data1,verify=False)
# response = requests.post('https://192.168.250.12/rest/v10.04/login',auth=HTTPBasicAuth('admin', 'pass01',verify=False))
print(response)


# curl -H "accept: */*" -H "x-use-csrf-token: true" -d "" -i -k -X POST 'https://192.168.250.12/rest/latest/login?username=admin&password=pass01'

# curl -X POST "https://192.168.250.12/rest/latest/logout"

# curl -i -k -X GET "https://192.168.250.12/rest" -H  "accept: */*" -d ""
# curl -i -k -X POST "https://192.168.250.12/rest/v10.04/login?username=admin&password=admin" -H  "accept: */*" -d ""

# curl -k -X POST "https://192.168.250.12/rest/v10.18/login?username=admin&password=pass01" -H  "accept: */*" -H  "x-use-csrf-token: true" -d ""
