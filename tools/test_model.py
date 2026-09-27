#!/usr/bin/env python3
"""
Script de test du modèle YOLOv5 pour le système de tri DOFbot
Permet de tester le modèle indépendamment du système ROS
"""

import sys
import os
import time
from pathlib import Path

# Ajouter le chemin des modèles au PYTHONPATH
MODEL_DIR = Path(__file__).parent.parent / "models"
sys.path.insert(0, str(MODEL_DIR))

try:
    import torch
    import cv2
    import yaml
    import numpy as np
    from PIL import Image
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("🔧 Installez les dépendances: pip3 install torch opencv-python pyyaml pillow")
    sys.exit(1)


class YOLOv5Tester:
    """Classe pour tester le modèle YOLOv5"""
    
    def __init__(self, weights_path, config_path):
        """Initialiser le testeur
        
        Args:
            weights_path: Chemin vers best.pt
            config_path: Chemin vers dataset.yaml
        """
        self.weights_path = Path(weights_path)
        self.config_path = Path(config_path)
        self.model = None
        self.classes = None
        
        print("🔧 Configuration du testeur YOLOv5...")
        print(f"  📁 Modèle: {self.weights_path}")
        print(f"  📁 Config: {self.config_path}")
        
    def load_model(self):
        """Charger le modèle YOLOv5"""
        print("\n🔄 Chargement du modèle...")
        
        if not self.weights_path.exists():
            print(f"❌ Fichier modèle introuvable: {self.weights_path}")
            return False
        
        try:
            # Charger le modèle
            self.model = torch.hub.load(
                'ultralytics/yolov5',
                'custom',
                path=str(self.weights_path),
                force_reload=False
            )
            
            # Configurer le device
            device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
            self.model.to(device)
            
            print(f"✅ Modèle chargé sur: {device}")
            print(f"  ⚙️  Device: {self.model.device}")
            print(f"  📊 Paramètres: {sum(p.numel() for p in self.model.parameters()) / 1e6:.1f}M")
            
            # Charger les noms des classes
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    self.classes = config.get('names', ['dangereux', 'menagers', 'recyclables'])
            else:
                self.classes = ['dangereux', 'menagers', 'recyclables']
                
            print(f"  🏷️  Classes: {self.classes}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement: {e}")
            return False
    
    def test_inference(self, img_size=640, conf_threshold=0.6):
        """Tester l'inférence sur une image aléatoire
        
        Args:
            img_size: Taille de l'image (640 par défaut)
            conf_threshold: Seuil de confiance
        """
        print(f"\n🧪 Test d'inférence (img_size={img_size}, conf={conf_threshold})...")
        
        # Créer une image aléatoire (simuler une image de caméra)
        test_img = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        try:
            # Configurer le modèle
            self.model.conf = conf_threshold
            self.model.iou = 0.45
            
            # Mesurer le temps d'inférence
            start_time = time.time()
            
            # Inférence
            results = self.model(test_img, size=img_size)
            
            inference_time = (time.time() - start_time) * 1000  # En millisecondes
            
            # Récupérer les détections
            detections = results.pandas().xyxy[0]
            
            print(f"✅ Inférence réussie !")
            print(f"  ⏱️  Temps: {inference_time:.1f} ms")
            print(f"  🎯 Détections: {len(detections)}")
            
            if len(detections) > 0:
                print("\n  📋 Détails des détections:")
                for idx, det in detections.iterrows():
                    class_name = self.classes[int(det['class'])]
                    confidence = det['confidence']
                    print(f"    {idx+1}. {class_name} ({confidence:.2%})")
            else:
                print("  ℹ️  Aucune détection (normal pour image aléatoire)")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'inférence: {e}")
            return False
    
    def test_camera(self, conf_threshold=0.6, num_frames=10):
        """Tester sur images de la caméra (si disponible)
        
        Args:
            conf_threshold: Seuil de confiance
            num_frames: Nombre d'images à tester
        """
        print(f"\n📷 Test avec caméra ({num_frames} frames)...")
        
        try:
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                print("⚠️  Caméra non disponible, test ignoré")
                return False
            
            print("✅ Caméra ouverte")
            print("  📊 Résolution:", int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), "x", int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
            
            self.model.conf = conf_threshold
            
            inference_times = []
            
            for i in range(num_frames):
                ret, frame = cap.read()
                if not ret:
                    print(f"⚠️  Échec lecture frame {i+1}")
                    continue
                
                start_time = time.time()
                results = self.model(frame)
                inference_time = (time.time() - start_time) * 1000
                
                inference_times.append(inference_time)
                
                detections = results.pandas().xyxy[0]
                print(f"  Frame {i+1}/{num_frames}: {inference_time:.1f}ms, {len(detections)} détections")
            
            cap.release()
            
            if inference_times:
                avg_time = np.mean(inference_times)
                print(f"\n📊 Statistiques:")
                print(f"  ⏱️  Temps moyen: {avg_time:.1f} ms")
                print(f"  🚀 FPS moyen: {1000/avg_time:.1f}")
                print(f"  📈 Min/Max: {min(inference_times):.1f} / {max(inference_times):.1f} ms")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur test caméra: {e}")
            return False
    
    def test_batch(self, batch_size=4, img_size=640):
        """Tester l'inférence par batch
        
        Args:
            batch_size: Taille du batch
            img_size: Taille des images
        """
        print(f"\n📦 Test inférence par batch (batch_size={batch_size})...")
        
        # Créer un batch d'images aléatoires
        images = [np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8) for _ in range(batch_size)]
        
        try:
            start_time = time.time()
            results = self.model(images, size=img_size)
            batch_time = (time.time() - start_time) * 1000
            
            time_per_image = batch_time / batch_size
            
            print(f"✅ Inférence batch réussie !")
            print(f"  ⏱️  Temps total: {batch_time:.1f} ms")
            print(f"  ⚡ Temps/image: {time_per_image:.1f} ms")
            print(f"  🚀 FPS: {1000/time_per_image:.1f}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur inférence batch: {e}")
            return False
    
    def run_all_tests(self):
        """Lancer tous les tests"""
        print("\n" + "="*60)
        print("🧪 TESTS DU MODÈLE YOLOv5 - UCAOTECH DOFBOT TRC2025")
        print("="*60)
        
        # Test 1: Chargement
        if not self.load_model():
            print("\n❌ Tests interrompus (échec chargement modèle)")
            return False
        
        # Test 2: Inférence simple
        time.sleep(1)
        if not self.test_inference():
            print("\n⚠️  Test inférence simple échoué")
        
        # Test 3: Caméra (si disponible)
        time.sleep(1)
        self.test_camera(num_frames=5)
        
        # Test 4: Batch
        time.sleep(1)
        if not self.test_batch(batch_size=4):
            print("\n⚠️  Test batch échoué")
        
        print("\n" + "="*60)
        print("✅ TESTS TERMINÉS")
        print("="*60)
        
        return True


def main():
    """Fonction principale"""
    
    # Chemins par défaut (relatifs au script)
    script_dir = Path(__file__).parent.parent
    weights_path = script_dir / "models" / "best.pt"
    config_path = script_dir / "models" / "dataset.yaml"
    
    # Vérifier l'existence des fichiers
    if not weights_path.exists():
        print(f"❌ Modèle introuvable: {weights_path}")
        print("📝 Assurez-vous que best.pt est dans models/")
        return 1
    
    # Créer le testeur
    tester = YOLOv5Tester(weights_path, config_path)
    
    # Lancer les tests
    success = tester.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
