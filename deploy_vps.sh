#!/bin/bash
# deploy_vps.sh
# Cronjob-Script für eigenen VPS/Server
# Führt den Scraper aus und pusht Änderungen direkt zu GitHub
#
# Setup:
#   1. Dieses Repo auf dem VPS klonen:
#      git clone https://github.com/YOUR_USERNAME/dropshipping-blocklist.git
#      cd dropshipping-blocklist
#
#   2. GitHub Personal Access Token (PAT) erstellen:
#      GitHub → Settings → Developer settings → Personal access tokens → Fine-grained
#      Berechtigung: "Contents" = Read and Write für dieses Repo
#
#   3. Git-Credentials konfigurieren (einmalig):
#      git config user.name "VPS Bot"
#      git config user.email "your@email.com"
#      git remote set-url origin https://YOUR_USERNAME:YOUR_PAT@github.com/YOUR_USERNAME/dropshipping-blocklist.git
#
#   4. Cronjob einrichten (jeden Montag 06:00):
#      crontab -e
#      0 6 * * 1 /path/to/dropshipping-blocklist/deploy_vps.sh >> /var/log/dropshipping-blocklist.log 2>&1

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_PREFIX="[$(date '+%Y-%m-%d %H:%M:%S')]"

echo "$LOG_PREFIX Starte Dropshipping-Blocklist Update..."
cd "$SCRIPT_DIR"

# Neueste Version holen
echo "$LOG_PREFIX git pull..."
git pull --quiet

# Dependencies prüfen / installieren
if ! python3 -c "import requests, bs4" 2>/dev/null; then
    echo "$LOG_PREFIX Installiere Python-Abhängigkeiten..."
    pip3 install --quiet --break-system-packages requests beautifulsoup4
fi

# Scraper ausführen
echo "$LOG_PREFIX Führe Scraper aus..."
python3 scraper.py

# Prüfen ob es Änderungen gibt
if git diff --quiet blocklist.txt domains.txt 2>/dev/null && \
   ! git status --short | grep -q "blocklist.txt\|domains.txt"; then
    echo "$LOG_PREFIX Keine Änderungen — Quelle unverändert."
    exit 0
fi

# Anzahl Einträge ermitteln
ENTRIES=$(grep -c "^||" blocklist.txt || echo "0")

# Commit und Push
echo "$LOG_PREFIX Pushe Änderungen ($ENTRIES Einträge)..."
git add blocklist.txt domains.txt
git commit -m "chore: Blockliste aktualisiert ($ENTRIES Einträge) [$(date '+%Y-%m-%d')]"
git push

echo "$LOG_PREFIX ✓ Fertig. $ENTRIES Einträge publiziert."
