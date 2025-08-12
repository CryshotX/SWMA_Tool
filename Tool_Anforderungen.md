# SWMA Tool - Vollständige Tool-Anforderungen

## Star Wars Modding Assistant - Technische Spezifikation

### 🎯 Projektziel

Entwicklung eines robusten, automatisierten Tools zur Modifikation von Star Wars Empire at War XML-Dateien mit intelligenter Backup-Verwaltung und präziser Hardpoint-Kontrolle.

---

## 🔧 Kernanforderungen

### 1. **Automatische Backup-Wiederherstellung**

**Priorität**: KRITISCH

#### Anforderungen:

- **Erste Ausführung**: Automatische Backups aller relevanten Dateien
- **Jede weitere Ausführung**: Wiederherstellung von Original-Backups vor Änderungen
- **Sicherheit**: Verhindert kumulative Änderungen
- **Zuverlässigkeit**: Immer von echten Originalwerten ausgehend

#### Technische Spezifikation:

```python
class BackupManager:
    def create_initial_backups(self) -> bool:
        # Erstellt Backups bei erster Ausführung
        # Prüft auf existierende Backups
        # Gibt True zurück wenn Backups vorhanden/erstellt

    def restore_from_backups(self) -> bool:
        # Stellt alle Dateien von neuesten Backups wieder her
        # Verwendet Zeitstempel für neueste Backups
        # Gibt True zurück wenn Wiederherstellung erfolgreich
```

#### Relevante Dateien:

- `Units/Templates_Frigates.xml`
- `Units/Templates_Capitals.xml`
- `Units/Republic_Space_Units.xml`
- `Units/Skirmish/SkirmishUnits_Republic.xml`
- `Hardpoints/HardPoints_Coresaga_Frigates.xml`
- `Hardpoints/HardPoints_Coresaga_Capitals.xml`

### 2. **Hardpoint-Mechaniken**

**Priorität**: HOCH

#### Anforderungen:

- **Fire Rate Increase**: Reduziert `Fire_Min/Max_Recharge_Seconds`
- **Damage Increase**: Erhöht `Fire_Pulse_Count`
- **Burst Delay Adjustment**: Kontrolliert `Fire_Pulse_Delay_Seconds`
- **Präzision**: Mindestverzögerung von 0.05 Sekunden

#### Technische Spezifikation:

```python
def apply_hardpoint_changes(self, unit_config, hardpoint_file, unit_name):
    # Fire Rate Increase
    if 'fire_rate_increase' in changes:
        new_value = current_value / (1 + percent / 100)

    # Damage Increase
    if 'damage_increase' in changes:
        new_value = max(current_value + 1, int(current_value * (1 + percent / 100)))

    # Burst Delay Adjustment
    if 'burst_delay_adjustment' in changes:
        new_value = current_value * (1 + percent / 100)
        new_value = max(0.05, new_value)  # Minimum
```

#### WICHTIG:

- `<Damage>` Tag ist **nur für Auto-Resolve** relevant
- **Echte Kampfschäden** werden durch Hardpoint-Parameter kontrolliert
- **Additive Vererbung** beachten - Werte werden addiert, nicht überschrieben

### 3. **Intelligente Geschwader-Platzierung**

**Priorität**: HOCH

#### Anforderungen:

- **Automatische Erkennung**: Template-basierte vs. Campaign-basierte Units
- **Doppelte Geschwader-Verhinderung**: Entfernt Tags aus der anderen Datei
- **Korrekte Platzierung**: Template-basiert → SkirmishUnits, Campaign-basiert → Republic_Space_Units

#### Technische Spezifikation:

```python
def is_template_based_skirmish_unit(self, unit_config) -> bool:
    # Prüft Variant_Of_Existing_Type
    # True wenn Template_ Prefix vorhanden

def apply_skirmish_squadron_changes(self, unit_config):
    if is_template_based:
        # Geschwader in SkirmishUnits definieren
        # Aus Republic_Space_Units entfernen
    else:
        # Geschwader in Republic_Space_Units definieren
        # Aus SkirmishUnits entfernen
```

#### Geschwader-Tags:

```xml
<Spawned_Squadron_Delay_Seconds>0.0</Spawned_Squadron_Delay_Seconds>
<Starting_Spawned_Units_Tech_0>Squadron_Name, Count</Starting_Spawned_Units_Tech_0>
<Reserve_Spawned_Units_Tech_0>Squadron_Name, Count</Reserve_Spawned_Units_Tech_0>
```

---

## ⚙️ Konfigurationsanforderungen

### 1. **YAML-Konfiguration**

**Priorität**: MITTEL

#### Anforderungen:

- **Lesbarkeit**: Klare, strukturierte Konfiguration
- **Flexibilität**: Prozentuale und absolute Werte
- **Validierung**: JSON-Schema für Autocompletion
- **Erweiterbarkeit**: Einfache Hinzufügung neuer Parameter

#### Grundstruktur:

```yaml
game_mode: skirmish # oder campaign

units:
  Unit_Name:
    template: Template_Unit_Name
    base_unit: Skirmish_Unit_Name
    campaign_unit: Campaign_Unit_Name

    template_changes:
      shield_points: +10%
      energy_refresh_rate: +20%

    squadrons:
      delay_seconds: 0
      starting:
        0: # Tech Level
          - type: Clone_Arc_170_Squadron
            count: 2
      reserve:
        0:
          - type: Clone_Arc_170_Squadron
            count: 4

    hardpoints:
      fire_rate_increase: +100%
      damage_increase: +200%
      burst_delay_adjustment: -25%
```

### 2. **JSON-Schema**

**Priorität**: MITTEL

#### Anforderungen:

- **Autocompletion**: IntelliSense für YAML-Dateien
- **Validierung**: Syntax- und Typ-Überprüfung
- **Dokumentation**: Beschreibungen für alle Parameter
- **Erweiterbarkeit**: Einfache Hinzufügung neuer Felder

---

## 🚀 Funktionsanforderungen

### 1. **Kommandozeilen-Interface**

**Priorität**: HOCH

#### Anforderungen:

```bash
# Standard-Ausführung
python swma.py --config shipchanges.yaml

# Ohne Backups (nicht empfohlen)
python swma.py --config shipchanges.yaml --no-backup

# Vorschau-Modus
python swma.py --config shipchanges.yaml --preview

# Reset aller Änderungen
python swma.py --config shipchanges.yaml --reset

# Reset einer spezifischen Einheit
python swma.py --config shipchanges.yaml --reset-unit "Unit_Name"
```

### 2. **Workflow**

**Priorität**: HOCH

#### Anforderungen:

1. **Konfiguration laden**: YAML-Datei parsen und validieren
2. **Backup-Prüfung**: Existierende Backups erkennen oder erstellen
3. **Wiederherstellung**: Alle Dateien von Backups wiederherstellen
4. **Änderungen anwenden**: Neue Modifikationen implementieren
5. **Validierung**: Erfolgreiche Anwendung bestätigen

### 3. **Fehlerbehandlung**

**Priorität**: HOCH

#### Anforderungen:

- **Robuste Fehlerbehandlung**: Graceful Degradation
- **Detaillierte Logs**: Klare Fehlermeldungen
- **Rollback-Mechanismus**: Automatische Wiederherstellung bei Fehlern
- **Validierung**: Vor-Ausführung-Prüfungen

---

## 🔒 Sicherheitsanforderungen

### 1. **Backup-Sicherheit**

**Priorität**: KRITISCH

#### Anforderungen:

- **Immer Backups aktiviert**: Standard-Verhalten
- **Backup-Verzeichnis schützen**: Nicht löschbar während Ausführung
- **Zeitstempel**: Eindeutige Backup-Identifikation
- **Integritätsprüfung**: Backup-Validierung

### 2. **Datenintegrität**

**Priorität**: HOCH

#### Anforderungen:

- **XML-Validierung**: Korrekte XML-Struktur
- **Wert-Validierung**: Sinnvolle Parameter-Bereiche
- **Referenz-Validierung**: Existierende Unit-Namen
- **Konsistenz-Prüfung**: Logische Widersprüche vermeiden

---

## 📈 Performance-Anforderungen

### 1. **Ausführungsgeschwindigkeit**

**Priorität**: MITTEL

#### Anforderungen:

- **Schnelle Ausführung**: < 30 Sekunden für typische Konfigurationen
- **Effiziente XML-Verarbeitung**: Optimierte Parsing-Strategien
- **Minimale Speichernutzung**: Effiziente Datenstrukturen
- **Skalierbarkeit**: Unterstützung für große Konfigurationen

### 2. **Ressourcenverbrauch**

**Priorität**: NIEDRIG

#### Anforderungen:

- **Minimaler Speicherverbrauch**: < 100MB für typische Ausführungen
- **CPU-Effizienz**: Optimierte Algorithmen
- **Disk-I/O**: Minimale Datei-Operationen
- **Netzwerk**: Keine externen Abhängigkeiten

---

## 🧪 Testanforderungen

### 1. **Funktionale Tests**

**Priorität**: HOCH

#### Anforderungen:

- **Unit-Tests**: Alle Kernfunktionen
- **Integration-Tests**: End-to-End-Workflows
- **Regression-Tests**: Verhindert Breaking Changes
- **Edge-Case-Tests**: Grenzfälle und Fehlerszenarien

### 2. **Validierungstests**

**Priorität**: MITTEL

#### Anforderungen:

- **YAML-Validierung**: Korrekte Konfigurationsdateien
- **XML-Validierung**: Korrekte Ausgabe-Dateien
- **Backup-Validierung**: Funktionale Backup-Wiederherstellung
- **Performance-Tests**: Ausführungsgeschwindigkeit

---

## 📚 Dokumentationsanforderungen

### 1. **Benutzerdokumentation**

**Priorität**: HOCH

#### Anforderungen:

- **Vollständige Anleitung**: Schritt-für-Schritt-Tutorials
- **Beispiele**: Praktische Konfigurationsbeispiele
- **Troubleshooting**: Häufige Probleme und Lösungen
- **Best Practices**: Empfohlene Vorgehensweisen

### 2. **Entwicklerdokumentation**

**Priorität**: MITTEL

#### Anforderungen:

- **API-Dokumentation**: Alle öffentlichen Funktionen
- **Architektur-Beschreibung**: System-Design und -Struktur
- **Erweiterungsanleitung**: Hinzufügung neuer Features
- **Code-Kommentare**: Inline-Dokumentation

---

## 🔮 Zukünftige Erweiterungen

### 1. **Geplante Features**

**Priorität**: NIEDRIG

#### Anforderungen:

- **Multi-Fraktion-Support**: CIS, Empire, andere Fraktionen
- **GUI-Interface**: Benutzerfreundliche Oberfläche
- **Batch-Verarbeitung**: Mehrere Konfigurationen gleichzeitig
- **Mod-Integration**: Integration mit Mod-Managern

### 2. **Technische Verbesserungen**

**Priorität**: NIEDRIG

#### Anforderungen:

- **Caching-System**: Performance-Optimierung
- **Erweiterte Validierung**: Umfassendere Prüfungen
- **Logging-System**: Detaillierte Ausführungsprotokolle
- **Plugin-System**: Erweiterbare Architektur

---

## 📊 Erfolgskriterien

### 1. **Funktionale Kriterien**

- ✅ **Backup-Wiederherstellung**: 100% zuverlässig
- ✅ **Hardpoint-Modifikationen**: Präzise und konsistent
- ✅ **Geschwader-Platzierung**: Intelligente und korrekte Logik
- ✅ **Fehlerbehandlung**: Robuste und informative Fehlermeldungen

### 2. **Performance-Kriterien**

- ✅ **Ausführungszeit**: < 30 Sekunden für typische Konfigurationen
- ✅ **Speicherverbrauch**: < 100MB für normale Ausführungen
- ✅ **Skalierbarkeit**: Unterstützung für 100+ Units

### 3. **Benutzerfreundlichkeit**

- ✅ **Einfache Konfiguration**: Klare YAML-Struktur
- ✅ **Autocompletion**: IntelliSense-Unterstützung
- ✅ **Dokumentation**: Vollständige und verständliche Anleitungen
- ✅ **Fehlerbehandlung**: Benutzerfreundliche Fehlermeldungen

---

## 🎯 Prioritäten-Matrix

| Anforderung              | Priorität | Aufwand | Risiko  | Status            |
| ------------------------ | --------- | ------- | ------- | ----------------- |
| Backup-Wiederherstellung | KRITISCH  | HOCH    | NIEDRIG | ✅ IMPLEMENTIERT  |
| Hardpoint-Mechaniken     | HOCH      | MITTEL  | NIEDRIG | ✅ IMPLEMENTIERT  |
| Geschwader-Platzierung   | HOCH      | MITTEL  | MITTEL  | ✅ IMPLEMENTIERT  |
| YAML-Konfiguration       | MITTEL    | NIEDRIG | NIEDRIG | ✅ IMPLEMENTIERT  |
| JSON-Schema              | MITTEL    | NIEDRIG | NIEDRIG | ✅ IMPLEMENTIERT  |
| CLI-Interface            | HOCH      | NIEDRIG | NIEDRIG | ✅ IMPLEMENTIERT  |
| Fehlerbehandlung         | HOCH      | MITTEL  | MITTEL  | ✅ IMPLEMENTIERT  |
| Performance-Optimierung  | MITTEL    | HOCH    | MITTEL  | 🔄 IN ENTWICKLUNG |
| GUI-Interface            | NIEDRIG   | HOCH    | MITTEL  | 📋 GEPLANT        |
| Multi-Fraktion-Support   | NIEDRIG   | HOCH    | HOCH    | 📋 GEPLANT        |

---

**Version**: 2.0  
**Letzte Aktualisierung**: 2025-08-02  
**Status**: ✅ KERNANFORDERUNGEN IMPLEMENTIERT  
**Nächste Schritte**: Performance-Optimierung und erweiterte Features
