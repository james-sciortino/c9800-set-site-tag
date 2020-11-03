# C9800-Set-Site-Tag
This script is for the Cisco Catalyst 9800 Wireless Controller platform, and utilizes several Cisco-IOS-XE 17.3.1 YANG Models.

Its purpose is to assist wireless administrators to programmatically automate the creation and assignment of unique site-tags for efficient AP management. 

# Summary
Site-tags on the C9800 Wireless Controller Platform serve the following purposes:
1. Define if an AP is configured for Local Mode or Flexconnect mode, and also contains the AP Join Profile and Flex Profile that is applied to the AP.
2. Include attributes that are specific to the physical site. For example, the list of primary APs for efficient upgrade is a part of a site-tag.
3. Used as a AAA RADIUS attribute in Cisco ISE, particularly to differentiate authorization results for wireless clients associating to different APs.

# How it works
This Python code intends to accomplish the following tasks:
- Step 1. Identify all policy-tags and site-tags that exist on the C9800 WLC.
- Step 2. Compare the policy-tag names and site-tag names.
- Step 3. For each difference, create a new site-tag with a name that matches the policy-tag.
- Step 4. Identify all Cisco AP's and their assigned site-tag.
- Step 5. For each Cisco AP that does not have a site-tag name that matches its policy-tag name, assign the AP to the appropriate site-tag. 

For Fabric Enabled APs and WLCs:
This code is particularly useful for fabric-enabled APs and WLCs managed by DNA Center. 
By default, without any Day-0 template, DNA-C will create a unique policy-tag specific to the fabric AP's floor assignment in the DNA site hierarchy. However, DNA-C will not create a unique site-tag, but instead
will assign the AP to the default site-tag, named 'default-site-tag-fabric'.

For 'Over-The-Top' APs and WLC's:
This code can be beneficial for traditional APs and WLCs.
When Cisco APs initially join the C9800 WLC, they are assigned to a default RF-tag, site-tag and policy-tag. 
Wireless administrators can create a unique policy tag manually and assign each AP to it, then use this code to create and assign each AP to a unique site-tag.

# How to use
1. Update "config.py" with your C9800's information, including hostname, port, username & password.
    - Do not modify any of the YANG data models below "# WLC API Calls"   
    - The variable WLC_TAG can be used to exclude unused or unassigned policy_tags      
    - You can use the + operator to exclude as many tags as you need.   
2. Make sure your folder has the following three files:
    - util.py - contains all necessary Python functions
    - config.py - contains WLC config info and YANG data models for API calls
    - main.py - primary script
3. From a bash or PowerShell terminal, run the following command:
    - python main.py

To verify all required packages are installed:
pip install -r requirements.txt

Example Use-Case:
1. The following 4 APs were joined to a fabric-enabled C9800 WLC managed by DNA Center.
2. Each AP is currently functional and assigned to a floor in the DNA Center site hierarchy. 
3. Each AP is provisioned with the default policy-tag and site-tag configured by DNA Center.
    - The policy-tag name provides specific context to AP's floor assignment; only AP's on this floor are assigned to this policy-tag.
    - The site-tag name is generic and applied to all Cisco APs on the WLC.
4. The goal is assign a unique site-tag name for each AP that matches its unique policy-tag name.
5. Each net-new site-tag will be cloned with the same profile assignments as the default site-tag.
6. In this scenario, each AP is assigned to the 1st Floor Site of site SesameSt: "PT_SesameSt_Floor1_bba53"

$ python main.py 

Scanning existing list of policy-tags...

Existing Policy Tags...

['PT_SesameSt_Floor1_bba53', 'default-policy-tag']

Comparing policy-tags and site-tags...

The following site-tags need to be created...

PT_SesameSt_Floor1_bba53

Do you want to create these site-tag(s)? (Y/N) Yes

OK. Cloning existing site-tag 'default-site-tag-fabric' and creating new site-tag(s) as needed.

Applying cloned site-tag(s) to C9800 Wireless LAN Controller...

New site-tags created successfully.

Do you want to assign the new site-tag(s) to the appropriate Cisco Access Points? (Y/N) Yes

Scanning Cisco Access Points..

The following APs and site-tag assignments will be changed...

AP: 

[7c:ad:74:ff:6e:be, PT_SesameSt_Floor1_bba53]

[a0:3d:6f:b7:44:60, PT_SesameSt_Floor1_bba53]

[a0:e0:af:3f:00:44, PT_SesameSt_Floor1_bba53]

[f4:db:e6:43:97:82, PT_SesameSt_Floor1_bba53]

WARNING: Applying this change to the selected group of APs will cause them to reboot. Do you want to continue? (Y/N) Yes

Applying payload to C9800-80 Wireless LAN Controller..

<Response [204]>

[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/james-sciortino/C9800-Set-Site-Tag)