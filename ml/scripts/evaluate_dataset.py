#!/usr/bin/env python3
"""
Script de Test sur le Dataset RÉEL de la Compétition
====================================================

Ce script teste le modèle sur des images du dataset de compétition
(pas sur des images Pixabay) pour avoir une estimation RÉELLE de la performance.

Auteur: TRC2025 Team
Date: 11 octobre 2025
"""

import torch
from pathlib import Path
import yaml
from collections import defaultdict
import sys

# Configuration des chemins
BASE_DIR = Path(__file__).resolve().parent.parent
YOLOV5_PATH = BASE_DIR / 'models' / 'yolov5'
MODEL_PATH = BASE_DIR / 'models' / 'trained_models' / 'garbage_classifier_v1' / 'weights' / 'best.pt'

# Ajouter YOLOv5 au path
sys.path.insert(0, str(YOLOV5_PATH))

class CompetitionDatasetTester:
    """Testeur sur le dataset réel de la compétition"""
    
    def __init__(self):
        self.model_path = MODEL_PATH
        self.yolov5_path = YOLOV5_PATH
        self.base_dir = BASE_DIR
        
        # Classes de la compétition TRC2025
        self.classes = {
            0: 'dangereux',      # 15 points, -20 si erreur
            1: 'menagers',       # 5 points, -20 si erreur  
            2: 'recyclables'     # 10 points, -20 si erreur
        }
        
        self.results = {
            'dangereux': {'correct': 0, 'total': 0, 'errors': []},
            'menagers': {'correct': 0, 'total': 0, 'errors': []},
            'recyclables': {'correct': 0, 'total': 0, 'errors': []}
        }
        
    def load_model(self):
        """Charge le modèle YOLOv5 entraîné"""
        print("🔄 Chargement du modèle depuis le dépôt local...")
        
        try:
            # Charger depuis le repo local YOLOv5
            self.model = torch.hub.load(
                str(self.yolov5_path),
                'custom',
                path=str(self.model_path),
                source='local',
                force_reload=False
            )
            self.model.conf = 0.25  # Seuil de confiance
            self.model.iou = 0.45   # IoU pour NMS
            
            print("✅ Modèle chargé avec succès!")
            print(f"   📍 Modèle: {self.model_path.name}")
            print(f"   📊 Classes: {list(self.classes.values())}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement du modèle: {e}")
            return False
    
    def get_dataset_info(self):
        """Récupère les informations du dataset"""
        data_yaml = self.base_dir / 'data' / 'dataset.yaml'
        
        if not data_yaml.exists():
            print(f"⚠️  Fichier {data_yaml} introuvable")
            return None
        
        with open(data_yaml, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        return data
    
    def test_on_validation_set(self):
        """Teste sur le set de validation (images jamais vues pendant l'entraînement)"""
        print("\n" + "="*70)
        print("📊 TEST SUR LE SET DE VALIDATION DU DATASET DE COMPÉTITION")
        print("="*70)
        
        # Récupérer le chemin du set de validation
        data_info = self.get_dataset_info()
        if not data_info:
            print("❌ Impossible de charger les informations du dataset")
            return
        
        # Construire le chemin complet
        dataset_path = Path(data_info.get('path', self.base_dir / 'data'))
        val_relative = data_info.get('val', 'prepared/val/images')
        val_path = dataset_path / val_relative
        
        if not val_path.exists():
            print(f"❌ Dossier de validation introuvable: {val_path}")
            print(f"   Vérifiez le chemin dans dataset.yaml")
            return
        
        # Lister toutes les images de validation
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        val_images = []
        for ext in image_extensions:
            val_images.extend(val_path.glob(f'*{ext}'))
        
        if not val_images:
            print(f"⚠️  Aucune image trouvée dans {val_path}")
            return
        
        print(f"\n📁 Dossier de validation: {val_path}")
        print(f"📸 Nombre d'images: {len(val_images)}")
        
        # Charger les labels pour connaître la vérité terrain
        labels_path = Path(str(val_path).replace('images', 'labels'))
        
        print(f"\n🔍 Test en cours...")
        
        correct_predictions = 0
        total_predictions = 0
        class_stats = defaultdict(lambda: {'correct': 0, 'total': 0})
        
        for img_path in val_images:
            # Prédiction
            results = self.model(str(img_path))
            predictions = results.pandas().xyxy[0]
            
            # Charger le label correspondant
            label_file = labels_path / f"{img_path.stem}.txt"
            
            if not label_file.exists():
                continue
            
            with open(label_file, 'r') as f:
                label_lines = f.readlines()
            
            if not label_lines:
                continue
            
            # Extraire la vraie classe (première valeur de la ligne)
            true_class_id = int(label_lines[0].split()[0])
            true_class_name = self.classes[true_class_id]
            
            # Vérifier si la prédiction est correcte
            if len(predictions) > 0:
                pred_class_name = predictions.iloc[0]['name']
                confidence = predictions.iloc[0]['confidence']
                
                total_predictions += 1
                class_stats[true_class_name]['total'] += 1
                
                if pred_class_name == true_class_name:
                    correct_predictions += 1
                    class_stats[true_class_name]['correct'] += 1
                    status = "✅"
                else:
                    status = "❌"
                
                print(f"{status} {img_path.name}: Vrai={true_class_name}, "
                      f"Prédit={pred_class_name} ({confidence:.2%})")
            else:
                print(f"⚠️  {img_path.name}: Aucune détection")
                total_predictions += 1
                class_stats[true_class_name]['total'] += 1
        
        # Afficher les résultats
        self._print_results(correct_predictions, total_predictions, class_stats)
    
    def test_on_sample_images(self, sample_dir):
        """Teste sur un échantillon d'images (pour vérification visuelle)"""
        print("\n" + "="*70)
        print(f"📊 TEST SUR ÉCHANTILLON D'IMAGES: {sample_dir}")
        print("="*70)
        
        sample_path = Path(sample_dir)
        if not sample_path.exists():
            print(f"❌ Dossier introuvable: {sample_path}")
            return
        
        # Tester chaque classe
        for class_name in self.classes.values():
            class_dir = sample_path / class_name
            
            if not class_dir.exists():
                print(f"⚠️  Dossier {class_name} non trouvé")
                continue
            
            images = list(class_dir.glob('*.jpg')) + list(class_dir.glob('*.png'))
            
            if not images:
                print(f"⚠️  Aucune image dans {class_name}")
                continue
            
            print(f"\n📂 Classe: {class_name.upper()} ({len(images)} images)")
            print("-" * 70)
            
            for img_path in images[:5]:  # Afficher max 5 images par classe
                results = self.model(str(img_path))
                predictions = results.pandas().xyxy[0]
                
                if len(predictions) > 0:
                    pred_class = predictions.iloc[0]['name']
                    confidence = predictions.iloc[0]['confidence']
                    
                    if pred_class == class_name:
                        status = "✅ CORRECT"
                        self.results[class_name]['correct'] += 1
                    else:
                        status = f"❌ ERREUR (prédit: {pred_class})"
                        self.results[class_name]['errors'].append(img_path.name)
                    
                    self.results[class_name]['total'] += 1
                    
                    print(f"  {status}")
                    print(f"    📄 {img_path.name}")
                    print(f"    🎯 Confiance: {confidence:.2%}")
                else:
                    print(f"  ⚠️  AUCUNE DÉTECTION - {img_path.name}")
                    self.results[class_name]['total'] += 1
                    self.results[class_name]['errors'].append(img_path.name)
    
    def _print_results(self, correct, total, class_stats):
        """Affiche les résultats détaillés"""
        print("\n" + "="*70)
        print("📊 RÉSULTATS DU TEST")
        print("="*70)
        
        # Résultat global
        accuracy = (correct / total * 100) if total > 0 else 0
        print(f"\n🎯 PRÉCISION GLOBALE: {correct}/{total} = {accuracy:.1f}%")
        
        # Résultats par classe
        print(f"\n📈 DÉTAIL PAR CLASSE:")
        print("-" * 70)
        
        points_data = {
            'dangereux': {'correct_points': 15, 'error_penalty': -20},
            'menagers': {'correct_points': 5, 'error_penalty': -20},
            'recyclables': {'correct_points': 10, 'error_penalty': -20}
        }
        
        total_score = 0
        
        for class_name in self.classes.values():
            stats = class_stats[class_name]
            if stats['total'] > 0:
                class_accuracy = stats['correct'] / stats['total'] * 100
                errors = stats['total'] - stats['correct']
                
                # Calculer le score pour cette classe
                points = points_data[class_name]
                score = (stats['correct'] * points['correct_points']) + \
                        (errors * points['error_penalty'])
                total_score += score
                
                print(f"\n  📦 {class_name.upper()}")
                print(f"     Précision: {stats['correct']}/{stats['total']} = {class_accuracy:.1f}%")
                print(f"     Points: {stats['correct']} × {points['correct_points']} "
                      f"- {errors} × 20 = {score:+d} points")
        
        print("\n" + "="*70)
        print(f"💰 SCORE TOTAL ESTIMÉ (tri uniquement): {total_score:+d} points")
        print("="*70)
        
        # Interprétation
        print("\n📝 INTERPRÉTATION:")
        if accuracy >= 90:
            print("  🏆 EXCELLENT! Modèle prêt pour la compétition!")
        elif accuracy >= 70:
            print("  ✅ BON! Performance compétitive.")
        elif accuracy >= 50:
            print("  ⚠️  MOYEN. Amélioration recommandée.")
        else:
            print("  ❌ FAIBLE. Modèle nécessite optimisation URGENTE.")
        
        if total_score > 0:
            print(f"  💚 Score positif: vous gagnez des points au tri!")
        else:
            print(f"  🔴 Score négatif: trop d'erreurs, stratégie à revoir!")
    
    def run(self, test_type='validation'):
        """Lance le test"""
        print("\n" + "🤖 "*20)
        print("TEST DU MODÈLE SUR DATASET DE COMPÉTITION TRC2025")
        print("🤖 "*20)
        
        # Charger le modèle
        if not self.load_model():
            return
        
        # Afficher les infos du dataset
        data_info = self.get_dataset_info()
        if data_info:
            print(f"\n📋 Informations du dataset:")
            print(f"   Train: {data_info.get('train', 'N/A')}")
            print(f"   Val: {data_info.get('val', 'N/A')}")
            print(f"   Classes: {data_info.get('names', [])}")
        
        # Lancer le test
        if test_type == 'validation':
            self.test_on_validation_set()
        else:
            self.test_on_sample_images(test_type)


def main():
    """Point d'entrée principal"""
    import sys
    
    tester = CompetitionDatasetTester()
    
    if len(sys.argv) > 1:
        # Test sur un dossier spécifique
        test_path = sys.argv[1]
        tester.run(test_type=test_path)
    else:
        # Test sur le set de validation par défaut
        tester.run(test_type='validation')
    
    print("\n✅ Test terminé!")
    print("\n💡 CONSEIL:")
    print("   Si la précision ≥ 90% → Votre modèle est PARFAIT pour la compétition!")
    print("   Si la précision < 70% → Vérifiez que les cubes du jour J sont bien")
    print("                            identiques à ceux du dataset d'entraînement.")


if __name__ == '__main__':
    main()
