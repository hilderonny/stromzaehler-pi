# Camera
import picamera2
import io
import time
import RPi.GPIO
import http.server
import os
import urllib.parse

# Define GPIO port of the camera LED
camera_led_port = 32

# Initialize camera
camera = picamera2.Picamera2()
camera.start()

# Change to subdirectory "public" to serve static files
os.chdir('public')

# Custom class for API handling
class ApiHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        # Handle API request for the image
        if parsed_path.path == '/api/image':
            # Switch light on
            RPi.GPIO.output(camera_led_port, True)
            time.sleep(.5)
            # Take image
            stream = io.BytesIO()
            camera.capture_file(stream, format='jpeg')
            image = stream.getvalue()
            time.sleep(.5)
            # Switch light off
            RPi.GPIO.output(camera_led_port, False)
            # Respond with captured image
            self.send_response(200)
            self.send_header("Content-Type", "image/jpeg")
            self.send_header("Content-Length", str(len(image)))
            self.end_headers()
            self.wfile.write(image)
        else:
            # Use the default functionality of SimpleHTTPRequestHandler for static files
            super().do_GET()
    # Prevent logging
    # def log_message(self, format, *args):
    #     pass

# Set LED GPIO to output
RPi.GPIO.setmode(RPi.GPIO.BCM)
RPi.GPIO.setup(camera_led_port, RPi.GPIO.OUT, initial=False)

# Create Server on Port 80
server = http.server.HTTPServer(('', 80), ApiHTTPRequestHandler)

# Run Server until interrupt
try:
    server.serve_forever()
finally:
    # Clean up ressources
    camera.close()
    server.server_close()
