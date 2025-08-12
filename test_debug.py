#!/usr/bin/env python3
"""
Debug-Skript für SWMA Tool
"""

import xml.etree.ElementTree as ET
import yaml
from pathlib import Path

def test_xml_processing():
    """Testet die XML-Verarbeitung"""
    
    # Konfiguration laden
    with open('shipchanges.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    print("Konfiguration geladen:")
    print(yaml.dump(config, default_flow_style=False, indent=2))
    
    # XML-Datei laden
    xml_file = Path("../Units/Templates_Frigates.xml")
    print(f"\nLade XML-Datei: {xml_file}")
    
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # Template suchen
    template_name = "Template_Acclamator_I_Carrier"
    print(f"\nSuche Template: {template_name}")
    
    template_element = None
    for element in root.findall(".//SpaceUnit"):
        if element.get('Name') == template_name:
            template_element = element
            break
    
    if template_element is None:
        print("Template nicht gefunden!")
        return
    
    print("Template gefunden!")
    
    # Shield_Points suchen
    shield_tag = template_element.find("Shield_Points")
    if shield_tag is not None:
        original_value = float(shield_tag.text)
        print(f"Original Shield_Points: {original_value}")
        
        # Wert ändern
        new_value = 1980
        shield_tag.text = str(new_value)
        print(f"Neuer Shield_Points Wert: {new_value}")
        
        # Speichern
        tree.write(xml_file, encoding='utf-8', xml_declaration=True)
        print(f"XML-Datei gespeichert: {xml_file}")
    else:
        print("Shield_Points Tag nicht gefunden!")

if __name__ == "__main__":
    test_xml_processing() 