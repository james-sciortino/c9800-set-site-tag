import requests
import json
from requests.auth import HTTPBasicAuth
import urllib3
from datetime import date
from prettytable import PrettyTable
import util 

# Step 1. Identify all policy-tags and site-tags, excluding any default policy-tags of your choosing.
util.spacer()
print("Scanning existing list of policy-tags...")
get_policy_tags = util.wlan_cfg()
get_site_tags = util.site_cfg()

# Step 2. Identify the difference of policy-tags and site-tags. 
print("Comparing policy-tags and site-tags...")
util.spacer()
print("The following site-tags need to be created...")
tag_difference = util.diff(get_site_tags, get_policy_tags)

# Step 3. For each difference identified, create a new site-tag with a name that matches the policy-tag.
answer1 = input("Do you want to create these site-tag(s)? (Y/N) ")
util.yes_no(answer1)
util.spacer()
print("OK. Cloning existing site-tag 'default-site-tag-fabric' and creating new site-tag(s) as needed.")
net_new_tags = tag_difference
cloned_tags = util.clone_site_tags(net_new_tags)
util.spacer()
print("Applying cloned site-tag(s) to C9800 Wireless LAN Controller..." )
util.spacer()
create_tags = util.create_policy_tags(cloned_tags)

print("New site-tags created successfully." )
util.spacer()

# Step 4. Identify all Cisco Access Points and their assigned site-tags.
answer2 = input("Do you want to assign the new site-tag(s) to the appropriate Cisco Access Points? (Y/N) ")
util.spacer()
util.yes_no(answer2)
print("Scanning Cisco Access Points..")
util.spacer()
get_ap_tags = util.ap_cfg()
print("The following APs and site-tag assignments will be changed...")
duplicated_tags = util.duplicate_tags(get_ap_tags)

# Step 5. For each Cisco Access Point that does not have a site-tag that matches its policy-tag, assign the respective site-tag.
answer3 = input("WARNING: Applying this change to the selected group of APs will cause them to reboot. Do you want to continue? (Y/N) ")
util.yes_no(answer3)
print("Applying payload to C9800-80 Wireless LAN Controller..")
reassign_ap_tags = util.assign_ap_tags(duplicated_tags)
