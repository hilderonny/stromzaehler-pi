# Camera
import picamera2
import io
import time
import threading
import RPi.GPIO

# Store latest image
latest_image = None
# Define GPIO port of the camera LED
camera_led_port = 32

# Initialize camera
camera = picamera2.Picamera2()
camera.start()
time.sleep(2)

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
import urllib.parse

# Change to subdirectory "public" to serve static files
os.chdir('public')

# Custom class for API handling
class ApiHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global latest_image
        parsed_path = urllib.parse.urlparse(self.path)
        # Handle API request for the image
        if parsed_path.path == '/api/image':
            if latest_image:
                self.send_response(200)
                self.send_header("Content-Type", "image/jpeg")
                self.send_header("Content-Length", str(len(latest_image)))
                self.end_headers()
                self.wfile.write(latest_image)
            else:
                self.send_response(503)
                self.end_headers()
        else:
            # Use the default functionality of SimpleHTTPRequestHandler for static files
            super().do_GET()
    # Prevent logging
    def log_message(self, format, *args):
        pass

# Set LED GPIO to output
RPi.GPIO.setmode(RPi.GPIO.BCM)
RPi.GPIO.setup(camera_led_port, RPi.GPIO.OUT, initial=False)
# Turn on LED, later this is done only when a picture is taken
RPi.GPIO.output(camera_led_port, True)

# Create Server on Port 80
server = http.server.HTTPServer(('', 80), ApiHTTPRequestHandler)

# Run Server until interrupt
try:
    server.serve_forever()
finally:
    # Clean up ressources
    camera.close()
    shutdown_event.set()
    capture_thread.join()
    server.server_close()