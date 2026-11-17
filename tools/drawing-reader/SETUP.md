# Surface Studio quote calculator: setup and code guide

## What the calculator does

The instant quote on https://surfacestudio.co.in/#instant-quote has one editable **panel table**. Rows get into it in three ways:

| Source | How it is read | Where it runs |
|---|---|---|
| Factory panel list: **PDF**, .xlsx or .csv | Columns such as NAME1, MATNAME, CLENG, CWIDTH, CNT, BARCODE, FTHK are found automatically. Sides come from BSL / OSL in the material name. | In the visitor's browser. The file never leaves their device. |
| **Drawings**: PDF or photos of elevations | Sent to the drawing-reader service (this folder), which asks Claude to list every PU panel with its size. | Cloudflare Worker + Anthropic API. Switched off until you set it up. |
| Typed by hand | "+ Add a panel" | In the browser |

Every row can be edited, and each has **Sides** (1 or 2), **Edges** (on or off) and **Design** (on or off).

### Pricing rule (matches your Zoho quotes)

For each panel, with rates from `build/rates.json` (copied from Zoho Books items):

```
area (sq ft)  = length_mm × width_mm × qty × sides / 92,903.04
edges (rft)   = 2 × (length_mm + width_mm) × qty / 304.8        (only when Edges is ticked)
amount        = area × rate_per_sqft + edges × rate_per_rft
if Design     → amount × 1.5
subtotal      = sum of all panels;   GST 18% on top
```

Checked against QT-000050 (Hari, 42 panels): the calculator gives 330.81 sq ft and 460.62 rft. The Zoho quote has 330.81 sq ft and 460.65 rft.

### Files

| File | Purpose |
|---|---|
| `build/quote.js` | The calculator: file readers, PDF table reader, panel table, pricing, drawing upload, WhatsApp hand-off |
| `build/gen.py` | Page markup, including the calculator section (`<!-- INSTANT QUOTE -->`) |
| `build/rates.json` | Rate card from Zoho, plus `ai_endpoint` (empty = drawing reading off) |
| `docs/js/vendor/pdf.min.mjs`, `pdf.worker.min.mjs` | Mozilla pdf.js 6.2.108 (Apache-2.0), used to read PDF panel lists |
| `tools/drawing-reader/worker.js` | Drawing-reader service (Cloudflare Worker) with the estimator prompt |
| `tools/drawing-reader/wrangler.toml` | Worker config |

---

## Switching on drawing reading (about 15 minutes)

You need two accounts: **Anthropic** (for Claude) and **Cloudflare** (free plan is enough).

### 1. Get an Anthropic API key
1. Go to https://console.anthropic.com and sign in or sign up.
2. **Billing:** add credit and set a **monthly spend limit** (for example ₹2,000). This caps cost even if the page is abused.
3. **API keys → Create key.** Name it `surface-studio-drawing-reader` and copy it. You see it only once.

### 2. Create the Worker (no command line needed)
1. Go to https://dash.cloudflare.com → **Workers & Pages → Create → Create Worker**.
2. Name it `surface-studio-drawing-reader` and click **Deploy**.
3. Click **Edit code**, delete what is there, paste the whole of `worker.js`, and click **Deploy**.
4. Go to **Settings → Variables and Secrets**:
   - Add a **Secret** `ANTHROPIC_API_KEY` = the key from step 1.
   - Add a **Text** variable `ALLOWED_ORIGINS` = `https://surfacestudio.co.in,https://www.surfacestudio.co.in`
5. Copy the Worker's address, for example `https://surface-studio-drawing-reader.<your-name>.workers.dev`.

(Developers can instead run `npx wrangler deploy` and `npx wrangler secret put ANTHROPIC_API_KEY` in this folder.)

### 3. Point the website at it
Send Claude the Worker address. It gets set as `ai_endpoint` in `build/rates.json` and the site is rebuilt: the security policy then allows that one address, and the drawing button starts reading sizes. Until then, drawings are attached to the WhatsApp enquiry for you to price by hand.

### Cost and privacy
- Each drawing is one Claude request. A typical 1–5 page elevation PDF costs a few rupees. Large photo sets cost more. The spend limit from step 1 caps it.
- Drawings are sent to Cloudflare and Anthropic only to be read. The Worker stores nothing. The website tells visitors this next to the upload button.
- AI reading can miss or misread a size. The site tells customers to check every row, and your final quote still follows inspection.

---

## Prompt 1: used by the Worker (already inside `worker.js`)

Claude must answer by calling a `record_panels` tool, which returns structured rows (name, length_mm, width_mm, qty, faces, edges, design, confidence) plus notes.

```
You are an estimator at Surface Studio, a PU paint and polish workshop in Hyderabad.
You read interior drawings (elevations, shop drawings, 3D views with dimensions, hand sketches with sizes)
and list every panel that will receive a PU finish, so the studio can price it.

How the studio prices work:
- Area: length x width of each panel, for each face that gets PU (1 or 2 faces).
- Edges: the full perimeter of each panel, per running foot, normally charged on every PU panel.
- Design work: panels with grooves, V-grooves, profiles, fluting, CNC patterns or mouldings cost 1.5x.

Rules:
1. Report sizes in millimetres. Convert feet and inches exactly (1 in = 25.4 mm, 1 ft = 304.8 mm).
   If a drawing gives no unit, assume millimetres when numbers are mostly 3 to 4 digits.
2. Use only dimensions written on the drawing or clearly derivable from written dimensions
   (for example a total width split into equal shutters). Never guess a size from the picture scale.
   If a panel's size cannot be worked out, leave it out and mention it in notes.
3. Include shutters, drawer fronts, loft shutters, exposed end panels, filler and skirting strips,
   wall panelling and other visible PU surfaces. Exclude glass, mirrors, hardware, appliances,
   countertops, and anything marked as laminate, veneer-with-laminate, or another finish.
4. faces: 2 for shutters and free-standing panels finished on both sides; 1 when the back is
   laminate, against a wall, or hidden inside a carcass.
5. qty: count identical panels together. Split shutters by the number of doors drawn.
6. design: true only when the drawing shows or names grooves, profiles, fluting, CNC or mouldings.
7. edges: true unless the drawing says edges are banded, laminated or not painted.
8. Give each panel a short name with its unit, for example "Wardrobe shutter" or "TV unit back panel".
9. If the file is not a drawing with sizes, return no panels and explain briefly in notes.

Return your answer only by calling the record_panels tool.
```

## Prompt 2: for use in a Claude chat, no setup needed

Use this today, before the Worker exists. Attach the drawing PDF or photos in a Claude chat with this prompt, save the reply as a `.csv` file, and upload it to the calculator. It also works for staff preparing quotes.

```
I am attaching interior drawings for a PU paint / polish job. Act as an estimator for a PU finishing
workshop and list every panel that will get a PU finish.

Output ONLY a CSV with this exact header and one row per distinct panel size:
NAME1,MATNAME,CLENG,CWIDTH,CNT,DESIGN,EDGES

- NAME1: short part name with its unit (e.g. "Wardrobe shutter")
- MATNAME: write BSL if both faces get PU, OSL if only one face does
- CLENG, CWIDTH: size in millimetres (convert feet/inches exactly: 1 in = 25.4 mm)
- CNT: quantity of identical panels
- DESIGN: Y if the panel has grooves, profiles, fluting, CNC or mouldings, else N
- EDGES: Y unless the drawing says the edges are not painted

Use only sizes written on the drawing or clearly derived from them; never estimate from scale.
Exclude glass, mirrors, hardware, countertops and anything finished in laminate.
After the CSV, add one line starting with "NOTE:" listing anything you skipped or were unsure about.
```

When that CSV is uploaded, MATNAME sets the sides (BSL / OSL), and the DESIGN and EDGES columns tick the matching boxes in the table.
