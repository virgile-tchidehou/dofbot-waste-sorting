#!/usr/bin/env python3
"""
Vision Node pour DOFBot - Classification de déchets avec YOLOv5
TRC2025 - TEKBOT Robotics Challenge

Ce node ROS charge le modèle YOLOv5 entraîné et fournit un service
de classification d'images pour identifier les types de déchets.

Classes:
    - dangereux (dangerous waste)
    - menagers (household waste)
    - recyclables (recyclable waste)

Services:
    /classify_waste (dofbot_tri/Classify) - Classifier une image

Topics:
    /camera/image_raw (sensor_msgs/Image) - Images de la caméra
    /waste_detection (std_msgs/String) - Résultat classification

Paramètres:
    ~model_path (string) - Chemin vers best.pt
    ~conf_threshold (float) - Seuil de confiance (défaut: 0.5)
    ~img_size (int) - Taille image pour inférence (défaut: 640)
    ~device (string) - Device PyTorch (défaut: 'cuda:0')
"""

import rospy
import torch
import sys
import os
from pathlib import Path
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge, CvBridgeError
import cv2
import numpy as np
import time

# Ajouter le chemin YOLOv5 au PYTHONPATH
FILE = Path(__file__).resolve()
MODELS_ROOT = FILE.parents[1] / 'models'
YOLOV5_ROOT = MODELS_ROOT / 'yolov5'

if str(YOLOV5_ROOT) not in sys.path:
    sys.path.append(str(YOLOV5_ROOT))

# Imports YOLOv5
try:
    from models.common import DetectMultiBackend
    from utils.general import (
        check_img_size,
        non_max_suppression,
        scale_boxes
    )
    from utils.torch_utils import select_device
    from utils.augmentations import letterbox
except ImportError as e:
    rospy.logerr(f"Erreur import YOLOv5: {e}")
    rospy.logerr(f"PYTHONPATH: {sys.path}")
    raise


class VisionNode:
    """Node ROS pour la détection et classification de déchets"""
    
    def __init__(self):
        """Initialiser le node vision"""
        rospy.init_node('vision_node', anonymous=False)
        
        # Paramètres ROS
        self.model_path = rospy.get_param(
            '~model_path',
            str(MODELS_ROOT / 'best.pt')
        )
        self.conf_threshold = rospy.get_param('~conf_threshold', 0.5)
        self.img_size = rospy.get_param('~img_size', 640)
        self.device_name = rospy.get_param('~device', 'cuda:0')
        self.enable_visualization = rospy.get_param('~enable_visualization', False)
        
        # Statistiques
        self.inference_times = []
        self.total_detections = 0
        self.detections_by_class = {'dangereux': 0, 'menagers': 0, 'recyclables': 0}
        
        rospy.loginfo("=" * 60)
        rospy.loginfo("  VISION NODE - TRC2025 DOFBot")
        rospy.loginfo("=" * 60)
        rospy.loginfo(f"Modèle: {self.model_path}")
        rospy.loginfo(f"Seuil confiance: {self.conf_threshold}")
        rospy.loginfo(f"Taille image: {self.img_size}")
        rospy.loginfo(f"Device: {self.device_name}")
        
        # Initialiser le modèle YOLOv5
        self._load_model()
        
        # Bridge ROS-OpenCV
        self.bridge = CvBridge()
        
        # Publisher pour les détections
        self.detection_pub = rospy.Publisher(
            '/waste_detection',
            String,
            queue_size=10
        )
        
        # Subscriber pour les images (optionnel - pour monitoring continu)
        self.enable_continuous = rospy.get_param('~enable_continuous', False)
        if self.enable_continuous:
            self.image_sub = rospy.Subscriber(
                '/camera/image_raw',
                Image,
                self.image_callback,
                queue_size=1
            )
            rospy.loginfo("Mode continu activé (subscriber /camera/image_raw)")
        
        # Service pour classification à la demande
        try:
            from dofbot_tri.srv import Classify, ClassifyResponse
            self.classify_service = rospy.Service(
                'classify_waste',
                Classify,
                self.classify_service_handler
            )
            rospy.loginfo("Service /classify_waste créé")
        except ImportError:
            rospy.logwarn("Service Classify non disponible (srv pas compilé?)")
            rospy.logwarn("Le node fonctionnera en mode subscriber uniquement")
        
        # Timer pour afficher les stats
        rospy.Timer(rospy.Duration(30), self.print_statistics)
        
        rospy.loginfo("=" * 60)
        rospy.loginfo("✅ Vision Node prêt !")
        rospy.loginfo("=" * 60)
    
    def _load_model(self):
        """Charger le modèle YOLOv5"""
        try:
            rospy.loginfo("Chargement du modèle YOLOv5...")
            
            # Sélectionner le device
            self.device = select_device(self.device_name)
            rospy.loginfo(f"Device sélectionné: {self.device}")
            
            # Charger le modèle
            self.model = DetectMultiBackend(
                self.model_path,
                device=self.device,
                dnn=False,
                fp16=False
            )
            
            # Paramètres du modèle
            self.stride = self.model.stride
            self.names = self.model.names
            self.img_size = check_img_size(self.img_size, s=self.stride)
            
            # Warmup (première inférence lente)
            rospy.loginfo("Warmup du modèle...")
            dummy = torch.zeros((1, 3, self.img_size, self.img_size)).to(self.device)
            for _ in range(2):
                _ = self.model(dummy)
            
            rospy.loginfo(f"✅ Modèle chargé avec succès")
            rospy.loginfo(f"Classes détectées: {self.names}")
            
        except Exception as e:
            rospy.logerr(f"❌ Erreur chargement modèle: {e}")
            raise
    
    def preprocess_image(self, img):
        """
        Prétraiter une image OpenCV pour YOLOv5
        
        Args:
            img (np.ndarray): Image BGR de OpenCV
            
        Returns:
            torch.Tensor: Image prétraitée pour inférence
        """
        # Letterbox resize (garde aspect ratio)
        img = letterbox(img, self.img_size, stride=self.stride, auto=True)[0]
        
        # Convert BGR to RGB et HWC to CHW
        img = img.transpose((2, 0, 1))[::-1]
        img = np.ascontiguousarray(img)
        
        # Convertir en tensor PyTorch
        img = torch.from_numpy(img).to(self.device)
        img = img.float() / 255.0  # 0-255 to 0.0-1.0
        
        # Ajouter dimension batch si nécessaire
        if len(img.shape) == 3:
            img = img[None]  # (C, H, W) -> (1, C, H, W)
        
        return img
    
    def classify_image(self, cv_image):
        """
        Classifier une image avec YOLOv5
        
        Args:
            cv_image (np.ndarray): Image BGR de OpenCV
            
        Returns:
            tuple: (class_name, confidence, bbox) ou (None, 0.0, None) si rien détecté
                - class_name (str): 'dangereux', 'menagers', ou 'recyclables'
                - confidence (float): Confiance de la prédiction (0-1)
                - bbox (list): [x1, y1, x2, y2] coordonnées de la boîte
        """
        start_time = time.time()
        
        try:
            # Prétraitement
            img = self.preprocess_image(cv_image)
            
            # Inférence
            with torch.no_grad():
                pred = self.model(img, augment=False, visualize=False)
            
            # Post-traitement (NMS - Non-Maximum Suppression)
            pred = non_max_suppression(
                pred,
                self.conf_threshold,
                0.45,  # IOU threshold
                None,  # classes filter
                False,  # agnostic NMS
                max_det=10  # max détections
            )
            
            # Temps d'inférence
            inference_time = (time.time() - start_time) * 1000  # en ms
            self.inference_times.append(inference_time)
            if len(self.inference_times) > 100:
                self.inference_times.pop(0)
            
            # Extraire la meilleure détection
            if len(pred[0]) > 0:
                # Trier par confiance (descendant)
                pred[0] = pred[0][pred[0][:, 4].argsort(descending=True)]
                
                # Meilleure détection: [x1, y1, x2, y2, conf, class]
                best_det = pred[0][0]
                
                # Extraire infos
                bbox = best_det[:4].cpu().numpy().tolist()
                confidence = float(best_det[4])
                class_id = int(best_det[5])
                class_name = self.names[class_id]
                
                # Stats
                self.total_detections += 1
                if class_name in self.detections_by_class:
                    self.detections_by_class[class_name] += 1
                
                rospy.loginfo(
                    f"🎯 Détection: {class_name.upper()} "
                    f"(confiance: {confidence:.2f}, "
                    f"temps: {inference_time:.1f}ms)"
                )
                
                return class_name, confidence, bbox
            else:
                rospy.logdebug(f"Aucune détection (temps: {inference_time:.1f}ms)")
                return None, 0.0, None
                
        except Exception as e:
            rospy.logerr(f"❌ Erreur classification: {e}")
            return None, 0.0, None
    
    def image_callback(self, msg):
        """
        Callback pour les images de la caméra (mode continu)
        
        Args:
            msg (sensor_msgs/Image): Message image ROS
        """
        try:
            # Convertir ROS Image -> OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            
            # Classifier
            class_name, confidence, bbox = self.classify_image(cv_image)
            
            # Publier si détection valide
            if class_name and confidence >= self.conf_threshold:
                detection_msg = String()
                detection_msg.data = f"{class_name}:{confidence:.2f}"
                self.detection_pub.publish(detection_msg)
                
                # Visualisation optionnelle
                if self.enable_visualization and bbox:
                    self._visualize_detection(cv_image, class_name, confidence, bbox)
                    
        except CvBridgeError as e:
            rospy.logerr(f"❌ Erreur conversion image: {e}")
        except Exception as e:
            rospy.logerr(f"❌ Erreur traitement image: {e}")
    
    def classify_service_handler(self, req):
        """
        Handler pour le service ROS /classify_waste
        
        Args:
            req (dofbot_tri/ClassifyRequest): Image à classifier
            
        Returns:
            dofbot_tri/ClassifyResponse: Résultat classification
        """
        from dofbot_tri.srv import ClassifyResponse
        
        try:
            # Convertir ROS Image -> OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(req.image, "bgr8")
            
            # Classifier
            class_name, confidence, bbox = self.classify_image(cv_image)
            
            # Préparer la réponse
            if class_name:
                return ClassifyResponse(
                    waste_type=class_name,
                    confidence=confidence
                )
            else:
                return ClassifyResponse(
                    waste_type="unknown",
                    confidence=0.0
                )
                
        except CvBridgeError as e:
            rospy.logerr(f"❌ Erreur conversion image service: {e}")
            return ClassifyResponse(waste_type="error", confidence=0.0)
        except Exception as e:
            rospy.logerr(f"❌ Erreur service classification: {e}")
            return ClassifyResponse(waste_type="error", confidence=0.0)
    
    def _visualize_detection(self, img, class_name, confidence, bbox):
        """
        Afficher la détection sur l'image (debug)
        
        Args:
            img (np.ndarray): Image OpenCV
            class_name (str): Nom de la classe
            confidence (float): Confiance
            bbox (list): [x1, y1, x2, y2]
        """
        try:
            # Dessiner la boîte
            x1, y1, x2, y2 = map(int, bbox)
            color = self._get_class_color(class_name)
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
            
            # Label
            label = f"{class_name}: {confidence:.2f}"
            cv2.putText(
                img, label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5, color, 2
            )
            
            # Afficher (nécessite X11 forwarding ou écran connecté)
            cv2.imshow("Detection", img)
            cv2.waitKey(1)
            
        except Exception as e:
            rospy.logwarn(f"Erreur visualisation: {e}")
    
    def _get_class_color(self, class_name):
        """Couleur BGR pour chaque classe"""
        colors = {
            'dangereux': (0, 0, 255),    # Rouge
            'menagers': (255, 0, 0),     # Bleu
            'recyclables': (0, 255, 0)   # Vert
        }
        return colors.get(class_name, (255, 255, 255))
    
    def print_statistics(self, event):
        """Afficher les statistiques périodiquement"""
        if len(self.inference_times) > 0:
            avg_time = np.mean(self.inference_times)
            fps = 1000.0 / avg_time if avg_time > 0 else 0
            
            rospy.loginfo("=" * 60)
            rospy.loginfo("📊 STATISTIQUES VISION NODE")
            rospy.loginfo(f"  Temps inférence moyen: {avg_time:.1f} ms ({fps:.1f} FPS)")
            rospy.loginfo(f"  Détections totales: {self.total_detections}")
            rospy.loginfo(f"  Par classe:")
            for class_name, count in self.detections_by_class.items():
                pct = (count / self.total_detections * 100) if self.total_detections > 0 else 0
                rospy.loginfo(f"    - {class_name}: {count} ({pct:.1f}%)")
            rospy.loginfo("=" * 60)
    
    def shutdown_hook(self):
        """Cleanup lors de l'arrêt du node"""
        rospy.loginfo("Arrêt du Vision Node...")
        if self.enable_visualization:
            cv2.destroyAllWindows()


def main():
    """Point d'entrée principal"""
    try:
        node = VisionNode()
        rospy.on_shutdown(node.shutdown_hook)
        rospy.spin()
        
    except rospy.ROSInterruptException:
        rospy.loginfo("Vision Node interrompu")
    except Exception as e:
        rospy.logerr(f"❌ Erreur fatale: {e}")
        raise


if __name__ == '__main__':
    main()
