# KDY Markt-Erweiterung für SWMA Tool

## 🎯 Übersicht

Das SWMA Tool wurde um eine **KDY Markt-Funktionalität** erweitert, die es ermöglicht, die Wahrscheinlichkeiten und Verfügbarkeit von Schiffen im KDY Markt (Kuat Drive Yards) des Galactic Conquest zu konfigurieren.

## 🛒 Was ist der KDY Markt?

Der KDY Markt ist ein dynamisches System in Star Wars Empire at War, das in jedem galaktischen Zyklus neue Schiffe anbietet. Jedes Schiff hat:

- **Chance-Wert** (0-100): Wahrscheinlichkeit, dass das Schiff pro Zyklus erscheint
- **Lock-Status**: Ob das Schiff verfügbar ist oder nicht
- **Anforderungen**: Technologie- oder Ereignis-basierte Voraussetzungen
- **Dynamische Anpassungen**: Werte ändern sich basierend auf Spielereignissen

## ⚙️ Konfiguration

### Grundstruktur

```yaml
kdy_market:
  enabled: true # Aktiviert/deaktiviert KDY Markt-Verarbeitung

  ships:
    # Schiff-Konfigurationen hier...

  events:
    # Event-Konfigurationen hier...
```

### Schiff-Konfiguration

Jedes Schiff kann mit folgenden Parametern konfiguriert werden:

```yaml
ships:
  PROCURATOR_BATTLECRUISER:
    chance: 40 # Wahrscheinlichkeit (0-100)
    locked: false # Verfügbar/gesperrt
    readable_name: "Procurator Battlecruiser" # Anzeigename
    requirement_text: "" # Anforderungstext
    order: 1 # Sortierreihenfolge
```

### Event-Konfiguration

Events können die Markt-Dynamik beeinflussen:

```yaml
events:
  VENATOR_RESEARCH:
    adjustments:
      PROCURATOR_BATTLECRUISER: -20 # Reduziert Chance um 20%
    unlocks:
      MAELSTROM_BATTLECRUISER: true # Macht verfügbar
```

## 🚀 Verwendung

### Einfache Wahrscheinlichkeitsanpassung

```yaml
kdy_market:
  ships:
    PROCURATOR_BATTLECRUISER:
      chance: 60 # Erhöht von 40 auf 60

    PRAETOR_I_BATTLECRUISER:
      chance: 5 # Reduziert von 20 auf 5
```

### Schiffe entsperren/sperren

```yaml
kdy_market:
  ships:
    ACCLAMATOR_DESTROYER:
      locked: false # Macht verfügbar (ohne Era-Anforderung)
      chance: 15

    MAELSTROM_BATTLECRUISER:
      locked: false # Macht verfügbar (ohne Venator-Research)
      chance: 25
```

### Komplexe Ereignis-Konfiguration

```yaml
kdy_market:
  events:
    CUSTOM_EVENT:
      adjustments:
        PROCURATOR_BATTLECRUISER: -30
        PRAETOR_I_BATTLECRUISER: +20
      unlocks:
        CUSTOM_SHIP: true
      requirements:
        OLD_SHIP: "[ This ship is no longer available ]"
```

## 📋 Verfügbare Schiffe

### Standard-Schiffe (immer verfügbar)

- `PROCURATOR_BATTLECRUISER` - Chance: 40
- `PRAETOR_I_BATTLECRUISER` - Chance: 20

### Era-abhängige Schiffe

- `ACCLAMATOR_DESTROYER` - Chance: 8 (ab 22 BBY)
- `ACCLAMATOR_BATTLESHIP` - Chance: 6 (ab 22 BBY)

### Forschungs-abhängige Schiffe

- `MAELSTROM_BATTLECRUISER` - Chance: 40 (Venator Research)

### KDY Contract-Schiffe

- `SECUTOR_STAR_DESTROYER` - Chance: 40
- `TECTOR_STAR_DESTROYER` - Chance: 50
- `IMPERATOR_STAR_DESTROYER` - Chance: 50
- `IMPERATOR_STAR_DESTROYER_ASSAULT` - Chance: 10

## 🎮 Praktische Anwendungsfälle

### 1. Balance-Anpassungen

```yaml
kdy_market:
  ships:
    PROCURATOR_BATTLECRUISER:
      chance: 60 # Häufiger verfügbar
    PRAETOR_I_BATTLECRUISER:
      chance: 5 # Seltener verfügbar
```

### 2. Era-Anpassungen

```yaml
kdy_market:
  ships:
    ACCLAMATOR_DESTROYER:
      locked: false # Verfügbar ab Spielstart
      chance: 15
```

### 3. Custom Events

```yaml
kdy_market:
  events:
    MY_CUSTOM_EVENT:
      adjustments:
        PROCURATOR_BATTLECRUISER: -30
        MAELSTROM_BATTLECRUISER: +50
      unlocks:
        SECRET_SHIP: true
```

## 🔧 Technische Details

### Bearbeitete Dateien

- `Scripts/Library/ShipMarketOptions.lua` - Basis-Schiffskonfiguration
- `Scripts/Library/ShipMarketAdjustmentsLibrary.lua` - Event-basierte Anpassungen

### Backup-System

- Automatische Backups der Lua-Dateien
- Wiederherstellung vor jeder Ausführung
- Sicherheit vor kumulativen Änderungen

### Validierung

- Prüfung auf gültige Schiff-Namen
- Validierung von Chance-Werten (0-100)
- Korrekte Lua-Syntax-Generierung

## ⚠️ Wichtige Hinweise

1. **Backup-System**: Immer aktiviert lassen für Sicherheit
2. **Werte-Bereich**: Chance-Werte zwischen 0-100
3. **Lua-Syntax**: Automatische Generierung korrekter Lua-Tabellen
4. **Event-Namen**: Müssen mit den Spiel-Events übereinstimmen
5. **Schiff-Namen**: Müssen exakt mit den Lua-Dateien übereinstimmen

## 🐛 Fehlerbehebung

### "Datei nicht gefunden"

- Prüfe, ob die Lua-Dateien im korrekten Pfad liegen
- Stelle sicher, dass das Tool im richtigen Verzeichnis ausgeführt wird

### "Ungültige Chance-Werte"

- Chance-Werte müssen zwischen 0 und 100 liegen
- Verwende nur positive Zahlen

### "Schiff nicht gefunden"

- Prüfe die exakte Schreibweise des Schiff-Namens
- Vergleiche mit den Namen in den Lua-Dateien

## 📈 Zukünftige Erweiterungen

- [ ] Unterstützung für andere Fraktionen (CIS, Republic)
- [ ] GUI-Interface für einfache Konfiguration
- [ ] Automatische Balance-Tests
- [ ] Integration mit Mod-Managern
- [ ] Erweiterte Event-Systeme

---

**Version**: 1.0  
**Letzte Aktualisierung**: 2025-01-27  
**Autor**: SWMA Tool Development Team
