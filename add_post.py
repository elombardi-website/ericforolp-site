#!/usr/bin/env python3
"""Add a new blog post from a markdown file.

Usage:
    python3 add_post.py posts/my-new-post.md

The markdown file needs a frontmatter block, then the post body:

    ---
    title: My New Post Title
    date: July 15, 2026
    category: campaign updates
    description: One sentence shown on the blog card and in search results.
    ---

    Regular paragraphs. **bold**, *italic*, [links](https://example.com).

    ## Section heading

    - bullet lists
    1. numbered lists

    ![caption text](img/photo.jpg)          <- put photos in Website/blog/img/ first

    <iframe src="https://..."></iframe>      <- raw HTML lines pass through as-is

What it does:
  1. writes blog/<slug>.html (slug = markdown filename)
  2. inserts a card at the top of blog.html
  3. adds a "Newer" link to the previously-newest post
  4. reminds you to update the homepage "From the blog" cards
"""
import re, sys, html as hm, pathlib

HERE = pathlib.Path(__file__).parent
BLOGDIR = HERE / "blog"

# ---------- tiny markdown -> html ----------
def inline(s):
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    return s

def md_to_html(md):
    out, lines = [], md.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip():
            i += 1; continue
        if line.startswith("<"):                       # raw HTML passthrough
            block = [line]
            while i + 1 < len(lines) and lines[i + 1].strip():
                i += 1; block.append(lines[i].rstrip())
            out.append('<div class="embed">' + "\n".join(block) + "</div>"
                       if block[0].startswith("<iframe") else "\n".join(block))
        elif line.startswith("### "):
            out.append(f"<h3>{inline(line[4:])}</h3>")
        elif line.startswith("## "):
            out.append(f"<h2>{inline(line[3:])}</h2>")
        elif m := re.match(r"!\[([^\]]*)\]\(([^)]+)\)", line):
            cap = f"<figcaption>{inline(m.group(1))}</figcaption>" if m.group(1) else ""
            out.append(f'<figure><img alt="" src="{m.group(2)}" loading="lazy">{cap}</figure>')
        elif re.match(r"[-*] ", line):
            items = []
            while i < len(lines) and re.match(r"[-*] ", lines[i].strip()):
                items.append(f"<li>{inline(lines[i].strip()[2:])}</li>"); i += 1
            i -= 1
            out.append("<ul>" + "".join(items) + "</ul>")
        elif re.match(r"\d+\. ", line):
            items = []
            while i < len(lines) and re.match(r"\d+\. ", lines[i].strip()):
                text = re.sub(r"^\d+\. ", "", lines[i].strip())
                items.append(f"<li>{inline(text)}</li>"); i += 1
            i -= 1
            out.append("<ol>" + "".join(items) + "</ol>")
        elif line.startswith("> "):
            out.append(f"<blockquote><p>{inline(line[2:])}</p></blockquote>")
        else:                                          # paragraph (may span lines)
            para = [line]
            while i + 1 < len(lines) and lines[i + 1].strip() and not re.match(r"(#{2,3} |[-*] |\d+\. |> |!\[|<)", lines[i + 1].strip()):
                i += 1; para.append(lines[i].strip())
            out.append(f"<p>{inline(' '.join(para))}</p>")
        i += 1
    return "\n".join(out)

# ---------- page template (matches migrate_blog.py output) ----------
NAV = """<header class="nav"><div class="wrap">
  <a class="mark" href="../index.html"><span class="dot"></span>Eric Lombardi <span style="color:var(--mute-on-dark); font-weight:500;">· for Ontario</span></a>
  <nav class="links">
    <a href="../platform/index.html">Platform</a>
    <a href="../blog.html">Blog</a>
    <a href="../news.html">News</a>
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
  <a href="../platform/index.html">Platform</a>
  <a href="../blog.html">Blog</a>
  <a href="../news.html">News</a>
  <a href="https://everyriding.ericforolp.ca">Every Riding ↗</a>
  <a href="https://luma.com/ericforolp">Events ↗</a>
  <a href="https://calendly.com/ericforolp/meet-eric/">Book a meeting with Eric ↗</a>
  <a class="msign" href="https://action.ontarioliberal.ca/f/eric">Sign-up to vote — it's free</a>
</nav>
</header>
<script>(function(){var h=document.querySelector("header.nav"),b=h.querySelector(".burger");
b.addEventListener("click",function(){var o=h.classList.toggle("open");b.setAttribute("aria-expanded",o);});})();</script>"""

FOOT = """<footer class="foot"><div class="inner">
  <div class="fm"><span class="dot"></span>Eric Lombardi for Ontario</div>
  <nav>
    <a href="../index.html">Home</a>
    <a href="../platform/index.html">Platform</a>
    <a href="../news.html">News</a>
    <a href="https://donate.ericforolp.ca">Donate</a>
  </nav>
  <div class="fine">© 2026 Eric Lombardi. All rights reserved. · <a href="../privacy-policy.html" style="color:inherit;">Privacy</a> · <a href="../terms-of-service.html" style="color:inherit;">Terms</a></div>
</div></footer>"""

FAVICON = """<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect x='8' y='8' width='16' height='16' transform='rotate(45 16 16)' fill='%23E81E25'/%3E%3C/svg%3E">"""

def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    src = pathlib.Path(sys.argv[1])
    slug = src.stem
    raw = src.read_text()
    fm = re.match(r"---\n(.*?)\n---\n(.*)", raw, re.S)
    if not fm:
        sys.exit("No frontmatter block found (--- title: ... ---)")
    meta = dict(re.findall(r"^(\w+):\s*(.+)$", fm.group(1), re.M))
    for k in ("title", "date", "description"):
        if k not in meta:
            sys.exit(f"Frontmatter missing '{k}:'")
    title, date = meta["title"], meta["date"]
    cat = meta.get("category", "In my own words")
    desc = meta["description"]
    body = md_to_html(fm.group(2))

    blog_html = (HERE / "blog.html").read_text()
    prev_slug_m = re.search(r'href="blog/([a-z0-9-]+)\.html"', blog_html)
    prev_slug = prev_slug_m.group(1) if prev_slug_m else None

    pager = '<div class="postnav"><span><a href="../blog.html">← All posts</a></span>'
    if prev_slug:
        pager += f'<span><a href="{prev_slug}.html">Older ›</a></span>'
    pager += "</div>"

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{hm.escape(title)} — Eric Lombardi for Ontario</title>
<meta name="description" content="{hm.escape(desc, quote=True)}">
{FAVICON}
<link rel="stylesheet" href="../site.css">
<link rel="stylesheet" href="../home.css">
</head>
<body>

{NAV}

<section class="hero"><div class="inner" style="padding:64px 22px 50px; max-width:860px;">
  <div class="kicker">{hm.escape(cat)}</div>
  <h1 style="margin-top:12px; font-size:clamp(30px,4.4vw,46px); line-height:1.12;">{hm.escape(title)}</h1>
  <p class="tagline" style="margin-top:14px;">{hm.escape(date)} · Eric Lombardi</p>
</div></section>

<section class="stripe"><div class="wrap">
  <article class="post">
{body}
  </article>
  {pager}
</div></section>

{FOOT}

</body></html>
"""
    (BLOGDIR / f"{slug}.html").write_text(page)
    print(f"wrote blog/{slug}.html")

    # insert card at top of blog.html
    card = f"""    <a class="blogcard" href="blog/{slug}.html">
      <div class="bd">{hm.escape(date)}</div><h3>{hm.escape(title)}</h3>
      <p>{hm.escape(desc)}</p><div class="go">Read →</div></a>
"""
    blog_html = blog_html.replace('<div class="blogcards">\n', '<div class="blogcards">\n' + card, 1)
    (HERE / "blog.html").write_text(blog_html)
    print("added card to blog.html")

    # give the previously-newest post a "Newer" link
    if prev_slug:
        prev_file = BLOGDIR / f"{prev_slug}.html"
        p = prev_file.read_text()
        if f'{slug}.html">‹ Newer' not in p:
            p = p.replace('<div class="postnav"><span><a href="../blog.html">← All posts</a></span>',
                          f'<div class="postnav"><span><a href="../blog.html">← All posts</a></span><span><a href="{slug}.html">‹ Newer</a></span>', 1)
            prev_file.write_text(p)
            print(f"linked ‹ Newer on blog/{prev_slug}.html")

    print("\nDone. Optional: update the three 'From the blog' cards in index.html "
          "so the homepage shows the newest posts.")

if __name__ == "__main__":
    main()
