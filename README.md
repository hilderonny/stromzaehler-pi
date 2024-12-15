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

## 3. Webserver

https://chatgpt.com/c/675f31f5-894c-8005-ab33-c503bfbb53ac

## 4. Live-Kamerabild
## 5. Beleuchtung
## 6. OCR
## 7. Datenbank
## 8. Befestigung
## 9. Weboberfläche
