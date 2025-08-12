# SWMA Tool - Autovervollständigung Setup

## Übersicht

Das SWMA Tool unterstützt jetzt Autovervollständigung für die `shipchanges.yaml` Datei! Dies bietet:

- ✅ **Intelligente Vorschläge** für alle verfügbaren Parameter
- ✅ **Validierung** der Eingabewerte
- ✅ **Tooltips** mit Beschreibungen und Beispielen
- ✅ **Fehlerhervorhebung** bei ungültigen Werten

## Setup-Anleitungen

### 1. Visual Studio Code (Empfohlen)

1. **YAML Extension installieren:**

   - Öffne VS Code
   - Gehe zu Extensions (Ctrl+Shift+X)
   - Suche nach "YAML" von Red Hat
   - Installiere die Extension

2. **Schema zuordnen:**

   - Öffne `shipchanges.yaml`
   - VS Code sollte automatisch das Schema erkennen
   - Falls nicht: Rechtsklick → "Select Schema" → Wähle `shipchanges.schema.json`

3. **Workspace-Einstellungen (Optional):**
   ```json
   {
     "yaml.schemas": {
       "./shipchanges.schema.json": "shipchanges.yaml"
     }
   }
   ```

### 2. IntelliJ IDEA / PyCharm

1. **YAML Plugin installieren:**

   - File → Settings → Plugins
   - Suche nach "YAML" und installiere es

2. **Schema zuordnen:**
   - Rechtsklick auf `shipchanges.yaml`
   - "Associate with Schema"
   - Wähle `shipchanges.schema.json`

### 3. Sublime Text

1. **Package Control installieren** (falls noch nicht geschehen)
2. **YAML Package installieren:**
   - Ctrl+Shift+P → "Package Control: Install Package"
   - Suche nach "YAML" und installiere es

### 4. Vim/Neovim

1. **Coc.nvim installieren:**

   ```vim
   Plug 'neoclide/coc.nvim', {'branch': 'release'}
   ```

2. **YAML Language Server installieren:**

   ```vim
   :CocInstall coc-yaml
   ```

3. **Schema zuordnen:**
   ```vim
   :CocCommand yaml.setSchema shipchanges.schema.json
   ```

## Features der Autovervollständigung

### Template-Änderungen

```yaml
template_changes:
  shield_points: +30% # ✅ Autovervollständigung + Tooltip
  energy_refresh_rate: 500 # ✅ Validierung + Beschreibung
  max_speed: +20% # ✅ Prozent-Format erkannt
```

### Squadron-Konfiguration

```yaml
squadrons:
  delay_seconds: 3 # ✅ Tooltip mit Erklärung
  starting:
    0: # ✅ Tech-Level 0-5 verfügbar
      - type: ARC_130_Squadron # ✅ Dropdown mit allen Squadron-Typen
        count: 3 # ✅ Mindestwert 1 validiert
```

### Hardpoint-Änderungen

```yaml
hardpoints:
  damage_increase: +30% # ✅ Prozent-Format validiert
```

## Verfügbare Squadron-Typen

### Republic

- `ARC_130_Squadron`
- `Nimbus_Squadron`
- `NTB_630_Squadron`
- `V-19_Squadron`
- `Z-95_Squadron`
- `Y-Wing_Squadron`
- `X-Wing_Squadron`
- `A-Wing_Squadron`
- `B-Wing_Squadron`
- `E-Wing_Squadron`
- `Clone_ARC_170_Squadron`
- `Torrent_Squadron`
- `Clone_BTLB_Y_Wing_Squadron`

### Empire

- `TIE_Fighter_Squadron`
- `TIE_Interceptor_Squadron`
- `TIE_Bomber_Squadron`
- `TIE_Advanced_Squadron`
- `TIE_Defender_Squadron`
- `TIE_Phantom_Squadron`
- `TIE_Avenger_Squadron`
- `TIE_Predator_Squadron`

### CIS

- `Vulture_Squadron`
- `Hyena_Squadron`
- `Tri_Fighter_Squadron`
- `Droid_Fighter_Squadron`
- `Droid_Bomber_Squadron`

## Validierungsregeln

### Prozentwerte

- Format: `+30%`, `-15%`, `+100%`
- Gültige Bereiche: `-100%` bis `+1000%`

### Absolute Werte

- Zahlen: `1800`, `500.0`, `1.5`
- Keine Prozentzeichen

### Tech-Level

- Nur `0` bis `5` erlaubt
- String-Format: `"0"`, `"1"`, etc.

## Troubleshooting

### Schema wird nicht erkannt

1. Überprüfe, ob die Datei `shipchanges.schema.json` im gleichen Ordner liegt
2. Stelle sicher, dass der YAML-Editor das Schema unterstützt
3. Versuche, die IDE neu zu starten

### Autovervollständigung funktioniert nicht

1. Überprüfe die Extension/Plugin-Installation
2. Stelle sicher, dass die Datei als YAML erkannt wird
3. Überprüfe die Schema-Zuordnung

### Fehler bei der Validierung

1. Überprüfe die YAML-Syntax (Einrückung, Doppelpunkte)
2. Stelle sicher, dass die Werte dem erwarteten Format entsprechen
3. Konsultiere die Tooltips für gültige Werte

## Beispiel-Konfiguration

```yaml
game_mode: skirmish

units:
  Acclamator_I_Carrier:
    template: Template_Acclamator_I_Carrier
    base_unit: Skirmish_Acclamator_I_Carrier
    template_changes:
      shield_points: +30%
      energy_refresh_rate: +100%
      tactical_health: +25%
      max_speed: +20%
    squadrons:
      delay_seconds: 3
      starting:
        0:
          - type: ARC_130_Squadron
            count: 3
          - type: Nimbus_Squadron
            count: 1
      reserve:
        0:
          - type: ARC_130_Squadron
            count: 2
          - type: NTB_630_Squadron
            count: 1
    hardpoints:
      damage_increase: +30%
```

## Support

Bei Problemen mit der Autovervollständigung:

1. Überprüfe diese README
2. Konsultiere die IDE-spezifische Dokumentation
3. Stelle sicher, dass alle Extensions/Plugins aktuell sind
