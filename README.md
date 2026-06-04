# Dropshipping Blockliste CH 🛡️

Automatisch generierte Filterliste für **AdGuard**, **uBlock Origin** und **Pi-hole** mit dubiósen Dropshipping-Shops — basierend auf der verifizierten Liste des [Schweizerischen Konsumentenschutzes](https://www.konsumentenschutz.ch/online-ratgeber/dropshipping-die-stolpersteine-beim-onlinehandel-mit-billigware-aus-china/).

> ⚠️ **Hinweis:** Dieses Projekt wurde dem Konsumentenschutz zur Bewilligung vorgelegt.

---

## Einbinden

### AdGuard Home / AdGuard Browser-Extension

Einstellungen → Filterlisten → Benutzerdefiniert → URL einfügen:
```
https://raw.githubusercontent.com/swaelti/dropshipping-blocklist/main/blocklist.txt
```

### uBlock Origin

Dashboard → Filterlisten → Importieren → URL einfügen:
```
https://raw.githubusercontent.com/swaelti/dropshipping-blocklist/main/blocklist.txt
```

### Pi-hole

Web-UI → Adlists → URL einfügen:
```
https://raw.githubusercontent.com/swaelti/dropshipping-blocklist/main/domains.txt
```

---

## Dateien

| Datei | Beschreibung |
|---|---|
| `blocklist.txt` | AdGuard / uBlock Origin Format (`\|\|domain.tld^`) |
| `domains.txt` | Einfache Domain-Liste für Pi-hole |
| `scraper.py` | Python-Scraper der die Liste generiert |
| `deploy_vps.sh` | Deployment-Script für eigenen VPS/Server |

---

## Lokal ausführen

```bash
pip install requests beautifulsoup4
python3 scraper.py
```

**Wichtig:** Der Scraper muss von einer normalen IP (Heim-/Büronetz, eigener VPS) ausgeführt werden — die Quellseite blockiert Datacenter-IPs.

---

## Automatische Aktualisierung

**Option A — GitHub Actions mit Self-Hosted Runner** (empfohlen):
1. GitHub Actions Self-Hosted Runner auf eigenem Server einrichten
2. `.github/workflows/update.yml` läuft jeden Montag automatisch

**Option B — Cronjob auf VPS** (einfacher):
```bash
# Einmalig: PAT konfigurieren (Fine-grained token, Contents: Read+Write)
git remote set-url origin https://swaelti:YOUR_PAT@github.com/swaelti/dropshipping-blocklist.git

# Cronjob (crontab -e):
0 6 * * 1 /path/to/dropshipping-blocklist/deploy_vps.sh >> /var/log/dropshipping.log 2>&1
```

---

## Quelle & Rechtliches

- **Quelle:** [Stiftung für Konsumentenschutz](https://www.konsumentenschutz.ch/)
- Alle Domains stammen aus der öffentlich zugänglichen, manuell verifizierten Liste
- Betrieb ohne kommerzielle Absicht, ausschliesslich zum Schutz der Konsumentinnen und Konsumenten
- Keine Gewähr für Vollständigkeit oder Aktualität

---

## Fehler melden / Mitmachen

- Falsch gelistete Domains → [Issue erstellen](../../issues)
- Dubiósen Shop melden → [Konsumentenschutz Meldeformular](https://findmind.ch/c/dropshipping-)
