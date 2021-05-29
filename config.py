# Use this file to configure your WLC via REST APIs
# Replace all values below with your production WLC

# WLC Parameters
WLC_FQDN = "192.168.20.33"
WLC_PORT = "443"
WLC_USER =  "dnoadmin"
WLC_PASS = "Cisco123"
WLC_TAG = ["default-policy-tag"]

# WLC API Calls
YANG_SITE_CFG = "/restconf/data/Cisco-IOS-XE-wireless-site-cfg:site-cfg-data"
YANG_WLAN_CFG = "/restconf/data/Cisco-IOS-XE-wireless-wlan-cfg:wlan-cfg-data"
YANG_AP_CFG = "/restconf/data/Cisco-IOS-XE-wireless-ap-cfg:ap-cfg-data"
YANG_SITE_TAG = "/restconf/data/Cisco-IOS-XE-wireless-site-cfg:site-cfg-data/site-tag-configs/"
YANG_AP_TAG = "/restconf/data/Cisco-IOS-XE-wireless-ap-cfg:ap-cfg-data/ap-tags/ap-tag/"

