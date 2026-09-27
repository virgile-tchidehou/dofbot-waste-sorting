#!/usr/bin/env python3
"""
Script d'Entraînement Avancé pour TRC2025
==========================================

Modes disponibles:
    - fine-tune : Continue depuis best.pt (85.2%) - RECOMMANDÉ
    - from-scratch : Repart de zéro avec yolov5m.pt
    - resume : Reprend un entraînement interrompu

Auteur: TRC2025 Team
Date: 11 octobre 2025
"""

import sys
from pathlib import Path
import subprocess
import yaml
import argparse

class AdvancedModelTrainer:
    def __init__(self, base_dir="."):
        self.base_dir = Path(base_dir)
        self.yolov5_dir = self.base_dir / "models" / "yolov5"
        self.best_model = self.base_dir / "models" / "trained_models" / "garbage_classifier_v1" / "weights" / "best.pt"
        
    def setup_yolov5(self):
        """Installe YOLOv5"""
        if not self.yolov5_dir.exists():
            print("📥 Clonage de YOLOv5...")
            subprocess.run([
                "git", "clone", "https://github.com/ultralytics/yolov5.git",
                str(self.yolov5_dir)
            ], check=True)
            
            print("📦 Installation des dépendances...")
            subprocess.run([
                "pip", "install", "-r", str(self.yolov5_dir / "requirements.txt")
            ], check=True)
        
        print("✅ YOLOv5 prêt")
    
    def load_config(self):
        """Charge la configuration d'entraînement"""
        config_path = self.base_dir / "config" / "training_config.yaml"
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)['training']
    
    def train(self, mode='fine-tune', epochs=None, name_suffix=''):
        """
        Lance l'entraînement
        
        Args:
            mode: 'fine-tune', 'from-scratch', ou 'resume'
            epochs: Nombre d'epochs (None = utiliser config)
            name_suffix: Suffixe pour le nom du modèle
        """
        config = self.load_config()
        dataset_path = self.base_dir / "data" / "dataset.yaml"
        
        if not dataset_path.exists():
            print("❌ dataset.yaml non trouvé")
            return
        
        # Déterminer les poids de départ
        if mode == 'fine-tune':
            if not self.best_model.exists():
                print(f"❌ Modèle best.pt introuvable: {self.best_model}")
                print("   Utilisez mode 'from-scratch' pour commencer de zéro")
                return
            weights = str(self.best_model)
            training_type = "FINE-TUNING (suite de l'entraînement)"
        elif mode == 'from-scratch':
            weights = f"{config['model']}.pt"
            training_type = "FROM SCRATCH (depuis zéro)"
        elif mode == 'resume':
            last_checkpoint = self.base_dir / "models" / "trained_models" / config['name'] / "weights" / "last.pt"
            if not last_checkpoint.exists():
                print(f"❌ Checkpoint last.pt introuvable: {last_checkpoint}")
                return
            weights = str(last_checkpoint)
            training_type = "RESUME (reprise d'un entraînement interrompu)"
        else:
            print(f"❌ Mode invalide: {mode}")
            return
        
        # Nombre d'epochs
        num_epochs = epochs if epochs else config['epochs']
        
        # Nom du modèle
        if name_suffix:
            model_name = f"{config['name']}_{name_suffix}"
        else:
            if mode == 'fine-tune':
                model_name = f"{config['name']}_finetuned"
            elif mode == 'from-scratch':
                model_name = f"{config['name']}_fromscratch"
            else:
                model_name = config['name']
        
        print("=" * 70)
        print("🚀 ENTRAÎNEMENT DU MODÈLE TRC2025")
        print("=" * 70)
        print(f"Mode: {training_type}")
        print(f"Poids de départ: {Path(weights).name}")
        print(f"Epochs: {num_epochs}")
        print(f"Batch size: {config['batch_size']}")
        print(f"Image size: {config['img_size']}")
        print(f"Nom du modèle: {model_name}")
        print(f"Dataset: {dataset_path}")
        print("=" * 70)
        print()
        
        # Ajouter yolov5 au sys.path pour l'importer
        sys.path.insert(0, str(self.yolov5_dir))
        
        # Chemin vers le fichier hyperparamètres
        hyp_path = self.base_dir / "config" / "hyp.yaml"
        
        cmd = [
            sys.executable, 
            str(self.yolov5_dir / "train.py"),
            "--img", str(config['img_size']),
            "--batch", str(config['batch_size']),
            "--epochs", str(num_epochs),
            "--data", str(dataset_path),
            "--weights", weights,
            "--project", str(self.base_dir / "models" / "trained_models"),
            "--name", model_name,
            "--exist-ok",
            "--patience", str(config['patience'])
        ]
        
        # Ajouter le fichier hyperparamètres si disponible
        if hyp_path.exists():
            cmd.extend(["--hyp", str(hyp_path)])
            print(f"📝 Utilisation des hyperparamètres: {hyp_path}")
        
        print("🏃 Lancement de l'entraînement...")
        print()
        
        try:
            subprocess.run(cmd, check=True)
            print()
            print("=" * 70)
            print("✅ ENTRAÎNEMENT TERMINÉ!")
            print("=" * 70)
            print()
            print("📊 Prochaine étape: Tester le nouveau modèle")
            print(f"   python scripts/test_on_competition_dataset.py")
            print()
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur pendant l'entraînement: {e}")
        except KeyboardInterrupt:
            print()
            print("⏹️  Entraînement interrompu par l'utilisateur")
            print(f"   Pour reprendre: python scripts/train_model_advanced.py --mode resume")

def main():
    parser = argparse.ArgumentParser(description='Entraînement avancé du modèle TRC2025')
    parser.add_argument('--mode', type=str, default='fine-tune',
                       choices=['fine-tune', 'from-scratch', 'resume'],
                       help='Mode d\'entraînement (défaut: fine-tune)')
    parser.add_argument('--epochs', type=int, default=None,
                       help='Nombre d\'epochs (défaut: valeur du config)')
    parser.add_argument('--name-suffix', type=str, default='',
                       help='Suffixe pour le nom du modèle')
    
    args = parser.parse_args()
    
    # Afficher les recommandations
    print()
    if args.mode == 'fine-tune':
        print("✅ MODE RECOMMANDÉ: Fine-tuning")
        print("   Part de votre modèle actuel (85.2%) et l'améliore")
        print("   Temps estimé: 2-3h pour 50 epochs")
        print("   Gain attendu: 85.2% → 90-93%")
    elif args.mode == 'from-scratch':
        print("⚠️  MODE AVANCÉ: From Scratch")
        print("   Repart de zéro avec yolov5m pré-entraîné")
        print("   Temps estimé: 6-8h pour 100 epochs")
        print("   Gain attendu: 80-92% (incertain)")
    elif args.mode == 'resume':
        print("🔄 MODE REPRISE: Resume")
        print("   Reprend un entraînement interrompu")
    print()
    
    # Créer le trainer
    trainer = AdvancedModelTrainer()
    trainer.setup_yolov5()
    trainer.train(mode=args.mode, epochs=args.epochs, name_suffix=args.name_suffix)

if __name__ == "__main__":
    main()
