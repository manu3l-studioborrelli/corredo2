#!/usr/bin/env python3
"""Rebuild index.html (homepage preview) from data/catalog.csv + tools/template.html.

    python tools/build.py        # homepage + category pages + product page

Also writes data/catalog.json (clean product list, ready for the product/category pages).
"""
import csv, json, re, html, collections, hashlib, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
esc = html.escape

# ───────────────────────── data ─────────────────────────
COLORS = {
    'nero': '#2b2b2b', 'bianco': '#ffffff', 'beige': '#e6d5b8', 'tortora': '#b5a392', 'panna': '#f3ecd9',
    'tiffany': '#81d8d0', 'biscotto': '#d9b78f', 'rosa': '#f4c2c9', 'azzurro': '#bcd9ee', 'blu': '#2f5aa8',
    'verde': '#3f8a5a', 'rosso': '#c8323c', 'giallo': '#f2c94c', 'grigio': '#9aa0a6', 'grigio chiaro': '#cfd2d6',
    'grigio scuro': '#6b6f76', 'grigio perla': '#d9dbe0', 'blu elettrico': '#1e4fff', 'corallo': '#ff7a68',
    'nudo': '#e8c2a8', 'avion': '#7fb1d6', 'sabbia': '#d8c39a', 'marrone': '#7a5638', 'bordeaux': '#6e1f2f',
}


def slug(s):
    s = s.lower()
    for a, b in (('à', 'a'), ('è', 'e'), ('é', 'e'), ('ì', 'i'), ('ò', 'o'), ('ù', 'u')):
        s = s.replace(a, b)
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')


def money(s):
    s = s.replace('€', '').strip().replace('.', '').replace(',', '.')
    return float(s) if s else None


def clean_name(n):
    n = n.strip()
    if n.endswith('...'):
        n = n[:-3].rstrip(' ,')
    return n


def load():
    rows = []
    for r in csv.DictReader(open(ROOT / 'data/catalog.csv', encoding='utf-8')):
        prev = re.search(r'prezzo precedente\s*([\d.,]+)', r['bundle_offer'])
        bundle = '' if prev else r['bundle_offer'].strip()
        cols = [c.strip() for c in r['colors'].split(',') if c.strip()]
        rows.append(dict(
            id=r['product_id'], handle=slug(clean_name(r['product_name'])) + '-' + r['product_id'].lower(),
            category=r['category'], subcategory=r['subcategory'], title=clean_name(r['product_name']),
            brand=r['brand'].strip(), audience=r['audience'], price=money(r['price_eur']),
            priceType=r['price_type'], unit=r['unit'], packQty=int(r['pack_qty'] or 1), bundle=bundle,
            compareAt=money(prev.group(1)) if prev else None, sizes=r['sizes'].strip(), colors=cols,
            season=r['season_hint'], posts=int(r['posts_count'] or 1)))
    return rows


# P216 has no price in the sheet: demo value so the product page can be shown. Confirm with the client.
DEMO_OVERRIDES = {'P216': dict(price=9.99, priceType='esatto', priceIsDemo=True)}


def cat_url(c, sub=None):
    return 'categoria-%s.html%s' % (slug(c), '?sub=%s' % slug(sub) if sub else '')


def product_url(p):
    # only P216 has a product page for now
    return 'prodotto.html' if p['id'] == 'P216' else '#'


PRODUCTS = load()
for _p in PRODUCTS:
    _p.update(DEMO_OVERRIDES.get(_p['id'], {}))
BY_ID = {p['id']: p for p in PRODUCTS}
CATS = collections.OrderedDict()
for p in PRODUCTS:
    CATS.setdefault(p['category'], collections.Counter())[p['subcategory']] += 1


def cat_count(c):
    return sum(CATS[c].values())


def cat_min(c, sub=None):
    return min(p['price'] for p in PRODUCTS if p['category'] == c and p['price'] and (sub is None or p['subcategory'] == sub))


def eur(v):
    return '€' + ('%.2f' % v).replace('.', ',')


def eur_s(v):
    return ('%.2f' % v).replace('.', ',') + ' €'


# ───────────────────────── images (Unsplash stock) ─────────────────────────
IMG = {
    'lenz': ['1606796913825-2b02883605e9', '1598535746036-87d13382f6a6', '1601276174812-63280a55656e'],
    'letto': ['1698746044395-85beb2b04522', '1564019472231-4586c552dc27', '1688384452551-5cacc39946e0'],
    'trap': ['1688384452551-5cacc39946e0', '1698746044395-85beb2b04522', '1564019472231-4586c552dc27'],
    'plaid': ['1674475760738-8c7af859f821', '1688384452551-5cacc39946e0'],
    'asciug': ['1574421233376-06f2ccf017f7', '1523471826770-c437b4636fe6'],
    'accapp': ['1710378439817-6159c79bda03', '1704428381481-92bf396b24bd', '1766727923624-2e8eede5aa8c'],
    'bagno': ['1523471826770-c437b4636fe6', '1574421233376-06f2ccf017f7'],
    'tappeti': ['1600166898405-da9535204843', '1583847268964-b28dc8f51f92', '1572123979839-3749e9973aba'],
    'zerbini': ['1672403391906-810131b660eb', '1672403393566-6a75b48e7951', '1615927998810-ca467ad48c5f'],
    'casa': ['1511401139252-f158d3209c17', '1615529182904-14819c35db37'],
    'scarp': ['1478887011962-709960f8ced8', '1502238074616-a146498d5158', '1551851363-65f4f9107b97'],
    'cuscini': ['1553114552-c4ece3a33c93', '1538577880403-f9998e75dd06'],
    'cucina': ['1692651435527-a3ecf950ae30', '1615529182904-14819c35db37'],
    'intimoD': ['1525171254930-643fc658b64e', '1562157873-818bc0726f68'],
    'intimoU': ['1548768041-2fceab4c0b85'],
    'calze': ['1641399050826-9616c90427bb', '1730448111621-c0524e75b0e8'],
    'pantofole': ['1543420629-5350879dd4cd'],
    'pigD': ['1654512462970-8191bc8742bd', '1692111643020-4b4726e0dd8f', '1694709109732-ed8768fe8d48'],
    'pigU': ['1768696082915-bdc6774f94c7'],
    'abbD': ['1762154057377-cc9d3dd6900c', '1613966570650-add3cf83aa83', '1713881630214-82c44407cf25'],
    'abbU': ['1720514496268-44bb31c03815', '1714317437555-bdaa756ade0b', '1717127354833-e4d10625d3e7'],
    'bimbi': ['1560506840-ec148e82a604', '1566454544259-f4b94c3d758c', '1560859259-fcf2b952aed8'],
    'neo': ['1569974641446-22542de88536', '1768693602418-260d828b878d', '1766918780914-5df4a5a98c44'],
    'sport': ['1600696491085-19dbbeb4f8c1', '1584863495140-a320b13a11a8'],
    'telo': ['1625931046289-e51edea3e176', '1760783320488-9af5d3217f50', '1533263523557-048aafccc637'],
    'borsa': ['1554342872-034a06541bad', '1719386214534-b7f60036d2ef', '1506094543314-3747d5123bbe'],
    'costumi': ['1762944081584-f150e797f803', '1789222523783-65911021aad5', '1789222523814-dc3cc295b1f0'],
}
PALETTES = [('#f5dcd3', '#b04a4a'), ('#fbe3cf', '#b5612a'), ('#e6dff0', '#6a4f8a'), ('#d9e6ee', '#3c6a85'),
            ('#ecdfc6', '#7a5b2e'), ('#dbe5d6', '#48644a'), ('#d6dbe6', '#26344a'), ('#f3d2cf', '#8f1d2c'), ('#d5ebe2', '#2f7a5e')]


def pool_for(p):
    c, s, a, t = p['category'], p['subcategory'], p['audience'], p['title'].lower()
    if c == 'Biancheria letto':
        return {'Lenzuola': 'lenz', 'Trapunte': 'trap', 'Coperte': 'plaid', 'Plaid': 'plaid'}.get(s, 'letto')
    if c == 'Bagno':
        return {'Accappatoi': 'accapp', 'Accappatoi bimbi': 'accapp', 'Tappeti bagno': 'bagno'}.get(s, 'asciug')
    if c == 'Casa e arredo':
        return {'Scarpiere': 'scarp', 'Cuscini': 'cuscini', 'Zerbini': 'zerbini', 'Runner': 'letto', 'Tappeti': 'tappeti',
                'Tappeti a metraggio': 'tappeti'}.get(s, 'casa')
    if c == 'Cucina e tavola':
        return 'cucina'
    if c == 'Intimo donna':
        return 'intimoD'
    if c == 'Intimo uomo':
        return 'intimoU'
    if c == 'Calze e calzini':
        return 'calze'
    if c == 'Calzature':
        return 'pantofole'
    if c == 'Pigiami e notte':
        return 'pigU' if (a == 'uomo' or ('uomo' in t and 'donna' not in t)) else 'pigD'
    if c == 'Abbigliamento donna':
        return 'abbD'
    if c == 'Abbigliamento uomo':
        return 'abbU'
    if c in ('Abbigliamento bimbi', 'Scuola'):
        return 'bimbi'
    if c == 'Neonato':
        return 'neo'
    if c == 'Sport e tute':
        return 'sport'
    if c == 'Mare e costumi':
        return {'Teli mare': 'telo', 'Borse mare': 'borsa'}.get(s, 'costumi')
    return 'casa'


def h(p):
    return int(hashlib.md5(p['id'].encode()).hexdigest(), 16)


for p in PRODUCTS:
    pool = IMG[pool_for(p)]
    p['image'] = [pool[(h(p) + i) % len(pool)] for i in range(min(3, len(pool)))]

# P216 (product page): photos per colour, in gallery order black, black, white, white, blue
P216_IMAGES = ['1562135291-7728cc647783', '1610502778270-c5c6f4c7d575', '1620799139507-2a76f79a2f4d',
               '1620799139652-715e4d5b232d', '1666358070734-b9d6590278c9']
BY_ID['P216']['image'] = P216_IMAGES


for p in PRODUCTS:  # availability is NOT in the sheet: deterministic demo values (~8% out of stock, ~12% low)
    r = h(p) % 100
    p['stock'] = 'in' if p['id'] == 'P216' else ('out' if r < 8 else 'low' if r < 20 else 'in')
    p['stockIsDemo'] = True


def pal(p):
    return PALETTES[h(p) % len(PALETTES)]


def u(pid, w=500):
    return 'https://images.unsplash.com/photo-%s?auto=format&fit=crop&w=%d&q=70' % (pid, w)


def art(pid, bg, fg, w=500, cls='', alt='', lazy=True):
    return ('<div class="art %s" style="--bg:%s;--fg:%s"><img src="%s" alt="%s"%s decoding="async"></div>'
            % (cls, bg, fg, u(pid, w), esc(alt), ' loading="lazy"' if lazy else ''))


# ───────────────────────── components ─────────────────────────
def U(n):
    return '<svg class="i" viewBox="0 0 24 24" aria-hidden="true"><use href="#u-%s"/></svg>' % n


ARROW = U('arrow')


def ICO(n):
    return '<svg class="ico" viewBox="0 0 64 64" aria-hidden="true"><use href="#i-%s"/></svg>' % n


def price_html(p):
    s = '<div class="%s">' % ('price price--sale' if p['compareAt'] else 'price')
    if p['priceType'] == 'da':
        s += '<span class="price__from">da</span>'
    s += '<span class="price__now">%s</span>' % eur(p['price'])
    if p['compareAt']:
        s += '<s>%s</s>' % eur(p['compareAt'])
    if p['unit'] == 'metro':
        s += '<span class="price__unit">/ metro</span>'
    elif p['unit'] == 'paio':
        s += '<span class="price__unit">/ paio</span>'
    elif p['unit'] == 'set':
        s += '<span class="price__unit">/ set%s</span>' % (' da %d' % p['packQty'] if p['packQty'] > 1 else '')
    return s + '</div>'


def swatches(p):
    out = []
    for c in p['colors'][:5]:
        if c == 'vari colori':
            out.append('<i class="multi" title="Vari colori"></i>')
        elif c in COLORS:
            out.append('<i style="--c:%s" title="%s"></i>' % (COLORS[c], esc(c)))
    return '<div class="swatches" aria-label="Colori disponibili">%s</div>' % ''.join(out) if out else ''


def badge(p):
    if p['compareAt']:
        return '<span class="badge">-%d%%</span>' % round((1 - p['price'] / p['compareAt']) * 100)
    m = re.match(r'(\d) (\w+) ([\d,]+) €', p['bundle'])
    if m:
        return '<span class="badge">%s a %s €</span>' % (m.group(1), m.group(3))
    if 'omaggio' in p['bundle']:
        return '<span class="badge">3ª in omaggio</span>'
    return ''


def vendor(p):
    return esc(p['brand'].split(',')[0]) if p['brand'] else 'Il Corredo 2'


def add_btn(p, cls='btn btn--sm', extra=''):
    return ('<button class="%s" data-add %sdata-id="%s" data-title="%s" data-price="%s" data-img="%s">Aggiungi al carrello</button>'
            % (cls, extra, p['id'], esc(p['title']), p['price'], u(p['image'][0], 200)))


def pcard(p):
    bg, fg = pal(p)
    return '''<article class="pcard" data-product>
  <div class="pcard__media">
    <a href="%(url)s" aria-label="%(t)s">%(art)s</a>
    %(badge)s
    <button class="wish" aria-label="Aggiungi ai preferiti" aria-pressed="false">%(heart)s</button>
  </div>
  <div class="pcard__body">
    <span class="pcard__vendor">%(v)s</span>
    <h3 class="pcard__title"><a href="%(url)s">%(t)s</a></h3>
    %(sw)s
    %(price)s
    %(btn)s
  </div>
</article>''' % dict(url=product_url(p), t=esc(p['title']), art=art(p['image'][0], bg, fg), badge=badge(p), heart=U('heart'), v=vendor(p),
                     sw=swatches(p), price=price_html(p), btn=add_btn(p))


def hitem(p):
    bg, fg = pal(p)
    return '''<div class="hitem" data-product>
  <a href="%s">%s</a>
  <div class="hitem__t"><small>%s</small><strong>%s</strong>
    %s</div>
  <button class="add-mini" aria-label="Aggiungi %s al carrello" data-add data-id="%s" data-title="%s" data-price="%s" data-img="%s">%s</button>
</div>''' % (product_url(p), art(p['image'][0], bg, fg), vendor(p), esc(p['title']), price_html(p), esc(p['title']), p['id'], esc(p['title']),
             p['price'], u(p['image'][0], 200), U('plus'))


def carousel(inner, label):
    return ('<div class="carousel" data-carousel role="region" aria-label="%s">\n'
            '  <button class="carousel__btn carousel__btn--prev" aria-label="Precedente">%s</button>\n'
            '  <div class="carousel__track">%s</div>\n'
            '  <button class="carousel__btn carousel__btn--next" aria-label="Successivo">%s</button>\n</div>'
            % (label, U('left'), inner, U('right')))


def P(*ids):
    return [BY_ID['P' + i] for i in ids]


# Scuola has a single product (a school uniform) and is kept out of the navigation.
GROUPS = [
    ('Abbigliamento', 'shirt', ['Abbigliamento donna', 'Abbigliamento uomo', 'Sport e tute', 'Mare e costumi']),
    ('Intimo e notte', 'pajamas', ['Intimo donna', 'Intimo uomo', 'Pigiami e notte', 'Calze e calzini', 'Calzature']),
    ('Casa', 'sofa', ['Biancheria letto', 'Bagno', 'Casa e arredo', 'Cucina e tavola']),
    ('Bambini', 'heart', ['Abbigliamento bimbi', 'Neonato']),
]
CAROUSEL_ORDER = ['Intimo donna', 'Abbigliamento donna', 'Pigiami e notte', 'Biancheria letto', 'Bagno', 'Casa e arredo', 'Cucina e tavola',
                  'Intimo uomo', 'Abbigliamento uomo', 'Neonato', 'Abbigliamento bimbi', 'Calze e calzini', 'Calzature', 'Sport e tute',
                  'Mare e costumi']
CAT_IMG = {'Intimo donna': IMG['intimoD'][0], 'Abbigliamento donna': IMG['abbD'][0], 'Pigiami e notte': IMG['pigD'][2],
           'Biancheria letto': IMG['letto'][1], 'Bagno': IMG['asciug'][0], 'Casa e arredo': IMG['tappeti'][0],
           'Cucina e tavola': IMG['cucina'][0], 'Intimo uomo': IMG['intimoU'][0], 'Abbigliamento uomo': IMG['abbU'][0],
           'Neonato': IMG['neo'][0], 'Abbigliamento bimbi': IMG['bimbi'][0], 'Calze e calzini': IMG['calze'][0],
           'Calzature': IMG['pantofole'][0], 'Sport e tute': IMG['sport'][0], 'Mare e costumi': IMG['telo'][0]}


def cpal(c):
    return PALETTES[CAROUSEL_ORDER.index(c) % len(PALETTES)]


def subs(c, n=None):
    s = [k for k, _ in CATS[c].most_common()]
    return s[:n] if n else s


# ───────────────────────── sections ─────────────────────────
def nav_items():
    cols = ''
    for title, icon, cats in GROUPS:
        lis = ''.join('<li><a href="%s">%s</a></li>' % (cat_url(c), esc(c)) for c in cats)
        cols += '<div><h4>%s<span>%s</span></h4><ul>%s</ul></div>' % (ICO(icon), title, lis)
    mega = ('<div class="mega">\n            %s\n            <a class="mega__promo" href="%s">%s<strong>Aspettando l&rsquo;inverno</strong>'
            '<span>Coperte, trapunte e plaid da %s</span><span class="link-u">Scopri la collezione</span></a>\n          </div>'
            % (cols, cat_url('Biancheria letto', 'Plaid'), ICO('bed'), eur_s(cat_min('Biancheria letto', 'Plaid'))))
    items = ['<li class="nav__item"><a class="nav__link" href="categoria-offerte.html">Offerte<span class="nav-badge">Deal</span></a></li>',
             '<li class="nav__item nav__item--static" data-mega>\n          <a class="nav__link" href="categoria-tutti.html" aria-haspopup="true" aria-expanded="false">'
             'Tutte le categorie%s</a>\n          %s\n        </li>' % (U('down'), mega)]
    for c in ['Intimo donna', 'Abbigliamento donna', 'Pigiami e notte', 'Biancheria letto', 'Bagno', 'Casa e arredo']:
        items.append('<li class="nav__item"><a class="nav__link" href="%s">%s</a></li>' % (cat_url(c), esc(c)))
    return '        ' + '\n        '.join(items)


def drawer_links():
    out = ['    <a class="dlink" href="categoria-offerte.html">Offerte<span class="tag">Deal</span></a>']
    for k, c in enumerate(CAROUSEL_ORDER):
        links = ''.join('<a href="%s">%s</a>' % (cat_url(c, s), esc(s)) for s in subs(c))
        out.append('<button class="dlink" data-acc="d%d" aria-expanded="false">%s%s</button><div class="dsub" id="d%d">'
                   '<a class="dsub__all" href="%s">Vedi tutto in %s</a>%s</div>' % (k, esc(c), U('down'), k, cat_url(c), esc(c), links))
    out += ['    <a class="dlink" href="#">Il nostro negozio</a>', '    <a class="dlink" href="#">Idee e consigli</a>']
    return '\n'.join(out)


def search_options():
    return '<option>Tutte le categorie</option>' + ''.join('<option>%s</option>' % esc(c) for c in CAROUSEL_ORDER)


def hero_slides():
    slides = [
        ('wine', 'Aspettando l&rsquo;inverno', 'Coperte, trapunte<br>e plaid',
         'Plaid da %s, trapunte da %s: tutto per un letto caldo.' % (eur_s(cat_min('Biancheria letto', 'Plaid')), eur_s(cat_min('Biancheria letto', 'Trapunte'))),
         'Scopri il letto', IMG['trap'][0], True),
        ('navy', 'Notte perfetta', 'Pigiami per<br>tutta la famiglia',
         '%d modelli per lei e per lui, da %s.' % (cat_count('Pigiami e notte'), eur_s(cat_min('Pigiami e notte'))),
         'Scopri i pigiami', IMG['pigD'][1], False),
        ('blush', 'Intimo per lei e per lui', 'Comfort<br>ogni giorno',
         'Slip da %s, reggiseni da %s, boxer e completi in confezioni convenienti.' % (eur_s(cat_min('Intimo donna', 'Slip')), eur_s(cat_min('Intimo donna', 'Reggiseni'))),
         'Scopri l&rsquo;intimo', IMG['intimoD'][1], False),
        ('sand', 'Casa che accoglie', 'Bagno, tappeti<br>e tavola',
         'Asciugamani da %s a coppia, tappeti da %s, tovaglie e strofinacci.' % (eur_s(cat_min('Bagno', 'Asciugamani')), eur_s(cat_min('Casa e arredo', 'Tappeti'))),
         'Scopri la casa', IMG['tappeti'][1], False),
    ]
    out = []
    urls = [cat_url('Biancheria letto'), cat_url('Pigiami e notte'), cat_url('Intimo donna'), cat_url('Bagno')]
    for (theme, eyebrow, h2, txt, cta, img, first), url in zip(slides, urls):
        out.append('''    <article class="slide slide--%s" aria-roledescription="slide">
  <div class="slide__text">
    <span class="slide__eyebrow">%s</span>
    <h2>%s</h2>
    <p>%s</p>
    <a class="btn" href="%s">%s%s</a>
  </div>
  <div class="slide__art"><img src="%s" alt="" %s decoding="async"></div>
</article>''' % (theme, eyebrow, h2, txt, url, cta, ARROW, u(img, 1200), 'fetchpriority="high"' if first else 'loading="lazy"'))
    return '  <div class="hero__track">\n' + '\n'.join(out) + '\n  </div>'


def categories():
    cards = ''
    for c in CAROUSEL_ORDER:
        bg, fg = cpal(c)
        cards += '<a class="catcard" href="%s">%s<h3>%s</h3><span>%d prodotti</span></a>' % (cat_url(c), art(CAT_IMG[c], bg, fg), esc(c), cat_count(c))
    return '''<section class="section container reveal" aria-labelledby="h-cat">
  <div class="sec-head"><h2 id="h-cat">Acquista per categoria</h2><a class="link-u" href="categoria-tutti.html">Tutte le categorie</a></div>
  %s
</section>''' % carousel(cards, 'Categorie')


def deals():
    tabs = [
        ('Offerte multiple', P('018', '177', '013', '246', '279', '208', '120')),
        ('Sotto i 5 €', P('030', '123', '084', '045', '055', '131', '027', '060')),
        ('Più in vetrina', P('086', '001', '015', '027', '099', '108', '229', '074')),
    ]
    side, panels = '', ''
    for k, (label, prods) in enumerate(tabs, 1):
        bg, fg = pal(prods[0])
        side += ('<button class="tab-v" role="tab" id="tv%d" aria-controls="dp%d" aria-selected="%s" tabindex="%d">%s<span>%s</span>%s</button>\n        '
                 % (k, k, 'true' if k == 1 else 'false', 0 if k == 1 else -1, art(prods[0]['image'][0], bg, fg), label, U('right')))
        panels += '<div role="tabpanel" id="dp%d" aria-labelledby="tv%d" class="panel"%s>%s</div>\n      ' % (
            k, k, '' if k == 1 else ' hidden', carousel(''.join(pcard(p) for p in prods), 'Prodotti in offerta'))
    return '''<section class="section container reveal" aria-labelledby="h-deals" data-tabs>
  <div class="deals">
    <div class="deals__side">
      <h2 id="h-deals">Offerte e prezzi piccoli</h2>
      <div class="deals__sub"><span>Una selezione dal nostro catalogo</span></div>
      <div class="tabs-v" role="tablist" aria-label="Collezioni in offerta">
        %s</div>
      <a class="link-u" href="#">Vedi tutto</a>
    </div>
    <div class="deals__main">
      %s</div>
  </div>
</section>''' % (side, panels)


def banner_winter():
    win = [p for p in PRODUCTS if p['category'] == 'Biancheria letto' and p['subcategory'] in ('Trapunte', 'Coperte', 'Plaid', 'Copriletti') and p['season'] == 'inverno']
    return '''<section class="container reveal" aria-label="Promozione inverno">
  <div class="banner banner--wine">
    <div class="banner__dots"></div>
    <div class="banner__text">
      <span class="slide__eyebrow">Aspettando l&rsquo;inverno</span>
      <h2>Che arrivi<br>il freddo</h2>
      <p>Trapunte, coperte, plaid e copriletti trapuntati: %d modelli per scaldare la casa, a partire da %s.</p>
      <a class="btn" href="#">Scopri le offerte%s</a>
    </div>
    <div class="banner__art"><img src="%s" alt="" loading="lazy" decoding="async"></div>
  </div>
</section>''' % (len(win), eur_s(min(p['price'] for p in win if p['price'])), ARROW, u(IMG['plaid'][0], 900))


def infocards():
    items = [('018', '3 trapunte a 99,99 €', 'Trapunta Regina con balze e fiocchi', IMG['trap'][0]),
             ('246', '3 teli mare a 10 €', 'Teli 100% cotone con borsetta', IMG['telo'][0]),
             ('013', '3 tappeti a 9,99 €', 'Tappeto sardo 50×80 cm', IMG['tappeti'][1]),
             ('208', '2 lampade a 5 €', 'Lampada da tavolo LED ricaricabile', IMG['casa'][0]),
             ('216', 'La terza è in omaggio', 'Maglie Navigare girocollo', P216_IMAGES[0]),
             ('279', '3 borse mare a 9,99 €', 'Fantasie digitali', IMG['borsa'][0])]
    cards = ''
    for pid, t, s, img in items:
        bg, fg = pal(BY_ID['P' + pid])
        cards += ('<a class="infocard" href="#">%s<div class="infocard__t"><strong>%s</strong><span>%s</span><span class="link-u">Scopri di più</span></div></a>'
                  % (art(img, bg, fg), t, s))
    return '<section class="section container reveal" aria-label="Offerte speciali">\n  %s\n</section>' % carousel(cards, 'Promozioni')


def showcase():
    p = BY_ID['P018']
    tids = [IMG['trap'][0], IMG['trap'][1], IMG['trap'][2], IMG['lenz'][1]]
    hexes = [COLORS[c] for c in p['colors']]
    fgs = ['#7a5b2e', '#5b4a3b', '#6b5f46', '#2f7a5e', '#7a5b2e']
    bg, fg = pal(p)
    thumbs = ''.join('<button data-thumb aria-current="%s" aria-label="Foto %d">%s</button>' % ('true' if k == 0 else 'false', k + 1, art(t, bg, fg))
                     for k, t in enumerate(tids))
    sws = ''.join('<button class="sw" style="--c:%s" data-bg="%s" data-fg="%s" aria-label="%s" aria-pressed="%s"></button>'
                  % (x, x, fgs[k], esc(p['colors'][k].capitalize()), 'true' if k == 0 else 'false') for k, x in enumerate(hexes))
    three = ('%.2f' % (3 * p['price'])).replace('.', ',')
    return '''<section class="section container reveal" aria-labelledby="h-show">
  <div class="showcase" data-showcase data-product>
    <div class="gallery">
      <div class="gallery__main" data-gal-main style="--bg:%(bg)s;--fg:%(fg)s"><span class="badge">3 a 99,99 €</span>
        <div class="art"><img src="%(img900)s" alt="%(t)s" decoding="async"></div></div>
      <div class="gallery__thumbs">
        %(thumbs)s
      </div>
    </div>
    <div class="pdp">
      <span class="pdp__vendor">Il Corredo 2 · Biancheria letto · Trapunte</span>
      <h2 id="h-show">%(t)s</h2>
      <p>Trapunta matrimoniale invernale con bordo a balze e fiocchi, per un letto morbido e curato nei dettagli.</p>
      <ul class="ticks">
        <li>%(check)sBordo a balze con fiocchi</li>
        <li>%(check)sDisponibile in %(ncol)d colori: beige, tortora, panna, tiffany e biscotto</li>
        <li>%(check)sOfferta: 3 trapunte a 99,99 € invece di %(three)s €</li>
      </ul>
      <div><span class="opt__label">Colore: <span data-sw-name>Beige</span></span>
        <div class="sw-row" role="group" aria-label="Colore">
          %(sws)s
        </div></div>
      <div class="pdp__price"><span class="price__now" style="color:var(--red)">%(price)s</span><span class="badge">3 a €99,99</span></div>
      <div class="buyrow">
        <div class="qty"><button data-qty-step="-1" aria-label="Diminuisci">%(minus)s</button><output data-qty-out>1</output><button data-qty-step="1" aria-label="Aumenta">%(plus)s</button></div>
        %(btn)s
      </div>
      <div class="pdp__meta">
        <div>%(check)sDisponibile nel negozio di San Giorgio a Cremano</div>
        <div><svg class="i" viewBox="0 0 64 64" aria-hidden="true"><use href="#i-truck"/></svg>Consegna in 2–4 giorni lavorativi</div>
        <div><svg class="i" viewBox="0 0 64 64" aria-hidden="true"><use href="#i-return"/></svg>Reso gratuito entro 30 giorni</div>
      </div>
    </div>
  </div>
</section>''' % dict(bg=bg, fg=fg, img900=u(tids[0], 900), t=esc(p['title']), thumbs=thumbs, check=U('check'), ncol=len(p['colors']),
                     three=three, sws=sws, price=eur(p['price']), minus=U('minus'), plus=U('plus'),
                     btn=add_btn(p, 'btn btn--red', 'data-qty data-open-cart '))


def promo_occ():
    occ = [('moon', 'Per la notte', 'Pigiami e notte'), ('bed', 'Per il letto', 'Biancheria letto'), ('sofa', 'Per la casa', 'Casa e arredo'),
           ('towel', 'Per il bagno', 'Bagno'), ('sock', 'Per i piedi', 'Calze e calzini'), ('shirt', 'Ogni giorno', 'Abbigliamento donna'),
           ('star', 'Per il mare', 'Mare e costumi'), ('heart', 'Per i piccoli', 'Neonato')]
    grid = ''.join('<a class="occ" href="%s"><svg class="i" viewBox="0 0 64 64" aria-hidden="true"><use href="#i-%s"/></svg>%s</a>' % (cat_url(c), i, t) for i, t, c in occ)
    return '''<section class="container reveal" aria-label="Promozioni">
  <div class="pgrid">
    <div class="banner banner--sage" style="grid-template-columns:1fr">
      <div class="banner__dots"></div>
      <div class="banner__text">
        <span class="slide__eyebrow">Casa a piccoli prezzi</span>
        <h3>Tappeti da %s<br>plaid da %s</h3>
        <p>Tappeti, zerbini, cuscini per sedie e tutto per rinnovare casa senza spendere molto.</p>
        <a class="btn" href="#">Acquista ora%s</a>
      </div>
      <div class="banner__art"><img src="%s" alt="" loading="lazy" decoding="async"></div>
    </div>
    <div class="occasions">
      <h3>Acquista per occasione</h3>
      <div class="occasions__grid">%s</div>
    </div>
  </div>
</section>''' % (eur_s(cat_min('Casa e arredo', 'Tappeti')), eur_s(cat_min('Biancheria letto', 'Plaid')), ARROW, u(IMG['casa'][1], 900), grid)


def round_():
    items = [('Pigiami e notte', 'Pigiami'), ('Biancheria letto', 'Copriletti'), ('Biancheria letto', 'Trapunte'), ('Intimo donna', 'Reggiseni'),
             ('Biancheria letto', 'Lenzuola'), ('Bagno', 'Asciugamani'), ('Calze e calzini', 'Calzini'), ('Cucina e tavola', 'Tovaglie'),
             ('Casa e arredo', 'Tappeti'), ('Calzature', 'Pantofole'), ('Mare e costumi', 'Teli mare')]
    cards = ''
    for k, (c, s) in enumerate(items):
        rep = next(p for p in PRODUCTS if p['category'] == c and p['subcategory'] == s)
        bg, fg = PALETTES[k % len(PALETTES)]
        cards += '<a class="round" href="%s">%s<h3>%s</h3></a>' % (cat_url(c, s), art(rep['image'][0], bg, fg), esc(s))
    return '''<section class="section container reveal" aria-labelledby="h-round">
  <div class="sec-head"><h2 id="h-round">Cerca per tipo di prodotto</h2></div>
  %s
</section>''' % carousel(cards, 'Tipi di prodotto')


def picks():
    tabs = [('Intimo', 'blush', 'Comfort per tutta la famiglia', IMG['intimoD'][0], P('033', '259', '142', '241')),
            ('Pigiami', 'navy', 'Notti calde e morbide', IMG['pigD'][1], P('126', '042', '252', '010')),
            ('Letto', 'sky', 'Un letto da sogno', IMG['letto'][1], P('097', '249', '201', '264')),
            ('Bagno', 'sage', 'Bagno in ordine', IMG['asciug'][0], P('043', '044', '275', '089'))]
    head = ''.join('<button class="tab-h" role="tab" id="pt%d" aria-controls="pc%d" aria-selected="%s" tabindex="%d">%s</button>'
                   % (k, k, 'true' if k == 1 else 'false', 0 if k == 1 else -1, t[0]) for k, t in enumerate(tabs, 1))
    panels = ''
    for k, (name, theme, ttl, img, prods) in enumerate(tabs, 1):
        panels += '''  <div role="tabpanel" id="pc%d" aria-labelledby="pt%d" class="panel promocol"%s>
  <div class="banner banner--%s" style="grid-template-columns:1fr"><div class="banner__dots"></div>
  <div class="banner__art"><img src="%s" alt="" loading="lazy" decoding="async"></div>
  <div class="banner__text"><span class="slide__eyebrow">%s</span><h3 style="font-size:28px">%s</h3><a class="btn btn--light" href="#">Vedi tutto%s</a></div></div>
  <div class="pgrid-products">%s</div>
</div>
''' % (k, k, '' if k == 1 else ' hidden', theme, u(img, 900), name, ttl, ARROW, ''.join(pcard(p) for p in prods))
    return '''<section class="section container reveal" aria-labelledby="h-pc" data-tabs>
  <div class="sec-head"><h2 id="h-pc">Scelti per te</h2><a class="link-u" href="#">Vedi tutto</a></div>
  <div class="tabs-h" role="tablist" aria-label="Collezioni">%s</div>
%s</section>''' % (head, panels)


def banners2():
    return '''<section class="container reveal" aria-label="Promozioni">
  <div class="pgrid">
    <div class="banner banner--blush" style="grid-template-columns:1fr"><div class="banner__dots"></div>
      <div class="banner__text"><span class="slide__eyebrow">Reggiseni da</span><h3 style="font-size:clamp(54px,14vw,84px);line-height:.95">%s</h3><p>Con e senza ferretto, a fascia, taglie forti: %d modelli di reggiseni.</p><a class="btn" href="#">Acquista ora%s</a></div>
      <div class="banner__art"><img src="%s" alt="" loading="lazy" decoding="async"></div></div>
    <div class="banner banner--sky" style="grid-template-columns:1fr"><div class="banner__dots"></div>
      <div class="banner__text"><span class="slide__eyebrow">Biancheria letto</span><h3>Un letto da<br>sogno</h3><p>%d prodotti tra lenzuola, completi letto, trapunte e copriletti.</p><a class="btn" href="#">Scopri la collezione%s</a></div>
      <div class="banner__art"><img src="%s" alt="" loading="lazy" decoding="async"></div></div>
  </div>
</section>''' % (eur_s(cat_min('Intimo donna', 'Reggiseni')), CATS['Intimo donna']['Reggiseni'], ARROW, u(IMG['intimoD'][1], 900),
                 cat_count('Biancheria letto'), ARROW, u(IMG['lenz'][1], 900))


def depts():
    out = ''
    for c in ['Biancheria letto', 'Abbigliamento donna', 'Intimo donna', 'Pigiami e notte', 'Bagno', 'Casa e arredo']:
        bg, fg = cpal(c)
        lis = ''.join('<li><a href="%s">%s</a></li>' % (cat_url(c, s), esc(s)) for s in subs(c, 6))
        out += '<div class="dept"><div class="dept__head">%s<h3>%s</h3></div><ul>%s</ul><a class="link-u" href="%s">Vedi tutto</a></div>' % (art(CAT_IMG[c], bg, fg), esc(c), lis, cat_url(c))
    return '''<section class="section container reveal" aria-labelledby="h-dept">
  <div class="sec-head"><div><h2 id="h-dept">Tutto il necessario, in un solo negozio</h2><p>Dal guardaroba alla camera da letto, dal bagno alla spiaggia.</p></div></div>
  <div class="depts">%s</div>
</section>''' % out


def hset():
    prods = P('016', '019', '024', '042', '054', '266')
    return '''<section class="section container reveal" aria-labelledby="h-set">
  <div class="sec-head"><h2 id="h-set">Il meglio della stagione</h2><a class="link-u" href="#">Vedi tutto</a></div>
  <div class="hset">
    <div class="banner banner--ink hset__banner" style="grid-template-columns:1fr"><div class="banner__dots"></div>
      <div class="banner__art"><img src="%s" alt="" loading="lazy" decoding="async"></div>
      <div class="banner__text"><span class="slide__eyebrow">Scelti dal negozio</span><h3 style="font-size:30px">Pronti per l&rsquo;inverno, a prezzi piccoli</h3><a class="btn" href="#">Scopri%s</a></div></div>
    <div class="hlist">%s</div>
  </div>
</section>''' % (u(IMG['casa'][1], 900), ARROW, ''.join(hitem(p) for p in prods))


def brands():
    cnt, cats_, first = collections.Counter(), collections.defaultdict(collections.Counter), {}
    for p in PRODUCTS:
        for b in [x.strip() for x in p['brand'].split(',') if x.strip()]:
            cnt[b] += 1
            cats_[b][p['category']] += 1
            first.setdefault(b, p)
    cards = ''
    for k, (b, n) in enumerate(cnt.most_common(8)):
        p = first[b]
        bg, fg = PALETTES[k % len(PALETTES)]
        cards += ('<div class="arr">%s<p><strong>%s</strong><br><span style="color:var(--muted);font-size:14px">%d prodott%s · %s</span></p>'
                  '<a class="btn btn--sm btn--ghost" href="#" style="width:auto;align-self:flex-start">Scopri</a></div>'
                  % (art(p['image'][0], bg, fg, cls='art--wide'), esc(b), n, 'o' if n == 1 else 'i', esc(cats_[b].most_common(1)[0][0].lower())))
    return '''<section class="section container reveal" aria-labelledby="h-arr">
  <div class="sec-head"><div><h2 id="h-arr">Le marche che trovi da noi</h2><p>%d marche, tra nomi conosciuti e linee del negozio.</p></div></div>
  %s
</section>''' % (len(cnt), carousel(cards, 'Marche'))


def payments():
    return (ROOT / 'tools/payments.html').read_text(encoding='utf-8')


def footer_cats():
    return ''.join('<li><a href="%s">%s</a></li>' % (cat_url(c), esc(c)) for c in
                   ['Intimo donna', 'Abbigliamento donna', 'Pigiami e notte', 'Biancheria letto', 'Bagno', 'Casa e arredo', 'Mare e costumi'])


def build():
    t = (ROOT / 'tools/template.html').read_text(encoding='utf-8')
    parts = dict(NAV_ITEMS=nav_items(), DRAWER_LINKS=drawer_links(), SEARCH_OPTIONS=search_options(), HERO_SLIDES=hero_slides(),
                 CATEGORIES=categories(), DEALS=deals(), BANNER_WINTER=banner_winter(), INFOCARDS=infocards(), SHOWCASE=showcase(),
                 PROMO_OCC=promo_occ(), ROUND=round_(), PICKS=picks(), BANNERS2=banners2(), DEPTS=depts(), HSET=hset(),
                 BRANDS=brands(), FOOTER_CATS=footer_cats(), PAYMENTS=payments())
    for k, v in parts.items():
        t = t.replace('{{%s}}' % k, v)
    assert '{{' not in t, re.findall(r'\{\{\w+\}\}', t)
    (ROOT / 'index.html').write_text(t, encoding='utf-8')
    cat = [dict(p, image=['https://images.unsplash.com/photo-' + i for i in p['image']]) for p in PRODUCTS]
    (ROOT / 'data/catalog.json').write_text(json.dumps(cat, ensure_ascii=False, indent=1), encoding='utf-8')
    print('index.html %d bytes · %d products · %d categories' % (len(t.encode()), len(PRODUCTS), len(CATS)))


if __name__ == '__main__':
    build()
