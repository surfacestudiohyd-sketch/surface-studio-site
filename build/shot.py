import sys
from playwright.sync_api import sync_playwright
src, tag = sys.argv[1], sys.argv[2]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    for name,w in [('d',1440),('m',390)]:
        pg = b.new_page(viewport={'width':w,'height':900})
        pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        pg.goto('file://'+src); pg.wait_for_timeout(600)
        h = pg.evaluate('document.documentElement.scrollHeight')
        pg.screenshot(path=f'/home/claude/shots/{tag}_{name}.png', full_page=True)
        print(name, w, h, 'overflowX', pg.evaluate('document.documentElement.scrollWidth'))
    b.close()
