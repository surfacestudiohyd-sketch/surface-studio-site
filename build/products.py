"""Product content for the Surface Studio site, built from the studio's Zoho Books rate card (rates.json).
Only finishes that are actually on the rate card are shown."""
import json, urllib.parse

RATES = json.load(open('/home/claude/build/rates.json'))['rates']
WA = 'https://wa.me/919505969558?text='
BLOB = {
    'hero': '104b5cdcfad2ef867be56049edc28d6a', 'navy': '6d7e8d05bc8e79f4f837b821a91df98b', 'door': '2ae73c91fd232b9dd80207c8dd933762',
    'teak': '4e861e5150f1535f7aa084e7ad018846', 'walnut': 'cee414d04ae558554a9430262b109e93', 'white-oak': 'b35683588ded28a6fffc8b2ad38d49c4',
    'smoked-oak': '09e26507dd977680686813713a3b7ba4', 'mahogany': 'db466db4c5dbccbf6c02c4ee0da8c9d0', 'wenge': '8be97defdd7c84a4418bfabdfd7b66ec',
}

def low(prefix):
    return int(min(v['sft'] for k, v in RATES.items() if k.startswith(prefix)))

PAINT_FROM, POLISH_FROM, METAL_FROM = low('paint|'), low('polish|'), int(RATES['paint|Axalta|Metallic']['sft'])

services = [
    ('PU Paint', f'Solid-colour 2K polyurethane on MDF and HDHMR shutters, in matte or glossy. Any RAL or NCS shade, or matched to your sample. From ₹{PAINT_FROM} per sq ft.', 'Kitchens · wardrobes · TV units · wall panels'),
    ('PU Polish', f'Clear PU over veneer and solid wood, natural or tinted, in matte or glossy. The grain stays visible and protected. From ₹{POLISH_FROM} per sq ft.', 'Veneer shutters · doors · furniture'),
    ('Metallic &amp; Pearl PU', f'Axalta metallic and pearl topcoats for feature shutters and statement units. From ₹{METAL_FROM} per sq ft.', 'Feature walls · islands · display units'),
    ('Modular Panel Finishing', 'Send your factory cutlist. Every panel is barcode-tracked, finished on one or both sides as listed (BSL / OSL) and returned in batches.', 'Modular factories · interior firms'),
    ('Furniture &amp; Door Refinishing', 'Old polish sanded back, filled and re-coated in PU polish or paint, for doors, chairs and loose furniture.', 'Homes · renovations'),
]

TH = 'padding: 12px 14px; text-align: left; font-weight: 600; color: #C9C9D1; border-bottom: 1px solid #2A2A32'
TD = 'padding: 11px 14px; border-bottom: 1px solid #2A2A32; white-space: nowrap'

def ratecard(brand):
    rows = ''
    for k, v in sorted(RATES.items()):
        work, b, *fin = k.split('|')
        if b != brand:
            continue
        name = ('PU Paint · ' if work == 'paint' else 'PU Polish · ') + ' · '.join(fin)
        rows += (f'<tr><th scope="row" style="{TD}; font-weight: 500; text-align: left; white-space: normal">{name}</th>'
                 f'<td style="{TD}">₹{int(v["sft"])}</td><td style="{TD}; color: #A9A9B3">₹{int(v["rft"])}</td></tr>\n')
    return (f'<div style="overflow-x: auto; border: 1px solid #2A2A32; border-radius: 16px; background: #1D1D23">'
            f'<table style="width: 100%; border-collapse: collapse; font-size: 14px">'
            f'<caption style="caption-side: bottom; padding: 10px 14px; text-align: left; font-size: 12px; color: #A9A9B3">Per finished face, before 18% GST. Strips 100 mm wide or less are charged per running foot.</caption>'
            f'<thead><tr><th scope="col" style="{TH}">{brand} finish</th><th scope="col" style="{TH}">per sq ft</th><th scope="col" style="{TH}">per rft</th></tr></thead>'
            f'<tbody>\n{rows}</tbody></table></div>')

def panel(flag, first, tint, name, sub, body, best, brand):
    return f'''<sc-if value="{{{{{flag}}}}}" hint-placeholder-val="{{{{ {first} }}}}">
<div style="margin-top: 40px; display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 420px), 1fr)); gap: 20px; align-items: start">
<div style="background: linear-gradient(160deg,{tint} 0%,#1D1D23 60%); border: 1px solid #2A2A32; border-radius: 22px; padding: 34px">
<h3 style="margin: 0; font-size: 40px; font-weight: 800; letter-spacing: 0.16em">{name}</h3>
<p style="margin: 6px 0 0; font-size: 14px; color: #A9A9B3">{sub}</p>
<p style="margin: 22px 0 0; font-size: 16px; line-height: 1.7; color: #D6D6DC">{body}</p>
<p style="margin: 18px 0 0; font-size: 14px; color: #A9A9B3"><span style="color: #F4F4F6; font-weight: 600">Best for:</span> {best}</p>
</div>
{ratecard(brand)}
</div>
</sc-if>
'''

panels = panel('isSirca', 'true', '#24201D', 'SIRCA', 'Italian wood coatings',
               'Our go-to for kitchens and wardrobes: Sirca 2K PU lays down a dense, even film with good clarity, in matte or glossy paint and natural or tinted polish.',
               'kitchen shutters, wardrobes, TV units, doors', 'Sirca')
panels += panel('isIca', 'false', '#211D26', 'ICA', 'Italian wood coatings',
                'Premium Italian PU for interiors where the finish is the feature: smooth matte paint, deep gloss, and veneer polishes that keep the grain crisp.',
                'luxury veneers, feature shutters, premium furniture', 'ICA')
panels += panel('isAxalta', 'false', '#1F2329', 'AXALTA', 'Axalta Coating Systems',
                'Known for precise colour and tough films. Axalta is the range we offer in metallic and pearl, and our value pick for solid matte and glossy shades.',
                'metallic and pearl fronts, solid-colour shutters, commercial interiors', 'Axalta')

# ---------- shade library ----------
SWS = 'display: block; width: 100%; aspect-ratio: 1 / 1'
def ask(t):
    return WA + urllib.parse.quote('Hi Surface Studio, I would like a quote for this shade: ' + t)

def card(bg, name, meta, asktext, img=None):
    shiny = any(w in meta for w in ('Glossy', 'Pearl', 'Metallic'))
    if img:
        sw = f'<img src="/_blob/{img}" width="600" height="600" alt="{name} wood tone under clear PU polish" style="{SWS}; height: auto; object-fit: cover">'
    else:
        sw = (f'<span style="{SWS}; background: {bg}"></span>'
              f'<span aria-hidden="true" style="position: absolute; inset: 0; background: linear-gradient(135deg, rgba(255,255,255,0) 38%, rgba(255,255,255,{0.3 if shiny else 0.05}) 47%, rgba(255,255,255,0) 56%)"></span>')
    return (f'<li style="border: 1px solid #2A2A32; border-radius: 16px; background: #1D1D23; overflow: hidden">'
            f'<div style="position: relative">{sw}</div>'
            f'<div style="padding: 12px 14px 4px"><p style="margin: 0; font-weight: 600; font-size: 15px">{name}</p>'
            f'<p style="margin: 3px 0 0; font-size: 13px; color: #A9A9B3">{meta}</p>'
            f'<a href="{ask(asktext)}"$EXT style="display: inline-flex; align-items: center; min-height: 44px; font-size: 13px; font-weight: 600; color: #FF9A3C">Ask on WhatsApp</a></div></li>\n')

SOLID = [('#F1ECE1', 'Pure White', 'RAL 9010'), ('#E9E0D2', 'Cream', 'RAL 9001'), ('#E1D4BF', 'Light Ivory', 'RAL 1015'),
         ('#CBD0CC', 'Light Grey', 'RAL 7035'), ('#B5B0A1', 'Silk Grey', 'RAL 7044'), ('#383E42', 'Anthracite', 'RAL 7016'),
         ('#0E0E10', 'Jet Black', 'RAL 9005'), ('#1D334A', 'Sapphire Blue', 'RAL 5003'), ('#7B8873', 'Sage Green', 'Matched to sample'),
         ('#2F4538', 'Fir Green', 'RAL 6009'), ('#7A4A33', 'Terracotta', 'Matched to sample'), ('#45322E', 'Chocolate', 'RAL 8017')]
METAL = [('linear-gradient(135deg,#7a5a1e,#e8c46a 45%,#9a742a 70%,#f2d68c)', 'Gold', 'Metallic'),
         ('linear-gradient(135deg,#5a3a1c,#c08a52 45%,#6e4524 70%,#d9a36b)', 'Bronze', 'Metallic'),
         ('linear-gradient(135deg,#6b2e18,#d77a4a 45%,#7e3a1f 70%,#e8986a)', 'Copper', 'Metallic'),
         ('linear-gradient(135deg,#8c8478,#e6dfd2 45%,#9a9286 70%,#f2ece2)', 'Champagne', 'Metallic'),
         ('linear-gradient(135deg,#6e7276,#e4e6e8 45%,#80858a 70%,#f4f5f6)', 'Silver', 'Metallic'),
         ('linear-gradient(135deg,#e9e4da,#ffffff 40%,#dcd3e4 60%,#f5efe2)', 'Pearl White', 'Pearl')]
WOOD = [('teak', 'Natural Teak', 'Natural · Glossy'), ('white-oak', 'White Oak', 'Natural · Matte'),
        ('walnut', 'Walnut', 'Coloured · Glossy'), ('smoked-oak', 'Smoked Oak', 'Coloured · Matte'),
        ('mahogany', 'Mahogany', 'Coloured · Glossy'), ('wenge', 'Wenge', 'Coloured · Matte')]
GRID = 'margin: 0; padding: 0; list-style: none; display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 150px), 1fr)); gap: 14px'
H3 = 'font-size: 20px; font-weight: 600'

tiles = (f'<h3 style="margin: 0 0 6px; {H3}">Solid PU colours</h3><p style="margin: 0 0 16px; font-size: 14px; color: #A9A9B3">PU Paint · Sirca, ICA or Axalta · matte or glossy · from ₹{PAINT_FROM}/sq ft</p>'
         f'<ul style="{GRID}">\n' + ''.join(card(b, n, c + ' · Matte or Glossy', f'{n} ({c}) PU paint') for b, n, c in SOLID) + '</ul>\n')
tiles += (f'<h3 style="margin: 40px 0 6px; {H3}">Metallic &amp; pearl</h3><p style="margin: 0 0 16px; font-size: 14px; color: #A9A9B3">Axalta PU Paint · from ₹{METAL_FROM}/sq ft</p>'
          f'<ul style="{GRID}">\n' + ''.join(card(b, n, 'Axalta · ' + f, f'{n} {f.lower()} PU (Axalta)') for b, n, f in METAL) + '</ul>\n')
tiles += (f'<h3 style="margin: 40px 0 6px; {H3}">PU polish wood tones</h3><p style="margin: 0 0 16px; font-size: 14px; color: #A9A9B3">PU Polish on veneer or solid wood · natural or tinted · from ₹{POLISH_FROM}/sq ft</p>'
          f'<ul style="{GRID}">\n' + ''.join(card('', n, 'PU Polish · ' + m, f'{n} PU polish ({m})', img=BLOB[k]) for k, n, m in WOOD) + '</ul>\n')

sheen = [('Matte', 'Soft, low-glare, hides fingerprints best', 'linear-gradient(135deg,#2B2B31 60%,#34343B)', 0),
         ('Glossy', 'Deep and reflective, easy to wipe clean', 'linear-gradient(135deg,#1A1A1E 42%,#9A9AA6 51%,#1A1A1E 60%)', 1)]
