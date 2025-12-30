import json
import websocket
import ssl
import os

class QlikEngineClient:
    def __init__(self, host, user_directory, user_id, verify_ssl=False):
        """
        host: Qlik Sense hostname (without protocol)
        user_directory: UserDirectory for header auth
        user_id: UserId for header auth
        verify_ssl: True/False for SSL verification
        """
        self.host = host.rstrip("/")
        self.user_directory = user_directory
        self.user_id = user_id
        self.verify_ssl = verify_ssl

    def _build_ws_url(self, app_id):
        """
        Build the WebSocket URL with header authentication
        """
        return (
            f"wss://{self.host}/app/{app_id}"
            f"?reloadUri="
            f"&X-Qlik-User=UserDirectory={self.user_directory};UserId={self.user_id}"
        )

    def _send_jsonrpc(self, ws, request):
        """
        Send a JSON-RPC request and return the parsed response
        """
        ws.send(json.dumps(request))
        resp = ws.recv()
        return json.loads(resp)

    def get_script(self, app_id):
        """
        Connect to Engine API and fetch the load script for a given app
        """
        ws_url = self._build_ws_url(app_id)
        ws = websocket.create_connection(ws_url,
                                         sslopt={"cert_reqs": ssl.CERT_NONE} if not self.verify_ssl else None)

        # Step 1: Open the document
        open_doc_req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "OpenDoc",
            "handle": -1,
            "params": [app_id]
        }
        open_doc_resp = self._send_jsonrpc(ws, open_doc_req)
        app_handle = open_doc_resp['result']['qReturn']['qHandle']

        # Step 2: Get the load script
        get_script_req = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "GetScript",
            "handle": app_handle,
            "params": []
        }
        get_script_resp = self._send_jsonrpc(ws, get_script_req)
        script = get_script_resp['result']['qScript']

        ws.close()
        return script

    def save_script(self, app_id, folder="scripts"):
        """
        Fetch the script and save it to a .qvs file
        """
        script = self.get_script(app_id)
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, f"{app_id}.qvs")
        with open(path, "w", encoding="utf-8") as f:
            f.write(script)
        print(f"Script saved to {path}")
        return path

class QlikQRSClient:
    def __init__(self, server, virtual_proxy, user, verify_ssl=False):
        self.server = server.rstrip("/")
        self.virtual_proxy = virtual_proxy.strip("/")
        self.user = user
        self.verify_ssl = verify_ssl

    def _generate_xrfkey(self):
        # Qlik requires exactly 16 characters
        return uuid.uuid4().hex[:16]

    def _headers(self, xrfkey):
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Qlik-Xrfkey": xrfkey,
            "hdr-user": self.user
        }

    def _build_url(self, endpoint, params):
        xrfkey = self._generate_xrfkey()

        params = params.copy() if params else {}
        params["xrfkey"] = xrfkey

        query_string = urlencode(params, doseq=True)

        url = (
            f"{self.server}/"
            f"{self.virtual_proxy}/qrs"
            f"{endpoint}"
            f"?{query_string}"
        )

        return url, xrfkey

    def get(self, endpoint, **params):
        url, xrfkey = self._build_url(endpoint, params)

        response = requests.get(
            url,
            headers=self._headers(xrfkey),
            verify=self.verify_ssl,
            allow_redirects=False
        )

        # response.raise_for_status()
        return response

    def post(self, endpoint, payload=None, **params):
        url, xrfkey = self._build_url(endpoint, params)

        response = requests.post(
            url,
            headers=self._headers(xrfkey),
            json=payload,
            verify=self.verify_ssl,
            allow_redirects=False
        )

        # response.raise_for_status()
        return response.json()