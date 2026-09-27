# Script de Nettoyage du Projet TRC2025
# Auteur: TRC2025 Team
# Date: 11 octobre 2025

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "   NETTOYAGE DU PROJET TRC2025" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Verifier qu'on est dans le bon dossier
if (!(Test-Path "data") -or !(Test-Path "models") -or !(Test-Path "scripts")) {
    Write-Host "[ERREUR] Ce script doit etre execute depuis le dossier racine du projet!" -ForegroundColor Red
    Write-Host "   Chemin actuel: $(Get-Location)" -ForegroundColor Yellow
    exit 1
}

# Fonction pour calculer la taille
function Get-FolderSize {
    param([string]$Path)
    if (Test-Path $Path) {
        $size = (Get-ChildItem -Path $Path -Recurse -File -ErrorAction SilentlyContinue | 
                 Measure-Object -Property Length -Sum).Sum
        return [math]::Round($size / 1MB, 2)
    }
    return 0
}

# Fonction pour calculer la taille d'un fichier
function Get-FileSize {
    param([string]$Path)
    if (Test-Path $Path) {
        $size = (Get-Item $Path).Length
        return [math]::Round($size / 1MB, 2)
    }
    return 0
}

Write-Host "[ANALYSE] Analyse du projet en cours..." -ForegroundColor Yellow
Write-Host ""

# Liste des fichiers/dossiers a supprimer
$itemsToDelete = @()

# Priorite 1: Fichiers de poids dupliques
if (Test-Path "yolov5m.pt") {
    $size = Get-FileSize "yolov5m.pt"
    $itemsToDelete += [PSCustomObject]@{
        Path = "yolov5m.pt"
        Type = "Fichier"
        Size = $size
        Reason = "Doublon (existe dans models/yolov5/)"
        Priority = "[HAUTE]"
    }
}

if (Test-Path "yolov5s.pt") {
    $size = Get-FileSize "yolov5s.pt"
    $itemsToDelete += [PSCustomObject]@{
        Path = "yolov5s.pt"
        Type = "Fichier"
        Size = $size
        Reason = "Non utilise (vous utilisez yolov5m)"
        Priority = "[HAUTE]"
    }
}

# Priorite 2: Images de test Pixabay
if (Test-Path "data\test_images") {
    $size = Get-FolderSize "data\test_images"
    $count = (Get-ChildItem "data\test_images" -Recurse -File -ErrorAction SilentlyContinue).Count
    $itemsToDelete += [PSCustomObject]@{
        Path = "data\test_images\"
        Type = "Dossier"
        Size = $size
        Reason = "Images Pixabay non representatives ($count images)"
        Priority = "[MOYENNE]"
    }
}

# Priorite 2: Scripts obsoletes
if (Test-Path "scripts\test_model.py") {
    $size = Get-FileSize "scripts\test_model.py"
    $itemsToDelete += [PSCustomObject]@{
        Path = "scripts\test_model.py"
        Type = "Fichier"
        Size = $size
        Reason = "Ancienne version (remplace par test_model_v2.py)"
        Priority = "[MOYENNE]"
    }
}

if (Test-Path "scripts\download_test_images.py") {
    $size = Get-FileSize "scripts\download_test_images.py"
    $itemsToDelete += [PSCustomObject]@{
        Path = "scripts\download_test_images.py"
        Type = "Fichier"
        Size = $size
        Reason = "Script pour images Pixabay (non pertinent)"
        Priority = "[MOYENNE]"
    }
}

# Priorite 3: Fichiers optionnels
if (Test-Path "data\raw_images") {
    $size = Get-FolderSize "data\raw_images"
    $count = (Get-ChildItem "data\raw_images" -Recurse -File -ErrorAction SilentlyContinue).Count
    $itemsToDelete += [PSCustomObject]@{
        Path = "data\raw_images\"
        Type = "Dossier"
        Size = $size
        Reason = "Images brutes ($count images) - deja dans prepared/"
        Priority = "[BASSE]"
    }
}

if (Test-Path "models\trained_models\garbage_classifier_v1\weights\last.pt") {
    $size = Get-FileSize "models\trained_models\garbage_classifier_v1\weights\last.pt"
    $itemsToDelete += [PSCustomObject]@{
        Path = "models\trained_models\garbage_classifier_v1\weights\last.pt"
        Type = "Fichier"
        Size = $size
        Reason = "Checkpoint final (vous gardez best.pt)"
        Priority = "[BASSE]"
    }
}

# Afficher le tableau
if ($itemsToDelete.Count -eq 0) {
    Write-Host "[OK] Aucun fichier a nettoyer detecte!" -ForegroundColor Green
    Write-Host ""
    exit 0
}

Write-Host "[RESULTATS] Fichiers/dossiers a supprimer:" -ForegroundColor Cyan
Write-Host ""
$itemsToDelete | Format-Table -Property Priority, Type, @{Label="Taille (MB)";Expression={$_.Size}}, Path, Reason -AutoSize

$totalSize = ($itemsToDelete | Measure-Object -Property Size -Sum).Sum
Write-Host ""
Write-Host "[ESPACE] Total a liberer: $([math]::Round($totalSize, 2)) MB" -ForegroundColor Yellow
Write-Host ""

# Demander confirmation
Write-Host "[CHOIX] Choisissez une option:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  [1] Nettoyage SAFE (Priorite Haute + Moyenne uniquement)" -ForegroundColor Green
Write-Host "      -> Supprime fichiers dupliques et obsoletes (risque: AUCUN)"
Write-Host ""
Write-Host "  [2] Nettoyage COMPLET (Toutes priorites)" -ForegroundColor Yellow
Write-Host "      -> Supprime aussi raw_images et last.pt (risque: faible)"
Write-Host ""
Write-Host "  [3] ANNULER (ne rien supprimer)" -ForegroundColor Red
Write-Host ""

$choice = Read-Host "Votre choix (1/2/3)"

if ($choice -eq "3" -or $choice -eq "") {
    Write-Host ""
    Write-Host "[ANNULE] Nettoyage annule." -ForegroundColor Yellow
    exit 0
}

# Creer une sauvegarde avant suppression
Write-Host ""
Write-Host "[SAUVEGARDE] Creation d'une sauvegarde de securite..." -ForegroundColor Cyan

$backupFolder = "BACKUP_before_cleanup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $backupFolder -Force | Out-Null

foreach ($item in $itemsToDelete) {
    $sourcePath = $item.Path
    if (Test-Path $sourcePath) {
        $destPath = Join-Path $backupFolder $sourcePath
        $destDir = Split-Path $destPath -Parent
        
        if (!(Test-Path $destDir)) {
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        }
        
        if ($item.Type -eq "Dossier") {
            Copy-Item -Path $sourcePath -Destination $destPath -Recurse -Force -ErrorAction SilentlyContinue
        } else {
            Copy-Item -Path $sourcePath -Destination $destPath -Force -ErrorAction SilentlyContinue
        }
    }
}

Write-Host "[OK] Sauvegarde creee dans: $backupFolder" -ForegroundColor Green
Write-Host ""

# Supprimer les fichiers selon le choix
Write-Host "[SUPPRESSION] Suppression en cours..." -ForegroundColor Yellow
Write-Host ""

$deletedSize = 0
$deletedCount = 0

foreach ($item in $itemsToDelete) {
    # Filtrer selon le choix
    if ($choice -eq "1") {
        # Nettoyage SAFE: uniquement priorite haute et moyenne
        if ($item.Priority -ne "[BASSE]") {
            $shouldDelete = $true
        } else {
            $shouldDelete = $false
        }
    } else {
        # Nettoyage COMPLET: tout supprimer
        $shouldDelete = $true
    }
    
    if ($shouldDelete) {
        $path = $item.Path
        if (Test-Path $path) {
            try {
                if ($item.Type -eq "Dossier") {
                    Remove-Item -Path $path -Recurse -Force
                } else {
                    Remove-Item -Path $path -Force
                }
                Write-Host "  [OK] Supprime: $path" -ForegroundColor Green
                $deletedSize += $item.Size
                $deletedCount++
            } catch {
                Write-Host "  [ERREUR] Erreur lors de la suppression de $path : $_" -ForegroundColor Red
            }
        } else {
            Write-Host "  [INFO] Deja supprime: $path" -ForegroundColor Yellow
        }
    }
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "   NETTOYAGE TERMINE!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "[RESUME] Resultats:" -ForegroundColor Cyan
Write-Host "  - Fichiers/dossiers supprimes: $deletedCount" -ForegroundColor White
Write-Host "  - Espace libere: $([math]::Round($deletedSize, 2)) MB" -ForegroundColor White
Write-Host "  - Sauvegarde: $backupFolder" -ForegroundColor White
Write-Host ""
Write-Host "[CONSEIL] Si tout fonctionne bien, vous pouvez supprimer le dossier de sauvegarde:" -ForegroundColor Yellow
Write-Host "  Remove-Item -Path '$backupFolder' -Recurse -Force" -ForegroundColor Gray
Write-Host ""
Write-Host "[SUIVANT] Prochaine etape: Augmentation du dataset!" -ForegroundColor Cyan
Write-Host "  python scripts/augment_dataset.py --mode mixed" -ForegroundColor White
Write-Host ""
