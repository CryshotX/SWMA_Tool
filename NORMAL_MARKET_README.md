# SWMA Tool - Normale Markt-Freischaltung

## 🎯 Übersicht

Das SWMA Tool unterstützt jetzt die **Normale Markt-Freischaltung**, die Schiffe direkt im normalen Baumarkt verfügbar macht, ohne auf komplexe Event-Systeme oder Lua-Skripte angewiesen zu sein.

## 🏪 Funktionsweise

### **Automatische Freischaltung**

Wenn `unlock_normal_market: true` für eine Einheit gesetzt ist, führt das Tool folgende Änderungen durch:

1. **`Build_Initially_Locked: Yes → No`** - Entsperrt gesperrte Schiffe
2. **`Tech_Level: 99 → 0`** - Macht Spezial-Szenarien-Schiffe allgemein verfügbar
3. **Automatische Erkennung** - Nur Campaign-Units werden verarbeitet

### **Vorteile**

- ✅ **Zuverlässig** - Keine Lua-Abhängigkeiten
- ✅ **Sofort verfügbar** - Keine Wartezeit auf Events
- ✅ **Einfach** - Funktioniert wie alle anderen Schiffe
- ✅ **Wartbar** - Saubere XML-Bearbeitung

## 📝 Konfiguration

### **Basis-Syntax**

```yaml
units:
  Schiff_Name:
    base_unit: Skirmish_Schiff_Name
    campaign_unit: Campaign_Schiff_Name
    unlock_normal_market: true # Schaltet im normalen Baumarkt frei

    # Weitere Konfigurationen...
    template_changes:
      shield_points: +50%
    hardpoints:
      damage_increase: +100%
```

### **Beispiel-Konfiguration**

```yaml
units:
  Maelstrom_Battlecruiser:
    template: Template_Maelstrom_Battlecruiser
    base_unit: Skirmish_Maelstrom_Battlecruiser
    campaign_unit: Maelstrom_Battlecruiser
    unlock_normal_market: true # ← Schiff wird freigeschaltet
    template_changes:
      shield_refresh_rate: +100%
      shield_points: +50%
      energy_refresh_rate: +100%
      population_value: 15
    hardpoints:
      damage_increase: +100%
      burst_delay_adjustment: -40%
      fire_rate_increase: +50%

  Procurator_Battlecruiser:
    base_unit: Skirmish_Procurator_Battlecruiser
    campaign_unit: Procurator_Battlecruiser
    unlock_normal_market: true # ← Schiff wird freigeschaltet
    template_changes:
      shield_refresh_rate: +180%
      shield_points: +80%
      energy_refresh_rate: +200%
      population_value: 18
```

## 🎮 Verwendung

### **Standard-Ausführung**

```bash
cd XML/SWMA_Tool
python swma.py --config shipchanges.yaml
```

### **Ausgabe-Beispiel**

```
🏪 Schalte Maelstrom_Battlecruiser im normalen Baumarkt frei...
  Build_Initially_Locked: Yes -> No
✅ Maelstrom_Battlecruiser im normalen Baumarkt freigeschaltet

🏪 Schalte Procurator_Battlecruiser im normalen Baumarkt frei...
  Build_Initially_Locked: Yes -> No
✅ Procurator_Battlecruiser im normalen Baumarkt freigeschaltet
```

## 🔧 Technische Details

### **Betroffene Dateien**

- **`XML/Units/Republic_Space_Units.xml`** - Campaign-Units werden modifiziert
- **Keine Lua-Dateien** - Saubere XML-only Lösung

### **XML-Änderungen**

**Vor der Freischaltung:**

```xml
<SpaceUnit Name="Maelstrom_Battlecruiser">
    <Build_Initially_Locked>Yes</Build_Initially_Locked>
    <Tech_Level>0</Tech_Level>
    <!-- ... -->
</SpaceUnit>
```

**Nach der Freischaltung:**

```xml
<SpaceUnit Name="Maelstrom_Battlecruiser">
    <Build_Initially_Locked>No</Build_Initially_Locked>
    <Tech_Level>0</Tech_Level>
    <!-- ... -->
</SpaceUnit>
```

## 🚀 Kompatible Schiffe

Die folgenden Schiffe wurden erfolgreich für die normale Markt-Freischaltung getestet:

- ✅ **Maelstrom_Battlecruiser**
- ✅ **Procurator_Battlecruiser**
- ✅ **Praetor_I_Battlecruiser**
- ✅ **Mandator_II_Dreadnought**

## ⚠️ Hinweise

### **Anforderungen**

- **Campaign-Unit erforderlich** - Das `campaign_unit` Feld muss gesetzt sein
- **Republic Shipyard Level Four** - Schiffe benötigen meist die höchste Werft-Stufe
- **Ausreichende Credits** - Die Schiffe sind teuer (4.000-100.000+ Credits)

### **Backup-System**

Das SWMA Tool erstellt automatisch Backups aller modifizierten Dateien. Die Original-Zustände können jederzeit mit `--reset` wiederhergestellt werden.

### **Kompatibilität**

- ✅ **Skirmish-Modus** - Vollständig unterstützt
- ✅ **Campaign-Modus** - Vollständig unterstützt
- ✅ **Galactic Conquest** - Vollständig unterstützt
- ✅ **Multiplayer** - Vollständig unterstützt

---

**Version**: 3.0  
**Letzte Aktualisierung**: 2025-01-27  
**Ersetzt**: KDY Markt-System (entfernt wegen Instabilität)
