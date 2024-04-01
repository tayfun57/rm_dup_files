import os
import sys
import hashlib
import shutil
from datetime import datetime

# Überprüfe, ob ausreichend viele Argumente übergeben wurden
if len(sys.argv) < 4:
    print("Verwendung: python script.py quelle <Ordner1> <Ordner2> ... ziel <Zielordner>")
    sys.exit(1)

# Extrahiere die Ordnerliste und den Zielordner aus den Skriptargumenten
quellen_index = sys.argv.index('quelle') + 1
ziel_index = sys.argv.index('ziel') + 1
ordner_liste = sys.argv[quellen_index:ziel_index - 1]
neuer_ordner = sys.argv[ziel_index]

# Erstelle den neuen Ordner, wenn er noch nicht existiert
if not os.path.exists(neuer_ordner):
    os.makedirs(neuer_ordner)

# Funktion zum Berechnen des Blake2b-Hashes einer Datei
def hash_datei(dateipfad):
    blake2b = hashlib.blake2b()
    with open(dateipfad, 'rb') as f:
        while True:
            daten = f.read(65536)  # Lese 64KB gleichzeitig
            if not daten:
                break
            blake2b.update(daten)
    return blake2b.digest()

# Funktion zum Kopieren einer Datei in den neuen Ordner
def kopiere_datei(datei, zielordner):
    modifikationszeit = os.path.getmtime(datei)
    datum = datetime.utcfromtimestamp(modifikationszeit).strftime('%Y-%m-%d')
    _, dateiname = os.path.split(datei)
    neuer_dateiname = f"{datum}_{dateiname}"
    shutil.copy(datei, os.path.join(zielordner, neuer_dateiname))

# Set zum Speichern der bereits gefundenen Hashes
gefundene_hashes = set()

# Dictionary, um Duplikate zu speichern
duplikate = {}

# Durchlaufe alle angegebenen Ordner
for ordner in ordner_liste:
    for ordner_pfad, _, dateien in os.walk(ordner):
        for datei in dateien:
            dateipfad = os.path.join(ordner_pfad, datei)
            hashwert = hash_datei(dateipfad)
            # Überprüfe, ob der Hash bereits gefunden wurde
            if hashwert in gefundene_hashes:
                if hashwert in duplikate:
                    duplikate[hashwert].append(dateipfad)
                else:
                    duplikate[hashwert] = [dateipfad]
            else:
                kopiere_datei(dateipfad, neuer_ordner)
                gefundene_hashes.add(hashwert)

# Ausgabe der Duplikate in der Kommandozeile
if duplikate:
    print("Duplikate wurden gefunden:")
    for hashwert, dateiliste in duplikate.items():
        print(f"Hash: {hashwert}")
        for datei in dateiliste:
            print(f"- {datei}")
else:
    print("Keine Duplikate gefunden.")

print("Die Bilder wurden umbenannt und in den neuen Ordner verschoben.")
