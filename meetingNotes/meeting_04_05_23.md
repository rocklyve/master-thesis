## Meeting 05.04.2023

1. Zykluserkennung schwierig, da Antrag + allg. zeitlich + Geräte bauen + Studie x Auswertung

1.1. Am einen Ohr Temp messen, am anderen Ohr goldstandard. 1. Step allg. 2. step im alltag.
Hauptherausforderung ist: earpiece entwerfen mit Sensorik, zusammenarbeit mit HIWIS, EquadratC, 3,3V mit Ground + Clock, die den Takt vorgibt + Datenkanal zur datenübertragen...
dann software ergänzen zum auslesen, es gibt verschiedene Sensoren, tobi schickt mir die.

easyEDA auch anschauen

vllt Bewegung mitbetrachten, damit man diverse Schwankungen rauswerfen kann.

Wir machen Termin aus mit einem HiWi zum designen. Tobi gibt mir auch ncohmal n crashkurs.

ich soll jz mal einen Proposal abstract schreiben.

Motivation
Problem
Fragestellung
Geplantes Vorgehen (auch mit relevanten Metriken)
Ergebnisse

Schritt 1 ist vergleich verschiedener Messpositionen der optischen Sensoren

Schritt 2 ist die Anwendung, z.B zirkaliaren Rhytmuses

2. Kauseitenerkennung

3. Fitness + Activity wenn Tobi was hat

4. Trinken über Schluckereignis und nicht kauen vllt?


### After meeting links from Tobias

#### Sensoren:

* https://media.digikey.com/pdf/Data%20Sheets/Excelitas%20PDFs/TPiS_1S_1385.pdf
* https://www.mouser.de/datasheet/2/734/MLX90632_Datasheet_Melexis-1595868.pdf

2. anscheinend laut tobi besser (MLX Sensor).

#### PCB Design Tool (am besten mal tutorial dazu anschauen auf youtube):
https://easyeda.com/

#### hier noch eine sehr ausführliche erklärung zu i2c:
https://www.circuitbasics.com/basics-of-the-i2c-communication-protocol/

da die sensoren alle die gleiche addresse haben werden brauche wir da noch so address übersetzter, ich denke sopwas in die richung: https://www.analog.com/media/en/technical-documentation/data-sheets/4316fa.pdf