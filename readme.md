[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/james-sciortino/C9800-Set-Site-Tag)

# C9800-Set-Site-Tag.py

*This script is for the Cisco Catalyst 9800 Wireless Controller platform, and utilizes several Cisco-IOS-XE 17.3.1 YANG Models.*

---

# Purpose
The purpose of this script is to assist wireless administrators to programmatically automate the creation and assignment of unique site-tags for efficient AP management. 

This script was originally intended for administrators of fabric enabled Catalyst 9800 WLCs and APs managed by DNA Center. By default, for each fabric enabled AP, DNA Center will create and assign unique policy-tag specific to the fabric AP's floor assignment in the DNA site hierarchy. However, DNA Center will not create and assign a unique site-tag. Instead, it will assign the AP to the default site-tag named 'default-site-tag-fabric'.

This script will standardize all fabric enabled APs by assigning them to a working site-tag with the same name as its policy-tag. 

This code will empower wireless administrators to better leverage AP site-tags for user segmentation via ISE authorization policies. This will also maintain a 1:1 policy-tag to site-tag naming convention for proper organization and management of fabric enabled APs. 

This code can also be applied to traditional 'Over-The-Top' Cisco APs and Catalyst 9800 WLCs as well. When Cisco APs initially join the C9800 WLC, they are assigned to a default site-tag and policy-tag. Wireless administrators must first create a unique policy tag manually and assign each AP to it. This this code can be utilized to standardize all OTT APs with a site-tag to a working site-tag with the same name as its policy-tag.

# Site-Tag Summary
Site-tags on the Catalyst 9800 Wireless Controller platform replace AP groups found on Cisco Aironet WLCs, and serve the following purposes:
1. Define if an AP is configured for Local Mode or Flexconnect mode; contains the AP Join Profile and Flex Profile that is applied to the AP.
2. Include attributes that are specific to the physical site. For example, the list of primary APs for efficient upgrade is a part of a site-tag.
3. Sent as a AAA RADIUS attribute that can be used for Cisco ISE, particularly to differentiate authorization results for wireless clients associating to different APs.

# How This Code Works
This Python code will accomplish the following tasks:
- Step 1. Identify all policy-tags and site-tags that exist on the C9800 WLC.
- Step 2. Compare the policy-tag names and site-tag names.
- Step 3. For each difference, create a new site-tag with a name that matches the policy-tag.
- Step 4. Identify all Cisco AP's and their assigned site-tag.
- Step 5. For each Cisco AP that does not have a site-tag name that matches its policy-tag name, assign the AP to the appropriate site-tag. 

# Installation Steps
1. Clone the repository from a bash or PowerShell terminal
```console
clone https://github.com/james-sciortino/C9800-Set-Site-Tag.git
```
2. Navigate into the directory
```console
cd c9800-set-site-tag
```
3. Update [config.py](config.py) with your C9800's information, including hostname or management IP address, port, username & password. 
```console
nano config.py
```
4. Create the virtual environment in a sub dir in the same directory
```console
python3 -m venv venv
```
5. Start the virtual environment and install [requirements.txt](requirements.txt) from the <c9800-set-site-tag> folder.
```console
source venv/bin/activate
pip install -r requirements.txt 
```
6. Run the script from a bash or PowerShell terminal.
```console
python main.py
```

# FAQ 
1. What is the purpose of each file?
    - [util.py](util.py) - Contains all necessary Python functions
    - [config.py](config.py) - Contains Catalyst 9800 WLC config info and YANG data models for API calls
    - [main.py](main.py) - Primary script. This is the file you execute to run this code. 
2. Does this code use NETCONF, RESTCONF, or both?
    - This code leverages *RESTCONF* APIs and *YANG* data models only. *NETCONF* is not used.
3. How do I enable RESTCONF on my Catalyst 9800 WLC?
    - From a command prompt, type:
    ```console
    restconf
    ```
    - More information can be found [here](https://developer.cisco.com/docs/ios-xe/#!enabling-restconf-on-ios-xe/authentication)
4. How do I properly modify [config.py](config.py) with the appropriate information? 
    - Do not modify any of the YANG data models below "# WLC API Calls"   
    - The variable *WLC_TAG* can be used to exclude unused policy_tags in your discovery   
    - You can use the + operator to concatenate as many tags that you want to exclude

    - *WLC_FQDN* = *IP address* or *FQDN* of your Catalyst 9800 WLC's *management IP*
    - *WLC_PORT* = Port used for *RESTCONF* API calls on your WLC. Default is *443*
    - *WLC_USER* =  *Username* with *Privilege Level 15* on your Catalyst 9800 WLC
    - *WLC_PASS* = *Password* of your *Username* with *Privilege Level 15* on your Catalyst 9800 WLC
    - *WLC_TAG* = The *name* of any *policy-tag* you want to exclude during discovery.
        - You can use the + operator to concatenate as many tags that you want to exclude
        - For best results, leave this variable at its default value.

# Tutorial
*In this scenario, there are four fabric enabled APs were joined to a fabric-enabled C9800 WLC managed by DNA Center.*
    - Each AP is assigned to the 1st Floor Site of the building *SesameSt*.
    - Each AP is provisioned with its default policy-tag named "*PT_SesameSt_Floor1_bba53*"  
    - The policy-tag name provides specific context to AP's floor assignment; only AP's on this floor are assigned to this policy-tag.
    - Each AP is provisioned with its default site-tag named "*default-site-tag-fabric*"
    - The site-tag name is generic and applied to all Cisco APs on the WLC.
*The goal is assign a unique site-tag name for each AP that matches its unique policy-tag name.*
    - Each net-new site-tag will be cloned with the same profile assignments as the default site-tag.
    - Each AP will be assigned to a working site-tag named "*PT_SesameSt_Floor1_bba53*" and then will be *rebooted*.

```
$ python main.py 
+---------------------------------------------+
Scanning existing list of policy-tags...
+-------------------------------------------------------------------------+
|                           Existing Policy Tags                          |
+-------------------------------------------------------------------------+
| ['dna-generated-tag', 'homelab-policy-tag', 'PT_SesameSt_Floor1_bba53'] |
+-------------------------------------------------------------------------+
Comparing policy-tags and site-tags...
+---------------------------------------------+
The following site-tags need to be created...
+-------------------+
| Missing Site-Tags |
+-------------------+
|         []        |
+-------------------+
Do you want to create these site-tag(s)? (Y/N) N

james@James-PC MINGW64 ~/OneDrive/James/Python/Network-Automation/C9800/Site-Tag-Script (master)
$ python main.py 
+---------------------------------------------+
Scanning existing list of policy-tags...
+-------------------------------------------------------------------------+
|                           Existing Policy Tags                          |
+-------------------------------------------------------------------------+
| ['dna-generated-tag', 'homelab-policy-tag', 'PT_SesameSt_Floor1_bba53'] |
+-------------------------------------------------------------------------+
Comparing policy-tags and site-tags...
+---------------------------------------------+
The following site-tags need to be created...
+------------------------------+
|      Missing Site-Tags       |
+------------------------------+
| ['PT_SesameSt_Floor1_bba53'] |
+------------------------------+
Do you want to create these site-tag(s)? (Y/N) Y
+---------------------------------------------+
OK. Cloning existing site-tag 'default-site-tag-fabric' and creating new site-tag(s) as needed.
+---------------------------------------------+
Applying cloned site-tag(s) to C9800 Wireless LAN Controller...
+---------------------------------------------+
New site-tags created successfully.
+---------------------------------------------+
Do you want to assign the new site-tag(s) to the appropriate Cisco Access Points? (Y/N) Y
+---------------------------------------------+
Scanning Cisco Access Points..
+---------------------------------------------+
The following APs and site-tag assignments will be changed...
+-------------------+--------------------------+
|         AP        |         Site-Tag         |
+-------------------+--------------------------+
| 7c:ad:74:ff:6e:be | PT_SesameSt_Floor1_bba53 |
| a0:3d:6f:b7:44:60 | PT_SesameSt_Floor1_bba53 |
| a0:e0:af:3f:00:44 | PT_SesameSt_Floor1_bba53 |
| f4:db:e6:43:97:82 | PT_SesameSt_Floor1_bba53 |
+-------------------+--------------------------+
WARNING: Applying this change to the selected group of APs will cause them to reboot. Do you want to continue? (Y/N) Y
Applying payload to C9800-80 Wireless LAN Controller..
<Response [204]>
```

# Authors & Maintainers
Please contact me with questions or comments.
James Sciortino - james.sciortino@outlook.com

# License
This project is licensed under the terms of the MIT License.