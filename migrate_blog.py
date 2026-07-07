#!/usr/bin/env python3
"""One-shot migration: Webflow blog posts + privacy/terms -> static pages in Website/."""
import re, os, html as htmlmod, urllib.request, pathlib

SCRATCH = pathlib.Path(__file__).parent / "webflow"
SITE = pathlib.Path("/Users/ericlombardi/HSR Proposal/Website")
BLOGDIR = SITE / "blog"
IMGDIR = BLOGDIR / "img"
BLOGDIR.mkdir(exist_ok=True)
IMGDIR.mkdir(exist_ok=True)

POSTS = [  # newest first, matching blog.html card order
    "what-my-policy-survey-says-about-ontario-right-now",
    "alto-should-be-just-the-beginning-of-ontarios-high-speed-rail-network",
    "an-ontario-budget-for-decline-war-in-iran",
    "a-billion-here-a-billion-there",
    "poorer-than-alabama----what-the-gdp-per-capita-debate-is-really-about",
    "hamilton-speech-university-funding-changes-and-other-thoughts",
    "liberal-leadership-timelines-are-out",
]

def balanced_div(html, start_marker):
    j = html.find(start_marker)
    if j < 0:
        return None
    depth = 0
    for m in re.finditer(r"<div\b|</div>", html[j:]):
        depth += 1 if m.group(0).startswith("<div") else -1
        if depth == 0:
            return html[j : j + m.end()]
    return None

def strip_outer_div(block):
    inner = block[block.index(">") + 1 :]
    return inner[: inner.rindex("</div>")]

def download_img(url, slug, n):
    ext = ".png" if ".png" in url.lower() else ".jpg"
    if ".svg" in url.lower():
        ext = ".svg"
    name = f"{slug[:40].rstrip('-')}-{n}{ext}"
    dest = IMGDIR / name
    if not dest.exists():
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as r, open(dest, "wb") as f:
            f.write(r.read())
    return f"img/{name}"

def clean_body(body, slug):
    body = strip_outer_div(body)
    # webflow embed wrappers -> .embed
    body = re.sub(r'<div class="w-embed[^"]*"[^>]*>', '<div class="embed">', body)
    # figures: drop the bare <div> wrapper around the img
    body = re.sub(r"<div><img", "<img", body)
    body = re.sub(r"(<img[^>]*>)</div>", r"\1", body)
    body = re.sub(r'class="w-richtext-align[^"]*"', "", body)
    body = re.sub(r' class="w-inline-block"', "", body)
    # Webflow filler paragraphs (zero-width joiners) and broken px units
    body = re.sub(r"<p>(?:\s|‍|<br>)*</p>", "", body)
    body = re.sub(r"(?:<br>)?‍</p>", "</p>", body)
    body = body.replace("pxpx", "px")
    # figure max-widths wider than the column are meaningless — drop them
    def fix_maxw(m):
        return "" if int(m.group(1)) > 700 else m.group(0)
    body = re.sub(r'style="max-width:(\d+)px"\s*', fix_maxw, body)
    # localize body images
    n = [0]
    def repl_img(m):
        url = m.group(1)
        n[0] += 1
        local = download_img(url, slug, n[0])
        return m.group(0).replace(url, local)
    body = re.sub(r'<img[^>]*src="(https://cdn\.prod\.website-files\.com/[^"]*)"', repl_img, body)
    # internal links
    for s in POSTS:
        body = body.replace(f"https://www.ericforolp.ca/blog/{s}", f"{s}.html")
    body = body.replace('href="https://www.ericforolp.ca/"', 'href="../index.html"')
    body = body.replace('href="/blog"', 'href="../blog.html"')
    return body.strip()

def extract(path):
    html = open(path).read()
    title = re.search(r'<h1 class="h1-heading[^"]*">(.*?)</h1>', html).group(1).strip()
    meta = re.findall(r'<div class="body-text">([^<]*)</div>', html)
    date = meta[0] if meta else ""
    cat = meta[1] if len(meta) > 1 else "In my own words"
    desc_m = re.search(r'<meta content="([^"]*)" name="description"', html) or re.search(
        r'<meta name="description" content="([^"]*)"', html)
    desc = desc_m.group(1) if desc_m else ""
    body = balanced_div(html, '<div class="rich-blog-text w-richtext">')
    return title, date, cat, desc, body

NAV = """<header class="nav"><div class="wrap">
  <a class="mark" href="{p}index.html"><span class="dot"></span>Eric Lombardi <span style="color:var(--mute-on-dark); font-weight:500;">· for Ontario</span></a>
  <nav class="links">
    <a href="{p}platform/index.html">Platform</a>
    <a href="{p}blog.html">Blog</a>
    <a href="{p}news.html">News</a>
    <a href="https://everyriding.ericforolp.ca">Every Riding ↗</a>
    <a href="https://luma.com/ericforolp">Events ↗</a>
  </nav>
  <div class="cta">
    <a class="btn ghost" href="https://action.ontarioliberal.ca/f/eric">Sign-up to vote</a>
    <a class="btn red" href="https://calendly.com/ericforolp/meet-eric/">Book a meeting</a>
  </div>
  <button class="burger" aria-label="Menu" aria-expanded="false"><span></span><span></span><span></span></button>
</div>
<nav class="mnav">
  <a href="{p}platform/index.html">Platform</a>
  <a href="{p}blog.html">Blog</a>
  <a href="{p}news.html">News</a>
  <a href="https://everyriding.ericforolp.ca">Every Riding ↗</a>
  <a href="https://luma.com/ericforolp">Events ↗</a>
  <a href="https://calendly.com/ericforolp/meet-eric/">Book a meeting with Eric ↗</a>
  <a class="msign" href="https://action.ontarioliberal.ca/f/eric">Sign-up to vote — it's free</a>
</nav>
</header>
<script>(function(){{var h=document.querySelector("header.nav"),b=h.querySelector(".burger");
b.addEventListener("click",function(){{var o=h.classList.toggle("open");b.setAttribute("aria-expanded",o);}});}})();</script>"""

FOOT = """<footer class="foot"><div class="inner">
  <div class="fm"><span class="dot"></span>Eric Lombardi for Ontario</div>
  <nav>
    <a href="{p}index.html">Home</a>
    <a href="{p}platform/index.html">Platform</a>
    <a href="{p}news.html">News</a>
    <a href="https://donate.ericforolp.ca">Donate</a>
  </nav>
  <div class="fine">© 2026 Eric Lombardi. All rights reserved. · <a href="{p}privacy-policy.html" style="color:inherit;">Privacy</a> · <a href="{p}terms-of-service.html" style="color:inherit;">Terms</a></div>
</div></footer>"""

FAVICON = """<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect x='8' y='8' width='16' height='16' transform='rotate(45 16 16)' fill='%23E81E25'/%3E%3C/svg%3E">"""

def page(title_text, desc, hero, content, prefix, extra_head=""):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title_text} — Eric Lombardi for Ontario</title>
<meta name="description" content="{htmlmod.escape(desc, quote=True)}">
{FAVICON}
<link rel="stylesheet" href="{prefix}site.css">
<link rel="stylesheet" href="{prefix}home.css">
{extra_head}</head>
<body>

{NAV.format(p=prefix)}

{hero}

{content}

{FOOT.format(p=prefix)}

</body></html>
"""

# ---------- blog posts ----------
posts_meta = []
for slug in POSTS:
    title, date, cat, desc, body = extract(SCRATCH / f"blog-{slug}.html")
    posts_meta.append((slug, title, date, cat, desc))
    body = clean_body(body, slug)
    hero = f"""<section class="hero"><div class="inner" style="padding:64px 22px 50px; max-width:860px;">
  <div class="kicker">{cat}</div>
  <h1 style="margin-top:12px; font-size:clamp(30px,4.4vw,46px); line-height:1.12;">{title}</h1>
  <p class="tagline" style="margin-top:14px;">{date} · Eric Lombardi</p>
</div></section>"""
    idx = POSTS.index(slug)
    newer = POSTS[idx - 1] if idx > 0 else None
    older = POSTS[idx + 1] if idx < len(POSTS) - 1 else None
    def label(s):
        t = next(m[1] for m in posts_meta if m[0] == s) if any(m[0] == s for m in posts_meta) else None
        return t
    pager_parts = ['<a href="../blog.html">← All posts</a>']
    nav_links = []
    if newer: nav_links.append(f'<a href="{newer}.html">‹ Newer</a>')
    if older: nav_links.append(f'<a href="{older}.html">Older ›</a>')
    pager = f"""<div class="postnav">{''.join(f'<span>{x}</span>' for x in pager_parts + nav_links)}</div>"""
    content = f"""<section class="stripe"><div class="wrap">
  <article class="post">
{body}
  </article>
  {pager}
</div></section>"""
    out = page(htmlmod.unescape(re.sub("<[^>]+>", "", title)), desc, hero, content, "../")
    (BLOGDIR / f"{slug}.html").write_text(out)
    print("wrote blog/", slug)

# ---------- privacy & terms ----------
for src, slug, name in [("privacy.html", "privacy-policy", "Privacy Policy"),
                        ("terms.html", "terms-of-service", "Terms of Service")]:
    html = open(SCRATCH / src).read()
    upd = re.search(r'<div class="body-text"><strong>(Last updated[^<]*)</strong></div>', html)
    updated = upd.group(1) if upd else ""
    start = html.find('<div class="w-layout-vflex vertical-wrapper">', upd.end() if upd else 0)
    body = balanced_div(html, '<div class="w-layout-vflex vertical-wrapper">') if start < 0 else None
    if start >= 0:
        depth = 0
        for m2 in re.finditer(r"<div\b|</div>", html[start:]):
            depth += 1 if m2.group(0).startswith("<div") else -1
            if depth == 0:
                body = html[start : start + m2.end()]
                break
    if body is None:
        print("!! no content in", src); continue
    body = strip_outer_div(body).strip()
    body = body.replace(' class="body-text-big"', "").replace(' class="h3-heading"', "")
    body = body.replace('href="https://www.ericforolp.ca/"', 'href="index.html"')
    hero = f"""<section class="hero"><div class="inner" style="padding:64px 22px 50px; max-width:860px;">
  <div class="kicker">The fine print</div>
  <h1 style="margin-top:12px; font-size:clamp(30px,4.4vw,46px);">{name}</h1>
  <p class="tagline" style="margin-top:14px;">{updated}</p>
</div></section>"""
    content = f"""<section class="stripe"><div class="wrap">
  <article class="post legal">
{body}
  </article>
</div></section>"""
    out = page(name, f"{name} for ericforolp.ca — Eric Lombardi's campaign for Ontario Liberal Party leader.", hero, content, "")
    (SITE / f"{slug}.html").write_text(out)
    print("wrote", slug)

print("\nposts_meta:")
for m in posts_meta:
    print(" ", m[0], "|", m[2], "|", m[3])
