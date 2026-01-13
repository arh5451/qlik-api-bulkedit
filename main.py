import os
import urllib3
from qs_conn.qs_engine import QlikEngineClient
from config.config import load_config

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load Config
cfg = load_config()
qlik_cfg = cfg["qlik"]

# Initialize Client
client = QlikEngineClient(
    host=qlik_cfg["host"],
    user_directory=qlik_cfg["user_directory"],
    user_id=qlik_cfg["user_id"],
    proxy=qlik_cfg.get("proxy", "hdr"),
    verify_ssl=qlik_cfg.get("verify_ssl", False)
)

app_id = "ce0f6336-9ca0-462a-a0d2-e93ed31a5412"

try:
    print("--- Starting Qlik Script Export ---")
    
    # This will now trigger the [DEBUG] prints from the client
    script_text = client.get_script(app_id)
    
    # Save to file
    output_path = f"scripts/{app_id}.qvs"
    client.save_script(app_id, output_path)
    
    print(f"\n[SUCCESS] Script saved to {output_path}")

except Exception as e:
    print(f"\n[FATAL ERROR] {e}")