FROM ubuntu:24.04

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    mkvtoolnix \
    && rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers du projet
COPY mkv_url_cleaner.py .
COPY requirements.txt .

# Installer les dépendances Python
RUN pip3 install --no-cache-dir -r requirements.txt

# Variables d'environnement par défaut
ENV WATCH_MODE=True
ENV WATCH_INTERVAL=60
ENV ADD_CLEAN_SUFFIX=True
ENV REMOVE_SITE_PREFIX=True
ENV START_HOUR=3
ENV END_HOUR=5
ENV ENABLE_SCHEDULING=True

# Monter le répertoire source comme volume
VOLUME ["/media", "/config"]

# Lancer le script
CMD ["python3", "mkv_url_cleaner.py"]
