#!/usr/bin/env python3
import time
from Arm_Lib import Arm_Device

class DofbotTriSystem:
    def __init__(self):
        self.Arm = Arm_Device()
        time.sleep(0.1)
        
        # Positions de calibration
        self.tri_positions = {'pick_position': {'angles': [90, 53, 33, 36, 270, 135], 'description': 'Position pour prendre le cube (p_Brown)', 'source': 'p_Brown'}, 'corbeille_1': {'angles': [65, 22, 64, 56, 270, 60], 'description': 'Corbeille 1 - Position jaune', 'source': 'p_Yellow'}, 'corbeille_2': {'angles': [117, 19, 66, 56, 270, 60], 'description': 'Corbeille 2 - Position rouge', 'source': 'p_Red'}, 'corbeille_3': {'angles': [136, 66, 20, 29, 270, 60], 'description': 'Corbeille 3 - Position verte', 'source': 'p_Green'}, 'position_sure': {'angles': [90, 80, 50, 50, 270, 60], 'description': 'Position sûre entre les mouvements (p_top)', 'source': 'p_top'}, 'position_home': {'angles': [90, 130, 0, 0, 90, 60], 'description': 'Position home (p_mould)', 'source': 'p_mould'}}
        
        # Initialisation
        self.move_to_home()

    def move_to_home(self):
        """Position home"""
        home = [90, 130, 0, 0, 90, 60]
        self.Arm.Arm_serial_servo_write6_array(home, 1500)
        time.sleep(2)

    def trier_cube(self, corbeille_num):
        """Fonction principale de tri"""
        print(f"? Début tri vers corbeille {corbeille_num}")
        
        # Séquence de prise
        self.Arm.Arm_serial_servo_write6_array([90, 80, 50, 50, 270, 60], 1000)
        time.sleep(1)
        self.Arm.Arm_serial_servo_write6_array([90, 53, 33, 36, 270, 135], 1000) 
        time.sleep(1)
        self.Arm.Arm_serial_servo_write6_array([90, 80, 50, 50, 270, 60], 1000)
        time.sleep(1)
        
        # Séquence de dépôt
        corbeille_key = f"corbeille_{corbeille_num}"
        corbeille_angles = self.tri_positions[corbeille_key]["angles"]
        self.Arm.Arm_serial_servo_write6_array(corbeille_angles, 1000)
        time.sleep(1)
        self.Arm.Arm_serial_servo_write6_array([90, 80, 50, 50, 270, 60], 1000)
        
        print(f"? Cube trié vers corbeille {corbeille_num}")

# Utilisation:
# tri_system = DofbotTriSystem()
# tri_system.trier_cube(1)  # Trier vers corbeille 1
