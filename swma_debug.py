#!/usr/bin/env python3
"""
Debug-Version des SWMA Tools
"""

import os
import sys
import yaml
import xml.etree.ElementTree as ET
import shutil
from datetime import datetime
from pathlib import Path
import argparse
from typing import Dict, List, Any, Optional, Tuple

def debug_find_template_element(tree: ET.ElementTree, template_name: str) -> Optional[ET.Element]:
    """Debug-Version der Template-Suche"""
    root = tree.getroot()
    print(f"Suche Template: {template_name}")
    print(f"Root-Tag: {root.tag}")
    
    # Alle SpaceUnit-Elemente finden
    space_units = root.findall(".//SpaceUnit")
    print(f"Gefundene SpaceUnit-Elemente: {len(space_units)}")
    
    for i, element in enumerate(space_units):
        name = element.get('Name')
        print(f"  Element {i}: Name='{name}'")
        if name == template_name:
            print(f"  Template gefunden!")
            return element
    
    print("  Template nicht gefunden!")
    return None

def debug_apply_template_changes(config_file: str):
    """Debug-Version der Template-Änderungen"""
    
    # Konfiguration laden
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    print("Konfiguration geladen:")
    print(yaml.dump(config, default_flow_style=False, indent=2))
    
    # XML-Datei laden
    xml_file = Path("../Units/Templates_Frigates.xml")
    print(f"\nLade XML-Datei: {xml_file}")
    
    tree = ET.parse(xml_file)
    
    # Template suchen
    template_name = "Template_Acclamator_I_Carrier"
    template_element = debug_find_template_element(tree, template_name)
    
    if template_element is None:
        print("Template nicht gefunden!")
        return
    
    # Alle Tags im Template anzeigen
    print(f"\nAlle Tags im Template:")
    for child in template_element:
        print(f"  {child.tag}: '{child.text}'")
    
    # Änderungen anwenden
    unit_config = config['units']['Acclamator_I_Carrier']
    changes = unit_config['template_changes']
    
    print(f"\nWende Änderungen an:")
    print(f"Changes: {changes}")
    print(f"Changes type: {type(changes)}")
    print(f"Changes items: {list(changes.items())}")
    
    # Explizite Schleife
    for property_name, change_value in changes.items():
        print(f"\nVerarbeite: {property_name} = {change_value}")
        print(f"  Property type: {type(property_name)}")
        print(f"  Value type: {type(change_value)}")
        
        # Originalwert finden
        tag = template_element.find(property_name)
        print(f"  Tag gefunden: {tag is not None}")
        
        if tag is not None:
            print(f"  Tag text: '{tag.text}'")
            if tag.text:
                original_value = float(tag.text)
                print(f"  Original: {original_value}")
                
                # Neuen Wert setzen
                if isinstance(change_value, str) and change_value.endswith('%'):
                    # Prozentuale Änderung
                    percent_value = float(change_value.rstrip('%'))
                    new_value = original_value * (1 + percent_value / 100)
                else:
                    # Absoluter Wert
                    new_value = change_value
                
                tag.text = str(new_value)
                print(f"  Neu: {new_value}")
                print(f"  Tag text nach Änderung: '{tag.text}'")
            else:
                print(f"  Tag hat keinen Text")
        else:
            print(f"  Tag nicht gefunden: {property_name}")
    
    # Speichern
    tree.write(xml_file, encoding='utf-8', xml_declaration=True)
    print(f"\nXML-Datei gespeichert: {xml_file}")

if __name__ == "__main__":
    debug_apply_template_changes('shipchanges.yaml') 