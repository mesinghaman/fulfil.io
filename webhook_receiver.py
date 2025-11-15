#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import datetime

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        print(f"\n{'='*50}")
        print(f"Webhook received at {datetime.now()}")
        print(f"URL: {self.path}")
        print(f"Headers: {dict(self.headers)}")
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            print(f"Data: {json.dumps(data, indent=2)}")
        except:
            print(f"Raw data: {post_data.decode('utf-8')}")
        
        print(f"{'='*50}\n")
        
        # Send response
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"status": "received"}')
    
    def log_message(self, format, *args):
        pass  # Suppress default logging

if __name__ == '__main__':
    server = HTTPServer(('localhost', 8001), WebhookHandler)
    print("Webhook receiver running on http://localhost:8001")
    print("Use this URL in your webhook settings (with ngrok if needed)")
    server.serve_forever()
