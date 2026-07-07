# ericforolp.ca — static site

Full replacement for the Webflow site. No backend, no build step — every page is a
plain HTML file you can open in a browser. Design system matches the platform PDF
and keynote (PP Watch / PP Pangram Sans, brand red `#E81E25`).

## What's in here

| Path | What it is |
|---|---|
| `index.html` | Homepage (hero + video, platform, about, donate, news, survey, blog, FAQ) |
| `blog.html`, `blog/*.html` | Blog listing + one page per post |
| `news.html` | All media coverage |
| `privacy-policy.html`, `terms-of-service.html` | Legal pages |
| `platform/` | The full platform mini-site (landing + 13 chapters + 35 MB PDF) |
| `site.css`, `home.css` | Shared styles (platform design system + homepage/blog styles) |
| `fonts/`, `img/`, `blog/img/`, `platform/img/` | Fonts and photos |
| `add_post.py`, `add_news.py` | Helpers for adding content (see below) |
| `migrate_blog.py`, `webflow/` | One-time Webflow migration (kept for reference) |
| `shots.js`, `build/` | Screenshot tool + rendered previews (not needed in production) |

## Publishing on GitHub Pages

**Already set up (Jul 7, 2026).** This folder is a git repository connected to
GitHub account **elombardi-website**, and the site is live at:

> https://elombardi-website.github.io/ericforolp-site/

Repository: https://github.com/elombardi-website/ericforolp-site
(public — required for free GitHub Pages; it's all public campaign content).
GitHub Pages is configured to serve the `main` branch, root folder.

### Pointing your real domain at it

1. In the same **Settings → Pages** screen, enter your domain under
   **Custom domain** (e.g. `www.ericforolp.ca`) and Save — this creates a
   `CNAME` file in the repo.
2. At your DNS provider (wherever ericforolp.ca's DNS lives), add:
   - `www` → **CNAME** record pointing to `<your-username>.github.io`
   - For the bare domain `ericforolp.ca` → four **A** records:
     `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
3. Back in Settings → Pages, tick **Enforce HTTPS** once the DNS check passes
   (can take up to an hour).

⚠️ Don't switch DNS until you're ready to leave Webflow — the moment `www`
points at GitHub, the Webflow site (including the survey form at
`/tell-me-what-you-think` and the `/hsr` page) stops being reachable at those
URLs. Test everything on the `github.io` URL first. If you want to keep the
Webflow form alive, host this site on a subdomain first (e.g. `new.ericforolp.ca`)
or move the form to Tally/Formspree before cutting over.

### Publishing updates

After changing anything (or running `add_post.py` / `add_news.py`), run:

```bash
cd "/Users/ericlombardi/HSR Proposal/Website"
git add -A
git commit -m "describe what changed"
git push
```

Pages redeploys automatically on every push (~1 minute). You can also edit
files directly in the browser on github.com (open the file → pencil icon →
Commit changes) — same automatic redeploy.

## Where photos go

| Photo for… | Put the file in… | Then |
|---|---|---|
| Homepage (about, general) | `img/` | reference as `img/name.jpg` in `index.html` |
| A blog post | `blog/img/` | reference as `img/name.jpg` inside the post (posts live in `blog/`) |
| Platform chapters | `platform/img/` | already wired to chapter pages |

JPG for photos (aim under ~500 KB — export at 1600px wide max), PNG for
graphics/screenshots. To swap the About portrait, just replace
`img/eric-portrait.png` keeping the same filename.

## Adding a blog post

1. Write the post as a markdown file (any folder), e.g. `my-post-slug.md` —
   the filename becomes the URL (`blog/my-post-slug.html`):

   ```
   ---
   title: My Post Title
   date: July 15, 2026
   category: campaign updates
   description: One sentence for the blog card and search results.
   ---

   Body in markdown: **bold**, [links](https://…), ## headings, - bullets,
   ![caption](img/photo.jpg) for images (put the file in blog/img/ first).
   Raw HTML like <iframe> embeds passes through untouched.
   ```

2. Run: `python3 add_post.py my-post-slug.md`

   This writes the page, adds the card to the top of `blog.html`, and links
   it from the previous post. If it should appear in the homepage
   "From the blog" strip, update the three cards in `index.html` (copy the
   new card from `blog.html` and delete the oldest).

3. Commit and push (see above).

## Adding a news / media item

```bash
python3 add_news.py "Outlet Name" "Headline" "Jul 15, 2026" "https://link"
```

Adds it to the top of `news.html`. To feature it on the homepage, paste the
same `<a class="newsitem">…</a>` line into the "Featured news" list in
`index.html` and remove the oldest (keep ~4).

## Regenerating the platform pages

The platform mini-site is generated from `../PlatformSite/` (which reads
`../Platform/sections.json`). After changing platform content:

```bash
cd ../PlatformSite && python3 generate_site.py
cp -R index.html sections site.css ../Website/platform/
cd ../Website && sed -i '' 's|https://www.ericforolp.ca|..|g' platform/index.html platform/sections/*.html
```

(Then re-apply the nav label/CTA if the generator still has old ones — or ask Claude.)

## Previewing / screenshots

Open any `.html` file directly in a browser, or render full-page screenshots
of every page (desktop + mobile) into `build/`:

```bash
node shots.js
```
