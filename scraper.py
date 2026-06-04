#!/usr/bin/env python3
"""
Dropshipping Blocklist Generator
Quelle: https://www.konsumentenschutz.ch/online-ratgeber/dropshipping-die-stolpersteine-beim-onlinehandel-mit-billigware-aus-china/

Hinweis: Die Quellseite blockiert Anfragen von Datacenter-IPs (GitHub Actions).
Deployment-Optionen:
  A) GitHub Actions Self-Hosted Runner auf eigenem VPS/Server
  B) Cronjob auf VPS + Push via GitHub API (deploy_vps.sh)
  C) Lokal ausführen + manuell committen
"""

import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

SOURCE_URL = (
    "https://www.konsumentenschutz.ch/online-ratgeber/"
    "dropshipping-die-stolpersteine-beim-onlinehandel-mit-billigware-aus-china/"
)
OUTPUT_FILE = Path("blocklist.txt")
DOMAINS_FILE = Path("domains.txt")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "de-CH,de;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

# Domains die nie blockiert werden sollen
WHITELIST = {
    "amazon.com", "amazon.de", "amazon.ch",
    "digitec.ch", "galaxus.ch", "interdiscount.ch",
    "aliexpress.com", "temu.com", "shein.com", "wish.com", "dhgate.com",
    "konsumentenschutz.ch", "seco.admin.ch", "fedlex.admin.ch",
    "trustpilot.com", "findmind.ch", "blick.ch", "srf.ch", "20min.ch",
}


def fetch_page(url: str) -> BeautifulSoup:
    """Lädt die Seite mit einer Session (Homepage zuerst für Cookies)."""
    session = requests.Session()

    print("Initialisiere Session (Homepage)...")
    try:
        session.get(
            "https://www.konsumentenschutz.ch/",
            headers=HEADERS,
            timeout=15,
        )
        time.sleep(1)  # Kurze Pause wirkt natürlicher
    except Exception:
        pass  # Wenn Homepage fehlschlägt, trotzdem weitermachen

    print(f"Lade Zielseite: {url}")
    response = session.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def extract_domains(soup: BeautifulSoup) -> list[str]:
    """Extrahiert alle Domains aus der HTML-Tabelle."""
    domains = set()

    domain_pattern = re.compile(
        r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+"
        r"[a-zA-Z]{2,}$"
    )

    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cells = row.find_all(["td", "th"])
            if not cells:
                continue

            raw = cells[0].get_text(strip=True).strip().lower()
            raw = re.sub(r"\s+", "", raw)

            if not raw or raw == "website":
                continue

            if domain_pattern.match(raw) and raw not in WHITELIST:
                domains.add(raw)

    return sorted(domains)


def get_source_last_modified(soup: BeautifulSoup) -> str:
    """Liest das Aktualisierungsdatum von der Quellseite."""
    text = soup.get_text()
    match = re.search(r"Zuletzt aktualisiert:\s*(\d{2}\.\d{2}\.\d{4})", text)
    return match.group(1) if match else "unbekannt"


def write_adguard_list(domains: list[str], source_last_modified: str) -> None:
    """Schreibt die AdGuard/uBlock Origin kompatible Filterliste."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    count = len(domains)

    header = f"""! Title: Dubióse Dropshipping-Shops CH/DE/AT (Konsumentenschutz)
! Description: Automatisch generierte Blockliste basierend auf der verifizierten
!   Liste des Schweizerischen Konsumentenschutzes. Enthält Online-Shops die wegen
!   irreführender Produktangaben, gefälschter Bewertungen, fehlender Impressums-
!   angaben oder mangelhafter Qualität gemeldet wurden.
! Source: {SOURCE_URL}
! Quelle zuletzt aktualisiert: {source_last_modified}
! Generiert: {now}
! Einträge: {count}
! Lizenz: Verwendung auf eigene Verantwortung. Keine Gewähr für Vollständigkeit.
!
! Einbinden in AdGuard / uBlock Origin:
!   https://raw.githubusercontent.com/YOUR_USERNAME/dropshipping-blocklist/main/blocklist.txt
!
! =========================================================

"""
    rules = "\n".join(f"||{domain}^" for domain in domains)
    OUTPUT_FILE.write_text(header + rules + "\n", encoding="utf-8")
    print(f"✓ Filterliste geschrieben: {OUTPUT_FILE} ({count} Einträge)")


def write_plain_domains(domains: list[str]) -> None:
    """Schreibt eine einfache Domain-Liste (für Pi-hole)."""
    DOMAINS_FILE.write_text("\n".join(domains) + "\n", encoding="utf-8")
    print(f"✓ Domain-Liste geschrieben: {DOMAINS_FILE} ({len(domains)} Einträge)")


def main() -> int:
    try:
        soup = fetch_page(SOURCE_URL)
        domains = extract_domains(soup)

        if not domains:
            print("FEHLER: Keine Domains gefunden!")
            print("Mögliche Ursachen:")
            print("  - Seitenstruktur hat sich geändert")
            print("  - Request von Datacenter-IP blockiert (403)")
            print("  → Auf eigenem Server/VPS ausführen, nicht auf GitHub Actions")
            return 1

        source_date = get_source_last_modified(soup)
        print(f"✓ Quell-Datum: {source_date}")
        print(f"✓ {len(domains)} Domains extrahiert")

        write_adguard_list(domains, source_date)
        write_plain_domains(domains)

        print("\nVorschau (erste 10 Einträge):")
        for d in domains[:10]:
            print(f"  ||{d}^")

        return 0

    except requests.HTTPError as e:
        if e.response.status_code == 403:
            print("FEHLER 403: Zugriff verweigert.")
            print("Die Seite blockiert Datacenter-IPs.")
            print("→ Scraper auf eigenem VPS/PC ausführen (nicht GitHub Actions)")
            print("→ Siehe: deploy_vps.sh für VPS-Deployment")
        else:
            print(f"HTTP-Fehler: {e}")
        return 1
    except requests.RequestException as e:
        print(f"FEHLER beim Laden der Seite: {e}")
        return 1
    except Exception as e:
        print(f"FEHLER: {e}")
        raise


if __name__ == "__main__":
    sys.exit(main())
