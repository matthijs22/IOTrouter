import importlib
import json
from http.server import BaseHTTPRequestHandler

from config import Config
from logHandler import LogHandler


class RequestHandler(BaseHTTPRequestHandler):
    _config = Config()
    _logHandler = LogHandler(_config.logfile)

    # Error handling class
    def handle_error(self, code, message):
        self.send_response(code)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(str.encode(message))
        self._logHandler.create_entry(message)

    # Return response from Device
    def handle_response(self, message):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(str.encode(message))

    # Validate API key
    def auth(self, apiKey):
        return True if apiKey == self._config.apiKey else False

    # Routes the request to the appropriate device class and returns its data
    def execute(self, path, params):
        try:
            _segments = path.split("/")[1:]
            query_type = _segments[0]
            device_name = _segments[1]
            function_name = _segments[2]
        except KeyError as e:
            self.handle_error(404, "Path cannot be routed")
            return

        # Primary route for device calls, will refactor if more types are implemented in the future
        if query_type == "device" and device_name != "" and function_name != "":
            try:
                device_type = self._config.devices[device_name]["type"]
                device_ip = self._config.devices[device_name]["ip"]
                _device_module = importlib.import_module("devices." + device_type)
                _device_class = getattr(_device_module, device_type)
                _device = _device_class(device_name, device_ip)  # dynamically instantiate the device class
                fn = getattr(_device, function_name)
                response = fn(params)
                self.handle_response(response)
            except AttributeError as e:  # device does not support requested function
                self.handle_error(404, "Path cannot be routed. Device does not support the requested function.")
        else:
            self.handle_error(404, "Path cannot be routed.")

    # Just reports server as running
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(str.encode("Server Running"))

    # Validates posted parameters and handles authentication
    def do_POST(self):
        # read response data
        try:
            _content_len = int(self.headers.get('Content-Length'))
            _post_body = self.rfile.read(_content_len)
            post_data = json.loads(_post_body)
        except ValueError as e:
            self.handle_error(400, "Invalid submission. Body is not JSON")
            return

        # authenticate user
        if not self.auth(post_data['apiKey']):
            self.handle_error(401, "Invalid API key")
            return

        self.execute(self.path, post_data['params'])
