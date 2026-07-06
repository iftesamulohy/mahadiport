# Second Site Deploy — Agent Prompt

Same VPS-এ existing `ohydev` site-কে না ভেঙে একটা আলাদা folder-এ দ্বিতীয় Django site deploy করার জন্য এই prompt-টা তোমার agent (Claude Code) এ paste করে দাও।

> ⚠️ **Security:** নিচের reference script-এ আগে যে GitHub token hardcoded ছিল সেটা placeholder দিয়ে replace করা হয়েছে। ওই পুরনো `ghp_...` token টা exposed হয়ে গেছে — GitHub → Settings → Developer settings → Personal access tokens এ গিয়ে **revoke করে নতুন একটা বানাও**।

---

## PROMPT (agent-এ paste করো)

````text
# TASK
On an existing Ubuntu VPS that already hosts a Django site called "ohydev"
(Gunicorn + Nginx + systemd + certbot), I want to deploy a SECOND, fully
independent Django site FROM THIS REPO on the SAME VPS — in a different folder
— WITHOUT breaking, overwriting, or touching the first site in any way.

Generate two shell scripts for THIS repo:
  1. deploy/setup_vps.sh   — one-time provisioning on a VPS that is already provisioned for site #1
  2. deploy/update.sh      — redeploy-on-push script (mirrors site #1's update.sh)

# FILL THESE IN (ask me if any are unclear before writing):
  NEW_DOMAIN   = <e.g. newsite.com>
  NEW_APP_DIR  = <e.g. /var/www/newsite>
  NEW_SERVICE  = <e.g. newsite>        # used for systemd units + nginx site file
  NEW_BIND     = <a Gunicorn port/socket that does NOT collide with site #1 — see rule 2>
  REPO_URL     = <do NOT hardcode a token; use a placeholder or env var — see rule 7>

# HARD CONSTRAINTS — the second site must not collide with the first anywhere:

1. FULL NAMESPACING. No leftover "ohydev" / "iftesamulohy.com" hardcoding anywhere
   in the generated scripts. Everything derives from NEW_SERVICE / NEW_APP_DIR /
   NEW_DOMAIN / NEW_BIND.

2. GUNICORN BIND MUST BE UNIQUE (most important). Site #1 already binds a port or
   unix socket. Before choosing NEW_BIND:
     - If you have shell access to the VPS, read /etc/systemd/system/ohydev.service
       (its ExecStart / gunicorn config) and the existing nginx site to see what
       site #1 binds to.
     - If you do NOT have VPS access, ASK ME what port/socket site #1 uses.
   Then pick a different one (e.g. if site #1 = 127.0.0.1:8000, use 8001; or a unix
   socket at $NEW_APP_DIR/$NEW_SERVICE.sock). Make deploy/gunicorn.service AND
   deploy/nginx.conf agree on the SAME NEW_BIND.

3. UNIQUE SYSTEMD UNIT NAMES: $NEW_SERVICE.service, $NEW_SERVICE-campaigns.service,
   $NEW_SERVICE-campaigns.timer. Never write to ohydev*.service/.timer.

4. NGINX: create a separate site file /etc/nginx/sites-available/$NEW_SERVICE,
   symlink into sites-enabled. server_name = $NEW_DOMAIN,www.$NEW_DOMAIN.
   proxy_pass / upstream must point to NEW_BIND. DO NOT run
   `rm -f /etc/nginx/sites-enabled/default` or remove any other enabled site —
   that could disturb site #1. Always run `nginx -t` before reload.

5. CERTBOT: issue a NEW cert only for -d $NEW_DOMAIN -d www.$NEW_DOMAIN.
   Do not touch site #1's existing certificate.

6. SHARED / ALREADY-DONE STEPS MUST BE NO-OPS: apt packages, ufw rules, and
   git safe.directory are already set up system-wide. Guard apt installs with
   `command -v` checks (like site #1's update.sh does). Do not run destructive
   firewall resets.

7. SECURITY: do NOT hardcode any GitHub token in the committed script. Read the
   repo URL/token from an environment variable or a clearly-marked placeholder,
   and never echo the token to stdout.

8. update.sh must mirror site #1's update.sh but fully namespaced: cd to
   $NEW_APP_DIR, load .env, DJANGO_SETTINGS_MODULE fallback, git pull, guarded
   apt, pip install, migrate, collectstatic, chown www-data, reinstall the
   $NEW_SERVICE-campaigns unit(s), daemon-reload, restart $NEW_SERVICE, then
   print $NEW_SERVICE status.

9. BOTH SCRIPTS: `set -euo pipefail`, root check, idempotent (safe to re-run
   halfway), clear `step`/echo output. The setup script should pause once to let
   me copy an existing DB/media (with a SKIP option for a fresh DB), same UX as
   site #1.

# DELIVERABLES
  - deploy/setup_vps.sh and deploy/update.sh (namespaced as above)
  - If deploy/gunicorn.service, deploy/nginx.conf, deploy/campaigns.service, or
    deploy/campaigns.timer exist in this repo, update them to use NEW_BIND and
    NEW_SERVICE names — or tell me exactly which lines to change.
  - A short summary at the end: "what differs from the ohydev version and why."

# REFERENCE — site #1's existing scripts (token stripped; model the new ones on these):

## site #1 setup_vps.sh
#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════
#  ONE-TIME VPS SETUP — Ohy.dev portfolio
#  Fresh Ubuntu 22.04 / 24.04 → fully deployed site with HTTPS.
#
#  How to use:
#    1. Edit the values in the "EDIT THESE" block below.
#    2. Copy this file to the VPS (from your local machine):
#         scp deploy/setup_vps.sh root@YOUR_VPS_IP:/root/
#    3. On the VPS, run:
#         sudo bash /root/setup_vps.sh
#
#  The script pauses once so you can copy your existing database
#  and media files — your current data is kept.
#  Safe to re-run if something fails halfway.
# ════════════════════════════════════════════════════════════════════
set -euo pipefail

# ╔══════════════════════════════════════════════════════════════════╗
# ║  EDIT THESE VALUES BEFORE RUNNING                                ║
# ╚══════════════════════════════════════════════════════════════════╝
DOMAIN="iftesamulohy.com"          # your domain WITHOUT www
CERTBOT_EMAIL="iftesamulohy@gmail.com"  # for Let's Encrypt expiry notices
REPO_URL="https://<GITHUB_TOKEN>@github.com/iftesamulohy/ohyportfolio.git"
# ^ If the repo is PRIVATE, include a GitHub token:
#   REPO_URL="https://YOUR_GITHUB_TOKEN@github.com/iftesamulohy/ohyportfolio.git"

# These match deploy/gunicorn.service and deploy/nginx.conf — only
# change them if you also edit those files.
APP_DIR="/var/www/ohydev"
SERVICE="ohydev"
# ════════════════════════════════════════════════════════════════════

[ "$EUID" -eq 0 ] || { echo "ERROR: run as root:  sudo bash $0"; exit 1; }

step() { echo; echo "════ $1 ════"; }

step "1/9  System packages"
apt-get update -y
# poppler-utils provides pdfinfo/pdfseparate/pdfunite, used to build the
# free book-preview PDFs (ProductPreviewView). Without it, content preview 404s.
apt-get install -y python3-venv python3-pip git nginx certbot python3-certbot-nginx ufw poppler-utils

step "2/9  Firewall"
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable

step "3/9  Clone repository → $APP_DIR"
mkdir -p /var/www
if [ -d "$APP_DIR/.git" ]; then
    echo "Already cloned — pulling latest."
    git -C "$APP_DIR" pull
else
    git clone "$REPO_URL" "$APP_DIR"
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
ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN
DJANGO_SETTINGS_MODULE=config.settings.production
SECURE_HSTS_SECONDS=31536000

# ── Fill these in later (site works without them) ──
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=

META_PIXEL_ID=
META_ACCESS_TOKEN=
META_API_VERSION=v19.0

UDDOKTAPAY_API_KEY=
UDDOKTAPAY_API_URL=
EOF
    echo "Created .env with a fresh SECRET_KEY and ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN"
    echo "NOTE: email + payment keys are blank — fill them in $APP_DIR/.env later,"
    echo "      then run:  systemctl restart $SERVICE"
fi

step "6/9  Your existing data (database + media)"
if [ ! -f db.sqlite3 ]; then
    echo "db.sqlite3 is NOT here yet. From your LOCAL machine, run:"
    echo
    echo "    scp ~/ohy_fold/port_dep/db.sqlite3 root@$(hostname -I | awk '{print $1}'):$APP_DIR/db.sqlite3"
    echo "    rsync -av ~/ohy_fold/port_dep/media/ root@$(hostname -I | awk '{print $1}'):$APP_DIR/media/"
    echo
    while [ ! -f db.sqlite3 ]; do
        read -rp "Press ENTER once copied (or type SKIP for a fresh empty database): " ans
        [ "${ans:-}" = "SKIP" ] && { echo "Continuing with a fresh database."; break; }
        [ -f db.sqlite3 ] || echo "Still not found — waiting."
    done
else
    echo "db.sqlite3 found — your existing data will be used."
fi

step "7/9  Migrate, collectstatic, permissions"
mkdir -p logs media
venv/bin/python manage.py migrate --noinput
venv/bin/python manage.py collectstatic --noinput
chown -R www-data:www-data "$APP_DIR"

step "8/9  Gunicorn (systemd) + Nginx"
cp deploy/gunicorn.service "/etc/systemd/system/$SERVICE.service"

# Email campaign dispatcher — a oneshot + timer that runs `send_due_campaigns`
# every 2 min, so scheduled campaigns go out without a Celery worker.
cp deploy/campaigns.service "/etc/systemd/system/$SERVICE-campaigns.service"
cp deploy/campaigns.timer   "/etc/systemd/system/$SERVICE-campaigns.timer"

systemctl daemon-reload
systemctl enable --now "$SERVICE"
systemctl restart "$SERVICE"
systemctl enable --now "$SERVICE-campaigns.timer"

sed "s/iftesamulohy\.com/$DOMAIN/g" deploy/nginx.conf > "/etc/nginx/sites-available/$SERVICE"
ln -sf "/etc/nginx/sites-available/$SERVICE" "/etc/nginx/sites-enabled/$SERVICE"
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx

step "9/9  HTTPS (Let's Encrypt)"
if certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" \
        --non-interactive --agree-tos -m "$CERTBOT_EMAIL" --redirect; then
    echo "HTTPS enabled — http:// now redirects to https://"
else
    echo "WARNING: certbot failed — usually DNS hasn't propagated to this server yet."
    echo "The site still works on http://$DOMAIN. Once DNS points here, run:"
    echo "    certbot --nginx -d $DOMAIN -d www.$DOMAIN --redirect"
fi

# ── SSH key for GitHub Actions auto-deploy ─────────────────────────
if [ ! -f /root/.ssh/github_deploy ]; then
    mkdir -p /root/.ssh && chmod 700 /root/.ssh
    ssh-keygen -t ed25519 -f /root/.ssh/github_deploy -N "" -C "github-actions-deploy" -q
    cat /root/.ssh/github_deploy.pub >> /root/.ssh/authorized_keys
    chmod 600 /root/.ssh/authorized_keys
fi

echo
echo "════════════════════════════════════════════════════════════════"
echo "  DONE — visit:  https://$DOMAIN"
echo "  Admin:         https://$DOMAIN/admin/  (your existing login)"
echo "════════════════════════════════════════════════════════════════"
echo
echo "To enable AUTO-DEPLOY on every push to main, add these 3 secrets"
echo "on GitHub → repo → Settings → Secrets and variables → Actions:"
echo
echo "  VPS_HOST     = $(hostname -I | awk '{print $1}')"
echo "  VPS_USER     = root"
echo "  VPS_SSH_KEY  = (paste EVERYTHING between the lines below)"
echo "────────────────────────────────────────────────────────────────"
cat /root/.ssh/github_deploy
echo "────────────────────────────────────────────────────────────────"
echo
echo "Service status:"
systemctl status "$SERVICE" --no-pager | head -5

## site #1 update.sh
#!/usr/bin/env bash
# Redeploy script — runs ON THE VPS (as root) after new code is pushed.
# Triggered automatically by GitHub Actions over SSH, or manually:
#   cd /var/www/ohydev && sudo bash deploy/update.sh
set -euo pipefail

APP_DIR=/var/www/ohydev
cd "$APP_DIR"

# ── Load production environment (DJANGO_SETTINGS_MODULE + secrets) ──
# Without this, manage.py falls back to dev settings, which breaks
# collectstatic on production (missing staticfiles manifest = 500).
if [ -f "$APP_DIR/.env" ]; then
    set -a
    source "$APP_DIR/.env"
    set +a
fi
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings.production}"

# Let root operate on the www-data-owned git repo without complaints
git config --global --add safe.directory "$APP_DIR" 2>/dev/null || true

echo "==> Pulling latest code"
git pull

echo "==> Ensuring system packages (poppler-utils for book-preview PDFs)"
# pdfinfo/pdfseparate/pdfunite power ProductPreviewView; without them the
# content preview 404s. Idempotent — apt is a no-op once installed.
if ! command -v pdfunite >/dev/null 2>&1; then
    apt-get update -y && apt-get install -y poppler-utils
fi

echo "==> Installing dependencies"
venv/bin/pip install -r requirements.txt -q

echo "==> Running migrations"
venv/bin/python manage.py migrate --noinput

echo "==> Collecting static files"
venv/bin/python manage.py collectstatic --noinput

echo "==> Fixing ownership"
chown -R www-data:www-data "$APP_DIR"

echo "==> Refreshing systemd units (campaign timer may have changed)"
# Reinstall + reload so edits to deploy/*.service|*.timer take effect on deploy.
cp deploy/campaigns.service /etc/systemd/system/ohydev-campaigns.service 2>/dev/null || true
cp deploy/campaigns.timer   /etc/systemd/system/ohydev-campaigns.timer   2>/dev/null || true
systemctl daemon-reload
systemctl enable --now ohydev-campaigns.timer 2>/dev/null || true

echo "==> Restarting Gunicorn"
systemctl restart ohydev

echo "==> Done. Service status:"
systemctl status ohydev --no-pager -l | head -10

# END OF REFERENCE

Before writing anything, confirm site #1's current Gunicorn bind and ask me about
any FILL-IN value you cannot infer.
````
