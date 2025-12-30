import requests
import os
import uuid
from urllib.parse import urlencode
import urllib3
# One-liner to suppress only the single InsecureRequestWarning from urllib3 needed.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from qs_conn.qs_engine import QlikEngineClient

# Setup the client


client = QlikQRSClient(
    server="https://sense.highcoordination.de",
    virtual_proxy="hdr",
    user_id=r"HICO-GROUP\ahs",
    verify_ssl=False
)

# Qlik Sense Applicaiton - API Test
app_id = "ce0f6336-9ca0-462a-a0d2-e93ed31a5412"

# Example 1: Just fetch the script as a string
script = client.get_script(app_id)
print(script)

# Example 2: Fetch and save the script to a file
path = client.save_script(app_id, folder="qlik_scripts")
print(f"Saved to: {path}")

# Test Request
# about = client.get("/about")
# print(about)

# Create Directory to save the script if it doesn't exist
folder = "qvs_scripts"
os.makedirs(folder, exist_ok=True)  # create folder if it doesn't exist
path = os.path.join(folder, f"test.qvs")

# Get Request - QVS Script of an App
app_id = "ce0f6336-9ca0-462a-a0d2-e93ed31a5412"

# Debugging output
url, xrfkey = client._build_url(f"/app/{app_id}/script", params={})

print("DEBUG URL:", url)
print("XRFKEY:", xrfkey)
print("HEADERS:", client._headers(xrfkey))

r = client.get(f"/app/{app_id}/script")
script = r.json()["script"]

print(f"Output is: {script}")
print(r.response).text 

# Save the script to a QVS file
with open(path, "w", encoding="utf-8") as f:
    f.write(script)

print(f"Script saved to {path}")
