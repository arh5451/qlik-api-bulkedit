import json
import ssl
import websocket

# Add this line at the top of your script or inside __init__
websocket.enableTrace(True)

class QlikEngineClient:
    def __init__(self, host, user_directory, user_id, proxy="hdr", verify_ssl=False):
        # Clean the host to ensure no protocol prefixes
        self.host = host.replace("http://", "").replace("https://", "").rstrip("/")
        self.user_directory = user_directory
        self.user_id = user_id
        self.proxy = proxy
        self.verify_ssl = verify_ssl

    def _build_ws_url(self, app_id=None):
        # Build path based on whether we are connecting to a specific app or the engine hub
        path = f"app/{app_id}" if app_id else "app/"
        prefix = f"{self.proxy}/" if self.proxy and self.proxy.lower() != "none" else ""
        
        full_url = f"wss://{self.host}/{prefix}{path}"
        print(f"\n[DEBUG] Target URL: {full_url}")
        return full_url

    def get_script(self, app_id):
        ws_url = self._build_ws_url(app_id)
        
        # Clean UserId (remove domain if it was passed as DOMAIN\USER)
        clean_user_id = self.user_id.split('\\')[-1]
        user_header_value = f"UserDirectory={self.user_directory};UserId={clean_user_id}"
        
        # Format headers as a dictionary (key matches QMC 'Header authentication header name')
        headers = {"X-Qlik-User": user_header_value}
        
        print(f"[DEBUG] Sending Headers: {headers}")
        print(f"[DEBUG] Origin: https://{self.host}")

        ssl_opts = {"cert_reqs": ssl.CERT_NONE} if not self.verify_ssl else {}

        # Create connection
        ws = websocket.create_connection(
            ws_url, 
            header=headers, 
            sslopt=ssl_opts,
            origin=f"https://{self.host}"
        )

        try:
            # Step 1: Open Document
            open_doc_req = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "OpenDoc",
                "handle": -1,
                "params": [app_id]
            }
            ws.send(json.dumps(open_doc_req))

            app_handle = None
            while True:
                response = json.loads(ws.recv())
                if response.get("id") == 1:
                    if "error" in response:
                        raise Exception(f"OpenDoc Error: {response['error']}")
                    app_handle = response['result']['qReturn']['qHandle']
                    break

            # Step 2: Get Script
            get_script_req = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "GetScript",
                "handle": app_handle,
                "params": []
            }
            ws.send(json.dumps(get_script_req))

            while True:
                response = json.loads(ws.recv())
                if response.get("id") == 2:
                    return response['result']['qScript']
        finally:
            ws.close()
            print("[DEBUG] WebSocket Connection Closed.")

    def save_script(self, app_id, path):
        script = self.get_script(app_id)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(script)
        return path