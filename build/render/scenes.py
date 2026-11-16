# Renders accurate PU-finish illustrations (smooth sprayed panels, correct sheen) as JPGs via Chrome.
import sys
from playwright.sync_api import sync_playwright
WOOD=lambda seed,bf,col_lo,col_hi,warp: f'''
<filter id="w{seed}" x="-10%" y="-10%" width="120%" height="120%" color-interpolation-filters="sRGB">
 <feTurbulence type="fractalNoise" baseFrequency="{bf}" numOctaves="4" seed="{seed}" result="n"/>
 <feTurbulence type="fractalNoise" baseFrequency="0.003 0.015" numOctaves="2" seed="{seed+7}" result="d"/>
 <feDisplacementMap in="n" in2="d" scale="{warp}" xChannelSelector="R" yChannelSelector="G" result="nd"/>
 <feColorMatrix in="nd" type="matrix" values="1 0 0 0 0  1 0 0 0 0  1 0 0 0 0  0 0 0 0 1" result="gray"/>
 <feComponentTransfer in="gray"><feFuncR type="table" tableValues="{col_lo[0]} {col_hi[0]} {col_lo[0]} {col_hi[0]} {col_lo[0]}"/><feFuncG type="table" tableValues="{col_lo[1]} {col_hi[1]} {col_lo[1]} {col_hi[1]} {col_lo[1]}"/><feFuncB type="table" tableValues="{col_lo[2]} {col_hi[2]} {col_lo[2]} {col_hi[2]} {col_lo[2]}"/></feComponentTransfer>
</filter>'''
def c(h): h=h.lstrip('#'); return tuple(round(int(h[i:i+2],16)/255,3) for i in (0,2,4))

def wood_swatch(seed,lo,hi,gloss):
    sheen = '<rect width="600" height="600" fill="url(#gl)"/>' if gloss else '<rect width="600" height="600" fill="url(#mt)"/>'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="600" viewBox="0 0 600 600">
<defs>{WOOD(seed,"0.0035 0.11",c(lo),c(hi),26)}
<linearGradient id="gl" x1="0" y1="0" x2="1" y2="1"><stop offset="0.30" stop-color="#fff" stop-opacity="0"/><stop offset="0.43" stop-color="#fff" stop-opacity="0.30"/><stop offset="0.47" stop-color="#fff" stop-opacity="0.08"/><stop offset="0.62" stop-color="#fff" stop-opacity="0"/></linearGradient>
<linearGradient id="mt" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0.07"/><stop offset="1" stop-color="#000" stop-opacity="0.12"/></linearGradient></defs>
<rect x="-40" y="-40" width="680" height="680" filter="url(#w{seed})"/>{sheen}</svg>'''

def hero():
    # Wardrobe wall: sage-green matte PU shutters, loft, brass profile handles, oak floor, soft daylight.
    sh=[]; x0=520; W=230; gap=6
    for i in range(4):
        x=x0+i*(W+gap)
        sh.append(f'<rect x="{x}" y="250" width="{W}" height="560" rx="2" fill="url(#sage)"/>')
        sh.append(f'<rect x="{x}" y="120" width="{W}" height="124" rx="2" fill="url(#sage)"/>')
        hx = x+W-16 if i%2==0 else x+10
        sh.append(f'<rect x="{hx}" y="430" width="6" height="200" rx="3" fill="url(#brass)"/>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1000" viewBox="0 0 1600 1000">
<defs>
<linearGradient id="wall" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#2a2622"/><stop offset="0.55" stop-color="#5d554c"/><stop offset="1" stop-color="#3a342e"/></linearGradient>
<linearGradient id="sage" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#8f9c86"/><stop offset="0.6" stop-color="#7b8873"/><stop offset="1" stop-color="#5f6b59"/></linearGradient>
<linearGradient id="brass" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#7a5a26"/><stop offset="0.5" stop-color="#e7c27a"/><stop offset="1" stop-color="#8a6630"/></linearGradient>
<radialGradient id="light" cx="0.78" cy="0.25" r="0.75"><stop offset="0" stop-color="#fff3dc" stop-opacity="0.38"/><stop offset="1" stop-color="#fff3dc" stop-opacity="0"/></radialGradient>
<linearGradient id="shade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity="0.35"/></linearGradient>
{WOOD(11,"0.002 0.09",c("#4a3524"),c("#8a6644"),22)}
<linearGradient id="refl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7b8873" stop-opacity="0.25"/><stop offset="1" stop-color="#7b8873" stop-opacity="0"/></linearGradient>
</defs>
<rect width="1600" height="1000" fill="url(#wall)"/>
<rect x="500" y="100" width="980" height="730" fill="#1d1b19"/>
{''.join(sh)}
<rect x="500" y="810" width="980" height="20" fill="#2b2824"/>
<g transform="translate(0,830)"><rect x="-60" width="1720" height="200" filter="url(#w11)"/><rect width="1600" height="170" fill="url(#shade)"/></g>
<rect x="520" y="832" width="938" height="90" fill="url(#refl)"/>
<rect width="1600" height="1000" fill="url(#light)"/>
</svg>'''

def gloss_panel():
    # Close-up: deep navy high-gloss PU shutter with mirror reflection streaks and a crisp sprayed edge.
    return '''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="960" viewBox="0 0 1200 960">
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#d9d4cb"/><stop offset="1" stop-color="#a9a297"/></linearGradient>
<linearGradient id="navy" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1f3350"/><stop offset="0.5" stop-color="#13233a"/><stop offset="1" stop-color="#0b1626"/></linearGradient>
<linearGradient id="streak" x1="0" y1="0" x2="1" y2="0.35"><stop offset="0.18" stop-color="#fff" stop-opacity="0"/><stop offset="0.30" stop-color="#fff" stop-opacity="0.55"/><stop offset="0.335" stop-color="#fff" stop-opacity="0.12"/><stop offset="0.40" stop-color="#fff" stop-opacity="0"/><stop offset="0.62" stop-color="#fff" stop-opacity="0"/><stop offset="0.68" stop-color="#fff" stop-opacity="0.22"/><stop offset="0.70" stop-color="#fff" stop-opacity="0"/></linearGradient>
<linearGradient id="edge" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#0a1424"/><stop offset="1" stop-color="#2a4266"/></linearGradient>
<filter id="sh" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="22"/></filter>
</defs>
<rect width="1200" height="960" fill="url(#bg)"/>
<rect x="250" y="150" width="760" height="760" rx="6" fill="#000" opacity="0.35" filter="url(#sh)" transform="translate(30,40)"/>
<rect x="206" y="120" width="24" height="760" fill="url(#edge)"/>
<rect x="230" y="120" width="760" height="760" rx="3" fill="url(#navy)"/>
<rect x="230" y="120" width="760" height="760" rx="3" fill="url(#streak)"/>
<rect x="230" y="120" width="760" height="2" fill="#fff" opacity="0.35"/>
<rect x="904" y="330" width="10" height="340" rx="5" fill="#c9c3b8"/>
<rect x="904" y="330" width="4" height="340" rx="2" fill="#fff" opacity="0.6"/>
</svg>'''

def polish_door():
    # Teak veneer door under clear glossy PU polish: visible grain, soft reflection.
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="960" viewBox="0 0 1200 960">
<defs>{WOOD(23,"0.0028 0.10",c("#6b3f1d"),c("#b07a43"),30)}
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#e8e2d8"/><stop offset="1" stop-color="#bfb6a8"/></linearGradient>
<linearGradient id="gl" x1="0" y1="0" x2="1" y2="0.4"><stop offset="0.20" stop-color="#fff" stop-opacity="0"/><stop offset="0.34" stop-color="#fff" stop-opacity="0.30"/><stop offset="0.37" stop-color="#fff" stop-opacity="0.08"/><stop offset="0.50" stop-color="#fff" stop-opacity="0"/></linearGradient>
<filter id="sh"><feGaussianBlur stdDeviation="20"/></filter></defs>
<rect width="1200" height="960" fill="url(#bg)"/>
<rect x="330" y="80" width="560" height="860" fill="#000" opacity="0.3" filter="url(#sh)" transform="translate(24,24)"/>
<g transform="translate(320,70)"><svg width="560" height="860" overflow="hidden"><rect x="-40" y="-40" width="640" height="940" filter="url(#w23)"/></svg><rect width="560" height="860" fill="url(#gl)"/>
<rect x="60" y="70" width="440" height="330" fill="none" stroke="#3d220e" stroke-opacity="0.35" stroke-width="5"/>
<rect x="60" y="460" width="440" height="330" fill="none" stroke="#3d220e" stroke-opacity="0.35" stroke-width="5"/>
<circle cx="500" cy="440" r="14" fill="#cfb27a"/><circle cx="496" cy="436" r="5" fill="#fff" opacity="0.6"/></g>
</svg>'''

WOODS={'teak':(31,'#6e4220','#b5813f',1),'walnut':(41,'#3a2416','#7a5236',1),'white-oak':(51,'#b89a73','#e3cfae',0),
       'smoked-oak':(61,'#4a3a2d','#8e7660',0),'mahogany':(71,'#4d1f14','#9a4a2e',1),'wenge':(81,'#1f1611','#4f3d30',0)}
jobs={'hero-pu-wardrobe.jpg':(hero(),1600,1000),'gloss-navy-pu-panel.jpg':(gloss_panel(),1200,960),'teak-pu-polish-door.jpg':(polish_door(),1200,960)}
for k,(sd,lo,hi,g) in WOODS.items(): jobs[f'wood-{k}.jpg']=(wood_swatch(sd,lo,hi,g),600,600)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    for name,(svg,w,h) in jobs.items():
        pg=b.new_page(viewport={'width':w,'height':h})
        pg.set_content('<html><body style="margin:0">'+svg+'</body></html>'); pg.wait_for_timeout(150)
        pg.screenshot(path='/home/claude/render/'+name,type='jpeg',quality=84); pg.close()
    b.close()
print('ok',len(jobs))
