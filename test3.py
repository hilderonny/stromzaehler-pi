# Camera
import picamera2
import time
import RPi.GPIO
import numpy
import PIL

# Define GPIO port of the camera LED
camera_led_port = 32

# Initialize camera
camera = picamera2.Picamera2()
camera.start()

# Set LED GPIO to output
RPi.GPIO.setmode(RPi.GPIO.BCM)
RPi.GPIO.setup(camera_led_port, RPi.GPIO.OUT, initial=False)

# Switch light on
RPi.GPIO.output(camera_led_port, True)
time.sleep(.5)


# Bild aufnehmen
array = camera.capture_array()
# print(len(array), array)

numpy_array = numpy.array(array)
# Ausschnitt: Zeilen 4-7 (Index 3:7), Spalten 3-5 (Index 2:5), und nur der erste Wert aus jedem Tupel
# ausschnitt_flattened = data[3:7, 2:5, 0].flatten()

# Referenzbildgröße = 46x84 Pixel
# PNG-Datei mit 1-Bit Farbtiefe einlesen
image_path = "dein_bild.png"
referenzbild = PIL.Image.open("images/0_bw.png")
# Sicherstellen, dass das Bild im Modus '1' (1-Bit-Farbtiefe) vorliegt
if referenzbild.mode != '1':
    referenzbild = referenzbild.convert('1')
referenz_numpy_array = numpy.array(referenzbild).astype(numpy.uint8).flatten()
print(referenzbild.size, len(referenz_numpy_array), referenz_numpy_array)

# Ziffer 0 bei 19,166
digit_0_array = numpy_array[19:65, 166:250, 0].flatten()
print(len(digit_0_array), digit_0_array)
kleinster_wert = numpy.min(digit_0_array)
groesster_wert = numpy.max(digit_0_array)
mittelwert = (float(kleinster_wert) + float(groesster_wert)) / 2
einbit_array = numpy.where(digit_0_array < mittelwert, 0, 1)
print(kleinster_wert, groesster_wert, mittelwert, len(einbit_array), einbit_array)

# Vergleich mit Referenzbild
# Unterschiede zählen
anzahl_unterschiede = numpy.sum(einbit_array != referenz_numpy_array)
print(anzahl_unterschiede)


# red_channel_array = [pixel[0] for row in array for pixel in row]
# red_channel_array = numpy_array[:, :, 0].flatten()
# print(len(red_channel_array), red_channel_array)

# Zuschneiden auf den Bereich (x=245, y=649) bis (x=2375, y=1059)
# x1, y1, x2, y2 = 245, 649, 2375, 1059
# cropped_array = array[y1:y2, x1:x2]

# Schritt 1: In Graustufen konvertieren
# gray = cv2.cvtColor(cropped_array, cv2.COLOR_BGR2GRAY)

# Schritt 2: Kontrast erhöhen (Histogramm-Ausgleich)
# gray = cv2.equalizeHist(gray)

# Schritt 3: Schwellenwert setzen (Binärisierung)
# _, binary = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)

# Optional: Das vorverarbeitete Bild speichern (Debugging)
# cv2.imwrite("processed_image.jpg", binary)

# Schritt 4: In ein PIL-Bild konvertieren
# processed_image = Image.fromarray(binary)

# Optional: Das zugeschnittene Original speichern
# cropped_image = Image.fromarray(cropped_array)
# cropped_image.save("cropped_image.jpg", "JPEG")




# Switch light off
time.sleep(.5)
RPi.GPIO.output(camera_led_port, False)

# Clean up ressources
camera.close()