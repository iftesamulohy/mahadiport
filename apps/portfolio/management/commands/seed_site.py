"""
Seed the site with Md Mahadi Hasan's real CV data (§10) plus hand-written
portfolio copy, in BOTH English and Bangla. Currency is USD ($) throughout —
Meta ad budgets are managed in dollars, including for foreign clients.

Idempotent: safe to re-run.

    python manage.py seed_site
    python manage.py seed_site --fresh   # wipe portfolio content first
"""

from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import translation

from apps.core.models import SiteSettings
from apps.portfolio.models import (
    CaseStudy,
    CaseStudyMetric,
    Experience,
    ExperiencePoint,
    Skill,
    SkillCategory,
    StatCounter,
    Testimonial,
)


class Command(BaseCommand):
    help = "Populate the site with Mahadi's real CV data and portfolio copy (EN + BN)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--fresh",
            action="store_true",
            help="Delete existing portfolio content before seeding.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        # Management commands run with translations deactivated; modeltranslation
        # needs an active language so base fields resolve to the default (en).
        translation.activate("en")

        if options["fresh"]:
            self.stdout.write("Wiping existing portfolio content…")
            for model in (
                CaseStudyMetric,
                CaseStudy,
                ExperiencePoint,
                Experience,
                Skill,
                SkillCategory,
                Testimonial,
                StatCounter,
            ):
                model.objects.all().delete()

        self._seed_site_settings()
        self._seed_experience()
        self._seed_skills()
        self._seed_stats()
        self._seed_case_studies()
        self._seed_testimonials()

        self.stdout.write(self.style.SUCCESS("✔ Site seeded successfully (EN + BN)."))

    # ------------------------------------------------------------------ #

    def _seed_site_settings(self):
        # Recreate the singleton from scratch via a single create() with base +
        # _bn kwargs. This is the code path modeltranslation handles correctly
        # (attribute-assignment on the singleton leaves the base column stale).
        SiteSettings.objects.all().delete()
        SiteSettings.objects.create(
            pk=1,
            site_name="Md Mahadi Hasan",
            email="mahadihasanshawons@gmail.com",
            phone="+8801328885839",
            whatsapp_number="8801328885839",
            # _en passed explicitly: modeltranslation treats a base value equal to
            # the model's field default as "unset", so we pin the English field.
            tagline="I make ad spend accountable.",
            tagline_en="I make ad spend accountable.",
            tagline_bn="প্রতিটি বিজ্ঞাপন খরচকে জবাবদিহিতে আনি।",
            hero_eyebrow="// PERFORMANCE MARKETER · DHAKA",
            hero_eyebrow_en="// PERFORMANCE MARKETER · DHAKA",
            hero_eyebrow_bn="// পারফরম্যান্স মার্কেটার · ঢাকা",
            hero_headline="Ad spend that answers for itself.",
            hero_headline_en="Ad spend that answers for itself.",
            hero_headline_bn="যে অ্যাড খরচ নিজেই নিজের হিসাব দেয়।",
            hero_subtext=(
                "I run Meta campaigns for local and international businesses with "
                "proper tracking — Pixel, CAPI, GA4 — so every dollar is attributed, "
                "and every decision is data. Lower CPL. Higher ROAS. No guesswork."
            ),
            hero_subtext_bn=(
                "আমি দেশি ও বিদেশি ব্যবসার জন্য মেটা ক্যাম্পেইন চালাই — সঠিক ট্র্যাকিং "
                "সহ (Pixel, CAPI, GA4)। ফলে প্রতিটি ডলারের হিসাব থাকে, আর প্রতিটি "
                "সিদ্ধান্ত হয় ডেটা-ভিত্তিক। কম CPL, বেশি ROAS — কোনো অনুমান নয়।"
            ),
            meta_description=(
                "Md Mahadi Hasan — performance marketer & Meta media buyer based in "
                "Dhaka, working with local and international clients. Pixel & CAPI, "
                "GA4, Advantage+ campaigns. Lower CPL, higher ROAS."
            ),
            meta_description_bn=(
                "মো মাহাদি হাসান — ঢাকা-ভিত্তিক পারফরম্যান্স মার্কেটার ও মেটা মিডিয়া "
                "বায়ার, দেশি ও বিদেশি ক্লায়েন্টের সাথে কাজ করেন। Pixel ও CAPI, GA4, "
                "Advantage+ ক্যাম্পেইন। কম CPL, বেশি ROAS।"
            ),
            location="South Jatrabari, Dhaka 1204, Bangladesh",
            location_bn="সাউথ যাত্রাবাড়ী, ঢাকা ১২০৪, বাংলাদেশ",
        )
        self.stdout.write("  · Site settings")

    def _seed_experience(self):
        experiences = [
            {
                "company": "Scaleup IT Ltd",
                "role": "Social Media Marketing Executive",
                "role_bn": "সোশ্যাল মিডিয়া মার্কেটিং এক্সিকিউটিভ",
                "location": "Mohakhali, Dhaka",
                "location_bn": "মহাখালী, ঢাকা",
                "start_date": date(2024, 11, 1),
                "end_date": None,
                "is_current": True,
                "order": 0,
                "points": [
                    (
                        "Developed and implemented social media strategies to attract "
                        "clients and build brand awareness.",
                        "ক্লায়েন্ট আকর্ষণ ও ব্র্যান্ড সচেতনতা বাড়াতে সোশ্যাল মিডিয়া "
                        "স্ট্র্যাটেজি তৈরি ও বাস্তবায়ন করেছি।",
                    ),
                    (
                        "Managed and optimized paid campaigns — improved conversion "
                        "rates, lowered cost per lead, and increased overall ROAS.",
                        "পেইড ক্যাম্পেইন পরিচালনা ও অপটিমাইজ করেছি — কনভার্সন রেট "
                        "বাড়িয়ে, কস্ট পার লিড কমিয়ে সামগ্রিক ROAS বাড়িয়েছি।",
                    ),
                    (
                        "Implemented Meta Pixel & CAPI, GTM, GA4, CRM integration and "
                        "attribution modeling for accurate, privacy-safe tracking.",
                        "সঠিক ও প্রাইভেসি-নিরাপদ ট্র্যাকিংয়ের জন্য Meta Pixel ও CAPI, "
                        "GTM, GA4, CRM ইন্টিগ্রেশন এবং অ্যাট্রিবিউশন মডেলিং সেটআপ করেছি।",
                    ),
                    (
                        "Ran Advantage+ campaigns, incrementality testing, media buying "
                        "and funnel architecture.",
                        "Advantage+ ক্যাম্পেইন, ইনক্রিমেন্টালিটি টেস্টিং, মিডিয়া বায়িং "
                        "এবং ফানেল আর্কিটেকচার নিয়ে কাজ করেছি।",
                    ),
                    (
                        "Led UGC creative strategy, AI-driven ad generation and dynamic "
                        "creative optimization.",
                        "UGC ক্রিয়েটিভ স্ট্র্যাটেজি, AI-চালিত অ্যাড তৈরি এবং ডায়নামিক "
                        "ক্রিয়েটিভ অপটিমাইজেশন পরিচালনা করেছি।",
                    ),
                ],
            },
            {
                "company": "Vitasoft Solutions",
                "role": "Sales Executive",
                "role_bn": "সেলস এক্সিকিউটিভ",
                "location": "Dholaipar, Dhaka",
                "location_bn": "ধোলাইপাড়, ঢাকা",
                "start_date": date(2022, 10, 1),
                "end_date": date(2023, 11, 1),
                "is_current": False,
                "order": 1,
                "points": [
                    (
                        "Sold software & IT services to businesses and individual clients.",
                        "ব্যবসা ও ব্যক্তিগত ক্লায়েন্টের কাছে সফটওয়্যার ও আইটি সেবা "
                        "বিক্রি করেছি।",
                    ),
                    (
                        "Consistently met and exceeded sales targets through needs-based "
                        "selling.",
                        "চাহিদা-ভিত্তিক বিক্রয়ের মাধ্যমে ধারাবাহিকভাবে সেলস টার্গেট "
                        "পূরণ ও অতিক্রম করেছি।",
                    ),
                    (
                        "Built long-term client relationships driving repeat business.",
                        "দীর্ঘমেয়াদি ক্লায়েন্ট সম্পর্ক গড়ে তুলে রিপিট ব্যবসা এনেছি।",
                    ),
                    (
                        "Delivered product demos and closed deals.",
                        "প্রোডাক্ট ডেমো দিয়েছি এবং ডিল ক্লোজ করেছি।",
                    ),
                    (
                        "Used CRM to track leads, follow-ups and sales performance.",
                        "লিড, ফলো-আপ ও সেলস পারফরম্যান্স ট্র্যাক করতে CRM ব্যবহার করেছি।",
                    ),
                ],
            },
        ]
        for data in experiences:
            points = data.pop("points")
            exp, _ = Experience.objects.update_or_create(
                company=data["company"], defaults=data
            )
            exp.points.all().delete()
            for i, (en, bn) in enumerate(points):
                ExperiencePoint.objects.create(
                    experience=exp, text=en, text_bn=bn, order=i
                )
        self.stdout.write("  · Experience (2)")

    def _seed_skills(self):
        # (English name, Bangla name)
        categories = [
            (
                ("Technical", "টেকনিক্যাল"),
                [
                    ("Meta Pixel & CAPI", 95),
                    ("Google Tag Manager (GTM)", 88),
                    ("Google Analytics 4 (GA4)", 90),
                    ("CRM Integration", 82),
                    ("Attribution Modeling", 85),
                ],
            ),
            (
                ("Strategic", "স্ট্র্যাটেজিক"),
                [
                    ("Advantage+ Campaigns", 92),
                    ("Incrementality Testing", 80),
                    ("Media Buying", 90),
                    ("Funnel Architecture", 88),
                ],
            ),
            (
                ("Creative", "ক্রিয়েটিভ"),
                [
                    ("UGC Creative Strategy", 87),
                    ("AI-Driven Ad Generation", 84),
                    ("Dynamic Creative Optimization", 86),
                ],
            ),
            (
                ("Tools", "টুলস"),
                [
                    ("Meta Business Suite", 93),
                    ("Canva", 85),
                    ("WordPress", 78),
                    ("MS Office", 88),
                ],
            ),
        ]
        from django.utils.text import slugify

        for ci, ((name_en, name_bn), skills) in enumerate(categories):
            cat, _ = SkillCategory.objects.update_or_create(
                slug=slugify(name_en),
                defaults={"name": name_en, "name_bn": name_bn, "order": ci},
            )
            # Skill names are technical/brand terms — kept identical in both languages.
            for si, (name, prof) in enumerate(skills):
                Skill.objects.update_or_create(
                    category=cat,
                    name=name,
                    defaults={"proficiency": prof, "order": si},
                )
        self.stdout.write("  · Skills (4 categories)")

    def _seed_stats(self):
        # (label_en, label_bn, value, suffix, order)
        stats = [
            ("Years in performance marketing", "বছর পারফরম্যান্স মার্কেটিংয়ে", 2, "+", 0),
            ("Campaigns managed", "ক্যাম্পেইন পরিচালিত", 30, "+", 1),
            ("Avg. CPL reduction", "গড় CPL হ্রাস", 40, "%", 2),
            ("Tracking accuracy (Pixel+CAPI)", "ট্র্যাকিং নির্ভুলতা (Pixel+CAPI)", 100, "%", 3),
        ]
        for label_en, label_bn, value, suffix, order in stats:
            StatCounter.objects.update_or_create(
                label=label_en,
                defaults={
                    "label_bn": label_bn,
                    "value": value,
                    "suffix": suffix,
                    "order": order,
                },
            )
        self.stdout.write("  · Stat counters (4)")

    def _seed_case_studies(self):
        cases = [
            {
                "slug": "advantage-plus-restructure",
                "is_featured": True,
                "order": 0,
                "title": "Cut CPL 43% for an F-commerce brand",
                "title_bn": "একটি F-কমার্স ব্র্যান্ডের CPL ৪৩% কমিয়েছি",
                "client_type": "F-commerce (Fashion)",
                "client_type_bn": "F-কমার্স (ফ্যাশন)",
                "challenge": (
                    "A growing fashion F-commerce brand was scaling spend but watching "
                    "cost-per-lead climb. Ad sets overlapped, audiences cannibalised "
                    "each other, and the account leaned on manual interest targeting "
                    "that had stopped delivering."
                ),
                "challenge_bn": (
                    "একটি বাড়ন্ত ফ্যাশন F-কমার্স ব্র্যান্ড খরচ বাড়াচ্ছিল, কিন্তু "
                    "কস্ট-পার-লিডও বাড়ছিল। অ্যাড সেটগুলো একে অপরের সাথে ওভারল্যাপ "
                    "করছিল, অডিয়েন্স নিজেদের মধ্যে প্রতিযোগিতা করছিল, আর অ্যাকাউন্টটি "
                    "এমন ম্যানুয়াল ইন্টারেস্ট টার্গেটিংয়ের উপর নির্ভর করছিল যা আর "
                    "কাজ করছিল না।"
                ),
                "approach": (
                    "Consolidated fragmented ad sets into a clean Advantage+ Shopping "
                    "structure, freed the budget from manual audience silos, and let "
                    "Meta's signal do the work — backed by clean conversion events so "
                    "the algorithm optimised on real purchases, not proxies."
                ),
                "approach_bn": (
                    "ছড়িয়ে থাকা অ্যাড সেটগুলোকে একটি পরিষ্কার Advantage+ Shopping "
                    "স্ট্রাকচারে একত্র করেছি, বাজেটকে ম্যানুয়াল অডিয়েন্স সাইলো থেকে "
                    "মুক্ত করেছি, এবং মেটার সিগন্যালকে কাজ করতে দিয়েছি — পরিষ্কার "
                    "কনভার্সন ইভেন্ট দিয়ে, যাতে অ্যালগরিদম আসল পারচেজের উপর অপটিমাইজ "
                    "করে।"
                ),
                "result_en": (
                    "Within six weeks CPL fell 43%, ROAS climbed past 4x, and the brand "
                    "scaled daily budget without the usual efficiency drop. "
                    "(Client under NDA — figures representative.)"
                ),
                "result_bn": (
                    "ছয় সপ্তাহের মধ্যে CPL ৪৩% কমে যায়, ROAS ৪x ছাড়িয়ে যায়, এবং "
                    "ব্র্যান্ডটি দৈনিক বাজেট বাড়ায় স্বাভাবিক দক্ষতা হ্রাস ছাড়াই। "
                    "(ক্লায়েন্ট NDA-এর অধীনে — সংখ্যাগুলো প্রতিনিধিত্বমূলক।)"
                ),
                "metrics": [
                    ("Cost per lead", "কস্ট পার লিড", "$6.20", "$3.40", "down_good", 6.20, 3.40, "$", "", 0),
                    ("ROAS", "ROAS", "2.1x", "4.3x", "up_good", 2.1, 4.3, "", "x", 1),
                    ("CTR", "CTR", "1.2%", "2.4%", "up_good", 1.2, 2.4, "", "%", 2),
                ],
            },
            {
                "slug": "capi-attribution-fix",
                "is_featured": True,
                "order": 1,
                "title": "Fixed broken attribution with Pixel + CAPI",
                "title_bn": "Pixel + CAPI দিয়ে ভাঙা অ্যাট্রিবিউশন ঠিক করেছি",
                "client_type": "Local service business",
                "client_type_bn": "লোকাল সার্ভিস ব্যবসা",
                "challenge": (
                    "iOS updates and browser tracking loss had gutted the client's "
                    "reported conversions. Meta was optimising blind — half the leads "
                    "never made it back to the platform, so scaling meant guessing."
                ),
                "challenge_bn": (
                    "iOS আপডেট আর ব্রাউজার ট্র্যাকিং হারানোর কারণে ক্লায়েন্টের রিপোর্ট "
                    "করা কনভার্সন প্রায় শেষ হয়ে গিয়েছিল। মেটা অন্ধভাবে অপটিমাইজ "
                    "করছিল — অর্ধেক লিড প্ল্যাটফর্মে ফিরে আসত না, তাই স্কেল করা মানেই "
                    "ছিল অনুমান।"
                ),
                "approach": (
                    "Deployed the Conversions API alongside the Pixel with proper event "
                    "deduplication, wired server-side events through GTM, and aligned "
                    "GA4 as an independent source of truth to validate every event."
                ),
                "approach_bn": (
                    "Pixel-এর পাশাপাশি সঠিক ইভেন্ট ডিডুপ্লিকেশন সহ Conversions API "
                    "চালু করেছি, GTM দিয়ে সার্ভার-সাইড ইভেন্ট সেটআপ করেছি, এবং প্রতিটি "
                    "ইভেন্ট যাচাই করতে GA4-কে স্বাধীন সোর্স অফ ট্রুথ হিসেবে সাজিয়েছি।"
                ),
                "result_en": (
                    "Event Match Quality jumped and reported conversions rose 38% as "
                    "previously-lost leads reappeared. With trustworthy signal, "
                    "optimisation stabilised and CPL dropped. "
                    "(Client under NDA — figures representative.)"
                ),
                "result_bn": (
                    "Event Match Quality বেড়ে যায় এবং হারিয়ে যাওয়া লিড ফিরে আসায় "
                    "রিপোর্ট করা কনভার্সন ৩৮% বাড়ে। নির্ভরযোগ্য সিগন্যাল থাকায় "
                    "অপটিমাইজেশন স্থিতিশীল হয় ও CPL কমে। "
                    "(ক্লায়েন্ট NDA-এর অধীনে — সংখ্যাগুলো প্রতিনিধিত্বমূলক।)"
                ),
                "metrics": [
                    ("Tracked conversions", "ট্র্যাক করা কনভার্সন", "62%", "100%", "up_good", 62, 100, "", "%", 0),
                    ("Event Match Quality", "ইভেন্ট ম্যাচ কোয়ালিটি", "4.1", "8.6", "up_good", 4.1, 8.6, "", "/10", 1),
                    ("Cost per lead", "কস্ট পার লিড", "$9.10", "$5.80", "down_good", 9.10, 5.80, "$", "", 2),
                ],
            },
            {
                "slug": "ugc-creative-sprint",
                "is_featured": False,
                "order": 2,
                "title": "UGC testing sprint doubled CTR",
                "title_bn": "UGC টেস্টিং স্প্রিন্ট CTR দ্বিগুণ করেছে",
                "client_type": "D2C (Beauty)",
                "client_type_bn": "D2C (বিউটি)",
                "challenge": (
                    "Polished studio creative was fatiguing fast — frequency rose, CTR "
                    "sank, and every new launch bought a shrinking window of "
                    "performance before costs spiked."
                ),
                "challenge_bn": (
                    "পরিপাটি স্টুডিও ক্রিয়েটিভ দ্রুত ক্লান্ত হয়ে পড়ছিল — ফ্রিকোয়েন্সি "
                    "বাড়ছিল, CTR কমছিল, আর প্রতিটি নতুন লঞ্চ খরচ বাড়ার আগে ক্রমশ "
                    "ছোট পারফরম্যান্স উইন্ডো দিচ্ছিল।"
                ),
                "approach": (
                    "Ran a structured UGC testing sprint: briefed creators around real "
                    "objections, generated hook variations with AI, and let Dynamic "
                    "Creative Optimization surface winners fast — killing losers early "
                    "on clean per-creative data."
                ),
                "approach_bn": (
                    "একটি কাঠামোবদ্ধ UGC টেস্টিং স্প্রিন্ট চালিয়েছি: আসল আপত্তি ঘিরে "
                    "ক্রিয়েটরদের ব্রিফ দিয়েছি, AI দিয়ে হুক ভ্যারিয়েশন তৈরি করেছি, এবং "
                    "Dynamic Creative Optimization দিয়ে দ্রুত উইনার বের করেছি — "
                    "পরিষ্কার ডেটায় দুর্বলগুলো আগেই বাদ দিয়েছি।"
                ),
                "result_en": (
                    "The winning UGC angle more than doubled CTR versus studio ads and "
                    "extended creative lifespan, cutting the cost of always-on testing. "
                    "(Client under NDA — figures representative.)"
                ),
                "result_bn": (
                    "বিজয়ী UGC অ্যাঙ্গেলটি স্টুডিও অ্যাডের তুলনায় CTR দ্বিগুণেরও বেশি "
                    "করে এবং ক্রিয়েটিভ আয়ু বাড়ায়, ফলে সবসময়-চালু টেস্টিংয়ের খরচ কমে। "
                    "(ক্লায়েন্ট NDA-এর অধীনে — সংখ্যাগুলো প্রতিনিধিত্বমূলক।)"
                ),
                "metrics": [
                    ("CTR", "CTR", "0.9%", "2.1%", "up_good", 0.9, 2.1, "", "%", 0),
                    ("Cost per purchase", "কস্ট পার পারচেজ", "$22", "$13", "down_good", 22, 13, "$", "", 1),
                    ("Thumb-stop rate", "থাম্ব-স্টপ রেট", "18%", "31%", "up_good", 18, 31, "", "%", 2),
                ],
            },
        ]
        for data in cases:
            metrics = data.pop("metrics")
            result_en = data.pop("result_en")
            result_bn = data.pop("result_bn")
            data["result_text"] = result_en
            data["result_text_bn"] = result_bn
            case, _ = CaseStudy.objects.update_or_create(
                slug=data["slug"], defaults=data
            )
            case.metrics.all().delete()
            for (le, lb, bv, av, direction, nb, na, prefix, suffix, order) in metrics:
                CaseStudyMetric.objects.create(
                    case_study=case,
                    label=le,
                    label_bn=lb,
                    before_val=bv,
                    after_val=av,
                    direction=direction,
                    numeric_before=nb,
                    numeric_after=na,
                    prefix=prefix,
                    suffix=suffix,
                    order=order,
                )
        self.stdout.write("  · Case studies (3)")

    def _seed_testimonials(self):
        testimonials = [
            {
                "name": "Rahim Uddin",
                "role_company": "Owner, Dhaka fashion brand",
                "role_company_bn": "মালিক, ঢাকার ফ্যাশন ব্র্যান্ড",
                "quote": (
                    "Our cost per lead was far too high. After Mahadi restructured the "
                    "account, spend dropped and sales went up. The reporting is clear — "
                    "I finally understand where every dollar goes."
                ),
                "quote_bn": (
                    "আমাদের কস্ট পার লিড অনেক বেশি ছিল। মাহাদি অ্যাকাউন্ট রিস্ট্রাকচার "
                    "করার পর খরচ কমেছে আর সেলস বেড়েছে। রিপোর্টিং একদম পরিষ্কার — কোন "
                    "ডলার কোথায় যাচ্ছে এখন সব বুঝি।"
                ),
                "order": 0,
            },
            {
                "name": "Sarah Mitchell",
                "role_company": "Founder, D2C beauty brand (US)",
                "role_company_bn": "ফাউন্ডার, D2C বিউটি ব্র্যান্ড (US)",
                "quote": (
                    "The UGC ads he tested completely changed our results. He actually "
                    "explains the numbers instead of just sending screenshots. It feels "
                    "like having a data person on the team."
                ),
                "quote_bn": (
                    "তিনি যে UGC অ্যাডগুলো টেস্ট করেছেন তা আমাদের রেজাল্ট পুরোপুরি "
                    "বদলে দিয়েছে। শুধু স্ক্রিনশট পাঠানোর বদলে তিনি সংখ্যাগুলো ব্যাখ্যা "
                    "করেন। মনে হয় যেন টিমে একজন ডেটা এক্সপার্ট আছে।"
                ),
                "order": 1,
            },
            {
                "name": "Tanvir Ahmed",
                "role_company": "Manager, local service business",
                "role_company_bn": "ম্যানেজার, লোকাল সার্ভিস ব্যবসা",
                "quote": (
                    "Our tracking setup was completely broken. After the CAPI setup, "
                    "every conversion shows up in Meta again. Now the data is something "
                    "we can actually trust."
                ),
                "quote_bn": (
                    "আমাদের ট্র্যাকিং সেটআপ একদম ভাঙা ছিল। CAPI সেটআপের পর প্রতিটি "
                    "কনভার্সন আবার মেটায় দেখা যাচ্ছে। এখন ডেটার উপর ভরসা করা যায়।"
                ),
                "order": 2,
            },
        ]
        for t in testimonials:
            Testimonial.objects.update_or_create(name=t["name"], defaults=t)
        self.stdout.write("  · Testimonials (3)")
