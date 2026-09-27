#!/usr/bin/env python3
import rospy
import smbus 
import time
from arm_info.srv import kinemarics, kinemaricsRequest
from dofbot_tri.srv import Classify, ClassifyRequest
from sensor_msgs.msg import Image
from Arm_Lib import Arm_Device

class DofbotTriController:
    def __init__(self):
        # Initialisation ROS
        rospy.init_node('dofbot_tri_controller', anonymous=True)
        
        # ? PARAMÈTRES DE SÉCURITÉ
        self.SERVO_LIMITS = {
            1: (0, 270),   # Base
            2: (0, 180),   # Épaule  
            3: (0, 180),   # Coude
            4: (0, 180),   # Poignet
            5: (0, 270),   # Rotation pince
            6: (0, 180)    # Pince
        }
        self.MAX_SPEED = 1500  # ms pour mouvement (plus = plus lent)
        self.SAFE_HOME = [90, 90, 90, 90, 90, 30]  # Position SAFE
        
        # Initialisation du Bras
        self.arm = Arm_Device()
        time.sleep(2)  # ?? Plus long pour l'initialisation
        self.arm.Arm_serial_set_torque(1)
        
        # Configuration I2C
        try:
            self.bus = smbus.SMBus(1)
            self.arduino_addr = 0x08
            rospy.loginfo("? I2C initialisé")
        except Exception as e:
            rospy.logerr(f"? Erreur I2C: {e}")
            self.bus = None
        
        # Attente des services ROS
        rospy.loginfo("? Attente des services ROS...")
        try:
            rospy.wait_for_service('/get_kinemarics', timeout=30)
            rospy.wait_for_service('vision/classify', timeout=30)
        except rospy.ROSException:
            rospy.logerr("? Timeout attente services ROS")
            return
        
        # Clients pour les services
        self.kinematics_srv = rospy.ServiceProxy('/get_kinemarics', kinemarics)
        self.vision_srv = rospy.ServiceProxy('vision/classify', Classify)
        
        # ? Positions CALIBRÉES (À ADAPTER À VOTRE SETUP)
        self.home_position = [90, 90, 90, 90, 90, 30]  # Pince OUVERTE
        self.bin_coordinates = {
            "recyclable": (120, -80, 20),
            "menager": (80, 150, 20), 
            "dangereux": (200, 0, 20)
        }
        self.conveyor_pick_position = (150, 0, 30)
        
        rospy.loginfo("? Contrôleur Dofbot initialisé en mode SÉCURISÉ")

    def check_servo_limits(self, angles):
        """? Vérifie que les angles sont dans les limites de sécurité"""
        if angles is None or len(angles) != 6:
            return False
            
        for i, angle in enumerate(angles):
            servo_id = i + 1
            min_angle, max_angle = self.SERVO_LIMITS[servo_id]
            if not (min_angle <= angle <= max_angle):
                rospy.logwarn(f"? Angle servo {servo_id} hors limites: {angle}")
                return False
        return True

    def safe_move(self, angles, duration):
        """? Déplacement SÉCURISÉ du bras avec vérifications"""
        if not self.check_servo_limits(angles):
            rospy.logerr("? Mouvement annulé - angles invalides")
            return False
            
        try:
            # Vérification supplémentaire de la durée
            if duration < 500 or duration > 3000:
                rospy.logwarn("??  Durée de mouvement anormale, ajustée")
                duration = min(max(duration, 500), 3000)
                
            # Déplacement avec monitoring
            self.arm.Arm_serial_servo_write6(
                angles[0], angles[1], angles[2], 
                angles[3], angles[4], angles[5], 
                duration
            )
            
            # Attente contrôlée
            sleep_time = duration / 1000 + 0.5
            time.sleep(sleep_time)
            
            rospy.loginfo(f"? Mouvement terminé: {angles}")
            return True
            
        except Exception as e:
            rospy.logerr(f"? Erreur pendant le mouvement: {e}")
            self.emergency_stop()
            return False

    def emergency_stop(self):
        """? Arrêt d'urgence - position SAFE"""
        rospy.logwarn("? Activation mode sécurité...")
        try:
            # Mouvement très lent vers position safe
            self.arm.Arm_serial_servo_write6_array(self.SAFE_HOME, 3000)
            time.sleep(3.5)
            rospy.loginfo("? Mode sécurité activé")
        except Exception as e:
            rospy.logerr(f"? Erreur mode sécurité: {e}")

    def read_i2c_detection(self):
        """Lecture sécurisée I2C"""
        if self.bus is None:
            return False
            
        try:
            detection_state = self.bus.read_byte_data(self.arduino_addr, 0)
            return detection_state == 1
        except Exception as e:
            rospy.logwarn(f"??  Erreur I2C: {e}")
            return False

    def get_image_from_camera(self):
        """Capture d'image avec timeout"""
        try:
            image_msg = rospy.wait_for_message("/usb_cam/image_raw", Image, timeout=5)
            return image_msg
        except rospy.ROSException:
            rospy.logwarn("??  Timeout caméra - vérifier /usb_cam/image_raw")
            return None

    def execute_pick_and_place(self, target_coords):
        """? Séquence Pick & Place SÉCURISÉE"""
        rospy.loginfo("? Début séquence Pick & Place sécurisée")
        
        x_t, y_t, z_t = target_coords
        x_p, y_p, z_p = self.conveyor_pick_position
        
        # ? SÉQUENCE SÉCURISÉE :
        steps = [
            # (description, x, y, z, pince)
            ("Au-dessus convoyeur", x_p, y_p, z_p + 40, 30),
            ("Approche objet", x_p, y_p, z_p + 10, 30), 
            ("Saisie objet", x_p, y_p, z_p, 30),
            ("? Fermeture pince", x_p, y_p, z_p, 135),
            ("Lever objet", x_p, y_p, z_p + 40, 135),
            ("Transport", x_t, y_t, z_t + 40, 135),
            ("Descente corbeille", x_t, y_t, z_t + 10, 135),
            ("Dépose", x_t, y_t, z_t, 135),
            ("? Ouverture pince", x_t, y_t, z_t, 30),
            ("Retrait", x_t, y_t, z_t + 30, 30),
        ]
        
        for desc, x, y, z, gripper in steps:
            rospy.loginfo(f"??  {desc}")
            
            if "pince" in desc.lower():
                # Commande directe de la pince
                try:
                    self.arm.Arm_serial_servo_write(6, gripper, 800)
                    time.sleep(1)
                except Exception as e:
                    rospy.logerr(f"? Erreur pince: {e}")
                    return False
            else:
                # Mouvement du bras
                angles = self.calculate_angles(x, y, z)
                if not self.safe_move(angles + [gripper], 1500):
                    rospy.logerr("? Séquence interrompue")
                    return False
            
            time.sleep(0.5)  # Pause entre les steps
        
        # Retour position initiale
        self.safe_move(self.home_position, 2000)
        rospy.loginfo("? Séquence Pick & Place terminée avec succès")
        return True

    def run(self):
        """Boucle principale SÉCURISÉE"""
        rate = rospy.Rate(2)  # ? Plus lent pour la sécurité
        
        # Position initiale sécurisée
        if not self.safe_move(self.home_position, 3000):
            rospy.logerr("? Impossible d'atteindre position initiale")
            return
            
        rospy.loginfo("? Contrôleur prêt - Mode sécurisé activé")
        
        while not rospy.is_shutdown():
            try:
                if self.read_i2c_detection():
                    rospy.loginfo("? Objet détecté sur convoyeur!")
                    self.reset_i2c_detection()
                    
                    # Petite pause pour stabilisation
                    time.sleep(1)
                    
                    # Acquisition image
                    image_msg = self.get_image_from_camera()
                    if image_msg is None:
                        continue
                    
                    # Classification
                    waste_class, confidence = self.classify_waste(image_msg)
                    rospy.loginfo(f"? Classification: {waste_class} ({confidence:.2f})")
                    
                    if confidence > 0.6:  # ? Seuil ajusté
                        target_coords = self.bin_coordinates.get(waste_class)
                        if target_coords:
                            success = self.execute_pick_and_place(target_coords)
                            if success:
                                rospy.loginfo(f"??  Déchet '{waste_class}' trié avec succès!")
                            else:
                                rospy.logwarn("??  Échec de la séquence de tri")
                        else:
                            rospy.logwarn(f"? Classe inconnue: {waste_class}")
                    else:
                        rospy.logwarn(f"? Confiance trop faible: {confidence:.2f}")
                
                rate.sleep()
                
            except Exception as e:
                rospy.logerr(f"? Erreur dans la boucle principale: {e}")
                self.emergency_stop()
                break

if __name__ == '__main__':
    try:
        controller = DofbotTriController()
        controller.run()
    except rospy.ROSInterruptException:
        rospy.loginfo("? Contrôleur arrêté proprement")
    except Exception as e:
        rospy.logerr(f"? Erreur critique: {e}")
