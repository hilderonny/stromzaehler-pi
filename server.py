# Camera
import picamera2
import io
import time
import RPi.GPIO
import http.server
import os
import urllib.parse
import PIL
import numpy
import threading
import sqlite3

# Load single reference image and return it as 1 bit array
def load_reference_image(file_name):
    # Load image (here we are in the public folder))
    pil_image = PIL.Image.open("../images/" + file_name)
    # Convert it to 1 bit if not already
    if pil_image.mode != '1':
        pil_image = pil_image.convert('1')
    # Make zeros and ones from True and False and flatten it into one dimension
    numpy_array = numpy.array(pil_image).astype(numpy.uint8).flatten()
    return numpy_array

# Load all reference images from 0 to 9 and return them as indexed array
def load_reference_images():
    reference_images = [
        load_reference_image(f"{number}_bw.png") for number in range(10)
    ]
    return reference_images

# Compare digit with reference images and return detected value or "?"
def detect_digit_value(digit_array):
    # Count differences
    differences = [
        numpy.sum(digit_array != array) for array in reference_arrays
    ]
    # The index of the lowest difference is the detected value
    index = numpy.argmin(differences)
    # Analyze difference count to prevent misinterpretation
    value = differences[index]
    # Accept value only when the differences are below the threshold
    #print(index, value)
    detected_digit_value = str(index) if value < detection_threshold else "?"
    return detected_digit_value

# Extract a digit from the given image
def extract_digit_array(image_array, offset_x, offset_y):
    numpy_array = numpy.array(image_array)
    digit_array = numpy_array[offset_y:offset_y+84, offset_x:offset_x+46, 0]
    min_value = numpy.min(digit_array)
    max_value = numpy.max(digit_array)
    average_value = (float(min_value) + float(max_value)) / 2
    onebit_array = numpy.where(digit_array < average_value, 0, 1).flatten()
    return onebit_array

# Takes an image, detects a value and returns it as string, eventually
# containing "?"
def take_image_and_detect_value():
    # Switch light on
    RPi.GPIO.output(camera_led_port, True)
    time.sleep(.5)
    # Capture image
    image_array = camera.capture_array()
    detected_value = ""
    for digit_position in digit_positions:
        digit_array = extract_digit_array(
            image_array, digit_position[0], digit_position[1]
        )
        # Compare with reference images
        digit_value = detect_digit_value(digit_array)
        detected_value += digit_value
    # Switch light off
    time.sleep(.5)
    RPi.GPIO.output(camera_led_port, False)
    return detected_value

# Image capturing thread
def capture_forever():
    # Open database connection and prepare measurements table
    db_connection = sqlite3.connect("../database.db")
    db_connection.execute(
        "CREATE TABLE IF NOT EXISTS measurements(timestamp, value);"
    )
    while not shutdown_event.is_set():
        # Detect value
        detected_value = take_image_and_detect_value()
        # Store value in database if valid
        if "?" not in detected_value:
            db_connection.execute(
                "INSERT INTO measurements VALUES(datetime('now'),?);",
                (int(detected_value),),
            )
            db_connection.commit()
            print("Stored " + detected_value)
            # Sleep a minute before next turn
            time.sleep(59)
        else:
            print("Ignored " + detected_value)
            # Sleep only 15 seconds before next turn to get a valid image
            time.sleep(14)
    db_connection.close()

# Define GPIO port of the camera LED
camera_led_port = 32

# Initialize camera
camera = picamera2.Picamera2()
camera.start()

# Change to subdirectory "public" to serve static files
os.chdir('public')

# Define detection threshold for digits
detection_threshold = 1300

# Define digit positions
digit_positions = [
    [19, 166],
    [109, 166],
    [200, 168],
    [292, 169],
    [388, 169],
    [479, 170],
    [576, 171]
]

# Define cancel event for capturing thread
shutdown_event = threading.Event()

# Load reference images
reference_arrays = load_reference_images()

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

# Create and start capturing thread
capture_thread = threading.Thread(target=capture_forever, daemon=True)
capture_thread.start()

# Run Server until interrupt
try:
    server.serve_forever()
finally:
    # Clean up ressources
    camera.close()
    server.server_close()
    shutdown_event.set()
    capture_thread.join()
