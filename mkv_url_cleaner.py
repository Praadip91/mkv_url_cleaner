import os
import subprocess
import json
import re
import time
import sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Support pour SOURCE_FOLDER (simple) ou SOURCE_FOLDERS (multiple)
SOURCE_FOLDERS_STR = os.getenv("SOURCE_FOLDERS")
if SOURCE_FOLDERS_STR:
    # Parser la liste JSON
    try:
        SOURCE_FOLDERS = json.loads(SOURCE_FOLDERS_STR)
    except json.JSONDecodeError:
        print(f"❌ Erreur dans le format SOURCE_FOLDERS : {SOURCE_FOLDERS_STR}")
        sys.exit(1)
else:
    # Utiliser SOURCE_FOLDER en fallback
    source_folder = os.getenv("SOURCE_FOLDER")
    SOURCE_FOLDERS = [source_folder] if source_folder else []

CLEANFILE_PATH = os.getenv("CLEANFILE_PATH", "cleanfile.txt")

# 🔧 Paramètres de nettoyage (depuis .env)
ADD_CLEAN_SUFFIX = os.getenv("ADD_CLEAN_SUFFIX", "True").lower() == "true"
REMOVE_SITE_PREFIX = os.getenv("REMOVE_SITE_PREFIX", "True").lower() == "true"

# 👀 Paramètres de watch mode
WATCH_MODE = os.getenv("WATCH_MODE", "False").lower() == "true"
WATCH_INTERVAL = int(os.getenv("WATCH_INTERVAL", "60"))  # en secondes

# ⏰ Paramètres de planification horaire
START_HOUR = int(os.getenv("START_HOUR", "3"))  # Heure de début (3h00)
END_HOUR = int(os.getenv("END_HOUR", "5"))      # Heure de fin (5h00)
ENABLE_SCHEDULING = os.getenv("ENABLE_SCHEDULING", "True").lower() == "true"

# Regex générique pour tous les sites commencant par www
SITE_REGEX = re.compile(
    r"\bwww\.[a-z0-9]+([-\.][a-z0-9]+)*\.[a-z]{2,}\b\s*-?\s*",
    re.IGNORECASE
)

def is_within_execution_window():
    """Vérifie si on est dans la fenêtre horaire autorisée"""
    if not ENABLE_SCHEDULING:
        return True
    
    current_hour = datetime.now().hour
    
    if START_HOUR <= END_HOUR:
        # Fenêtre normale (ex: 3h à 5h)
        return START_HOUR <= current_hour < END_HOUR
    else:
        # Fenêtre traversant minuit (ex: 22h à 2h)
        return current_hour >= START_HOUR or current_hour < END_HOUR

def can_start_new_process():
    """Vérifie si on peut démarrer un nouveau processus de nettoyage"""
    if not ENABLE_SCHEDULING:
        return True
    
    current_hour = datetime.now().hour
    
    if START_HOUR <= END_HOUR:
        # Après END_HOUR, pas de nouveau processus
        return current_hour < END_HOUR
    else:
        # Pour fenêtre traversant minuit
        return current_hour < END_HOUR or current_hour >= START_HOUR

def read_cleaned_files():
    """Lit la liste des fichiers déjà nettoyés"""
    if not os.path.exists(CLEANFILE_PATH):
        return set()
    
    cleaned = set()
    try:
        with open(CLEANFILE_PATH, "r", encoding="utf-8") as f:
            for line in f:
                cleaned.add(line.strip())
    except Exception as e:
        print(f"❌ Erreur lors de la lecture de {CLEANFILE_PATH}: {e}")
    
    return cleaned

def add_to_cleaned_files(mkv_path):
    """Ajoute un fichier à la liste des fichiers nettoyés"""
    try:
        with open(CLEANFILE_PATH, "a", encoding="utf-8") as f:
            f.write(mkv_path + "\n")
    except Exception as e:
        print(f"❌ Erreur lors de l'écriture dans {CLEANFILE_PATH}: {e}")

def is_already_cleaned(mkv_path):
    """Vérifie si un fichier a déjà été nettoyé"""
    cleaned_files = read_cleaned_files()
    return mkv_path in cleaned_files

def get_tracks(mkv_path):
    result = subprocess.run(
        ["mkvmerge", "-J", mkv_path],
        capture_output=True,
        text=True,
        check=True
    )
    return json.loads(result.stdout)["tracks"]

def clean_filename(filename):
    name, ext = os.path.splitext(filename)
    
    # Optionnel : enlever le site au début
    if REMOVE_SITE_PREFIX:
        name = SITE_REGEX.sub("", name).strip()
    
    # Optionnel : ajouter " clean" en fin
    if ADD_CLEAN_SUFFIX:
        return f"{name} clean{ext}"
    else:
        return f"{name}{ext}"

def remux_clean(mkv_path):
    tracks = get_tracks(mkv_path)

    # Sauvegarde des dates
    stat = os.stat(mkv_path)

    dirpath = os.path.dirname(mkv_path)
    original_name = os.path.basename(mkv_path)
    new_name = clean_filename(original_name)

    temp_path = os.path.join(dirpath, "__tmp_clean.mkv")
    final_path = os.path.join(dirpath, new_name)

    cmd = ["mkvmerge", "-o", temp_path]

    for track in tracks:
        tid = track["id"]
        ttype = track["type"]
        props = track.get("properties", {})
        name = props.get("track_name")

        # 🎬 VIDÉO → supprimer le nom
        if ttype == "video" and name:
            cmd += ["--track-name", f"{tid}:"]

        # 🎧 AUDIO → enlever uniquement le site (si activé)
        elif ttype == "audio" and name:
            new_name_track = SITE_REGEX.sub("", name).strip()
            if new_name_track != name:
                cmd += ["--track-name", f"{tid}:{new_name_track}"]

        # 📝 SOUS-TITRES → supprimer le nom
        elif ttype == "subtitles":
            cmd += ["--track-name", f"{tid}:"]

    # 🗑️ Supprimer le Title global
    cmd += ["--title", ""]

    cmd.append(mkv_path)
    subprocess.run(cmd, check=True)

    # Remplacer l’original
    os.remove(mkv_path)
    os.rename(temp_path, final_path)

    # Restaurer les dates (atime, mtime)
    os.utime(final_path, (stat.st_atime, stat.st_mtime))    
    # Ajouter le fichier à la liste des fichiers nettoyés
    add_to_cleaned_files(mkv_path)
def main():
    # Vérifier si un fichier est spécifié en ligne de commande
    if len(sys.argv) > 1:
        # Traiter le fichier spécifié
        file_path = sys.argv[1]
        
        if not os.path.exists(file_path):
            print(f"❌ Fichier non trouvé : {file_path}")
            sys.exit(1)
        
        if not file_path.lower().endswith(".mkv"):
            print(f"❌ Ce n'est pas un fichier .mkv : {file_path}")
            sys.exit(1)
        
        # Vérifier si on est dans la fenêtre d'exécution
        if not can_start_new_process():
            print(f"⏰ Fenêtre de nettoyage fermée (START: {START_HOUR}h, END: {END_HOUR}h). Fichier ignoré.")
            sys.exit(1)
        
        # Vérifier si le fichier a déjà été nettoyé
        if is_already_cleaned(file_path):
            print(f"⏭️  Fichier déjà nettoyé, ignoré : {file_path}")
            sys.exit(0)
        
        print(f"🧼 Nettoyage : {file_path}")
        try:
            remux_clean(file_path)
            print("✔ OK")
        except Exception as e:
            print(f"❌ ERREUR : {e}")
            sys.exit(1)
    
    elif WATCH_MODE:
        print(f"👀 Mode watch activé - Intervalle: {WATCH_INTERVAL}s")
        print(f"📁 Dossiers surveillés: {SOURCE_FOLDERS}")
        if ENABLE_SCHEDULING:
            print(f"⏰ Fenêtre d'exécution: {START_HOUR}h00 à {END_HOUR}h00")
        processed_files = set()
        
        while True:
            try:
                current_time = datetime.now().strftime("%H:%M:%S")
                
                # Vérifier si on est toujours dans la fenêtre d'exécution
                if not is_within_execution_window():
                    print(f"[{current_time}] ⏰ Fenêtre fermée, mise en pause...")
                    time.sleep(WATCH_INTERVAL)
                    continue
                
                # Vérifier si on peut démarrer de nouveaux processus
                if not can_start_new_process():
                    print(f"[{current_time}] ⏰ Fin de fenêtre atteinte, pas de nouveaux nettoyages")
                    time.sleep(WATCH_INTERVAL)
                    continue
                
                for source_folder in SOURCE_FOLDERS:
                    if not os.path.exists(source_folder):
                        print(f"⚠️  Dossier non trouvé : {source_folder}")
                        continue
                    
                    for root, dirs, files in os.walk(source_folder):
                        for file in files:
                            if not file.lower().endswith(".mkv"):
                                continue

                            # ❌ ignorer les fichiers déjà clean
                            if file.lower().endswith("clean.mkv"):
                                continue

                            if file.lower().endswith("trailer.mkv"):
                                continue

                            mkv_path = os.path.join(root, file)
                            
                            # Vérifier si le fichier a déjà été nettoyé
                            if is_already_cleaned(mkv_path):
                                continue
                            
                            file_id = os.path.getmtime(mkv_path)  # utiliser la date de modification
                            
                            # Traiter seulement les fichiers nouveaux ou modifiés
                            if mkv_path not in processed_files or processed_files.get(mkv_path) != file_id:
                                print(f"🧼 Nettoyage : {mkv_path}")
                                try:
                                    remux_clean(mkv_path)
                                    processed_files[mkv_path] = file_id
                                    print("✔ OK")
                                except Exception as e:
                                    print(f"❌ ERREUR : {e}")
                
                print(f"⏳ Attente de {WATCH_INTERVAL}s avant prochaine vérification...")
                time.sleep(WATCH_INTERVAL)
                
            except KeyboardInterrupt:
                print("\n🛑 Mode watch arrêté par l'utilisateur")
                sys.exit(0)
            except Exception as e:
                print(f"❌ ERREUR du watch mode : {e}")
                time.sleep(WATCH_INTERVAL)
    else:
        # Mode unique (run once)
        if ENABLE_SCHEDULING and not can_start_new_process():
            print(f"⏰ Fenêtre de nettoyage fermée (START: {START_HOUR}h, END: {END_HOUR}h)")
            print(f"⏰ Heure actuelle : {datetime.now().strftime('%H:%M:%S')}")
            print("❌ Aucun nettoyage ne peut être démarré en dehors de cette fenêtre.")
            sys.exit(1)
        
        if ENABLE_SCHEDULING:
            print(f"⏰ Fenêtre d'exécution: {START_HOUR}h00 à {END_HOUR}h00")
        
        for source_folder in SOURCE_FOLDERS:
            if not os.path.exists(source_folder):
                print(f"⚠️  Dossier non trouvé : {source_folder}")
                continue
            
            for root, dirs, files in os.walk(source_folder):
                for file in files:
                    if not file.lower().endswith(".mkv"):
                        continue

                    # ❌ ignorer les fichiers déjà clean

                    if file.lower().endswith("clean.mkv"):
                        continue

                    if file.lower().endswith("trailer.mkv"):
                        continue

                    mkv_path = os.path.join(root, file)
                    
                    # Vérifier si le fichier a déjà été nettoyé
                    if is_already_cleaned(mkv_path):
                        continue
                    
                    print(f"🧼 Nettoyage : {mkv_path}")

                    try:
                        remux_clean(mkv_path)
                        print("✔ OK")
                    except Exception as e:
                        print(f"❌ ERREUR : {e}")

if __name__ == "__main__":
    main()
