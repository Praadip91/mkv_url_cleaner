# MKV URL Cleaner - Docker Edition

Application de nettoyage automatique des fichiers MKV avec mode watch.

## Fonctionnalités

- 🧼 **Nettoyage des métadonnées MKV**: Supprime les titres de piste et du fichier
- 🌐 **Suppression des préfixes de site**: Enlève les URLs (www.example.com) des noms
- 👀 **Mode Watch**: Surveillance continue du dossier source
- 🐳 **Dockerisé**: Déploiement facile avec Docker Compose

## Installation et utilisation

### Avec Docker Compose (Recommandé)

1. **Cloner le projet et configurer**:
```bash
cd mkv_url_cleaner
cp .env.example .env
# Éditer .env et définir SOURCE_FOLDER
```

2. **Lancer le service**:
```bash
docker-compose up -d
```

3. **Voir les logs**:
```bash
docker-compose logs -f
```

4. **Arrêter le service**:
```bash
docker-compose down
```

### Avec Docker directement

```bash
docker build -t mkv-cleaner .

docker run -d \
  -v /path/to/media:/media \
  -e WATCH_MODE=True \
  -e WATCH_INTERVAL=60 \
  -e SOURCE_FOLDER=/media \
  --restart unless-stopped \
  --name mkv-cleaner \
  mkv-cleaner
```

### En local (sans Docker)

```bash
pip3 install -r requirements.txt
# Éditer .env
python3 mkv_url_cleaner.py
```

## Configuration (variables .env)

| Variable | Défaut | Description |
|----------|--------|-------------|
| `SOURCE_FOLDER` | - | Chemin du dossier MKV à surveiller |
| `WATCH_MODE` | True | Active la surveillance continue |
| `WATCH_INTERVAL` | 60 | Secondes entre chaque vérification |
| `ADD_CLEAN_SUFFIX` | True | Ajoute " clean" au fichier nettoyé |
| `REMOVE_SITE_PREFIX` | True | Enlève les URLs des noms |

## Dépendances système

- **mkvtoolnix**: Outils MKV (mkvmerge)
- **Python 3.10+**
- **Docker** (optionnel, pour la conteneurisation)

## Mode Watch

En activant `WATCH_MODE=True`, l'application:
- ✅ Vérifie le dossier toutes les `WATCH_INTERVAL` secondes
- ✅ Traite les nouveaux fichiers ou fichiers modifiés
- ✅ Continue de tourner indéfiniment
- ✅ S'arrête proprement avec Ctrl+C (mode local)

## Exemples de sortie

```
👀 Mode watch activé - Intervalle: 60s
📁 Dossier surveillé: /media
🧼 Nettoyage : /media/www.example.com - S01E01.mkv
✔ OK
⏳ Attente de 60s avant prochaine vérification...
```

## Troubleshooting

### Le conteneur s'arrête immédiatement
Vérifiez les logs: `docker-compose logs`

### Les fichiers ne sont pas traités
- Vérifiez que `SOURCE_FOLDER` est correct
- Assurez-vous que le volume Docker est bien monté
- Vérifiez que `WATCH_INTERVAL` n'est pas trop élevé

### Erreur "mkvmerge not found"
Assurez-vous que mkvtoolnix est installé dans le conteneur (Dockerfile à jour)

## Licence

MIT
