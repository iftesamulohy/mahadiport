#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════
#  ONE-TIME VPS SETUP — Md Mahadi Hasan portfolio  (SECOND site)
#
#  Deploys this repo as a fully independent Django site on a VPS that
#  ALREADY hosts another site (e.g. "ohydev"). It never touches the
#  first site: unique folder, unique systemd unit, unique nginx file,
#  its own unix socket, and its own Let's Encrypt certificate.
#
#  How to use:
#    1. Edit the "EDIT THESE" block below (DOMAIN + REPO_URL at minimum).
#    2. Copy this file to the VPS:
#         scp deploy/setup_vps.sh root@YOUR_VPS_IP:/root/setup_mahadi.sh
#    3. On the VPS, run:
#         sudo bash /root/setup_mahadi.sh
#
#  Pauses once so you can copy your existing database + media.
#  Safe to re-run if something fails halfway.
# ════════════════════════════════════════════════════════════════════
set -euo pipefail

# ╔══════════════════════════════════════════════════════════════════╗
# ║  EDIT THESE VALUES BEFORE RUNNING                                ║
# ╚══════════════════════════════════════════════════════════════════╝
DOMAIN="mdmahadihasan.com"                # the NEW domain, WITHOUT www
CERTBOT_EMAIL="iftesamulohy@gmail.com"    # for Let's Encrypt expiry notices

# Repo to clone. For a PUBLIC repo, a plain https URL is enough.
# For a PRIVATE repo, DON'T hardcode a token here — instead run:
#     export REPO_URL="https://YOUR_GITHUB_TOKEN@github.com/USER/REPO.git"
#   before invoking this script. The token is never printed.
REPO_URL="${REPO_URL:-https://github.com/iftesamulohy/mahadiport.git}"

# These match deploy/gunicorn.service and deploy/nginx.conf via placeholder
# substitution below — change all three together if you change any.
APP_DIR="/var/www/mahadi"
SERVICE="mahadi"
SOCK="$APP_DIR/$SERVICE.sock"    # unix socket => cannot collide with site #1
# ════════════════════════════════════════════════════════════════════

[ "$EUID" -eq 0 ] || { echo "ERROR: run as root:  sudo bash $0"; exit 1; }
[ "$DOMAIN" = "CHANGE_ME.com" ] && { echo "ERROR: set DOMAIN in the EDIT THESE block first."; exit 1; }

step() { echo; echo "════ $1 ════"; }

step "1/9  System packages (idempotent — no-ops if site #1 already installed them)"
# Guard each apt install so an already-provisioned VPS isn't churned.
need_pkg() { command -v "$1" >/dev/null 2>&1; }
if ! need_pkg git || ! need_pkg nginx || ! need_pkg certbot || ! command -v python3 >/dev/null; then
    apt-get update -y
    apt-get install -y python3-venv python3-pip git nginx certbot python3-certbot-nginx
else
    echo "Core packages already present — skipping apt."
fi

step "2/9  Firewall (assumed already configured system-wide; NOT reset)"
# ufw rules for OpenSSH + Nginx Full were set up for site #1. Re-allow is a
# harmless no-op; we deliberately do NOT run 'ufw --force enable'/'ufw reset'.
if command -v ufw >/dev/null 2>&1; then
    ufw allow 'Nginx Full' >/dev/null 2>&1 || true
    echo "Ensured 'Nginx Full' is allowed (no firewall reset performed)."
fi

step "3/9  Clone repository → $APP_DIR"
mkdir -p /var/www
if [ -d "$APP_DIR/.git" ]; then
    echo "Already cloned — pulling latest."
    git config --global --add safe.directory "$APP_DIR" 2>/dev/null || true
    git -C "$APP_DIR" pull
else
    # Never echo REPO_URL (it may embed a token).
    git clone "$REPO_URL" "$APP_DIR" || { echo "ERROR: git clone failed (check REPO_URL / token)."; exit 1; }
fi
cd "$APP_DIR"

step "4/9  Python virtualenv + dependencies"
[ -d venv ] || python3 -m venv venv
venv/bin/pip install --upgrade pip -q
venv/bin/pip install -r requirements.txt -q

step "5/9  .env file"
if [ -f .env ]; then
    echo ".env already exists — keeping it."
else
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))")
    cat > .env <<EOF
SECRET_KEY=$SECRET_KEY
DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings.prod
ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN
CSRF_TRUSTED_ORIGINS=https://$DOMAIN,https://www.$DOMAIN

# nginx (certbot --redirect) already forces http->https, so leave Django's
# own redirect off to avoid a pre-certificate redirect loop. Flip to True
# after HTTPS is confirmed working if you want belt-and-suspenders.
SECURE_SSL_REDIRECT=False

# ── Lead notification email (site works without SMTP) ──
LEAD_NOTIFY_EMAIL=mahadihasanshawons@gmail.com
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

# ── Optional Postgres. NOTE: requirements.txt has no psycopg driver, so
#    leaving this unset keeps the working SQLite db.sqlite3. Add psycopg
#    to requirements first if you switch. ──
# DATABASE_URL=postgres://user:pass@localhost:5432/mahadi
EOF
    echo "Created .env with a fresh SECRET_KEY and ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN"
    echo "NOTE: SMTP keys are blank — fill them in $APP_DIR/.env later,"
    echo "      then run:  systemctl restart $SERVICE"
fi

step "6/9  Your existing data (database + media)"
FRESH_DB=0
if [ ! -f db.sqlite3 ]; then
    VPS_IP=$(hostname -I | awk '{print $1}')
    echo "db.sqlite3 is NOT here yet. From your LOCAL machine, run:"
    echo
    echo "    scp ~/ohy_fold/mahadi/db.sqlite3 root@$VPS_IP:$APP_DIR/db.sqlite3"
    echo "    rsync -av ~/ohy_fold/mahadi/media/ root@$VPS_IP:$APP_DIR/media/"
    echo
    while [ ! -f db.sqlite3 ]; do
        read -rp "Press ENTER once copied (or type SKIP for a fresh seeded database): " ans
        if [ "${ans:-}" = "SKIP" ]; then FRESH_DB=1; echo "Continuing with a fresh database."; break; fi
        [ -f db.sqlite3 ] || echo "Still not found — waiting."
    done
else
    echo "db.sqlite3 found — your existing data will be used."
fi

step "7/9  Migrate, (seed if fresh), collectstatic, permissions"
mkdir -p media staticfiles
venv/bin/python manage.py migrate --noinput
if [ "$FRESH_DB" = "1" ]; then
    # README documents seed_site as the way to load the real CV content.
    echo "Fresh database — seeding real portfolio content (seed_site)."
    venv/bin/python manage.py seed_site || echo "seed_site skipped/failed — create content via /admin/ instead."
    echo "TIP: create an admin login with:  venv/bin/python manage.py createsuperuser"
fi
venv/bin/python manage.py collectstatic --noinput
chown -R www-data:www-data "$APP_DIR"

step "8/9  Gunicorn (systemd) + Nginx  — all namespaced to '$SERVICE'"
subst() { sed -e "s#__APP_DIR__#$APP_DIR#g" -e "s#__SERVICE__#$SERVICE#g" \
              -e "s#__SOCK__#$SOCK#g" -e "s#__DOMAIN__#$DOMAIN#g" "$1"; }

subst deploy/gunicorn.service > "/etc/systemd/system/$SERVICE.service"
systemctl daemon-reload
systemctl enable --now "$SERVICE"
systemctl restart "$SERVICE"

# Separate nginx site file — we NEVER remove 'default' or any other enabled
# site here, so site #1 stays untouched.
subst deploy/nginx.conf > "/etc/nginx/sites-available/$SERVICE"
ln -sf "/etc/nginx/sites-available/$SERVICE" "/etc/nginx/sites-enabled/$SERVICE"
nginx -t
systemctl reload nginx

step "9/9  HTTPS (Let's Encrypt) — new cert for THIS domain only"
if certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" \
        --non-interactive --agree-tos -m "$CERTBOT_EMAIL" --redirect; then
    echo "HTTPS enabled — http:// now redirects to https://"
else
    echo "WARNING: certbot failed — usually DNS hasn't propagated to this server yet."
    echo "The site still works on http://$DOMAIN. Once DNS points here, run:"
    echo "    certbot --nginx -d $DOMAIN -d www.$DOMAIN --redirect"
fi

# ── SSH key for GitHub Actions auto-deploy (reused if site #1 made one) ──
if [ ! -f /root/.ssh/github_deploy ]; then
    mkdir -p /root/.ssh && chmod 700 /root/.ssh
    ssh-keygen -t ed25519 -f /root/.ssh/github_deploy -N "" -C "github-actions-deploy" -q
    cat /root/.ssh/github_deploy.pub >> /root/.ssh/authorized_keys
    chmod 600 /root/.ssh/authorized_keys
fi

echo
echo "════════════════════════════════════════════════════════════════"
echo "  DONE — visit:  https://$DOMAIN"
echo "  Admin:         https://$DOMAIN/admin/"
echo "════════════════════════════════════════════════════════════════"
echo
echo "To enable AUTO-DEPLOY on push, add these secrets on the NEW GitHub repo"
echo "→ Settings → Secrets and variables → Actions:"
echo
echo "  VPS_HOST     = $(hostname -I | awk '{print $1}')"
echo "  VPS_USER     = root"
echo "  VPS_SSH_KEY  = (the private key below — same key site #1 uses is fine)"
echo "────────────────────────────────────────────────────────────────"
cat /root/.ssh/github_deploy
echo "────────────────────────────────────────────────────────────────"
echo
echo "Service status:"
systemctl status "$SERVICE" --no-pager | head -5
