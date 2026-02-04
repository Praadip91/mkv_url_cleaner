# MKV URL Cleaner 🧼

Script Python pour nettoyer automatiquement les métadonnées des fichiers MKV (suppression des noms de sites, titres, etc.).

## 🎯 Fonctionnalités

- ✅ Nettoyage automatique des métadonnées MKV
- ✅ Mode surveillance continue (watch mode)
- ✅ Planification horaire (ex: 3h à 5h du matin)
- ✅ Suppression des noms de domaines aux pistes audio
- ✅ Suppression des titres globaux
- ✅ Support multi-dossiers
- ✅ Suivi des fichiers déjà nettoyés
- ✅ Conteneurisation Docker

## 🚀 Déploiement Rapide avec Docker

### Via Docker Compose

```bash
# Exemple .env pour déploiement (multi-dossiers)
cat > .env << EOF
# Racine contenant vos dossiers sources (montée dans le conteneur)
SOURCE_ROOT=/media

# Liste JSON des dossiers source (paths absolus sur l'hôte, montés sous SOURCE_ROOT)
# Exemple: '["/media/folder1", "/media/folder2"]'
SOURCE_FOLDERS='["/media/folder1","/media/folder2"]'

# Emplacement hôte pour stocker cleanfile.txt (persistant)
CLEANFILE_HOST_DIR=/docker/mkv_url_cleaner_daniel

WATCH_MODE=True
WATCH_INTERVAL=60
START_HOUR=3
END_HOUR=5
ENABLE_SCHEDULING=True
EOF

docker compose up -d
```

### Via Portainer

1. **Allez dans Portainer** → `Stacks` → `Add Stack`
2. **Sélectionnez** `Docker Compose`
3. **Collez le contenu** du [docker-compose.yml](docker-compose.yml)
4. **Remplissez les variables d'environnement** dans la section `Environment`
5. **Cliquez sur** `Deploy the stack`

## 📝 Configuration

### Variables d'Environnement

| Variable | Défaut | Description |
|----------|--------|-------------|
| `SOURCE_ROOT` | `/media` | Répertoire racine monté dans le conteneur qui contient vos sources |
| `SOURCE_FOLDERS` | `['/media']` | JSON array des dossiers sources (paths absolus sur l'hôte) |
| `SOURCE_FOLDER` | `/media/videos` | (Compatibilité) premier dossier source si utilisé |
| `WATCH_MODE` | `True` | Surveillance continue |
| `WATCH_INTERVAL` | `60` | Intervalle de vérification (secondes) |
| `ADD_CLEAN_SUFFIX` | `True` | Ajouter " clean" au nom |
| `REMOVE_SITE_PREFIX` | `True` | Enlever le domaine du site |
| `START_HOUR` | `3` | Heure de début (0-23) |
| `END_HOUR` | `5` | Heure de fin (0-23) |
| `ENABLE_SCHEDULING` | `True` | Activer la planification |
| `CLEANFILE_HOST_DIR` | `/docker/mkv_url_cleaner_daniel` | Dossier hôte où sera stocké `cleanfile.txt` |
| `CLEANFILE_PATH` | `/docker/mkv_url_cleaner_daniel/cleanfile.txt` | Chemin utilisé dans le conteneur pour le fichier de suivi |

### Planification Horaire

**Exemple : Nettoyage seulement entre 3h00 et 5h00 du matin**

```bash
START_HOUR=3
END_HOUR=5
ENABLE_SCHEDULING=True
```

**Fenêtre traversant minuit : 22h à 2h du matin**

```bash
START_HOUR=22
END_HOUR=2
```

## 🐳 Image Docker

Image disponible sur GitHub Container Registry :

```bash
ghcr.io/praadip91/mkv_url_cleaner:main
```

## 📚 Documentation Complète

- [Configuration de la Planification Horaire](SCHEDULING.md)
- [Dockerfile](Dockerfile)

## 🔧 Installation Manuelle

```bash
# Cloner le repo
git clone https://github.com/Praadip91/mkv_url_cleaner.git
cd mkv_url_cleaner

# Créer un .env
cp .env.example .env

# Installer les dépendances
pip install -r requirements.txt

# Lancer le script
python3 mkv_url_cleaner.py
```

## 📋 Prérequis

- Python 3.8+
- mkvtoolnix
- python-dotenv

## 📄 Licence

MIT
