#!/usr/bin/env python3
"""
Vision Node pour système de tri DOFbot TRC2025
Utilise YOLOv5m pour la classification des déchets
Classes: 0=dangereux, 1=menagers, 2=recyclables

Version simplifiée compatible avec PyTorch 1.6.0 (Jetson Nano)
"""
import rospy
import cv2
import torch
import numpy as np
import sys
import os
import json
from pathlib import Path
from cv_bridge import CvBridge
from dofbot_tri.srv import Classify, ClassifyResponse
from sensor_msgs.msg import Image

class VisionNode:
    def __init__(self):
        rospy.init_node('vision_node')
        
        # Initialisation de CV Bridge
        self.bridge = CvBridge()
        
        # Chargement des paramètres depuis ROS param server (ou valeurs par défaut)
        self.conf_threshold = rospy.get_param('~conf_threshold', 0.6)
        self.iou_threshold = rospy.get_param('~iou_threshold', 0.45)
        self.img_size = rospy.get_param('~img_size', 640)
        
        # Charger les noms des classes depuis class_names.json
        self.class_names = self.load_class_names()
        
        # Modèle YOLOv5
        self.model = None
        self.device = None
        self.model_ready = False
        
        # Charger le modèle
        self.load_model()
        
        # Service de classification
        self.service = rospy.Service('vision/classify', Classify, self.handle_classify_request)
        
        rospy.loginfo("[OK] Vision Node ready - Service: vision/classify")
        rospy.loginfo(f"[PARAMS] Paramètres: conf={self.conf_threshold}, iou={self.iou_threshold}, img_size={self.img_size}")

    def load_class_names(self):
        """Charge les noms des classes depuis class_names.json"""
        try:
            script_dir = Path(__file__).parent.absolute()
            models_dir = script_dir.parent.parent / "models"
            class_names_path = models_dir / "class_names.json"
            
            if class_names_path.exists():
                with open(class_names_path, 'r') as f:
                    data = json.load(f)
                    # Utiliser les catégories du JSON
                    categories = data.get('categories', {})
                    # Convertir en liste ordonnée par ID
                    names = [''] * len(categories)
                    for name, info in categories.items():
                        idx = info.get('id', 0)
                        if idx < len(names):
                            names[idx] = name
                    return names
            else:
                rospy.logwarn(f"[WARNING] class_names.json introuvable: {class_names_path}")
                return ['dangereux', 'menagers', 'recyclables']
        except Exception as e:
            rospy.logerr(f"[ERROR] Erreur chargement class_names.json: {e}")
            return ['dangereux', 'menagers', 'recyclables']

    def load_model(self):
        """Charge le modèle YOLOv5m entraîné"""
        try:
            rospy.loginfo("[LOADING] Chargement du modèle YOLOv5...")
            
            # Chemin vers best.pt
            script_dir = Path(__file__).parent.absolute()
            models_dir = script_dir.parent.parent / "models"
            model_path = models_dir / "best.pt"
            
            if not model_path.exists():
                rospy.logerr(f"[ERROR] Modèle introuvable: {model_path}")
                rospy.logerr("[NOTE] Vérifier que best.pt est dans models/")
                return
            
            # Sélectionner le device (CUDA si disponible, sinon CPU)
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            rospy.loginfo(f"[DEVICE]  Device sélectionné: {self.device}")
            
            # Essayer de charger avec ultralytics d'abord
            try:
                from ultralytics import YOLO
                self.model = YOLO(str(model_path))
                self.model.to(self.device)
                self.model_ready = True
                rospy.loginfo("[OK] Modèle chargé avec ultralytics")
                return
            except ImportError:
                rospy.logwarn("[WARNING] ultralytics non disponible, tentative de chargement direct")
            
            # Chargement direct du checkpoint (pour PyTorch 1.6.0)
            try:
                checkpoint = torch.load(str(model_path), map_location=self.device)
                
                if 'model' in checkpoint:
                    self.model = checkpoint['model']
                    self.model.to(self.device)
                    self.model.eval()
                    self.model_ready = True
                    rospy.loginfo("[OK] Modèle chargé directement depuis checkpoint")
                    
                    # Vérifier les noms des classes
                    if hasattr(self.model, 'names'):
                        model_names = self.model.names
                    elif hasattr(self.model, 'module') and hasattr(self.model.module, 'names'):
                        model_names = self.model.module.names
                    else:
                        model_names = self.class_names
                    
                    rospy.loginfo(f"[CLASSES]  Classes du modèle: {model_names}")
                else:
                    raise ValueError("Structure du checkpoint invalide")
                    
            except Exception as e:
                # Si le chargement direct échoue, utiliser la classification simulée
                rospy.logwarn(f"[WARNING] Chargement modèle impossible: {e}")
                rospy.logwarn("[NOTE] Utilisation de la classification simulée")
                self.model_ready = False
            
        except Exception as e:
            rospy.logerr(f"[ERROR] Erreur chargement modèle: {e}")
            self.model_ready = False

    def handle_classify_request(self, req):
        """Traite les requêtes de classification d'images"""
        try:
            # Conversion ROS Image → OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(req.image, "bgr8")
            
            # Classification YOLOv5 (ou simulation si modèle non disponible)
            if self.model_ready:
                class_id, confidence = self.yolov5_classification(cv_image)
            else:
                rospy.logwarn("[WARNING]  Modèle non prêt, classification simulée")
                class_id, confidence = self.mock_classification(cv_image)
            
            class_name = self.class_names[class_id] if 0 <= class_id < len(self.class_names) else 'unknown'
            rospy.loginfo(f"[OK] Classification: classe {class_id} ({class_name}) - confiance: {confidence:.2%}")
            return ClassifyResponse(class_id=class_id, confidence=confidence)
            
        except Exception as e:
            rospy.logerr(f"[ERROR] Erreur classification: {e}")
            import traceback
            rospy.logerr(traceback.format_exc())
            return ClassifyResponse(class_id=-1, confidence=0.0)

    def yolov5_classification(self, image):
        """
        Classification avec YOLOv5
        
        Args:
            image: Image OpenCV BGR (H, W, 3)
            
        Returns:
            class_id: ID de la classe détectée
            confidence: Confiance de la détection (0.0 à 1.0)
        """
        try:
            # Utiliser ultralytics si disponible
            if hasattr(self, 'model') and hasattr(self.model, 'predict'):
                # Mode ultralytics
                results = self.model.predict(image, conf=self.conf_threshold, iou=self.iou_threshold)
                
                if results and len(results) > 0:
                    result = results[0]
                    if result.boxes and len(result.boxes) > 0:
                        # Prendre la meilleure détection
                        best_box = result.boxes[0]
                        class_id = int(best_box.cls.item())
                        confidence = float(best_box.conf.item())
                        return class_id, confidence
            
            # Mode inférence directe (pour PyTorch 1.6.0)
            elif self.model is not None:
                # Prétraitement
                img = cv2.resize(image, (self.img_size, self.img_size))
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img = np.transpose(img, (2, 0, 1))
                img = torch.from_numpy(img).float().to(self.device)
                img = img / 255.0
                img = img.unsqueeze(0)
                
                # Inférence
                with torch.no_grad():
                    outputs = self.model(img)
                    
                    # Pour YOLOv5, les outputs sont généralement [batch, anchors, (x,y,w,h,obj,cls)]
                    # Appliquer une logique simplifiée de post-processing
                    if isinstance(outputs, (list, tuple)):
                        outputs = outputs[0]
                    
                    # Trouver la classe avec la plus haute confiance
                    # Ceci est une simplification - le vrai YOLOv5 fait plus de post-processing
                    batch_size, num_anchors, num_classes_plus_5 = outputs.shape
                    # outputs[..., 4] = objectness, outputs[..., 5:] = class probs
                    
                    # Score final = objectness * class_prob
                    objectness = outputs[..., 4:5]
                    class_probs = outputs[..., 5:]
                    scores = objectness * class_probs
                    
                    # Meilleur score global
                    max_score, max_idx = torch.max(scores.view(batch_size, -1), dim=1)
                    confidence = float(max_score.item())
                    
                    if confidence > self.conf_threshold:
                        # Convertir l'indice global en indices classe
                        anchors_per_class = num_anchors
                        class_id = max_idx.item() // anchors_per_class
                        return class_id, confidence
            
            # Si rien n'a fonctionné
            return -1, 0.0
                
        except Exception as e:
            rospy.logerr(f"[ERROR] Erreur inférence YOLOv5: {e}")
            import traceback
            traceback.print_exc()
            return -1, 0.0

    def mock_classification(self, image):
        """
        Classification simulée pour les tests (quand modèle non disponible)
        Basée sur la couleur moyenne de l'image
        """
        try:
            # Convertir en HSV
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            avg_hue = np.mean(hsv[:,:,0])
            
            # Simuler une classification basée sur la teinte
            if avg_hue < 60:  # Rouge/Orange
                return 0, 0.75  # dangereux
            elif avg_hue < 120:  # Vert
                return 2, 0.80  # recyclables
            else:  # Bleu/autres
                return 1, 0.70  # menagers
                
        except Exception as e:
            rospy.logerr(f"[ERROR] Erreur mock classification: {e}")
            return -1, 0.0

    def test_model(self, test_image_path=None):
        """
        Fonction de test du modèle (sans ROS)
        Utile pour vérifier que le modèle fonctionne correctement
        
        Args:
            test_image_path: Chemin vers une image de test (optionnel)
        """
        if not self.model_ready:
            print("[ERROR] Modèle non prêt, utilisation de la classification simulée")
        
        try:
            # Créer une image de test si aucun chemin fourni
            if test_image_path is None or not os.path.exists(test_image_path):
                print("[CAMERA] Création d'une image de test aléatoire...")
                test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            else:
                print(f"[CAMERA] Chargement de l'image: {test_image_path}")
                test_image = cv2.imread(test_image_path)
                if test_image is None:
                    print(f"[ERROR] Impossible de charger l'image: {test_image_path}")
                    return
            
            # Classifier
            print("[LOADING] Classification en cours...")
            import time
            start_time = time.time()
            
            if self.model_ready:
                class_id, confidence = self.yolov5_classification(test_image)
            else:
                class_id, confidence = self.mock_classification(test_image)
            
            elapsed_time = (time.time() - start_time) * 1000  # ms
            
            # Afficher le résultat
            class_name = self.class_names[class_id] if 0 <= class_id < len(self.class_names) else 'unknown'
            print(f"\n[OK] Résultat:")
            print(f"  [PARAMS] Classe: {class_id} ({class_name})")
            print(f"  [DETECT] Confiance: {confidence:.2%}")
            print(f"  [TIME]  Temps: {elapsed_time:.1f} ms")
            if elapsed_time > 0:
                print(f"  [START] FPS: {1000/elapsed_time:.1f}")
            print()
            
            return class_id, confidence
            
        except Exception as e:
            print(f"[ERROR] Erreur test: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    try:
        # Mode ROS (par défaut)
        if len(sys.argv) == 1:
            print("[START] Démarrage Vision Node (mode ROS)...")
            node = VisionNode()
            rospy.spin()
        
        # Mode test (sans ROS)
        elif sys.argv[1] == '--test':
            print("\n" + "="*60)
            print("[TEST] MODE TEST - Vision Node (sans ROS)")
            print("="*60 + "\n")
            
            # Créer le node sans ROS
            import unittest.mock as mock
            with mock.patch('rospy.init_node'), \
                 mock.patch('rospy.Service'), \
                 mock.patch('rospy.get_param', side_effect=lambda x, default: default), \
                 mock.patch('rospy.loginfo', side_effect=print), \
                 mock.patch('rospy.logerr', side_effect=print), \
                 mock.patch('rospy.logwarn', side_effect=print):
                
                node = VisionNode()
                
                # Tester avec une image si fournie
                test_image_path = sys.argv[2] if len(sys.argv) > 2 else None
                node.test_model(test_image_path)
        
        else:
            print("Usage:")
            print("  python3 vision_node.py              # Mode ROS normal")
            print("  python3 vision_node.py --test       # Mode test sans ROS")
            print("  python3 vision_node.py --test <image_path>  # Tester avec une image")
            
    except Exception as e:
        print(f"[ERROR] Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
import rospy
import cv2
import torch
import numpy as np
import sys
import os
from pathlib import Path
from cv_bridge import CvBridge
from dofbot_tri.srv import Classify, ClassifyResponse
from sensor_msgs.msg import Image

# Ajouter le chemin du framework YOLOv5 au PYTHONPATH
script_dir = Path(__file__).parent.absolute()
models_dir = script_dir.parent.parent / "models"
sys.path.insert(0, str(models_dir))

# Import des utilitaires YOLOv5
try:
    from yolov5.utils.torch_utils import select_device
    from yolov5.models.experimental import attempt_load
    from yolov5.utils.general import non_max_suppression, scale_coords
except ImportError as e:
    rospy.logerr(f"[ERROR] Erreur import YOLOv5: {e}")
    rospy.logerr(f"[FOLDER] Vérifier que models/yolov5/ contient les fichiers nécessaires")

class VisionNode:
    def __init__(self):
        rospy.init_node('vision_node')
        
        # Initialisation de CV Bridge
        self.bridge = CvBridge()
        
        # Chargement des paramètres depuis ROS param server (ou valeurs par défaut)
        self.conf_threshold = rospy.get_param('~conf_threshold', 0.6)
        self.iou_threshold = rospy.get_param('~iou_threshold', 0.45)
        self.img_size = rospy.get_param('~img_size', 640)
        
        # Noms des classes (correspondant au dataset.yaml)
        self.class_names = ['dangereux', 'menagers', 'recyclables']
        
        # Modèle YOLOv5
        self.model = None
        self.device = None
        self.model_ready = False
        
        # Charger le modèle
        self.load_model()
        
        # Service de classification
        self.service = rospy.Service('vision/classify', Classify, self.handle_classify_request)
        
        rospy.loginfo("[OK] Vision Node ready - Service: vision/classify")
        rospy.loginfo(f"[PARAMS] Paramètres: conf={self.conf_threshold}, iou={self.iou_threshold}, img_size={self.img_size}")

    def load_model(self):
        """Charge le modèle YOLOv5m entraîné"""
        try:
            rospy.loginfo("[LOADING] Chargement du modèle YOLOv5...")
            
            # Chemin vers best.pt
            model_path = models_dir / "best.pt"
            
            if not model_path.exists():
                rospy.logerr(f"[ERROR] Modèle introuvable: {model_path}")
                rospy.logerr("[NOTE] Vérifier que best.pt est dans models/")
                return
            
            # Sélectionner le device (CUDA si disponible, sinon CPU)
            self.device = select_device()
            rospy.loginfo(f"[DEVICE]  Device sélectionné: {self.device}")
            
            # Charger le modèle
            self.model = attempt_load(str(model_path), map_location=self.device)
            self.model.eval()
            
            # Vérifier les noms des classes
            model_names = self.model.module.names if hasattr(self.model, 'module') else self.model.names
            rospy.loginfo(f"[CLASSES]  Classes du modèle: {model_names}")
            
            self.model_ready = True
            rospy.loginfo("[OK] Modèle YOLOv5m chargé avec succès")
            rospy.loginfo(f"[SIZE] Taille entrée: {self.img_size}x{self.img_size}")
            
        except Exception as e:
            rospy.logerr(f"[ERROR] Erreur chargement modèle: {e}")
            rospy.logerr("[NOTE] Vérifier l'installation de PyTorch et YOLOv5")
            self.model_ready = False

    def handle_classify_request(self, req):
        """Traite les requêtes de classification d'images"""
        try:
            # Conversion ROS Image → OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(req.image, "bgr8")
            
            # Classification YOLOv5 (ou simulation si modèle non disponible)
            if self.model_ready:
                class_id, confidence = self.yolov5_classification(cv_image)
            else:
                rospy.logwarn("[WARNING]  Modèle non prêt, classification simulée")
                class_id, confidence = self.mock_classification(cv_image)
            
            rospy.loginfo(f"[OK] Classification: classe {class_id} ({self.class_names[class_id] if class_id < len(self.class_names) else 'unknown'}) - confiance: {confidence:.2%}")
            return ClassifyResponse(class_id=class_id, confidence=confidence)
            
        except Exception as e:
            rospy.logerr(f"[ERROR] Erreur classification: {e}")
            import traceback
            rospy.logerr(traceback.format_exc())
            return ClassifyResponse(class_id=-1, confidence=0.0)

    def yolov5_classification(self, image):
        """
        Classification avec YOLOv5
        
        Args:
            image: Image OpenCV BGR (H, W, 3)
            
        Returns:
            class_id: ID de la classe détectée (0=dangereux, 1=menagers, 2=recyclables)
            confidence: Confiance de la détection (0.0 à 1.0)
        """
        try:
            # Redimensionner l'image à la taille d'entrée du modèle
            img = cv2.resize(image, (self.img_size, self.img_size))
            
            # Convertir BGR → RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Transposer (H, W, C) → (C, H, W)
            img = np.transpose(img, (2, 0, 1))
            
            # Convertir en tensor PyTorch
            img = torch.from_numpy(img).to(self.device)
            img = img.float()  # uint8 → float32
            img /= 255.0  # Normalisation [0, 255] → [0.0, 1.0]
            
            # Ajouter dimension batch si nécessaire
            if img.ndimension() == 3:
                img = img.unsqueeze(0)  # (C, H, W) → (1, C, H, W)
            
            # Inférence YOLOv5
            with torch.no_grad():
                pred = self.model(img)[0]
            
            # Appliquer Non-Maximum Suppression (NMS)
            pred = non_max_suppression(
                pred, 
                conf_thres=self.conf_threshold,
                iou_thres=self.iou_threshold
            )
            
            # Traiter les détections
            if pred is not None and len(pred) > 0 and pred[0] is not None:
                det = pred[0]  # Détections pour la première image du batch
                
                if len(det) > 0:
                    # Rescaler les coordonnées de l'image redimensionnée vers l'originale
                    det[:, :4] = scale_coords(img.shape[2:], det[:, :4], image.shape).round()
                    
                    # Prendre la meilleure détection (confiance la plus élevée)
                    best_det = det[0]  # Format: [x1, y1, x2, y2, conf, cls]
                    
                    class_id = int(best_det[5])  # Indice de classe
                    confidence = float(best_det[4])  # Confiance
                    
                    rospy.logdebug(f"[DETECT] Détection: classe {class_id}, conf {confidence:.2%}")
                    
                    return class_id, confidence
                else:
                    rospy.logwarn("[WARNING]  Aucune détection après NMS")
                    return -1, 0.0
            else:
                rospy.logwarn("[WARNING]  Aucune détection YOLOv5")
                return -1, 0.0
                
        except Exception as e:
            rospy.logerr(f"[ERROR] Erreur inférence YOLOv5: {e}")
            import traceback
            rospy.logerr(traceback.format_exc())
            return -1, 0.0

    def mock_classification(self, image):
        """
        Classification simulée pour les tests (quand modèle non disponible)
        Basée sur la couleur moyenne de l'image
        """
        try:
            # Convertir en HSV
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            avg_hue = np.mean(hsv[:,:,0])
            
            # Simuler une classification basée sur la teinte
            if avg_hue < 60:  # Rouge/Orange
                return 0, 0.75  # dangereux
            elif avg_hue < 120:  # Vert
                return 2, 0.80  # recyclables
            else:  # Bleu/autres
                return 1, 0.70  # menagers
                
        except Exception as e:
            rospy.logerr(f"[ERROR] Erreur mock classification: {e}")
            return -1, 0.0

    def test_model(self, test_image_path=None):
        """
        Fonction de test du modèle (sans ROS)
        Utile pour vérifier que le modèle fonctionne correctement
        
        Args:
            test_image_path: Chemin vers une image de test (optionnel)
        """
        if not self.model_ready:
            print("[ERROR] Modèle non prêt, impossible de tester")
            return
        
        try:
            # Créer une image de test si aucun chemin fourni
            if test_image_path is None or not os.path.exists(test_image_path):
                print("[CAMERA] Création d'une image de test aléatoire...")
                test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            else:
                print(f"[CAMERA] Chargement de l'image: {test_image_path}")
                test_image = cv2.imread(test_image_path)
                if test_image is None:
                    print(f"[ERROR] Impossible de charger l'image: {test_image_path}")
                    return
            
            # Classifier
            print("[LOADING] Classification en cours...")
            import time
            start_time = time.time()
            
            class_id, confidence = self.yolov5_classification(test_image)
            
            elapsed_time = (time.time() - start_time) * 1000  # ms
            
            # Afficher le résultat
            print(f"\n[OK] Résultat:")
            print(f"  [PARAMS] Classe: {class_id} ({self.class_names[class_id] if 0 <= class_id < len(self.class_names) else 'unknown'})")
            print(f"  [DETECT] Confiance: {confidence:.2%}")
            print(f"  [TIME]  Temps: {elapsed_time:.1f} ms")
            print(f"  [START] FPS: {1000/elapsed_time:.1f}\n")
            
            return class_id, confidence
            
        except Exception as e:
            print(f"[ERROR] Erreur test: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    try:
        # Mode ROS (par défaut)
        if len(sys.argv) == 1:
            rospy.loginfo("[START] Démarrage Vision Node (mode ROS)...")
            node = VisionNode()
            rospy.spin()
        
        # Mode test (sans ROS)
        elif sys.argv[1] == '--test':
            print("\n" + "="*60)
            print("[TEST] MODE TEST - Vision Node (sans ROS)")
            print("="*60 + "\n")
            
            # Créer le node sans ROS
            import unittest.mock as mock
            with mock.patch('rospy.init_node'), \
                 mock.patch('rospy.Service'), \
                 mock.patch('rospy.get_param', side_effect=lambda x, default: default), \
                 mock.patch('rospy.loginfo', side_effect=print), \
                 mock.patch('rospy.logerr', side_effect=print), \
                 mock.patch('rospy.logwarn', side_effect=print):
                
                node = VisionNode()
                
                # Tester avec une image si fournie
                test_image_path = sys.argv[2] if len(sys.argv) > 2 else None
                node.test_model(test_image_path)
        
        else:
            print("Usage:")
            print("  python3 vision_node.py              # Mode ROS normal")
            print("  python3 vision_node.py --test       # Mode test sans ROS")
            print("  python3 vision_node.py --test <image_path>  # Tester avec une image")
            
    except rospy.ROSInterruptException:
        pass
    except KeyboardInterrupt:
        print("\n[WARNING]  Arrêt demandé par l'utilisateur")
    except Exception as e:
        print(f"[ERROR] Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
