import http.server
import os

# Change to subdirectory "public" to serve static files
os.chdir('public')

# Create Server on Port 80
server = http.server.HTTPServer(('', 80), http.server.SimpleHTTPRequestHandler)

# Run Server until interrupt
try:
    server.serve_forever()
except KeyboardInterrupt:
    server.server_close()