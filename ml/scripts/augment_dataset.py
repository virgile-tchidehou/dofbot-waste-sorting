#!/usr/bin/env python3
"""
Script d'Augmentation du Dataset pour TRC2025
==============================================

Ce script augmente intelligemment le dataset d'entraînement pour améliorer
la précision du modèle de 85.2% à 91-93%.

Modes disponibles:
    - targeted : Augmentation intensive des 4 images problématiques (×15)
    - global   : Augmentation légère de toutes les images (×5)
    - mixed    : Combinaison optimale (recommandé)

Auteur: TRC2025 Team
Date: 11 octobre 2025
"""

import cv2
import numpy as np
from pathlib import Path
import shutil
import argparse
from tqdm import tqdm
import random

# Configuration des chemins
BASE_DIR = Path(__file__).resolve().parent.parent
TRAIN_IMAGES = BASE_DIR / 'data' / 'prepared' / 'train' / 'images'
TRAIN_LABELS = BASE_DIR / 'data' / 'prepared' / 'train' / 'labels'
AUGMENTED_DIR = BASE_DIR / 'data' / 'augmented'

# Images problématiques identifiées lors du test de validation
PROBLEMATIC_IMAGES = [
    'menagers_bidon_eau_5L.jpg',
    'menagers_gobelet_glace.jpg',
    'recyclables_canette_alu_propre.jpg',
    'recyclables_verre_restaurant.jpg'
]


class DatasetAugmenter:
    """Classe pour l'augmentation intelligente du dataset"""
    
    def __init__(self, mode='mixed', targeted_multiplier=15, global_multiplier=2):
        self.mode = mode
        self.targeted_multiplier = targeted_multiplier
        self.global_multiplier = global_multiplier
        
        # Créer les dossiers de sortie
        self.output_images = AUGMENTED_DIR / 'train' / 'images'
        self.output_labels = AUGMENTED_DIR / 'train' / 'labels'
        self.output_images.mkdir(parents=True, exist_ok=True)
        self.output_labels.mkdir(parents=True, exist_ok=True)
        
        print("=" * 70)
        print("AUGMENTATION DU DATASET TRC2025")
        print("=" * 70)
        print(f"Mode: {mode}")
        print(f"Images d'entraînement source: {TRAIN_IMAGES}")
        print(f"Dossier de sortie: {AUGMENTED_DIR}")
        print()
    
    def rotate_image(self, image, angle):
        """Rotation de l'image"""
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, matrix, (w, h), 
                                 borderMode=cv2.BORDER_REFLECT)
        return rotated
    
    def adjust_brightness(self, image, factor):
        """Ajustement de la luminosité"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 2] = hsv[:, :, 2] * factor
        hsv[:, :, 2] = np.clip(hsv[:, :, 2], 0, 255)
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    
    def adjust_contrast(self, image, factor):
        """Ajustement du contraste"""
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB).astype(np.float32)
        lab[:, :, 0] = lab[:, :, 0] * factor
        lab[:, :, 0] = np.clip(lab[:, :, 0], 0, 255)
        return cv2.cvtColor(lab.astype(np.uint8), cv2.COLOR_LAB2BGR)
    
    def add_gaussian_blur(self, image, sigma):
        """Ajout d'un flou gaussien léger"""
        ksize = int(sigma * 6) | 1  # Taille impaire
        return cv2.GaussianBlur(image, (ksize, ksize), sigma)
    
    def add_shadow(self, image):
        """Simulation d'ombre"""
        h, w = image.shape[:2]
        shadow = np.zeros((h, w), dtype=np.uint8)
        
        # Créer une forme d'ombre aléatoire
        x1, y1 = random.randint(0, w//2), random.randint(0, h//2)
        x2, y2 = random.randint(w//2, w), random.randint(h//2, h)
        cv2.rectangle(shadow, (x1, y1), (x2, y2), 255, -1)
        shadow = cv2.GaussianBlur(shadow, (51, 51), 30)
        
        # Appliquer l'ombre
        shadow = shadow[:, :, np.newaxis] / 255.0
        shadowed = image * (0.7 + 0.3 * shadow)
        return shadowed.astype(np.uint8)
    
    def zoom_image(self, image, factor):
        """Zoom sur l'image"""
        h, w = image.shape[:2]
        new_h, new_w = int(h * factor), int(w * factor)
        
        # Redimensionner
        resized = cv2.resize(image, (new_w, new_h))
        
        # Crop au centre pour revenir à la taille originale
        start_y = (new_h - h) // 2
        start_x = (new_w - w) // 2
        
        if factor > 1:  # Zoom in
            cropped = resized[start_y:start_y + h, start_x:start_x + w]
        else:  # Zoom out
            cropped = np.zeros((h, w, 3), dtype=np.uint8)
            cropped[start_y:start_y + new_h, start_x:start_x + new_w] = resized
        
        return cropped
    
    def get_augmentations(self, intensive=False):
        """Retourne la liste des augmentations à appliquer"""
        if intensive:
            # Augmentations intensives pour images problématiques
            return [
                ('original', lambda img: img),
                ('flip_h', lambda img: cv2.flip(img, 1)),
                ('rot_m15', lambda img: self.rotate_image(img, -15)),
                ('rot_m10', lambda img: self.rotate_image(img, -10)),
                ('rot_m5', lambda img: self.rotate_image(img, -5)),
                ('rot_p5', lambda img: self.rotate_image(img, 5)),
                ('rot_p10', lambda img: self.rotate_image(img, 10)),
                ('rot_p15', lambda img: self.rotate_image(img, 15)),
                ('bright_m20', lambda img: self.adjust_brightness(img, 0.8)),
                ('bright_m10', lambda img: self.adjust_brightness(img, 0.9)),
                ('bright_p10', lambda img: self.adjust_brightness(img, 1.1)),
                ('bright_p20', lambda img: self.adjust_brightness(img, 1.2)),
                ('contrast_m15', lambda img: self.adjust_contrast(img, 0.85)),
                ('contrast_p15', lambda img: self.adjust_contrast(img, 1.15)),
                ('blur_05', lambda img: self.add_gaussian_blur(img, 0.5)),
            ]
        else:
            # Augmentations légères pour le reste
            return [
                ('original', lambda img: img),
                ('flip_h', lambda img: cv2.flip(img, 1)),
                ('rot_m10', lambda img: self.rotate_image(img, -10)),
                ('rot_p10', lambda img: self.rotate_image(img, 10)),
                ('bright_p10', lambda img: self.adjust_brightness(img, 1.1)),
            ]
    
    def augment_image(self, image_path, label_path, is_problematic=False):
        """Augmente une image avec ses transformations"""
        # Lire l'image
        image = cv2.imread(str(image_path))
        if image is None:
            print(f"[ERREUR] Impossible de lire {image_path}")
            return 0
        
        # Lire le label
        if label_path.exists():
            with open(label_path, 'r') as f:
                label_content = f.read()
        else:
            print(f"[ATTENTION] Label introuvable pour {image_path}")
            return 0
        
        # Déterminer les augmentations
        intensive = is_problematic and self.mode in ['targeted', 'mixed']
        augmentations = self.get_augmentations(intensive=intensive)
        
        # Appliquer les augmentations
        count = 0
        base_name = image_path.stem
        
        for aug_name, aug_func in augmentations:
            try:
                # Appliquer la transformation
                augmented = aug_func(image)
                
                # Nom du fichier de sortie
                if aug_name == 'original':
                    output_name = base_name
                else:
                    output_name = f"{base_name}_{aug_name}"
                
                # Sauvegarder l'image augmentée
                output_image_path = self.output_images / f"{output_name}.jpg"
                cv2.imwrite(str(output_image_path), augmented)
                
                # Copier le label (les bounding boxes restent les mêmes)
                output_label_path = self.output_labels / f"{output_name}.txt"
                with open(output_label_path, 'w') as f:
                    f.write(label_content)
                
                count += 1
            except Exception as e:
                print(f"[ERREUR] Augmentation {aug_name} échouée pour {image_path}: {e}")
        
        return count
    
    def run(self):
        """Exécute l'augmentation selon le mode choisi"""
        print(f"[ANALYSE] Scan des images d'entraînement...")
        
        # Lister toutes les images
        train_images = list(TRAIN_IMAGES.glob('*.jpg')) + list(TRAIN_IMAGES.glob('*.png'))
        
        if not train_images:
            print(f"[ERREUR] Aucune image trouvée dans {TRAIN_IMAGES}")
            return
        
        print(f"[INFO] {len(train_images)} images d'entraînement trouvées")
        print()
        
        # Statistiques
        total_augmented = 0
        problematic_count = 0
        normal_count = 0
        
        # Traiter chaque image
        for image_path in tqdm(train_images, desc="Augmentation en cours"):
            label_path = TRAIN_LABELS / f"{image_path.stem}.txt"
            
            # Vérifier si c'est une image problématique
            is_problematic = image_path.name in PROBLEMATIC_IMAGES
            
            # Décider si on augmente cette image
            should_augment = False
            
            if self.mode == 'targeted':
                should_augment = is_problematic
            elif self.mode == 'global':
                should_augment = True
            elif self.mode == 'mixed':
                should_augment = True
            
            if should_augment:
                count = self.augment_image(image_path, label_path, is_problematic)
                total_augmented += count
                
                if is_problematic:
                    problematic_count += count
                else:
                    normal_count += count
        
        # Résumé
        print()
        print("=" * 70)
        print("AUGMENTATION TERMINÉE!")
        print("=" * 70)
        print(f"Images originales: {len(train_images)}")
        print(f"Images augmentées (problématiques): {problematic_count}")
        print(f"Images augmentées (normales): {normal_count}")
        print(f"Total d'images générées: {total_augmented}")
        print(f"Dossier de sortie: {AUGMENTED_DIR}")
        print()
        print("[SUIVANT] Étapes suivantes:")
        print("  1. Vérifier visuellement quelques images augmentées")
        print("  2. Mettre à jour dataset.yaml pour pointer vers data/augmented")
        print("  3. Réentraîner le modèle:")
        print("     python scripts/train_model.py config/training_config.yaml --epochs 50")
        print()


def update_dataset_yaml():
    """Met à jour dataset.yaml pour utiliser le dataset augmenté"""
    dataset_yaml = BASE_DIR / 'data' / 'dataset.yaml'
    
    # Créer une copie de sauvegarde
    backup_yaml = BASE_DIR / 'data' / 'dataset_backup.yaml'
    if dataset_yaml.exists():
        shutil.copy(dataset_yaml, backup_yaml)
        print(f"[SAUVEGARDE] dataset.yaml sauvegardé dans {backup_yaml}")
    
    # Mettre à jour le contenu
    new_content = f"""path: {BASE_DIR / 'data'}
train: augmented/train/images
val: prepared/val/images
nc: 3
names:
- dangereux
- menagers
- recyclables
"""
    
    with open(dataset_yaml, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"[OK] dataset.yaml mis à jour!")
    print(f"     Train: augmented/train/images")
    print(f"     Val: prepared/val/images (inchangé)")
    print()


def visualize_samples():
    """Affiche quelques exemples d'images augmentées"""
    print("[INFO] Pour visualiser les images augmentées:")
    print("  import cv2")
    print("  from pathlib import Path")
    print("  images = list(Path('data/augmented/train/images').glob('*.jpg'))[:5]")
    print("  for img_path in images:")
    print("      img = cv2.imread(str(img_path))")
    print("      cv2.imshow(img_path.name, img)")
    print("  cv2.waitKey(0)")
    print()


def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(description='Augmentation du dataset TRC2025')
    parser.add_argument('--mode', type=str, default='mixed',
                       choices=['targeted', 'global', 'mixed'],
                       help='Mode d\'augmentation (défaut: mixed)')
    parser.add_argument('--targeted-multiplier', type=int, default=15,
                       help='Facteur de multiplication pour images problématiques')
    parser.add_argument('--global-multiplier', type=int, default=5,
                       help='Facteur de multiplication pour toutes les images')
    parser.add_argument('--update-yaml', action='store_true',
                       help='Mettre à jour dataset.yaml automatiquement')
    
    args = parser.parse_args()
    
    # Créer l'augmenteur
    augmenter = DatasetAugmenter(
        mode=args.mode,
        targeted_multiplier=args.targeted_multiplier,
        global_multiplier=args.global_multiplier
    )
    
    # Exécuter l'augmentation
    augmenter.run()
    
    # Mettre à jour dataset.yaml si demandé
    if args.update_yaml:
        update_dataset_yaml()
    else:
        print("[INFO] Pour mettre à jour dataset.yaml automatiquement:")
        print("  python scripts/augment_dataset.py --mode mixed --update-yaml")
        print()


if __name__ == '__main__':
    main()
