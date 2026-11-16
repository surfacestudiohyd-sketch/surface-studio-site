# Surface Studio website

PU paint & polish studio, IDA Bollaram, Hyderabad — https://surfacestudio.co.in

## Layout
- `docs/` — the live website, served by GitHub Pages (Settings → Pages → Branch `main`, folder `/docs`).
  - `index.html`, `404.html`, `js/site.js`, `images/`, `favicon.svg`
  - SEO / GEO: `sitemap.xml`, `robots.txt`, `llms.txt`, JSON-LD business + FAQ schema in `index.html`
  - Instant quote: `js/quote.js` reads an uploaded .xlsx/.csv cutlist in the visitor's browser and prices it from the Zoho rate card (`build/rates.json`)
  - `CNAME` sets the custom domain; `.nojekyll` serves files as-is
  - `_headers` / `.htaccess` are security headers for Cloudflare Pages / Apache (ignored by GitHub Pages)
- `build/` — generator scripts the site is built from (`gen.py` → page, `convert.py` → static HTML, `head.html` → meta tags and schema).

## DNS (GoDaddy, surfacestudio.co.in)
TXT `_github-pages-challenge-surfacestudiohyd-sketch` → verification code from GitHub Pages settings
A `@` → 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153
CNAME `www` → surfacestudiohyd-sketch.github.io
