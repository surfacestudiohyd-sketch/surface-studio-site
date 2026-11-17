"""Builds the SEO landing pages (static HTML) into the output folder. Content uses only the Zoho rate card and facts already on the home page."""
import json, os, sys, html
sys.path.insert(0, '/home/claude/build')
from products import RATES, PAINT_FROM, POLISH_FROM, METAL_FROM
OUT = sys.argv[1]
URL = 'https://surfacestudio.co.in'
MAPS = 'https://www.google.com/maps/search/?api=1&query=Surface%20Studio%20Bollaram&query_place_id=ChIJqzA2LwCNyzsREJtpRkI6IGA'
CSP = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: blob:; frame-src https://www.google.com; connect-src 'self'; object-src 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests"
EXT = ' target="_blank" rel="noopener noreferrer"'
R = lambda k, u='sft': int(RATES[k][u])

CSS = '''*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:#121216;color:#F4F4F6;font-family:Outfit,system-ui,sans-serif;line-height:1.65;padding-bottom:0}
a{color:#FF9A3C}a:hover{color:#FFB770}
:focus-visible{outline:2px solid #FF9A3C;outline-offset:3px}
.wrap{max-width:860px;margin:0 auto;padding:0 24px}
header{position:sticky;top:0;z-index:20;background:rgba(18,18,22,.9);backdrop-filter:blur(14px);border-bottom:1px solid #24242B}
.bar{max-width:1200px;margin:0 auto;padding:14px 24px;display:flex;align-items:center;justify-content:space-between;gap:16px}
.logo{display:flex;flex-direction:column;line-height:.95;font-weight:800;font-size:17px;letter-spacing:.04em;color:#F4F4F6;text-decoration:none;min-height:44px;justify-content:center}
.logo span span{display:inline-block;width:11px;height:11px;border-radius:50%;background:linear-gradient(135deg,#FF8A1F,#B44CE6);margin-left:2px}
.btn{display:inline-flex;align-items:center;justify-content:center;min-height:48px;padding:0 24px;border-radius:999px;font-weight:600;font-size:15px;text-decoration:none;color:#fff;background:linear-gradient(90deg,#C2410C,#A532C2)}
.btn:hover{color:#fff}.btn.ghost{background:none;border:1px solid #3A3A44;color:#F4F4F6}
nav.crumb{font-size:13px;color:#A9A9B3;padding:26px 0 0}nav.crumb a{color:#C9C9D1}
h1{font-size:clamp(34px,6vw,56px);line-height:1.06;letter-spacing:-.02em;margin:14px 0 0}
h2{font-size:clamp(24px,3.4vw,32px);line-height:1.15;letter-spacing:-.01em;margin:56px 0 12px}
h3{font-size:19px;margin:28px 0 6px}
p,li{font-size:17px;color:#D6D6DC}p.lead{font-size:20px;color:#F4F4F6;margin:18px 0 0}
.muted{color:#A9A9B3;font-size:14px}
ul,ol{padding-left:22px}li{margin:6px 0}
.cta{display:flex;flex-wrap:wrap;gap:12px;margin:28px 0 0}
.tbl{overflow-x:auto;border:1px solid #2A2A32;border-radius:16px;background:#1D1D23;margin:16px 0 0}
table{width:100%;border-collapse:collapse;font-size:15px;min-width:420px}
th,td{padding:12px 16px;text-align:left;border-bottom:1px solid #2A2A32}thead th{color:#C9C9D1;font-weight:600}
tbody tr:last-child th,tbody tr:last-child td{border-bottom:0}tbody th{font-weight:500}
figure{margin:32px 0 0}figure img{width:100%;height:auto;border-radius:18px;border:1px solid #2A2A32;display:block}figcaption{font-size:13px;color:#A9A9B3;margin-top:8px}
details{border-bottom:1px solid #2A2A32}summary{cursor:pointer;list-style:none;display:flex;justify-content:space-between;gap:16px;align-items:center;min-height:56px;font-weight:600;font-size:17px}
summary::-webkit-details-marker{display:none}summary::after{content:"+";color:#FF9A3C;font-size:24px;font-weight:300}details[open] summary::after{content:"\\2212"}
details p{margin:0 0 18px;font-size:16px;color:#C9C9D1}
.box{margin:56px 0 0;padding:32px;border-radius:22px;border:1px solid #2A2A32;background:#1D1D23}.box h2{margin-top:0}
.more{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;list-style:none;padding:0;margin:16px 0 0}
.more a{display:block;padding:16px 18px;border-radius:14px;border:1px solid #2A2A32;background:#1D1D23;color:#F4F4F6;text-decoration:none;font-weight:600;font-size:16px}.more a:hover{border-color:#FF9A3C}
.more span{display:block;font-weight:400;font-size:14px;color:#A9A9B3;margin-top:4px}
footer{margin-top:80px;border-top:1px solid #24242B;background:#0F0F12;padding:36px 0 40px;font-size:14px;color:#A9A9B3}footer a{color:#C9C9D1}
footer p{font-size:14px;color:#A9A9B3;margin:6px 0}
.ss-bar{display:none}
@media (max-width:900px){.ss-bar{display:grid;grid-template-columns:1fr 1fr 1.3fr;gap:8px;position:fixed;left:0;right:0;bottom:0;z-index:30;padding:8px 10px calc(8px + env(safe-area-inset-bottom));background:rgba(18,18,22,.96);border-top:1px solid #2A2A32}
.ss-bar a{display:flex;align-items:center;justify-content:center;min-height:48px;border-radius:999px;border:1px solid #3A3A44;font-weight:600;font-size:14px;color:#F4F4F6;text-decoration:none}
.ss-bar a.main{border:0;background:linear-gradient(90deg,#C2410C,#A532C2);color:#fff}body{padding-bottom:calc(66px + env(safe-area-inset-bottom))}.bar .btn{padding:0 18px}}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
'''

def table(head, rows):
    h = ''.join(f'<th scope="col">{c}</th>' for c in head)
    b = ''.join('<tr>' + f'<th scope="row">{r[0]}</th>' + ''.join(f'<td>{c}</td>' for c in r[1:]) + '</tr>' for r in rows)
    return f'<div class="tbl"><table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'

PAGES = {}
ALL = [('pu-paint-hyderabad', 'PU paint in Hyderabad', 'Solid colours on MDF and HDHMR'),
       ('pu-polish-hyderabad', 'PU polish in Hyderabad', 'Clear and tinted polish on wood'),
       ('pu-paint-polish-price-hyderabad', 'PU price per sq ft', 'Full rate card and how we measure'),
       ('sirca-vs-ica-vs-axalta', 'Sirca vs ICA vs Axalta', 'Which coating brand to choose'),
       ('modular-panel-pu-finishing', 'Modular panel finishing', 'For factories and interior firms')]

paint_rows = [[b, f'₹{R(f"paint|{b}|Matte")}', f'₹{R(f"paint|{b}|Glossy")}'] for b in ('Sirca', 'ICA', 'Axalta')]
polish_rows = [[b, f'₹{R(f"polish|{b}|Matte|Natural")}', f'₹{R(f"polish|{b}|Glossy|Natural")}', f'₹{R(f"polish|{b}|Matte|Coloured")}', f'₹{R(f"polish|{b}|Glossy|Coloured")}'] for b in ('Sirca', 'ICA', 'Axalta')]
full_rows = []
for k, v in sorted(RATES.items()):
    w, b, *f = k.split('|')
    full_rows.append([('PU Paint' if w == 'paint' else 'PU Polish') + ' · ' + b + ' · ' + ' · '.join(f), f'₹{int(v["sft"])}', f'₹{int(v["rft"])}'])

PAGES['pu-paint-hyderabad'] = dict(
    title='PU Paint in Hyderabad | Price from ₹%d/sq ft | Surface Studio' % PAINT_FROM,
    desc='PU paint for kitchen shutters, wardrobes and panels in Hyderabad. Sirca, ICA and Axalta, matte or glossy, any RAL shade. From ₹%d per sq ft. Upload a cutlist for an instant quote.' % PAINT_FROM,
    h1='PU paint in Hyderabad', service='PU Paint', low=PAINT_FROM,
    lead=f'Surface Studio sprays solid-colour PU paint on MDF and HDHMR shutters, wardrobes and wall panels at its studio in IDA Bollaram, Hyderabad. Prices start at ₹{PAINT_FROM} per sq ft before GST.',
    img=('hero-pu-wardrobe.jpg', 1600, 1000, 'Illustration: wardrobe with sage-green matte PU shutters', 'Illustration of a matte PU painted wardrobe.'),
    body=f'''<h2>What PU paint is</h2>
<p>PU paint is a two-component polyurethane coating. It is mixed with a hardener, sprayed in thin layers and cured into a hard, smooth film. Pigmented PU covers the board in a solid colour, in a matte or glossy finish.</p>
<h2>PU paint price per sq ft</h2>
<p>Rates are per finished face, before 18% GST.</p>
{table(['Brand', 'Matte', 'Glossy'], paint_rows)}
<p class="muted">Axalta metallic is ₹{R("paint|Axalta|Metallic")} and Axalta pearl is ₹{R("paint|Axalta|Pearl")} per sq ft. Edges are charged per running foot, measured around each panel. See the <a href="/pu-paint-polish-price-hyderabad/">full rate card</a>.</p>
<h2>How a PU painted shutter is built up</h2>
<ol><li><strong>Board:</strong> smooth, stable MDF or HDHMR.</li><li><strong>Sanding and edge sealing:</strong> faces and edges closed off.</li><li><strong>PU sealer and primer:</strong> built up and sanded level.</li><li><strong>Colour coats:</strong> shade-matched PU.</li><li><strong>Finish coat:</strong> matte or glossy.</li></ol>
<p>For kitchens and humid areas we recommend HDHMR over standard MDF, with every face and edge sealed.</p>
<h2>Colours and finishes</h2>
<p>We match any RAL or NCS code, a laminate, or a physical sample, and spray a sample panel for approval before production. Solid colours come in matte or glossy from all three brands. Metallic and pearl finishes are done in Axalta.</p>
<h2>Where PU paint is used</h2>
<ul><li>Modular kitchen shutters and islands</li><li>Wardrobe and loft shutters</li><li>TV units and wall panelling</li><li>Doors and loose furniture</li></ul>''',
    faq=[('How much does PU paint cost per sq ft in Hyderabad?', f'At Surface Studio, PU paint starts at ₹{PAINT_FROM} per sq ft for Axalta matte and goes up to ₹{R("paint|Sirca|Glossy")} for Sirca or ICA glossy, per finished face, before 18% GST.'),
         ('Is PU paint better than Duco?', 'For most interiors, yes. PU is more durable, keeps its gloss longer and is more flexible, so it is less likely to yellow, fade or crack than Duco. It costs more and needs skilled spray application.'),
         ('Can PU paint be applied over laminate?', 'Yes, once the laminate is properly prepared with a specialised adhesion primer. Any peeling or swollen laminate has to be repaired first.'),
         ('Will white PU paint turn yellow?', 'Standard PU can yellow slightly over time. For whites and pale shades, ask us about the most colour-stable option when you request your quote.')])

PAGES['pu-polish-hyderabad'] = dict(
    title='PU Polish in Hyderabad | Price from ₹%d/sq ft | Surface Studio' % POLISH_FROM,
    desc='PU polish for veneer, teak doors and wooden furniture in Hyderabad. Natural or tinted, matte or glossy, in Sirca, ICA and Axalta. From ₹%d per sq ft.' % POLISH_FROM,
    h1='PU polish in Hyderabad', service='PU Polish', low=POLISH_FROM,
    lead=f'Surface Studio applies clear and tinted PU polish to veneer and solid wood at its studio in IDA Bollaram, Hyderabad. The grain stays visible and protected. Prices start at ₹{POLISH_FROM} per sq ft before GST.',
    img=('teak-pu-polish-door.jpg', 1200, 960, 'Illustration: teak veneer door finished in clear glossy PU polish', 'Illustration of a teak door under clear glossy PU polish.'),
    body=f'''<h2>What PU polish is</h2>
<p>PU polish is a transparent polyurethane coating for wood and veneer. It protects the surface from scratches, stains and moisture while letting the natural grain show. A natural polish keeps the wood's own tone. A coloured polish adds a tint, such as walnut or wenge.</p>
<h2>PU polish price per sq ft</h2>
<p>Rates are per finished face, before 18% GST.</p>
{table(['Brand', 'Natural matte', 'Natural glossy', 'Coloured matte', 'Coloured glossy'], polish_rows)}
<p class="muted">Edges are charged per running foot, measured around each panel. See the <a href="/pu-paint-polish-price-hyderabad/">full rate card</a>.</p>
<h2>How PU polish is applied</h2>
<ol><li><strong>Sanding:</strong> the grain is opened and smoothed.</li><li><strong>Filling:</strong> pores, holes and cracks are made good.</li><li><strong>PU sealer:</strong> two coats, sanded between.</li><li><strong>Clear topcoat:</strong> matte, glossy or a natural "invisible" look.</li></ol>
<h2>PU polish vs melamine polish</h2>
<p>PU is more durable than melamine, holds its sheen longer and resists yellowing and cracking better. Melamine is cheaper and gives a basic level of protection.</p>
<h2>What we polish</h2>
<ul><li>Veneer shutters and wall panels</li><li>Teak and other solid-wood doors, including re-polishing old doors</li><li>Dining tables, chairs and loose furniture</li></ul>''',
    faq=[('How much does PU polish cost per sq ft in Hyderabad?', f'At Surface Studio, PU polish starts at ₹{POLISH_FROM} per sq ft for Axalta natural matte and goes up to ₹{R("polish|Sirca|Glossy|Coloured")} for Sirca or ICA coloured glossy, per finished face, before 18% GST.'),
         ('Can old teak doors be re-polished with PU?', 'Yes. The old polish is sanded back, holes and cracks are filled, two coats of PU sealer go on, and the door is finished with a clear matte or glossy topcoat.'),
         ('What is the difference between PU polish and PU paint?', 'PU polish is clear or lightly tinted and keeps the wood grain visible. PU paint is pigmented and covers the surface in a solid colour.'),
         ('How do I care for a PU polished surface?', 'Wipe with a soft microfibre cloth and mild soap. Avoid harsh chemicals, abrasive pads and standing water, and let the finish cure fully before heavy use.')])

PAGES['pu-paint-polish-price-hyderabad'] = dict(
    title='PU Paint & Polish Price per Sq Ft in Hyderabad (Rate Card) | Surface Studio',
    desc='Full PU paint and PU polish rate card for Hyderabad: Sirca, ICA and Axalta, matte and glossy, per sq ft and per running foot. Upload a cutlist for an instant estimate.',
    h1='PU paint and polish price per sq ft in Hyderabad', service='PU paint and polish', low=POLISH_FROM,
    lead=f'PU paint starts at ₹{PAINT_FROM} per sq ft and PU polish at ₹{POLISH_FROM} per sq ft at Surface Studio, Hyderabad. This is our complete rate card, before 18% GST.',
    img=None,
    body=f'''<h2>Complete rate card</h2>
{table(['Finish', 'Per sq ft', 'Per running ft'], full_rows)}
<p class="muted">Prices are per finished face, before 18% GST. The per running ft rate applies to panel edges.</p>
<h2>How we measure</h2>
<ul><li><strong>Per sq ft:</strong> length × width of each panel, for every face that gets PU.</li><li><strong>One side or both:</strong> factory lists mark panels BSL (both sides lacquered) or OSL (one side, laminate behind). Shutters are usually BSL and carcass sides OSL.</li><li><strong>Design work:</strong> panels with grooves, profiles, fluting or other design work are charged at 1.5× the plain rate.</li><li><strong>Per running foot:</strong> the edges, measured around the full perimeter of each panel, charged in addition to the area.</li></ul>
<h2>Worked example</h2>
<p>A wardrobe shutter of 2100 × 450 mm is 10.17 sq ft per face and 16.73 running ft around its edges. Painted on both sides in Sirca matte PU, that is 20.34 sq ft × ₹{R("paint|Sirca|Matte")} + 16.73 rft × ₹{R("paint|Sirca|Matte","rft")} = ₹{round(2100*450*2/92903.04*R("paint|Sirca|Matte")+2*(2100+450)/304.8*R("paint|Sirca|Matte","rft")):,} before GST.</p>
<h2>Get your own figure</h2>
<p>Upload your cutlist, or type an approximate area, in the <a href="/#instant-quote">instant quote</a>. It applies this rate card and gives you a quote code to send us on WhatsApp. The final quote follows a panel inspection at the studio.</p>''',
    faq=[('What is the PU paint rate per sq ft in Hyderabad?', f'Surface Studio charges ₹{PAINT_FROM} to ₹{R("paint|Sirca|Glossy")} per sq ft for solid-colour PU paint, depending on brand and finish, per finished face and before 18% GST. Axalta metallic is ₹{R("paint|Axalta|Metallic")} and pearl is ₹{R("paint|Axalta|Pearl")}.'),
         ('What is the PU polish rate per sq ft in Hyderabad?', f'Surface Studio charges ₹{POLISH_FROM} to ₹{R("polish|Sirca|Glossy|Coloured")} per sq ft for PU polish, depending on brand, sheen and whether it is natural or coloured, before 18% GST.'),
         ('Is GST included in these prices?', 'No. All rates are before 18% GST.'),
         ('Do designed panels cost more?', 'Yes. Panels with grooves, profiles, fluting or other design work are charged at 1.5 times the plain-panel rate, because they take more sanding and spraying.'),
         ('What is the per running foot charge?', 'It covers the edges. Each panel edge is sanded, sealed and sprayed, so we measure the distance around every panel and charge it per running foot, in addition to the area.')])

PAGES['sirca-vs-ica-vs-axalta'] = dict(
    title='Sirca vs ICA vs Axalta PU: Which to Choose? | Surface Studio Hyderabad',
    desc='Sirca, ICA and Axalta PU compared for kitchens, wardrobes and veneer: what each is best for and what each costs per sq ft at Surface Studio, Hyderabad.',
    h1='Sirca vs ICA vs Axalta: which PU should you choose?', service='PU finishing with Sirca, ICA and Axalta', low=POLISH_FROM,
    lead='Surface Studio finishes in all three brands. All three suit kitchens and wardrobes. The right one depends on the look you want and your budget.',
    img=('gloss-navy-pu-panel.jpg', 1200, 960, 'Illustration: deep navy high-gloss PU shutter', 'Illustration of a glossy PU painted shutter.'),
    body=f'''<h2>At a glance</h2>
{table(['', 'Sirca', 'ICA', 'Axalta'], [
 ['Origin', 'Italy', 'Italy', 'Global coatings company'],
 ['We use it most for', 'Kitchen and wardrobe shutters', 'Premium veneer and feature finishes', 'Metallic, pearl and value solid colours'],
 ['PU paint, matte', f'₹{R("paint|Sirca|Matte")}', f'₹{R("paint|ICA|Matte")}', f'₹{R("paint|Axalta|Matte")}'],
 ['PU paint, glossy', f'₹{R("paint|Sirca|Glossy")}', f'₹{R("paint|ICA|Glossy")}', f'₹{R("paint|Axalta|Glossy")}'],
 ['PU polish, natural matte', f'₹{R("polish|Sirca|Matte|Natural")}', f'₹{R("polish|ICA|Matte|Natural")}', f'₹{R("polish|Axalta|Matte|Natural")}'],
 ['Metallic / pearl', 'Not offered', 'Not offered', f'₹{R("paint|Axalta|Metallic")} / ₹{R("paint|Axalta|Pearl")}']])}
<p class="muted">Prices per sq ft, per finished face, before 18% GST.</p>
<h2>Sirca</h2><p>Our usual choice for hard-wearing kitchen and wardrobe shutters. Sirca 2K PU lays down a dense, even film in matte or glossy paint and natural or tinted polish.</p>
<h2>ICA</h2><p>Premium Italian PU for interiors where the finish is the feature: smooth matte paint, deep gloss, and veneer polishes that keep the grain crisp.</p>
<h2>Axalta</h2><p>The range we offer in metallic and pearl, and our value pick for solid matte and glossy shades.</p>
<h2>How to decide</h2>
<ul><li><strong>Kitchen or wardrobe in a solid colour:</strong> Sirca, or Axalta to save a little per sq ft.</li><li><strong>Veneer or a statement piece:</strong> ICA.</li><li><strong>Metallic or pearl fronts:</strong> Axalta.</li></ul>
<p>Not sure? Send us your drawing or a reference photo and we will recommend a system and spray a sample panel.</p>''',
    faq=[('Sirca, ICA or Axalta: which is best for kitchen shutters?', 'All three suit kitchens. Sirca is our usual choice for hard-wearing kitchen shutters, and Axalta is a good-value option for solid colours.'),
         ('Which brand is cheapest?', f'At our rates, Axalta is the lowest for solid colours: ₹{R("paint|Axalta|Matte")} per sq ft for matte PU paint, against ₹{R("paint|Sirca|Matte")} for Sirca and ICA.'),
         ('Which brand do you use for metallic or pearl finishes?', 'Axalta. Metallic and pearl are not on our Sirca or ICA rate card.')])

PAGES['modular-panel-pu-finishing'] = dict(
    title='PU Finishing for Modular Kitchen Factories & Interior Firms | Surface Studio Hyderabad',
    desc='Send your factory cutlist. Surface Studio in IDA Bollaram, Hyderabad, PU-finishes modular panels on one or both sides (BSL / OSL), tracks every panel by barcode and returns them in batches.',
    h1='PU finishing for modular factories and interior firms', service='Modular panel PU finishing', low=PAINT_FROM,
    lead='Send us the panels and the factory panel list. We finish each panel as specified, track it by barcode and return it in batches matched to your project.',
    img=None,
    body=f'''<h2>How it works</h2>
<ol><li><strong>Share the cutlist.</strong> Factory lists with part name, material, length, width, quantity and barcode work as they are.</li><li><strong>Get an estimate.</strong> Upload the same file in the <a href="/#instant-quote">instant quote</a> for a price and quote code.</li><li><strong>Deliver the panels</strong> to our studio in Bollaram Industrial Area (IDA Bollaram).</li><li><strong>We finish and track.</strong> Each panel is checked against the list, finished on one or both sides and inspected.</li><li><strong>Batch dispatch.</strong> Panels go back grouped by unit, such as wardrobe, TV unit or loft.</li></ol>
<h2>BSL and OSL</h2>
<p>We read the material code on your list. <strong>BSL</strong> means both sides lacquered, so both faces are finished and charged. <strong>OSL</strong> means one side lacquered, with laminate on the back, so one face is charged.</p>
<h2>What we check on arrival</h2>
<ul><li>Panel count and sizes against the list</li><li>Thickness in the material name against the listed thickness</li><li>Edges and board condition before coating</li></ul>
<p>Anything that does not match is flagged to you before work starts.</p>
<h2>Rates</h2>
<p>PU paint from ₹{PAINT_FROM} and PU polish from ₹{POLISH_FROM} per sq ft, per finished face, before 18% GST. Edges are charged per running foot, measured around each panel. See the <a href="/pu-paint-polish-price-hyderabad/">full rate card</a>.</p>''',
    faq=[('Which file formats can I upload for a quote?', 'Excel (.xlsx) or CSV with length, width and quantity columns. Factory lists with CLENG, CWIDTH and CNT headings work as they are. For a PDF list, send it to us on WhatsApp.'),
         ('How do you price panels finished on one side?', 'Panels marked OSL are charged for one face. Panels marked BSL are charged for both faces.'),
         ('Where is the studio?', 'Bollaram Industrial Area (IDA Bollaram), Bollaram Village, Hyderabad, Telangana 502325. Open Monday to Saturday, 9:30 am to 5:30 pm.')])

BIZ = {"@type": "HomeAndConstructionBusiness", "@id": URL + "/#business", "name": "Surface Studio", "url": URL + "/", "telephone": "+919505969558",
       "address": {"@type": "PostalAddress", "streetAddress": "Bollaram Industrial Area (IDA Bollaram), Bollaram Village", "addressLocality": "Hyderabad", "addressRegion": "Telangana", "postalCode": "502325", "addressCountry": "IN"}}

def build(slug, p):
    url = f'{URL}/{slug}/'
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "Service", "@id": url + "#service", "name": p['service'], "serviceType": p['service'], "description": p['desc'], "url": url, "areaServed": {"@type": "City", "name": "Hyderabad"}, "provider": BIZ,
         "offers": {"@type": "Offer", "priceCurrency": "INR", "priceSpecification": {"@type": "UnitPriceSpecification", "price": p['low'], "priceCurrency": "INR", "unitText": "sq ft", "description": "Starting price per finished face, before GST"}}},
        {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Home", "item": URL + "/"}, {"@type": "ListItem", "position": 2, "name": p['h1'], "item": url}]},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p['faq']]}]}
    fig = ''
    og = 'hero-pu-wardrobe.jpg'
    if p['img']:
        f, w, h, alt, cap = p['img']; og = f
        fig = f'<figure><img src="/images/{f}" width="{w}" height="{h}" alt="{alt}" fetchpriority="high"><figcaption>{cap}</figcaption></figure>'
    faq = ''.join(f'<details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>' for q, a in p['faq'])
    more = ''.join(f'<li><a href="/{s}/">{t}<span>{d}</span></a></li>' for s, t, d in ALL if s != slug)
    e = html.escape
    page = f'''<!doctype html>
<html lang="en-IN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(p['title'])}</title>
<meta name="description" content="{e(p['desc'])}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="theme-color" content="#121216">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta http-equiv="Content-Security-Policy" content="{CSP}">
<meta name="geo.region" content="IN-TG"><meta name="geo.placename" content="IDA Bollaram, Hyderabad">
<meta property="og:type" content="article"><meta property="og:site_name" content="Surface Studio"><meta property="og:locale" content="en_IN">
<meta property="og:title" content="{e(p['h1'])}"><meta property="og:description" content="{e(p['desc'])}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{URL}/images/{og}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&amp;display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/pages.css">
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=1)}
</script>
</head>
<body>
<header><div class="bar"><a class="logo" href="/" aria-label="Surface Studio home"><span>SURFACE</span><span>STUDI<span></span></span></a><a class="btn" href="/#instant-quote">Instant Quote</a></div></header>
<main class="wrap">
<nav class="crumb" aria-label="Breadcrumb"><a href="/">Home</a> / {e(p['h1'])}</nav>
<h1>{e(p['h1'])}</h1>
<p class="lead">{p['lead']}</p>
<div class="cta"><a class="btn" href="/#instant-quote">Get an instant quote</a><a class="btn ghost" href="https://wa.me/919505969558"{EXT}>WhatsApp us</a></div>
{fig}
{p['body']}
<h2>Questions</h2>
{faq}
<div class="box"><h2>Talk to Surface Studio</h2>
<p>Bollaram Industrial Area (IDA Bollaram), Bollaram Village, Hyderabad, Telangana 502325. Open Monday to Saturday, 9:30 am to 5:30 pm.</p>
<div class="cta"><a class="btn" href="/#instant-quote">Get an instant quote</a><a class="btn ghost" href="tel:+919505969558">Call +91 95059 69558</a><a class="btn ghost" href="{MAPS.replace('&', '&amp;')}"{EXT}>Directions</a></div></div>
<h2>More from Surface Studio</h2>
<ul class="more">{more}</ul>
</main>
<footer><div class="wrap"><p><strong style="color:#F4F4F6">Surface Studio</strong> · PU paint &amp; polish studio, Hyderabad. Finishes by Sirca, ICA and Axalta.</p>
<p><a href="/">Home</a> · <a href="/#finishes">Shade library</a> · <a href="/#faq">FAQ</a> · <a href="/#contact">Contact</a> · <a href="{MAPS.replace('&', '&amp;')}"{EXT}>Google profile</a></p>
<p>© 2026 Surface Studio. Sirca, ICA and Axalta are trademarks of their respective owners.</p></div></footer>
<nav class="ss-bar" aria-label="Quick contact"><a href="tel:+919505969558">Call</a><a href="https://wa.me/919505969558"{EXT}>WhatsApp</a><a class="main" href="/#instant-quote">Instant quote</a></nav>
</body>
</html>
'''
    assert page.count('<h1') == 1 and '<script>' not in page
    os.makedirs(f'{OUT}/{slug}', exist_ok=True)
    open(f'{OUT}/{slug}/index.html', 'w').write(page)

os.makedirs(OUT + '/css', exist_ok=True)
open(OUT + '/css/pages.css', 'w').write(CSS)
for slug, p in PAGES.items(): build(slug, p)
imgs = ['hero-pu-wardrobe.jpg', 'gloss-navy-pu-panel.jpg', 'wood-teak.jpg']
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n  <url>\n    <loc>%s/</loc>\n    <lastmod>2026-11-16</lastmod>\n%s  </url>\n' % (URL, ''.join(f'    <image:image><image:loc>{URL}/images/{i}</image:loc></image:image>\n' for i in imgs))
sm += ''.join(f'  <url>\n    <loc>{URL}/{s}/</loc>\n    <lastmod>2026-11-16</lastmod>\n  </url>\n' for s in PAGES) + '</urlset>\n'
open(OUT + '/sitemap.xml', 'w').write(sm)
print('pages', len(PAGES))
