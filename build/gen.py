import json, html as H
MAPS='https://www.google.com/maps/search/?api=1&amp;query=Surface%20Studio%20Bollaram&amp;query_place_id=ChIJqzA2LwCNyzsREJtpRkI6IGA'
REVIEW='https://search.google.com/local/writereview?placeid=ChIJqzA2LwCNyzsREJtpRkI6IGA'
EXT=' target="_blank" rel="noopener noreferrer"'
# button gradient: deeper ends so white label text is >= 4.5:1 everywhere (#C2410C 5.2:1, #A532C2 5.5:1)
BTN='linear-gradient(90deg,#C2410C,#A532C2)'
STAR='<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3.5l2.6 5.3 5.9.9-4.3 4.1 1 5.8-5.2-2.7-5.2 2.7 1-5.8-4.3-4.1 5.9-.9z"></path></svg>'
GPROF='<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 4h6v6"></path><path d="M20 4l-9 9"></path><path d="M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"></path></svg>'
G='background: linear-gradient(90deg,#FF8A1F 0%,#E8565E 50%,#B44CE6 100%); -webkit-background-clip: text; background-clip: text; color: transparent'
EYE='margin: 0 0 14px; font-size: 13px; letter-spacing: 0.16em; text-transform: uppercase; color: #FF9A3C; font-weight: 600'
H2='margin: 0; font-size: clamp(32px, 4vw, 48px); font-weight: 700; letter-spacing: -0.02em; line-height: 1.08'
WRAP='max-width: 1200px; margin: 0 auto; padding: 96px 24px; box-sizing: border-box'
CHIP='padding: 9px 16px; border-radius: 999px; border: 1px solid #3A3A44; font-size: 14px; color: #D6D6DC'
PIN='<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21s7-6.2 7-11.5A7 7 0 0 0 5 9.5C5 14.800 12 21 12 21z"></path><circle cx="12" cy="9.500" r="2.500"></circle></svg>'
WA='<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 20l1.3-4A8 8 0 1 1 8 18.7z"></path></svg>'
LOGO='<span>SURFACE</span><span style="display: flex; align-items: center; gap: 2px">STUDI<span style="display: inline-block; width: 11px; height: 11px; border-radius: 50%; background: linear-gradient(135deg,#FF8A1F,#B44CE6); margin-top: 1px"></span></span>'
chips=lambda xs,st=CHIP:'\n'.join('<span style="%s">%s</span>'%(st,x) for x in xs)

services=[('PU Paint','Solid-colour 2K polyurethane for MDF and HDHMR shutters. Any shade, from dead matt to full gloss, with a hard, scratch-resistant film.','Kitchens · wardrobes · wall panels'),
('PU Polish','Clear sealer and topcoat systems for veneer and solid wood. They protect the grain and let it show: natural, open-pore or full-fill.','Veneer · teak doors · furniture'),
('Polyester High Gloss','Thick-build polyester, rubbed and buffed to a mirror, piano-style finish.','Statement wardrobes · bars · feature panels'),
('Water-based &amp; Low-VOC','Low-odour water-based finishes with the toughness of 2K systems, for occupied homes and tight timelines.','Bedrooms · children\'s rooms · renovations'),
('Metallics &amp; Special Effects','Copper, bronze, corten, pearl, marble and patina effects, sampled and approved before production.','Feature walls · islands · display units'),
('Modular Panel Finishing','Send your factory cutlist. Every panel is barcode-tracked, finished as specified and returned in batches matched to your project.','Modular factories · interior firms')]
svc=''.join('<div style="display: grid; grid-template-columns: 44px minmax(0, 1fr); gap: 4px 12px; padding: 26px 0; border-top: 1px solid #2A2A32"><span style="font-size: 14px; font-weight: 700; color: #FF9A3C; padding-top: 5px">%02d</span><div><h3 style="margin: 0; font-size: 22px; font-weight: 600">%s</h3><p style="margin: 8px 0 0; font-size: 15px; line-height: 1.65; color: #A9A9B3; max-width: 560px">%s</p><p style="margin: 10px 0 0; font-size: 13px; letter-spacing: 0.04em; color: #C9C9D1">%s</p></div></div>\n'%(i+1,t,d,b) for i,(t,d,b) in enumerate(services))

clients=[('Interior designers &amp; architects','Send a drawing and a reference. We sample the finish on a panel for your client to approve, then match it across the whole project.'),
('Modular kitchen factories','Share the panel list. We track every panel by barcode and return finished batches in the order your installers need them.'),
('Homeowners &amp; carpenters','Bring your shutters, doors or furniture to the studio in IDA Bollaram. We help you choose the system, shade and sheen.')]
cli=''.join('<div style="padding: 30px; border-radius: 18px; background: #1D1D23; border: 1px solid #2A2A32"><h3 style="margin: 0 0 10px; font-size: 19px; font-weight: 600">%s</h3><p style="margin: 0; font-size: 15px; line-height: 1.65; color: #A9A9B3">%s</p></div>\n'%c for c in clients)

def anatomy(title,color,rows):
    li=''.join('<li style="display: flex; gap: 16px; align-items: baseline; padding: 13px 18px; border-radius: 12px; background: #24242B"><span style="font-weight: 700; color: %s; font-size: 14px">%02d</span><span style="font-size: 15px; line-height: 1.5"><span style="font-weight: 600">%s</span><span style="color: #A9A9B3"> — %s</span></span></li>\n'%(color,i+1,a,b) for i,(a,b) in enumerate(rows))
    return '<div style="background: #1D1D23; border: 1px solid #2A2A32; border-radius: 22px; padding: 32px"><p style="margin: 0; font-size: 13px; letter-spacing: 0.14em; text-transform: uppercase; color: #A9A9B3">Anatomy of</p><h3 style="margin: 6px 0 22px; font-size: 24px; font-weight: 700">%s</h3><ol style="margin: 0; padding: 0; list-style: none; display: flex; flex-direction: column; gap: 8px">\n%s</ol></div>\n'%(title,li)
an=anatomy('a PU painted shutter','#FF9A3C',[('Board','smooth, stable MDF or HDHMR'),('Sanding &amp; edge sealing','faces and edges closed off'),('PU sealer &amp; primer','built up and sanded level'),('Colour coats','shade-matched PU'),('Finish coat','matt, gloss or a clear coat for depth')])+anatomy('a PU polish','#C98BF0',[('Core','natural wood or veneer'),('Sanding','the grain opened and smoothed'),('Filling','pores, holes and cracks made good'),('PU sealer','two coats, sanded between'),('Clear topcoat','matt, gloss or natural "invisible"')])
td='padding: 15px 22px; border-bottom: 1px solid #2A2A32'
rows=[('Durability','Highest of the three','Lower, can chip','Basic'),('Gloss over time','Holds its sheen','Tends to dull','Tends to fade'),('Yellowing &amp; cracking','Resists both','More prone','More prone'),('Moisture &amp; stains','Strong resistance','Moderate','Basic'),('Flexibility','Moves with the board','Stiffer film','Stiffer film')]
tb=''.join('<tr><th scope="row" style="%s; font-weight: 600">%s</th><td style="%s; background: #24211F">%s</td><td style="%s; color: #A9A9B3">%s</td><td style="%s; color: #A9A9B3">%s</td></tr>\n'%(td,a,td,b,td,c,td,d) for a,b,c,d in rows)

ON='min-height: 44px; padding: 0 26px; border: 0; border-radius: 999px; font-family: Outfit, system-ui, sans-serif; font-weight: 600; font-size: 15px; cursor: pointer; color: #FFFFFF; background: $BTN'
OFF='min-height: 44px; padding: 0 26px; border: 0; border-radius: 999px; font-family: Outfit, system-ui, sans-serif; font-weight: 600; font-size: 15px; cursor: pointer; color: #C9C9D1; background: transparent'
B=[('Sirca','isSirca','pickSirca'),('ICA','isIca','pickIca'),('Axalta','isAxalta','pickAxalta')]
tabs=''
for i,(n,f,_) in enumerate(B):
    tabs+='<sc-if value="{{%s}}" hint-placeholder-val="{{ %s }}">\n'%(f,'true' if i==0 else 'false')
    for j,(m,_,pk) in enumerate(B): tabs+='<button type="button" role="tab" aria-selected="%s" onClick="{{%s}}" style="%s">%s</button>\n'%('true' if i==j else 'false',pk,ON if i==j else OFF,m)
    tabs+='</sc-if>\n'
def panel(flag,first,tint,name,sub,body,best,items):
    it=''.join('<div style="background: #1D1D23; border: 1px solid #2A2A32; border-radius: 16px; padding: 20px"><p style="margin: 0; font-weight: 600; font-size: 16px">%s</p><p style="margin: 6px 0 0; font-size: 14px; line-height: 1.55; color: #A9A9B3">%s</p></div>\n'%x for x in items)
    return '''<sc-if value="{{%s}}" hint-placeholder-val="{{ %s }}">
<div style="margin-top: 40px; display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%%, 440px), 1fr)); gap: 20px">
<div style="background: linear-gradient(160deg,%s 0%%,#1D1D23 60%%); border: 1px solid #2A2A32; border-radius: 22px; padding: 38px">
<h3 style="margin: 0; font-size: 44px; line-height: 1.1; font-weight: 800; letter-spacing: 0.16em">%s</h3>
<p style="margin: 6px 0 0; font-size: 14px; color: #A9A9B3">%s</p>
<p style="margin: 26px 0 0; font-size: 17px; line-height: 1.7; color: #D6D6DC">%s</p>
<p style="margin: 20px 0 0; font-size: 14px; color: #A9A9B3"><span style="color: #F4F4F6; font-weight: 600">Best for:</span> %s</p>
</div>
<div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px">
%s</div>
</div>
</sc-if>
'''%(flag,first,tint,name,sub,body,best,it)
panels=panel('isSirca','true','#24201D','SIRCA','Sirca S.p.A. · Italy',"Classic Italian polyurethane, built for interiors that see daily use. Sirca's 2K PU sealers and topcoats give a dense, even film with excellent clarity. It is our go-to for kitchens and wardrobes that need to look new for a long time.",'kitchen shutters, wardrobes, TV units, doors',[('2K PU Sealers','Fill and level the grain for a flawless base.'),('PU Topcoats','Clear and pigmented, glossy through matt.'),('Acrylic PU','Non-yellowing, for whites and pale woods.'),('Polyester','High-build for mirror and piano gloss.'),('Stains','Walnut, teak, wenge and custom tones.'),('Special Effects','Metallic, pearl and textured finishes.')])
panels+=panel('isIca','false','#211D26','ICA','ICA Group · Civitanova Marche, Italy · since 1971',"A pioneer of water-based wood coatings since 1983. ICA brings us ultra-matt protection, antique effects and eco-friendly finishes that do not compromise on hardness.",'luxury veneers, low-odour homes, exterior wood, effect finishes',[('Finezza PU','Premium polyurethane for interior wood.'),('Finezza Acrylic','Crystal-clear, non-yellowing protection.'),('Acquabella','Water-based, low-odour, eco-friendly.'),('Antique Armonie','Aged, hand-worn decorative effects.'),('Polyester &amp; Gloss','Pigmented and clear high-gloss systems.'),('Exterior Wood','UV, water and anti-yellowing protection.')])
panels+=panel('isAxalta','false','#1F2329','AXALTA','Axalta Coating Systems · global coatings company',"One of the world's major coatings makers, known for automotive-grade colour and tough industrial finishes. Its wood systems come in both waterborne and solvent-based technology. We use them when a project needs exact colour, deep gloss and a hard-wearing film.",'solid-colour shutters, high-gloss fronts, metallic shades, commercial interiors',[('PU Primers &amp; Sealers','A level, well-bonded base for colour.'),('PU Topcoats','Pigmented and clear, matt through gloss.'),('Waterborne Systems','Low-emission, built to match solvent durability.'),('Solvent-based Clears','Strong flow, levelling and clarity.'),('Stains &amp; Glazes','Colour and depth for natural wood.'),('Colour Matching','Precise shades, repeatable batch to batch.')])

CAP='position: absolute; inset: auto 0 0 0; padding: 70px 22px 22px; background: linear-gradient(0deg,rgba(10,10,12,0.92),rgba(10,10,12,0))'
TILE='position: relative; border-radius: 18px; overflow: hidden; aspect-ratio: 1 / 1; border: 1px solid #2A2A32'
def cap(a,b): return '<div style="%s"><p style="margin: 0; font-weight: 600; font-size: 19px">%s</p><p style="margin: 4px 0 0; font-size: 14px; color: #C9C9D1">%s</p></div>'%(CAP,a,b)
tiles='<div class="ss-tile" style="%s"><img class="ss-img" src="/_blob/029ef0b2348f9cc381a7ab24a818acdb" width="1200" height="782" alt="Obsidian matte textured surface" style="width: 100%%; height: 100%%; object-fit: cover; display: block; filter: brightness(1.350)">%s</div>\n'%(TILE,cap('Obsidian Matte','Dead-flat PU · 5 gloss'))
tiles+='<div class="ss-tile" style="%s"><img class="ss-img" src="/_blob/61fb86cb385f3b9847f456021b504df7" width="1200" height="778" alt="Liquid copper metallic finish being sprayed" style="width: 100%%; height: 100%%; object-fit: cover; object-position: 30%% 50%%; display: block">%s</div>\n'%(TILE,cap('Liquid Copper','Reactive metallic effect'))
tiles+='<div class="ss-tile" style="%s; background: radial-gradient(120%% 80%% at 30%% 15%%, #4A4A55 0%%, #18181D 38%%, #050506 100%%)"><div class="ss-img" aria-hidden="true" style="position: absolute; inset: 0; background: linear-gradient(115deg, rgba(255,255,255,0) 35%%, rgba(255,255,255,0.16) 45%%, rgba(255,255,255,0) 55%%)"></div>%s</div>\n'%(TILE,cap('Piano Black','Polyester mirror gloss'))
tiles+='<div class="ss-tile" style="%s; background: linear-gradient(160deg,#8C6A45 0%%,#5B4129 55%%,#2E2014 100%%)"><div class="ss-img" aria-hidden="true" style="position: absolute; inset: 0; background: repeating-linear-gradient(92deg, rgba(255,255,255,0.07) 0px, rgba(255,255,255,0) 2px, rgba(0,0,0,0.08) 4px, rgba(0,0,0,0) 7px)"></div>%s</div>\n'%(TILE,cap('Brushed Bronze','Directional metallic'))
tiles+='<div class="ss-tile" style="%s; background: linear-gradient(150deg,#F4F1EA 0%%,#DDD8CE 60%%,#C4BEB2 100%%)"><div class="ss-img" aria-hidden="true" style="position: absolute; inset: 0; background: linear-gradient(120deg, rgba(255,255,255,0) 30%%, rgba(255,255,255,0.75) 44%%, rgba(255,255,255,0) 58%%)"></div>%s</div>\n'%(TILE,cap('Pearl Ivory','Non-yellowing acrylic PU'))
tiles+='<div class="ss-tile" style="%s; background: linear-gradient(160deg,#6B4A2F 0%%,#4A3220 50%%,#2F1F13 100%%)"><div class="ss-img" aria-hidden="true" style="position: absolute; inset: 0; background: repeating-linear-gradient(178deg, rgba(0,0,0,0.16) 0px, rgba(0,0,0,0) 3px, rgba(255,255,255,0.04) 9px, rgba(0,0,0,0) 17px)"></div>%s</div>\n'%(TILE,cap('Natural Walnut','Open-pore clear PU polish'))
sheen=[('Dead Matt','~5 gloss','#2B2B31',0),('Matt','~10–20 gloss','linear-gradient(135deg,#2B2B31 60%,#34343B)',0),('Satin','~30–40 gloss','linear-gradient(135deg,#2B2B31 45%,#3E3E46 60%,#2B2B31 75%)',0),('Semi Gloss','~60 gloss','linear-gradient(135deg,#25252A 40%,#55555F 55%,#25252A 68%)',0),('High Gloss','90+ gloss','linear-gradient(135deg,#1A1A1E 42%,#8A8A96 52%,#1A1A1E 60%)',0),('Mirror','Polyester, buffed','linear-gradient(135deg,#0B0B0D 44%,#E6E6EE 50%,#0B0B0D 56%)',1)]
sh=''.join('<div style="border-radius: 14px; border: 1px solid %s; overflow: hidden"><div style="height: 64px; background: %s"></div><div style="padding: 12px 16px; background: #1D1D23"><p style="margin: 0; font-weight: 600; font-size: 15px">%s</p><p style="margin: 4px 0 0; font-size: 13px; color: #A9A9B3">%s</p></div></div>\n'%('#FF8A1F' if hl else '#2A2A32',bg,a,b) for a,b,bg,hl in sheen)
steps=[('Surface Preparation','Panels inspected, edges checked, sanded and de-dusted for clean adhesion.'),('Sealer &amp; Primer','High-build sealer coats, sanded between layers until the base is level.'),('Precision Coating','Shade-matched topcoat, sprayed in a dust-managed space.'),('Controlled Curing','Full cure time respected, so the film reaches its rated hardness.'),('Final Perfection','Polished, inspected under light, wrapped and dispatched by batch.')]
st=''.join('<li style="position: relative; border-top: 2px solid #2A2A32; padding: 26px 24px 0 0"><span aria-hidden="true" style="position: absolute; top: -8px; left: 0; width: 14px; height: 14px; border-radius: 50%%; background: linear-gradient(135deg,#FF8A1F,#B44CE6)"></span><p style="margin: 0; font-size: 13px; font-weight: 700; letter-spacing: 0.12em; color: #FF9A3C">STEP %02d</p><h3 style="margin: 8px 0 8px; font-size: 18px; font-weight: 600">%s</h3><p style="margin: 0; font-size: 14px; line-height: 1.6; color: #A9A9B3">%s</p></li>\n'%(i+1,a,b) for i,(a,b) in enumerate(steps))
faqs=[('What is the difference between PU paint and PU polish?','PU paint is pigmented: it covers the surface in a solid colour, used on MDF and HDHMR shutters. PU polish is clear: it protects veneer or solid wood while keeping the natural grain visible. Both are available from dead matt to high gloss.'),
('How much does PU polish cost per sq ft in Hyderabad?','Pricing depends on the coating system, sheen level and whether one or both sides are finished. We quote per sq ft after seeing your drawings or cutlist, so send them over for an exact price.'),
('Sirca, ICA or Axalta: which is better for my kitchen?','All three suit kitchens. We usually choose Sirca 2K PU for hard-wearing kitchen and wardrobe shutters, ICA for water-based low-odour finishes, ultra-matt looks and antique effects, and Axalta when exact colour and deep gloss matter most. We recommend a system after seeing your material and design.'),
('Is PU better than Duco or melamine polish?','For most interiors, yes. PU is more durable, keeps its gloss longer and is more flexible, so it is less likely to yellow, fade or crack than Duco or melamine. It costs more, and it needs skilled spray application in a dust-controlled space.'),
('Is PU suitable for kitchens and bathroom vanities?','Yes. PU is highly resistant to moisture and stains, so it suits kitchen shutters and vanity units, ideally on HDHMR board with sealed edges. It is not meant for surfaces that sit in standing water.'),
('Will a white PU finish turn yellow?','Standard PU can yellow slightly over time. For whites and pale woods we use non-yellowing acrylic PU systems, such as Sirca Acrylic PU or ICA Finezza Acrylic.'),
('Are water-based finishes as strong as solvent-based PU?',"Two-component water-based coatings are designed to match solvent-based coatings in hardness and chemical resistance, with far lower VOCs and odour. They are a good choice for occupied homes."),
('Can you match an existing shade?','Yes. Give us a RAL or NCS code, a laminate or a physical sample, and we will match it and share a sample panel for approval before production.'),
('Do you finish panels for modular kitchen factories?','Yes. Share your factory panel list or cutlist. Every panel is tracked by its barcode, finished as specified and returned in batches matched to your project.'),
('Can PU be applied over laminate?','Yes, once the laminate is properly prepared with a specialised adhesion primer. Any peeling or swollen laminate has to be repaired first.'),
('Can old teak doors be re-polished with PU?','Yes. The old polish is sanded back, holes and cracks are filled, two coats of PU sealer go on, and the door is finished with a clear matt or gloss topcoat. Old teak often shows a richer grain afterwards.'),
('How long does a PU finishing job take?','It depends on the batch size, the finish and the number of coats, and it always includes full curing time. We confirm a delivery date with your quote, and larger projects are delivered in planned batches.')]
fq=''.join('<details class="ss-faq" style="border-bottom: 1px solid #2A2A32"><summary style="display: flex; justify-content: space-between; align-items: center; gap: 20px; padding: 22px 0; min-height: 44px; cursor: pointer; font-size: 18px; font-weight: 600; line-height: 1.4">%s</summary><p style="margin: 0; padding: 0 40px 24px 0; font-size: 15px; line-height: 1.7; color: #A9A9B3">%s</p></details>\n'%(H.escape(q,quote=False),H.escape(a,quote=False)) for q,a in faqs)
areas=['Bollaram','Miyapur','Bachupally','Ameenpur','Kukatpally','Kondapur','Gachibowli','Madhapur','Jubilee Hills','Banjara Hills','Kokapet','Financial District','Manikonda','Secunderabad','Shamshabad']
INP='width: 100%; box-sizing: border-box; min-height: 48px; padding: 12px 14px; border-radius: 12px; border: 1px solid #3A3A44; background: #121216; color: #F4F4F6; font-family: Outfit, system-ui, sans-serif; font-size: 15px'
LBL='display: block; margin: 0 0 8px; font-size: 13px; font-weight: 500; color: #C9C9D1'
navlinks='<a href="#services">Services</a>\n<a href="#pu-guide">PU Guide</a>\n<a href="#brands">Brands</a>\n<a href="#finishes">Finishes</a>\n<a href="#process">Process</a>\n<a href="#faq">FAQ</a>'

page='''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Surface Studio — PU Paint &amp; Polish, Hyderabad</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&amp;display=swap" rel="stylesheet">
<style>
body{margin:0;background:#121216}
a{color:#F4F4F6;text-decoration:none}a:hover{color:#FF9A3C}
.ss-img{transition:transform .6s ease}
[id]{scroll-margin-top:84px}
a:focus-visible,button:focus-visible,summary:focus-visible,[tabindex]:focus-visible{outline:2px solid #FF8A1F;outline-offset:3px;border-radius:6px}
select{color-scheme:dark}
select option{background:#1D1D23;color:#F4F4F6}
.ss-foot a{display:inline-flex;align-items:center;min-height:44px}
.ss-foot a:hover{color:#FF9A3C !important}
.ss-inl{display:inline-block;padding:12px 0;margin:-12px 0}
.ss-tile:hover .ss-img{transform:scale(1.06)}
.ss-cursor{animation:ssblink 1s steps(1) infinite}
.ss-cursor::after{content:"|"}
@keyframes ssblink{50%{opacity:0}}
.ss-nav-links{display:flex}
.ss-nav-links a{display:inline-flex;align-items:center;min-height:44px}
.ss-mob{display:none;position:relative}
.ss-mob summary{list-style:none}
.ss-mob summary::-webkit-details-marker{display:none}
.ss-faq summary{list-style:none}
.ss-faq summary::-webkit-details-marker{display:none}
.ss-faq summary::after{content:"+";font-size:26px;font-weight:300;color:#FF9A3C;flex:none}
.ss-faq[open] summary::after{content:"\\2212"}
.ss-faq summary:hover{color:#FF9A3C}
input::placeholder,textarea::placeholder{color:#8E8E99}
input:focus,select:focus,textarea:focus{outline:2px solid #FF8A1F;outline-offset:1px}
@media (max-width:900px){.ss-nav-links{display:none}.ss-mob{display:block}.ss-quote{display:none !important}}
@media (max-width:600px){.ss-h1{min-height:3.1em !important}.ss-strip{gap:12px 32px !important}.ss-strip-label{flex-basis:100%;text-align:center}}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none !important;transition:none !important;scroll-behavior:auto !important}.ss-tile:hover .ss-img{transform:none}}
</style>
</helmet>
<div style="font-family: 'Outfit', system-ui, sans-serif; color: #F4F4F6; background: #121216; width: 100%; overflow-x: clip">

<!-- NAV -->
<header style="position: sticky; top: 0; z-index: 20; background: rgba(18,18,22,0.86); backdrop-filter: blur(14px); border-bottom: 1px solid #24242B">
<div style="max-width: 1200px; margin: 0 auto; padding: 16px 24px; display: flex; align-items: center; justify-content: space-between; gap: 24px">
<a href="#top" aria-label="Surface Studio home" style="display: flex; flex-direction: column; justify-content: center; min-height: 44px; line-height: 0.95; font-weight: 800; font-size: 17px; letter-spacing: 0.04em">$LOGO</a>
<nav class="ss-nav-links" aria-label="Main" style="gap: 30px; font-size: 14px; font-weight: 500; align-items: center">
$NAV
</nav>
<div style="display: flex; align-items: center; gap: 10px">
<a class="ss-quote" href="tel:+919505969558" style="font-size: 14px; font-weight: 500; color: #C9C9D1; padding: 0 6px; min-height: 44px; display: inline-flex; align-items: center">+91 95059 69558</a>
<a href="#contact" style="font-size: 14px; font-weight: 600; padding: 0 20px; border-radius: 999px; color: #FFFFFF; background: $BTN; min-height: 44px; box-sizing: border-box; display: inline-flex; align-items: center">Get a Quote</a>
<details class="ss-mob">
<summary aria-label="Open menu" style="width: 44px; height: 44px; border-radius: 12px; border: 1px solid #3A3A44; display: flex; align-items: center; justify-content: center; cursor: pointer"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"></path></svg></summary>
<nav aria-label="Mobile" style="position: absolute; right: 0; top: 54px; width: 220px; padding: 12px 20px; border-radius: 16px; background: #1D1D23; border: 1px solid #2A2A32; display: flex; flex-direction: column; gap: 4px; font-size: 16px; font-weight: 500; line-height: 2.750">
$NAV
<a href="#contact">Contact &amp; location</a>
</nav>
</details>
</div>
</div>
</header>

<!-- HERO -->
<section id="top" style="position: relative; min-height: 660px; display: flex; align-items: center">
<img src="/_blob/61fb86cb385f3b9847f456021b504df7" width="1200" height="778" alt="Craftsman spray-coating a panel with a metallic copper finish" style="position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: 70% 40%">
<div aria-hidden="true" style="position: absolute; inset: 0; background: linear-gradient(90deg, rgba(18,18,22,0.96) 0%, rgba(18,18,22,0.84) 42%, rgba(18,18,22,0.35) 100%)"></div>
<div aria-hidden="true" style="position: absolute; left: 0; right: 0; bottom: 0; height: 160px; background: linear-gradient(0deg,#121216,rgba(18,18,22,0))"></div>
<div style="position: relative; max-width: 1200px; width: 100%; margin: 0 auto; padding: 96px 24px 110px; box-sizing: border-box">
<p style="margin: 0 0 22px; font-size: 13px; font-weight: 600; letter-spacing: 0.16em; text-transform: uppercase; color: #FF9A3C">PU paint &amp; polish studio&nbsp;·&nbsp;Hyderabad</p>
<h1 class="ss-h1" style="margin: 0; font-size: clamp(42px, 7vw, 84px); line-height: 1.02; font-weight: 700; letter-spacing: -0.02em; min-height: 2.050em">We Create <br><span style="$G">{{typed}}</span><span class="ss-cursor" aria-hidden="true" style="color: #B44CE6; font-weight: 300"></span></h1>
<p style="margin: 22px 0 0; max-width: 540px; font-size: 19px; line-height: 1.55; color: #C9C9D1; font-weight: 300">We finish kitchens, wardrobes, doors and furniture in PU, using Sirca, ICA and Axalta coatings. Dead matt to mirror gloss, shade-matched to your sample.</p>
<div style="margin-top: 36px; display: flex; flex-wrap: wrap; gap: 14px; align-items: center">
<a href="#contact" style="display: inline-flex; align-items: center; min-height: 50px; padding: 0 30px; border-radius: 999px; font-weight: 600; font-size: 16px; color: #FFFFFF; background: $BTN">Get a Quote</a>
<a href="https://wa.me/919505969558"$EXT style="display: inline-flex; align-items: center; gap: 10px; min-height: 50px; padding: 0 24px; border-radius: 999px; border: 1px solid #55555F; background: rgba(18,18,22,0.5); font-weight: 600; font-size: 16px">$WA WhatsApp us</a>
<a href="#finishes" style="display: inline-flex; align-items: center; gap: 8px; min-height: 50px; padding: 0 12px; font-weight: 600; font-size: 16px">See finishes <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"></path></svg></a>
</div>
<ul style="margin: 56px 0 0; padding: 0; list-style: none; display: flex; flex-wrap: wrap; gap: 12px 36px; font-size: 14px; color: #D6D6DC">
<li style="display: flex; align-items: center; gap: 10px"><span style="width: 7px; height: 7px; border-radius: 50%; background: #FF8A1F"></span>Studio in IDA Bollaram</li>
<li style="display: flex; align-items: center; gap: 10px"><span style="width: 7px; height: 7px; border-radius: 50%; background: #E8565E"></span>Open Mon – Sat, 9:30 am – 5:30 pm</li>
<li style="display: flex; align-items: center; gap: 10px"><span style="width: 7px; height: 7px; border-radius: 50%; background: #B44CE6"></span>Sample panel before production</li>
</ul>
</div>
</section>

<!-- BRAND STRIP -->
<section aria-label="Coating brands we use" style="border-top: 1px solid #24242B; border-bottom: 1px solid #24242B; background: #16161B">
<div style="max-width: 1200px; margin: 0 auto; padding: 24px; box-sizing: border-box; display: flex; flex-wrap: wrap; align-items: center; justify-content: center; gap: 14px 56px" class="ss-strip">
<span class="ss-strip-label" style="letter-spacing: 0.14em; text-transform: uppercase; font-size: 12px; color: #A9A9B3">We finish with</span>
<span style="font-size: 24px; font-weight: 800; letter-spacing: 0.18em">SIRCA</span>
<span style="font-size: 24px; font-weight: 800; letter-spacing: 0.18em">ICA</span>
<span style="font-size: 24px; font-weight: 800; letter-spacing: 0.18em">AXALTA</span>
</div>
</section>

<!-- ABOUT -->
<section id="about" style="$WRAP; display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 420px), 1fr)); gap: 56px; align-items: center">
<div>
<h2 style="margin: 0; font-size: clamp(36px, 4.6vw, 56px); line-height: 1.05; font-weight: 700; letter-spacing: -0.02em">Every surface <br><span style="$G">tells a story.</span></h2>
<p style="margin: 24px 0 0; font-size: 19px; line-height: 1.6; color: #D6D6DC">Surface Studio is a finishing studio dedicated to one thing: surfaces that look and feel exceptional for years.</p>
<p style="margin: 16px 0 0; font-size: 16px; line-height: 1.7; color: #A9A9B3">We match the coating system to the job: a dead-matt kitchen shutter, a mirror-gloss wardrobe, or an open-grain veneer that should look like nothing was applied at all. You send us panels. We send back finished pieces, ready to install.</p>
<ul style="margin: 30px 0 0; padding: 0; list-style: none; display: flex; flex-direction: column; gap: 14px; font-size: 16px; font-weight: 500">
$CHECKS
</ul>
</div>
<div style="position: relative; border-radius: 22px; overflow: hidden; border: 1px solid #2A2A32; aspect-ratio: 5 / 4">
<img src="/_blob/fec8263e01c0ca67dcfbe2ea8e3478b8" width="1094" height="1091" alt="Close-up of a deep-textured charcoal finish" style="width: 100%; height: 100%; object-fit: cover; display: block">
<div style="position: absolute; left: 20px; bottom: 20px; padding: 12px 18px; border-radius: 12px; background: rgba(18,18,22,0.78); backdrop-filter: blur(8px); font-weight: 600; font-size: 15px">Engineered perfection</div>
</div>
</section>

<!-- SERVICES -->
<section id="services" style="background: #17171C; border-top: 1px solid #24242B; border-bottom: 1px solid #24242B">
<div style="$WRAP; display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 340px), 1fr)); gap: 40px 72px; align-items: start">
<div>
<p style="$EYE">What we do</p>
<h2 style="$H2">Finishing expertise</h2>
<p style="margin: 18px 0 0; font-size: 17px; color: #A9A9B3; line-height: 1.6; max-width: 380px">Six services, one standard. Sprayed by hand, sanded between coats and cured with patience.</p>
<a href="#contact" style="margin-top: 28px; display: inline-flex; align-items: center; min-height: 48px; padding: 0 24px; border-radius: 999px; border: 1px solid #3A3A44; font-weight: 600; font-size: 15px">Ask for a quote</a>
</div>
<div style="border-bottom: 1px solid #2A2A32">
$SVC</div>
</div>
</section>

<!-- CLIENTS -->
<section aria-label="Who we work with" style="$WRAP">
<p style="$EYE">Who we work with</p>
<h2 style="$H2">Built around how you work</h2>
<div style="margin-top: 40px; display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 300px), 1fr)); gap: 18px">
$CLI</div>
</section>

<!-- PU GUIDE -->
<section id="pu-guide" style="background: #17171C; border-top: 1px solid #24242B; border-bottom: 1px solid #24242B">
<div style="$WRAP">
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 420px), 1fr)); gap: 40px; align-items: start">
<div>
<p style="$EYE">PU, explained</p>
<h2 style="$H2">What is a PU finish?</h2>
<p style="margin: 22px 0 0; font-size: 18px; line-height: 1.65; color: #D6D6DC">PU is short for polyurethane: a two-component coating, mixed with a hardener and sprayed in thin layers, that cures into a tough, smooth film in matt or gloss.</p>
<p style="margin: 14px 0 0; font-size: 16px; line-height: 1.7; color: #A9A9B3">That film resists scratches, stains and moisture far better than traditional polishes, which is why PU has become the standard for premium kitchens, wardrobes and doors. Pigmented, it is PU paint. Clear, over wood or veneer, it is PU polish.</p>
</div>
<div style="background: #1D1D23; border: 1px solid #2A2A32; border-radius: 22px; padding: 30px">
<p style="margin: 0 0 16px; font-weight: 600; font-size: 17px">Surfaces PU can be applied to</p>
<div style="display: flex; flex-wrap: wrap; gap: 10px">
$SUBS
</div>
<p style="margin: 20px 0 0; font-size: 14px; line-height: 1.65; color: #A9A9B3">For kitchens and humid areas we recommend HDHMR over standard MDF, with every face and edge sealed so moisture cannot get in.</p>
</div>
</div>
<div style="margin-top: 56px; display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 420px), 1fr)); gap: 20px">
$AN</div>
<div style="margin-top: 56px">
<h3 style="margin: 0 0 6px; font-size: clamp(24px, 3vw, 32px); font-weight: 700; letter-spacing: -0.01em">PU vs Duco vs Melamine</h3>
<p style="margin: 0 0 22px; font-size: 16px; color: #A9A9B3">How the three common wood finishes compare.</p>
<div style="overflow-x: auto; border: 1px solid #2A2A32; border-radius: 18px; background: #1D1D23">
<table style="width: 100%; min-width: 640px; border-collapse: collapse; font-size: 15px; text-align: left">
<thead><tr><th scope="col" style="$TD"></th><th scope="col" style="$TD; font-weight: 700; color: #FF9A3C; background: #24211F">PU</th><th scope="col" style="$TD; font-weight: 600">Duco</th><th scope="col" style="$TD; font-weight: 600">Melamine</th></tr></thead>
<tbody>
$TB</tbody>
</table>
</div>
</div>
<div style="margin-top: 40px; display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 300px), 1fr)); gap: 32px">
<div><h3 style="margin: 0 0 8px; font-size: 19px; font-weight: 600">Water-based PU</h3><p style="margin: 0; font-size: 15px; line-height: 1.65; color: #A9A9B3">Low VOCs, minimal odour and faster drying. The better choice for occupied homes, bedrooms and anyone sensitive to solvents.</p></div>
<div><h3 style="margin: 0 0 8px; font-size: 19px; font-weight: 600">Solvent-based PU</h3><p style="margin: 0; font-size: 15px; line-height: 1.65; color: #A9A9B3">Stronger odour and a longer cure, in exchange for the toughest film. The choice for heavy-use surfaces such as kitchen shutters.</p></div>
<div><h3 style="margin: 0 0 8px; font-size: 19px; font-weight: 600">Caring for a PU finish</h3><p style="margin: 0; font-size: 15px; line-height: 1.65; color: #A9A9B3">Wipe with a soft microfibre cloth and mild soap. Avoid harsh chemicals, abrasive pads and standing water, and let the finish cure fully before heavy use.</p></div>
</div>
</div>
</section>

<!-- BRANDS -->
<section id="brands" style="$WRAP">
<div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: flex-end; gap: 24px">
<div style="max-width: 620px">
<p style="$EYE">Our coating partners</p>
<h2 style="$H2">Three coating houses. <br>One studio.</h2>
</div>
<div role="tablist" aria-label="Coating brand" style="display: flex; flex-wrap: wrap; gap: 6px; padding: 6px; border-radius: 999px; background: #1D1D23; border: 1px solid #2A2A32">
$TABS</div>
</div>

$PANELS</section>

<!-- SIGNATURE FINISHES -->
<section id="finishes" style="background: #17171C; border-top: 1px solid #24242B; border-bottom: 1px solid #24242B">
<div style="$WRAP">
<p style="$EYE">Finish library</p>
<h2 style="$H2">Signature finishes</h2>
<p style="margin: 14px 0 0; font-size: 17px; color: #A9A9B3">A few favourites. Any of them can be sampled on your own board.</p>
<div style="margin-top: 44px; display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 300px), 1fr)); gap: 18px">
$TILES</div>
<div style="margin-top: 56px">
<p style="margin: 0 0 16px; font-size: 13px; letter-spacing: 0.16em; text-transform: uppercase; color: #A9A9B3; font-weight: 600">Choose your sheen</p>
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 150px), 1fr)); gap: 12px">
$SHEEN</div>
</div>
<div style="margin-top: 44px">
<p style="margin: 0 0 16px; font-size: 13px; letter-spacing: 0.16em; text-transform: uppercase; color: #A9A9B3; font-weight: 600">PU effects, on request</p>
<div style="display: flex; flex-wrap: wrap; gap: 10px">
$EFFECTS
</div>
</div>
</div>
</section>

<!-- PROCESS -->
<section id="process" style="$WRAP">
<p style="$EYE">How we work</p>
<h2 style="$H2">The precision workflow</h2>
<p style="margin: 14px 0 0; font-size: 17px; color: #A9A9B3">Five stages. No shortcuts between them.</p>
<ol style="margin: 56px 0 0; padding: 0; list-style: none; display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 190px), 1fr)); gap: 32px 0">
$STEPS</ol>
</section>

<!-- FAQ -->
<section id="faq" style="background: #17171C; border-top: 1px solid #24242B; border-bottom: 1px solid #24242B">
<div style="$WRAP; display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 340px), 1fr)); gap: 40px 72px; align-items: start">
<div>
<p style="$EYE">FAQ</p>
<h2 style="$H2">Questions, answered</h2>
<p style="margin: 18px 0 0; font-size: 17px; color: #A9A9B3; line-height: 1.6; max-width: 380px">What clients in Hyderabad ask us most about PU finishes. Something else on your mind?</p>
<a href="https://wa.me/919505969558"$EXT style="margin-top: 26px; display: inline-flex; align-items: center; gap: 10px; min-height: 48px; padding: 0 24px; border-radius: 999px; border: 1px solid #3A3A44; font-weight: 600; font-size: 15px">$WA Ask on WhatsApp</a>
</div>
<div style="border-top: 1px solid #2A2A32">
$FAQ</div>
</div>
</section>

<!-- CTA -->
<section id="contact" style="$WRAP">
<div style="max-width: 720px">
<h2 style="margin: 0; font-size: clamp(36px, 4.6vw, 56px); line-height: 1.05; font-weight: 700; letter-spacing: -0.02em">Let's create something <span style="$G">remarkable.</span></h2>
<p style="margin: 18px 0 0; font-size: 18px; line-height: 1.6; color: #A9A9B3">Tell us what you are finishing. We will recommend the right Sirca, ICA or Axalta system and send a quote.</p>
</div>
<div style="margin-top: 48px; display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 420px), 1fr)); gap: 20px; align-items: stretch">

<form onSubmit="{{send}}" style="position: relative; overflow: hidden; border-radius: 24px; border: 1px solid #2A2A32; background: #1D1D23; padding: clamp(24px, 3.4vw, 40px); display: flex; flex-direction: column; gap: 18px">
<div aria-hidden="true" style="position: absolute; right: -140px; top: -180px; width: 420px; height: 420px; border-radius: 50%; background: radial-gradient(circle, rgba(255,138,31,0.20), rgba(180,76,230,0.09) 45%, rgba(29,29,35,0) 70%)"></div>
<h3 style="position: relative; margin: 0; font-size: 24px; font-weight: 700">Request a quote</h3>
<div style="position: relative; display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 180px), 1fr)); gap: 16px">
<div><label for="q-name" style="$LBL">Your name</label><input id="q-name" name="name" type="text" required maxlength="80" autocomplete="name" placeholder="Full name" style="$INP"></div>
<div><label for="q-phone" style="$LBL">Phone</label><input id="q-phone" name="phone" type="tel" required maxlength="20" inputmode="tel" pattern="[0-9+\\-\\(\\) ]{8,20}" title="Phone number: 8 to 20 digits; spaces, +, - and brackets allowed" autocomplete="tel" placeholder="Mobile number" style="$INP"></div>
</div>
<div style="position: relative"><label for="q-need" style="$LBL">What do you need?</label><select id="q-need" name="need" style="$INP"><option>PU Paint (solid colour)</option><option>PU Polish (clear, on wood or veneer)</option><option>Polyester high gloss</option><option>Metallic or special effect</option><option>Modular panel finishing</option><option>Not sure yet</option></select></div>
<div style="position: relative"><label for="q-msg" style="$LBL">Project details</label><textarea id="q-msg" name="msg" rows="4" maxlength="1000" placeholder="Approx. sq ft, material, shade or reference, timeline" style="$INP; resize: vertical; line-height: 1.5"></textarea></div>
<button type="submit" style="position: relative; min-height: 52px; border: 0; border-radius: 999px; font-family: Outfit, system-ui, sans-serif; font-weight: 600; font-size: 16px; color: #FFFFFF; cursor: pointer; background: $BTN">Send on WhatsApp</button>
<p style="position: relative; margin: 0; font-size: 13px; color: #A9A9B3">Opens WhatsApp with your details filled in. Or email <a class="ss-inl" href="mailto:sales@surfacestudio.in" style="text-decoration: underline">sales@surfacestudio.in</a>.</p>
</form>

<div id="visit" style="border-radius: 24px; border: 1px solid #2A2A32; background: #1D1D23; overflow: hidden; display: flex; flex-direction: column">
<!-- MAP-START -->
<a href="$MAPS"$EXT aria-label="Open Surface Studio location in Google Maps" style="position: relative; min-height: 240px; flex: 1 1 240px; display: flex; align-items: center; justify-content: center; background-color: #17171C; background-image: linear-gradient(#24242B 1px, rgba(0,0,0,0) 1px), linear-gradient(90deg, #24242B 1px, rgba(0,0,0,0) 1px); background-size: 44px 44px">
<span style="display: flex; flex-direction: column; align-items: center; gap: 10px; text-align: center; padding: 16px">
<span style="width: 54px; height: 54px; border-radius: 50%; background: linear-gradient(135deg,#FF8A1F,#B44CE6); display: inline-flex; align-items: center; justify-content: center; color: #FFFFFF">$PIN</span>
<span style="font-weight: 600; font-size: 16px; color: #F4F4F6">Surface Studio · IDA Bollaram</span>
<span style="font-size: 13px; color: #A9A9B3">The live Google Map appears here on the website</span>
</span>
</a>
<!-- MAP-END -->
<div style="padding: clamp(24px, 3vw, 34px)">
<h3 style="margin: 0; font-size: 24px; font-weight: 700">Visit the studio</h3>
<address style="margin: 14px 0 0; font-style: normal; font-size: 16px; line-height: 1.65; color: #D6D6DC">Bollaram Industrial Area (IDA Bollaram), Bollaram Village, Hyderabad, Telangana 502325</address>
<p style="margin: 6px 0 0; font-size: 14px; color: #A9A9B3">Plus Code G8XV+8C5 · Mon&nbsp;–&nbsp;Sat, 9:30&nbsp;am&nbsp;–&nbsp;5:30&nbsp;pm · Sunday&nbsp;closed</p>
<div style="margin-top: 22px; display: flex; flex-wrap: wrap; gap: 12px">
<a href="$MAPS"$EXT style="display: inline-flex; align-items: center; gap: 10px; min-height: 48px; padding: 0 22px; border-radius: 999px; border: 1px solid #3A3A44; font-weight: 600; font-size: 15px">$PIN Directions</a>
<a href="tel:+919505969558" style="display: inline-flex; align-items: center; min-height: 48px; padding: 0 22px; border-radius: 999px; border: 1px solid #3A3A44; font-weight: 600; font-size: 15px">Call +91 95059 69558</a>
</div>
<div style="margin-top: 18px; padding-top: 18px; border-top: 1px solid #2A2A32; display: flex; flex-wrap: wrap; gap: 4px 24px; font-size: 15px; font-weight: 600">
<a href="$MAPS"$EXT style="display: inline-flex; align-items: center; gap: 8px; min-height: 44px; color: #FF9A3C">$GPROF View our Google profile</a>
<a href="$REVIEW"$EXT style="display: inline-flex; align-items: center; gap: 8px; min-height: 44px; color: #FF9A3C">$STAR Review us on Google</a>
</div>
</div>
</div>
</div>

<!-- AREAS -->
<div style="margin-top: 48px">
<h3 style="margin: 0; font-size: 20px; font-weight: 600">PU paint &amp; polish across Hyderabad</h3>
<p style="margin: 10px 0 18px; font-size: 15px; line-height: 1.65; color: #A9A9B3; max-width: 760px">From our studio in IDA Bollaram we finish panels, doors and furniture for clients across Hyderabad and Secunderabad, including:</p>
<div style="display: flex; flex-wrap: wrap; gap: 8px">
$AREAS
</div>
</div>
</section>

<!-- FOOTER -->
<footer style="border-top: 1px solid #24242B; background: #0F0F12">
<div style="max-width: 1200px; margin: 0 auto; padding: 56px 24px 32px; box-sizing: border-box">
<div style="display: flex; flex-wrap: wrap; justify-content: space-between; gap: 40px">
<div style="max-width: 340px">
<div role="img" aria-label="Surface Studio" style="display: flex; flex-direction: column; line-height: 0.95; font-weight: 800; font-size: 17px; letter-spacing: 0.04em">$LOGO</div>
<p style="margin: 18px 0 0; font-size: 15px; line-height: 1.6; color: #A9A9B3">PU paint &amp; polish studio, Hyderabad. Finishes by Sirca, ICA and Axalta.</p>
<p style="margin: 14px 0 0; font-size: 14px; line-height: 1.6; color: #A9A9B3">Bollaram Industrial Area (IDA Bollaram), Hyderabad, Telangana 502325</p>
<p class="ss-foot" style="margin: 6px 0 0; font-size: 14px"><a href="mailto:sales@surfacestudio.in">sales@surfacestudio.in</a> · <a href="tel:+919505969558">+91 95059 69558</a></p>
</div>
<div class="ss-foot" style="display: flex; gap: 16px 56px; flex-wrap: wrap; font-size: 14px; line-height: 1.4">
<div><p style="margin: 0 0 6px; font-weight: 600; font-size: 15px">Studio</p><div style="display: flex; flex-direction: column"><a href="#about" style="color: #A9A9B3">About</a><a href="#services" style="color: #A9A9B3">Services</a><a href="#process" style="color: #A9A9B3">Process</a><a href="#faq" style="color: #A9A9B3">FAQ</a></div></div>
<div><p style="margin: 0 0 6px; font-weight: 600; font-size: 15px">Finishes</p><div style="display: flex; flex-direction: column"><a href="#pu-guide" style="color: #A9A9B3">PU guide</a><a href="#brands" style="color: #A9A9B3">Sirca · ICA · Axalta</a><a href="#finishes" style="color: #A9A9B3">Finish library</a></div></div>
<div><p style="margin: 0 0 6px; font-weight: 600; font-size: 15px">Connect</p><div style="display: flex; flex-direction: column"><a href="https://wa.me/919505969558"$EXT style="color: #A9A9B3">WhatsApp</a><a href="$MAPS"$EXT style="color: #A9A9B3">Google profile &amp; map</a><a href="$REVIEW"$EXT style="color: #A9A9B3">Review us on Google</a><a href="mailto:sales@surfacestudio.in" style="color: #A9A9B3">Email</a></div></div>
</div>
</div>
<div style="margin-top: 40px; padding-top: 22px; border-top: 1px solid #24242B; display: flex; flex-wrap: wrap; justify-content: space-between; gap: 12px; font-size: 13px; color: #8E8E99">
<span>© 2026 Surface Studio. All rights reserved.</span>
<span>Sirca, ICA and Axalta are trademarks of their respective owners.</span>
</div>
</div>
</footer>

</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{"$preview":{"width":1440,"height":7400}}'>
class Component extends DCLogic {
  constructor(props) {
    super(props);
    this.state = { brand: 'sirca', word: 0, chars: 17, deleting: false };
    this.words = ['Precision Coated.', 'Beyond Paint.', 'Flawless Finishes.', 'Engineered Surfaces.'];
  }
  componentDidMount() { var self = this; this.timer = setInterval(function () { self.tick(); }, 85); }
  componentWillUnmount() { clearInterval(this.timer); }
  tick() {
    var s = this.state, w = this.words[s.word];
    if (!s.deleting) {
      if (s.chars < w.length) { this.setState({ chars: s.chars + 1 }); }
      else { this.pause = (this.pause || 0) + 1; if (this.pause > 22) { this.pause = 0; this.setState({ deleting: true }); } }
    } else {
      if (s.chars > 0) { this.setState({ chars: s.chars - 1 }); }
      else { this.setState({ deleting: false, word: (s.word + 1) % this.words.length }); }
    }
  }
  renderVals() {
    var self = this;
    return {
      typed: this.words[this.state.word].slice(0, this.state.chars),
      isSirca: this.state.brand === 'sirca',
      isIca: this.state.brand === 'ica',
      isAxalta: this.state.brand === 'axalta',
      pickSirca: function () { self.setState({ brand: 'sirca' }); },
      pickIca: function () { self.setState({ brand: 'ica' }); },
      pickAxalta: function () { self.setState({ brand: 'axalta' }); },
      send: function (e) {
        e.preventDefault();
        var f = e.target.elements;
        var v = function (n) { return String(f.namedItem(n).value || '').trim(); };
        var t = 'Hi Surface Studio, I would like a quote.\\nName: ' + v('name') + '\\nPhone: ' + v('phone') + '\\nRequirement: ' + v('need') + '\\nDetails: ' + v('msg');
        window.open('https://wa.me/919505969558?text=' + encodeURIComponent(t), '_blank', 'noopener');
      }
    };
  }
}
</script>
</body>
</html>
'''
CHK='<span style="width: 22px; height: 22px; flex: none; border-radius: 50%; background: linear-gradient(135deg,#FF8A1F,#B44CE6); display: inline-flex; align-items: center; justify-content: center"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" aria-hidden="true"><path d="M5 12l5 5 9-10"></path></svg></span>'
checks='\n'.join('<li style="display: flex; align-items: center; gap: 12px">%s%s</li>'%(CHK,t) for t in ['Genuine branded coatings, never diluted','Every panel tracked from cutlist to dispatch','Shade matched to your sample, RAL or NCS'])
rep={'$NAV':navlinks,'$CHECKS':checks,'$SVC':svc,'$CLI':cli,'$SUBS':chips(['MDF','HDHMR','Solid wood','Veneer','Plywood','WPC','Laminate','Metal','Glass']),'$AN':an,'$TB':tb,'$TABS':tabs,'$PANELS':panels,'$TILES':tiles,'$SHEEN':sh,
'$EFFECTS':chips(['Metallic','Pearl','Liquid copper &amp; bronze','Corten','Marble','Crackle','Patina','Dual-tone'],'padding: 10px 18px; border-radius: 999px; background: #1D1D23; border: 1px solid #2A2A32; font-size: 14px; color: #D6D6DC'),
'$STEPS':st,'$FAQ':fq,'$AREAS':chips(areas,'padding: 8px 14px; border-radius: 999px; border: 1px solid #2A2A32; font-size: 13px; color: #C9C9D1'),
'$LOGO':LOGO,'$MAPS':MAPS,'$REVIEW':REVIEW,'$EXT':EXT,'$BTN':BTN,'$STAR':STAR,'$GPROF':GPROF,'$PIN':PIN,'$WA':WA,'$WRAP':WRAP,'$EYE':EYE,'$H2':H2,'$TD':'padding: 16px 22px; border-bottom: 1px solid #2A2A32','$LBL':LBL,'$INP':INP,'$G':G}
for k in sorted(rep,key=len,reverse=True): page=page.replace(k,rep[k])
import re
assert not re.findall(r'\$[A-Z]{2,}',page), set(re.findall(r'\$[A-Z0-9]+',page))
open('/home/claude/site/project/Main.dc.html','w').write(page)
# schema
url="https://surfacestudio.in/"; maps=H.unescape(MAPS)
g={"@context":"https://schema.org","@graph":[
 {"@type":"HomeAndConstructionBusiness","@id":url+"#business","name":"Surface Studio","url":url,
  "description":"PU paint and polish studio in IDA Bollaram, Hyderabad, finishing kitchens, wardrobes, doors and furniture with Sirca, ICA and Axalta wood coatings.",
  "image":url+"images/copper-metallic-pu-finish-hyderabad.jpg","email":"sales@surfacestudio.in","telephone":"+919505969558","priceRange":"₹₹",
  "address":{"@type":"PostalAddress","streetAddress":"Bollaram Industrial Area (IDA Bollaram), Bollaram Village","addressLocality":"Hyderabad","addressRegion":"Telangana","postalCode":"502325","addressCountry":"IN"},
  "geo":{"@type":"GeoCoordinates","latitude":17.5484382,"longitude":78.343641},"hasMap":maps,
  "areaServed":[{"@type":"City","name":"Hyderabad"}]+[{"@type":"Place","name":a+", Hyderabad"} for a in areas],
  "openingHoursSpecification":[{"@type":"OpeningHoursSpecification","dayOfWeek":["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],"opens":"09:30","closes":"17:30"}],
  "brand":[{"@type":"Brand","name":n} for n in ["Sirca","ICA","Axalta"]],
  "knowsAbout":["PU paint","PU polish","polyurethane wood coatings","Sirca wood coatings","ICA wood coatings","Axalta wood coatings","water-based wood finishes","polyester high gloss","modular kitchen shutter finishing"],
  "makesOffer":[{"@type":"Offer","itemOffered":{"@type":"Service","name":H.unescape(s[0]),"description":H.unescape(s[1]),"areaServed":"Hyderabad"}} for s in services],
  "contactPoint":{"@type":"ContactPoint","telephone":"+919505969558","contactType":"sales","availableLanguage":["English","Hindi","Telugu"]},
  "sameAs":[maps]},
 {"@type":"WebSite","@id":url+"#website","url":url,"name":"Surface Studio","inLanguage":"en-IN","publisher":{"@id":url+"#business"}},
 {"@type":"FAQPage","@id":url+"#faq","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs]}]}
open('head_filled.html','w').write(open('head.html').read().replace('__JSONLD__',json.dumps(g,ensure_ascii=False,indent=1)))
print(len(page))
