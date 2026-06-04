#!/bin/sh
# run.sh — wird von cron aufgerufen

set -e

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "[$TIMESTAMP] Starte Scraper..."

# Pflicht-Variablen prüfen
if [ -z "$GITHUB_TOKEN" ] || [ -z "$GITHUB_USER" ] || [ -z "$GITHUB_REPO" ]; then
  echo "[$TIMESTAMP] FEHLER: GITHUB_TOKEN, GITHUB_USER oder GITHUB_REPO nicht gesetzt."
  exit 1
fi

REPO_DIR="/tmp/blocklist-work"
REPO_URL="https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com/${GITHUB_USER}/${GITHUB_REPO}.git"

# Repo klonen oder aktualisieren
if [ -d "$REPO_DIR/.git" ]; then
  echo "[$TIMESTAMP] Repo aktualisieren..."
  cd "$REPO_DIR"
  git pull --quiet
else
  echo "[$TIMESTAMP] Repo klonen..."
  rm -rf "$REPO_DIR"
  git clone --quiet "$REPO_URL" "$REPO_DIR"
  cd "$REPO_DIR"
fi

# Git-Identität setzen
git config user.name "Dropshipping Scraper Bot"
git config user.email "${GITHUB_USER}@users.noreply.github.com"

# Scraper ausführen (scraper.py liegt in /app, generiert Dateien im CWD)
cp /app/scraper.py .
python3 scraper.py

# Prüfen ob Änderungen vorliegen
if git diff --quiet blocklist.txt domains.txt 2>/dev/null && \
   ! git status --short | grep -qE "blocklist\.txt|domains\.txt"; then
  echo "[$TIMESTAMP] Keine Änderungen — Quelle unverändert."
  exit 0
fi

# Anzahl Einträge ermitteln und pushen
ENTRIES=$(grep -c "^||" blocklist.txt 2>/dev/null || echo "0")
DATE=$(date '+%Y-%m-%d')

git add blocklist.txt domains.txt
git commit -m "chore: Blockliste aktualisiert ($ENTRIES Einträge) [$DATE]"
git push --quiet

echo "[$TIMESTAMP] Fertig. $ENTRIES Einträge gepusht."
