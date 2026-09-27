#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 OUTIL DE CALIBRATION DOFBOT - DOFBOT WASTE SORTING COTONOU
Calibration manuelle des positions du bras robotique

Projet: dofbot-waste-sorting
Date: Octobre 2025
"""

import sys
import os
import time
import yaml
import msvcrt  # Pour détection touches Windows

# Ajouter le chemin pour Arm_Lib
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from Arm_Lib import Arm_Device
    ARM_LIB_AVAILABLE = True
except ImportError:
    ARM_LIB_AVAILABLE = False
    print("⚠️  Arm_Lib non disponible - Mode simulation")


class DofbotCalibration:
    """Outil de calibration interactif pour DOFbot"""
    
    def __init__(self, config_path="../config/positions.yaml"):
        """
        Initialise l'outil de calibration
        
        Args:
            config_path: Chemin vers le fichier positions.yaml
        """
        self.config_path = os.path.join(os.path.dirname(__file__), config_path)
        
        # Limites de sécurité des servos (degrés)
        self.SERVO_LIMITS = {
            1: (0, 180),    # Base rotation
            2: (0, 180),    # Shoulder
            3: (0, 180),    # Elbow
            4: (0, 180),    # Wrist pitch
            5: (0, 270),    # Wrist roll
            6: (0, 180)     # Gripper
        }
        
        # Variables de contrôle
        self.current_servo = 1
        self.step_size = 1  # Pas de déplacement en degrés
        self.available_steps = [1, 5, 10]
        self.current_step_index = 0
        
        # Position actuelle (angles des 6 servos)
        self.current_angles = [90, 90, 90, 90, 90, 30]
        
        # Charger les positions depuis YAML
        self.positions = self.load_positions()
        
        # Initialiser le bras si disponible
        self.arm = None
        self.simulation_mode = not ARM_LIB_AVAILABLE
        
        if ARM_LIB_AVAILABLE:
            try:
                self.arm = Arm_Device()
                time.sleep(0.5)
                self.arm.Arm_serial_set_torque(1)
                print("✅ Bras DOFbot connecté!")
                self.simulation_mode = False
            except Exception as e:
                print(f"⚠️  Erreur connexion bras: {e}")
                print("🔄 Passage en mode simulation")
                self.simulation_mode = True
        
        # Aller à la position HOME au démarrage
        if not self.simulation_mode:
            self.goto_home()
    
    def load_positions(self):
        """Charge les positions depuis positions.yaml"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Convertir la structure YAML en format utilisable
            positions = {}
            
            # Position HOME
            if 'home' in data:
                home = data['home']
                positions['HOME'] = [
                    home.get('joint1', 90),
                    home.get('joint2', 90),
                    home.get('joint3', 90),
                    home.get('joint4', 90),
                    home.get('joint5', 90),
                    home.get('gripper', 30)
                ]
            
            # Position OBSERVATION
            if 'observation' in data:
                obs = data['observation']
                positions['OBSERVATION'] = [
                    obs.get('joint1', 90),
                    obs.get('joint2', 100),
                    obs.get('joint3', 80),
                    obs.get('joint4', 90),
                    obs.get('joint5', 90),
                    obs.get('gripper', 30)
                ]
            
            # Positions des bacs
            if 'bins' in data:
                bins = data['bins']
                for bin_name in ['dangereux', 'menagers', 'recyclables']:
                    if bin_name in bins:
                        bin_data = bins[bin_name]
                        positions[bin_name.upper()] = [
                            bin_data.get('joint1', 90),
                            bin_data.get('joint2', 90),
                            bin_data.get('joint3', 90),
                            bin_data.get('joint4', 90),
                            bin_data.get('joint5', 90),
                            bin_data.get('gripper', 30)
                        ]
            
            print(f"✅ Positions chargées depuis: {self.config_path}")
            return positions
            
        except FileNotFoundError:
            print(f"⚠️  Fichier {self.config_path} non trouvé")
            print("📝 Création de positions par défaut...")
            return self.get_default_positions()
        except Exception as e:
            print(f"❌ Erreur chargement positions: {e}")
            return self.get_default_positions()
    
    def get_default_positions(self):
        """Retourne des positions par défaut"""
        return {
            'HOME': [90, 90, 90, 90, 90, 30],
            'OBSERVATION': [90, 100, 80, 90, 90, 30],
            'DANGEREUX': [135, 100, 60, 90, 90, 30],
            'MENAGERS': [90, 100, 60, 90, 90, 30],
            'RECYCLABLES': [45, 100, 60, 90, 90, 30]
        }
    
    def save_positions(self):
        """Sauvegarde les positions dans positions.yaml"""
        try:
            # Construire la structure YAML
            yaml_data = {
                'home': {
                    'joint1': int(self.positions['HOME'][0]),
                    'joint2': int(self.positions['HOME'][1]),
                    'joint3': int(self.positions['HOME'][2]),
                    'joint4': int(self.positions['HOME'][3]),
                    'joint5': int(self.positions['HOME'][4]),
                    'gripper': int(self.positions['HOME'][5]),
                    'speed': 1500,
                    'description': "Position de repos"
                },
                'observation': {
                    'joint1': int(self.positions['OBSERVATION'][0]),
                    'joint2': int(self.positions['OBSERVATION'][1]),
                    'joint3': int(self.positions['OBSERVATION'][2]),
                    'joint4': int(self.positions['OBSERVATION'][3]),
                    'joint5': int(self.positions['OBSERVATION'][4]),
                    'gripper': int(self.positions['OBSERVATION'][5]),
                    'speed': 1500,
                    'description': "Position d'observation caméra"
                },
                'bins': {
                    'dangereux': {
                        'joint1': int(self.positions['DANGEREUX'][0]),
                        'joint2': int(self.positions['DANGEREUX'][1]),
                        'joint3': int(self.positions['DANGEREUX'][2]),
                        'joint4': int(self.positions['DANGEREUX'][3]),
                        'joint5': int(self.positions['DANGEREUX'][4]),
                        'gripper': int(self.positions['DANGEREUX'][5]),
                        'speed': 1500,
                        'description': "Bac déchets dangereux (rouge)",
                        'class': 'dangereux'
                    },
                    'menagers': {
                        'joint1': int(self.positions['MENAGERS'][0]),
                        'joint2': int(self.positions['MENAGERS'][1]),
                        'joint3': int(self.positions['MENAGERS'][2]),
                        'joint4': int(self.positions['MENAGERS'][3]),
                        'joint5': int(self.positions['MENAGERS'][4]),
                        'gripper': int(self.positions['MENAGERS'][5]),
                        'speed': 1500,
                        'description': "Bac déchets ménagers (vert)",
                        'class': 'menagers'
                    },
                    'recyclables': {
                        'joint1': int(self.positions['RECYCLABLES'][0]),
                        'joint2': int(self.positions['RECYCLABLES'][1]),
                        'joint3': int(self.positions['RECYCLABLES'][2]),
                        'joint4': int(self.positions['RECYCLABLES'][3]),
                        'joint5': int(self.positions['RECYCLABLES'][4]),
                        'gripper': int(self.positions['RECYCLABLES'][5]),
                        'speed': 1500,
                        'description': "Bac déchets recyclables (bleu)",
                        'class': 'recyclables'
                    }
                },
                'safety': {
                    'min_angles': [0, 0, 0, 0, 0, 0],
                    'max_angles': [180, 180, 180, 180, 270, 180]
                }
            }
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(yaml_data, f, allow_unicode=True, default_flow_style=False)
            
            print(f"✅ Positions sauvegardées dans: {self.config_path}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur sauvegarde: {e}")
            return False
    
    def move_to_angles(self, angles, speed=1500):
        """
        Déplace le bras vers des angles spécifiques
        
        Args:
            angles: Liste de 6 angles [joint1...joint6]
            speed: Vitesse de déplacement (ms)
        """
        if self.simulation_mode:
            print(f"🔄 [SIMULATION] Déplacement vers: {angles}")
            self.current_angles = angles.copy()
            return True
        
        try:
            # Vérification des limites
            for i, angle in enumerate(angles):
                servo_id = i + 1
                min_angle, max_angle = self.SERVO_LIMITS[servo_id]
                
                if angle < min_angle or angle > max_angle:
                    print(f"⚠️  Servo {servo_id}: angle {angle}° hors limites [{min_angle}, {max_angle}]")
                    return False
            
            # Déplacement
            self.arm.Arm_serial_servo_write6_array(angles, speed)
            self.current_angles = angles.copy()
            time.sleep(speed / 1000 + 0.5)
            return True
            
        except Exception as e:
            print(f"❌ Erreur déplacement: {e}")
            return False
    
    def adjust_angle(self, servo_id, delta):
        """
        Ajuste l'angle d'un servo
        
        Args:
            servo_id: ID du servo (1-6)
            delta: Variation d'angle (+/-)
        """
        new_angles = self.current_angles.copy()
        new_angle = new_angles[servo_id - 1] + delta
        
        # Vérifier les limites
        min_angle, max_angle = self.SERVO_LIMITS[servo_id]
        new_angle = max(min_angle, min(max_angle, new_angle))
        
        new_angles[servo_id - 1] = new_angle
        
        if self.move_to_angles(new_angles, speed=500):
            return True
        return False
    
    def goto_home(self):
        """Va à la position HOME"""
        print("🏠 Déplacement vers HOME...")
        if 'HOME' in self.positions:
            return self.move_to_angles(self.positions['HOME'])
        return False
    
    def goto_observation(self):
        """Va à la position OBSERVATION"""
        print("👁️  Déplacement vers OBSERVATION...")
        if 'OBSERVATION' in self.positions:
            return self.move_to_angles(self.positions['OBSERVATION'])
        return False
    
    def goto_bin(self, bin_number):
        """
        Va vers un bac spécifique
        
        Args:
            bin_number: Numéro du bac (1=DANGEREUX, 2=MENAGERS, 3=RECYCLABLES)
        """
        bin_names = {1: 'DANGEREUX', 2: 'MENAGERS', 3: 'RECYCLABLES'}
        bin_name = bin_names.get(bin_number)
        
        if bin_name and bin_name in self.positions:
            print(f"📦 Déplacement vers BAC {bin_number} ({bin_name})...")
            return self.move_to_angles(self.positions[bin_name])
        else:
            print(f"⚠️  Bac {bin_number} non configuré")
            return False
    
    def save_current_as_position(self, position_name):
        """
        Sauvegarde la position actuelle
        
        Args:
            position_name: Nom de la position (HOME, OBSERVATION, DANGEREUX, etc.)
        """
        self.positions[position_name.upper()] = self.current_angles.copy()
        print(f"💾 Position {position_name.upper()} sauvegardée: {self.current_angles}")
        self.save_positions()
    
    def test_sequence(self):
        """Teste la séquence complète HOME → OBSERVATION → Bacs → HOME"""
        print("\n" + "="*60)
        print("🧪 TEST SÉQUENCE COMPLÈTE")
        print("="*60)
        
        sequence = [
            ("HOME", lambda: self.goto_home()),
            ("OBSERVATION", lambda: self.goto_observation()),
            ("BAC 1 (Dangereux)", lambda: self.goto_bin(1)),
            ("BAC 2 (Ménagers)", lambda: self.goto_bin(2)),
            ("BAC 3 (Recyclables)", lambda: self.goto_bin(3)),
            ("HOME (retour)", lambda: self.goto_home())
        ]
        
        for step_name, step_func in sequence:
            print(f"\n▶️  {step_name}...")
            if not step_func():
                print(f"❌ Échec à l'étape: {step_name}")
                return False
            time.sleep(2)
        
        print("\n✅ SÉQUENCE COMPLÈTE RÉUSSIE!")
        print("="*60)
        return True
    
    def display_status(self):
        """Affiche l'état actuel"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("╔" + "="*58 + "╗")
        print("║  🎯 CALIBRATION DOFBOT - DOFBOT WASTE SORTING           ║")
        print("║  Projet: dofbot-waste-sorting                                       ║")
        print("╚" + "="*58 + "╝")
        
        mode = "🔄 SIMULATION" if self.simulation_mode else "✅ CONNECTÉ"
        print(f"\nMode: {mode}")
        print(f"Servo actif: Joint {self.current_servo}")
        print(f"Pas de déplacement: {self.step_size}°")
        
        print("\n📊 POSITION ACTUELLE:")
        print("┌" + "─"*56 + "┐")
        for i, angle in enumerate(self.current_angles, 1):
            servo_name = ["Base", "Shoulder", "Elbow", "Wrist", "Roll", "Gripper"][i-1]
            min_a, max_a = self.SERVO_LIMITS[i]
            marker = "👉" if i == self.current_servo else "  "
            print(f"│ {marker} Joint{i} ({servo_name:8}): {angle:6.1f}° [{min_a}-{max_a}°]│")
        print("└" + "─"*56 + "┘")
        
        print("\n⌨️  COMMANDES:")
        print("┌─────────────────────────┬────────────────────────────┐")
        print("│ SÉLECTION SERVO         │ POSITIONS PRÉDÉFINIES      │")
        print("├─────────────────────────┼────────────────────────────┤")
        print("│ 1-6  : Sélectionner     │ h    : HOME                │")
        print("│        joint 1-6        │ o    : OBSERVATION         │")
        print("│                         │ b1   : Bac 1 (Dangereux)   │")
        print("│ AJUSTEMENT ANGLE        │ b2   : Bac 2 (Ménagers)    │")
        print("│ ↑    : +angle           │ b3   : Bac 3 (Recyclables) │")
        print("│ ↓    : -angle           │                            │")
        print("│                         │ ACTIONS                    │")
        print("│ AJUSTEMENT PAS          │ s    : Sauvegarder actuel  │")
        print("│ PgUp : Augmenter pas    │ t    : Tester séquence     │")
        print("│ PgDn : Diminuer pas     │ q    : Quitter             │")
        print("└─────────────────────────┴────────────────────────────┘")
    
    def get_key(self):
        """
        Lit une touche du clavier (Windows)
        Retourne: caractère ou code spécial
        """
        if msvcrt.kbhit():
            key = msvcrt.getch()
            
            # Touches spéciales (codes 224 ou 0)
            if key in [b'\xe0', b'\x00']:
                key2 = msvcrt.getch()
                # Flèches
                if key2 == b'H':  # Flèche haut
                    return 'UP'
                elif key2 == b'P':  # Flèche bas
                    return 'DOWN'
                elif key2 == b'I':  # Page Up
                    return 'PGUP'
                elif key2 == b'Q':  # Page Down
                    return 'PGDN'
            else:
                # Touches normales
                try:
                    return key.decode('utf-8').lower()
                except:
                    return None
        return None
    
    def run(self):
        """Boucle principale de calibration"""
        print("\n🚀 Démarrage de l'outil de calibration...")
        time.sleep(1)
        
        running = True
        last_update = time.time()
        
        while running:
            # Mettre à jour l'affichage toutes les 0.5s
            if time.time() - last_update > 0.5:
                self.display_status()
                last_update = time.time()
            
            key = self.get_key()
            
            if key:
                # Sélection servo (1-6)
                if key in '123456':
                    self.current_servo = int(key)
                    print(f"✓ Servo {self.current_servo} sélectionné")
                
                # Ajustement angle
                elif key == 'UP':
                    self.adjust_angle(self.current_servo, self.step_size)
                elif key == 'DOWN':
                    self.adjust_angle(self.current_servo, -self.step_size)
                
                # Ajustement pas
                elif key == 'PGUP':
                    self.current_step_index = (self.current_step_index + 1) % len(self.available_steps)
                    self.step_size = self.available_steps[self.current_step_index]
                    print(f"✓ Pas ajusté: {self.step_size}°")
                elif key == 'PGDN':
                    self.current_step_index = (self.current_step_index - 1) % len(self.available_steps)
                    self.step_size = self.available_steps[self.current_step_index]
                    print(f"✓ Pas ajusté: {self.step_size}°")
                
                # Positions prédéfinies
                elif key == 'h':
                    self.goto_home()
                elif key == 'o':
                    self.goto_observation()
                elif key == 'b':
                    # Attendre le numéro de bac
                    print("Entrez le numéro de bac (1-3): ", end='', flush=True)
                    bin_num = self.get_key()
                    if bin_num in '123':
                        self.goto_bin(int(bin_num))
                
                # Actions
                elif key == 's':
                    print("\n💾 SAUVEGARDER POSITION")
                    print("Quelle position voulez-vous sauvegarder?")
                    print("  h  : HOME")
                    print("  o  : OBSERVATION")
                    print("  b1 : BAC 1 (Dangereux)")
                    print("  b2 : BAC 2 (Ménagers)")
                    print("  b3 : BAC 3 (Recyclables)")
                    print("\nChoix: ", end='', flush=True)
                    
                    choice = input().strip().lower()
                    if choice == 'h':
                        self.save_current_as_position('HOME')
                    elif choice == 'o':
                        self.save_current_as_position('OBSERVATION')
                    elif choice == 'b1':
                        self.save_current_as_position('DANGEREUX')
                    elif choice == 'b2':
                        self.save_current_as_position('MENAGERS')
                    elif choice == 'b3':
                        self.save_current_as_position('RECYCLABLES')
                    else:
                        print("❌ Choix invalide")
                    
                    input("\nAppuyez sur Entrée pour continuer...")
                
                elif key == 't':
                    self.test_sequence()
                    input("\nAppuyez sur Entrée pour continuer...")
                
                elif key == 'q':
                    print("\n👋 Arrêt de la calibration...")
                    running = False
            
            time.sleep(0.01)  # Petite pause pour éviter 100% CPU
        
        # Retour à HOME avant de quitter
        if not self.simulation_mode:
            print("\n🏠 Retour à la position HOME...")
            self.goto_home()
        
        print("✅ Calibration terminée!")


def main():
    """Point d'entrée principal"""
    print("╔" + "="*58 + "╗")
    print("║                                                          ║")
    print("║  🤖 OUTIL DE CALIBRATION DOFBOT                         ║")
    print("║  DOFBOT WASTE SORTING                          ║")
    print("║  Projet: dofbot-waste-sorting                                       ║")
    print("║                                                          ║")
    print("╚" + "="*58 + "╝")
    
    try:
        calibrator = DofbotCalibration()
        calibrator.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interruption par l'utilisateur")
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n👋 Au revoir!")


if __name__ == '__main__':
    main()
