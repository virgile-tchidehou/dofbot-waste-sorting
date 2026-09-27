#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌐 SERVEUR WEBSOCKET POUR CALIBRATION DOFBOT
Permet la communication entre l'interface web et le bras robotique

Équipe: Ucaotech
TRC 2025 - Cotonou, Bénin
"""

import asyncio
import websockets
import json
import yaml
import os
import sys
from datetime import datetime

# Ajouter le chemin pour Arm_Lib
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from Arm_Lib import Arm_Device
    ARM_LIB_AVAILABLE = True
except ImportError:
    ARM_LIB_AVAILABLE = False
    print("⚠️  Arm_Lib non disponible - Mode simulation uniquement")


class CalibrationServer:
    """Serveur WebSocket pour calibration du bras DOFbot"""
    
    def __init__(self, config_path='../config/positions.yaml'):
        """
        Initialise le serveur de calibration
        
        Args:
            config_path: Chemin vers le fichier positions.yaml
        """
        self.config_path = os.path.join(os.path.dirname(__file__), config_path)
        self.clients = set()
        self.arm = None
        self.simulation_mode = True
        
        # Limites de sécurité
        self.SERVO_LIMITS = {
            1: (0, 180), 2: (0, 180), 3: (0, 180),
            4: (0, 180), 5: (0, 270), 6: (0, 180)
        }
        
        # Position actuelle
        self.current_angles = [90, 90, 90, 90, 90, 30]
        
        # Charger les positions
        self.positions = self.load_positions()
        
        # Initialiser le bras si disponible
        if ARM_LIB_AVAILABLE:
            try:
                self.arm = Arm_Device()
                self.arm.Arm_serial_set_torque(1)
                self.simulation_mode = False
                print("✅ Bras DOFbot connecté!")
            except Exception as e:
                print(f"⚠️  Erreur connexion bras: {e}")
                print("🔄 Mode simulation activé")
    
    def load_positions(self):
        """Charge les positions depuis positions.yaml"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            print(f"✅ Positions chargées depuis: {self.config_path}")
            return data
        except Exception as e:
            print(f"⚠️  Erreur chargement positions: {e}")
            return self.get_default_positions()
    
    def get_default_positions(self):
        """Retourne des positions par défaut"""
        return {
            'home': {'joint1': 90, 'joint2': 90, 'joint3': 90, 'joint4': 90, 'joint5': 90, 'gripper': 30},
            'observation': {'joint1': 90, 'joint2': 100, 'joint3': 80, 'joint4': 90, 'joint5': 90, 'gripper': 30},
            'bins': {
                'dangereux': {'joint1': 135, 'joint2': 100, 'joint3': 60, 'joint4': 90, 'joint5': 90, 'gripper': 30},
                'menagers': {'joint1': 90, 'joint2': 100, 'joint3': 60, 'joint4': 90, 'joint5': 90, 'gripper': 30},
                'recyclables': {'joint1': 45, 'joint2': 100, 'joint3': 60, 'joint4': 90, 'joint5': 90, 'gripper': 30}
            }
        }
    
    def save_positions(self):
        """Sauvegarde les positions dans positions.yaml"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.positions, f, allow_unicode=True, default_flow_style=False)
            print(f"✅ Positions sauvegardées: {self.config_path}")
            return True
        except Exception as e:
            print(f"❌ Erreur sauvegarde: {e}")
            return False
    
    def move_joint(self, joint_id, angle):
        """
        Déplace un joint spécifique
        
        Args:
            joint_id: ID du joint (1-6)
            angle: Angle cible
        """
        # Vérifier les limites
        min_angle, max_angle = self.SERVO_LIMITS[joint_id]
        if angle < min_angle or angle > max_angle:
            return False, f"Angle hors limites [{min_angle}, {max_angle}]"
        
        # Mettre à jour la position actuelle
        self.current_angles[joint_id - 1] = angle
        
        # Déplacer le bras physique si connecté
        if not self.simulation_mode and self.arm:
            try:
                self.arm.Arm_serial_servo_write(joint_id, angle, 500)
                return True, f"Joint {joint_id} déplacé à {angle}°"
            except Exception as e:
                return False, f"Erreur déplacement: {e}"
        else:
            return True, f"[SIMULATION] Joint {joint_id} → {angle}°"
    
    def move_to_angles(self, angles):
        """
        Déplace le bras vers des angles spécifiques
        
        Args:
            angles: Liste de 6 angles
        """
        # Vérifier toutes les limites
        for i, angle in enumerate(angles):
            joint_id = i + 1
            min_angle, max_angle = self.SERVO_LIMITS[joint_id]
            if angle < min_angle or angle > max_angle:
                return False, f"Joint {joint_id}: angle {angle}° hors limites"
        
        # Mettre à jour la position actuelle
        self.current_angles = angles.copy()
        
        # Déplacer le bras physique
        if not self.simulation_mode and self.arm:
            try:
                self.arm.Arm_serial_servo_write6_array(angles, 1500)
                return True, "Position atteinte"
            except Exception as e:
                return False, f"Erreur: {e}"
        else:
            return True, f"[SIMULATION] Position: {angles}"
    
    def save_position(self, position_name, angles):
        """
        Sauvegarde une position nommée
        
        Args:
            position_name: Nom de la position (home, observation, dangereux, etc.)
            angles: Liste de 6 angles
        """
        try:
            if position_name == 'home':
                self.positions['home'] = {
                    'joint1': angles[0], 'joint2': angles[1], 'joint3': angles[2],
                    'joint4': angles[3], 'joint5': angles[4], 'gripper': angles[5],
                    'speed': 1500, 'description': "Position de repos"
                }
            elif position_name == 'observation':
                self.positions['observation'] = {
                    'joint1': angles[0], 'joint2': angles[1], 'joint3': angles[2],
                    'joint4': angles[3], 'joint5': angles[4], 'gripper': angles[5],
                    'speed': 1500, 'description': "Position d'observation caméra"
                }
            elif position_name in ['dangereux', 'menagers', 'recyclables']:
                if 'bins' not in self.positions:
                    self.positions['bins'] = {}
                self.positions['bins'][position_name] = {
                    'joint1': angles[0], 'joint2': angles[1], 'joint3': angles[2],
                    'joint4': angles[3], 'joint5': angles[4], 'gripper': angles[5],
                    'speed': 1500, 'class': position_name
                }
            
            self.save_positions()
            return True, f"Position {position_name} sauvegardée"
        except Exception as e:
            return False, f"Erreur sauvegarde: {e}"
    
    async def send_log(self, websocket, message, level='info'):
        """Envoie un message de log au client"""
        await websocket.send(json.dumps({
            'type': 'log',
            'message': message,
            'level': level,
            'timestamp': datetime.now().isoformat()
        }))
    
    async def handle_client(self, websocket):
        """Gère les connexions clients WebSocket"""
        # Enregistrer le client
        self.clients.add(websocket)
        
        try:
            # Message de bienvenue
            await self.send_log(websocket, "✅ Connecté au serveur de calibration", 'success')
            
            if self.simulation_mode:
                await self.send_log(websocket, "🔄 Mode simulation actif", 'warning')
            else:
                await self.send_log(websocket, "✅ Bras DOFbot connecté", 'success')
            
            # Boucle de réception des messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    command = data.get('command')
                    params = data.get('data', {})
                    
                    # Traiter les commandes
                    if command == 'move_joint':
                        joint_id = params.get('joint')
                        angle = params.get('angle')
                        success, msg = self.move_joint(joint_id, angle)
                        level = 'success' if success else 'error'
                        await self.send_log(websocket, msg, level)
                    
                    elif command == 'move_to_position':
                        angles = params.get('angles')
                        success, msg = self.move_to_angles(angles)
                        level = 'success' if success else 'error'
                        await self.send_log(websocket, msg, level)
                    
                    elif command == 'save_position':
                        position_name = params.get('name')
                        angles = params.get('angles')
                        success, msg = self.save_position(position_name, angles)
                        level = 'success' if success else 'error'
                        await self.send_log(websocket, msg, level)
                    
                    elif command == 'get_positions':
                        await websocket.send(json.dumps({
                            'type': 'positions',
                            'data': self.positions
                        }))
                    
                    elif command == 'get_status':
                        await websocket.send(json.dumps({
                            'type': 'status',
                            'simulation_mode': self.simulation_mode,
                            'current_angles': self.current_angles
                        }))
                    
                    else:
                        await self.send_log(websocket, f"⚠️ Commande inconnue: {command}", 'warning')
                
                except json.JSONDecodeError:
                    await self.send_log(websocket, "❌ Erreur décodage JSON", 'error')
                except Exception as e:
                    await self.send_log(websocket, f"❌ Erreur traitement: {e}", 'error')
        
        except websockets.exceptions.ConnectionClosed:
            print(f"🔌 Client déconnecté: {websocket.remote_address}")
        
        finally:
            # Retirer le client
            self.clients.remove(websocket)
    
    async def start_server(self, host='0.0.0.0', port=8765):
        """
        Démarre le serveur WebSocket
        
        Args:
            host: Adresse d'écoute (0.0.0.0 = toutes les interfaces)
            port: Port d'écoute
        """
        print("╔" + "="*58 + "╗")
        print("║  🌐 SERVEUR CALIBRATION DOFBOT                          ║")
        print("║  TRC 2025 - Cotonou, Bénin 🇧🇯                          ║")
        print("╚" + "="*58 + "╝")
        print(f"\n🚀 Serveur WebSocket démarré sur ws://{host}:{port}")
        print(f"📊 Mode: {'🔄 SIMULATION' if self.simulation_mode else '✅ CONNECTÉ'}")
        print(f"📁 Configuration: {self.config_path}")
        print("\n💡 Ouvrez web/calibration_interface.html dans votre navigateur")
        print("⌨️  Appuyez sur Ctrl+C pour arrêter\n")
        
        async with websockets.serve(self.handle_client, host, port):
            await asyncio.Future()  # Run forever


def main():
    """Point d'entrée principal"""
    try:
        server = CalibrationServer()
        asyncio.run(server.start_server())
    except KeyboardInterrupt:
        print("\n\n⚠️  Serveur arrêté par l'utilisateur")
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n👋 Au revoir!")


if __name__ == '__main__':
    main()
