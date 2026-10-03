import tempfile
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET

from swma import SWModdingTool, XMLProcessor


class SkirmishFallbackTests(unittest.TestCase):
    def test_apply_unit_changes_fallback_updates_skirmish_unit_in_skirmish_mode(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            (tmp / 'Units').mkdir()
            (tmp / 'Units' / 'Skirmish').mkdir()

            campaign_file = tmp / 'Units' / 'Republic_Space_Units.xml'
            skirmish_file = tmp / 'Units' / 'Skirmish' / 'SkirmishUnits_Republic.xml'

            ET.ElementTree(ET.fromstring('''
            <SpaceUnits>
              <SpaceUnit Name="Arquitens">
                <Shield_Points>100</Shield_Points>
                <Shield_Refresh_Rate>10</Shield_Refresh_Rate>
                <Energy_Refresh_Rate>5</Energy_Refresh_Rate>
              </SpaceUnit>
            </SpaceUnits>
            ''')).write(campaign_file, encoding='utf-8', xml_declaration=True)

            ET.ElementTree(ET.fromstring('''
            <SpaceUnits>
              <SkirmishSpaceUnit Name="Skirmish_Arquitens">
                <Shield_Points>100</Shield_Points>
                <Shield_Refresh_Rate>10</Shield_Refresh_Rate>
                <Energy_Refresh_Rate>5</Energy_Refresh_Rate>
              </SkirmishSpaceUnit>
            </SpaceUnits>
            ''')).write(skirmish_file, encoding='utf-8', xml_declaration=True)

            tool = SWModdingTool.__new__(SWModdingTool)
            tool.xml_base_dir = tmp
            tool.xml_processor = XMLProcessor()
            tool.config = {'game_mode': 'skirmish'}
            tool.backup_manager = None
            tool.text_changes_applied = False

            unit_config = {
                'base_unit': 'Skirmish_Arquitens',
                'campaign_unit': 'Arquitens',
                'template_changes': {
                    'shield_refresh_rate': '+30%',
                    'shield_points': '+30%',
                    'energy_refresh_rate': '+20%',
                },
                'hardpoints': {
                    'damage_increase': '+60%',
                    'burst_delay_adjustment': '-30%',
                    'fire_rate_increase': '+70%',
                },
            }

            tool.apply_unit_changes_fallback(unit_config)

            tree = ET.parse(str(skirmish_file))
            unit = tool.xml_processor.find_unit_element(tree, 'Skirmish_Arquitens')
            self.assertIsNotNone(unit)
            # Schildwerte werden auf ganze Zahlen gerundet
            self.assertEqual(unit.find('Shield_Points').text, '130')
            self.assertEqual(unit.find('Shield_Refresh_Rate').text, '13')
            self.assertEqual(unit.find('Energy_Refresh_Rate').text, '6.0')


if __name__ == '__main__':
    unittest.main()
