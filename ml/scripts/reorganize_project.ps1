# Script de nettoyage et reorganisation complete du projet TRC2025
# Execute avec PowerShell

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  NETTOYAGE ET REORGANISATION PROJET TRC  " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Confirmation utilisateur
$confirmation = Read-Host "Voulez-vous continuer avec le nettoyage? (oui/non)"
if ($confirmation -ne "oui") {
    Write-Host "Operation annulee." -ForegroundColor Yellow
    exit
}

# Variables
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = "BACKUP_FINAL_$timestamp"
$baseDir = Get-Location

Write-Host ""
Write-Host "=== ETAPE 1: CREATION BACKUP ===" -ForegroundColor Green
Write-Host "Creation du backup dans: $backupDir"

# Creer backup (sauf models/yolov5 qui est trop gros)
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
Copy-Item -Path "data" -Destination "$backupDir/data" -Recurse -Force
Copy-Item -Path "scripts" -Destination "$backupDir/scripts" -Recurse -Force
Copy-Item -Path "*.md" -Destination "$backupDir/" -Force
Copy-Item -Path "*.pdf" -Destination "$backupDir/" -Force -ErrorAction SilentlyContinue

Write-Host "[OK] Backup cree" -ForegroundColor Green

Write-Host ""
Write-Host "=== ETAPE 2: CREATION NOUVELLE STRUCTURE ===" -ForegroundColor Green

# Creer dossier docs
if (-not (Test-Path "docs")) {
    New-Item -ItemType Directory -Path "docs" -Force | Out-Null
    Write-Host "[OK] Dossier docs/ cree" -ForegroundColor Green
} else {
    Write-Host "[INFO] Dossier docs/ existe deja" -ForegroundColor Yellow
}

# Creer dossier archives
if (-not (Test-Path "docs/archives")) {
    New-Item -ItemType Directory -Path "docs/archives" -Force | Out-Null
    Write-Host "[OK] Dossier docs/archives/ cree" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== ETAPE 3: DEPLACEMENT DOCUMENTATION ===" -ForegroundColor Green

# Deplacer documents strategiques vers docs/
$docsStrategiques = @(
    "STRATEGIE_FINALE_TRC2025.md",
    "MISSION_BONUS_OBJET_INFECTE.md",
    "PLAN_ACTION_SUITE.md",
    "ANALYSE_COMPETITION_TRC2025.md",
    "Manuel de Jeu - TRC25 V3.pdf"
)

foreach ($doc in $docsStrategiques) {
    if (Test-Path $doc) {
        Move-Item -Path $doc -Destination "docs/" -Force
        Write-Host "[OK] Deplace: $doc" -ForegroundColor Green
    }
}

# Deplacer anciens guides vers archives/
$docsArchives = @(
    "GUIDE_AUGMENTATION_DATASET.md",
    "REENTRAINEMENT_GUIDE.md",
    "GUIDE_DOWNLOAD_IMAGES.md",
    "EXPORT_GUIDE.md",
    "ANALYSE_NETTOYAGE_PROJET.md",
    "STRATEGIE_MISSIONS_BONUS.md",
    "PLAN_NETTOYAGE_COMPLET.md"
)

foreach ($doc in $docsArchives) {
    if (Test-Path $doc) {
        Move-Item -Path $doc -Destination "docs/archives/" -Force
        Write-Host "[OK] Archive: $doc" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "=== ETAPE 4: SUPPRESSION FICHIERS OBSOLETES ===" -ForegroundColor Green

# Supprimer data obsoletes
$dataObsoletes = @(
    "data/raw_images",
    "data/prepared/train",
    "data/dataset_backup.yaml"
)

foreach ($item in $dataObsoletes) {
    if (Test-Path $item) {
        Remove-Item -Path $item -Recurse -Force
        Write-Host "[OK] Supprime: $item" -ForegroundColor Green
    } else {
        Write-Host "[INFO] Deja supprime: $item" -ForegroundColor Yellow
    }
}

# Supprimer scripts obsoletes
$scriptsObsoletes = @(
    "scripts/train_model.py",
    "scripts/test_model_v2.py",
    "scripts/data_preparation.py",
    "scripts/train_fast_cpu.py",
    "scripts/export_model.py"
)

foreach ($script in $scriptsObsoletes) {
    if (Test-Path $script) {
        Remove-Item -Path $script -Force
        Write-Host "[OK] Supprime: $script" -ForegroundColor Green
    }
}

# Supprimer vieux backups
$oldBackups = Get-ChildItem -Directory -Filter "BACKUP_before_cleanup_*"
foreach ($backup in $oldBackups) {
    Remove-Item -Path $backup.FullName -Recurse -Force
    Write-Host "[OK] Supprime vieux backup: $($backup.Name)" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== ETAPE 5: CREATION .gitignore ===" -ForegroundColor Green

# Creer .gitignore
$gitignoreContent = @"
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
*.egg-info/
dist/
build/

# YOLOv5
runs/
wandb/
*.pt
*.onnx
*.engine

# Data (trop gros pour Git)
data/augmented/
data/prepared/
data/raw_images/

# Models (trop gros pour Git)
models/yolov5/
models/trained_models/

# Backups
BACKUP_*/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
"@

Set-Content -Path ".gitignore" -Value $gitignoreContent
Write-Host "[OK] .gitignore cree" -ForegroundColor Green

Write-Host ""
Write-Host "=== ETAPE 6: CREATION README STRUCTURE ===" -ForegroundColor Green

# Ajouter section structure au README
$readmeAddition = @"


## 📁 Structure du Projet

``````
dofbot_tri_complete/
├── config/                      # Configuration YOLOv5
├── data/
│   ├── augmented/              # Dataset augmenté (510 images)
│   ├── prepared/val/           # Validation (27 images)
│   └── dataset.yaml            # Config dataset
├── models/
│   ├── trained_models/
│   │   └── garbage_classifier_v1/  # Modèle principal (85.2%)
│   ├── yolov5/                 # Framework YOLOv5
│   └── class_names.json
├── scripts/
│   ├── test_on_competition_dataset.py   # Test validation
│   ├── augment_dataset.py               # Augmentation
│   ├── train_model_advanced.py          # Entraînement
│   └── train_like_original.py           # Réentraînement
├── docs/                        # Documentation
│   ├── STRATEGIE_FINALE_TRC2025.md
│   ├── MISSION_BONUS_OBJET_INFECTE.md
│   ├── PLAN_ACTION_SUITE.md
│   └── archives/               # Anciens guides
├── README.md
└── requirements.txt
``````

## 🚀 Quick Start

1. **Tester le modèle actuel:**
   ``````bash
   python scripts/test_on_competition_dataset.py
   ``````

2. **Réentraîner si nécessaire:**
   ``````bash
   python scripts/train_like_original.py
   ``````

3. **Voir la stratégie complète:**
   Lire `docs/STRATEGIE_FINALE_TRC2025.md`
"@

# Ajouter au README (à la fin)
Add-Content -Path "README.md" -Value $readmeAddition
Write-Host "[OK] README mis a jour" -ForegroundColor Green

Write-Host ""
Write-Host "=== ETAPE 7: CALCUL ESPACE LIBERE ===" -ForegroundColor Green

# Calculer taille backup
$backupSize = (Get-ChildItem -Path $backupDir -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "         NETTOYAGE TERMINE !               " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "RESUME:" -ForegroundColor White
Write-Host "  - Backup cree: $backupDir" -ForegroundColor Green
Write-Host "  - Taille backup: $([math]::Round($backupSize, 2)) MB" -ForegroundColor Green
Write-Host "  - Documentation organisee dans: docs/" -ForegroundColor Green
Write-Host "  - Scripts nettoyes (4 essentiels gardes)" -ForegroundColor Green
Write-Host "  - .gitignore cree" -ForegroundColor Green
Write-Host "  - README mis a jour" -ForegroundColor Green
Write-Host ""
Write-Host "STRUCTURE FINALE:" -ForegroundColor White
Write-Host "  dofbot_tri_complete/" -ForegroundColor Cyan
Write-Host "  ├── config/" -ForegroundColor White
Write-Host "  ├── data/" -ForegroundColor White
Write-Host "  ├── models/" -ForegroundColor White
Write-Host "  ├── scripts/ (4 fichiers)" -ForegroundColor White
Write-Host "  ├── docs/ (documentation organisee)" -ForegroundColor White
Write-Host "  ├── README.md" -ForegroundColor White
Write-Host "  └── requirements.txt" -ForegroundColor White
Write-Host ""
Write-Host "PROCHAINES ETAPES:" -ForegroundColor Yellow
Write-Host "  1. Verifier que tout fonctionne:" -ForegroundColor White
Write-Host "     python scripts/test_on_competition_dataset.py" -ForegroundColor Gray
Write-Host "  2. Si OK, supprimer le backup:" -ForegroundColor White
Write-Host "     Remove-Item -Path $backupDir -Recurse -Force" -ForegroundColor Gray
Write-Host "  3. Lire: docs/PLAN_ACTION_SUITE.md" -ForegroundColor White
Write-Host ""
Write-Host "Projet propre et organise ! Pret pour la suite." -ForegroundColor Green
Write-Host ""
