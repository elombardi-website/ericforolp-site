# Images status

**Nothing is currently required.** The hero photo slot became the embedded launch video,
and the survey section now uses topic chips (matching the live site) instead of a photo —
so `survey.jpg` is no longer needed. To add photos anywhere later, see "Where photos go"
in `README.md`.

**Already in place (no action needed):**
- `img/eric-portrait.png` — About section portrait (from the keynote deck)
- `img/pdf-cover.jpg` — platform PDF cover thumbnail (rendered from the document)
- `platform/img/*.jpg` — all 12 chapter photos (pulled from the platform document)

**After you add hero.jpg / survey.jpg:** replace the matching
`<div class="imgzone">…</div>` in `index.html` with
`<img src="img/hero.jpg" alt="" style="width:100%; height:340px; object-fit:cover; border-radius:16px;">`
(or tell Claude and it takes 30 seconds).

## Still pointing at the old Webflow site (migrate later or keep)
- The survey form (`/tell-me-what-you-think`) — forms need a backend; keeping Webflow's for now
- The `/hsr` page (linked from the Alto blog post) — the HSR map tool still lives there
- The 10 language variants (ar, es, fr-ca, he, hi, it, pa, tl, zh, zh-tw) — English only so far

## Migrated off Webflow (Jul 7, 2026)
- All 7 blog posts → `blog/<slug>.html` (bodies captured verbatim; images localized to
  `blog/img/`; the 16 Datawrapper charts in the survey post stay as hosted embeds and work
  on a static site). Prev/next pager + back-to-blog link on each post.
- Privacy Policy → `privacy-policy.html`, Terms of Service → `terms-of-service.html`;
  footers on all pages now link to them.
- Regenerate if needed: `migrate_blog.py` rebuilds all posts from Webflow HTML saved in
  `Website/webflow/` — for a new post, `curl -sL <post-url> -o webflow/blog-<slug>.html`,
  add the slug to POSTS (newest first), run `python3 migrate_blog.py`, and add a card to
  `blog.html`.

## Forms
The Webflow signup/subscribe forms were not recreated (static site has no form backend).
Sign-up CTAs point at action.ontarioliberal.ca/f/eric; subscribe points at team@ericlombardi.ca.
If you want embedded forms, easiest options: keep a Webflow embed, or a Mailchimp/Buttondown embed.
