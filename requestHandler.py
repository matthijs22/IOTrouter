import importlib
import json
from http.server import BaseHTTPRequestHandler

from config import Config
from logHandler import LogHandler


class RequestHandler(BaseHTTPRequestHandler):
    _config = Config()
    _logHandler = LogHandler(_config.logfile)


    # Error handling class
    def handleError(self, code, message):
        self.send_response(code)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(str.encode(message))
        self._logHandler.createEntry(message)

    # Return response from Device
    def handleResponse(self, message):
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
            queryType = _segments[0]
            deviceName = _segments[1]
            functionName = _segments[2]
        except Exception as e:
            self.handleError(404, "Path cannot be routed")
            return

        # Primary route for device calls, will refactor if more types are implemented in the future
        if queryType == "device" and deviceName != "" and functionName != "":
            try:
                deviceType = self._config.devices[deviceName]["type"]
                deviceIp = self._config.devices[deviceName]["ip"]
                _device_module = importlib.import_module("devices." + deviceType)
                _device_class = getattr(_device_module, deviceType)
                _device = _device_class(deviceName, deviceIp)  # dynamically instantiate the device class
                fn = getattr(_device, functionName)
                response = fn(params)
                self.handleResponse(response)
            except AttributeError as e:  # device does not support requested function
                self.handleError(404, "Path cannot be routed. Device does not support the requested function.")
        else:
            self.handleError(404, "Path cannot be routed.")

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
            data = json.loads(_post_body)
        except Exception as e:
            self.handleError(400, "Invalid submission. Body is not JSON")
            return

        # authenticate user
        if not self.auth(data['apiKey']):
            self.handleError(401, "Invalid API key")
            return

        self.execute(self.path, data['params'])
