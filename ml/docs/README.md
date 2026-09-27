# 📚 Documentation Projet TRC2025

**Système de tri automatique de déchets avec YOLOv5**  
DOFBot Jetson Nano - TEKBOT Robotics Challenge 2025

---

## 🎯 DOCUMENTS ESSENTIELS

### 🏆 Compétition

**[`GUIDE_TRC2025.md`](GUIDE_TRC2025.md)** - Guide complet compétition  
→ Règles, stratégie, plan d'action, mission bonus  
📖 **Lecture recommandée : 20 minutes**

### 🤖 Déploiement Robot

**[`DEPLOIEMENT_RAPIDE.md`](DEPLOIEMENT_RAPIDE.md)** - Quick start (5 min)  
→ Réponse directe : "Mon dossier models/ doit contenir quoi ?"  
⚡ **START HERE pour déployer**

**[`DEPLOIEMENT_COMPLET.md`](DEPLOIEMENT_COMPLET.md)** - Guide détaillé  
→ Installation complète, code ROS, optimisations  
📖 **Pour comprendre en profondeur : 30 minutes**

### 📊 Projet

**[`PROJET_STATUS.md`](PROJET_STATUS.md)** - État actuel  
→ Performance modèle (85.2%), structure, checklist  
📊 **Vue d'ensemble : 10 minutes**

### 📜 Règles officielles

**[`Manuel de Jeu - TRC25 V3.pdf`](Manuel%20de%20Jeu%20-%20TRC25%20V3.pdf)**  
→ Document officiel TEKBOT

---

## 🗂️ STRUCTURE SIMPLIFIÉE

```
docs/
├── GUIDE_TRC2025.md              🏆 Guide compétition complet
├── DEPLOIEMENT_RAPIDE.md         ⚡ Quick start (5 min)
├── DEPLOIEMENT_COMPLET.md        📖 Guide détaillé (30 min)
├── PROJET_STATUS.md              📊 État du projet
├── Manuel de Jeu - TRC25 V3.pdf  📜 Règles officielles
└── archives/                      📂 Guides techniques
    ├── EXPORT_GUIDE.md           → Export modèle (ONNX, TFLite...)
    ├── GUIDE_AUGMENTATION_DATASET.md → Augmentation données
    └── REENTRAINEMENT_GUIDE.md   → Réentraînement modèle
```

---

## 🚀 PARCOURS RECOMMANDÉS

### 👨‍💻 Développeur - Première découverte

1. [`../README.md`](../README.md) - Vue d'ensemble technique
2. [`PROJET_STATUS.md`](PROJET_STATUS.md) - État actuel
3. [`DEPLOIEMENT_RAPIDE.md`](DEPLOIEMENT_RAPIDE.md) - Déployer rapidement

### 🏁 Compétiteur - Préparer le match

1. [`GUIDE_TRC2025.md`](GUIDE_TRC2025.md) - **Lire en entier** ⭐
2. [`Manuel de Jeu - TRC25 V3.pdf`](Manuel%20de%20Jeu%20-%20TRC25%20V3.pdf) - Règles
3. [`PROJET_STATUS.md`](PROJET_STATUS.md) - Checklist finale

### 🔧 Technicien - Installer sur robot

1. [`DEPLOIEMENT_RAPIDE.md`](DEPLOIEMENT_RAPIDE.md) - Quick start
2. Exécuter `../scripts/prepare_deployment.ps1`
3. [`DEPLOIEMENT_COMPLET.md`](DEPLOIEMENT_COMPLET.md) - Si besoin détails

---

## ❓ QUESTIONS FRÉQUENTES

**Q: Mon dossier models/ sur le robot doit contenir quoi ?**  
→ [`DEPLOIEMENT_RAPIDE.md`](DEPLOIEMENT_RAPIDE.md) - Section "Réponse directe"

**Q: Quelle est la précision du modèle ?**  
→ [`PROJET_STATUS.md`](PROJET_STATUS.md) : **85.2%** (100% classe dangereuse)

**Q: Dois-je réentraîner ?**  
→ [`GUIDE_TRC2025.md`](GUIDE_TRC2025.md) - Section "Plan d'action" : Tester d'abord !

**Q: Combien de points je peux scorer ?**  
→ [`GUIDE_TRC2025.md`](GUIDE_TRC2025.md) - Section "Analyse scoring" : **+220 à +330 pts**

**Q: Comment préparer la compétition ?**  
→ [`GUIDE_TRC2025.md`](GUIDE_TRC2025.md) - **Lire entièrement**

---

## 📊 APERÇU RAPIDE

### Performance actuelle

| Métrique | Valeur | Status |
|----------|--------|--------|
| **Précision validation** | 85.2% | ✅ BON |
| **Classe dangereuse** | 100% | ⭐ PARFAIT |
| **Score estimé** | +220-280 pts | ✅ COMPÉTITIF |

### Prochaines étapes

1. ✅ **Tests physiques** avec cubes imprimés
2. ⏳ Décision réentraînement (si <80%)
3. ⏳ Optimisation vitesse (TensorRT)
4. ⏳ Tests chronométrés complets

**Voir détails :** [`GUIDE_TRC2025.md`](GUIDE_TRC2025.md) - Section "Plan d'action"

---

## 📂 Archives

Les guides techniques d'implémentation sont dans [`archives/`](archives/) :

- **Export modèle** : ONNX, TFLite, TensorRT
- **Augmentation dataset** : Techniques et scripts
- **Réentraînement** : Guide complet fine-tuning

Ces documents sont utiles pour le développement technique mais **pas nécessaires** pour la compétition.

---

## 🎯 DOCUMENTS SUPPRIMÉS

Pour éviter la confusion, les documents redondants ont été archivés ou fusionnés :

- ❌ `INDEX.md` → Remplacé par ce README
- ❌ `STRATEGIE_FINALE_TRC2025.md` → Fusionné dans `GUIDE_TRC2025.md`
- ❌ `ANALYSE_COMPETITION_TRC2025.md` → Fusionné dans `GUIDE_TRC2025.md`
- ❌ `PLAN_ACTION_SUITE.md` → Fusionné dans `GUIDE_TRC2025.md`
- ❌ `MISSION_BONUS_OBJET_INFECTE.md` → Fusionné dans `GUIDE_TRC2025.md`
- ❌ `ARCHITECTURE_DEPLOIEMENT_RESUME.md` → Contenu dans `DEPLOIEMENT_COMPLET.md`

**Résultat :** 10 documents → **5 documents essentiels** ! ✅

---

<div align="center">

## 🏆 OBJECTIF : PODIUM TRC2025 ! 🚀

**Tout est prêt. Il ne reste plus qu'à gagner !**

[🏆 Guide Compétition](GUIDE_TRC2025.md) | [⚡ Déploiement Rapide](DEPLOIEMENT_RAPIDE.md) | [📊 Status Projet](PROJET_STATUS.md)

</div>
