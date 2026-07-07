#!/usr/bin/env python3
"""Add a news/media item to news.html (newest first).

Usage:
    python3 add_news.py "Outlet Name" "Headline of the piece" "Jul 15, 2026" "https://link-to-piece"

Then, if it belongs on the homepage, copy the printed snippet into the
"Featured news" list in index.html (keep that list to ~4 items).
"""
import sys, html as hm, pathlib

if len(sys.argv) != 5:
    sys.exit(__doc__)
outlet, title, date, url = sys.argv[1:5]
item = (f'    <a class="newsitem" href="{url}">'
        f'<span class="no">{hm.escape(outlet)}</span>'
        f'<span class="nt">{hm.escape(title)}</span>'
        f'<span class="nd">{hm.escape(date)}</span></a>\n')

f = pathlib.Path(__file__).parent / "news.html"
s = f.read_text()
s = s.replace('<div class="newslist">\n', '<div class="newslist">\n' + item, 1)
f.write_text(s)
print("added to news.html:\n" + item)
print("If it should be featured on the homepage, paste the same line into the")
print('"Featured news" <div class="newslist"> in index.html (and remove the oldest).')
