#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import rospy
import cv2
import time
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

class FinalCameraNode:
    def __init__(self):
        rospy.init_node('final_camera_node')
        
        self.bridge = CvBridge()
        self.image_pub = rospy.Publisher('/dofbot_camera/image_raw', Image, queue_size=10)
        
        # Configuration éprouvée
        self.camera_index = 0
        self.frame_width = 640
        self.frame_height = 480
        self.fps = 10  # Correspond à notre test (9 FPS)
        
        # Initialisation caméra
        self.cap = self.setup_camera()
        if self.cap is None:
            rospy.logerr("? Échec initialisation caméra")
            return
            
        rospy.loginfo("? Node caméra final initialisé")
        rospy.loginfo("? Publication sur: /dofbot_camera/image_raw")
        rospy.loginfo("? Résolution: %dx%d", self.frame_width, self.frame_height)
        
    def setup_camera(self):
        """Configure la caméra avec les paramètres éprouvés"""
        try:
            cap = cv2.VideoCapture(self.camera_index)
            
            if not cap.isOpened():
                rospy.logerr("? Impossible d'ouvrir /dev/video%d", self.camera_index)
                return None
            
            # Configuration optimisée basée sur nos tests
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
            cap.set(cv2.CAP_PROP_FPS, self.fps)
            
            # Test de validation
            ret, frame = cap.read()
            if not ret:
                rospy.logerr("? Test capture échoué")
                cap.release()
                return None
                
            rospy.loginfo("? Test capture réussi")
            return cap
            
        except Exception as e:
            rospy.logerr("? Exception setup caméra: %s", e)
            return None
    
    def capture_and_publish(self):
        """Capture et publie une frame"""
        if self.cap is None:
            return False
            
        try:
            ret, frame = self.cap.read()
            if ret:
                # Redimensionner pour consistance
                frame = cv2.resize(frame, (self.frame_width, self.frame_height))
                
                # Convertir en message ROS
                ros_image = self.bridge.cv2_to_imgmsg(frame, "bgr8")
                ros_image.header.stamp = rospy.Time.now()
                ros_image.header.frame_id = "camera_frame"
                
                # Publier
                self.image_pub.publish(ros_image)
                return True
            else:
                rospy.logwarn("??  Échec capture frame")
                return False
                
        except Exception as e:
            rospy.logerr("? Erreur capture/publication: %s", e)
            return False
    
    def run(self):
        """Boucle principale"""
        rate = rospy.Rate(self.fps)
        success_count = 0
        error_count = 0
        
        rospy.loginfo("? Démarrage capture caméra...")
        
        while not rospy.is_shutdown():
            if self.capture_and_publish():
                success_count += 1
                
                # Log périodique
                if success_count % 30 == 0:  # Toutes les ~3 secondes à 10 FPS
                    rospy.loginfo("? Frames publiées: %d, erreurs: %d", 
                                 success_count, error_count)
            else:
                error_count += 1
                
                # Arrêt après trop d'erreurs consécutives
                if error_count >= 10:
                    rospy.logerr("? Trop d'erreurs, arrêt du node")
                    break
            
            rate.sleep()
    
    def __del__(self):
        """Nettoyage"""
        if hasattr(self, 'cap') and self.cap is not None:
            self.cap.release()
            cv2.destroyAllWindows()
            rospy.loginfo("? Caméra libérée")

if __name__ == "__main__":
    try:
        node = FinalCameraNode()
        node.run()
    except rospy.ROSInterruptException:
        pass
    except Exception as e:
        rospy.logerr("? Erreur critique: %s", e)
