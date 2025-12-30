import requests
import json

# -----------------------------------------
# CONFIGURATION
# -----------------------------------------
SERVER = "https://highcoordination.de"
APP_ID = "your-app-id-here"

HDR_USER = "domain\\your-username"  # must match Qlik virtual proxy config
XRFKEY = "abcdefghijklmnop"        # must be 16 chars

SEARCH_TEXT = "Old line of code"
REPLACE_TEXT = "New replacement line"

# -----------------------------------------
# COMMON HEADERS
# -----------------------------------------
headers = {
    "Content-Type": "application/json",
    "X-Qlik-Xrfkey": XRFKEY,
    "hdr-user": HDR_USER
}

# -----------------------------------------
# 1. GET CURRENT LOAD SCRIPT
# -----------------------------------------
url_get = f"{SERVER}/qrs/app/{APP_ID}/script?xrfkey={XRFKEY}"
resp = requests.get(url_get, headers=headers, verify=False)

if resp.status_code != 200:
    raise Exception(f"Failed to GET script: {resp.status_code} {resp.text}")

script = resp.json().get("script", "")
print("Current script loaded successfully.")

# # -----------------------------------------
# # 2. REPLACE TEXT
# # -----------------------------------------
# updated_script = script.replace(SEARCH_TEXT, REPLACE_TEXT)

# # -----------------------------------------
# # 3. SAVE UPDATED SCRIPT
# # -----------------------------------------
# url_put = f"{SERVER}/qrs/app/{APP_ID}/script?xrfkey={XRFKEY}"
# payload = { "script": updated_script }

# resp = requests.put(url_put, headers=headers, data=json.dumps(payload), verify=False)

# if resp.status_code != 200:
#     raise Exception(f"Failed to SAVE script: {resp.status_code} {resp.text}")

# print("Script updated successfully.")

# # -----------------------------------------
# # 4. RELOAD (OPTIONAL)
# # -----------------------------------------
# # Remove this section if you only want to save the script
# url_reload = f"{SERVER}/qrs/app/{APP_ID}/reload?xrfkey={XRFKEY}"
# resp = requests.post(url_reload, headers=headers, verify=False)

# if resp.status_code == 200:
#     print("Reload task started.")
# else:
#     print("Could not start reload:", resp.text)
