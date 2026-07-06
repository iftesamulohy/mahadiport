#!/usr/bin/env bash
# Redeploy script — runs ON THE VPS (as root) after new code is pushed.
# Triggered by GitHub Actions over SSH, or manually:
#   cd /var/www/mahadi && sudo bash deploy/update.sh
set -euo pipefail

# Namespaced to the SECOND site — never references site #1 (ohydev).
APP_DIR=/var/www/mahadi
SERVICE=mahadi
SOCK="$APP_DIR/$SERVICE.sock"

[ "$EUID" -eq 0 ] || { echo "ERROR: run as root:  sudo bash $0"; exit 1; }
cd "$APP_DIR"

# ── Load production environment (DJANGO_SETTINGS_MODULE + secrets) ──
# Without this, manage.py falls back to dev settings, which breaks
# collectstatic on production (missing staticfiles manifest = 500).
if [ -f "$APP_DIR/.env" ]; then
    set -a
    source "$APP_DIR/.env"
    set +a
fi
# NOTE: this project's prod module is 'config.settings.prod' (not 'production').
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings.prod}"

# Let root operate on the www-data-owned git repo without complaints.
git config --global --add safe.directory "$APP_DIR" 2>/dev/null || true

echo "==> Pulling latest code"
git pull

echo "==> Installing dependencies"
venv/bin/pip install -r requirements.txt -q

echo "==> Running migrations"
venv/bin/python manage.py migrate --noinput

echo "==> Collecting static files"
venv/bin/python manage.py collectstatic --noinput

echo "==> Fixing ownership"
chown -R www-data:www-data "$APP_DIR"

echo "==> Refreshing systemd unit (in case deploy/gunicorn.service changed)"
sed -e "s#__APP_DIR__#$APP_DIR#g" -e "s#__SERVICE__#$SERVICE#g" -e "s#__SOCK__#$SOCK#g" \
    deploy/gunicorn.service > "/etc/systemd/system/$SERVICE.service"
systemctl daemon-reload

echo "==> Restarting Gunicorn"
systemctl restart "$SERVICE"

echo "==> Done. Service status:"
systemctl status "$SERVICE" --no-pager -l | head -10
