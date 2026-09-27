#!/usr/bin/env python3
"""
Script de Test du Modèle sur Images Locales
===========================================

Teste le modèle YOLOv5 entraîné sur les images du dossier 'images/'
avec affichage visuel des résultats et statistiques détaillées.

Auteur: TRC2025 Team
Date: 23 octobre 2025
"""

import sys
import os
from pathlib import Path
import torch
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
import cv2

# Configuration des chemins
BASE_DIR = Path(__file__).parent.parent
MODEL_PATH = BASE_DIR / 'trc2025_train_models' / 'models' / 'trained_models' / 'garbage_classifier_v1' / 'weights' / 'best.pt'
IMAGES_DIR = BASE_DIR / 'images'

# Classes du modèle
CLASSES = {
    0: 'dangereux',
    1: 'menagers',
    2: 'recyclables'
}

# Couleurs pour l'affichage
COLORS = {
    'dangereux': 'red',
    'menagers': 'orange',
    'recyclables': 'green'
}

class ModelTester:
    """Classe pour tester le modèle sur des images locales"""

    def __init__(self):
        self.model = None
        self.results = defaultdict(lambda: {'correct': 0, 'total': 0, 'errors': []})

    def load_model(self):
        """Charge le modèle YOLOv5"""
        print("🔄 Chargement du modèle YOLOv5...")

        if not MODEL_PATH.exists():
            print(f"❌ Modèle introuvable: {MODEL_PATH}")
            print("   Vérifiez que le modèle a été entraîné et sauvegardé.")
            return False

        try:
            # Charger le modèle
            self.model = torch.hub.load(
                'ultralytics/yolov5',
                'custom',
                path=str(MODEL_PATH),
                force_reload=False
            )

            # Configuration
            self.model.conf = 0.25  # Seuil de confiance
            self.model.iou = 0.45   # IoU pour NMS

            print("✅ Modèle chargé avec succès!")
            print(f"   📍 Chemin: {MODEL_PATH}")
            print(f"   📊 Classes: {list(CLASSES.values())}")
            print(f"   ⚙️  Device: {next(self.model.parameters()).device}")

            return True

        except Exception as e:
            print(f"❌ Erreur lors du chargement: {e}")
            return False

    def get_true_class_from_filename(self, filename):
        """Détermine la vraie classe à partir du nom du fichier"""
        filename_lower = filename.lower()

        if filename_lower.startswith('dangereux_'):
            return 'dangereux'
        elif filename_lower.startswith('menagers_'):
            return 'menagers'
        elif filename_lower.startswith('recyclables_'):
            return 'recyclables'
        else:
            return None

    def test_single_image(self, image_path, show_image=False):
        """Teste le modèle sur une seule image"""
        try:
            # Charger l'image
            img = Image.open(image_path)

            # Faire la prédiction
            results = self.model(img)
            predictions = results.pandas().xyxy[0]

            # Déterminer la vraie classe
            true_class = self.get_true_class_from_filename(image_path.name)

            if true_class is None:
                print(f"⚠️  Impossible de déterminer la classe vraie pour: {image_path.name}")
                return None

            # Analyser les prédictions
            if len(predictions) > 0:
                # Prendre la prédiction avec la plus haute confiance
                best_pred = predictions.iloc[0]
                pred_class = best_pred['name']
                confidence = best_pred['confidence']

                # Évaluer la prédiction
                is_correct = (pred_class == true_class)
                status = "✅ CORRECT" if is_correct else "❌ ERREUR"

                # Mettre à jour les statistiques
                self.results[true_class]['total'] += 1
                if is_correct:
                    self.results[true_class]['correct'] += 1
                else:
                    self.results[true_class]['errors'].append({
                        'file': image_path.name,
                        'predicted': pred_class,
                        'confidence': confidence
                    })

                # Afficher le résultat
                color = COLORS.get(true_class, 'blue')
                print(f"  {status} | {image_path.name}")
                print(f"    Vrai: {true_class} | Prédit: {pred_class} | Confiance: {confidence:.1%}")

                # Afficher l'image si demandé
                if show_image:
                    self.show_image_with_prediction(img, predictions, true_class, pred_class, confidence)

                return {
                    'true_class': true_class,
                    'pred_class': pred_class,
                    'confidence': confidence,
                    'correct': is_correct
                }
            else:
                # Aucune détection
                print(f"  ⚠️  AUCUNE DÉTECTION | {image_path.name}")
                print(f"    Vrai: {true_class} | Prédit: (rien)")

                self.results[true_class]['total'] += 1
                self.results[true_class]['errors'].append({
                    'file': image_path.name,
                    'predicted': 'no_detection',
                    'confidence': 0.0
                })

                return None

        except Exception as e:
            print(f"❌ Erreur lors du traitement de {image_path.name}: {e}")
            return None

    def show_image_with_prediction(self, img, predictions, true_class, pred_class, confidence):
        """Affiche l'image avec les prédictions"""
        try:
            # Convertir PIL en numpy array
            img_np = np.array(img)

            # Dessiner les boîtes de détection
            for _, pred in predictions.iterrows():
                x1, y1, x2, y2 = int(pred['xmin']), int(pred['ymin']), int(pred['xmax']), int(pred['ymax'])
                class_name = pred['name']
                conf = pred['confidence']

                # Couleur selon la classe
                color = (0, 255, 0) if class_name == true_class else (0, 0, 255)  # Vert si correct, rouge si erreur

                # Dessiner la boîte
                cv2.rectangle(img_np, (x1, y1), (x2, y2), color, 2)

                # Ajouter le texte
                text = f"{class_name} ({conf:.1%})"
                cv2.putText(img_np, text, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # Afficher l'image
            plt.figure(figsize=(10, 8))
            plt.imshow(img_np)
            plt.title(f"Vrai: {true_class} | Prédit: {pred_class} | Confiance: {confidence:.1%}")
            plt.axis('off')
            plt.show()

        except Exception as e:
            print(f"Erreur lors de l'affichage: {e}")

    def test_all_images(self, show_images=False, max_images=None):
        """Teste le modèle sur toutes les images du dossier"""
        print("\n" + "="*80)
        print("🧪 TEST DU MODÈLE SUR IMAGES LOCALES")
        print("="*80)

        if not IMAGES_DIR.exists():
            print(f"❌ Dossier images introuvable: {IMAGES_DIR}")
            return False

        # Lister toutes les images
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        all_images = []

        for ext in image_extensions:
            all_images.extend(IMAGES_DIR.glob(f'*{ext}'))

        if not all_images:
            print(f"⚠️  Aucune image trouvée dans {IMAGES_DIR}")
            return False

        # Limiter le nombre d'images si demandé
        if max_images:
            all_images = all_images[:max_images]

        print(f"📁 Dossier: {IMAGES_DIR}")
        print(f"📸 Nombre d'images: {len(all_images)}")
        print(f"🎯 Classes attendues: {list(CLASSES.values())}")
        print("\n🔍 Analyse en cours...\n")

        # Tester chaque image
        processed_images = 0

        for image_path in all_images:
            result = self.test_single_image(image_path, show_images)
            if result:
                processed_images += 1

        # Afficher les statistiques finales
        self.print_final_stats()

        return True

    def print_final_stats(self):
        """Affiche les statistiques finales"""
        print("\n" + "="*80)
        print("📊 RÉSULTATS FINAUX")
        print("="*80)

        total_correct = 0
        total_images = 0

        # Statistiques par classe
        print("\n📈 DÉTAIL PAR CLASSE:")
        print("-" * 80)

        for class_name in CLASSES.values():
            stats = self.results[class_name]
            if stats['total'] > 0:
                accuracy = (stats['correct'] / stats['total']) * 100
                errors = len(stats['errors'])

                print(f"\n🎯 {class_name.upper()}")
                print(f"   Précision: {stats['correct']}/{stats['total']} = {accuracy:.1f}%")
                print(f"   Erreurs: {errors}")

                if errors > 0 and errors <= 3:  # Montrer max 3 erreurs par classe
                    print("   ❌ Erreurs détaillées:")
                    for error in stats['errors'][:3]:
                        print(f"      - {error['file']} → {error['predicted']} ({error['confidence']:.1%})")

                total_correct += stats['correct']
                total_images += stats['total']

        # Statistiques globales
        if total_images > 0:
            global_accuracy = (total_correct / total_images) * 100

            print(f"\n🎯 PRÉCISION GLOBALE: {total_correct}/{total_images} = {global_accuracy:.1f}%")

            # Interprétation
            print("\n📝 INTERPRÉTATION:")
            if global_accuracy >= 95:
                print("  🏆 EXCELLENT! Modèle prêt pour la compétition!")
            elif global_accuracy >= 85:
                print("  ✅ TRÈS BON! Performance solide.")
            elif global_accuracy >= 70:
                print("  ⚠️  BON. Quelques ajustements possibles.")
            elif global_accuracy >= 50:
                print("  ⚠️  MOYEN. Amélioration recommandée.")
            else:
                print("  ❌ FAIBLE. Modèle nécessite optimisation URGENTE.")

            # Points de compétition (estimation)
            points_data = {
                'dangereux': {'correct': 15, 'penalty': -20},
                'menagers': {'correct': 5, 'penalty': -20},
                'recyclables': {'correct': 10, 'penalty': -20}
            }

            total_score = 0
            for class_name, stats in self.results.items():
                if stats['total'] > 0:
                    points = points_data[class_name]
                    score = (stats['correct'] * points['correct']) + \
                           ((stats['total'] - stats['correct']) * points['penalty'])
                    total_score += score

            print(f"\n💰 SCORE ESTIMÉ (tri uniquement): {total_score:+d} points")
            if total_score > 0:
                print("  💚 Score positif: stratégie gagnante!")
            else:
                print("  🔴 Score négatif: trop d'erreurs!")

        print("\n" + "="*80)

    def run(self, show_images=False, max_images=None):
        """Lance le test complet"""
        print("🤖 "*15)
        print("TEST DU MODÈLE YOLOv5 SUR IMAGES LOCALES")
        print("TRC2025 - UCAOTECH DOFBOT")
        print("🤖 "*15)

        # Charger le modèle
        if not self.load_model():
            return False

        # Tester toutes les images
        success = self.test_all_images(show_images, max_images)

        if success:
            print("\n✅ Test terminé avec succès!")
            print("\n💡 PROCHAINES ÉTAPES:")
            print("   1. Si précision < 85%: ré-entraînez le modèle")
            print("   2. Testez sur le DOFbot avec des objets réels")
            print("   3. Ajustez les seuils de confiance si nécessaire")
        else:
            print("\n❌ Test échoué!")

        return success


def main():
    """Fonction principale"""
    import argparse

    parser = argparse.ArgumentParser(description='Test du modèle YOLOv5 sur images locales')
    parser.add_argument('--show-images', action='store_true',
                       help='Afficher les images avec les prédictions')
    parser.add_argument('--max-images', type=int,
                       help='Nombre maximum d\'images à tester')
    parser.add_argument('--quick-test', action='store_true',
                       help='Test rapide sur 5 images seulement')

    args = parser.parse_args()

    # Configuration du test
    show_images = args.show_images
    max_images = args.max_images

    if args.quick_test:
        max_images = 5
        print("🚀 MODE TEST RAPIDE: 5 images maximum")

    # Lancer le test
    tester = ModelTester()
    success = tester.run(show_images=show_images, max_images=max_images)

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()