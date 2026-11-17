# Briefing for an AI agent working on the Surface Studio website

Read this first. It describes the business, the live site, how the code is built, the pricing rules and the open items.

## The business
- **Surface Studio**: a PU paint and PU polish finishing workshop in **Bollaram Industrial Area (IDA Bollaram), Bollaram Village, Hyderabad, Telangana 502325**. Plus Code G8XV+8C5, lat 17.5484382, lng 78.343641.
- Phone and WhatsApp **+91 95059 69558**. Hours Mon–Sat 9:30 am–5:30 pm, Sunday closed.
- Google Maps place_id `ChIJqzA2LwCNyzsREJtpRkI6IGA`. The Business Profile is **not** managed by surfacestudiohyd@gmail.com (0 businesses there), so ownership is unresolved.
- Coating brands: **Sirca, ICA, Axalta**, shown as text names only. Never draw or copy their logos.
- Clients: interior firms (Incarved Interio, Flow Interiors, Ras Nexus, Cubical Flow Modulars and others), modular factories and homeowners.
- Quotes, clients and items live in **Zoho Books**, organization_id `60073098158`.
- No Google reviews yet. Do not invent ratings, reviews, testimonials, client logos or statistics.

## The website
- Live: **https://surfacestudio.co.in** (GitHub Pages, HTTPS enforced; www and http redirect to it).
- Repo: **github.com/surfacestudiohyd-sketch/surface-studio-site**. Pages serves the **`docs/`** folder of `main`. `docs/CNAME` = `surfacestudio.co.in`.
- DNS at GoDaddy: four A records 185.199.108–111.153 and `www` CNAME → `surfacestudiohyd-sketch.github.io`.
- **Workflow the owner chose:** every change goes on a branch and opens a **pull request**; the owner merges. Do not push to `main`.
- Dark theme (#121216 background, orange #FF8A1F → purple #B44CE6 accents, Outfit font). Buttons use a darker gradient (#C2410C → #A532C2) for contrast.

### Pages
- `/`: home. Sections: hero (typing headline, starting prices, open-now status), services, instant quote, who we work with, PU guide, brands (rate card per brand), shade library, process, FAQ, contact (quote form + Google map + address), areas served, guides links.
- `/pu-paint-hyderabad/`, `/pu-polish-hyderabad/`, `/pu-paint-polish-price-hyderabad/`, `/sirca-vs-ica-vs-axalta/`, `/modular-panel-pu-finishing/`: SEO landing pages with Service, FAQPage and BreadcrumbList JSON-LD.
- `404.html`, `sitemap.xml`, `robots.txt` (welcomes AI crawlers), `llms.txt` (plain summary for AI engines), `favicon.svg`.
- Security: strict CSP (meta tag + `_headers` / `.htaccess` for hosts that read them), no inline scripts (JS in `docs/js/`), external links with `rel="noopener noreferrer"`, no trackers.
- Images in `docs/images/` are **drawn illustrations**, not real job photos. The owner should supply real photos; stock and Google images could not be downloaded here.

## Instant quote calculator (`docs/js/quote.js`)
- Inputs: factory panel list as **PDF** (read in the browser with Mozilla pdf.js, bundled in `docs/js/vendor/`), **.xlsx** (own zip/XML reader), or **.csv**; **drawings** (PDF/photos) sent to an AI service when configured; or rows typed by hand.
- Recognised columns: NAME1, MATNAME, CLENG, CWIDTH, CNT, BARCODE, FTHK, DESIGN, EDGES (and common synonyms such as Length/Width/Qty). BSL in MATNAME means 2 sides, OSL means 1.
- **Pricing, matching the owner's Zoho quotes (checked against QT-000050):**
  - area sq ft = L × W × qty × sides / 92,903.04
  - edges rft = 2 × (L + W) × qty / 304.8 (only when the Edges box is ticked)
  - amount = area × rate_sqft + edges × rate_rft; ×1.5 for panels ticked **Design** (grooves, profiles, CNC)
  - GST 18% on top. Rates come from `build/rates.json`, copied from Zoho Books items named like `PU Paint - Sirca - Matte - sft` / `- rft`.
- **The visitor sees only the total (incl. GST).** For the breakdown they enter name and mobile, and WhatsApp opens with the quote code (`SSQ-yymmdd-XXXXXX`).
- **Quote log:** when `quote_log_endpoint` is set in `build/rates.json`, each quote (event `calculated`, once per code) and each breakdown request (event `whatsapp`, with name and mobile) is sent with `sendBeacon` to a Google Apps Script web app (`tools/quote-log/Code.gs`). It writes to the sheet "Surface Studio – Website Quotes" (ID `1SgvSuF3G2-oyFKuCGFxNm9b6x0ScbOZfe__ADn3pxOk`), tabs **Quotes** and **Panels**.
- **Drawing reader:** when `ai_endpoint` is set, drawings are POSTed to a Cloudflare Worker (`tools/drawing-reader/worker.js`). It calls the Anthropic Messages API with a forced `record_panels` tool and returns panels as JSON. The API key is a Worker secret.
- The CSP `connect-src` is widened automatically by `build/convert.py` only for configured endpoints.

## Build
`build/` holds the generators. They were written for the original workspace and use absolute paths under `/home/claude/` (build dir `/home/claude/build`, canvas file `/home/claude/site/project/Main.dc.html`, output `/home/claude/out/surface-studio-site`). Before using them elsewhere, change those paths. Otherwise, edit files in `docs/` directly and keep the rules above.
- `gen.py` writes the home page source (a design-canvas `.dc.html`) and `head_filled.html` (meta tags + JSON-LD). Content for services, brand rate cards and the shade library is in `products.py`.
- `convert.py` turns that into static `docs/index.html`, writes `js/site.js` and `js/quote.js` (injecting `rates.json`), copies pdf.js, and fills in the CSP.
- `pages.py` writes the five landing pages, `css/pages.css` and `sitemap.xml`.
- `quote.js` in `build/` is the calculator source with a `__RATES__` placeholder.
- Test with headless Chrome (Playwright). Serve `.mjs` as `text/javascript` or the PDF reader won't load.

## Open items (as of 17 Nov 2026)
1. **Public rates:** the site shows Zoho list rates (Axalta matte ₹300 sq ft + ₹80 rft). QT-000050 was quoted at ₹255 + ₹50. The owner has not said which to publish.
2. **Email:** the site shows sales@surfacestudio.in but the domain is surfacestudio.co.in. The correct address is not confirmed.
3. **Search Console:** the URL-prefix property `https://surfacestudio.co.in/` is added under surfacestudiohyd@gmail.com. Verification file `docs/googlef08e83d939db81b9.html` (PR #4) must be merged, then press Verify and submit `sitemap.xml`.
4. **Google Business Profile:** find which account owns the listing, or claim it. Then add the website, services, categories and real photos. Do not create a duplicate listing.
5. **Quote log:** deploy `tools/quote-log/Code.gs` as a web app and set `quote_log_endpoint`.
6. **Drawing reader:** deploy the Worker with an Anthropic key and spend limit, then set `ai_endpoint`.
7. Real job photos and Google reviews are the biggest remaining gains.

## Rules to keep
- Use only facts above or ones the owner confirms. No made-up prices, reviews, client names or claims.
- Keep the rate card in `build/rates.json` as the single source of prices.
- Keep everything accessible: real buttons and labels, 44px tap targets, 4.5:1 contrast, works at 390px wide.
- Open a pull request for every change and describe what was checked and what was not.
