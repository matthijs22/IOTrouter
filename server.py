import socketserver

from config import Config
from requestHandler import RequestHandler

config = Config()
with socketserver.TCPServer(("", config.port), RequestHandler) as httpd:
    print("Server running on port", config.port)
    httpd.serve_forever()
