# Camera
import picamera2
import io
import time
import threading

# Store latest image
latest_image = None

# Initialize camera
camera = picamera2.Picamera2()

# Clean shutdown of capture threads
shutdown_event = threading.Event()

# Function for continuous capturing
def capture_images():
    global latest_image
    stream = io.BytesIO()
    while not shutdown_event.is_set():
        stream.seek(0)
        camera.capture_file(stream, format='jpeg')
        latest_image = stream.getvalue()
        stream.seek(0)
        stream.truncate()
        time.sleep(0.1)  # Capture every 0.1 seconds

# Capture thread
capture_thread = threading.Thread(target=capture_images, daemon=True)
capture_thread.start()

# Webserver
import http.server
import os

# Change to subdirectory "public" to serve static files
os.chdir('public')

# Create Server on Port 80
server = http.server.HTTPServer(('', 80), http.server.SimpleHTTPRequestHandler)

# Run Server until interrupt
try:
    server.serve_forever()
finally:
    # Clean up ressources
    camera.close()
    shutdown_event.set()
    capture_thread.join()
    server.server_close()