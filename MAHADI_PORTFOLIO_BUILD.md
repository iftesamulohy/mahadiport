# MAHADI_PORTFOLIO_BUILD.md
## Portfolio Website — Md Mahadi Hasan (Digital Marketer / Media Buyer)
### Dynamic site built with Django + HTMX + Alpine.js

> **Agent instruction:** This is a complete build specification. Follow it top to bottom. Every section is intentional — do not substitute generic defaults for the design decisions written here. Build phase by phase (Phase plan at the bottom) and verify the acceptance checklist before finishing.

---

## 1. Project Overview

**Who:** Md Mahadi Hasan — Social Media Marketing Executive at Scaleup IT Ltd (Dhaka, Bangladesh). Performance marketer specializing in Meta ads: Pixel & CAPI, GTM, GA4, Advantage+ campaigns, funnel architecture, UGC creative strategy, attribution modeling. Previously Sales Executive at Vitasoft Solutions.

**What:** A single-brand personal portfolio site that positions Mahadi as a *performance marketer who understands data*, not a generic "social media guy". Target audience: F-commerce owners, local businesses, and agencies in Bangladesh looking to hire a media buyer.

**The page's single job:** Convince a business owner within 15 seconds that Mahadi can lower their cost-per-lead and raise ROAS — then get them to contact him.

**Core requirements:**
- Fully dynamic: all content editable from Django admin (no hardcoded text in templates)
- Django + HTMX + Alpine.js (no React, no heavy JS frameworks)
- Light/Dark mode with smooth transition, persisted preference
- Signature interactive element: **live animated ad-performance curve** (details in §6)
- Scroll-reveal animations, counter animations, micro-interactions
- Contact form via HTMX (no page reload), leads saved to DB + admin
- Mobile-first responsive, fast (Lighthouse 90+), SEO-ready
- Meta Pixel + CAPI-ready (a marketer's own site MUST have proper tracking — this is a portfolio proof point in itself)

---

## 2. Tech Stack

| Layer | Choice | Notes |
|---|---|---|
| Backend | Django 5.x | Single project, 3 apps |
| Frontend interactivity | HTMX 2.x + Alpine.js 3.x | Self-host both files in `static/vendor/` (BDIX/offline-friendly, no CDN dependency) |
| Styling | Vanilla CSS with CSS custom properties | NO Tailwind. Theme system depends on CSS variables (§5). One `main.css`, organized by section comments |
| Database | PostgreSQL (production) / SQLite (dev) | Standard `dj-database-url` pattern |
| Animations | CSS transitions + `IntersectionObserver` + one small vanilla-JS module for the hero curve | No animation libraries (no GSAP, no AOS) — everything hand-rolled and lightweight |
| Fonts | Self-hosted via `@font-face` (download from Google Fonts, place in `static/fonts/`) | See §5 typography |
| Forms | Django forms + HTMX partial swap | Honeypot field for spam |
| Images | Pillow + `sorl-thumbnail` or plain `ImageField` with manual sizes | WebP where possible |
| Deployment target | VPS (Ubuntu 24.04), Gunicorn + Caddy | Caddy for auto-TLS. Docker optional |

---

## 3. Django Project Structure

```
mahadi_portfolio/
├── config/                 # project settings
│   ├── settings/
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── prod.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── core/               # site settings, theme, pages, SEO
│   ├── portfolio/          # experience, skills, case studies, testimonials, stats
│   └── leads/              # contact form, lead storage, notifications
├── templates/
│   ├── base.html
│   ├── partials/           # HTMX fragments
│   └── sections/           # homepage section includes
├── static/
│   ├── css/main.css
│   ├── js/
│   │   ├── theme.js        # dark/light toggle
│   │   ├── curve.js        # signature hero animation
│   │   └── reveal.js       # IntersectionObserver scroll reveals + counters
│   ├── vendor/             # htmx.min.js, alpine.min.js
│   └── fonts/
└── media/
```

---

## 4. Models (all content dynamic)

### `core.SiteSettings` (singleton — use `django-solo` or a `get_solo()` classmethod pattern)
```python
site_name           = CharField(default="Md Mahadi Hasan")
tagline             = CharField()          # e.g. "I make ad spend accountable."
hero_headline       = CharField()
hero_subtext        = TextField()
email               = EmailField(default="mahadihasanshawons@gmail.com")
phone               = CharField(default="+8801328885839")
location            = CharField(default="Jatrabari, Dhaka, Bangladesh")
facebook_url        = URLField(blank=True)
linkedin_url        = URLField(blank=True)
whatsapp_number     = CharField(blank=True)   # for wa.me link
cv_file             = FileField(blank=True)   # downloadable CV button
meta_pixel_id       = CharField(blank=True)
og_image            = ImageField(blank=True)
meta_description    = TextField(blank=True)
```

### `portfolio.Experience`
```python
company        = CharField()      # "Scaleup IT Ltd", "Vitasoft Solutions"
role           = CharField()      # "Social Media Marketing Executive"
location       = CharField()      # "Mohakhali, Dhaka"
start_date     = DateField()
end_date       = DateField(null=True, blank=True)   # null = "Present"
summary        = TextField(blank=True)
order          = PositiveIntegerField(default=0)
is_current     = BooleanField(default=False)
```

### `portfolio.ExperiencePoint`
```python
experience = FK(Experience, related_name="points")
text       = CharField(max_length=300)
order      = PositiveIntegerField(default=0)
```

### `portfolio.SkillCategory` + `portfolio.Skill`
```python
# SkillCategory: name ("Technical", "Strategic", "Creative", "Tools"), order
# Skill:
category    = FK(SkillCategory, related_name="skills")
name        = CharField()          # "Meta Pixel & CAPI", "GA4", "Advantage+ Campaigns"
proficiency = PositiveSmallIntegerField(default=80)  # 0–100, drives animated meter
icon        = CharField(blank=True)  # optional inline-SVG name or emoji
order       = PositiveIntegerField(default=0)
```

### `portfolio.CaseStudy`  ← the most important model
```python
title         = CharField()        # "Cut CPL 43% for a Dhaka F-commerce brand"
client_type   = CharField()        # "F-commerce (Fashion)" — anonymized is fine
slug          = SlugField(unique=True)
challenge     = TextField()
approach      = TextField()
result_text   = TextField()
cover_image   = ImageField(blank=True)
is_featured   = BooleanField(default=False)
order         = PositiveIntegerField(default=0)
created_at    = DateTimeField(auto_now_add=True)
```

### `portfolio.CaseStudyMetric`  ← powers before/after animated numbers
```python
case_study  = FK(CaseStudy, related_name="metrics")
label       = CharField()      # "Cost per lead", "ROAS", "CTR"
before_val  = CharField()      # "৳85"
after_val   = CharField()      # "৳48"
direction   = CharField(choices=[("down_good","Lower is better"),("up_good","Higher is better")])
numeric_after = FloatField(null=True, blank=True)  # for counter animation
```

### `portfolio.Testimonial`
```python
name, role_company, quote (TextField), avatar (ImageField, blank), order
# Render Messenger-style chat bubbles (see §7 Testimonials)
```

### `portfolio.StatCounter`  ← hero/stats strip counters
```python
label   = CharField()   # "Ad spend managed", "Campaigns run", "Avg. CPL reduction"
value   = FloatField()  # 1.2
suffix  = CharField()   # "M৳+", "+", "%"
order   = PositiveIntegerField()
```

### `leads.Lead`
```python
name        = CharField()
email       = EmailField(blank=True)
phone       = CharField()            # phone is primary in BD context — make it required, email optional
business    = CharField(blank=True)  # "What do you sell?"
monthly_budget = CharField(blank=True, choices=[("<10k","Under ৳10k"),("10-50k","৳10k–50k"),("50k+","৳50k+"),("na","Not sure yet")])
message     = TextField(blank=True)
source_path = CharField(blank=True)  # captured from hidden field (which page/section)
created_at  = DateTimeField(auto_now_add=True)
is_read     = BooleanField(default=False)
```

Seed script: create `apps/portfolio/management/commands/seed_site.py` that loads all real CV data below (§10) so the site is fully populated on first run.

---

## 5. Design System

> **Design thesis:** The subject's world is the *ads dashboard* — Ads Manager graphs, metric cards, attribution windows, green up-arrows and red down-arrows. The site should feel like a beautifully designed performance report, not a template portfolio. Confidence through data, warmth through Bengali-market context.

### 5.1 Color tokens (CSS custom properties — the entire theme system)

```css
:root {                          /* LIGHT — "daylight report" */
  --bg:            #F7F8FA;      /* cool paper, not cream */
  --bg-elev:       #FFFFFF;      /* cards */
  --ink:           #101623;      /* near-black navy ink */
  --ink-soft:      #4A5568;
  --line:          #E3E7EE;
  --accent:        #1D6FF2;      /* "Meta blue" pushed deeper — the trade tool's own color, owned deliberately */
  --accent-ink:    #FFFFFF;
  --signal-up:     #16A34A;      /* conversion green — used ONLY for positive metrics/arrows */
  --signal-down:   #DC2626;      /* used ONLY for "before" / cost metrics */
  --curve-glow:    rgba(29,111,242,.18);
}

[data-theme="dark"] {            /* DARK — "war-room at night" */
  --bg:            #0A0F1A;
  --bg-elev:       #111827;
  --ink:           #EDF1F7;
  --ink-soft:      #94A3B8;
  --line:          #1F2937;
  --accent:        #4D8DFF;
  --accent-ink:    #06101F;
  --signal-up:     #34D399;
  --signal-down:   #F87171;
  --curve-glow:    rgba(77,141,255,.25);
}
```

Rules:
- **Every** color in the CSS must come from these variables. Zero hardcoded hex in component styles.
- `--signal-up`/`--signal-down` are semantic: green means a metric improved, red means the "before" state. Never use them decoratively.
- Add `html { transition: background-color .35s ease, color .35s ease; }` plus per-card transitions so theme toggle feels like a dashboard switching to night mode.

### 5.2 Typography

- **Display:** `Sora` (700/800) — geometric, techy but friendly; used for headlines and big metric numbers.
- **Body:** `Inter` (400/500/600).
- **Data/labels:** `JetBrains Mono` (500) — used for metric labels, eyebrow labels ("CASE STUDY 01"), the ticking numbers in the hero curve, and dates. The mono face is what makes the "dashboard" feel real.
- Self-host all three in `static/fonts/` with `font-display: swap`.
- Type scale: hero clamp `clamp(2.2rem, 6vw, 4rem)`; section titles `clamp(1.6rem, 3.5vw, 2.4rem)`; metric numbers in mono at display sizes.

### 5.3 Layout language

- Max content width `1120px`, generous whitespace, `border-radius: 14px` on cards, 1px `--line` borders instead of heavy shadows (subtle `box-shadow` only on hover).
- **Eyebrow labels in JetBrains Mono uppercase** above every section title, styled like dashboard breadcrumbs: `// EXPERIENCE`, `// CASE STUDIES`, `// SKILLS`.
- Section order on homepage: Hero → Stats strip → Case Studies → Skills → Experience timeline → Testimonials → Contact → Footer.

---

## 6. ⭐ SIGNATURE ELEMENT — The Live Performance Curve (hero)

This is the one bold, memorable thing. Everything else stays disciplined.

**Concept:** The hero is split. Left: headline + subtext + CTA. Right (stacked below on mobile): a **live-animating SVG ad-performance chart** that looks like a real Ads Manager graph running on its own.

**Behavior spec (`static/js/curve.js`, vanilla JS, ~150 lines):**

1. An SVG (`viewBox="0 0 600 320"`) with a faint grid (mono-styled axis labels: `Day 1 … Day 30`).
2. **Two lines animate simultaneously:**
   - **ROAS line** (`--accent`, 2.5px, with a soft `--curve-glow` area fill under it): trends *upward* with realistic noise — small dips, then recovery, overall climb. Generated procedurally: random-walk with positive drift, new point every ~900ms, line redraws with smooth `d` path interpolation (use a simple cubic smoothing function between points).
   - **CPL line** (`--signal-down`, 1.5px, dashed): trends *downward* with noise — mirrors the story "cost goes down while return goes up."
3. A **moving dot** rides the tip of the ROAS line with a pulsing halo (`animation: pulse 1.6s infinite`).
4. **Ticking metric chips** float above the chart (absolutely positioned cards, mono font):
   - `ROAS 4.2x ▲` — number counts up/down live matching the curve tip, arrow uses `--signal-up`
   - `CPL ৳48 ▼` — matching the CPL line, ▼ in `--signal-up` color (because lower CPL is GOOD — this detail matters, a real media buyer will notice)
5. When the curve reaches the right edge, it smoothly scrolls left (window slides) — infinite ambient motion, like a live dashboard.
6. **Interactive:** on hover/touch over the chart, show a mono tooltip crosshair with fake but plausible values ("Day 17 · ROAS 3.8x · CPL ৳52"). On the hero CTA button hover, briefly boost the ROAS line's drift upward for 2 seconds (playful cause-and-effect: "hire me → graph goes up"). Subtle, don't announce it.
7. **`prefers-reduced-motion: reduce`** → render a static pre-drawn version of both curves with final metric values. Mandatory.
8. Keep total JS under ~6KB. No canvas, no libraries — pure SVG path manipulation.

**Hero copy (seed values, editable in admin):**
- Eyebrow (mono): `// PERFORMANCE MARKETER · DHAKA`
- Headline: **"Ad spend that answers for itself."**
- Subtext: "I run Meta campaigns for Bangladeshi businesses with proper tracking — Pixel, CAPI, GA4 — so every taka is attributed, and every decision is data. Lower CPL. Higher ROAS. No guesswork."
- Primary CTA: `Book a free audit` (scrolls to contact) · Secondary: `Download CV` (from `SiteSettings.cv_file`)

---

## 7. Sections & Interactions (homepage)

### 7.1 Stats strip (below hero)
Horizontal row of `StatCounter` values. Numbers **count up** when scrolled into view (IntersectionObserver in `reveal.js`, ease-out over 1.2s, mono font). Seed: `2+ Years in performance marketing` · `30+ Campaigns managed` · `40% Avg. CPL reduction` · `100% Tracking accuracy (Pixel+CAPI)`.

### 7.2 Case Studies
- Grid of cards. Each card shows title, client type chip, and its **metrics as before→after pills**: `CPL ৳85 → ৳48` where the "before" is struck-through in `--signal-down` tone and "after" glows `--signal-up`.
- Card click → HTMX `hx-get="/case/<slug>/panel/"` loads a **detail panel** into a slide-over drawer (Alpine handles open/close, HTMX fetches content). URL updates via `hx-push-url`. Deep-linkable: direct visit to `/case/<slug>/` renders full page with the drawer pre-opened.
- Inside the panel, metric numbers animate (count from before-value to after-value) when opened.
- If Mahadi has no public case studies yet: seed 3 **anonymized, realistic** ones marked "Client under NDA — figures representative" (Challenge/Approach/Result written from his actual Scaleup work: Advantage+ restructure, CAPI implementation fixing attribution, UGC creative testing sprint).

### 7.3 Skills
- Tabbed by `SkillCategory` (HTMX `hx-get` swaps the tab panel — genuinely dynamic, not hidden divs).
- Each skill renders as a row: name + **animated meter bar** that fills to `proficiency%` on reveal, with the percentage ticking up in mono beside it.
- Categories seeded: **Technical** (Meta Pixel & CAPI, GTM, GA4, CRM Integration, Attribution Modeling), **Strategic** (Advantage+ Campaigns, Incrementality Testing, Media Buying, Funnel Architecture), **Creative** (UGC Creative Strategy, AI-Driven Ad Generation, Dynamic Creative Optimization), **Tools** (Meta Business Suite, Canva, WordPress, MS Office).

### 7.4 Experience timeline
- Vertical timeline, line drawn in `--line`, nodes pulse in `--accent` when scrolled into view. Current role node has a live "● Running" badge in `--signal-up`.
- Each entry: role, company, dates (mono), location, bullet points from `ExperiencePoint`.
- Entries reveal with staggered fade-up (80ms stagger).

### 7.5 Testimonials — Messenger-style
- Rendered as **chat bubbles** (left-aligned bubble with avatar, name + role beneath) — F-commerce clients literally live in Messenger, so this framing is native to the audience.
- Bubbles pop in sequentially on reveal with a tiny "typing dots → bubble" animation for the first one only (once, not looping).

### 7.6 Contact (lead form)
- Two-column: left = pitch ("Free 20-minute ad account audit — ami dekhbo kothay taka leak hocche.") + phone/WhatsApp/email links; right = the form.
- Fields: Name, Phone (required), Email (optional), What do you sell?, Monthly ad budget (select), Message.
- Submit via `hx-post="/leads/submit/"` → server validates → returns success partial (green check animation + "Pabo apnake 24 ghontar moddhe — check your phone!") swapped in place. Errors return the form partial with inline field errors. Honeypot hidden field `website` — if filled, silently return success without saving.
- On success, fire Meta Pixel `Lead` event (only if `meta_pixel_id` set).

### 7.7 Footer
Minimal: name, one-line tagline, social links, "Built with Django + HTMX" (a small credibility flex), theme toggle repeated, copyright year via template tag.

---

## 8. Theme System (light/dark)

- `data-theme` attribute on `<html>`. Default: **respect `prefers-color-scheme`** on first visit, then persist explicit choice.
- Persistence: `localStorage` + a cookie (`theme=dark`) so Django can render the correct `data-theme` server-side and **avoid flash-of-wrong-theme**. Inline `<script>` in `<head>` (before CSS) reads localStorage as fallback and sets the attribute immediately.
- Toggle UI: a pill switch in the navbar — **sun/moon is fine, but style it as a dashboard toggle**: mono label flips `LIGHT ⇄ DARK`. Animate the knob with a spring-ish cubic-bezier.
- When theme flips, the hero curve's glow and grid colors transition too (they use variables, so this is free — verify it).

---

## 9. Navbar & Global Behavior

- Sticky navbar, transparent over hero → gains `--bg-elev` background + bottom border after 40px scroll (tiny JS or Alpine `@scroll.window`).
- Links: Case Studies · Skills · Experience · Contact + theme toggle + `Book audit` button.
- Smooth-scroll with `scroll-margin-top` on sections. Active section highlighted via IntersectionObserver.
- Mobile: hamburger → full-screen overlay menu (Alpine), links stagger in.

---

## 10. Seed Data (real CV content — use exactly)

**Experience 1 — current:**
- Scaleup IT Ltd · Social Media Marketing Executive · Mohakhali, Dhaka · Nov 2024 – Present
- Points: developed and implemented social media strategies to attract clients and build brand awareness; managed and optimized paid campaigns — improved conversion rates, lowered cost per lead, increased overall ROAS; implemented Meta Pixel & CAPI, GTM, GA4, CRM integration and attribution modeling; ran Advantage+ campaigns, incrementality testing, media buying and funnel architecture; led UGC creative strategy, AI-driven ad generation and dynamic creative optimization.

**Experience 2:**
- Vitasoft Solutions · Sales Executive · Dholaipar, Dhaka · Oct 2022 – Nov 2023
- Points: sold software & IT services to businesses and individual clients; consistently met and exceeded sales targets through needs-based selling; built long-term client relationships driving repeat business; delivered product demos and closed deals; used CRM to track leads, follow-ups and sales performance.

**Education (render as a compact block under Experience, or in About):**
- BBA in Accounting — Dhaka College (running) · HSC Business Studies — Dhaka City College, 2018, GPA 4.00/5 · SSC Business Studies — Kadamtala Purbo Bashabo School & College, 2016, GPA 4.39/5.

**Languages:** Bangla (native), English (fluent).

**Contact:** phone +8801328885839 · email mahadihasanshawons@gmail.com · South Jatrabari, Dhaka 1204.

> ⚠️ Do NOT copy the CV's weak "Career Objective" or "Ability and Skills" filler lines ("good inner personal skills" etc.) onto the site. The site's copy is written fresh per §6–7. The CV file itself can still be attached as the downloadable PDF.

---

## 11. SEO, Analytics, Performance

- Per-page `<title>` + meta description from `SiteSettings` / CaseStudy fields; OG tags + `og_image`; JSON-LD `Person` schema (name, jobTitle, address locality Dhaka, sameAs social links).
- Meta Pixel base code injected in `base.html` **only when** `meta_pixel_id` is set; `PageView` on load, `Lead` on form success, `Contact` on WhatsApp/phone click.
- Sitemap (`django.contrib.sitemaps`) + robots.txt.
- Performance: self-hosted fonts preloaded, images `loading="lazy"` below the fold, hero SVG is inline (no request), HTMX/Alpine deferred. Target Lighthouse ≥90 all categories.
- Accessibility: visible focus rings (`--accent` outline), aria-labels on toggle and drawer, form labels always visible (no placeholder-only), contrast checked in BOTH themes, `prefers-reduced-motion` respected everywhere (curve, counters, reveals all degrade to static/instant).

---

## 12. Build Phases

1. **Phase 1 — Skeleton:** project setup, apps, models, migrations, admin registration (with inlines: ExperiencePoint under Experience, Metric under CaseStudy), seed command with all §10 data.
2. **Phase 2 — Base template & design system:** `base.html`, CSS variables, fonts, navbar, footer, theme toggle with cookie+localStorage persistence, no-flash inline script.
3. **Phase 3 — Hero + signature curve:** hero layout, `curve.js` per §6 spec including reduced-motion fallback and hover crosshair.
4. **Phase 4 — Sections:** stats counters, case studies grid + HTMX drawer + detail routes, skills tabs + meters, experience timeline, testimonials, `reveal.js` (single IntersectionObserver handling reveals, counters, meters).
5. **Phase 5 — Leads:** form, HTMX submit flow, honeypot, admin list with `is_read` filter, optional email notification to Mahadi on new lead (console backend in dev).
6. **Phase 6 — Polish:** SEO/schema/pixel, sitemap, 404 page (dashboard-styled: "404 — This funnel has no conversions"), responsive audit at 360px/768px/1120px, Lighthouse pass, both-themes visual QA.

## 13. Acceptance Checklist

- [ ] All homepage content editable via admin; seed command populates everything
- [ ] Theme toggles with no flash on reload, persists, respects system preference on first visit
- [ ] Hero curve animates (two lines, ticking chips, moving dot), pauses/statics under reduced motion, hover crosshair works
- [ ] Case study drawer loads via HTMX, deep-links work, metrics animate before→after
- [ ] Skills tabs swap via HTMX; meters animate on reveal
- [ ] Contact form submits without reload, validates, saves Lead, blocks honeypot, fires Pixel Lead event when pixel configured
- [ ] Mobile menu, sticky navbar state, smooth scrolling all work at 360px width
- [ ] Zero hardcoded colors outside the token block; both themes pass contrast
- [ ] Lighthouse ≥90 across the board
