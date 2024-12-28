import numpy as np
import pytesseract
from picamera2 import Picamera2  # Falls Du die picamera2-Bibliothek nutzt
from PIL import Image  # Zum Speichern als JPG

import RPi.GPIO
camera_led_port = 32
RPi.GPIO.setmode(RPi.GPIO.BCM)
RPi.GPIO.setup(camera_led_port, RPi.GPIO.OUT, initial=False)
# Turn on LED, later this is done only when a picture is taken
RPi.GPIO.output(camera_led_port, True)

# Kamera initialisieren
camera = Picamera2()
camera.configure(camera.create_still_configuration())
camera.start()

# Bild aufnehmen
array = camera.capture_array()

# Zuschneiden auf den Bereich (x=55, y=156) bis (x=597, y=267)
x1=245
y1=649
x2=2375
y2=1059
cropped_array = array[y1:y2, x1:x2]

# Das NumPy-Array in ein PIL-Image konvertieren
cropped_image = Image.fromarray(cropped_array)

# Bild als JPG speichern
cropped_image.save("cropped_image.jpg", "JPEG")

print("Das zugeschnittene Bild wurde gespeichert als 'cropped_image.jpg'.")

text = pytesseract.image_to_string(cropped_array)

print(text)

# Kamera stoppen
camera.stop()

RPi.GPIO.output(camera_led_port, False)
