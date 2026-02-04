# Planification Horaire - Configuration

## 🎯 Nouvelles Variables d'Environnement

Le script a été modifié pour supporter une **planification horaire** permettant de limiter l'exécution entre certaines heures.

### Variables de Configuration

| Variable | Type | Défaut | Description |
|----------|------|--------|-------------|
| `START_HOUR` | int (0-23) | 3 | Heure de début d'exécution |
| `END_HOUR` | int (0-23) | 5 | Heure de fin d'exécution |
| `ENABLE_SCHEDULING` | boolean | True | Activer/désactiver la planification |

### Exemple de configuration `.env`

```bash
# ⏰ Paramètres de planification horaire
START_HOUR=3           # Début à 3h00
END_HOUR=5             # Fin à 5h00
ENABLE_SCHEDULING=True # Activer la planification
```

## 📋 Comportement

### Mode Watch (surveillance continue)
- ✅ Entre 3h00 et 4h59 : Les fichiers sont nettoyés
- ❌ À partir de 5h00 : Le script attend sans démarrer de nouveaux nettoyages
- ✅ Continue de traiter les fichiers déjà en cours

### Mode Exécution Unique
- ✅ Entre 3h00 et 4h59 : Le nettoyage s'exécute normalement
- ❌ À partir de 5h00 : Le script refuse de démarrer

### Mode Désactivé
- Si `ENABLE_SCHEDULING=False`, aucune restriction horaire

## 🔄 Fenêtres Spéciales

La logique supporte également les fenêtres traversant minuit :
```bash
START_HOUR=22  # 22h00 (10 PM)
END_HOUR=2     # 2h00 (2 AM le jour suivant)
```

## 📝 Modification du Code

Le script a été modifié aux points suivants :

1. **Import** : `from datetime import datetime`
2. **Variables globales** : Nouvelles variables `START_HOUR`, `END_HOUR`, `ENABLE_SCHEDULING`
3. **Fonctions** :
   - `is_within_execution_window()` : Vérifie si on est dans la fenêtre horaire
   - `can_start_new_process()` : Vérifie si on peut démarrer de nouveaux processus
4. **Mode Watch** : Affichage du statut horaire et mise en pause automatique
5. **Mode Unique** : Refus d'exécution si hors fenêtre horaire
6. **Mode CLI** : Refus de nettoyage si hors fenêtre horaire
