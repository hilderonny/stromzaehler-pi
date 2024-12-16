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
`latest_image` gespeichert.

## 5. Beleuchtung
## 6. OCR
## 7. Datenbank
## 8. Befestigung
## 9. Weboberfläche

https://chatgpt.com/c/675f31f5-894c-8005-ab33-c503bfbb53ac
