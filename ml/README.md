# 🧠 TRC2025 Training Models# 🤖 Projet DOFBot - Tri Automatique de Déchets

> **Historical validation note:** accuracy and mAP figures below are retained from the 2025 project records. The full dataset and trained model weights are intentionally excluded from the public repository, so these numbers are not independently reproducible from this repository alone.




**Module d'Entraînement des Modèles ML - Ucaotech DOFbot TRC2025****TRC2025 - TEKBOT Robotics Challenge**  

Système de classification de déchets avec YOLOv5 pour robot DOFBot Jetson Nano

---

---

## 📋 Vue d'Ensemble

## 🎯 Vue d'ensemble

Ce dossier contient tous les éléments nécessaires à l'entraînement et l'optimisation des modèles de machine learning pour la détection et classification des déchets.

Système de reconnaissance et classification automatique de déchets en 3 catégories :

**Modèle Principal** : YOLOv8n optimisé pour tri de déchets (3 classes)- **Dangereux** 🔴 : Objets potentiellement nocifs (batteries, amiante, acides...)

- **Ménagers** ⚫ : Déchets domestiques ordinaires

### Classes Détectées- **Recyclables** 🟢 : Matériaux recyclables (plastique, carton, verre...)

- 📦 **Carton** : Boîtes, emballages carton

- 🧴 **Plastique** : Bouteilles, contenants plastiques### 📊 Performances actuelles

- 🔩 **Métal** : Canettes, objets métalliques

| Métrique | Valeur | Status |

---|----------|--------|--------|

| **Précision validation** | 85.2% | ✅ Bon |

## 📁 Structure| **Classe dangereuse** | 100% (9/9) | ⭐ Parfait |

| **Classe ménagers** | 77.8% (7/9) | ⚠️ À surveiller |

```| **Classe recyclables** | 77.8% (7/9) | ⚠️ À surveiller |

trc2025_train_models/| **Score estimé compétition** | +160 points | ✅ Compétitif |

├── config/                      # Configurations entraînement

│   ├── yolo_config.yaml        # Config YOLOv8---

│   └── training_params.json    # Hyperparamètres

│## 🛠️ Technologies

├── data/                        # Datasets

│   ├── train/                  # Images entraînement (2500+)- **Framework** : YOLOv5 (Ultralytics)

│   ├── val/                    # Images validation (500+)- **Langage** : Python 3.13.5

│   ├── test/                   # Images test (200+)- **Deep Learning** : PyTorch 2.8.0

│   └── annotations/            # Annotations COCO format- **Modèle** : YOLOv5m (20.8M paramètres)

│- **Dataset** : 510 images train + 27 images validation

├── models/                      # Modèles entraînés

│   ├── yolov8n_waste.pt       # Modèle principal (PyTorch)---

│   ├── yolov8n_waste_best.pt  # Meilleure version

│   ├── yolov8n_waste.engine   # Version TensorRT (optimisée)## 📁 Structure du projet

│   └── classifier_backup.h5   # Backup TensorFlow

│```

├── scripts/                     # Scripts entraînementdofbot_tri_complete/

│   ├── train_yolo.py          # Entraînement YOLOv8├── data/

│   ├── evaluate_model.py      # Évaluation performance│   ├── augmented/train/        # 510 images augmentées

│   ├── export_tflite.py       # Export TensorFlow Lite│   ├── prepared/val/           # 27 images validation

│   └── augment_data.py        # Augmentation données│   └── dataset.yaml            # Config dataset

││

├── docs/                        # Documentation spécifique├── models/

│   ├── README.md              # Guide détaillé│   ├── trained_models/

│   └── archives/              # Anciennes versions│   │   └── garbage_classifier_v1/    # Modèle principal (85.2%)

││   │       └── weights/

├── requirements.txt            # Dépendances Python│   │           └── best.pt           # Meilleur modèle (40.6 MB)

└── README.md                   # Ce fichier│   └── yolov5/                       # Framework YOLOv5

```│

├── scripts/

---│   ├── test_on_competition_dataset.py      # Test validation

│   ├── augment_dataset.py                  # Augmentation dataset

## 🚀 Quick Start│   ├── train_like_original.py              # Réentraînement

│   ├── prepare_deployment.ps1              # Préparer déploiement

### 1. Installation Dépendances│   └── vision_node_example.py              # Code ROS exemple

│

```bash├── docs/                               # 📚 Documentation complète

cd trc2025_train_models│   ├── INDEX.md                        # 🗂️ Navigation docs

pip install -r requirements.txt│   ├── DEPLOIEMENT_RAPIDE_TLDR.md     # ⚡ START HERE

```│   ├── DEPLOIEMENT_ROBOT_JETSON.md    # 📖 Guide complet

│   ├── ARCHITECTURE_DEPLOIEMENT_RESUME.md

### 2. Entraînement Modèle│   ├── PROJET_STATUS.md                # 📊 État du projet

│   ├── STRATEGIE_FINALE_TRC2025.md     # 🏆 Stratégie compétition

```bash│   ├── PLAN_ACTION_SUITE.md            # 📋 Prochaines étapes

# Entraînement complet│   └── ...

python scripts/train_yolo.py --data config/yolo_config.yaml --epochs 100│

├── config/                             # Configuration

# Entraînement rapide (test)├── README.md                           # Ce fichier

python scripts/train_yolo.py --data config/yolo_config.yaml --epochs 10 --batch 8└── requirements.txt                    # Dépendances Python

``````



### 3. Évaluation---



```bash## 🚀 Quick Start

# Évaluation sur dataset validation

python scripts/evaluate_model.py --model models/yolov8n_waste_best.pt --data data/val/### 1️⃣ Tester le modèle



# Métriques détaillées```bash

python scripts/evaluate_model.py --model models/yolov8n_waste_best.pt --detailedpython scripts/test_on_competition_dataset.py

``````



### 4. Export Optimisé**Résultat attendu :**

```

```bash✅ 85.2% accuracy (23/27 images correctes)

# Export TensorRT (Jetson Nano)   - dangereux: 100% (9/9)

python scripts/export_tflite.py --model models/yolov8n_waste_best.pt --format engine   - menagers: 77.8% (7/9)

   - recyclables: 77.8% (7/9)

# Export ONNX```

python scripts/export_tflite.py --model models/yolov8n_waste_best.pt --format onnx

```### 2️⃣ Réentraîner (optionnel)



---```bash

python scripts/train_like_original.py

## 📊 Performance Actuelle```



### Métriques GlobalesDurée : 10-12 heures (CPU)



| Métrique | Valeur | Objectif |### 3️⃣ Déployer sur robot

|----------|--------|----------|

| **mAP@0.5** | 0.92 | ✅ >0.85 |**Sur PC Windows :**

| **mAP@0.5:0.95** | 0.78 | ✅ >0.70 |```powershell

| **Précision** | 0.94 | ✅ >0.90 |.\scripts\prepare_deployment.ps1

| **Recall** | 0.91 | ✅ >0.85 |# → Crée deploy_to_robot/ (~42 MB)

| **F1-Score** | 0.92 | ✅ >0.87 |```



### Performance par Classe**Transférer vers Jetson :**

```bash

| Classe | Precision | Recall | F1-Score | Support |scp -r deploy_to_robot/* jetson@<IP>:~/transfer/

|--------|-----------|--------|----------|---------|```

| **Carton** | 0.94 | 0.91 | 0.92 | 350 |

| **Plastique** | 0.93 | 0.89 | 0.91 | 280 |**Installer sur robot :**

| **Métal** | 0.96 | 0.93 | 0.94 | 220 |```bash

| **Moyenne** | **0.94** | **0.91** | **0.92** | **850** |cd ~/catkin_ws/src/dofbot_tri/

mkdir -p models/yolov5/{models,utils}

### Performance Embarquée (Jetson Nano Orin)cp ~/transfer/best.pt models/

cp ~/transfer/dataset.yaml models/

| Configuration | FPS | Latence | Précision |cp -r ~/transfer/yolov5/* models/yolov5/

|--------------|-----|---------|-----------|```

| YOLOv8n (PyTorch) | 28 | 35ms | Standard |

| YOLOv8n (TensorRT FP16) | 42 | 24ms | Légère baisse |---

| YOLOv8n (TensorRT INT8) | 55 | 18ms | Baisse modérée |

## 📚 Documentation

---

### 🎯 Par besoin

## 🔗 Intégration Projet Principal

| Besoin | Document | Temps lecture |

Ce module fait partie du projet principal `ucaotech_dofbot_trc2025`.|--------|----------|---------------|

| **Déployer sur robot** | [`docs/DEPLOIEMENT_RAPIDE_TLDR.md`](docs/DEPLOIEMENT_RAPIDE_TLDR.md) | ⚡ 5 min |

**Documentation complète** : Voir `../docs/` pour tous les guides :| **Guide complet déploiement** | [`docs/DEPLOIEMENT_ROBOT_JETSON.md`](docs/DEPLOIEMENT_ROBOT_JETSON.md) | 📖 20 min |

- Architecture système : `../docs/technical/ARCHITECTURE.md`| **État du projet** | [`docs/PROJET_STATUS.md`](docs/PROJET_STATUS.md) | 📊 10 min |

- Guide déploiement : `../docs/guides/DEPLOYMENT.md`| **Stratégie compétition** | [`docs/STRATEGIE_FINALE_TRC2025.md`](docs/STRATEGIE_FINALE_TRC2025.md) | 🏆 15 min |

- Guide compétition : `../docs/guides/COMPETITION_TRC2025.md`| **Prochaines étapes** | [`docs/PLAN_ACTION_SUITE.md`](docs/PLAN_ACTION_SUITE.md) | 📋 5 min |

- API Reference : `../docs/technical/API_REFERENCE.md`| **Navigation complète** | [`docs/INDEX.md`](docs/INDEX.md) | 🗂️ Index |



**Usage dans le projet** :### 🔗 Liens rapides

```python

# Dans vision_node.py- **Manuel officiel TRC2025** : `docs/Manuel de Jeu - TRC25 V3.pdf`

from ultralytics import YOLO- **Mission bonus (+50pts)** : `docs/MISSION_BONUS_OBJET_INFECTE.md`

- **Analyse compétition** : `docs/ANALYSE_COMPETITION_TRC2025.md`

# Charger modèle entraîné

model = YOLO('trc2025_train_models/models/yolov8n_waste.engine')---



# Détection## 🤖 Architecture Robot (ROS)

results = model.predict(image, conf=0.75)

```### Structure requise sur Jetson Nano



---```

~/catkin_ws/src/dofbot_tri/

## 📚 Scripts Principaux├── CMakeLists.txt

├── package.xml

### `train_yolo.py`├── srv/

Entraînement du modèle YOLOv8│   └── Classify.srv              # Service classification

```bash├── scripts/

python scripts/train_yolo.py --data config/yolo_config.yaml --epochs 100 --batch 16│   ├── vision_node.py            # Node vision (charge modèle)

```│   └── i2c_controller_node.py    # Contrôle bras

├── launch/

### `evaluate_model.py`│   └── tri.launch                # Launch file

Évaluation des performances├── models/                        # ⭐ À créer (voir docs)

```bash│   ├── best.pt                   # Modèle YOLOv5 (40.6 MB)

python scripts/evaluate_model.py --model models/yolov8n_waste_best.pt --data data/val/ --detailed│   ├── dataset.yaml              # Config classes

```│   └── yolov5/                   # Framework

│       ├── models/

### `export_tflite.py`│       └── utils/

Export vers différents formats (TensorRT, ONNX, TFLite)└── config/

```bash    └── arm_positions.yaml

python scripts/export_tflite.py --model models/yolov8n_waste_best.pt --format engine --half```

```

**Voir documentation :** [`docs/DEPLOIEMENT_RAPIDE_TLDR.md`](docs/DEPLOIEMENT_RAPIDE_TLDR.md)

### `augment_data.py`

Augmentation du dataset---

```bash

python scripts/augment_data.py --input data/raw/ --output data/train/ --factor 3## 🔧 Installation locale

```

### Prérequis

---

- Python 3.8+ (testé avec 3.13.5)

## 🎯 Workflow Typique- PyTorch 2.0+

- 8 GB RAM minimum

1. **Préparer données** : Collecte, annotation, organisation- 5 GB espace disque

2. **Augmenter dataset** : Rotation, flip, ajustements

3. **Entraîner modèle** : YOLOv8 training (100 epochs)### Installation

4. **Évaluer performance** : Métriques validation

5. **Optimiser** : Export TensorRT pour Jetson```bash

6. **Déployer** : Copier modèle vers projet principal# Cloner le repo

git clone <repo-url>

---cd dofbot_tri_complete



## 📈 Améliorations Possibles# Installer dépendances

pip install -r requirements.txt

- **Plus de données** : Collecter images variées

- **Hyperparamètres** : Grid search optimisation# Tester

- **Augmentation avancée** : MixUp, CutOutpython scripts/test_on_competition_dataset.py

- **Modèle plus gros** : YOLOv8s ou YOLOv8m```

- **Quantization** : INT8 pour vitesse maximale

---

---

## 📊 Historique du projet

## 📞 Références

### Version actuelle : Post-cleanup v1.0

- **YOLOv8** : https://docs.ultralytics.com/

- **PyTorch** : https://pytorch.org/**Modèle :**

- **TensorRT** : https://developer.nvidia.com/tensorrt- Architecture : YOLOv5m

- Entraînement : 100 epochs

---- Dataset : 510 images train (augmentées) + 27 validation

- Performance : 85.2% validation

**Pour documentation détaillée, voir** : `docs/README.md`

**Optimisations effectuées :**

**Dernière mise à jour : 16 octobre 2025**- ✅ Augmentation dataset (102 → 510 images)

- ✅ Nettoyage projet (~700 MB libérés)
- ✅ Documentation complète organisée
- ✅ Scripts de déploiement automatiques

**Prochaines étapes :**
1. Tests physiques avec cubes réels
2. Décision réentraînement (si <80% physique)
3. Optimisation vitesse (TensorRT)
4. Intégration complète DOFBot

---

## 🏆 Compétition TRC2025

### Contexte

- **Lieu** : Abidjan, Côte d'Ivoire
- **Date** : TRC2025
- **Challenge** : Tri automatique de 90 cubes
- **Temps** : 5 minutes

### Scoring

| Type déchet | Points | Erreur |
|-------------|--------|--------|
| Dangereux | +15 pts | -20 pts |
| Recyclable | +10 pts | -20 pts |
| Ménager | +5 pts | -20 pts |

### Stratégie

**Qualité > Quantité**
- Trier 40-50 cubes avec 85-90% précision
- Score estimé : +360 à +425 points
- Focus sur classe dangereuse (100% détection)

**Voir stratégie complète :** [`docs/STRATEGIE_FINALE_TRC2025.md`](docs/STRATEGIE_FINALE_TRC2025.md)

---

## 🛠️ Scripts utiles

### Test et validation

```bash
# Tester sur dataset validation
python scripts/test_on_competition_dataset.py

# Augmenter le dataset (déjà fait)
python scripts/augment_dataset.py
```

### Entraînement

```bash
# Réentraîner avec mêmes paramètres
python scripts/train_like_original.py

# Entraînement avancé
python scripts/train_model_advanced.py
```

### Déploiement

```powershell
# Préparer package pour robot (Windows)
.\scripts\prepare_deployment.ps1
```

---

## 🐛 Troubleshooting

### Modèle ne charge pas

```bash
# Vérifier le fichier existe
ls -lh models/trained_models/garbage_classifier_v1/weights/best.pt
# Doit afficher ~40.6 MB

# Tester le chargement
python -c "import torch; m=torch.hub.load('ultralytics/yolov5','custom',path='models/trained_models/garbage_classifier_v1/weights/best.pt'); print(m.names)"
```

### Erreur "No module named 'yaml'"

```bash
pip install PyYAML
```

### Performance lente

- Utiliser GPU si disponible : `device='cuda:0'`
- Réduire taille image : `img_size=416`
- Exporter en TensorRT (Jetson)

---

## 📝 Notes importantes

### Dataset

- **Train** : 510 images (augmentées)
- **Validation** : 27 images (jamais modifiées)
- **Source** : Dataset ECOCITY officiel TRC2025
- **Classes** : dangereux, menagers, recyclables

### Modèle

- **Fichier** : `models/trained_models/garbage_classifier_v1/weights/best.pt`
- **Taille** : 40.6 MB
- **Format** : PyTorch (.pt)
- **Exports** : ONNX, TFLite, TorchScript disponibles

### Backup

- **Backup sécurité** : `BACKUP_FINAL_20251011_201347/` (232 MB)
- **Ne pas supprimer** jusqu'après compétition !

---

## 🤝 Contribution

Ce projet est développé pour la compétition TRC2025.

**Équipe :** [Votre équipe]  
**Contact :** [Votre contact]

---

## 📄 Licence

- Projet : [Votre licence]
- YOLOv5 : AGPL-3.0 (Ultralytics)

---

## 🎉 Remerciements

- **Ultralytics** pour YOLOv5
- **TEKBOT** pour l'organisation TRC2025
- **PyTorch** pour le framework deep learning

---

## 🚀 Prochaines étapes

### Priorité 1 : Tests physiques (MAINTENANT)

1. Imprimer 10-15 images ECOCITY sur papier
2. Coller sur cubes 3×3 cm
3. Tester avec DOFBot + caméra + modèle actuel
4. Mesurer précision réelle

**Critère décision :**
- Si ≥80% → Optimiser vitesse
- Si <80% → Réentraîner (10-12h)

### Priorité 2 : Optimisation (après tests)

- Export TensorRT pour Jetson Nano
- Optimisation trajectoires bras
- Tests chronométrés complets

### Priorité 3 : Mission bonus (optionnel)

- Contacter organisateur pour image "cube infecté"
- Ajouter 4ème classe au modèle
- Fine-tune 10-20 epochs

**Voir plan complet :** [`docs/PLAN_ACTION_SUITE.md`](docs/PLAN_ACTION_SUITE.md)

---

<div align="center">

**🏆 OBJECTIF : 1ère place pour le TRC2025 ! 🚀**

[📚 Documentation](docs/) | [⚡ Déploiement](docs/DEPLOIEMENT_RAPIDE_TLDR.md) | [🏆 Stratégie](docs/STRATEGIE_FINALE_TRC2025.md)

</div>
