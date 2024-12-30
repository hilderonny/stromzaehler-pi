# stromzaehler-pi

Stromverbauchsauswertung mit Raspberry PI, PI-Kamera und altem Rotationsstromzähler.

Ich plane, eine Photovoltaikanlage anzuschaffen und möchte vorher zunächst mal 
einen Überblick bekommen, wie viel Strom ich wann verbrauche. Über das Jahr
verteilt möchte ich sehen, wieviel Strom pro Monat, Tag und Stunde verbraucht 
wird. Eventuell sogar minütlich.

Derzeit habe ich noch einen alten Stromzähler mit Rotationsscheibe. Ich baue 
dazu eine Kiste mit Raspberry PI, auf dem ein Webserver und eine Datenbank 
läuft. An diesen ist eine Kamera angeschlossen, die einmal pro Minute ein Foto 
vom Stromzähler macht, den Zählerstand erkennt und mit Zeitstempel in die 
Datenbank schreibt.

Der Webserver ist dazu da, dass ich über den PC die Daten abfragen kann.
Dazu wird der Raspberry PI per LAN oder WLAN in das lokale Netzwerk eingebunden 
und lauscht über eine simples HTTP auf Port 80.

Um zwischendurch einfach debuggen zu können, werden ich als erstes den Webserver
aufsetzen. Damit kann ich mir dann das Live-Kamerabild ansehen und prüfen, ob 
die Beleuchtung im Stromzählerkasten ausreicht. Auf dem Bild kann ich dann auch 
die erkannten Zahlen markieren.

Das Hübschmachen der Weboberfläche mache ich zum Schluss, wenn das Gerät verbaut
ist. Die Daten werden dann ja bereits aufgezeichnet, wodurch ich für die 
Darstellung mehr Zeit habe.

## 1. Hardware

Ich verwende einen Raspberry PI 2 Model B. Da das System keine hohe Performanz 
benötigt, reicht ein solcher Raspi vollkommen aus (denke ich). Außerdem braucht 
dieser nicht so viel Strom wie die neueren Generationen. Als Kamera benutze ich 
eine Standard Raspberry PI Kamera. Das Gehäuse werde ich selber drucken, nachdem
ich weiß, wo ich die einzelnen Teile im Zählerschrank anbringen will.

## 2. Grundinstallation

Zuerst bereite ich eine SD-Karte mit dem 
[Raspberry PI Imager](https://www.raspberrypi.com/software/) Programm vor.
Als Betriebssystem genügte `Raspberry PI OS Lite (32 Bit)`, da eine grafische
Oberfläche auf einem Server unnötig wäre.

Als Grundeinstellungen konfigurierte ich gleich WIFI und SSH, damit ich sofort
per SSH auf das Gerät komme.

Als WLAN-Adapter hatte ich einen USB-WLAN-Stick von Edimax verwendet. Allerdings
funktionierte dabei die Standardkonfiguration nicht, sodass sich dieser nicht
in das WLAN einbuchte. Vermutlich fehlten da noch Treiber. Daher verband ich den
Raspberry direkt per LAN über einen PowerLine-Adapter mit der Fritzbox.

Als nächstes klonte ich dieses Repository lokal nach
`home/pi/github/hilderonny/stromzaehler-pi`. Dabei nutzte ich das [GitHub
Command Line 
Interface](https://github.com/cli/cli/blob/trunk/docs/install_linux.md).

```sh
gh repo clone hilderonny/stromzaehler-pi /home/pi/github/hilderonny/stromzaehler-pi
```

Anschließend konnte ich mich mit Visual Studio Code per SSH auf den PI
verbinden und von dort aus weiter entwickeln und gleich mit der eingebauten
Kommandozeile testen.

## 3. Webserver

Bei der Frage, welche Programmiersprache ich verwenden sollte, entschied ich 
mich für Python. Hiermit kann man Webserver und Datenbanken betreiben und die
notwendigen OCR Funktionalitäten gibt es hier auch als Bibliotheken.

Die gesamte Funktionalität wird in einem Script `server.py` implementiert.
Zuerst soll der Server HTML Dateiuen aus einem Unterverzeichnis `public`
bereitstellen.

```py
import http
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
```

Um zu testen, ob das Ausliefern von HTML- und anderen Dateien auch aus
Unterverzeichnissen funktioniert, habe ich eine `index.html` und eine
`css/style.css` Datei erstellt.

**index.html**

```html
<!DOCTYPE html>
<html>
    <head>
        <link rel="stylesheet" href="css/style.css">
    </head>
    <body>
        Hallo Welt!
    </body>
</html>
```

**css/style.css**

```css
body { color: green; }
```

Da der Server auf Port 80 lauschen soll, muss das Skript mit root-Rechten
ausgeführt werden.

```sh
sudo python server.py
```

## 4. Live-Kamerabild

Als nächstes wird probiert, ob man das Kamerabild sieht. Dazu soll es zyklisch
aufgenommen und auf Abruf über die Weboberfläche angezeigt werden. Zuerst aber
der Teil, der das Bild zyklisch abruft. Dazu bietet sich die Kamera Bibliothek
vom Raspberry PI an. Ab Bookworm wird dazu `picamera2` verwendet, welches man
so hier installiert.

```sh
sudo apt install -y python3-picamera2 --no-install-recommends
```

Eine Anleitung für die Bibliothek findet man 
[hier](https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf).

**Kameraerweiterung**

```py
import picamera2
import io
import time
import threading

# Store latest image
latest_image = None

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

...

# Run Server until interrupt
try:
    server.serve_forever()
finally:
    # Clean up ressources
    camera.close()
    shutdown_event.set()
    capture_thread.join()
    server.server_close()
```

Nun wird zumindest jede Zehntelsekunde ein Bild gemacht und in der Variablen
`latest_image` gespeichert. Als nächste soll dieses Bild per HTTP-Aufruf
zurückgegeben werden. Dazu wird eine API unter der URL
`/api/image` definiert, was eine Anpassung des Webservers erfordert.

```py
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

# Create Server on Port 80
server = http.server.HTTPServer(('', 80), ApiHTTPRequestHandler)
```

Ruft man nun im Browser die URL `/api/image`auf, sollte das aktuelle Bild
angezeigt werden. Damit das Bild als nahezu Echtzeit-Video angezeigt wird,
wird die HTML-Seite angepasst.

```html
<!DOCTYPE html>
<html>
    <head>
        <link rel="stylesheet" href="css/style.css">
        <script type="module" src="scripts/main.js"></script>
    </head>
    <body>
        <img>
    </body>
</html>
```

Ein Javascript sorgt dafür, dass das Bild alle 100 Millisekunden neu geladen
wird.

```js
setInterval(() => {
    document.querySelector("img").setAttribute("src", "api/image?" + Date.now())
}, 100)
``` 

Das Bild flackert nun zwar ab und zu - wenn genau zu dem Zeitpunkt, 
zu dem das Bild abgefragt wird, dieses neu geschrieben - aber das soll hier
erst mal nicht stören, zumal später phnehin nur einmal pro Minute ein Bild
gemacht wird.

## 5. Beleuchtung

Zum Glück verwende ich einen Raspberry PI 2 Modell B+ und eine PiKamera V1.3.
Bei dieser Kombination ist auf der Kamera noch eine rote LED verbaut, die
sich per GPIO ansteuern lässt.

Das passiert in Python, indem der GPIO-Port 32 angeschaltet wird.

```py
import RPi.GPIO
# Define GPIO port of the camera LED
camera_led_port = 32
# Set LED GPIO to output
RPi.GPIO.setmode(RPi.GPIO.BCM)
RPi.GPIO.setup(camera_led_port, RPi.GPIO.OUT, initial=False)
# Turn on LED, later this is done only when a picture is taken
RPi.GPIO.output(camera_led_port, True)
```

## 6. Befestigung

In diesem Schritt will ich prüfen, wie der Raspberry und die Kamera vor dem
Stromzähler positioniert werden muss, ob die Beleuchtung ausreicht und ob der
Kamerafokus und der Öffnungswinkel ausreichen.

Dazu habe ich einen [Rahmen](3dmodels/rahmenentwurf.scad) entworfen, der den
größtmöglichen Abstand der Kamera ermöglicht, nicht viel Filament braucht und
an den Stromzähler geklemmt wird.

Das Ergebnis war ... miserabel. Die LED reicht zum einen von der Leuchtkraft
nicht aus, um genug Licht zu produzieren, und zum zum anderen blendet das
von der Glasscheibe am Stromzähler reflektierte Licht.

Das Bild selbst ist zwar unscharf, aber wenigstens ist der gesamte Zählerstand
auf dem Bild. Die Schärfe kann ich an der Kamera direkt anpassen, indem ich an
der Linsenverschraubung drehe, siehe dazu
https://projects.raspberrypi.org/de-DE/projects/infrared-bird-box/6

## 7. OCR

Referenzbildgröße: 46x84 Pixel
Offset je Ziffer:
1: 19, 166
2: 109, 166
3: 200, 168
4: 292, 169
5: 388, 169
6: 479, 170
7: 576, 171

```sh
sudo apt install tesseract-ocr
tesseract --psm 13 image.jpg stdout
sudo pip install pytesseract --break-system-packages
sudo pip3 install opencv-python-headless --break-system-packages
```

## 8. Datenbank
## 9. Weboberfläche
## 10. Hintergrunddienst

https://chatgpt.com/c/675f31f5-894c-8005-ab33-c503bfbb53ac
