"""
Cisco Catalyst 9800 - Clone Policy-Tags To Site-Tags, Then Assign APs. 
Author: James Sciortino <james.sciortino@outlook.com>

DNA-C9800-SiteTag.py
"""
from config import  WLC_FQDN, \
                    WLC_PORT, \
                    WLC_USER, \
                    WLC_PASS, \
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

today = date.today() # Set  data and time
todays_date = today.strftime("%m/%d/%y") # Set  data and time format 

headers = { #### Stage your headers for an API call
            'content-type': "application/yang-data+json",
            'accept': "application/yang-data+json"
        }

site_table = PrettyTable(['Existing AP Site-Tags']) # Setup the PrettyTable that will display the output of the WLC's exisiting AP site-tags
site_table.padding_width = 1

policy_table = PrettyTable(['Existing Policy Tags']) # Setup the PrettyTable that will display the output of the WLC's exisiting AP policy-tags
policy_table.padding_width = 1

tag_diff_table = PrettyTable(['Missing Site-Tags']) # Setup the PrettyTable that will display the AP policy-tag names we plan to clone as AP site-tags.
tag_diff_table.padding_width = 1

ap_mod_table = PrettyTable(['AP', 'Site-Tag']) # Setup the PrettyTable that will display the AP name and site-tags we plan to create. 
ap_mod_table.padding_width = 1

def wlan_cfg(): # Function that performs a GET API call to return JSON data of existing policy-tags on the WLC, excluding any default policy-tags. 
    url = "https://{}:{}{}".format(WLC_FQDN, WLC_PORT, YANG_WLAN_CFG) # Create a variable named 'url' which pulls data from our 'manager.py' file for appropriate string values.
    response = requests.request("GET", url, auth=HTTPBasicAuth(WLC_USER, WLC_PASS), # Create a variable named 'response' which will use the 'request' library to issue our 'GET' REST API call
                                headers=headers, verify=False)
    policy_lists = response.json()["Cisco-IOS-XE-wireless-wlan-cfg:wlan-cfg-data"]["policy-list-entries"]["policy-list-entry"] # Create a variable named 'policy_lists' which contains the returned JSON data from our most recent 'GET' REST API call.
    policy_list = [] # Create an empty Python list, where all our WLC policy-tag name values will be added. 
    for tag in policy_lists: # Initiate a Python 'for loop' that will iterate through our variable named 'policy_lists' which contains the returned JSON data of our policy-tag names.
        if tag['tag-name'] not in ['default-policy-tag']: # Python logic that excludes any policy tag named 'default-policy-tag'
                policy_list.append(tag['tag-name']) # Add the value of each tag-name to our Python list 'policy_list'. The JSON data is converted to a Python list here.
    return policy_list # Return the Python list of policy-tag names to the global Python script.

def site_cfg(): # Function that performs a GET API call to return JSON data of existing site-tags on the WLC
    url = "https://{}:{}{}".format(WLC_FQDN, WLC_PORT, YANG_SITE_CFG)# Create a variable named 'url' which pulls data from our 'manager.py' file for appropriate string values.
    response = requests.request("GET", url, auth=HTTPBasicAuth(WLC_USER, WLC_PASS), ##### Create a variable named 'response' which will use the 'request' library to issue our 'GET' REST API
                                headers=headers, verify=False)
    site_cfg = response.json()["Cisco-IOS-XE-wireless-site-cfg:site-cfg-data"]["site-tag-configs"]["site-tag-config"] # Create a variable named 'site_cfg' which contains the returned JSON data from our most recent 'GET' REST API call.
    site_list = [] # Create an empty Python list, where all  existing WLC site-tag name values will be added. 
    for tag in site_cfg: # Initiate a Python 'for loop' that will iterate through our variable named 'site_cfg' which contains the returned JSON data of site-tag names.
        site_list.append(tag['site-tag-name']) # Add the value of each site-tag  name to our Python list 'site_cfg'. The JSON data is converted to a Python list here.
    return site_list #  Return the Python list of site-tag names to the global Python script.

def ap_cfg(): # Function that performs a GET API call to return JSON data of existing APs + their tags assignments on the WLC.
    url = "https://{}:{}{}".format(WLC_FQDN, WLC_PORT, YANG_AP_CFG) # Create a variable named 'url' which pulls data from our 'manager.py' file for appropriate string values.
    response = requests.request("GET", url, auth=HTTPBasicAuth(WLC_USER, WLC_PASS), # Create a variable named 'response' which will use the 'request' library to issue our 'GET' REST API call
                                headers=headers, verify=False)
    ap_assignments = response.json()["Cisco-IOS-XE-wireless-ap-cfg:ap-cfg-data"]["ap-tags"]["ap-tag"] # Create a variable named 'ap_assignments' which contains the returned JSON data from our most recent 'GET' REST API call.
    ap_list = [] # Create an empty Python list, where all existing AP tag data will be added.
    for tag in ap_assignments: # Initiate a Python 'for loop' that will iterate through our variable named 'ap_assignments' which contains the returned JSON AP tag data.
        ap_list.append(tag) # Add the value of each AP's tag assignments to our Python list 'ap_list'. The JSON data is converted to a Python list here.
    # Just want the key values? You can use:
    # ap_list.append(tag['ap-mac'])
    # ap_list.append(tag['site-tag'])
    # ap_list.append(tag['policy-tag'])
    return ap_list #  Return the Python list of AP tag assignments to the global Python script.

def diff(site_tags, policy_tags): # Function that compares the list of existing site-tags and policy-tags, and returns the difference.
    list_diff = [i for i in policy_tags if i not in site_tags] # Typically this will display the name of each policy-tag name that must be cloned to a site-tag.
    return list_diff # Return the difference to the global Python script

def clone_site_tags(net_new): # Function that performs a GET API call to effectively clone the default DNA policy-tag.
    url = "https://{}:{}{}".format(WLC_FQDN, WLC_PORT, YANG_SITE_CFG) # Create a variable named 'url' which pulls data from our 'manager.py' file for appropriate string values.
    response = requests.request("GET", url, auth=HTTPBasicAuth(WLC_USER, WLC_PASS), # Create a variable named 'response' which will use the 'request' library to call our 'GET' REST API
                                headers=headers, verify=False)
    # Clone dictionary [1] into memory only.
    join_profile = response.json()["Cisco-IOS-XE-wireless-site-cfg:site-cfg-data"]["site-tag-configs"]["site-tag-config"][1]["ap-join-profile"] # Copy the default DNA 'ap-join-profile' into memory.
    flex_profile =  response.json()["Cisco-IOS-XE-wireless-site-cfg:site-cfg-data"]["site-tag-configs"]["site-tag-config"][1]["flex-profile"] # Copy the default DNA 'flex-profile' into memory.
    local_site =  response.json()["Cisco-IOS-XE-wireless-site-cfg:site-cfg-data"]["site-tag-configs"]["site-tag-config"][1]["is-local-site"] # Copy the default DNA 'is-local-site"' into memory.
    site_tag =  response.json()["Cisco-IOS-XE-wireless-site-cfg:site-cfg-data"]["site-tag-configs"]["site-tag-config"][1]["site-tag-name"] # Copy the default DNA 'site-tag-name"' into memory.
    generate_list = [] # Create an empty Python list, where all existing AP tag data will be added.
    for new_site in net_new: # Initiate a Python 'for loop' that will iterate through our variable named 'net_new' which contains the list of all AP policy tag names we plan to clone as a new site-tag.
        template =   { # Create the template for our JSON payload of our new AP site-tag. 
                    "site-tag-name": new_site, # Assign the new 'site-tag-name' equal to the existing name of the policy-tag we're iterating over. 
                    "description": ("Created via Python on " + todays_date), # Assign a brief description of our new site-tag with a string containing today's date.
                    "flex-profile": flex_profile, # Assign the new 'flex-profile' equal to the existing value of policy-tag we're iterating over. 
                    "ap-join-profile": join_profile, # Assign the new 'join_profile' equal to the existing value of policy-tag we're iterating over. 
                    "is-local-site": local_site # Assign the new 'local_site' equal to the existing value of policy-tag we're iterating over. 
                    }
        generate_list.append(template)  # Add the template value we just created to our Python list 'generate_list'.  The JSON data is converted to a Python list here.
    create_string = '{"Cisco-IOS-XE-wireless-site-cfg:site-tag-config":' + json.dumps(generate_list) + "}" # Convert our 'generate_list' Python variable to JSON data and add in the necessary YANG header. Assign it to a variable named 'create_string'
    return json.loads(create_string) #  Return the payload Python string to the global Python script.

def create_policy_tags(payload): # Function to POST the policy-tags to the WLC, effectively created them on the WLC
    url = "https://{}:{}{}".format(WLC_FQDN, WLC_PORT, YANG_SITE_TAG) # Create a variable named 'url' which pulls data from our 'manager.py' file for appropriate string values.
    response = requests.request("POST", url, auth=HTTPBasicAuth(WLC_USER, WLC_PASS), # Create a variable named 'response' which will use the 'request' library to call our 'POST' REST API
                                headers=headers, data=json.dumps(payload), verify=False) # Convert our payload Python string to JSON data
    print(payload) # Print the JSON data we're pushing to the 
    print(response) # Print the API response for validation. Expecting a 200 or 201 response. 

def duplicate_tags(get_ap_tags):  # Function to generate the list of AP's that we want to take action on.
    generate_list = []   # Create an empty Python list, where  AP tag data will be stored
    for key in get_ap_tags: # Initiate a Python 'for loop' that will iterate through the site-tag assignments for every single AP on the WLC
        if(key["policy-tag"] != key["site-tag"]): # Python logic that will filter out any AP that already has a site-tag name that matches its policy-tag.
            payload =   {  # Create the template for our JSON payload of identified AP's, including only their MAC address and site-tag.
            "ap-mac": key["ap-mac"],  # Maintaint the MAC address of the AP. No change here.
            "site-tag": key["policy-tag"] # Assign the site-tag name to the policy-tags name. 
            }
        generate_list.append(payload) # Add the payload to the list named 'generate_list'. Here the JSON data is converted to a Python list.
    create_string = '{"Cisco-IOS-XE-wireless-ap-cfg:ap-tag":' + json.dumps(generate_list) + "}" # Convert our 'generate_list' Python variable to JSON data and add in the necessary YANG header. Assign it to a variable named 'create_string'
    return json.loads(create_string) #  Return the payload Python string to the global Python script.

def assign_ap_tags(payload): # Function that performs a PATCH API call to assign each AP to the new site-tag with appropriate name. 
    # Note - This will cause the AP to reboot.  
    print("payload is")
    print(payload)
    url = "https://{}:{}{}".format(WLC_FQDN, WLC_PORT, YANG_AP_TAG) # Create a variable named 'url' which pulls data from our 'manager.py' file for appropriate string values.
    response = requests.request("PATCH", url, auth=HTTPBasicAuth(WLC_USER, WLC_PASS), # Create a variable named 'response' which will use the 'request' library to call our 'PATCH' REST API
                                headers=headers, data=json.dumps(payload), verify=False) # Convert our payload Python string to JSON data
    print(response)

def yes_no(answer): # Basic Python function to create a 'yes' or 'no' decision tree for user input.
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

# Step 1. Identify all policy-tags and site-tags, excluding any default policy-tags of your choosing.
get_policy_tags = wlan_cfg()
get_site_tags = site_cfg()
site_table.add_row([get_site_tags])
print(site_table)
policy_table.add_row([get_policy_tags])
print(policy_table)

# Step 2. Identify the difference of policy-tags and site-tags. 
print(" Here's the difference:")
tag_difference = diff(get_site_tags, get_policy_tags)
tag_diff_table.add_row([tag_difference])
print(tag_diff_table)

# Step 3. For each difference identified, create a new site-tag with a name that matches the policy-tag.
answer1 = input("Do you want to create the AP Site-Tag(s) with the same name? (Y/N) ")
yes_no(answer1)
print("OK. Cloning site-tag 'default-site-tag-fabric' and creating new site-tags as needed.")
net_new_tags = tag_difference
cloned_tags = clone_site_tags(net_new_tags)
print("Applying cloned site-tag(s) to C9800-80 Wireless LAN Controller..." )
create_tags = create_policy_tags(cloned_tags)
print("New site-tags created successfully." )

# Step 4. Identify all Cisco Access Points and their assigned site-tags.
answer2 = input("Do you want to assign the new site-tag(s) to the appropriate Cisco Access Points? (Y/N) ")
yes_no(answer2)
print("Scanning Cisco Access Points..")
get_ap_tags = ap_cfg()
print("Identifying Cisco Access Points out of compliance...")
duplicated_tags = duplicate_tags(get_ap_tags)
for ap in duplicated_tags["Cisco-IOS-XE-wireless-ap-cfg:ap-tag"]:
    ap_mod_table.add_row([ap["ap-mac"],ap["site-tag"]])
print(ap_mod_table)

# Step 5. For each Cisco Access Point that does not have a site-tag that matches its policy-tag, assign the respective site-tag.
answer3 = input("WARNING: Applying this change to the selected group of Cisco Access Points will cause them to reboot. /n Do you want to continue? (Y/N) ")
yes_no(answer3)
print("Applying payload to C9800-80 Wireless LAN Controller..")
reassign_ap_tags = assign_ap_tags(duplicated_tags)
