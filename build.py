#!/usr/bin/env python3
"""Builds the PawShelf website.

i18n/<lang>.json + i18n/characters.json  ->  <slug>/index.html, <slug>/privacy.html, <slug>/support.html, index.html

Run:  python3 build.py
The repository root is the website, so it can be served as is (GitHub Pages, Netlify, Cloudflare Pages).
"""
import html
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).parent

# Set these before publishing.
SITE_URL = "https://archivelab-kr.github.io/pawshelf"  # GitHub Pages, like moabook; canonical/hreflang/og/sitemap
SUPPORT_EMAIL = "archivelabapps@gmail.com"
PRICE_USD = "4.99"  # same as App Store Connect (scripts/store/upload.py --price in the app repo)
# Campaign link like moabook (pt = this account, ct = website, mt=12 = Mac) so App Store Connect shows installs from
# the site; empty shows "Coming soon". Set before approval: the app goes live automatically once approved.
APP_STORE_URL = "https://apps.apple.com/app/apple-store/id6837677780?pt=120201957&ct=website&mt=12"

# (code used in <html lang> and hreflang, folder name)
LANGS = [("en", "en"), ("ko", "ko"), ("ja", "ja"), ("zh-Hans", "zh-hans"), ("de", "de"), ("es", "es"),
         ("fr", "fr"), ("it", "it"), ("nl", "nl"), ("pt-BR", "pt-br"), ("pt-PT", "pt-pt")]
CHARS = ["boxCat", "hamster", "squirrel", "penguin", "owl", "magpie",
         "fetchDog", "kangaroo", "pelican", "octopus", "mole", "turtle"]
PAGES = ["index.html", "privacy.html", "support.html"]

LINKS = {
    "google": "https://policies.google.com/privacy",
    "firebase": "https://firebase.google.com/support/privacy",
}

# Small inline icons (decorative, aria-hidden).
ICON = {
    "globe": '<svg viewBox="0 0 20 20"><circle cx="10" cy="10" r="7.5" stroke="currentColor" stroke-width="1.5" fill="none"/><path d="M2.5 10h15M10 2.5c2.6 2.4 2.6 12.6 0 15M10 2.5c-2.6 2.4-2.6 12.6 0 15" stroke="currentColor" stroke-width="1.3" fill="none"/></svg>',
    "pause": '<svg class="i-pause" viewBox="0 0 20 20"><rect x="5" y="4" width="3.5" height="12" rx="1" fill="currentColor"/><rect x="11.5" y="4" width="3.5" height="12" rx="1" fill="currentColor"/></svg>',
    "play": '<svg class="i-play" viewBox="0 0 20 20"><path d="M6 4.2v11.6a.8.8 0 0 0 1.2.7l9.3-5.8a.8.8 0 0 0 0-1.4L7.2 3.5a.8.8 0 0 0-1.2.7z" fill="currentColor"/></svg>',
}


def icon(name):
    return ICON[name].replace("<svg ", '<svg aria-hidden="true" focusable="false" ', 1)


def esc(s):
    """Escape text, then turn {email}, {google}, {firebase} tokens into links."""
    out = html.escape(s, quote=False)
    out = out.replace("{email}", f'<a href="mailto:{SUPPORT_EMAIL}">{SUPPORT_EMAIL}</a>')
    for key, link in LINKS.items():
        out = out.replace("{" + key + "}", f'<a href="{link}">{link.removeprefix("https://")}</a>')
    return out


def attr(s):
    return html.escape(s, quote=True)


def url(slug, page):
    return f"{SITE_URL}/{slug}/" + ("" if page == "index.html" else page)


def head(code, slug, page, title, desc, extra=""):
    alternates = "\n".join(f'<link rel="alternate" hreflang="{c}" href="{url(s, page)}">' for c, s in LANGS)
    return f"""<!doctype html>
<html lang="{code}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{attr(title)}</title>
<meta name="description" content="{attr(desc)}">
<meta name="color-scheme" content="light dark">
<link rel="canonical" href="{url(slug, page)}">
{alternates}
<link rel="alternate" hreflang="x-default" href="{SITE_URL}/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="PawShelf">
<meta property="og:title" content="{attr(title)}">
<meta property="og:description" content="{attr(desc)}">
<meta property="og:url" content="{url(slug, page)}">
<meta property="og:image" content="{SITE_URL}/assets/icon-1024.png">
<link rel="icon" type="image/png" href="../assets/favicon.png">
<link rel="apple-touch-icon" href="../assets/icon-256.png">
<link rel="stylesheet" href="../assets/style.css">
<script src="../assets/site.js" defer></script>{extra}
</head>
<body>"""


def app_jsonld(t, code, slug):
    """schema.org SoftwareApplication for search engines (home pages only). Add aggregateRating once there are reviews."""
    data = {"@context": "https://schema.org", "@type": "SoftwareApplication", "name": "PawShelf",
            "description": t["description"], "operatingSystem": "macOS 14 or later",
            "applicationCategory": "UtilitiesApplication", "inLanguage": code, "url": url(slug, "index.html"),
            "image": f"{SITE_URL}/assets/icon-1024.png", "screenshot": f"{SITE_URL}/assets/demo/poster-en.jpg",
            "offers": {"@type": "Offer", "price": PRICE_USD, "priceCurrency": "USD"},
            "publisher": {"@type": "Organization", "name": "ArchiveLab"}}
    if APP_STORE_URL:
        data["downloadUrl"] = APP_STORE_URL
    return '\n<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False).replace("</", "<\\/") + "</script>"


def header(t, page):
    options = "".join(
        f'<option value="../{s}/{page}"{" selected" if s == t["_slug"] else ""}>{esc(all_t[s]["lang_name"])}</option>'
        for _, s in LANGS)
    return f"""
<header class="top{' on-hero' if page == 'index.html' else ''}">
  <a class="brand" href="./"><img src="../assets/icon-256.png" alt="" width="34" height="34">PawShelf</a>
  <nav class="top-nav">
    <a href="support.html">{esc(t["nav_support"])}</a>
    <label class="lang">{icon("globe")}<span class="sr">{esc(t["language"])}</span>
      <select>{options}</select>
    </label>
  </nav>
</header>"""


def footer(t, page):
    langs = "".join(
        f'<li><a href="../{s}/{page}" hreflang="{c}" lang="{c}">{esc(all_t[s]["lang_name"])}</a></li>' for c, s in LANGS)
    return f"""
<footer class="foot">
  <div class="foot-in">
    <p class="foot-brand"><img src="../assets/icon-256.png" alt="" width="28" height="28">PawShelf</p>
    <ul class="foot-links">
      <li><a href="./">{esc(t["nav_home"])}</a></li>
      <li><a href="support.html">{esc(t["nav_support"])}</a></li>
      <li><a href="privacy.html">{esc(t["nav_privacy"])}</a></li>
    </ul>
    <ul class="foot-langs" aria-label="{attr(t["language"])}">{langs}</ul>
    <p class="foot-copy">© 2026 PawShelf</p>
  </div>
</footer>
</body>
</html>
"""


def cta(t):
    if APP_STORE_URL:
        return f'<a class="cta" href="{attr(APP_STORE_URL)}">{esc(t["cta_download"])}</a>'
    return f'<p class="cta is-soon">{esc(t["cta_soon"])}</p>'


def demo_asset(slug, name, ext):
    """A language's own recording when there is one (record-demo.swift in the app repo), else the English one."""
    own = f"assets/demo/{name}-{slug}.{ext}"
    return "../" + (own if (ROOT / own).exists() else f"assets/demo/{name}-en.{ext}")


def home(t, chars, top):
    slug = t["_slug"]
    shots = ["drop", "shelf", "out"]  # real frames from the recorded take, one per step
    steps = "".join(
        f'<li><img src="{demo_asset(slug, shot, "jpg")}" alt="" width="520" height="390" loading="lazy">'
        f"<h3>{esc(h)}</h3><p>{esc(p)}</p></li>"
        for shot, (h, p) in zip(shots, t["steps"]))
    features = "".join(f"<li><h3>{esc(h)}</h3><p>{esc(p)}</p></li>" for h, p in t["features"])
    pals = "".join(f"""
      <li class="pal">
        <div class="pal-art"><img src="../assets/chars/{c}.png" alt="" width="83" height="120" loading="lazy"><img class="alt" src="../assets/chars/{c}-hello.png" alt="" width="83" height="120" loading="lazy"></div>
        <h3>{esc(chars[c][0])}</h3>
        <p>{esc(chars[c][1])}</p>
      </li>""" for c in CHARS)
    return f"""
{top}
<main>
<section class="hero">
  <div class="hero-in">
    <div class="hero-copy">
      <h1>{esc(t["hero_h1"]).replace(chr(10), "<br>")}</h1>
      <p class="lead">{esc(t["hero_p"])}</p>
      {cta(t)}
      <p class="req">{esc(t["requirements"])}</p>
    </div>
    <figure class="screen">
      <video src="{demo_asset(slug, "demo", "mp4")}" poster="{demo_asset(slug, "poster", "jpg")}" width="1280" height="720"
             autoplay muted loop playsinline preload="auto" aria-label="{attr(t["demo_label"])}"></video>
      <button class="video-toggle" type="button" data-pause="{attr(t["video_pause"])}" data-play="{attr(t["video_play"])}" aria-label="{attr(t["video_pause"])}">
        {icon("pause")}{icon("play")}
      </button>
    </figure>
  </div>
</section>

<section class="how" id="how">
  <h2>{esc(t["how_h2"])}</h2>
  <ol class="steps">{steps}</ol>
</section>

<section class="pals" id="characters">
  <div class="pals-in">
    <h2>{esc(t["chars_h2"])}</h2>
    <p class="section-lead">{esc(t["chars_p"])}</p>
    <ul class="pal-grid">{pals}
    </ul>
    <p class="pals-hint">{esc(t["chars_hint"])}</p>
  </div>
</section>

<section class="features" id="features">
  <h2>{esc(t["features_h2"])}</h2>
  <ul class="feature-list">{features}</ul>
</section>

<section class="promise">
  <div class="promise-in">
    <h2>{esc(t["promise_h2"])}</h2>
    <p>{esc(t["promise_p"])}</p>
    <p><a href="privacy.html">{esc(t["promise_link"])}</a></p>
  </div>
</section>
</main>"""


def privacy(t):
    p = t["privacy"]
    sections = "".join(
        f"<h2>{esc(h)}</h2>" + "".join(f"<p>{esc(x)}</p>" for x in paras) for h, paras in p["sections"])
    return f"""
<main class="doc">
  <h1>{esc(p["title"])}</h1>
  <p class="updated">{esc(p["updated"])}</p>
  <p class="lead">{esc(p["intro"])}</p>
  {sections}
  <p class="note">{esc(p["note"])}</p>
</main>"""


def support(t):
    s = t["support"]
    faq = "".join(f"<h3>{esc(q)}</h3><p>{esc(a)}</p>" for q, a in s["faq"])
    return f"""
<main class="doc">
  <h1>{esc(s["title"])}</h1>
  <p class="lead">{esc(s["intro"])}</p>
  <h2>{esc(s["faq_h2"])}</h2>
  {faq}
</main>"""


def root_index():
    """Language picker at the site root: sends the browser to its language, falls back to English."""
    slugs = {s: s for _, s in LANGS}
    alternates = "\n".join(f'<link rel="alternate" hreflang="{c}" href="{url(s, "index.html")}">' for c, s in LANGS)
    links = "".join(f'<li><a href="{s}/" lang="{c}">{esc(all_t[s]["lang_name"])}</a></li>' for c, s in LANGS)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PawShelf</title>
<meta name="description" content="{attr(all_t["en"]["description"])}">
{alternates}
<link rel="alternate" hreflang="x-default" href="{SITE_URL}/">
<link rel="icon" type="image/png" href="assets/favicon.png">
<script>
(function () {{
  var slugs = {json.dumps(slugs)};
  var pick = "en";
  var prefs = navigator.languages || [navigator.language || "en"];
  for (var i = 0; i < prefs.length; i++) {{
    var l = prefs[i].toLowerCase();
    if (slugs[l]) {{ pick = l; break; }}
    if (l.indexOf("zh") === 0) {{ pick = "zh-hans"; break; }}
    if (l.indexOf("pt") === 0) {{ pick = "pt-br"; break; }}
    var base = l.split("-")[0];
    if (slugs[base]) {{ pick = base; break; }}
  }}
  location.replace(pick + "/");
}})();
</script>
<noscript><meta http-equiv="refresh" content="0; url=en/"></noscript>
</head>
<body>
<ul>{links}</ul>
</body>
</html>
"""


def check_keys(ref, other, lang, path=""):
    """Every language must have the same keys and list lengths as English."""
    if isinstance(ref, dict):
        for k in ref:
            if k not in other:
                sys.exit(f"{lang}: missing {path}{k}")
            check_keys(ref[k], other[k], lang, f"{path}{k}.")
    elif isinstance(ref, list):
        if not isinstance(other, list) or len(ref) != len(other):
            sys.exit(f"{lang}: {path[:-1]} should have {len(ref)} entries")
        for i, (a, b) in enumerate(zip(ref, other)):
            check_keys(a, b, lang, f"{path}{i}.")


all_t = {}
for code, slug in LANGS:
    all_t[slug] = json.loads((ROOT / "i18n" / f"{slug}.json").read_text(encoding="utf-8"))
    all_t[slug]["_slug"] = slug
    if slug != "en":
        check_keys(all_t["en"], all_t[slug], slug)

characters = json.loads((ROOT / "i18n" / "characters.json").read_text(encoding="utf-8"))

for code, slug in LANGS:
    t = all_t[slug]
    chars = {c: (characters[c]["name"], characters[c]["tagline"]) if code == "en"
             else (characters[c]["loc"][code]["name"], characters[c]["loc"][code]["tagline"]) for c in CHARS}
    out = ROOT / slug
    out.mkdir(exist_ok=True)
    pages = {
        "index.html": (t["title"], t["description"], home(t, chars, header(t, "index.html"))),
        "privacy.html": (f'{t["privacy"]["title"]} | PawShelf', t["privacy"]["intro"], header(t, "privacy.html") + privacy(t)),
        "support.html": (f'{t["support"]["title"]} | PawShelf', t["support"]["intro"].replace("{email}", SUPPORT_EMAIL),
                         header(t, "support.html") + support(t)),
    }
    for page, (title, desc, body) in pages.items():
        extra = app_jsonld(t, code, slug) if page == "index.html" else ""
        (out / page).write_text(head(code, slug, page, title, desc, extra) + body + footer(t, page), encoding="utf-8")

(ROOT / "index.html").write_text(root_index(), encoding="utf-8")
(ROOT / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "".join(f"  <url><loc>{url(s, p)}</loc></url>\n" for _, s in LANGS for p in PAGES)
    + "</urlset>\n", encoding="utf-8")
print(f"Built {len(LANGS)} languages x {len(PAGES)} pages + index.html + sitemap.xml")
if not APP_STORE_URL:
    print("note: APP_STORE_URL is empty, pages show 'coming soon'")
