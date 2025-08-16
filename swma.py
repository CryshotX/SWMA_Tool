#!/usr/bin/env python3
"""
Star Wars Modding Automation Tool (SWMA)
========================================

Ein Tool zur automatischen Modifikation von Star Wars Empire at War XML-Dateien.
Unterstützt Skirmish und Campaign-Modi mit intelligenter Datei-Erkennung.
"""

import os
import sys
import yaml
import xml.etree.ElementTree as ET
import shutil
from datetime import datetime
from pathlib import Path
import argparse
import re
import subprocess
from typing import Dict, List, Any, Optional, Tuple

class BackupManager:
    """Verwaltet Backups der Original-Dateien mit automatischer Wiederherstellung"""
    
    def __init__(self, backup_dir: str = "backups", xml_base_dir: Path = None):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        self.xml_base_dir = xml_base_dir
        
        # Liste aller relevanten Dateien für Backups
        self.relevant_files = [
            "Units/Templates_Frigates.xml",
            "Units/Templates_Capitals.xml", 
            "Units/Republic_Space_Units.xml",
            "Units/Skirmish/SkirmishUnits_Republic.xml",
            "Hardpoints/HardPoints_Coresaga_Frigates.xml",
            "Hardpoints/HardPoints_Coresaga_Capitals.xml"
        ]
    
    def create_backup(self, file_path: str) -> str:
        """Erstellt ein Backup einer Datei, aber nur wenn noch kein Backup existiert"""
        source_path = Path(file_path)
        if not source_path.exists():
            raise FileNotFoundError(f"Datei nicht gefunden: {file_path}")
        
        backup_name = f"{source_path.stem}_original{source_path.suffix}"
        backup_path = self.backup_dir / backup_name
        
        if backup_path.exists():
            # Backup existiert bereits, nichts tun
            return str(backup_path)
        
        shutil.copy2(source_path, backup_path)
        print(f"Backup erstellt: {backup_path}")
        return str(backup_path)
    
    def restore_backup(self, backup_path: str, target_path: str):
        """Stellt eine Datei aus einem Backup wieder her"""
        shutil.copy2(backup_path, target_path)
        print(f"Backup wiederhergestellt: {target_path}")
    
    def create_initial_backups(self) -> bool:
        """Erstellt Backups aller relevanten Dateien bei der ersten Ausführung"""
        print("Prüfe auf existierende Backups...")
        
        # Prüfe ob bereits Backups existieren
        backup_files = list(self.backup_dir.glob("*_original.xml"))
        if len(backup_files) >= len(self.relevant_files):
            print(f"Backups bereits vorhanden ({len(backup_files)} Dateien)")
            return True
        
        if not self.xml_base_dir:
            print("XML-Basis-Verzeichnis nicht gesetzt")
            return False
        
        print("Erstelle initiale Backups aller relevanten Dateien...")
        created_count = 0
        
        for file_path in self.relevant_files:
            source_path = self.xml_base_dir / file_path
            backup_name = f"{source_path.stem}_original.xml"
            backup_path = self.backup_dir / backup_name
            if source_path.exists() and not backup_path.exists():
                try:
                    shutil.copy2(source_path, backup_path)
                    print(f"Backup erstellt: {backup_name}")
                    created_count += 1
                except Exception as e:
                    print(f"Fehler beim Backup von {file_path}: {e}")
            elif backup_path.exists():
                print(f"Backup existiert bereits: {backup_name}")
            else:
                print(f"Datei nicht gefunden: {file_path}")
        
        if created_count > 0:
            print(f"{created_count} Backups erfolgreich erstellt")
            return True
        else:
            print("Keine neuen Backups erstellt")
            return False
    
    def restore_from_backups(self) -> bool:
        """Stellt alle Dateien von den Original-Backups wieder her"""
        if not self.xml_base_dir:
            print("XML-Basis-Verzeichnis nicht gesetzt")
            return False
        
        print("Stelle Dateien von Backups wieder her...")
        restored_count = 0
        
        for file_path in self.relevant_files:
            source_path = self.xml_base_dir / file_path
            backup_name = f"{source_path.stem}_original.xml"
            backup_path = self.backup_dir / backup_name
            if not source_path.exists() or not backup_path.exists():
                continue
            try:
                shutil.copy2(backup_path, source_path)
                print(f"Wiederhergestellt: {file_path} von {backup_name}")
                restored_count += 1
            except Exception as e:
                print(f"Fehler bei Wiederherstellung von {file_path}: {e}")
        
        if restored_count > 0:
            print(f"{restored_count} Dateien erfolgreich wiederhergestellt")
            return True
        else:
            print("Keine Dateien wiederhergestellt")
            return False

class XMLProcessor:
    """Verarbeitet XML-Dateien für Modifikationen"""
    
    def __init__(self):
        # XML-Namespace für Empire at War
        self.namespace = {'eaw': 'http://www.petroglyphgames.com/empireatwar'}
        ET.register_namespace('', self.namespace['eaw'])
    
    def load_xml(self, file_path: str) -> ET.ElementTree:
        """Lädt eine XML-Datei"""
        try:
            tree = ET.parse(file_path)
            return tree
        except ET.ParseError as e:
            raise ValueError(f"XML-Parse-Fehler in {file_path}: {e}")
    
    def save_xml(self, tree: ET.ElementTree, file_path: str):
        """Speichert eine XML-Datei"""
        tree.write(file_path, encoding='utf-8', xml_declaration=True)
        print(f"XML-Datei gespeichert: {file_path}")
    
    def find_unit_element(self, tree: ET.ElementTree, unit_name: str) -> Optional[ET.Element]:
        """Findet ein Unit-Element in der XML-Datei"""
        root = tree.getroot()
        
        # Verschiedene mögliche Element-Namen
        element_names = [
            f"{{http://www.petroglyphgames.com/empireatwar}}SpaceUnit",
            f"{{http://www.petroglyphgames.com/empireatwar}}SkirmishSpaceUnit",
            "SpaceUnit",
            "SkirmishSpaceUnit"
        ]
        
        for element_name in element_names:
            for element in root.findall(f".//{element_name}"):
                if element.get('Name') == unit_name:
                    return element
        
        return None
    
    def find_template_element(self, tree: ET.ElementTree, template_name: str) -> Optional[ET.Element]:
        """Findet ein Template-Element in der XML-Datei"""
        root = tree.getroot()
        
        # Verschiedene mögliche Template-Element-Namen
        element_names = [
            f"{{http://www.petroglyphgames.com/empireatwar}}SpaceUnit",
            "SpaceUnit"
        ]
        
        for element_name in element_names:
            for element in root.findall(f".//{element_name}"):
                if element.get('Name') == template_name:
                    return element
        
        return None
    
    def find_hardpoint_elements(self, tree: ET.ElementTree, ship_type: str) -> List[ET.Element]:
        """Findet Hardpoint-Elemente für einen Schiffstyp"""
        root = tree.getroot()
        hardpoints = []
        
        # Suche nach Hardpoint-Elementen
        for element in root.findall(".//HardPoint"):
            name = element.get('Name', '')
            if ship_type.lower() in name.lower():
                hardpoints.append(element)
        
        return hardpoints
    
    def get_original_value(self, element: ET.Element, tag_name: str) -> Optional[float]:
        """Ermittelt den Originalwert eines Tags"""
        # Versuche verschiedene Schreibweisen
        possible_names = [tag_name, tag_name.title(), tag_name.upper()]
        
        for name in possible_names:
            tag = element.find(name)
            if tag is not None and tag.text:
                try:
                    return float(tag.text)
                except ValueError:
                    continue
        
        return None
    
    def set_value(self, element: ET.Element, tag_name: str, value: Any):
        """Setzt einen Wert in einem XML-Element"""
        # Versuche verschiedene Schreibweisen
        possible_names = [tag_name, tag_name.title(), tag_name.upper()]
        
        for name in possible_names:
            tag = element.find(name)
            if tag is not None:
                tag.text = str(value)
                return
        
        # Tag erstellen falls nicht vorhanden
        new_tag = ET.SubElement(element, tag_name)
        new_tag.text = str(value)
    
    def remove_squadron_tags(self, element: ET.Element):
        """Entfernt alle Squadron-bezogenen Tags"""
        squadron_tags = [
            # Korrekte Tags (ohne tech_)
            'Starting_Spawned_Units_Tech_0', 'Starting_Spawned_Units_Tech_1',
            'Starting_Spawned_Units_Tech_2', 'Starting_Spawned_Units_Tech_3',
            'Starting_Spawned_Units_Tech_4', 'Starting_Spawned_Units_Tech_5',
            'Reserve_Spawned_Units_Tech_0', 'Reserve_Spawned_Units_Tech_1',
            'Reserve_Spawned_Units_Tech_2', 'Reserve_Spawned_Units_Tech_3',
            'Reserve_Spawned_Units_Tech_4', 'Reserve_Spawned_Units_Tech_5',
            # Falsche Tags (mit tech_) - für Kompatibilität
            'Starting_Spawned_Units_Tech_tech_0', 'Starting_Spawned_Units_Tech_tech_1',
            'Starting_Spawned_Units_Tech_tech_2', 'Starting_Spawned_Units_Tech_tech_3',
            'Starting_Spawned_Units_Tech_tech_4', 'Starting_Spawned_Units_Tech_tech_5',
            'Reserve_Spawned_Units_Tech_tech_0', 'Reserve_Spawned_Units_Tech_tech_1',
            'Reserve_Spawned_Units_Tech_tech_2', 'Reserve_Spawned_Units_Tech_tech_3',
            'Reserve_Spawned_Units_Tech_tech_4', 'Reserve_Spawned_Units_Tech_tech_5'
        ]
        
        for tag_name in squadron_tags:
            for tag in element.findall(tag_name):
                element.remove(tag)
    
    def add_squadron_tag(self, element: ET.Element, tag_name: str, squadron_type: str, count: int):
        """Fügt einen Squadron-Tag hinzu"""
        tag = ET.SubElement(element, tag_name)
        tag.text = f"{squadron_type}, {count}"

class SWModdingTool:
    """Hauptklasse für das Star Wars Modding Automation Tool"""
    
    def __init__(self, config_file: str, backup_originals: bool = True):
        self.config_file = config_file
        
        # XML-Verzeichnis ermitteln (übergeordnetes Verzeichnis)
        self.xml_base_dir = Path(__file__).parent.parent
        
        # BackupManager mit XML-Basis-Verzeichnis initialisieren
        self.backup_manager = BackupManager(xml_base_dir=self.xml_base_dir) if backup_originals else None
        self.xml_processor = XMLProcessor()
        self.config = self.load_config()
        
        # Text-Verzeichnis (Schwesterordner von XML)
        self.text_base_dir = self.xml_base_dir.parent / "Text"
        # Merker: Wurden Text/Tooltip-Dateien geändert?
        self.text_changes_applied: bool = False
        
        # KDY Markt Lua-Dateien
        self.ship_market_options = self.xml_base_dir.parent / "Scripts/Library/ShipMarketOptions.lua"
        self.ship_market_adjustments = self.xml_base_dir.parent / "Scripts/Library/ShipMarketAdjustmentsLibrary.lua"
        
    def load_config(self) -> Dict[str, Any]:
        """Lädt die Konfigurationsdatei"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            raise FileNotFoundError(f"Konfigurationsdatei nicht gefunden: {self.config_file}")
        except yaml.YAMLError as e:
            raise ValueError(f"YAML-Parse-Fehler: {e}")
    
    def get_ship_class(self, unit_name: str) -> str:
        """Ermittelt die Schiffsklasse basierend auf dem Namen"""
        frigate_keywords = ['acclamator', 'venator', 'victory', 'frigate']
        # Erweiterte Erkennung für Großkampfschiffe/Battlecruiser/Dreadnoughts
        capital_keywords = [
            'star_destroyer', 'tector', 'secutor', 'capital',
            'praetor', 'procurator', 'mandator', 'maelstrom',
            'battlecruiser', 'dreadnought', 'imperator'
        ]
        
        unit_lower = unit_name.lower()
        
        for keyword in frigate_keywords:
            if keyword in unit_lower:
                return "Frigates"
        
        for keyword in capital_keywords:
            if keyword in unit_lower:
                return "Capitals"
        
        return "Frigates"  # Standard
    
    def get_target_files(self, unit_name: str, game_mode: str) -> Dict[str, str]:
        """Ermittelt die Ziel-Dateien für eine Einheit"""
        ship_class = self.get_ship_class(unit_name)
        
        files = {
            'template': str(self.xml_base_dir / f"Units/Templates_{ship_class}.xml"),
            'hardpoints': str(self.xml_base_dir / f"Hardpoints/HardPoints_Coresaga_{ship_class}.xml"),
            'skirmish_file': str(self.xml_base_dir / "Units/Skirmish/SkirmishUnits_Republic.xml"),
            'campaign_file': str(self.xml_base_dir / "Units/Republic_Space_Units.xml")
        }
        
        # Vereinfacht - beide Dateien werden bereitgestellt, die Entscheidung wird in apply_squadron_changes getroffen
        if game_mode == "skirmish":
            files['squadrons'] = files['skirmish_file']
        else:
            files['squadrons'] = files['campaign_file']
        
        return files
    
    def is_template_based_skirmish_unit(self, unit_config: Dict[str, Any]) -> bool:
        """Prüft, ob eine SkirmishUnit direkt auf einem Template basiert"""
        base_unit = unit_config.get('base_unit', '')
        campaign_unit = unit_config.get('campaign_unit', '')
        
        # Lade die SkirmishUnits_Republic.xml und prüfe die Variant_Of_Existing_Type
        skirmish_file = str(self.xml_base_dir / "Units/Skirmish/SkirmishUnits_Republic.xml")
        
        try:
            tree = self.xml_processor.load_xml(skirmish_file)
            unit_element = self.xml_processor.find_unit_element(tree, base_unit)
            
            if unit_element is not None:
                variant_element = unit_element.find('Variant_Of_Existing_Type')
                if variant_element is not None and variant_element.text:
                    variant_type = variant_element.text.strip()
                    # Prüfe, ob es direkt auf ein Template verweist
                    return variant_type.startswith('Template_')
        except Exception as e:
            print(f"Warnung: Konnte Template-Basis für {base_unit} nicht ermitteln: {e}")
        
        return False
    
    def calculate_percentage_value(self, original_value: float, percentage: str) -> float:
        """Berechnet einen neuen Wert basierend auf einer prozentualen Änderung"""
        if not percentage.endswith('%'):
            raise ValueError(f"Ungültiges Prozentformat: {percentage}")
        
        try:
            percent_value = float(percentage.rstrip('%'))
            return original_value * (1 + percent_value / 100)
        except ValueError:
            raise ValueError(f"Ungültiger Prozentwert: {percentage}")
    
    def apply_cost_changes(self, unit_config: Dict[str, Any], skirmish_file: str):
        """Wendet Kaufpreis-Änderungen an"""
        if 'cost_changes' not in unit_config:
            return
        
        print(f"Wende Kaufpreis-Änderungen an: {skirmish_file}")
        
        # XML laden
        tree = self.xml_processor.load_xml(skirmish_file)
        base_unit = unit_config.get('base_unit')
        
        if not base_unit:
            print(f"Kein base_unit für Einheit angegeben")
            return
        
        unit_element = self.xml_processor.find_unit_element(tree, base_unit)
        if not unit_element:
            print(f"Skirmish-Unit nicht gefunden: {base_unit}")
            return
        
        # Änderungen anwenden
        changes = unit_config['cost_changes']
        
        for property_name, change_value in changes.items():
            original_value = self.xml_processor.get_original_value(unit_element, property_name)
            
            if original_value is None:
                print(f"Warnung: Originalwert nicht gefunden für {property_name}")
                continue
            
            if isinstance(change_value, str) and change_value.endswith('%'):
                new_value = self.calculate_percentage_value(original_value, change_value)
            else:
                new_value = change_value
            
            # Stelle sicher, dass der Wert eine ganze Zahl ist
            new_value = int(new_value)
            
            self.xml_processor.set_value(unit_element, property_name, new_value)
            print(f"  {property_name}: {original_value} -> {new_value}")
        
        # Speichern
        self.xml_processor.save_xml(tree, skirmish_file)

    def apply_template_changes(self, unit_config: Dict[str, Any], template_file: str):
        """Wendet Template-Änderungen an"""
        if 'template_changes' not in unit_config:
            return
        
        print(f"Wende Template-Änderungen an: {template_file}")
        
        # XML laden
        tree = self.xml_processor.load_xml(template_file)
        template_name = unit_config.get('template')
        
        if not template_name:
            print(f"Kein Template für Einheit angegeben – versuche, Änderungen direkt auf Units anzuwenden")
            self.apply_unit_changes_fallback(unit_config)
            return
        
        template_element = self.xml_processor.find_template_element(tree, template_name)
        if not template_element:
            print(f"Template nicht gefunden: {template_name}")
            return
        
        # Änderungen anwenden
        changes = unit_config['template_changes']
        updated_values = {}  # Speichere aktualisierte Werte für Tooltips
        
        for property_name, change_value in changes.items():
            original_value = self.xml_processor.get_original_value(template_element, property_name)
            
            if original_value is None:
                print(f"Warnung: Originalwert nicht gefunden für {property_name}")
                continue
            
            if isinstance(change_value, str) and change_value.endswith('%'):
                new_value = self.calculate_percentage_value(original_value, change_value)
            else:
                new_value = change_value

            # Schildwerte immer auf ganze Zahlen runden
            if property_name in ("shield_points", "shield_refresh_rate"):
                try:
                    new_value = int(round(float(new_value)))
                except Exception:
                    pass
            
            self.xml_processor.set_value(template_element, property_name, new_value)
            print(f"  {property_name}: {original_value} -> {new_value}")
            
            # Speichere für Tooltip-Updates
            updated_values[property_name] = new_value
        
        # Speichern
        self.xml_processor.save_xml(tree, template_file)

        # Tooltips/Textdateien aktualisieren, falls relevante Werte angepasst wurden
        if any(k in updated_values for k in ("shield_points", "shield_refresh_rate", "tactical_health")):
            try:
                self.update_tooltips_for_unit(unit_config, updated_values)
            except Exception as e:
                print(f"Warnung: Konnte Tooltips nicht aktualisieren: {e}")
    

    
    def apply_squadron_changes(self, unit_config: Dict[str, Any], squadron_file: str):
        """Wendet Squadron-Änderungen an mit neuer Logik"""
        if 'squadrons' not in unit_config:
            return
        
        game_mode = self.config.get('game_mode', 'skirmish')
        
        if game_mode == "skirmish":
            # Neue Logik für Skirmish-Modus
            self.apply_skirmish_squadron_changes(unit_config)
        else:
            # Alte Logik für Campaign-Modus beibehalten
            self.apply_single_file_squadron_changes(unit_config, squadron_file)
    
    def apply_skirmish_squadron_changes(self, unit_config: Dict[str, Any]):
        """Wendet Squadron-Änderungen im Skirmish-Modus an - sowohl für Skirmish als auch Campaign"""
        if 'squadrons' not in unit_config:
            return
        
        is_template_based = self.is_template_based_skirmish_unit(unit_config)
        
        skirmish_file = str(self.xml_base_dir / "Units/Skirmish/SkirmishUnits_Republic.xml")
        campaign_file = str(self.xml_base_dir / "Units/Republic_Space_Units.xml")
        
        if is_template_based:
            # Template-basierte Units: Geschwader in BEIDEN Dateien definieren
            print(f"Template-basierte Unit erkannt - Geschwader werden in SkirmishUnits UND Republic_Space_Units definiert")
            self.apply_single_file_squadron_changes(unit_config, skirmish_file)
            self.apply_single_file_squadron_changes(unit_config, campaign_file)
        else:
            # Campaign-basierte Units: Geschwader in BEIDEN Dateien definieren
            print(f"Campaign-basierte Unit erkannt - Geschwader werden in Republic_Space_Units UND SkirmishUnits definiert")
            self.apply_single_file_squadron_changes(unit_config, campaign_file)
            self.apply_single_file_squadron_changes(unit_config, skirmish_file)
    
    def get_original_tech_levels(self, unit_name: str, squadron_file: str) -> List[int]:
        """Ermittelt die ursprünglichen Tech Level aus der Backup-Datei"""
        # Backup-Datei finden
        backup_file = self.find_latest_backup(squadron_file)
        if not backup_file:
            print(f"Warnung: Kein Backup gefunden für {squadron_file}, verwende Standard-Tech-Level")
            if 'Republic_Space_Units.xml' in squadron_file:
                return [1, 2, 4]  # Standard für Campaign
            else:
                return [0]  # Standard für Skirmish
        
        try:
            # Backup-Datei laden
            backup_tree = self.xml_processor.load_xml(backup_file)
            backup_unit = self.xml_processor.find_unit_element(backup_tree, unit_name)
            
            if not backup_unit:
                print(f"Warnung: Einheit {unit_name} nicht im Backup gefunden, verwende Standard-Tech-Level")
                if 'Republic_Space_Units.xml' in squadron_file:
                    return [1, 2, 4]
                else:
                    return [0]
            
            # Alle Squadron-Tags im Backup finden
            tech_levels = set()
            squadron_tags = [
                'Starting_Spawned_Units_Tech_0', 'Starting_Spawned_Units_Tech_1',
                'Starting_Spawned_Units_Tech_2', 'Starting_Spawned_Units_Tech_3',
                'Starting_Spawned_Units_Tech_4', 'Starting_Spawned_Units_Tech_5',
                'Reserve_Spawned_Units_Tech_0', 'Reserve_Spawned_Units_Tech_1',
                'Reserve_Spawned_Units_Tech_2', 'Reserve_Spawned_Units_Tech_3',
                'Reserve_Spawned_Units_Tech_4', 'Reserve_Spawned_Units_Tech_5'
            ]
            
            for tag_name in squadron_tags:
                if backup_unit.find(tag_name) is not None:
                    # Tech Level aus Tag-Namen extrahieren
                    if 'Tech_' in tag_name:
                        tech_part = tag_name.split('Tech_')[-1]
                        try:
                            tech_level = int(tech_part)
                            tech_levels.add(tech_level)
                        except ValueError:
                            continue
            
            if tech_levels:
                return sorted(list(tech_levels))
            else:
                print(f"Warnung: Keine Tech-Level im Backup gefunden für {unit_name}, verwende Standard")
                if 'Republic_Space_Units.xml' in squadron_file:
                    return [1, 2, 4]
                else:
                    return [0]
                    
        except Exception as e:
            print(f"Warnung: Fehler beim Ermitteln der ursprünglichen Tech-Level: {e}")
            if 'Republic_Space_Units.xml' in squadron_file:
                return [1, 2, 4]
            else:
                return [0]

    def apply_single_file_squadron_changes(self, unit_config: Dict[str, Any], squadron_file: str):
        """Wendet Squadron-Änderungen auf eine einzelne Datei an"""
        if 'squadrons' not in unit_config:
            return
        
        print(f"Wende Squadron-Änderungen an: {squadron_file}")
        
        # XML laden
        tree = self.xml_processor.load_xml(squadron_file)
        unit_name = unit_config.get('base_unit') or unit_config.get('campaign_unit') or list(unit_config.keys())[0]
        
        # Für Campaign-Datei verwende campaign_unit Namen
        if 'Republic_Space_Units.xml' in squadron_file:
            unit_name = unit_config.get('campaign_unit', unit_name)
        
        unit_element = self.xml_processor.find_unit_element(tree, unit_name)
        if not unit_element:
            print(f"Einheit nicht gefunden: {unit_name} in {squadron_file}")
            return
        
        squadron_config = unit_config['squadrons']
        
        # Bestehende Squadron-Tags entfernen
        self.xml_processor.remove_squadron_tags(unit_element)
        
        # Ursprüngliche Tech Level aus Backup ermitteln
        tech_levels = self.get_original_tech_levels(unit_name, squadron_file)
        print(f"  Verwende ursprüngliche Tech-Level: {tech_levels}")
        
        # Neue Squadron-Konfiguration für alle Tech Level hinzufügen
        if 'starting' in squadron_config:
            for tech_level in tech_levels:
                # Verwende die Squadrons aus dem ersten konfigurierten Tech Level (normalerweise 0)
                first_tech_level = list(squadron_config['starting'].keys())[0]
                squadrons = squadron_config['starting'][first_tech_level]
                
                for squadron in squadrons:
                    tag_name = f"Starting_Spawned_Units_Tech_{tech_level}"
                    self.xml_processor.add_squadron_tag(
                        unit_element, tag_name, 
                        squadron['type'], squadron['count']
                    )
                    print(f"  {tag_name}: {squadron['type']} x{squadron['count']}")
        
        if 'reserve' in squadron_config:
            for tech_level in tech_levels:
                # Verwende die Squadrons aus dem ersten konfigurierten Tech Level (normalerweise 0)
                first_tech_level = list(squadron_config['reserve'].keys())[0]
                squadrons = squadron_config['reserve'][first_tech_level]
                
                for squadron in squadrons:
                    tag_name = f"Reserve_Spawned_Units_Tech_{tech_level}"
                    self.xml_processor.add_squadron_tag(
                        unit_element, tag_name, 
                        squadron['type'], squadron['count']
                    )
                    print(f"  {tag_name}: {squadron['type']} x{squadron['count']}")
        
        # Delay anpassen
        if 'delay_seconds' in squadron_config:
            self.xml_processor.set_value(
                unit_element, 'Spawned_Squadron_Delay_Seconds', 
                squadron_config['delay_seconds']
            )
            print(f"  Spawned_Squadron_Delay_Seconds: {squadron_config['delay_seconds']}")
        
        # Speichern
        self.xml_processor.save_xml(tree, squadron_file)
    
    def remove_squadron_from_file(self, unit_config: Dict[str, Any], squadron_file: str):
        """Entfernt Squadron-Konfiguration aus einer Datei"""
        print(f"Entferne eventuell vorhandene Geschwader aus: {squadron_file}")
        
        try:
            # XML laden
            tree = self.xml_processor.load_xml(squadron_file)
            unit_name = unit_config.get('base_unit') or unit_config.get('campaign_unit') or list(unit_config.keys())[0]
            
            # Für Campaign-Datei verwende campaign_unit Namen
            if 'Republic_Space_Units.xml' in squadron_file:
                unit_name = unit_config.get('campaign_unit', unit_name)
            
            unit_element = self.xml_processor.find_unit_element(tree, unit_name)
            if unit_element is not None:
                # Nur Squadron-Tags entfernen
                self.xml_processor.remove_squadron_tags(unit_element)
                print(f"  Squadron-Tags entfernt für: {unit_name}")
                
                # Speichern
                self.xml_processor.save_xml(tree, squadron_file)
            else:
                print(f"  Einheit nicht gefunden: {unit_name} in {squadron_file}")
        except Exception as e:
            print(f"  Warnung: Konnte Geschwader nicht aus {squadron_file} entfernen: {e}")
    
    def apply_hardpoint_changes(self, unit_config: Dict[str, Any], hardpoint_file: str, unit_name: str):
        """Wendet Hardpoint-Änderungen an"""
        if 'hardpoints' not in unit_config:
            return
        
        print(f"Wende Hardpoint-Änderungen an: {hardpoint_file}")
        
        # XML laden
        tree = self.xml_processor.load_xml(hardpoint_file)
        
        # Den ersten Teil des Unit-Namens für die Hardpoint-Suche verwenden
        ship_type = unit_name.split('_')[0]  # "Acclamator" aus "Acclamator_I_Carrier"
        
        hardpoint_elements = self.xml_processor.find_hardpoint_elements(tree, ship_type)
        if not hardpoint_elements:
            print(f"Keine Hardpoints gefunden für: {ship_type}")
            return
        
        hardpoint_config = unit_config['hardpoints']
        
        # Fire Rate Increase: Feuerrate erhöhen (Recharge verringern)
        if 'fire_rate_increase' in hardpoint_config:
            fire_rate_increase = hardpoint_config['fire_rate_increase']
            if isinstance(fire_rate_increase, str) and fire_rate_increase.endswith('%'):
                percent_value = float(fire_rate_increase.rstrip('%'))
                
                for hardpoint in hardpoint_elements:
                    min_recharge = self.xml_processor.get_original_value(
                        hardpoint, 'Fire_Min_Recharge_Seconds'
                    )
                    max_recharge = self.xml_processor.get_original_value(
                        hardpoint, 'Fire_Max_Recharge_Seconds'
                    )
                    
                    if min_recharge is not None:
                        new_min_recharge = min_recharge / (1 + percent_value / 100)
                        self.xml_processor.set_value(
                            hardpoint, 'Fire_Min_Recharge_Seconds', new_min_recharge
                        )
                        print(f"  {hardpoint.get('Name')} Min_Recharge: {min_recharge} -> {new_min_recharge:.3f}")
                    
                    if max_recharge is not None:
                        new_max_recharge = max_recharge / (1 + percent_value / 100)
                        self.xml_processor.set_value(
                            hardpoint, 'Fire_Max_Recharge_Seconds', new_max_recharge
                        )
                        print(f"  {hardpoint.get('Name')} Max_Recharge: {max_recharge} -> {new_max_recharge:.3f}")
        
        # Damage Increase: Schüsse pro Salve erhöhen (Fire_Pulse_Count)
        if 'damage_increase' in hardpoint_config:
            damage_increase = hardpoint_config['damage_increase']
            if isinstance(damage_increase, str) and damage_increase.endswith('%'):
                percent_value = float(damage_increase.rstrip('%'))
                
                for hardpoint in hardpoint_elements:
                    pulse_count = self.xml_processor.get_original_value(
                        hardpoint, 'Fire_Pulse_Count'
                    )
                    
                    if pulse_count is not None:
                        # Pulse Count um Prozentsatz erhöhen (mindestens +1)
                        new_pulse_count = max(pulse_count + 1, int(pulse_count * (1 + percent_value / 100)))
                        self.xml_processor.set_value(
                            hardpoint, 'Fire_Pulse_Count', new_pulse_count
                        )
                        print(f"  {hardpoint.get('Name')} Pulse_Count: {pulse_count} -> {new_pulse_count}")
                    
# Optional: Pulse Delay wird nur über burst_delay_adjustment kontrolliert
        
        # Burst Delay Adjustment: Kontrolle der Verzögerung zwischen Schüssen in einer Salve
        if 'burst_delay_adjustment' in hardpoint_config:
            burst_delay_adjustment = hardpoint_config['burst_delay_adjustment']
            if isinstance(burst_delay_adjustment, str) and burst_delay_adjustment.endswith('%'):
                percent_value = float(burst_delay_adjustment.rstrip('%'))
                
                for hardpoint in hardpoint_elements:
                    pulse_delay = self.xml_processor.get_original_value(
                        hardpoint, 'Fire_Pulse_Delay_Seconds'
                    )
                    
                    if pulse_delay is not None:
                        if percent_value >= 0:
                            # Positive Werte erhöhen die Verzögerung
                            new_pulse_delay = pulse_delay * (1 + percent_value / 100)
                        else:
                            # Negative Werte reduzieren die Verzögerung
                            new_pulse_delay = pulse_delay * (1 + percent_value / 100)
                            new_pulse_delay = max(0.05, new_pulse_delay)  # Minimum 0.05 Sekunden
                        
                        self.xml_processor.set_value(
                            hardpoint, 'Fire_Pulse_Delay_Seconds', new_pulse_delay
                        )
                        print(f"  {hardpoint.get('Name')} Pulse_Delay (Burst): {pulse_delay} -> {new_pulse_delay:.3f}")
        
        # Speichern
        self.xml_processor.save_xml(tree, hardpoint_file)

    def apply_unit_changes_fallback(self, unit_config: Dict[str, Any]):
        """Wendet 'template_changes' ersatzweise direkt auf Campaign-/Skirmish-Units an,
        wenn kein Template angegeben ist (z.B. bei Praetor/Procurator)."""
        if 'template_changes' not in unit_config:
            return

        changes = unit_config['template_changes']

        # Dateien bestimmen
        campaign_file = str(self.xml_base_dir / "Units/Republic_Space_Units.xml")
        skirmish_file = str(self.xml_base_dir / "Units/Skirmish/SkirmishUnits_Republic.xml")

        # Ziel-Units ermitteln
        campaign_unit_name = unit_config.get('campaign_unit')
        skirmish_unit_name = unit_config.get('base_unit')

        # Auf Campaign anwenden
        if campaign_unit_name:
            try:
                tree = self.xml_processor.load_xml(campaign_file)
                unit_element = self.xml_processor.find_unit_element(tree, campaign_unit_name)
                if unit_element is not None:
                    updated_values: Dict[str, Any] = {}
                    for property_name, change_value in changes.items():
                        original_value = self.xml_processor.get_original_value(unit_element, property_name)
                        if original_value is None and isinstance(change_value, str) and change_value.endswith('%'):
                            print(f"  Warnung: Originalwert nicht gefunden für {property_name} (Campaign), Prozentänderung übersprungen")
                            continue
                        if isinstance(change_value, str) and change_value.endswith('%') and original_value is not None:
                            new_value = self.calculate_percentage_value(original_value, change_value)
                        else:
                            new_value = change_value
                        # Schildwerte immer auf ganze Zahlen runden
                        if property_name in ("shield_points", "shield_refresh_rate"):
                            try:
                                new_value = int(round(float(new_value)))
                            except Exception:
                                pass
                        self.xml_processor.set_value(unit_element, property_name, new_value)
                        print(f"  (Campaign) {campaign_unit_name} {property_name}: {original_value} -> {new_value}")
                        updated_values[property_name] = new_value
                    self.xml_processor.save_xml(tree, campaign_file)

                    # Tooltips/Textdateien aktualisieren, falls relevante Werte angepasst wurden
                    if any(k in updated_values for k in ("shield_points", "shield_refresh_rate", "tactical_health")):
                        try:
                            self.update_tooltips_for_unit(unit_config, updated_values)
                        except Exception as e:
                            print(f"  Warnung: Konnte Tooltips nicht aktualisieren: {e}")
                else:
                    print(f"  Campaign-Unit nicht gefunden: {campaign_unit_name}")
            except Exception as e:
                print(f"  Warnung: Konnte Änderungen nicht auf Campaign-Unit anwenden: {e}")

        # WICHTIG: Keine direkten Änderungen auf Skirmish-Unit setzen, da Vererbung additiv ist
        # und Skirmish-Units i.d.R. von Campaign-Units erben. Skirmish übernimmt Werte aus Campaign.
    
    def apply_changes(self):
        """Wendet alle Änderungen aus der Konfiguration an"""
        game_mode = self.config.get('game_mode', 'skirmish')
        print(f"Starte SWMA im {game_mode.upper()}-Modus")
        print(f"XML-Basis-Verzeichnis: {self.xml_base_dir}")
        print("=" * 50)
        
        # Automatische Backup-Wiederherstellung vor jeder Ausführung
        if self.backup_manager:
            print("AUTOMATISCHE BACKUP-WIEDERHERSTELLUNG")
            print("=" * 50)
            
            # Prüfe ob Backups existieren, erstelle sie falls nötig
            if not self.backup_manager.create_initial_backups():
                print("Konnte keine initialen Backups erstellen")
                return
            
            # Stelle alle Dateien von Backups wieder her
            if not self.backup_manager.restore_from_backups():
                print("Konnte nicht alle Dateien wiederherstellen")
            
            print("=" * 50)
            print("WENDE NEUE ÄNDERUNGEN AN")
            print("=" * 50)
        else:
            print("Backup-Manager deaktiviert - keine automatische Wiederherstellung")
            print("=" * 50)
        
        for unit_name, unit_config in self.config.get('units', {}).items():
            print(f"\nVerarbeite Einheit: {unit_name}")
            print("-" * 30)
            
            # Ziel-Dateien ermitteln
            target_files = self.get_target_files(unit_name, game_mode)
            
            # Template-Änderungen
            if 'template_changes' in unit_config:
                self.apply_template_changes(unit_config, target_files['template'])
            
            # Squadron-Änderungen (mit intelligenter Datei-Auswahl)
            if 'squadrons' in unit_config:
                self.apply_squadron_changes(unit_config, target_files['squadrons'])
            
            # Hardpoint-Änderungen
            if 'hardpoints' in unit_config:
                self.apply_hardpoint_changes(unit_config, target_files['hardpoints'], unit_name)
            
            # Kaufpreis-Änderungen (nur für Skirmish)
            if game_mode == 'skirmish' and 'cost_changes' in unit_config:
                self.apply_cost_changes(unit_config, target_files['squadrons'])
        
        # KDY Markt-Verarbeitung
        if 'kdy_market' in self.config:
            self.process_kdy_market()
        
        print("\n" + "=" * 50)
        print("Alle Änderungen erfolgreich angewendet!")

        # Falls Textdateien geändert wurden, automatisch DATs neu bauen
        if self.text_changes_applied:
            self.rebuild_text_dat()

    def reset_template_changes(self, unit_config: Dict[str, Any], template_file: str):
        """Setzt alle Template-Änderungen auf Originalwerte zurück"""
        print(f"Setze Template-Änderungen zurück: {template_file}")
        
        # XML laden
        tree = self.xml_processor.load_xml(template_file)
        template_name = unit_config.get('template')
        
        if not template_name:
            print(f"Kein Template für Einheit angegeben")
            return
        
        template_element = self.xml_processor.find_template_element(tree, template_name)
        if not template_element:
            print(f"Template nicht gefunden: {template_name}")
            return
        
        # Liste aller möglichen Template-Eigenschaften
        template_properties = [
            'shield_points', 'shield_refresh_rate', 'energy_capacity', 'energy_refresh_rate',
            'tactical_health', 'armor_type', 'max_speed', 'max_thrust', 'max_rate_of_turn',
            'override_acceleration', 'override_deceleration', 'ai_combat_power', 'damage',
            'maintenance_cost', 'build_cost_credits', 'build_time_seconds', 'squadron_capacity',
            'tech_level', 'required_star_base_level'
        ]
        
        # Backup-Datei finden und laden
        backup_file = self.find_latest_backup(template_file)
        if not backup_file:
            print(f"Kein Backup gefunden für: {template_file}")
            return
        
        backup_tree = self.xml_processor.load_xml(backup_file)
        backup_template = self.xml_processor.find_template_element(backup_tree, template_name)
        
        if not backup_template:
            print(f"Template nicht im Backup gefunden: {template_name}")
            return
        
        # Alle Eigenschaften zurücksetzen
        reset_count = 0
        for property_name in template_properties:
            original_value = self.xml_processor.get_original_value(backup_template, property_name)
            current_value = self.xml_processor.get_original_value(template_element, property_name)
            
            if original_value is not None and current_value is not None:
                if abs(original_value - current_value) > 0.001:  # Nur wenn sich Werte unterscheiden
                    self.xml_processor.set_value(template_element, property_name, original_value)
                    print(f"  {property_name}: {current_value} -> {original_value}")
                    reset_count += 1
        
        if reset_count == 0:
            print("  Keine Werte zum Zurücksetzen gefunden")
        else:
            print(f"  {reset_count} Werte zurückgesetzt")
        
        # Speichern
        self.xml_processor.save_xml(tree, template_file)
    
    def reset_hardpoint_changes(self, unit_config: Dict[str, Any], hardpoint_file: str, unit_name: str):
        """Setzt alle Hardpoint-Änderungen auf Originalwerte zurück"""
        print(f"Setze Hardpoint-Änderungen zurück: {hardpoint_file}")
        
        # XML laden
        tree = self.xml_processor.load_xml(hardpoint_file)
        
        # Den ersten Teil des Unit-Namens für die Hardpoint-Suche verwenden
        ship_type = unit_name.split('_')[0]  # "Acclamator" aus "Acclamator_I_Carrier"
        
        hardpoint_elements = self.xml_processor.find_hardpoint_elements(tree, ship_type)
        if not hardpoint_elements:
            print(f"Keine Hardpoints gefunden für: {ship_type}")
            return
        
        # Backup-Datei finden und laden
        backup_file = self.find_latest_backup(hardpoint_file)
        if not backup_file:
            print(f"Kein Backup gefunden für: {hardpoint_file}")
            return
        
        backup_tree = self.xml_processor.load_xml(backup_file)
        
        # Hardpoint-Eigenschaften zurücksetzen
        reset_count = 0
        for hardpoint in hardpoint_elements:
            hardpoint_name = hardpoint.get('Name')
            backup_hardpoint = self.find_hardpoint_by_name(backup_tree, hardpoint_name)
            
            if backup_hardpoint:
                # Feuerrate-Eigenschaften zurücksetzen
                fire_properties = ['Fire_Min_Recharge_Seconds', 'Fire_Max_Recharge_Seconds']
                
                for prop in fire_properties:
                    original_value = self.xml_processor.get_original_value(backup_hardpoint, prop)
                    current_value = self.xml_processor.get_original_value(hardpoint, prop)
                    
                    if original_value is not None and current_value is not None:
                        if abs(original_value - current_value) > 0.001:  # Nur wenn sich Werte unterscheiden
                                                    self.xml_processor.set_value(hardpoint, prop, original_value)
                        print(f"  {hardpoint_name} {prop}: {current_value} -> {original_value}")
                        reset_count += 1
        
        if reset_count == 0:
            print("  Keine Hardpoint-Werte zum Zurücksetzen gefunden")
        else:
            print(f"  {reset_count} Hardpoint-Werte zurückgesetzt")
        
        # Speichern
        self.xml_processor.save_xml(tree, hardpoint_file)
    
    def reset_squadron_changes(self, unit_config: Dict[str, Any], squadron_file: str):
        """Setzt alle Squadron-Änderungen auf Originalwerte zurück"""
        print(f"Setze Squadron-Änderungen zurück: {squadron_file}")
        
        # XML laden
        tree = self.xml_processor.load_xml(squadron_file)
        unit_name = unit_config.get('base_unit') or unit_config.get('campaign_unit') or list(unit_config.keys())[0]
        
        # Für Campaign-Datei verwende campaign_unit Namen
        if 'Republic_Space_Units.xml' in squadron_file:
            unit_name = unit_config.get('campaign_unit', unit_name)
        
        unit_element = self.xml_processor.find_unit_element(tree, unit_name)
        if not unit_element:
            print(f"Einheit nicht gefunden: {unit_name}")
            return
        
        # Backup-Datei finden und laden
        backup_file = self.find_latest_backup(squadron_file)
        if not backup_file:
            print(f"Kein Backup gefunden für: {squadron_file}")
            return
        
        backup_tree = self.xml_processor.load_xml(backup_file)
        backup_unit = self.xml_processor.find_unit_element(backup_tree, unit_name)
        
        if not backup_unit:
            print(f"Einheit nicht im Backup gefunden: {unit_name}")
            return
        
        # Squadron-Tags zurücksetzen
        squadron_tags = [
            'Starting_Spawned_Units_Tech_0', 'Starting_Spawned_Units_Tech_1',
            'Starting_Spawned_Units_Tech_2', 'Starting_Spawned_Units_Tech_3',
            'Starting_Spawned_Units_Tech_4', 'Starting_Spawned_Units_Tech_5',
            'Reserve_Spawned_Units_Tech_0', 'Reserve_Spawned_Units_Tech_1',
            'Reserve_Spawned_Units_Tech_2', 'Reserve_Spawned_Units_Tech_3',
            'Reserve_Spawned_Units_Tech_4', 'Reserve_Spawned_Units_Tech_5',
            'Spawned_Squadron_Delay_Seconds'
        ]
        
        reset_count = 0
        for tag_name in squadron_tags:
            backup_value = self.xml_processor.get_original_value(backup_unit, tag_name)
            current_value = self.xml_processor.get_original_value(unit_element, tag_name)
            
            if backup_value is not None:
                if current_value is None or abs(backup_value - current_value) > 0.001:
                    self.xml_processor.set_value(unit_element, tag_name, backup_value)
                    print(f"  {tag_name}: {current_value} -> {backup_value}")
                    reset_count += 1
        
        # Squadron-Tags entfernen, die im Original nicht existierten
        for tag_name in squadron_tags:
            if self.xml_processor.get_original_value(backup_unit, tag_name) is None:
                for tag in unit_element.findall(tag_name):
                    unit_element.remove(tag)
                    print(f"  {tag_name}: entfernt")
                    reset_count += 1
        
        if reset_count == 0:
            print("  Keine Squadron-Werte zum Zurücksetzen gefunden")
        else:
            print(f"  {reset_count} Squadron-Werte zurückgesetzt")
        
        # Speichern
        self.xml_processor.save_xml(tree, squadron_file)
    
    def reset_cost_changes(self, unit_config: Dict[str, Any], skirmish_file: str):
        """Setzt alle Kaufpreis-Änderungen auf Originalwerte zurück"""
        print(f"Setze Kaufpreis-Änderungen zurück: {skirmish_file}")
        
        # XML laden
        tree = self.xml_processor.load_xml(skirmish_file)
        base_unit = unit_config.get('base_unit')
        
        if not base_unit:
            print(f"Kein base_unit für Einheit angegeben")
            return
        
        unit_element = self.xml_processor.find_unit_element(tree, base_unit)
        if not unit_element:
            print(f"Skirmish-Unit nicht gefunden: {base_unit}")
            return
        
        # Backup-Datei finden und laden
        backup_file = self.find_latest_backup(skirmish_file)
        if not backup_file:
            print(f"Kein Backup gefunden für: {skirmish_file}")
            return
        
        backup_tree = self.xml_processor.load_xml(backup_file)
        backup_unit = self.xml_processor.find_unit_element(backup_tree, base_unit)
        
        if not backup_unit:
            print(f"Einheit nicht im Backup gefunden: {base_unit}")
            return
        
        # Kaufpreis-Tags zurücksetzen
        cost_tags = [
            'Tactical_Build_Cost_Multiplayer',
            'Tactical_Build_Cost_Campaign',
            'Build_Cost_Credits',
            'Maintenance_Cost'
        ]
        
        reset_count = 0
        for tag_name in cost_tags:
            backup_value = self.xml_processor.get_original_value(backup_unit, tag_name)
            current_value = self.xml_processor.get_original_value(unit_element, tag_name)
            
            if backup_value is not None:
                if current_value is None or abs(backup_value - current_value) > 0.001:
                    self.xml_processor.set_value(unit_element, tag_name, backup_value)
                    print(f"  {tag_name}: {current_value} -> {backup_value}")
                    reset_count += 1
        
        if reset_count == 0:
            print("  Keine Kaufpreis-Werte zum Zurücksetzen gefunden")
        else:
            print(f"  {reset_count} Kaufpreis-Werte zurückgesetzt")
        
        # Speichern
        self.xml_processor.save_xml(tree, skirmish_file)
    
    def find_latest_backup(self, original_file: str) -> Optional[str]:
        """Findet die älteste Backup-Datei für eine Original-Datei (das Original)"""
        if not self.backup_manager:
            return None
        
        backup_dir = self.backup_manager.backup_dir
        original_name = Path(original_file).stem
        
        # Alle Backup-Dateien für diese Original-Datei finden
        backup_files = list(backup_dir.glob(f"{original_name}_original.xml"))
        
        if not backup_files:
            return None
        
        # Älteste Datei zurückgeben (das Original)
        return str(min(backup_files, key=lambda x: x.stat().st_mtime))
    
    def find_hardpoint_by_name(self, tree: ET.ElementTree, hardpoint_name: str) -> Optional[ET.Element]:
        """Findet ein Hardpoint-Element anhand des Namens"""
        root = tree.getroot()
        
        for element in root.findall(".//HardPoint"):
            if element.get('Name') == hardpoint_name:
                return element
        
        return None

    # -------- Tooltip/Text-Update-Funktionen --------
    def get_encyclopedia_text_keys(self, unit_config: Dict[str, Any]) -> List[str]:
        """Extrahiert alle TEXT_* Keys aus <Encyclopedia_Text> für die Einheit aus Campaign und Skirmish."""
        unit_name = unit_config.get('campaign_unit') or unit_config.get('base_unit')
        if not unit_name:
            return []
        files_to_check = [
            str(self.xml_base_dir / "Units/Republic_Space_Units.xml"),
            str(self.xml_base_dir / "Units/Skirmish/SkirmishUnits_Republic.xml"),
        ]
        seen = set()
        ordered_keys: List[str] = []
        for file_path in files_to_check:
            try:
                tree = self.xml_processor.load_xml(file_path)
                unit_element = self.xml_processor.find_unit_element(tree, unit_name)
                if unit_element is None:
                    continue
                enc_el = unit_element.find('Encyclopedia_Text')
                if enc_el is None:
                    continue
                text_blob = ''.join(list(enc_el.itertext()))
                tokens = re.split(r"\s+|,", text_blob.strip())
                keys = [t for t in tokens if t and t.startswith('TEXT_')]
                for k in keys:
                    if k not in seen:
                        seen.add(k)
                        ordered_keys.append(k)
            except Exception:
                continue
        return ordered_keys

    def find_text_file_containing_key(self, key: str) -> Optional[Path]:
        """Durchsucht das Text-Verzeichnis nach einer Zeile, die mit 'KEY,' beginnt."""
        if not self.text_base_dir.exists():
            return None
        for txt_path in sorted(self.text_base_dir.glob('*.txt')):
            try:
                with open(txt_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith(f"{key},"):
                            return txt_path
            except Exception:
                continue
        return None

    def update_text_line_in_file(self, txt_path: Path, key: str, updated_values: Dict[str, Any]) -> bool:
        """Aktualisiert eine einzelne Zeile in der angegebenen Textdatei. Gibt True zurück, wenn eine Änderung erfolgte."""
        try:
            with open(txt_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            print(f"  Warnung: Konnte Datei nicht lesen: {txt_path} ({e})")
            return False

        changed = False
        for i, line in enumerate(lines):
            if not line.startswith(f"{key},"):
                continue
            prefix, value = line.split(',', 1)
            new_value = value.rstrip('\n')

            # Muster 1: Separater Schild-Tooltip wie "Shields: 450 / [9/R] (Corvette)"
            if re.search(r"Shields?:", new_value):
                # Schildpunkte ersetzen
                if 'shield_points' in updated_values:
                    def repl_points(m: re.Match) -> str:
                        return f"{m.group(1)}{int(round(float(updated_values['shield_points'])))}"
                    new_value_tmp = re.sub(r"(Shields?:\s*)(\d+)", repl_points, new_value)
                    new_value = new_value_tmp

                # Refresh-Rate ersetzen, wenn vorhanden als [...] mit /R
                if 'shield_refresh_rate' in updated_values:
                    def repl_rate(m: re.Match) -> str:
                        # Erhalte eventuelles Dezimalformat
                        rate = float(updated_values['shield_refresh_rate'])
                        return f"[{rate}/R]" if '.' in m.group(1) else f"[{int(round(rate))}/R]"
                    new_value = re.sub(r"\[(\d+(?:\.\d+)?)\/R\]", repl_rate, new_value)

            # Muster 2: Statblock-Basis: "Health: A | Shields: B" oder "Health: A | Unshielded"
            if re.search(r"Health:\s*\d+", new_value) or "Unshielded" in new_value:
                # Health aktualisieren
                if 'tactical_health' in updated_values:
                    def repl_health(m: re.Match) -> str:
                        return f"{m.group(1)}{int(round(float(updated_values['tactical_health'])))}"
                    new_value = re.sub(r"(Health:\s*)(\d+)", repl_health, new_value)

                # Shields aktualisieren
                if 'shield_points' in updated_values:
                    sp = int(round(float(updated_values['shield_points'])))
                    if sp <= 0:
                        # Zu "Unshielded" migrieren
                        if "Shields:" in new_value or "Shield:" in new_value:
                            new_value = re.sub(r"Shields?:\s*\d+", "Unshielded", new_value)
                        else:
                            new_value = new_value.replace("Unshielded", "Unshielded")
                    else:
                        if "Unshielded" in new_value:
                            new_value = new_value.replace("Unshielded", f"Shields: {sp}")
                        else:
                            def repl_shields(m: re.Match) -> str:
                                return f"{m.group(1)}{sp}"
                            new_value = re.sub(r"(Shields?:\s*)(\d+)", repl_shields, new_value)
            
            # Muster 3: Separater HULL-Tooltip: "Hull: A (Class)"
            if 'tactical_health' in updated_values and re.search(r"Hull:\s*\d+", new_value):
                def repl_hull(m: re.Match) -> str:
                    return f"{m.group(1)}{int(round(float(updated_values['tactical_health'])))}"
                new_value = re.sub(r"(Hull:\s*)(\d+)", repl_hull, new_value)

            if new_value != value.rstrip('\n'):
                # Backup anlegen, falls noch nicht vorhanden
                try:
                    if self.backup_manager:
                        self.backup_manager.create_backup(str(txt_path))
                except Exception:
                    pass
                lines[i] = f"{prefix},{new_value}\n"
                changed = True
                print(f"  Tooltip aktualisiert: {key} -> {new_value}")
                break

        if changed:
            try:
                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
            except Exception as e:
                print(f"  Warnung: Konnte Datei nicht schreiben: {txt_path} ({e})")
                return False
            # Globales Flag setzen
            self.text_changes_applied = True
        return changed

    def update_tooltips_for_unit(self, unit_config: Dict[str, Any], updated_values: Dict[str, Any]):
        """Aktualisiert Tooltip-/Statblock-Texte auf Basis der geänderten Werte."""
        keys = self.get_encyclopedia_text_keys(unit_config)
        if not keys:
            return

        # Relevante Keys filtern
        candidate_keys: List[str] = []
        for k in keys:
            if "_SHIELD" in k:
                candidate_keys.append(k)
            elif "_HULL" in k:
                candidate_keys.append(k)
            elif re.match(r"TEXT_STATBLOCK_.*_BASE$", k):
                candidate_keys.append(k)

        # Nichts zu tun
        if not candidate_keys:
            return

        for key in candidate_keys:
            txt_path = self.find_text_file_containing_key(key)
            if not txt_path:
                print(f"  Hinweis: Kein Textfile für {key} gefunden")
                continue
            self.update_text_line_in_file(txt_path, key, updated_values)

    def rebuild_text_dat(self):
        """Führt den Text-Build aus (alphabetize-and-build.bat), falls vorhanden."""
        try:
            if not self.text_base_dir.exists():
                print("Hinweis: Text-Verzeichnis nicht gefunden, überspringe DAT-Build")
                return
            bat_path = self.text_base_dir / "alphabetize-and-build.bat"
            if not bat_path.exists():
                print("Hinweis: Build-Skript 'alphabetize-and-build.bat' nicht gefunden, überspringe DAT-Build")
                return
            print("Starte automatischen DAT-Build der Textdateien...")
            subprocess.run(["cmd", "/c", str(bat_path.name)], cwd=self.text_base_dir, check=True)
            print("DAT-Build abgeschlossen.")
        except subprocess.CalledProcessError as e:
            print(f"Warnung: DAT-Build fehlgeschlagen (Exit {e.returncode})")
        except Exception as e:
            print(f"Warnung: Konnte DAT-Build nicht ausführen: {e}")

    def reset_changes(self, unit_name: str = None):
        """Setzt alle Änderungen für eine Einheit oder alle Einheiten zurück"""
        game_mode = self.config.get('game_mode', 'skirmish')
        print(f"Starte SWMA Reset im {game_mode.upper()}-Modus")
        print(f"XML-Basis-Verzeichnis: {self.xml_base_dir}")
        print("=" * 50)
        
        units_to_reset = {}
        if unit_name:
            if unit_name in self.config.get('units', {}):
                units_to_reset[unit_name] = self.config['units'][unit_name]
            else:
                print(f"Einheit nicht gefunden: {unit_name}")
                return
        else:
            units_to_reset = self.config.get('units', {})
        
        for unit_name, unit_config in units_to_reset.items():
            print(f"\nSetze Einheit zurück: {unit_name}")
            print("-" * 30)
            
            # Ziel-Dateien ermitteln
            target_files = self.get_target_files(unit_name, game_mode)
            
            # Template-Änderungen zurücksetzen
            self.reset_template_changes(unit_config, target_files['template'])
            
            # Squadron-Änderungen zurücksetzen (sowohl Skirmish als auch Campaign)
            skirmish_file = str(self.xml_base_dir / "Units/Skirmish/SkirmishUnits_Republic.xml")
            self.reset_squadron_changes(unit_config, skirmish_file)
            
            campaign_file = str(self.xml_base_dir / "Units/Republic_Space_Units.xml")
            campaign_config = unit_config.copy()
            if 'campaign_unit' in unit_config:
                campaign_config['base_unit'] = unit_config['campaign_unit']
            self.reset_squadron_changes(campaign_config, campaign_file)
            
            # Hardpoint-Änderungen zurücksetzen
            self.reset_hardpoint_changes(unit_config, target_files['hardpoints'], unit_name)
            
            # Kaufpreis-Änderungen zurücksetzen (nur für Skirmish)
            if game_mode == 'skirmish':
                skirmish_file = str(self.xml_base_dir / "Units/Skirmish/SkirmishUnits_Republic.xml")
                self.reset_cost_changes(unit_config, skirmish_file)
        
        print("\n" + "=" * 50)
        print("Alle Änderungen erfolgreich zurückgesetzt!")

    def process_kdy_market(self):
        """Verarbeitet KDY Markt-Konfigurationen"""
        if 'kdy_market' not in self.config:
            return
            
        kdy_config = self.config['kdy_market']
        
        if not kdy_config.get('enabled', True):
            print("KDY Markt ist deaktiviert.")
            return
            
        print("🛒 Verarbeite KDY Markt-Konfiguration...")
        
        # ShipMarketOptions.lua bearbeiten
        self.process_ship_market_options(kdy_config)
        
        # ShipMarketAdjustmentsLibrary.lua bearbeiten
        self.process_ship_market_adjustments(kdy_config)
        
        print("✅ KDY Markt-Konfiguration abgeschlossen.")

    def process_ship_market_options(self, kdy_config):
        """Bearbeitet ShipMarketOptions.lua"""
        if not self.ship_market_options.exists():
            print(f"⚠️  Datei nicht gefunden: {self.ship_market_options}")
            return
            
        with open(self.ship_market_options, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Aktuelle Werte extrahieren (als Backup)
        current_ships = self.extract_current_ship_values(content)
        
        # Neue Werte anwenden
        if 'ships' in kdy_config:
            for ship_name, ship_config in kdy_config['ships'].items():
                content = self.update_ship_market_entry(content, ship_name, ship_config)
                
        # Datei speichern
        with open(self.ship_market_options, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ {self.ship_market_options.name} aktualisiert")

    def process_ship_market_adjustments(self, kdy_config):
        """Bearbeitet ShipMarketAdjustmentsLibrary.lua"""
        if not self.ship_market_adjustments.exists():
            print(f"⚠️  Datei nicht gefunden: {self.ship_market_adjustments}")
            return
            
        with open(self.ship_market_adjustments, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Neue Events hinzufügen
        if 'events' in kdy_config:
            for event_name, event_config in kdy_config['events'].items():
                content = self.add_or_update_event(content, event_name, event_config)
                
        # Datei speichern
        with open(self.ship_market_adjustments, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ {self.ship_market_adjustments.name} aktualisiert")

    def extract_current_ship_values(self, content):
        """Extrahiert aktuelle Schiffswerte aus der Lua-Datei"""
        ships = {}
        
        # Suche nach Schiff-Einträgen
        ship_pattern = r'\["([^"]+)"\]\s*=\s*\{[^}]*chance\s*=\s*(\d+)[^}]*locked\s*=\s*(true|false)'
        matches = re.findall(ship_pattern, content, re.DOTALL)
        
        for ship_name, chance, locked in matches:
            ships[ship_name] = {
                'chance': int(chance),
                'locked': locked == 'true'
            }
            
        return ships

    def update_ship_market_entry(self, content, ship_name, ship_config):
        """Aktualisiert einen Schiff-Eintrag in der Lua-Datei"""
        
        # Erstelle den neuen Eintrag
        new_entry = f'''				["{ship_name}"] = {{
					locked = {str(ship_config.get('locked', False)).lower()},
					gc_locked = false,
					amount = 0,
					chance = {ship_config.get('chance', 0)},
					perception_modifier = nil,
					association = nil,
					readable_name = "{ship_config.get('readable_name', ship_name)}",
					text_requirement = "{ship_config.get('requirement_text', '')}",
					order = {ship_config.get('order', 1)},
				}},'''
        
        # Suche nach existierendem Eintrag und ersetze ihn
        pattern = rf'\["{re.escape(ship_name)}"\]\s*=\s*\{{[^}}]+\}},'
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, new_entry, content, flags=re.DOTALL)
        else:
            # Füge neuen Eintrag hinzu (vor dem schließenden })
            content = re.sub(r'(\s*),\s*\}', f',\n{new_entry}\n			}}', content)
            
        return content

    def add_or_update_event(self, content, event_name, event_config):
        """Fügt ein neues Event hinzu oder aktualisiert ein existierendes"""
        
        # Erstelle den neuen Event-Eintrag
        event_entry = f'''		["{event_name}"] = {{'''
        
        if 'adjustments' in event_config:
            event_entry += f'''
			adjustment_lists = {{'''
            for ship, adjustment in event_config['adjustments'].items():
                event_entry += f'''
				{{"EMPIRE", "KDY_MARKET", "{ship}", {adjustment}}},'''
            event_entry += '''
			},'''
            
        if 'locks' in event_config:
            event_entry += f'''
			lock_lists = {{'''
            for ship, locked in event_config['locks'].items():
                event_entry += f'''
				{{"EMPIRE", "KDY_MARKET", "{ship}", {str(locked).lower()}}},'''
            event_entry += '''
			},'''
            
        if 'unlocks' in event_config:
            if 'lock_lists' not in event_config:
                event_entry += f'''
			lock_lists = {{'''
            for ship, unlocked in event_config['unlocks'].items():
                event_entry += f'''
				{{"EMPIRE", "KDY_MARKET", "{ship}", {str(not unlocked).lower()}}},'''
            event_entry += '''
			},'''
            
        if 'requirements' in event_config:
            event_entry += f'''
			requirement_lists = {{'''
            for ship, requirement in event_config['requirements'].items():
                event_entry += f'''
				{{"EMPIRE", "KDY_MARKET", "{ship}", "{requirement}"}},'''
            event_entry += '''
			},'''
            
        event_entry += '''
		},'''
        
        # Suche nach existierendem Event und ersetze es
        pattern = rf'\["{re.escape(event_name)}"\]\s*=\s*\{{[^}}]+\}},'
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, event_entry, content, flags=re.DOTALL)
        else:
            # Füge neues Event hinzu (vor dem schließenden })
            content = re.sub(r'(\s*)\}', f'{event_entry}\n}}', content)
            
        return content


def main():
    """Hauptfunktion"""
    parser = argparse.ArgumentParser(description='Star Wars Modding Automation Tool')
    parser.add_argument('--config', '-c', required=True, help='Konfigurationsdatei (YAML)')
    parser.add_argument('--no-backup', action='store_true', help='Keine Backups erstellen')
    parser.add_argument('--preview', action='store_true', help='Nur Vorschau, keine Änderungen')
    parser.add_argument('--reset', action='store_true', help='Setzt alle Änderungen auf Originalwerte zurück')
    parser.add_argument('--reset-unit', help='Setzt Änderungen für eine spezifische Einheit zurück')
    
    args = parser.parse_args()
    
    try:
        # Tool initialisieren
        tool = SWModdingTool(args.config, backup_originals=not args.no_backup)
        
        if args.preview:
            print("VORSCHAU-MODUS - Keine Änderungen werden vorgenommen")
            print("Konfiguration geladen:")
            print(yaml.dump(tool.config, default_flow_style=False, indent=2))
        elif args.reset:
            print("RESET-MODUS - Setze alle Änderungen zurück")
            tool.reset_changes()
        elif args.reset_unit:
            print(f"RESET-MODUS - Setze Änderungen für Einheit zurück: {args.reset_unit}")
            tool.reset_changes(args.reset_unit)
        else:
            # Änderungen anwenden (automatische Backup-Wiederherstellung ist in apply_changes integriert)
            tool.apply_changes()
    
    except Exception as e:
        print(f"Fehler: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 