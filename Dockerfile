FROM python:3.12-slim

# Git für Push zu GitHub, cron für Scheduling, tini als sauberer PID-1-Prozess
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    cron \
    tini \
    && rm -rf /var/lib/apt/lists/*

# Python-Abhängigkeiten
RUN pip install --no-cache-dir requests beautifulsoup4

WORKDIR /app

# Scraper-Script
COPY scraper.py .
COPY run.sh .
RUN chmod +x run.sh

# Crontab einrichten (jeden Montag 06:00 UTC)
COPY crontab /etc/cron.d/scraper
RUN chmod 0644 /etc/cron.d/scraper && crontab /etc/cron.d/scraper

# Logs sichtbar machen
RUN touch /var/log/scraper.log

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["sh", "-c", "cron && tail -f /var/log/scraper.log"]
