#!/usr/bin/env python3
"""Category pages (categoria-*.html) and the product page (prodotto.html).

Run through tools/build.py. Reuses the header / drawers / footer of tools/template.html and the
product helpers of build_home.py.
"""
import json, re, datetime
import build_home as H
from build_home import (ROOT, esc, PRODUCTS, BY_ID, CATS, COLORS, CAROUSEL_ORDER, CAT_IMG, IMG, U, ICO, ARROW,
                        eur, eur_s, price_html, swatches, badge, vendor, pcard, carousel, art, u, pal, slug,
                        cat_url, product_url, cat_count, cat_min, subs, P216_IMAGES, PALETTES)

STOCK_LABEL = {'in': 'Disponibile', 'low': 'Ultimi pezzi', 'out': 'Esaurito'}
AUD = {'donna': 'Donna', 'uomo': 'Uomo', 'uomo e donna': 'Uomo e donna', 'bimbi': 'Bambini', 'neonato': 'Neonato', 'casa': 'Casa'}
SEASON = {"tutto l'anno": "Tutto l'anno", 'inverno': 'Inverno', 'estate': 'Estate'}
PRICE_BANDS = [('0-5', 'Fino a 5 €', 0, 5), ('5-10', 'Da 5 a 10 €', 5, 10), ('10-20', 'Da 10 a 20 €', 10, 20), ('20-999', 'Oltre 20 €', 20, 999)]
WA = 'https://wa.me/393533545919'


def split_page():
    t = (ROOT / 'tools/template.html').read_text(encoding='utf-8')
    a = t.index('<main id="main">')
    b = t.index('</main>')
    head, tail = t[:a], t[b + len('</main>'):]
    for k, v in dict(NAV_ITEMS=H.nav_items(), DRAWER_LINKS=H.drawer_links(), SEARCH_OPTIONS=H.search_options(),
                     FOOTER_CATS=H.footer_cats(), PAYMENTS=H.payments()).items():
        head, tail = head.replace('{{%s}}' % k, v), tail.replace('{{%s}}' % k, v)
    return head, tail


def page(title, desc, main, script, bodyclass=''):
    head, tail = split_page()
    head = re.sub(r'<title>.*?</title>', '<title>%s</title>' % esc(title), head, flags=re.S)
    head = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + esc(desc), head)
    head = head.replace('</head>', '<link rel="stylesheet" href="css/pages.css?v=2">\n</head>')
    tail = tail.replace('<script src="js/main.js?v=8"></script>', '<script src="js/main.js?v=8"></script>\n<script src="js/%s?v=2"></script>' % script)
    return head + '<main id="main">\n' + main + '\n</main>' + tail


def crumbs(items):
    out = []
    for k, (label, url) in enumerate(items):
        last = k == len(items) - 1
        out.append('<span aria-current="page">%s</span>' % esc(label) if last else '<a href="%s">%s</a>' % (url, esc(label)))
    return '<nav class="crumbs" aria-label="Briciole di pane">%s</nav>' % '<i aria-hidden="true">›</i>'.join(out)


# ───────────────────────── collections ─────────────────────────
def is_offer(p):
    return bool(p['compareAt'] or re.match(r'\d \w+ [\d,]+ €', p['bundle']) or 'omaggio' in p['bundle'])


def collections():
    cols = []
    for c in CAROUSEL_ORDER + ['Scuola']:
        items = [p for p in PRODUCTS if p['category'] == c]
        cols.append(dict(slug=slug(c), name=c, items=items, group=lambda p: p['subcategory'], group_label='Sottocategoria',
                         img=CAT_IMG.get(c, IMG['bimbi'][0]), kind='category'))
    cols.append(dict(slug='offerte', name='Offerte', items=[p for p in PRODUCTS if is_offer(p)], group=lambda p: p['category'],
                     group_label='Categoria', img=IMG['trap'][0], kind='offers'))
    cols.append(dict(slug='tutti', name='Tutte le categorie', items=list(PRODUCTS), group=lambda p: p['category'],
                     group_label='Categoria', img=IMG['letto'][1], kind='all'))
    return cols


def card_desc(p):
    bits = []
    if p['sizes']:
        bits.append('Taglie: %s' % p['sizes'])
    cols = [c for c in p['colors']]
    if cols:
        bits.append('Colori: %s' % ', '.join(cols))
    if p['packQty'] > 1:
        bits.append('Confezione da %d' % p['packQty'])
    if p['bundle']:
        bits.append('Offerta: %s' % p['bundle'])
    if p['brand']:
        bits.append('Marca: %s' % p['brand'])
    return ' · '.join(bits) or 'Disponibile nel negozio di San Giorgio a Cremano.'


def needs_options(p):
    named = [c for c in p['colors'] if c != 'vari colori']
    return bool(p['sizes']) or len(named) >= 2


def cat_card(p, grp, idx):
    bg, fg = pal(p)
    named = [c for c in p['colors'] if c in COLORS]
    colors = ','.join(slug(c) for c in p['colors'])
    stock = p['stock']
    badges = ''
    if is_offer(p):
        b = badge(p)
        badges += b or '<span class="badge">Offerta</span>'
    if stock == 'out':
        badges += '<span class="badge badge--out">Esaurito</span>'
    img2 = ''
    if len(p['image']) > 1 and p['image'][1] != p['image'][0]:
        img2 = '<img class="alt" src="%s" alt="" loading="lazy" decoding="async">' % u(p['image'][1])
    url = product_url(p)
    if p['price'] is None:
        price = '<div class="price price--ask"><span class="price__ask">Prezzo in negozio</span></div>'
        btn = '<a class="btn btn--sm btn--ghost" href="%s?text=%s" target="_blank" rel="noopener">Chiedi il prezzo</a>' % (WA, esc('Ciao! Vorrei il prezzo di: ' + p['title']).replace(' ', '%20'))
    elif stock == 'out':
        price = price_html(p)
        btn = '<button class="btn btn--sm" disabled>Esaurito</button>'
    elif needs_options(p):
        price = price_html(p)
        btn = '<a class="btn btn--sm" href="%s">Scegli le opzioni</a>' % url
    else:
        price = price_html(p)
        btn = H.add_btn(p)
    return '''<article class="pcard pcard--cat%(oos)s" data-product data-i="%(i)d" data-id="%(id)s" data-sub="%(g)s" data-brand="%(brand)s" data-colors="%(colors)s" data-price="%(price)s" data-aud="%(aud)s" data-season="%(season)s" data-stock="%(stock)s" data-offer="%(offer)d" data-title="%(title)s">
  <div class="pcard__media">
    <a href="%(url)s" aria-label="%(title)s">%(art)s</a>
    <div class="badges">%(badges)s</div>
    <button class="wish" aria-label="Aggiungi ai preferiti" aria-pressed="false">%(heart)s</button>
  </div>
  <div class="pcard__body">
    <span class="pcard__vendor">%(vendor)s</span>
    <h3 class="pcard__title"><a href="%(url)s">%(title)s</a></h3>
    <p class="pcard__desc">%(desc)s</p>
    %(sw)s
    %(priceh)s
    <p class="stock stock--%(stock)s"><i></i>%(slabel)s</p>
    %(btn)s
  </div>
</article>''' % dict(oos=' is-out' if stock == 'out' else '', i=idx, id=p['id'], g=slug(grp), brand=esc(slug(p['brand'].split(',')[0])) if p['brand'] else '',
                     colors=colors, price='' if p['price'] is None else p['price'], aud=slug(p['audience']), season=slug(p['season']),
                     stock=stock, offer=1 if is_offer(p) else 0, title=esc(p['title']), url=url,
                     art=art(p['image'][0], bg, fg).replace('</div>', img2 + '</div>'), badges=badges, heart=U('heart'),
                     vendor=vendor(p), desc=esc(card_desc(p)), sw=swatches(p), priceh=price, slabel=STOCK_LABEL[stock], btn=btn)


def facet_checks(name, label, options):
    """options: list of (value, label, count, extra_html)"""
    if len(options) < 2:
        return ''
    lis = ''.join('<li><label class="check"><input type="checkbox" data-f="%s" value="%s"><span class="check__box"></span>%s<small>%d</small></label></li>'
                  % (name, esc(v), extra + esc(l), n) for v, l, n, extra in options)
    return '<details class="fgroup" open><summary>%s</summary><ul class="fgroup__list">%s</ul></details>' % (label, lis)


def filters_html(col):
    items = col['items']
    g = col['group']
    cnt = lambda key: __import__('collections').Counter(key(p) for p in items)
    subs_ = cnt(g)
    sub_opts = [(slug(k), k, n, '') for k, n in subs_.most_common()]
    brand_c = __import__('collections').Counter(p['brand'].split(',')[0] for p in items if p['brand'])
    brand_opts = [(slug(k), k, n, '') for k, n in brand_c.most_common()]
    colour_c = __import__('collections').Counter()
    for p in items:
        for c in p['colors']:
            colour_c[c] += 1
    col_opts = []
    for k, n in colour_c.most_common():
        if k == 'vari colori':
            sw = '<i class="sw-dot multi"></i>'
        elif k in COLORS:
            sw = '<i class="sw-dot" style="--c:%s"></i>' % COLORS[k]
        else:
            continue
        col_opts.append((slug(k), k.capitalize(), n, sw))
    price_opts = []
    for val, lab, lo, hi in PRICE_BANDS:
        n = sum(1 for p in items if p['price'] is not None and lo <= p['price'] < hi) if hi != 999 else sum(1 for p in items if p['price'] is not None and p['price'] >= lo)
        if n:
            price_opts.append((val, lab, n, ''))
    aud_c = cnt(lambda p: p['audience'])
    aud_opts = [(slug(k), AUD.get(k, k), n, '') for k, n in aud_c.most_common()]
    sea_c = cnt(lambda p: p['season'])
    sea_opts = [(slug(k), SEASON.get(k, k), n, '') for k, n in sea_c.most_common()]
    offers = sum(1 for p in items if is_offer(p))
    toggles = '''<label class="switch"><input type="checkbox" data-f="avail"><span class="switch__ui"></span>Solo prodotti disponibili</label>'''
    if offers and col['kind'] != 'offers':
        toggles += '''<label class="switch"><input type="checkbox" data-f="offer"><span class="switch__ui"></span>Solo in offerta <small>(%d)</small></label>''' % offers
    body = toggles + facet_checks('sub', col['group_label'], sub_opts) + facet_checks('price', 'Prezzo', price_opts) + facet_checks('brand', 'Marca', brand_opts) \
        + facet_checks('color', 'Colore', col_opts) + facet_checks('aud', 'Per chi', aud_opts) + facet_checks('season', 'Stagione', sea_opts)
    return '''<aside class="drawer filters" id="filters" aria-hidden="true" aria-label="Filtri">
  <div class="drawer__head"><h2>Filtri</h2><button class="icon-btn" data-close aria-label="Chiudi">%(x)s</button></div>
  <form class="drawer__body filters__body" data-filters onsubmit="return false">%(body)s</form>
  <div class="filters__foot"><button class="btn btn--ghost" type="button" data-reset>Azzera</button><button class="btn" type="button" data-close>Mostra <span data-show-n>%(n)d</span> prodotti</button></div>
</aside>''' % dict(x=U('x'), body=body, n=len(items))


def other_cats(current):
    cards = ''
    for k, c in enumerate([c for c in CAROUSEL_ORDER if c != current]):
        bg, fg = PALETTES[k % len(PALETTES)]
        cards += '<a class="round" href="%s">%s<h3>%s</h3></a>' % (cat_url(c), art(CAT_IMG[c], bg, fg), esc(c))
    return '''<section class="section container reveal" aria-labelledby="h-others">
  <div class="sec-head"><h2 id="h-others">Continua a scoprire</h2><a class="link-u" href="categoria-tutti.html">Tutte le categorie</a></div>
  %s
</section>''' % carousel(cards, 'Altre categorie')


FAQ = [('Posso ritirare l&rsquo;ordine in negozio?', 'Sì: ordina online e ritira gratuitamente nel negozio di Via San Martino 58, San Giorgio a Cremano.'),
       ('Quanto costa la spedizione?', 'La spedizione è gratuita per ordini oltre 49 €. Sotto questa soglia il costo viene calcolato al checkout.'),
       ('Posso restituire un prodotto?', 'Hai 30 giorni per il reso. Scrivici su WhatsApp e ti guidiamo passo dopo passo.')]


def seo_text(col):
    items = col['items']
    priced = [p['price'] for p in items if p['price'] is not None]
    if col['kind'] == 'category':
        sub = ', '.join('%s (%d)' % (k.lower(), n) for k, n in __import__('collections').Counter(p['subcategory'] for p in items).most_common(6))
        brands = sorted({p['brand'].split(',')[0] for p in items if p['brand']})
        t = '<p>Nella categoria <strong>%s</strong> trovi %d prodotti: %s.</p>' % (esc(col['name']), len(items), esc(sub))
        t += '<p>I prezzi vanno da %s a %s.' % (eur_s(min(priced)), eur_s(max(priced))) if priced else ''
        t += (' Tra le marche: %s.' % esc(', '.join(brands[:8]))) if brands else ''
        t += '</p>' if priced else ''
        t += '<p>Vieni a provare i prodotti nel negozio di San Giorgio a Cremano oppure ordina online e ritira in negozio.</p>'
        return t
    if col['kind'] == 'offers':
        return '<p>Multipacchetti e promozioni del negozio: più pezzi allo stesso prezzo, terze maglie in omaggio e prezzi scontati rispetto al listino.</p>'
    return '<p>Tutto il catalogo del negozio: %d prodotti per lei, per lui, per i più piccoli e per la casa.</p>' % len(items)


def collection_page(col):
    items = col['items']
    n = len(items)
    priced = [p['price'] for p in items if p['price'] is not None]
    if col['kind'] == 'category':
        lead = ('%d prodotti, da %s a %s.' % (n, eur_s(min(priced)), eur_s(max(priced)))) if priced else '%d prodott%s: prezzi in negozio.' % (n, 'o' if n == 1 else 'i')
    elif col['kind'] == 'offers':
        lead = 'Multipacchetti, prezzi scontati e promozioni del negozio.'
    else:
        lead = 'Tutto il catalogo: %d prodotti in %d categorie.' % (n, len(CAROUSEL_ORDER) + 1)
    groups = __import__('collections').Counter(col['group'](p) for p in items)
    chips = '<button class="subchip is-active" type="button" data-chip="">Tutti<small>%d</small></button>' % n
    chips += ''.join('<button class="subchip" type="button" data-chip="%s">%s<small>%d</small></button>' % (slug(k), esc(k), c) for k, c in groups.most_common())
    cards = ''.join(cat_card(p, col['group'](p), i) for i, p in enumerate(items))
    bg, fg = ('#f5dcd3', '#b04a4a')
    crumb = [('Home', 'index.html')] + ([('Tutte le categorie', 'categoria-tutti.html')] if col['kind'] == 'category' else []) + [(col['name'], '#')]
    faq = ''.join('<details class="acc__item"><summary>%s</summary><div class="acc__body"><p>%s</p></div></details>' % (q, a) for q, a in FAQ)
    main = '''<section class="cat-hero">
  <div class="container">
    %(crumbs)s
    <div class="cat-hero__row">
      <div class="cat-hero__text"><h1>%(name)s</h1><p class="cat-hero__lead">%(lead)s</p></div>
      <div class="cat-hero__img">%(img)s</div>
    </div>
    <div class="subchips" role="group" aria-label="%(gl)s">%(chips)s</div>
  </div>
</section>
<section class="container catalog" data-catalog data-sub-default="%(sub)s">
  <div class="toolbar" data-toolbar>
    <button class="tb-filter" type="button" data-open="filters">%(filter_i)s<span>Filtri</span><b data-filter-n hidden>0</b></button>
    <p class="tb-total"><strong data-total>%(n)d</strong> prodotti</p>
    <label class="tb-sort"><span>Ordina per</span>
      <select data-sort aria-label="Ordina per">
        <option value="featured">In evidenza</option><option value="price-asc">Prezzo crescente</option><option value="price-desc">Prezzo decrescente</option>
        <option value="az">Nome A–Z</option><option value="za">Nome Z–A</option>
      </select></label>
    <div class="tb-layout" role="group" aria-label="Vista">
      <button type="button" data-layout="grid" aria-pressed="true" aria-label="Vista a griglia"><svg class="i" viewBox="0 0 24 24"><path d="M4 4h6v6H4zM14 4h6v6h-6zM4 14h6v6H4zM14 14h6v6h-6z"/></svg></button>
      <button type="button" data-layout="list" aria-pressed="false" aria-label="Vista a elenco"><svg class="i" viewBox="0 0 24 24"><path d="M4 6h16M4 12h16M4 18h16"/></svg></button>
    </div>
  </div>
  <div class="catalog__body">
    %(filters)s
    <div class="catalog__main">
      <div class="active-tags" data-active-tags></div>
      <div class="pgrid-cat" data-grid>%(cards)s</div>
      <div class="empty" data-empty hidden><strong>Nessun prodotto corrisponde ai filtri.</strong><p>Prova a rimuovere qualche filtro.</p><button class="btn" type="button" data-reset>Azzera i filtri</button></div>
      <div class="loadmore" data-loadmore>
        <p>Stai visualizzando <b data-shown>0</b> di <b data-total2>%(n)d</b> prodotti</p>
        <div class="loadmore__bar" aria-hidden="true"><i data-bar></i></div>
        <button class="btn btn--ghost" type="button" data-more>Carica altri prodotti</button>
      </div>
    </div>
  </div>
</section>
%(others)s
<section class="section container reveal" aria-labelledby="h-faq">
  <div class="cat-info">
    <div class="cat-info__text"><h2 id="h-faq">%(name)s</h2><div class="rte">%(seo)s</div></div>
    <div class="acc">%(faq)s</div>
  </div>
</section>''' % dict(crumbs=crumbs(crumb), name=esc(col['name']), lead=lead, img=art(col['img'], bg, fg, 700, lazy=False), gl=col['group_label'], chips=chips,
                     sub='', filter_i='<svg class="i" viewBox="0 0 24 24"><path d="M4 6h16M7 12h10M10 18h4"/></svg>', n=n, filters=filters_html(col),
                     cards=cards, others=other_cats(col['name']), seo=seo_text(col), faq=faq)
    title = '%s — Il Corredo 2' % col['name']
    desc = '%s %s Il Corredo 2, San Giorgio a Cremano.' % (col['name'], lead)
    return page(title, desc, main, 'category.js')


# ───────────────────────── product page ─────────────────────────
SIZES = ['S', 'M', 'L', 'XL', 'XXL']
# availability by colour and size: DEMO DATA (the sheet has no stock levels)
STOCK216 = {'nero': dict(S=12, M=20, L=8, XL=3, XXL=0), 'bianco': dict(S=0, M=15, L=9, XL=11, XXL=4), 'blu': dict(S=6, M=0, L=14, XL=7, XXL=2)}
COLOR_IMG = {'nero': 0, 'bianco': 2, 'blu': 4}


def product_page():
    p = BY_ID['P216']
    price = p['price']
    colors = [dict(key=c, name=c.capitalize(), hex=COLORS[c], img=COLOR_IMG[c]) for c in p['colors']]
    data = dict(id=p['id'], title=p['title'], price=price, colors=colors, sizes=SIZES, stock=STOCK216,
                images=[u(i, 1000) for i in P216_IMAGES], thumbs=[u(i, 200) for i in P216_IMAGES], whatsapp=WA)
    bg, fg = pal(p)
    thumbs = ''.join('<button type="button" class="pp__thumb%s" data-thumb="%d" aria-label="Foto %d">%s</button>'
                     % (' is-active' if k == 0 else '', k, k + 1, art(i, bg, fg, 200, lazy=False)) for k, i in enumerate(P216_IMAGES))
    swatch_btns = ''.join('<button type="button" class="sw" style="--c:%s" data-color="%s" aria-label="%s" aria-pressed="%s"></button>'
                          % (c['hex'], c['key'], c['name'], 'true' if k == 0 else 'false') for k, c in enumerate(colors))
    size_btns = ''.join('<button type="button" class="chip" data-size="%s" aria-pressed="false">%s</button>' % (s, s) for s in SIZES)
    sets = 2 * price
    three = 3 * price
    row_tpl = '''<div class="brow" data-brow="%d"><span class="brow__n">Maglia %d%s</span>
          <select data-brow-color aria-label="Colore maglia %d">%s</select>
          <select data-brow-size aria-label="Taglia maglia %d"><option value="">Taglia</option>%s</select></div>'''
    color_opts = ''.join('<option value="%s">%s</option>' % (c['key'], c['name']) for c in colors)
    size_opts = ''.join('<option value="%s">%s</option>' % (s, s) for s in SIZES)
    rows = ''.join(row_tpl % (i, i + 1, ' <em>in omaggio</em>' if i == 2 else '', i + 1, color_opts, i + 1, size_opts) for i in range(3))
    rec = [q for q in PRODUCTS if q['category'] in ('Abbigliamento uomo', 'Intimo uomo') and q['price'] and q['stock'] != 'out' and q['id'] != 'P216'][:8]
    rec_cards = ''.join(pcard(q) for q in rec)
    others = []
    for k, c in enumerate(['Abbigliamento uomo', 'Intimo uomo', 'Pigiami e notte', 'Sport e tute', 'Calze e calzini', 'Biancheria letto']):
        b2, f2 = PALETTES[k % len(PALETTES)]
        others.append('<a class="round" href="%s">%s<h3>%s</h3></a>' % (cat_url(c), art(CAT_IMG[c], b2, f2), esc(c)))
    specs = [('Codice articolo', p['id']), ('Marca', p['brand']), ('Categoria', p['category']), ('Tipo', 'T-shirt girocollo'), ('Taglie', 'S, M, L, XL, XXL'),
             ('Colori', ', '.join(c.capitalize() for c in p['colors'])), ('Stagione', "Tutto l'anno"), ('Per chi', 'Uomo'), ('Offerta', 'Ne acquisti 2, la terza è in omaggio')]
    spec_rows = ''.join('<li><span>%s</span><div>%s</div></li>' % (esc(a), esc(b)) for a, b in specs)
    main = '''<div class="container pp-crumbs">%(crumbs)s</div>
<section class="container pp" data-pdp>
  <div class="pp__gallery">
    <div class="pp__thumbs" role="group" aria-label="Foto del prodotto">%(thumbs)s</div>
    <div class="pp__stage">
      <button type="button" class="pp__zoom" data-zoom aria-label="Ingrandisci la foto"><img data-main src="%(img0)s" alt="%(title)s" width="1000" height="1000"></button>
      <span class="badge">3x2</span>
      <button type="button" class="pp__nav pp__nav--prev" data-nav="-1" aria-label="Foto precedente">%(left)s</button>
      <button type="button" class="pp__nav pp__nav--next" data-nav="1" aria-label="Foto successiva">%(right)s</button>
      <span class="pp__count" data-count>1 / %(nimg)d</span>
    </div>
  </div>
  <div class="pp__info">
    <a class="pp__vendor" href="%(caturl)s">%(brand)s</a>
    <h1 class="pp__title">%(title)s</h1>
    <div class="pp__price"><span class="price__now" data-price>%(price)s</span><small data-price-note>IVA inclusa</small></div>
    <p class="pp__lead">T-shirt girocollo Navigare, un classico del guardaroba da portare da sola o sotto una camicia. Ne acquisti due, la terza è in omaggio.</p>
    <form class="pp__form" data-form onsubmit="return false" novalidate>
      <fieldset class="opt"><legend>Colore: <span data-color-name>Nero</span></legend>
        <div class="sw-row" role="group" aria-label="Colore">%(swatches)s</div></fieldset>
      <fieldset class="opt"><legend>Taglia: <span data-size-name>seleziona una taglia</span></legend>
        <div class="chips" role="group" aria-label="Taglia">%(sizes)s</div>
        <p class="opt__help">Non sai quale taglia scegliere? <a href="%(wa)s" target="_blank" rel="noopener">Scrivici su WhatsApp</a></p></fieldset>
      <fieldset class="opt"><legend>Scegli l&rsquo;offerta</legend>
        <div class="bundles" role="radiogroup" aria-label="Offerta">
          <label class="bundle is-active"><input type="radio" name="bundle" value="1" checked>
            <span class="bundle__main"><strong>1 maglia</strong><small>Prezzo singolo</small></span><span class="bundle__price">%(price)s</span></label>
          <label class="bundle"><input type="radio" name="bundle" value="3">
            <span class="bundle__tag">Offerta 3x2</span>
            <span class="bundle__main"><strong>3 maglie, ne paghi 2</strong><small>La terza è in omaggio: risparmi %(save)s</small></span>
            <span class="bundle__price">%(sets)s <s>%(three)s</s></span></label>
        </div>
        <div class="brows" data-brows hidden>%(rows)s</div>
      </fieldset>
      <div class="pp__stock" data-stock role="status" aria-live="polite"></div>
      <div class="pp__notify" data-notify hidden><label for="notify-email">Ti avvisiamo quando torna disponibile</label>
        <div class="nform__row"><input id="notify-email" type="email" placeholder="La tua email" autocomplete="email"><button class="btn btn--sm" type="button" data-notify-btn>Avvisami</button></div></div>
      <p class="pp__error" data-error role="alert" hidden></p>
      <div class="pp__buy" data-buy>
        <div class="qty" data-qty><button type="button" data-qty-step="-1" aria-label="Diminuisci">%(minus)s</button><output data-qty-out>1</output><button type="button" data-qty-step="1" aria-label="Aumenta">%(plus)s</button></div>
        <button type="button" class="btn btn--red" data-add-pdp>Aggiungi al carrello</button>
        <button type="button" class="pp__wish wish" aria-label="Aggiungi ai preferiti" aria-pressed="false">%(heart)s</button>
      </div>
      <a class="btn btn--ghost btn--block pp__wa" href="%(wa)s?text=Ciao!%%20Vorrei%%20informazioni%%20sulle%%20maglie%%20Navigare%%20girocollo" target="_blank" rel="noopener">%(chat)sChiedi informazioni su WhatsApp</a>
    </form>
    <ul class="pp__perks">
      <li>%(store)s<span><strong>Ritiro gratuito in negozio</strong><small data-pickup>Pronto in 2 ore a San Giorgio a Cremano</small></span></li>
      <li>%(truck)s<span><strong>Consegna a casa</strong><small data-eta>Spedizione gratuita oltre 49 €</small></span></li>
      <li>%(ret)s<span><strong>Reso facile entro 30 giorni</strong><small>Ti guidiamo su WhatsApp</small></span></li>
    </ul>
    <div class="pp__pay"><span>Pagamenti sicuri</span>%(pay)s</div>
    <div class="acc">
      <details class="acc__item" open><summary>Descrizione</summary><div class="acc__body"><p>Le maglie girocollo Navigare sono disponibili in nero, bianco e blu, dalla S alla XXL. Con l&rsquo;offerta 3x2, acquistandone due, la terza è in omaggio: ideale per fare scorta dei colori base.</p></div></details>
      <details class="acc__item"><summary>Taglie e vestibilità</summary><div class="acc__body"><p>Taglie disponibili: dalla S alla XXL. Se sei indeciso tra due taglie, scrivici su WhatsApp o passa in negozio per provarla.</p></div></details>
      <details class="acc__item"><summary>Spedizione e resi</summary><div class="acc__body"><p>Spedizione gratuita per ordini oltre 49 €. Consegna in 2–4 giorni lavorativi. Reso gratuito entro 30 giorni dall&rsquo;acquisto.</p></div></details>
      <details class="acc__item"><summary>Ritiro in negozio</summary><div class="acc__body"><p>Ordina online e ritira gratuitamente in Via San Martino 58, San Giorgio a Cremano. Ti avvisiamo appena l&rsquo;ordine è pronto.</p></div></details>
    </div>
    <div class="pp__share"><span>Condividi:</span>
      <a href="https://www.facebook.com/sharer/sharer.php?u=" target="_blank" rel="noopener" aria-label="Condividi su Facebook">%(fb)s</a>
      <a href="https://wa.me/?text=" target="_blank" rel="noopener" aria-label="Condividi su WhatsApp">%(chat)s</a>
      <button type="button" data-copy aria-label="Copia il link">%(link)s</button></div>
  </div>
</section>
<section class="container pp-details reveal" aria-labelledby="h-details">
  <div class="pp-details__grid">
    <div><h2 id="h-details">Descrizione</h2>
      <p>Le maglie girocollo <strong>Navigare</strong> sono un classico del guardaroba maschile: da indossare da sole o come primo strato sotto camicie e giacche.</p>
      <p>Sono disponibili in tre colori base (<strong>nero, bianco e blu</strong>) e in cinque taglie, dalla <strong>S alla XXL</strong>. Con l&rsquo;offerta del negozio, <strong>se ne acquisti due, la terza è in omaggio</strong>.</p></div>
    <div><h2>Informazioni prodotto</h2><ul class="specs">%(specs)s</ul></div>
  </div>
  <div class="pp-secure">
    <div><h3>%(shield)sAcquisto sicuro</h3><p>Paghi in totale sicurezza con carta o PayPal. Per qualsiasi dubbio, il negozio è a un messaggio di distanza.</p></div>
    <div class="pp-secure__pay">%(pay)s</div>
  </div>
</section>
<section class="section container reveal" aria-labelledby="h-rec">
  <div class="sec-head"><h2 id="h-rec">Potrebbe piacerti anche</h2><a class="link-u" href="%(caturl)s">Vedi tutto</a></div>
  %(rec)s
</section>
<section class="section container reveal" aria-labelledby="h-more">
  <div class="sec-head"><h2 id="h-more">Continua a scoprire</h2><a class="link-u" href="categoria-tutti.html">Tutte le categorie</a></div>
  %(more)s
</section>
<div class="sticky-atc" data-sticky hidden>
  <div class="sticky-atc__in container">
    <div class="sticky-atc__img"><img data-sticky-img src="%(img0t)s" alt="" width="56" height="56"></div>
    <div class="sticky-atc__t"><strong>%(title)s</strong><small data-sticky-var>Seleziona colore e taglia</small></div>
    <div class="sticky-atc__p" data-sticky-price>%(price)s</div>
    <button type="button" class="btn btn--red" data-sticky-add>Aggiungi al carrello</button>
  </div>
</div>
<div class="lightbox" data-lightbox hidden role="dialog" aria-modal="true" aria-label="Foto ingrandita">
  <button type="button" class="lightbox__close" data-lb-close aria-label="Chiudi">%(x)s</button>
  <button type="button" class="lightbox__nav lightbox__nav--prev" data-lb-nav="-1" aria-label="Foto precedente">%(left)s</button>
  <img data-lb-img src="%(img0)s" alt="%(title)s">
  <button type="button" class="lightbox__nav lightbox__nav--next" data-lb-nav="1" aria-label="Foto successiva">%(right)s</button>
  <span class="lightbox__count" data-lb-count></span>
</div>
<script type="application/json" id="pdp-data">%(json)s</script>''' % dict(
        crumbs=crumbs([('Home', 'index.html'), (p['category'], cat_url(p['category'])), (p['subcategory'], cat_url(p['category'], p['subcategory'])), (p['title'], '#')]),
        thumbs=thumbs, img0=data['images'][0], img0t=data['thumbs'][0], title=esc(p['title']), left=U('left'), right=U('right'), nimg=len(P216_IMAGES),
        caturl=cat_url(p['category']), brand=esc(p['brand']), price=eur(price), swatches=swatch_btns, sizes=size_btns, wa=WA, sets=eur(sets), three=eur(three),
        save=eur(price), rows=rows, minus=U('minus'), plus=U('plus'), heart=U('heart'), chat=ICO('chat').replace('class="ico"', 'class="i"'),
        store=ICO('store').replace('class="ico"', 'class="i"'), truck=ICO('truck').replace('class="ico"', 'class="i"'), ret=ICO('return').replace('class="ico"', 'class="i"'),
        shield=ICO('shield').replace('class="ico"', 'class="i"'), pay=H.payments(), fb=U('facebook'), link='<svg class="i" viewBox="0 0 24 24"><path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/></svg>',
        specs=spec_rows, rec=carousel(rec_cards, 'Altri prodotti'), more=carousel(''.join(others), 'Categorie'), x=U('x'), json=json.dumps(data, ensure_ascii=False))
    return page('%s — Il Corredo 2' % p['title'], 'Maglie Navigare girocollo in nero, bianco e blu, dalla S alla XXL. Ne acquisti 2, la terza è in omaggio. Il Corredo 2, San Giorgio a Cremano.', main, 'product.js')


def build():
    n = 0
    for col in collections():
        (ROOT / ('categoria-%s.html' % col['slug'])).write_text(collection_page(col), encoding='utf-8')
        n += 1
    (ROOT / 'prodotto.html').write_text(product_page(), encoding='utf-8')
    print('%d collection pages + prodotto.html' % n)
