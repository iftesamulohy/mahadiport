# Md Mahadi Hasan — Portfolio

Dynamic personal portfolio for a performance marketer / Meta media buyer, built with
**Django 5 + HTMX + Alpine.js**. All content is editable from the Django admin; the
homepage's signature element is a live-animating SVG ad-performance curve.

## Stack
- Django 5.1, PostgreSQL (prod) / SQLite (dev)
- HTMX 2 + Alpine.js 3 (self-hosted in `static/vendor/`, no CDN)
- Vanilla CSS with custom-property theming (light/dark), self-hosted fonts
- WhiteNoise for static files, Gunicorn + Caddy target for deploy

## Project layout
```
config/settings/{base,dev,prod}.py   # split settings
apps/core/        # SiteSettings singleton, context processor, sitemaps, robots, 404
apps/portfolio/   # experience, skills, case studies, testimonials, stats + seed_site
apps/leads/       # contact form, lead storage, HTMX submit, email notify
templates/        # base.html, sections/, partials/, emails/
static/           # css/main.css, js/{theme,curve,reveal}.js, vendor/, fonts/
```

## Setup (dev)
```bash
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/python manage.py migrate
./venv/bin/python manage.py seed_site          # loads all real CV content
./venv/bin/python manage.py createsuperuser
./venv/bin/python manage.py runserver
```
Visit http://127.0.0.1:8000/ and the admin at /admin/.

Re-seed from scratch: `python manage.py seed_site --fresh`.

## Configuration
Copy the sample env values into `.env` (already present in dev). Key vars:
- `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`
- `DATABASE_URL` (e.g. `postgres://user:pass@host:5432/db`)
- `LEAD_NOTIFY_EMAIL`, `EMAIL_HOST*` (prod SMTP; dev prints to console)

Set the **Meta Pixel ID**, social links, CV file and OG image from
Admin → Site Core → Site Settings. The Pixel base code (PageView / Lead / Contact
events) only renders when a Pixel ID is set.

## Production
```bash
export DJANGO_SETTINGS_MODULE=config.settings.prod
python manage.py collectstatic --noinput
gunicorn config.wsgi:application
```
Put Caddy in front for auto-TLS. Set a real 50+ char `SECRET_KEY`.

## Internationalization (English / বাংলা)
- Default language is **English** (foreign + local clients); a navbar switcher
  toggles Bangla. Preference is stored in the `django_language` cookie via
  `set_language`, and `LocaleMiddleware` serves the right language.
- Dynamic content is bilingual via **django-modeltranslation** (admin shows
  per-language tabs). Currency is USD (`$`) throughout — Meta budgets are managed
  in dollars.
- Static UI strings use Django's `{% translate %}` / `gettext`. The environment
  has no `gettext` CLI, so the Bangla catalog is authored + compiled with polib:
  edit `scripts/build_messages.py`, then run
  `./venv/bin/python scripts/build_messages.py` (writes `locale/bn/LC_MESSAGES/django.{po,mo}`).
- Translatable model fields carry **no** `default=` — modeltranslation treats a
  base value equal to the field default as "unset", which corrupts the default
  language. Keep new translatable fields default-less.

## Notes
- Theme is persisted via `localStorage` + a `theme` cookie so Django renders the
  correct `data-theme` server-side (no flash).
- Everything degrades under `prefers-reduced-motion` (curve → static, counters →
  final values, reveals → instant).
- Visual QA was done with Playwright (`pip install playwright`; uses system Chrome).
