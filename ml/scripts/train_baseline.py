"""
Script d'entraînement avec LES MÊMES paramètres que l'entraînement initial réussi
Adaptation : moins d'epochs car 510 images au lieu de 102
"""

import subprocess
import sys
from pathlib import Path

# MÊMES PARAMÈTRES que garbage_classifier_v1 (qui a réussi)
CONFIG = {
    'epochs': 30,  # Réduit de 100 à 30 car 5× plus d'images (510 vs 102)
    'batch_size': 8,  # IDENTIQUE
    'img_size': 640,  # IDENTIQUE
    'workers': 8,  # IDENTIQUE
    'patience': 25,  # IDENTIQUE
    'cache': None,  # IDENTIQUE (pas de cache)
}

def train_like_original():
    """
    Fine-tuning avec exactement les mêmes paramètres que l'entraînement initial
    """
    print("=" * 70)
    print("🎯 FINE-TUNING - MÊMES PARAMÈTRES QUE L'ENTRAÎNEMENT INITIAL")
    print("=" * 70)
    print(f"Configuration:")
    print(f"  • Epochs: {CONFIG['epochs']} (vs 100 initial, car 5× plus d'images)")
    print(f"  • Batch size: {CONFIG['batch_size']} ✓ IDENTIQUE")
    print(f"  • Image size: {CONFIG['img_size']} ✓ IDENTIQUE")
    print(f"  • Workers: {CONFIG['workers']} ✓ IDENTIQUE")
    print(f"  • Patience: {CONFIG['patience']} ✓ IDENTIQUE")
    print()
    print(f"Dataset:")
    print(f"  • Premier entraînement: 102 images")
    print(f"  • Maintenant: 510 images (5× plus)")
    print()
    print(f"Durée estimée: 4-6 heures")
    print(f"Précision espérée: 89-91%")
    print("=" * 70)
    
    # Chemins
    base_dir = Path(__file__).parent.parent
    yolov5_dir = base_dir / "models" / "yolov5"
    dataset_yaml = base_dir / "data" / "dataset.yaml"
    hyp_yaml = base_dir / "config" / "hyp.yaml"
    weights = base_dir / "models" / "trained_models" / "garbage_classifier_v1" / "weights" / "best.pt"
    
    # Commande YOLOv5 - EXACTEMENT comme l'original
    cmd = [
        sys.executable,
        str(yolov5_dir / "train.py"),
        "--weights", str(weights),
        "--data", str(dataset_yaml),
        "--hyp", str(hyp_yaml),
        "--epochs", str(CONFIG['epochs']),
        "--batch-size", str(CONFIG['batch_size']),
        "--imgsz", str(CONFIG['img_size']),
        "--workers", str(CONFIG['workers']),
        "--project", str(base_dir / "models" / "trained_models"),
        "--name", "garbage_classifier_v2",
        "--exist-ok",
        "--patience", str(CONFIG['patience']),
        # Pas de --cache (comme l'original)
        # Pas de --rect (comme l'original)
    ]
    
    print("\n🏃 Lancement de l'entraînement...")
    print("💡 Configuration identique au modèle initial qui a atteint 97.4% mAP\n")
    
    try:
        subprocess.run(cmd, cwd=str(yolov5_dir), check=True)
        print("\n✅ Entraînement terminé avec succès!")
        print(f"Modèle sauvegardé dans: models/trained_models/garbage_classifier_v2/")
        print("\n📊 Pour tester:")
        print("python scripts/test_on_competition_dataset.py")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Erreur pendant l'entraînement: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Entraînement interrompu par l'utilisateur")
        print("\n💡 Pour reprendre:")
        print("python scripts/train_model_advanced.py --mode resume")
        sys.exit(1)

if __name__ == "__main__":
    train_like_original()
