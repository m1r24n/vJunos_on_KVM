#!/usr/bin/env python3
import requests, pprint, urllib3
urllib3.disable_warnings()

def get_aoxcx_config(d1,i,config_dir):
    ip_address = d1['vm'][i]['ip_address']
    url1=f"https://{ip_address}/rest/v10.18/login"
    data1 = {'username':d1['junos_login']['user'],'password':d1['junos_login']['password']}
    session=requests.session()
    login=session.post(url1,data=data1,verify=False)
    print(f"status code : {login.status_code}")
    if login.status_code != 200:
        print(f"error accessing API of switch {i}")
    else:
        #url2="https://192.168.250.12/rest/v10.18/system/interfaces"
        url2=f"https://{ip_address}/rest/v10.18/configs/running-config"
        #url2="https://192.168.250.12/rest/v10.18/configs"
        #headers1 = {"Accept": "application/json"}
        headers1 = {"Accept": "text/plain"}
        result= session.get(url2,verify=False,headers=headers1)
        # pprint.pprint(result.text)
        with open(f"{config_dir}/{i}.conf","w") as f1:
            f1.write(result.text)
        # d1 = result.text.split("\n")
        # #d1 = json.dumps(result.text)
        # for i in d1:
        #     print(i)
        # logout
        url3=f"https://{ip_address}/rest/v10.18/logout"
        logout=session.post(url3,verify=False)
        #print(logout)

# main 
d1 = {
    'junos_login': {
        'user':'admin',
        'password':'pass01'
        },
    'vm':
        {

        'sw2':
            {
            'ip_address':'192.168.250.12'
            }
        }
}
get_aoxcx_config(d1,'sw2','config')