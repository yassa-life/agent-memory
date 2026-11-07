import http.server
import socketserver
import os
import sys
from pathlib import Path

# Ensure UTF-8 stdout on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

PORT = 28492
MEMORY_DIR = Path(__file__).parent.resolve()

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(MEMORY_DIR), **kwargs)

    def do_GET(self):
        if self.path in ['/', '/index.html']:
            self.path = '/visualizer.html'
        return super().do_GET()

    def log_message(self, format, *args):
        pass

def run_server(port=PORT):
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", port), CustomHandler) as httpd:
        print(f"Project Memory dashboard running at http://localhost:{port}")
        sys.stdout.flush()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Server stopped.")

if __name__ == '__main__':
    run_server()
