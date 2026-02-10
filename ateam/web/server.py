"""
Zero-dependency Web Server for A-Team Reflection.
Uses http.server to provide a live dashboard.
"""

import http.server
import socketserver
import json
import os
import urllib.parse
from pathlib import Path
from ateam.core import RoomManager, WorkspaceIndexer

# Resolve static directory relative to this file
STATIC_DIR = Path(__file__).parent

class ReflectionHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def do_GET(self):
        # API Routes
        if self.path.startswith('/api/'):
            self._handle_api()
        else:
            # Static File Serving
            super().do_GET()

    def _handle_api(self):
        parsed = urllib.parse.urlparse(self.path)
        route = parsed.path.replace('/api/', '')
        params = urllib.parse.parse_qs(parsed.query)
        
        manager = RoomManager()
        
        res_data = {}
        status = 200

        try:
            if route == 'rooms':
                rooms = manager.list_rooms()
                res_data = [r.model_dump() for r in rooms]
                
            elif route == 'history':
                room_name = params.get('room', [None])[0]
                if room_name:
                    history_mgr = manager.get_history(room_name)
                    # Get last 50 messages
                    msgs = history_mgr.get_history(limit=50)
                    res_data = []
                    for m in msgs:
                        res_data.append({
                            "role": m.role,
                            "content": m.content,
                            "agent_tag": m.agent_tag,
                            "timestamp": m.timestamp.isoformat()
                        })
                else:
                    res_data = {"error": "Room name required"}
                    status = 400

            elif route == 'summary':
                indexer = WorkspaceIndexer()
                indexer.refresh()
                res_data = indexer.get_summary()

            else:
                res_data = {"error": "Endpoint not found"}
                status = 404

        except Exception as e:
            res_data = {"error": str(e)}
            status = 500

        # Send JSON response
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(res_data).encode('utf-8'))

def start_server(port=8080):
    handler = ReflectionHandler
    # Allow port reuse to avoid 'Address already in use' errors
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"🚀 A-Team Reflection Live at: http://localhost:{port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            httpd.shutdown()

if __name__ == "__main__":
    start_server()
