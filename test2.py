import numpy as np
import pytesseract
from picamera2 import Picamera2
from PIL import Image  # Zum Speichern als JPG
import cv2  # OpenCV für Bildvorverarbeitung
import RPi.GPIO

# GPIO für LED-Steuerung einrichten
camera_led_port = 32
RPi.GPIO.setmode(RPi.GPIO.BCM)
RPi.GPIO.setup(camera_led_port, RPi.GPIO.OUT, initial=False)
RPi.GPIO.output(camera_led_port, True)  # LED einschalten

# Kamera initialisieren
camera = Picamera2()
camera.configure(camera.create_still_configuration())
camera.start()

# Bild aufnehmen
array = camera.capture_array()

# Zuschneiden auf den Bereich (x=245, y=649) bis (x=2375, y=1059)
x1, y1, x2, y2 = 245, 649, 2375, 1059
cropped_array = array[y1:y2, x1:x2]

# Schritt 1: In Graustufen konvertieren
gray = cv2.cvtColor(cropped_array, cv2.COLOR_BGR2GRAY)

# Schritt 2: Kontrast erhöhen (Histogramm-Ausgleich)
gray = cv2.equalizeHist(gray)

# Schritt 3: Schwellenwert setzen (Binärisierung)
_, binary = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)

# Optional: Das vorverarbeitete Bild speichern (Debugging)
cv2.imwrite("processed_image.jpg", binary)

# Schritt 4: In ein PIL-Bild konvertieren
processed_image = Image.fromarray(binary)

# Optional: Das zugeschnittene Original speichern
cropped_image = Image.fromarray(cropped_array)
cropped_image.save("cropped_image.jpg", "JPEG")

# Schritt 5: Text mit pytesseract aus dem vorverarbeiteten Bild extrahieren
text = pytesseract.image_to_string(processed_image, config="--psm 6")
print("Erkannter Text:", text)

# Kamera stoppen und LED ausschalten
camera.stop()
RPi.GPIO.output(camera_led_port, False)
