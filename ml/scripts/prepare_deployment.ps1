# Script PowerShell pour préparer le package de déploiement vers Jetson Nano
# Usage: .\prepare_deployment.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PRÉPARATION PACKAGE DÉPLOIEMENT" -ForegroundColor Cyan
Write-Host "  Robot DOFBot Jetson Nano" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$PROJECT_ROOT = $PSScriptRoot + "\.."
$DEPLOY_DIR = "$PROJECT_ROOT\deploy_to_robot"
$MODEL_PATH = "$PROJECT_ROOT\models\trained_models\garbage_classifier_v1\weights\best.pt"
$DATASET_YAML = "$PROJECT_ROOT\data\dataset.yaml"
$YOLOV5_PATH = "$PROJECT_ROOT\models\yolov5"

# Vérifier que les fichiers existent
Write-Host "[1/6] Vérification des fichiers source..." -ForegroundColor Yellow

if (-not (Test-Path $MODEL_PATH)) {
    Write-Host "❌ ERREUR: Modèle best.pt introuvable!" -ForegroundColor Red
    Write-Host "   Cherché dans: $MODEL_PATH" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $DATASET_YAML)) {
    Write-Host "❌ ERREUR: dataset.yaml introuvable!" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $YOLOV5_PATH)) {
    Write-Host "❌ ERREUR: Dossier yolov5 introuvable!" -ForegroundColor Red
    exit 1
}

Write-Host "   ✅ Tous les fichiers source trouvés" -ForegroundColor Green
Write-Host ""

# Créer le dossier de déploiement
Write-Host "[2/6] Création du dossier de déploiement..." -ForegroundColor Yellow

if (Test-Path $DEPLOY_DIR) {
    Write-Host "   ⚠️  Le dossier existe déjà, suppression..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $DEPLOY_DIR
}

New-Item -ItemType Directory -Path $DEPLOY_DIR | Out-Null
New-Item -ItemType Directory -Path "$DEPLOY_DIR\yolov5" | Out-Null
New-Item -ItemType Directory -Path "$DEPLOY_DIR\yolov5\models" | Out-Null
New-Item -ItemType Directory -Path "$DEPLOY_DIR\yolov5\utils" | Out-Null
New-Item -ItemType Directory -Path "$DEPLOY_DIR\v1" | Out-Null

Write-Host "   ✅ Structure créée" -ForegroundColor Green
Write-Host ""

# Copier le modèle principal
Write-Host "[3/6] Copie du modèle best.pt..." -ForegroundColor Yellow
Copy-Item $MODEL_PATH "$DEPLOY_DIR\best.pt"
$modelSize = (Get-Item "$DEPLOY_DIR\best.pt").Length / 1MB
Write-Host "   ✅ best.pt copié ($([math]::Round($modelSize, 2)) MB)" -ForegroundColor Green
Write-Host ""

# Copier dataset.yaml
Write-Host "[4/6] Copie de dataset.yaml..." -ForegroundColor Yellow
Copy-Item $DATASET_YAML "$DEPLOY_DIR\dataset.yaml"
Write-Host "   ✅ dataset.yaml copié" -ForegroundColor Green
Write-Host ""

# Copier les fichiers YOLOv5 essentiels
Write-Host "[5/6] Copie des fichiers YOLOv5 essentiels..." -ForegroundColor Yellow

# __init__.py
if (Test-Path "$YOLOV5_PATH\__init__.py") {
    Copy-Item "$YOLOV5_PATH\__init__.py" "$DEPLOY_DIR\yolov5\__init__.py"
} else {
    # Créer un __init__.py vide
    New-Item -ItemType File -Path "$DEPLOY_DIR\yolov5\__init__.py" | Out-Null
}

# Dossier models/
$yolov5_models_files = @(
    "common.py",
    "yolo.py",
    "experimental.py",
    "__init__.py"
)

foreach ($file in $yolov5_models_files) {
    $sourcePath = "$YOLOV5_PATH\models\$file"
    if (Test-Path $sourcePath) {
        Copy-Item $sourcePath "$DEPLOY_DIR\yolov5\models\$file"
        Write-Host "   ✅ models/$file" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  models/$file non trouvé (peut être optionnel)" -ForegroundColor Yellow
    }
}

# Dossier utils/
$yolov5_utils_files = @(
    "__init__.py",
    "general.py",
    "torch_utils.py",
    "augmentations.py",
    "dataloaders.py",
    "plots.py",
    "metrics.py",
    "callbacks.py"
)

foreach ($file in $yolov5_utils_files) {
    $sourcePath = "$YOLOV5_PATH\utils\$file"
    if (Test-Path $sourcePath) {
        Copy-Item $sourcePath "$DEPLOY_DIR\yolov5\utils\$file"
        Write-Host "   ✅ utils/$file" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  utils/$file non trouvé (peut être optionnel)" -ForegroundColor Yellow
    }
}

Write-Host ""

# Copier fichiers optionnels pour backup
Write-Host "[6/6] Copie des fichiers optionnels (backup)..." -ForegroundColor Yellow

$optionalFiles = @{
    "hyp.yaml" = "$PROJECT_ROOT\models\trained_models\garbage_classifier_v1\hyp.yaml"
    "opt.yaml" = "$PROJECT_ROOT\models\trained_models\garbage_classifier_v1\opt.yaml"
    "results.png" = "$PROJECT_ROOT\models\trained_models\garbage_classifier_v1\results.png"
}

foreach ($fileName in $optionalFiles.Keys) {
    $sourcePath = $optionalFiles[$fileName]
    if (Test-Path $sourcePath) {
        Copy-Item $sourcePath "$DEPLOY_DIR\v1\$fileName"
        Write-Host "   ✅ v1/$fileName" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  $fileName non trouvé (optionnel)" -ForegroundColor Yellow
    }
}

Write-Host ""

# Créer un README pour le package
Write-Host "Création du README de déploiement..." -ForegroundColor Yellow

$readmeContent = @"
# Package de déploiement - Modèle YOLOv5 TRC2025

**Date de création:** $(Get-Date -Format "dd/MM/yyyy HH:mm")
**Version modèle:** v1 (85.2% accuracy)

## Contenu du package

### Fichiers essentiels (OBLIGATOIRES)
- ``best.pt`` (40.6 MB) - Modèle YOLOv5 entraîné
- ``dataset.yaml`` - Configuration des classes
- ``yolov5/models/`` - Architectures réseau YOLOv5
- ``yolov5/utils/`` - Utilitaires YOLOv5

### Fichiers optionnels (pour backup)
- ``v1/hyp.yaml`` - Hyperparamètres d'entraînement
- ``v1/opt.yaml`` - Options d'entraînement
- ``v1/results.png`` - Graphiques de performance

## Installation sur Jetson Nano

### 1. Transférer le package
``````bash
# Via SCP (remplacer <JETSON_IP> par l'IP du Jetson)
scp -r deploy_to_robot/* jetson@<JETSON_IP>:~/transfer/
``````

### 2. Installer sur le robot
``````bash
# SSH vers le Jetson
ssh jetson@<JETSON_IP>

# Créer la structure
cd ~/catkin_ws/src/dofbot_tri/
mkdir -p models/yolov5/models
mkdir -p models/yolov5/utils
mkdir -p models/v1

# Copier les fichiers
cp ~/transfer/best.pt models/best.pt
cp ~/transfer/dataset.yaml models/dataset.yaml
cp -r ~/transfer/yolov5/models/* models/yolov5/models/
cp -r ~/transfer/yolov5/utils/* models/yolov5/utils/
cp ~/transfer/yolov5/__init__.py models/yolov5/__init__.py
cp ~/transfer/v1/* models/v1/ 2>/dev/null || true

# Vérifier
ls -lh models/best.pt
tree models/ -L 2
``````

### 3. Tester le chargement
``````bash
cd ~/catkin_ws/src/dofbot_tri/models/
python3 << EOF
import torch
model = torch.hub.load('yolov5', 'custom', path='best.pt', source='local')
print(f"✅ Modèle chargé: {model.names}")
EOF
``````

## Structure finale sur robot

``````
~/catkin_ws/src/dofbot_tri/models/
├── best.pt                    (40.6 MB)
├── dataset.yaml              (1 KB)
├── yolov5/
│   ├── __init__.py
│   ├── models/
│   │   ├── common.py
│   │   ├── yolo.py
│   │   └── experimental.py
│   └── utils/
│       ├── general.py
│       ├── torch_utils.py
│       ├── augmentations.py
│       └── dataloaders.py
└── v1/
    ├── hyp.yaml
    ├── opt.yaml
    └── results.png
``````

## Performances

- **Accuracy validation:** 85.2% (23/27 images)
- **Classe dangereuse:** 100% (9/9) ⭐
- **Classe ménagers:** 77.8% (7/9)
- **Classe recyclables:** 77.8% (7/9)
- **Score estimé:** +160 points

## Documentation complète

Voir: ``docs/DEPLOIEMENT_ROBOT_JETSON.md`` dans le projet principal

## Support

En cas de problème:
1. Vérifier taille best.pt (~40.6 MB)
2. Vérifier PYTHONPATH inclut yolov5
3. Consulter ``docs/DEPLOIEMENT_ROBOT_JETSON.md``
"@

Set-Content -Path "$DEPLOY_DIR\README.md" -Value $readmeContent -Encoding UTF8
Write-Host "   ✅ README.md créé" -ForegroundColor Green
Write-Host ""

# Calculer la taille totale
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RÉSUMÉ DU PACKAGE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$totalSize = (Get-ChildItem -Recurse $DEPLOY_DIR | Measure-Object -Property Length -Sum).Sum / 1MB
$fileCount = (Get-ChildItem -Recurse $DEPLOY_DIR -File).Count

Write-Host ""
Write-Host "📦 Package créé avec succès !" -ForegroundColor Green
Write-Host ""
Write-Host "📂 Emplacement: $DEPLOY_DIR" -ForegroundColor Cyan
Write-Host "📊 Taille totale: $([math]::Round($totalSize, 2)) MB" -ForegroundColor Cyan
Write-Host "📄 Nombre de fichiers: $fileCount" -ForegroundColor Cyan
Write-Host ""

# Lister les fichiers principaux
Write-Host "📋 Contenu principal:" -ForegroundColor Yellow
Get-ChildItem $DEPLOY_DIR -File | ForEach-Object {
    $size = $_.Length / 1MB
    Write-Host "   - $($_.Name) ($([math]::Round($size, 2)) MB)" -ForegroundColor White
}
Write-Host ""

# Proposer de créer une archive
Write-Host "========================================" -ForegroundColor Cyan
$createZip = Read-Host "Créer une archive ZIP pour transfert facile? (O/N)"

if ($createZip -eq "O" -or $createZip -eq "o") {
    Write-Host ""
    Write-Host "Création de l'archive..." -ForegroundColor Yellow
    
    $zipPath = "$PROJECT_ROOT\deploy_to_robot.zip"
    
    if (Test-Path $zipPath) {
        Remove-Item $zipPath -Force
    }
    
    Compress-Archive -Path "$DEPLOY_DIR\*" -DestinationPath $zipPath
    
    $zipSize = (Get-Item $zipPath).Length / 1MB
    
    Write-Host "✅ Archive créée: deploy_to_robot.zip ($([math]::Round($zipSize, 2)) MB)" -ForegroundColor Green
    Write-Host ""
    Write-Host "📤 Transfert via SCP:" -ForegroundColor Cyan
    Write-Host "   scp deploy_to_robot.zip jetson@<JETSON_IP>:~/transfer.zip" -ForegroundColor White
    Write-Host ""
    Write-Host "📦 Extraction sur Jetson:" -ForegroundColor Cyan
    Write-Host "   unzip ~/transfer.zip -d ~/transfer/" -ForegroundColor White
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ PRÉPARATION TERMINÉE !" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📚 Prochaines étapes:" -ForegroundColor Yellow
Write-Host "   1. Transférer le package vers le Jetson Nano" -ForegroundColor White
Write-Host "   2. Suivre les instructions dans README.md" -ForegroundColor White
Write-Host "   3. Consulter docs/DEPLOIEMENT_ROBOT_JETSON.md" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Bonne chance pour TRC2025 !" -ForegroundColor Green
Write-Host ""
