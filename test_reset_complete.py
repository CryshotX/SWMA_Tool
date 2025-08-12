#!/usr/bin/env python3
"""
Umfassender Test des SWMA-Tools
===============================

Testet, ob wirklich ALLE Werte vor jeder Änderung zurückgesetzt werden.
"""

import os
import sys
import yaml
import xml.etree.ElementTree as ET
import shutil
from datetime import datetime
from pathlib import Path
import subprocess

def create_test_config():
    """Erstellt eine Test-Konfiguration mit verschiedenen Änderungen"""
    test_config = {
        'game_mode': 'skirmish',
        'units': {
            'Acclamator_II': {
                'template': 'Template_Acclamator_II',
                'base_unit': 'Skirmish_Acclamator_II',
                'campaign_unit': 'Acclamator_II',
                'template_changes': {
                    'shield_points': '+10%',
                    'energy_refresh_rate': '+20%',
                    'population_value': 10
                },
                'squadrons': {
                    'delay_seconds': 8,
                    'starting': {
                        '0': [
                            {'type': 'Clone_ARC_170_Squadron', 'count': 1}
                        ]
                    },
                    'reserve': {
                        '0': [
                            {'type': 'Clone_ARC_170_Squadron', 'count': 3}
                        ]
                    }
                }
            },
            'Venator': {
                'template': 'Template_Venator_Star_Destroyer',
                'base_unit': 'Skirmish_Venator_Star_Destroyer',
                'campaign_unit': 'Venator_Star_Destroyer',
                'template_changes': {
                    'shield_points': '+10%',
                    'shield_refresh_rate': '+40%',
                    'population_value': 10
                },
                'squadrons': {
                    'delay_seconds': 2,
                    'starting': {
                        '0': [
                            {'type': 'Clone_ARC_170_Squadron', 'count': 2},
                            {'type': 'Clone_Nimbus_V_Wing_Squadron', 'count': 2}
                        ]
                    },
                    'reserve': {
                        '0': [
                            {'type': 'Clone_ARC_170_Squadron', 'count': 8},
                            {'type': 'Clone_Nimbus_V_Wing_Squadron', 'count': 8}
                        ]
                    }
                },
                'hardpoints': {
                    'fire_rate_increase': '+30%'
                }
            }
        }
    }
    
    with open('test_shipchanges.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(test_config, f, default_flow_style=False, indent=2)
    
    print("Test-Konfiguration erstellt: test_shipchanges.yaml")
    return test_config

def get_xml_value(file_path, element_name, attribute_name, tag_name):
    """Liest einen Wert aus einer XML-Datei"""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Suche nach dem Element
        for element in root.findall(f".//{element_name}"):
            if element.get('Name') == attribute_name:
                # Suche nach dem Tag
                tag = element.find(tag_name)
                if tag is not None:
                    return float(tag.text) if tag.text else None
        return None
    except Exception as e:
        print(f"Fehler beim Lesen von {file_path}: {e}")
        return None

def check_file_consistency(file_path, backup_dir):
    """Überprüft, ob eine Datei mit ihrem Backup übereinstimmt"""
    if not os.path.exists(file_path):
        return False, "Datei existiert nicht"
    
    # Finde das neueste Backup
    file_stem = Path(file_path).stem
    backup_pattern = f"{file_stem}_*.xml"
    backup_files = list(Path(backup_dir).glob(backup_pattern))
    
    if not backup_files:
        return False, "Kein Backup gefunden"
    
    latest_backup = max(backup_files, key=lambda x: x.stat().st_mtime)
    
    # Vergleiche Dateien
    try:
        with open(file_path, 'rb') as f1, open(latest_backup, 'rb') as f2:
            if f1.read() == f2.read():
                return True, "Datei stimmt mit Backup überein"
            else:
                return False, "Datei unterscheidet sich vom Backup"
    except Exception as e:
        return False, f"Fehler beim Vergleich: {e}"

def run_swma_test():
    """Führt den vollständigen SWMA-Test durch"""
    print("STARTE UMfassenden SWMA-Test")
    print("=" * 60)
    
    # 1. Test-Konfiguration erstellen
    print("1. Erstelle Test-Konfiguration...")
    test_config = create_test_config()
    
    # 2. Erste Ausführung (sollte Backups erstellen)
    print("\n2. Erste SWMA-Ausführung (Backup-Erstellung)...")
    try:
        result = subprocess.run([
            sys.executable, 'swma.py', 
            '--config', 'test_shipchanges.yaml'
        ], capture_output=True, text=True, cwd='.')
        
        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("Erste Ausführung erfolgreich")
        else:
            print(f"Erste Ausführung fehlgeschlagen (Code: {result.returncode})")
            return False
    except Exception as e:
        print(f"Fehler bei erster Ausführung: {e}")
        return False
    
    # 3. Werte nach erster Ausführung prüfen
    print("\n3. Prüfe Werte nach erster Ausführung...")
    xml_base_dir = Path("..")
    
    # Prüfe Template-Werte
    template_file = xml_base_dir / "Units/Templates_Capitals.xml"
    if template_file.exists():
        shield_points = get_xml_value(template_file, "SpaceUnit", "Template_Acclamator_II", "Shield_Points")
        print(f"Acclamator_II Shield_Points nach erster Ausführung: {shield_points}")
    
    # 4. Zweite Ausführung (sollte automatisch zurücksetzen)
    print("\n4. Zweite SWMA-Ausführung (automatische Wiederherstellung)...")
    try:
        result = subprocess.run([
            sys.executable, 'swma.py', 
            '--config', 'test_shipchanges.yaml'
        ], capture_output=True, text=True, cwd='.')
        
        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("Zweite Ausführung erfolgreich")
        else:
            print(f"Zweite Ausführung fehlgeschlagen (Code: {result.returncode})")
            return False
    except Exception as e:
        print(f"Fehler bei zweiter Ausführung: {e}")
        return False
    
    # 5. Werte nach zweiter Ausführung prüfen
    print("\n5. Prüfe Werte nach zweiter Ausführung...")
    if template_file.exists():
        shield_points_after = get_xml_value(template_file, "SpaceUnit", "Template_Acclamator_II", "Shield_Points")
        print(f"Acclamator_II Shield_Points nach zweiter Ausführung: {shield_points_after}")
    
    # 6. Datei-Konsistenz prüfen
    print("\n6. Prüfe Datei-Konsistenz...")
    backup_dir = Path("backups")
    relevant_files = [
        "Units/Templates_Frigates.xml",
        "Units/Templates_Capitals.xml", 
        "Units/Republic_Space_Units.xml",
        "Units/Skirmish/SkirmishUnits_Republic.xml",
        "Hardpoints/HardPoints_Coresaga_Frigates.xml",
        "Hardpoints/HardPoints_Coresaga_Capitals.xml"
    ]
    
    all_consistent = True
    for file_path in relevant_files:
        full_path = xml_base_dir / file_path
        if full_path.exists():
            consistent, message = check_file_consistency(full_path, backup_dir)
            status = "OK" if consistent else "FEHLER"
            print(f"{status} {file_path}: {message}")
            if not consistent:
                all_consistent = False
    
    # 7. Reset-Test
    print("\n7. Teste expliziten Reset...")
    try:
        result = subprocess.run([
            sys.executable, 'swma.py', 
            '--config', 'test_shipchanges.yaml',
            '--reset'
        ], capture_output=True, text=True, cwd='.')
        
        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("Reset erfolgreich")
        else:
            print(f"Reset fehlgeschlagen (Code: {result.returncode})")
            return False
    except Exception as e:
        print(f"Fehler beim Reset: {e}")
        return False
    
    # 8. Finale Konsistenz-Prüfung
    print("\n8. Finale Konsistenz-Prüfung...")
    final_consistent = True
    for file_path in relevant_files:
        full_path = xml_base_dir / file_path
        if full_path.exists():
            consistent, message = check_file_consistency(full_path, backup_dir)
            status = "OK" if consistent else "FEHLER"
            print(f"{status} {file_path}: {message}")
            if not consistent:
                final_consistent = False
    
    # 9. Aufräumen
    print("\n9. Räume auf...")
    if os.path.exists('test_shipchanges.yaml'):
        os.remove('test_shipchanges.yaml')
        print("Test-Konfiguration entfernt")
    
    # Ergebnis
    print("\n" + "=" * 60)
    if all_consistent and final_consistent:
        print("TEST ERFOLGREICH: Alle Werte werden korrekt zurückgesetzt!")
        return True
    else:
        print("TEST FEHLGESCHLAGEN: Nicht alle Werte werden korrekt zurückgesetzt!")
        return False

if __name__ == "__main__":
    success = run_swma_test()
    sys.exit(0 if success else 1) 