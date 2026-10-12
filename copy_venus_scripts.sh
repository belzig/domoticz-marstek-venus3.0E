#!/bin/bash

# Zielverzeichnis definieren (relativ zu diesem Skript)
TARGET_DIR="../../scripts"

# Sicherstellen, dass das Zielverzeichnis existiert
mkdir -p "$TARGET_DIR"

echo "Kopiere Marstek Venus Skripte nach $TARGET_DIR..."

# Dateien kopieren (-p sorgt dafür, dass die Rechte -rwxr-xr-x erhalten bleiben)
cp -p venus_get_status.py "$TARGET_DIR/"
cp -p venus_set_auto_operation.py "$TARGET_DIR/"
cp -p venus_set_manual_operation.py "$TARGET_DIR/"

# Zur Sicherheit die Rechte im Zielverzeichnis noch einmal explizit setzen
chmod 755 "$TARGET_DIR"/venus_get_status.py
chmod 755 "$TARGET_DIR"/venus_set_auto_operation.py
chmod 755 "$TARGET_DIR"/venus_set_manual_operation.py

echo "Fertig! Alle Skripte wurden erfolgreich kopiert und sind ausführbar."
