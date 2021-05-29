from config import  WLC_FQDN, \
                    WLC_PORT, \
                    WLC_USER, \
                    WLC_PASS, \
                    WLC_TAG, \
                    YANG_SITE_CFG, \
                    YANG_WLAN_CFG, \
                    YANG_AP_CFG , \
                    YANG_SITE_TAG, \
                    YANG_AP_TAG    
import requests
import json
from requests.auth import HTTPBasicAuth
import urllib3
from datetime import date
from prettytable import PrettyTable

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # Silence the insecure warning due to SSL Certificate

today = date.today() 
todays_date = today.strftime("%m/%d/%y") 

headers = { 
            'content-type': "application/yang-data+json",
            'accept': "application/yang-data+json"
        }

site_table = PrettyTable(['Existing AP Site-Tags']) 
site_table.padding_width = 1

policy_table = PrettyTable(['Existing Policy Tags']) 
policy_table.padding_width = 1

tag_diff_table = PrettyTable(['Missing Site-Tags']) 
tag_diff_table.padding_width = 1

ap_mod_table = PrettyTable(['AP', 'Site-Tag'])
ap_mod_table.padding_width = 1

def spacer():
    print("+"+"-"*45+"+")

def wlan_cfg():
    url = "https://{}:{}{}".format(WLC_FQDN, WLC_PORT, YANG_WLAN_CFG) 
    response = requests.request("GET", url, auth=HTTPBasicAuth(WLC_USER, WLC_PASS),
                                headers=headers, verify=False)
    policy_lists = response.json()["Cisco-IOS-XE-wireless-wlan-cfg:wlan-cfg-data"]["policy-list-entries"]["policy-list-entry"] 
    policy_list = [] 
    for tag in policy_lists:
        if tag['tag-name'] not in WLC_TAG: 
                policy_list.append(tag['tag-name']) 
    policy_table.add_row([policy_list])
    print(policy_table)
    return policy_list 

def site_cfg(): 
    url = "https://{}:{}{}".format(WLC_FQDN, WLC_PORT, YANG_SITE_CFG)
    response = requests.request("GET", url, auth=HTTPBasicAuth(WLC_USER, WLC_PASS), 
                                headers=headers, verify=False)
    site_cfg = response.json()["Cisco-IOS-XE-wireless-site-cfg:site-cfg-data"]["site-tag-configs"]["site-tag-config"] 
    site_list = [] 
    for tag in site_cfg: 
        site_list.append(tag['site-tag-name']) 
    site_table.add_row([site_list])
    return site_list 

def ap_cfg(): 
    url = "https://{}:{}{}".format(WLC_FQDN, WLC_PORT, YANG_AP_CFG) 
    response = requests.request("GET", url, auth=HTTPBasicAuth(WLC_USER, WLC_PASS),
                                headers=headers, verify=False)
    ap_assignments = response.json()["Cisco-IOS-XE-wireless-ap-cfg:ap-cfg-data"]["ap-tags"]["ap-tag"] 
    ap_list = []
    for tag in ap_assignments: 
        ap_list.append(tag)
    # Just want the key values? You can use:
    # ap_list.append(tag['ap-mac'])
    # ap_list.append(tag['site-tag'])
    # ap_list.append(tag['policy-tag'])
    return ap_list 

def diff(site_tags, policy_tags): 
    list_diff = [i for i in policy_tags if i not in site_tags] 
    tag_diff_table.add_row([list_diff])
    print(tag_diff_table)
    return list_diff

def clone_site_tags(net_new): 
    url = "https://{}:{}{}".format(WLC_FQDN, WLC_PORT, YANG_SITE_CFG) 
    response = requests.request("GET", url, auth=HTTPBasicAuth(WLC_USER, WLC_PASS), 
                                headers=headers, verify=False)

    # Commented-out line-items are only for copying Flex profiles.
    join_profile = response.json()["Cisco-IOS-XE-wireless-site-cfg:site-cfg-data"]["site-tag-configs"]["site-tag-config"][1]["ap-join-profile"]
    #flex_profile =  response.json()["Cisco-IOS-XE-wireless-site-cfg:site-cfg-data"]["site-tag-configs"]["site-tag-config"][1]["flex-profile"]
    #local_site =  response.json()["Cisco-IOS-XE-wireless-site-cfg:site-cfg-data"]["site-tag-configs"]["site-tag-config"][1]["is-local-site"] 
    site_tag =  response.json()["Cisco-IOS-XE-wireless-site-cfg:site-cfg-data"]["site-tag-configs"]["site-tag-config"][1]["site-tag-name"]
    
    generate_list = [] 
    for new_site in net_new:
        # Commented-out line-items are only for copying Flex profiles.
        template =   { 
                    "site-tag-name": new_site, 
                    "description": ("Created via Python on " + todays_date), 
                    #"flex-profile": flex_profile, 
                    "ap-join-profile": join_profile, 
                    #"is-local-site": local_site 
                    }
        generate_list.append(template)  
    create_string = '{"Cisco-IOS-XE-wireless-site-cfg:site-tag-config":' + json.dumps(generate_list) + "}" 
    return json.loads(create_string) 

def create_policy_tags(payload): 
    url = "https://{}:{}{}".format(WLC_FQDN, WLC_PORT, YANG_SITE_TAG) 
    response = requests.request("POST", url, auth=HTTPBasicAuth(WLC_USER, WLC_PASS), 
                                headers=headers, data=json.dumps(payload), verify=False) 
    if response.status_code == 204:
        print(response)

def duplicate_tags(get_ap_tags):  
    generate_list = []  
    for key in get_ap_tags: 
        if(key["policy-tag"] != key["site-tag"]): 
            payload =   {  
            "ap-mac": key["ap-mac"],  
            "site-tag": key["policy-tag"] 
            }
            generate_list.append(payload)
    create_string = '{"Cisco-IOS-XE-wireless-ap-cfg:ap-tag":' + json.dumps(generate_list) + "}" 
    for ap in generate_list:
        ap_mod_table.add_row([ap["ap-mac"],ap["site-tag"]])
    print(ap_mod_table)
    return json.loads(create_string) 

def assign_ap_tags(payload): 
    # Note - This will cause the AP to reboot.  
    url = "https://{}:{}{}".format(WLC_FQDN, WLC_PORT, YANG_AP_TAG) 
    response = requests.request("PATCH", url, auth=HTTPBasicAuth(WLC_USER, WLC_PASS), 
                                headers=headers, data=json.dumps(payload), verify=False) 
    print(response)

def yes_no(answer): 
    yes = set(['yes','y', 'ye', ''])
    no = set(['no','n'])
    while True:
        choice = answer.lower()
        if choice in yes:
            return True
        elif choice in no:
            exit()
        else:
            print("Please respond with 'yes' or 'no'")                        
