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

Das Ergebnis war brauchbar. Die eingebaute LED reicht von der Leuchtkraft
aus, um genug Licht zu produzieren. Die Scheibe reflektiert zwar, aber die
Kamera ist so angebracht, dass die LED-Reflektion über den Ziffern ist.

Das Bild selbst ist zwar unscharf, aber wenigstens ist der gesamte Zählerstand
auf dem Bild. Die Schärfe kann ich an der Kamera direkt anpassen, indem ich an
der Linsenverschraubung drehe, siehe dazu
https://projects.raspberrypi.org/de-DE/projects/infrared-bird-box/6

## 7. OCR

Ich wollte auf zusätzliche Bibliotheken wie OpenCV oder KI-Systeme wie Tesseract
verzichten und die Ziffernerkennung so einfach, wie möglich machen. Also
entschied ich mich für einfache Referenzvergleiche. Dazu Machte ich mit der
Kamera Bilder vom Stromzähler, sodass ich von jeder Ziffer mindestens ein Bild
bekam. Dann schnitt ich die Ziffern in gleich großen Abschnitten zu 46x84 Pixeln
aus und wandelte sie mit Paint.NET in ein 1-Bit-PNG-Bild um.

![0](images/0_bw.png) ![1](images/1_bw.png) ![2](images/2_bw.png)
![3](images/3_bw.png) ![4](images/4_bw.png) ![5](images/5_bw.png)
![6](images/6_bw.png) ![7](images/7_bw.png) ![8](images/8_bw.png)
![9](images/9_bw.png)

Anschließend maß ich den Offset jeder Ziffernstelle im Bild aus. Der Algorithmus
schneidet nun vom Bild ein Rechteck an der Offsetstelle der jeweiligen Ziffer
in der Größe der Referenzbilder (46x84 Pixel) aus und macht daraus ein
Schwarz-Weiß-Bild. Dazu verwendet der vom Bild nur den roten Kanal, da nur
dieser durch die rote LED ausreichend Daten enthält. Anschließend wird von der
Helligheit der kleinste und größte Wert ermittelt und der Mittelwert gebildet.
Mit diesem Mittelwert wird das Bild dann in 1 Bit - so wie die Referenzbilder -
umgewandelt. Der einfacheren Vergleichbarkeit halber wird das
zweidimensionale Bild-Array in ein eindimensionales Feld flachgeklopft.

```py
import numpy

# Flaches 1-Bit-Array für bestimmte Ziffer an Offset extrahieren
def extract_digit_array(image_array, offset_x, offset_y):
    # Numpy für effiziente Matritzen- und Vektorenrechnungen verwenden
    numpy_array = numpy.array(image_array)
    # Bildausschnitt für Ziffer ermitteln, nur ersten (roten) Kanal verwenden
    digit_array = numpy_array[offset_y:offset_y+84, offset_x:offset_x+46, 0]
    # Mindestwert und Maximalwert für Mittelwertbestimmung errechnen
    min_value = numpy.min(digit_array)
    max_value = numpy.max(digit_array)
    average_value = (float(min_value) + float(max_value)) / 2
    # 1-Bit-Feld durch einfachen Mittelwertvergleich erstellen
    onebit_array = numpy.where(digit_array < average_value, 0, 1).flatten()
    return onebit_array
```

Um die Referenzbilder vergleichbar zu haben, werden diese ebenfalls in ein
1-Bit-Feld eingelesen.

```py
import PIL

# Einzelnes Referenzbild laden und als 1-Bit-Feld zurückgeben
def load_reference_image(file_name):
    # Bild laden
    pil_image = PIL.Image.open("images/" + file_name)
    # Falls es nich schon ein 1-Bit-Bild ist, umwandeln
    if pil_image.mode != '1':
        pil_image = pil_image.convert('1')
    # In 0 und 1 umwandeln und aus 2 Dimensionen eine machen
    numpy_array = numpy.array(pil_image).astype(numpy.uint8).flatten()
    return numpy_array

# Alle Referenzbilder von 0 bis 9 laden und in einem sortierten Feld liefern
def load_reference_images():
    reference_images = [load_reference_image(f"{number}_bw.png") for number in range(10)]
    return reference_images
```

Für den eigentlichen Vergleich werden alle Stellen über deren Offset extrahiert
und mit allen Referenzbildern verglichen. Der Vergleich zählt dabei einfach die
unterschiedlichen Pixel zwischen Ziffernbild und Referenzbild. Das Referenzbild,
welches die wenigsten Abweichungen aufweist, stellt vermutlich die passende
Ziffer dar.

Da die Ziffern rotieren, kann es vorkommen, dass eine Ziffer mal nicht eindeutig
erkannt werden kann. Für so einen Fall wird ein Unterschiedsschwellwert von
1000 (aus dem Bauch heraus) festgelegt. Hat jedes Referenzbild mehr als 1000
Abweichungen, so gilt die Ziffer als "nicht zuverlässig erkannt" und wird mit
`?` markiert.

```py
# Ziffern-Feld mit Referenzbildern vergleichen und Wert ermitteln
def detect_digit_value(digit_array):
    # Unterschiede zählen
    differences = [numpy.sum(digit_array != reference_digit_array) for reference_digit_array in reference_arrays]
    # Der Index des geringsten Unterschiedes ist gleichzeitig die Ziffer
    index = numpy.argmin(differences)
    # Genaue Anuzahl Unterschiede ermitteln, um Fehlinterpretationen zu erkennen
    value = differences[index]
    # Nur wenn die Unterschiede unter 1000 liegen ist Ziffer zuverlässig 
    detected_value = str(index) if value < 1000 else "?"
    return detected_value

# Offsets der Ziffern festlegen
digit_positions = [
    [19, 166],
    [109, 166],
    [200, 168],
    [292, 169],
    [388, 169],
    [479, 170],
    [576, 171]
]

# Bild aufnehmen
image_array = camera.capture_array()

# Erkannten Wert deklarieren
value = ""

# Jede Ziffernposition betrachten
for digit_position in digit_positions:
    # 1-Bit-Feld für Ziffer extrahieren
    digit_array = extract_digit_array(image_array, digit_position[0], digit_position[1])
    # Ziffer oder "?" erkennen
    digit_value = detect_digit_value(digit_array)
    Ziffern zusammenfügen
    value += digit_value

# Erkannten Zählerstand ausgeben
print(value)
```

## 8. Datenbank

Als Datenbank verwende ich der Einfachheit halber SQLite. In einer Tabelle
`measurements` wird der Zeitstempel der Messung und der ausgelesene Wert
gespeichert. Beim Wert ignoriere ich das Komma, sodass aus `99423,6` ein
`994236` wird. Die Umrechnung mache ich an der Oberfläche. Beim Starten werden
die Datenbankdatei und die Tabelle angelegt, wenn sie nicht schon existieren.

```py
import sqlite3
db_connection = sqlite3.connect("database.db", autocommit=True)
db_connection.execute(
    "CREATE TABLE IF NOT EXISTS measurements(timestamp, value);"
)
```

Messwerte werden nur dann eingetragen, wenn sie korrekt gelesen wurden.

```py
if "?" not in value:
    db_connection.execute(
        "INSERT INTO measurements(timestamp, value) VALUES(datetime('now'),?);",
        (value,),
    )
```

Anschließend kann man die Werte mit Standard-SQL-Abfragen wieder auslesen, zum
Beispiel für einen bestimmten Monat.

```py
# Date functions: https://www.sqlite.org/lang_datefunc.html
for row in db_connection.execute("""
    SELECT timestamp, value 
    FROM measurements 
    WHERE strftime('%Y-%m', timestamp) = '2024-12';
"""):
    print(row)
```

## 9. Zyklische Wertermittlung

Der Server soll zyklisch einmal je Minute ein Bild aufnehmen, analysieren und
den Wert (sofern dieser korrekt erkannt wurde) in die Datenbank schreiben. Dazu
wird ein Thread erstellt, der neben dem HTTP Server parallel läuft.

```py
import time
import threading

# Abbruchbedingung für Thread festlegen
shutdown_event = threading.Event()

# Thread-Funktion
def thread_function():
    while not shutdown_event.is_set():
        # Mache irgendwas
        # ...
        # Eine Minute warten, bevor nächster Durchlauf kommt
        time.sleep(60)

# Thread erzeugen und starten
capture_thread = threading.Thread(target=thread_function, daemon=True)
capture_thread.start()

# Irgendwann aufräumen und Thread beenden
shutdown_event.set()
capture_thread.join()
```

## 10. API für Datenbankabfragen

Um die Datenbank abzufragen, sende ich mit JavaScript von der Website per POST
eine SQL-Abfrage und erhalte dafür eine JSON-Struktur.

```js
var response = await fetch("api/database", {
    body: "SELECT * FROM measurements;",
    method: "POST",
    header: {
        "Content-Type": "application/x-www-form-urlencoded"
    }
})
var json = await response.json(response)
console.log(json)
```

Auf Serverseite wird diese Abfrage im HTTP-Handler verarbeitet, welcher eine
separate Datenbankverbindung aufbaut. Das muss sein, weil unterschiedliche
Threads nicht dieselbe Verbindung benutzen können.

```py
import json

# Datenbank öffnen, Request abschicken und Ergebnis als JSON zurück geben
def request_database_for_json(request):
    db_connection = sqlite3.connect("../database.db")
    cursor = db_connection.execute(request)
    data = cursor.fetchall()
    db_connection.close()
    return json.dumps(data)

class ApiHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    # Abfrage muss per POST gesendet werden
    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == '/api/database':
            length = self.headers["Content-length"]
            length = int(length)
            request = self.rfile.read(length)
            json = request_database_for_json(request.decode('UTF-8'))
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(bytes(json, "utf-8"))        
```

## 11. Hintergrunddienst

Der Server soll gleich beim Systemstart anlaufen. Dazu habe ich unter
`/etc/systemd/system/stromzaehler.service` folgende Konfiguration erstellt.

```
[Unit]
Description=Stromzaehler

[Service]
ExecStart=/usr/bin/python /home/pi/github/hilderonny/stromzaehler-pi/server.py
Restart=always
User=root
WorkingDirectory=/home/pi/github/hilderonny/stromzaehler-pi/

[Install]
WantedBy=multi-user.target
```

Die Einrichtung des Dienstes geht dann so:

```sh
sudo systemctl daemon-reload
sudo systemctl enable stromzaehler.service
sudo systemctl start stromzaehler.service
```

## 12. Weboberfläche

TODO...

https://chatgpt.com/c/675f31f5-894c-8005-ab33-c503bfbb53ac
