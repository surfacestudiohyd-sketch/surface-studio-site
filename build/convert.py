import re, json, sys, os
src = open(sys.argv[1]).read()
out = sys.argv[2]
outdir = os.path.dirname(os.path.abspath(out))
body = src.split('<x-dc>')[1].split('</x-dc>')[0]
helmet = re.search(r'<helmet>(.*?)</helmet>', body, re.S).group(1)
body = re.sub(r'<helmet>.*?</helmet>', '', body, flags=re.S)
blobs = {'6d8a7fb943b1b5dd089ceffb779d040a': 'images/hero-pu-wardrobe.jpg', '6d7e8d05bc8e79f4f837b821a91df98b': 'images/gloss-navy-pu-panel.jpg', '2ae73c91fd232b9dd80207c8dd933762': 'images/teak-pu-polish-door.jpg', '4e861e5150f1535f7aa084e7ad018846': 'images/wood-teak.jpg', 'cee414d04ae558554a9430262b109e93': 'images/wood-walnut.jpg', 'b35683588ded28a6fffc8b2ad38d49c4': 'images/wood-white-oak.jpg', '09e26507dd977680686813713a3b7ba4': 'images/wood-smoked-oak.jpg', 'db466db4c5dbccbf6c02c4ee0da8c9d0': 'images/wood-mahogany.jpg', '8be97defdd7c84a4418bfabdfd7b66ec': 'images/wood-wenge.jpg'}
for k,v in blobs.items(): body = body.replace('/_blob/'+k, v)
body = body.replace('onSubmit="{{send}}"','id="enquiry"')
body = body.replace('{{typed}}', '<span id="typed">Precision Coated.</span>')

# Keyless Google Maps embed. A name + full-address query, centred on the studio's exact lat/lng, is the most
# reliable keyless way to land on the Surface Studio listing (the q=place_id: form needs the Embed API + a key).
MAP_EMBED = ('https://www.google.com/maps?q=Surface+Studio,+Bollaram+Industrial+Area,+Bollaram,+Hyderabad,+Telangana+502325'
             '&amp;ll=17.5484382,78.343641&amp;z=16&amp;hl=en&amp;output=embed')
IFRAME = ('<iframe title="Surface Studio on Google Maps (IDA Bollaram, Hyderabad)" src="%s" loading="lazy" '
          'referrerpolicy="strict-origin-when-cross-origin" '
          'style="border:0;width:100%%;height:100%%;min-height:260px;flex:1 1 260px;display:block;filter:grayscale(.3) contrast(1.05)"></iframe>') % MAP_EMBED
body = re.sub(r'<!-- MAP-START -->.*?<!-- MAP-END -->', lambda m: IFRAME, body, flags=re.S)

# tabs: one real tablist with ids / aria-controls instead of the canvas' three sc-if copies
tab_re = re.compile(r'<div role="tablist".*?</div>\n', re.S)
BRANDS = [('sirca','Sirca'),('ica','ICA'),('axalta','Axalta')]
tabs = ('<div role="tablist" aria-label="Coating brand" style="display: flex; flex-wrap: wrap; gap: 6px; padding: 6px; border-radius: 999px; background: #1D1D23; border: 1px solid #2A2A32">'
 + ''.join('<button type="button" role="tab" class="ss-tab" id="tab-%s" aria-controls="panel-%s" data-tab="%s" aria-selected="%s" tabindex="%s">%s</button>'
           % (k,k,k,'true' if i==0 else 'false','0' if i==0 else '-1',n) for i,(k,n) in enumerate(BRANDS))
 + '</div>\n')
body = tab_re.sub(lambda m: tabs, body, count=1)
for k,flag,hid in [('sirca','isSirca',''),('ica','isIca',' hidden'),('axalta','isAxalta',' hidden')]:
    body = re.sub(r'<sc-if value="\{\{%s\}\}"[^>]*>' % flag,
                  '<div data-panel="%s" id="panel-%s" role="tabpanel" aria-labelledby="tab-%s" tabindex="0"%s>' % (k,k,k,hid), body)
body = body.replace('</sc-if>', '</div>')

# lazy-load non-hero images (the first <img> is the hero / LCP image)
first = True
def lazy(m):
    global first
    if first: first=False; return m.group(0).replace('<img ','<img fetchpriority="high" ')
    return m.group(0).replace('<img ','<img loading="lazy" decoding="async" ')
body = re.sub(r'<img [^>]*>', lazy, body)
assert '{{' not in body and 'sc-if' not in body, re.findall(r'.{40}\{\{.{40}', body)

# sanity checks on the generated page
assert body.count('<div') == body.count('</div>'), (body.count('<div'), body.count('</div>'))
assert len(re.findall(r'<h1[ >]', body)) == 1
ids = re.findall(r'\sid="([^"]+)"', body)
assert len(ids) == len(set(ids)), sorted(i for i in ids if ids.count(i) > 1)
for a in set(re.findall(r'href="#([^"]+)"', body)):
    assert a in ids, 'missing anchor target #' + a
for a in re.findall(r'<a [^>]*href="https?://[^"]*"[^>]*>', body):
    assert 'target="_blank"' in a and 'rel="noopener noreferrer"' in a, a

head = open('/home/claude/build/head_filled.html').read()
extra_css = """
.ss-tab{min-height:44px;padding:0 26px;border:0;border-radius:999px;font-family:Outfit,system-ui,sans-serif;font-weight:600;font-size:15px;cursor:pointer;color:#C9C9D1;background:transparent}
.ss-tab[aria-selected="true"]{color:#fff;background:linear-gradient(90deg,#C2410C,#A532C2)}
[hidden]{display:none !important}
.ss-bar{display:none}
@media (max-width:900px){
.ss-bar{display:grid;grid-template-columns:1fr 1fr 1.3fr;gap:8px;position:fixed;left:0;right:0;bottom:0;z-index:30;padding:8px 10px calc(8px + env(safe-area-inset-bottom));background:rgba(18,18,22,.96);border-top:1px solid #2A2A32;backdrop-filter:blur(12px)}
.ss-bar a{display:flex;align-items:center;justify-content:center;gap:8px;min-height:48px;border-radius:999px;border:1px solid #3A3A44;font-family:Outfit,system-ui,sans-serif;font-weight:600;font-size:14px;color:#F4F4F6;text-decoration:none}
.ss-bar a.ss-bar-main{border:0;background:linear-gradient(90deg,#C2410C,#A532C2);color:#fff}
body{padding-bottom:calc(66px + env(safe-area-inset-bottom))}
}
@media print{.ss-bar{display:none !important}}
html{scroll-behavior:smooth}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
"""
helmet = helmet.replace('</style>', extra_css + '</style>')

# Page behaviour lives in an external file so the CSP can forbid inline scripts (script-src 'self').
js = r'''/* Surface Studio - site behaviour. External file so the Content-Security-Policy can forbid inline scripts. */
(function () {
  'use strict';
  // Hero typing effect. The full phrase "Precision Coated." is already in the HTML for crawlers / no-JS.
  var words = ['Precision Coated.', 'Beyond Paint.', 'Flawless Finishes.', 'Engineered Surfaces.'];
  var w = 0, c = words[0].length, del = false, p = 0, el = document.getElementById('typed');
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (el && !reduce) {
    setInterval(function () {
      var s = words[w];
      if (!del) { if (c < s.length) { c++; } else if (++p > 22) { p = 0; del = true; } }
      else { if (c > 0) { c--; } else { del = false; w = (w + 1) % words.length; } }
      el.textContent = s.slice(0, c);
    }, 85);
  }

  // Quote form -> WhatsApp. User input only goes into the URL (encodeURIComponent), never into the DOM.
  var fm = document.getElementById('enquiry');
  if (fm) {
    fm.addEventListener('submit', function (e) {
      e.preventDefault();
      var f = fm.elements;
      var v = function (n, max) { var x = f.namedItem(n); return x ? String(x.value || '').trim().slice(0, max) : ''; };
      var t = 'Hi Surface Studio, I would like a quote.' +
        '\nName: ' + v('name', 80) + '\nPhone: ' + v('phone', 20) +
        '\nRequirement: ' + v('need', 80) + '\nDetails: ' + v('msg', 1000);
      window.open('https://wa.me/919505969558?text=' + encodeURIComponent(t), '_blank', 'noopener');
    });
  }

  // Open / closed status in India time (studio hours Mon-Sat 9:30-17:30).
  var on = document.getElementById('open-now');
  if (on) {
    try {
      var parts = new Intl.DateTimeFormat('en-GB', { timeZone: 'Asia/Kolkata', weekday: 'short', hour: '2-digit', minute: '2-digit', hour12: false }).formatToParts(new Date());
      var g = function (t) { for (var i = 0; i < parts.length; i++) if (parts[i].type === t) return parts[i].value; return ''; };
      var day = g('weekday'), mins = (+g('hour') % 24) * 60 + (+g('minute'));
      var isOpen = day !== 'Sun' && mins >= 570 && mins < 1050;
      on.textContent = isOpen ? 'Open now \u00B7 until 5:30 pm' : 'Closed now \u00B7 Mon \u2013 Sat, 9:30 am \u2013 5:30 pm';
    } catch (e) {}
  }
  var firstFaq = document.querySelector('.ss-faq');
  if (firstFaq) firstFaq.setAttribute('open', '');

  // Mobile menu: close on link click, outside click and Escape.
  var mob = document.querySelector('.ss-mob');
  if (mob) {
    mob.querySelectorAll('a').forEach(function (a) { a.addEventListener('click', function () { mob.removeAttribute('open'); }); });
    document.addEventListener('click', function (e) { if (mob.hasAttribute('open') && !mob.contains(e.target)) mob.removeAttribute('open'); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && mob.hasAttribute('open')) { mob.removeAttribute('open'); mob.querySelector('summary').focus(); }
    });
  }

  // Brand tabs (WAI-ARIA tabs pattern: click, Arrow keys, Home / End).
  var tabs = Array.prototype.slice.call(document.querySelectorAll('.ss-tab'));
  function select(b, focus) {
    tabs.forEach(function (x) {
      var on = x === b;
      x.setAttribute('aria-selected', on ? 'true' : 'false');
      x.tabIndex = on ? 0 : -1;
    });
    document.querySelectorAll('[data-panel]').forEach(function (p) { p.hidden = p.getAttribute('data-panel') !== b.getAttribute('data-tab'); });
    if (focus) b.focus();
  }
  tabs.forEach(function (b, i) {
    b.addEventListener('click', function () { select(b, false); });
    b.addEventListener('keydown', function (e) {
      var n = null;
      if (e.key === 'ArrowRight') n = tabs[(i + 1) % tabs.length];
      else if (e.key === 'ArrowLeft') n = tabs[(i - 1 + tabs.length) % tabs.length];
      else if (e.key === 'Home') n = tabs[0];
      else if (e.key === 'End') n = tabs[tabs.length - 1];
      if (n) { e.preventDefault(); select(n, true); }
    });
  });
})();
'''
os.makedirs(os.path.join(outdir, 'js'), exist_ok=True)
open(os.path.join(outdir, 'js', 'site.js'), 'w').write(js)
import json as _json
_rates=_json.load(open('/home/claude/build/rates.json'))
import shutil as _sh
os.makedirs(os.path.join(outdir,'js','vendor'),exist_ok=True)
for _f in ('pdf.min.mjs','pdf.worker.min.mjs'):
    _sh.copy('/opt/npm-tools/node_modules/pdfjs-dist/legacy/build/'+_f, os.path.join(outdir,'js','vendor',_f))
_sh.copy('/opt/npm-tools/node_modules/pdfjs-dist/LICENSE', os.path.join(outdir,'js','vendor','PDFJS-LICENSE.txt'))
open(os.path.join(outdir,'js','quote.js'),'w').write(open('/home/claude/build/quote.js').read().replace('__RATES__',_json.dumps(_rates,separators=(',',':'))))
import urllib.parse as _up
_ai=_rates.get('ai_endpoint','').strip()
_ai_origin=('%s://%s'%(_up.urlparse(_ai).scheme,_up.urlparse(_ai).netloc)) if _ai else ''
_log=_rates.get('quote_log_endpoint','').strip()
if _log:
    assert _log.startswith('https://script.google.com/'), 'quote_log_endpoint must be an Apps Script /exec URL'
    _ai_origin=(_ai_origin+' ' if _ai_origin else '')+'https://script.google.com https://script.googleusercontent.com'
if _ai_origin:
    assert _ai_origin.startswith('https://'), 'ai_endpoint must be https'
    head=head.replace("connect-src 'self'","connect-src 'self' "+_ai_origin)
    for _hf in ('_headers','.htaccess'):
        _p=os.path.join(outdir,_hf)
        if os.path.exists(_p):
            _t=open(_p).read()
            if _ai_origin not in _t: open(_p,'w').write(_t.replace("connect-src 'self'","connect-src 'self' "+_ai_origin))
script = '<script src="js/site.js" defer></script>\n<script src="js/quote.js" defer></script>'

html = ('<!doctype html>\n<html lang="en-IN">\n<head>\n' + head + helmet + '\n</head>\n<body>\n'
        + body.replace('<!-- HERO -->','<main>\n<!-- HERO -->').replace('<!-- FOOTER -->','<section class="ss-guides" aria-label="Guides and prices" style="max-width: 1200px; margin: 0 auto; padding: 0 24px 72px; box-sizing: border-box; font-family: Outfit, system-ui, sans-serif"><h2 style="margin: 0 0 16px; font-size: 20px; font-weight: 600; color: #F4F4F6">Guides and prices</h2><ul style="margin: 0; padding: 0; list-style: none; display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 210px), 1fr)); gap: 12px"><li><a href="/pu-paint-hyderabad/" style="display: block; min-height: 44px; padding: 16px 18px; border-radius: 14px; border: 1px solid #2A2A32; background: #1D1D23; font-weight: 600; font-size: 16px">PU paint in Hyderabad<span style="display: block; margin-top: 4px; font-weight: 400; font-size: 14px; color: #A9A9B3">Solid colours on MDF and HDHMR</span></a></li><li><a href="/pu-polish-hyderabad/" style="display: block; min-height: 44px; padding: 16px 18px; border-radius: 14px; border: 1px solid #2A2A32; background: #1D1D23; font-weight: 600; font-size: 16px">PU polish in Hyderabad<span style="display: block; margin-top: 4px; font-weight: 400; font-size: 14px; color: #A9A9B3">Clear and tinted polish on wood</span></a></li><li><a href="/pu-paint-polish-price-hyderabad/" style="display: block; min-height: 44px; padding: 16px 18px; border-radius: 14px; border: 1px solid #2A2A32; background: #1D1D23; font-weight: 600; font-size: 16px">PU price per sq ft<span style="display: block; margin-top: 4px; font-weight: 400; font-size: 14px; color: #A9A9B3">Full rate card and how we measure</span></a></li><li><a href="/sirca-vs-ica-vs-axalta/" style="display: block; min-height: 44px; padding: 16px 18px; border-radius: 14px; border: 1px solid #2A2A32; background: #1D1D23; font-weight: 600; font-size: 16px">Sirca vs ICA vs Axalta<span style="display: block; margin-top: 4px; font-weight: 400; font-size: 14px; color: #A9A9B3">Which coating brand to choose</span></a></li><li><a href="/modular-panel-pu-finishing/" style="display: block; min-height: 44px; padding: 16px 18px; border-radius: 14px; border: 1px solid #2A2A32; background: #1D1D23; font-weight: 600; font-size: 16px">Modular panel finishing<span style="display: block; margin-top: 4px; font-weight: 400; font-size: 14px; color: #A9A9B3">For factories and interior firms</span></a></li></ul></section>\n</main>\n<!-- FOOTER -->')
        + '<nav class="ss-bar" aria-label="Quick contact"><a href="tel:+919505969558"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 4h4l2 5-2.500 1.500a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"></path></svg>Call</a><a href="https://wa.me/919505969558" target="_blank" rel="noopener noreferrer"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 20l1.300-4A8 8 0 1 1 8 18.700z"></path></svg>WhatsApp</a><a class="ss-bar-main" href="#instant-quote">Instant quote</a></nav>\n' + script + '\n</body>\n</html>\n')
assert '<script>' not in html, 'inline script would be blocked by the CSP'
open(out,'w').write(html)
print(len(html))
