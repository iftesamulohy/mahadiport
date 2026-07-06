"""
Author + compile the Bangla message catalog without gettext CLI tools.

The project targets an environment without `xgettext`/`msgfmt`, so we build
locale/bn/LC_MESSAGES/django.{po,mo} directly with polib. Every msgid here must
match a {% translate "..." %} / gettext_lazy("...") string in the codebase.

    ./venv/bin/python scripts/build_messages.py
"""

import pathlib

import polib

BN = {
    # Nav / buttons
    "Case Studies": "কেস স্টাডি",
    "Skills": "স্কিল",
    "Experience": "অভিজ্ঞতা",
    "Contact": "যোগাযোগ",
    "Book audit": "অডিট বুক করুন",
    "Book a free audit": "ফ্রি অডিট বুক করুন",
    "Download CV": "সিভি ডাউনলোড",
    "View breakdown": "বিস্তারিত দেখুন",
    "Get results like this": "এমন ফলাফল পান",
    "Running": "চলছে",
    "Back to home": "হোমে ফিরুন",
    # Eyebrow labels
    "CASE STUDIES": "কেস স্টাডি",
    "SKILLS": "স্কিল",
    "EXPERIENCE": "অভিজ্ঞতা",
    "CONTACT": "যোগাযোগ",
    "TESTIMONIALS": "প্রশংসাপত্র",
    "CASE": "কেস",
    "FEATURED": "ফিচার্ড",
    "CHALLENGE": "চ্যালেঞ্জ",
    "APPROACH": "পদ্ধতি",
    "RESULT": "ফলাফল",
    "ERROR 404": "এরর ৪০৪",
    # Section titles / leads
    "Proof, not promises.": "প্রতিশ্রুতি নয়, প্রমাণ।",
    "Real campaign work — restructures, tracking fixes and creative sprints — "
    "with the before/after numbers that mattered.":
        "বাস্তব ক্যাম্পেইনের কাজ — রিস্ট্রাকচার, ট্র্যাকিং ঠিক করা আর ক্রিয়েটিভ "
        "স্প্রিন্ট — যে আগে/পরে সংখ্যাগুলো আসল ফারাক গড়েছে।",
    "The stack behind the numbers.": "সংখ্যার পেছনের টুলসেট।",
    "From pixel plumbing to creative testing — the toolkit that makes campaigns "
    "measurable and scalable.":
        "পিক্সেল সেটআপ থেকে ক্রিয়েটিভ টেস্টিং — যে টুলকিট ক্যাম্পেইনকে পরিমাপযোগ্য "
        "ও স্কেলযোগ্য করে।",
    "Where the reps came from.": "অভিজ্ঞতা যেখান থেকে।",
    "What clients say — in their words.": "ক্লায়েন্টরা যা বলেন — তাদের ভাষায়।",
    "Free 20-minute ad account audit.": "ফ্রি ২০ মিনিটের অ্যাড অ্যাকাউন্ট অডিট।",
    "I'll show you where your budget is bleeding, what's mis-tracked, and the "
    "two or three moves that lower your CPL. No obligation.":
        "আমি দেখিয়ে দেব আপনার বাজেট কোথায় নষ্ট হচ্ছে, কী ভুল ট্র্যাক হচ্ছে, আর "
        "কোন দুই-তিনটি পদক্ষেপে আপনার CPL কমবে। কোনো বাধ্যবাধকতা নেই।",
    # 404
    "This funnel has no conversions.": "এই ফানেলে কোনো কনভার্সন নেই।",
    "Page not found.": "পেজ খুঁজে পাওয়া যায়নি।",
    "The page you're looking for didn't convert — it's not here. Let's get you "
    "back to something that performs.":
        "আপনি যে পেজটি খুঁজছেন সেটি কনভার্ট করেনি — এটি এখানে নেই। চলুন এমন কিছুতে "
        "ফিরে যাই যা পারফর্ম করে।",
    # Form
    "Name": "নাম",
    "Phone": "ফোন",
    "Email": "ইমেইল",
    "optional": "ঐচ্ছিক",
    "What do you sell?": "আপনি কী বিক্রি করেন?",
    "Monthly ad budget": "মাসিক অ্যাড বাজেট",
    "Message": "মেসেজ",
    "Send — get my free audit": "পাঠান — আমার ফ্রি অডিট নিন",
    "Phone is primary — I'll reply on WhatsApp or call.":
        "ফোনই মুখ্য — আমি WhatsApp-এ বা কলে উত্তর দেব।",
    "Your name": "আপনার নাম",
    "you@example.com (optional)": "you@example.com (ঐচ্ছিক)",
    "e.g. fashion page, restaurant, service…":
        "যেমন ফ্যাশন পেজ, রেস্টুরেন্ট, সার্ভিস…",
    "Anything you want me to know?": "আমাকে কিছু জানাতে চান?",
    "Select a range…": "একটি রেঞ্জ বাছুন…",
    # Success
    "Message received 🎉": "মেসেজ পেয়েছি 🎉",
    "You'll hear from me within 24 hours — check your phone!":
        "২৪ ঘণ্টার মধ্যে আমার কাছ থেকে খবর পাবেন — ফোন চেক করুন!",
    "I'll review your ad account and tell you where the budget is leaking.":
        "আমি আপনার অ্যাড অ্যাকাউন্ট রিভিউ করে বলব বাজেট কোথায় লিক হচ্ছে।",
    # Footer
    "Built with Django + HTMX": "Django + HTMX দিয়ে তৈরি",
    # Language names (settings LANGUAGES)
    "English": "ইংরেজি",
    "বাংলা": "বাংলা",
}

BASE = pathlib.Path(__file__).resolve().parent.parent
po_dir = BASE / "locale" / "bn" / "LC_MESSAGES"
po_dir.mkdir(parents=True, exist_ok=True)

po = polib.POFile()
po.metadata = {
    "Project-Id-Version": "mahadi-portfolio 1.0",
    "Language": "bn",
    "MIME-Version": "1.0",
    "Content-Type": "text/plain; charset=UTF-8",
    "Content-Transfer-Encoding": "8bit",
    "Plural-Forms": "nplurals=2; plural=(n != 1);",
}

for msgid, msgstr in BN.items():
    po.append(polib.POEntry(msgid=msgid, msgstr=msgstr))

po.save(str(po_dir / "django.po"))
po.save_as_mofile(str(po_dir / "django.mo"))
print(f"Wrote {len(BN)} entries to {po_dir}/django.{{po,mo}}")
