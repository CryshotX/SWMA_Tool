# Star Wars Modding Automation Tool (SWMA)

Ein Python-Tool zur automatischen Modifikation von Star Wars Empire at War XML-Dateien.

## 📁 Projektstruktur

```
SWMA_Tool/
├── swma.py              # Hauptscript
├── shipchanges.yaml     # Konfigurationsdatei
├── requirements.txt     # Python-Abhängigkeiten
├── README_SWMA.md       # Diese Anleitung
└── backups/             # Automatisch erstellt (Backups)
```

## Features

- **Automatische Datei-Erkennung** für Skirmish und Campaign-Modi
- **Intelligente Squadron-Konfiguration** mit komplett überschreiben
- **Prozentuale Berechnungen** immer vom Originalwert aus
- **Automatische Backups** vor jeder Änderung
- **Hardpoint-Modifikationen** für Schadenserhöhungen
- **Template-Änderungen** für Schiffseigenschaften

## Installation

### Voraussetzungen

```bash
pip install pyyaml
```

### Schnellstart

```bash
# In den SWMA_Tool Ordner wechseln
cd SWMA_Tool

# Abhängigkeiten installieren
pip install -r requirements.txt
```

## Verwendung

### Grundlegende Nutzung

```bash
# Alle Änderungen anwenden (mit Backups)
python swma.py --config shipchanges.yaml

# Ohne Backups
python swma.py --config shipchanges.yaml --no-backup

# Nur Vorschau (keine Änderungen)
python swma.py --config shipchanges.yaml --preview
```

### Konfigurationsdatei (YAML)

```yaml
# Spielmodus: skirmish oder campaign
game_mode: skirmish

units:
  Einheitenname:
    template: Template_Name
    base_unit: Base_Unit_Name

    # Schiffseigenschaften ändern
    template_changes:
      shield_points: +30% # Prozentuale Erhöhung
      energy_refresh_rate: +100% # Prozentuale Erhöhung
      squadron_capacity: 40 # Absoluter Wert

    # Squadron-Konfiguration (komplett überschreiben)
    squadrons:
      delay_seconds: 2
      starting:
        tech_0:
          - type: ARC_130_Squadron
            count: 1
      reserve:
        tech_0:
          - type: ARC_130_Squadron
            count: 3

    # Hardpoint-Änderungen (Schaden)
    hardpoints:
      damage_increase: +40% # über Feuerrate-Reduktion
```

## Konfigurationsoptionen

### Template-Änderungen

Unterstützte Eigenschaften:

- `shield_points` - Schildstärke
- `shield_refresh_rate` - Schildregeneration
- `energy_refresh_rate` - Energieregeneration
- `squadron_capacity` - Jäger-Kapazität
- `tactical_health` - Schiffshülle
- `max_speed` - Geschwindigkeit

### Squadron-Konfiguration

- **Tech-Levels:** `tech_0`, `tech_1`, `tech_2`, `tech_3`, `tech_4`, `tech_5`
- **Typen:** `starting` (Start-Jäger), `reserve` (Reserve-Jäger)
- **Delay:** `delay_seconds` (Spawn-Verzögerung)

### Hardpoint-Änderungen

- **Schadenserhöhung:** Reduziert Feuerrate für DPS-Erhöhung
- **Prozentangaben:** Immer vom Originalwert aus berechnet

## Datei-Struktur

Das Tool erkennt automatisch die richtigen Dateien im übergeordneten XML-Verzeichnis:

### Skirmish-Modus

- **Templates:** `../Units/Templates_Frigates.xml`, `../Units/Templates_Capitals.xml`
- **Squadrons:** `../Units/Skirmish/SkirmishUnits_Republic.xml`
- **Hardpoints:** `../Hardpoints/HardPoints_Coresaga_Frigates.xml`, `../Hardpoints/HardPoints_Coresaga_Capitals.xml`

### Campaign-Modus

- **Squadrons:** `../Units/Republic_Space_Units.xml`

## Backup-System

- **Automatische Backups** vor jeder Änderung
- **Timestamp-basierte Namen** (z.B. `Templates_Frigates_20241201_143022.xml`)
- **Backup-Verzeichnis:** `backups/` (im SWMA_Tool Ordner)

## Beispiel-Konfiguration

Die `shipchanges.yaml` enthält bereits eine vollständige Konfiguration für alle Stammeinheiten:

- **Acclamator_I_Carrier** - Schilde +30%, Energie +100%, ARC-130/Nimbus/NTB-630
- **Venator** - Schilde +40%, Schaden +30%, 3 ARC-130 + 1 NTB-630
- **Victory_I** - Schilde +50%, Schaden +70%, 2 ARC-130
- **Imperial Star Destroyer** - Energie +100%, Schaden +40%
- **Tector** - Schilde +50%, Schaden +100%, ARC-130 + Nimbus
- **Secutor** - Schilde +100%, 3 ARC-130 + 3 Nimbus + 2 NTB-630

## Fehlerbehebung

### Häufige Probleme

1. **"Datei nicht gefunden"**

   - Prüfe, ob die XML-Dateien im übergeordneten Verzeichnis liegen
   - Prüfe die Dateinamen in der Konfiguration

2. **"Template nicht gefunden"**

   - Prüfe den Template-Namen in der Konfiguration
   - Prüfe, ob das Template in der XML-Datei existiert

3. **"Einheit nicht gefunden"**
   - Prüfe den `base_unit` Namen
   - Prüfe, ob die Einheit in der Squadron-Datei existiert

### Debug-Modus

```bash
# Vorschau der Konfiguration
python swma.py --config shipchanges.yaml --preview
```

## Sicherheitshinweise

- **Immer Backups erstellen** (Standard-Verhalten)
- **Teste Änderungen** in einer Kopie des Mods
- **Prüfe die Vorschau** vor der Anwendung
- **Sichere Original-Dateien** vor dem ersten Einsatz

## Erweiterte Funktionen

### Eigene Konfigurationen

Erstelle eigene YAML-Dateien für verschiedene Modifikationen:

```bash
python swma.py --config meine_aenderungen.yaml
```

### Batch-Verarbeitung

```bash
# Mehrere Konfigurationen nacheinander
for config in *.yaml; do
    python swma.py --config "$config"
done
```

## Support

Bei Problemen oder Fragen:

1. Prüfe die Fehlermeldungen
2. Verwende den `--preview` Modus
3. Prüfe die Backup-Dateien
4. Stelle sicher, dass alle XML-Dateien korrekt formatiert sind

## Ordnerstruktur

```
XML/                           # Hauptverzeichnis mit XML-Dateien
├── Units/
│   ├── Templates_Frigates.xml
│   ├── Templates_Capitals.xml
│   ├── Republic_Space_Units.xml
│   └── Skirmish/
│       └── SkirmishUnits_Republic.xml
├── Hardpoints/
│   ├── HardPoints_Coresaga_Frigates.xml
│   └── HardPoints_Coresaga_Capitals.xml
└── SWMA_Tool/                 # Tool-Ordner
    ├── swma.py
    ├── shipchanges.yaml
    ├── requirements.txt
    ├── README_SWMA.md
    └── backups/               # Automatisch erstellt
```
