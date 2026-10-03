/* Il Corredo 2 — product page: colour + size variants, 3x2 bundle, availability, gallery, sticky add-to-cart */
(function () {
  'use strict';
  var root = document.querySelector('[data-pdp]'); if (!root) return;
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var D = JSON.parse(document.getElementById('pdp-data').textContent);
  var fmt = function (n) { return '€' + n.toFixed(2).replace('.', ','); };
  var COLOR = {}; D.colors.forEach(function (c) { COLOR[c.key] = c; });
  var S = { color: D.colors[0].key, size: '', bundle: 1, qty: 1, img: 0 };

  var form = $('[data-form]', root), mainImg = $('[data-main]', root), countEl = $('[data-count]', root);
  var stockEl = $('[data-stock]', root), notify = $('[data-notify]', root), errEl = $('[data-error]', root);
  var addBtn = $('[data-add-pdp]', root), buyRow = $('[data-buy]', root), qtyOut = $('[data-qty-out]', root);
  var rowsWrap = $('[data-brows]', root), rows = $$('[data-brow]', root);
  var priceEl = $('[data-price]', root), priceNote = $('[data-price-note]', root);
  var sticky = $('[data-sticky]'), stickyVar = $('[data-sticky-var]'), stickyPrice = $('[data-sticky-price]'), stickyImg = $('[data-sticky-img]');
  var optColor = $$('.opt', root)[0], optSize = $$('.opt', root)[1];

  function stockOf(color, size) { var c = D.stock[color]; return c && size in c ? c[size] : null; }

  /* ---------- gallery ---------- */
  function setImg(i) {
    var n = D.images.length; S.img = (i + n) % n;
    mainImg.src = D.images[S.img];
    $$('[data-thumb]', root).forEach(function (t, k) { t.classList.toggle('is-active', k === S.img); });
    countEl.textContent = (S.img + 1) + ' / ' + n;
    stickyImg.src = D.thumbs[S.img];
    if (!lb.hidden) { lbImg.src = D.images[S.img]; lbCount.textContent = (S.img + 1) + ' / ' + n; }
  }
  $$('[data-thumb]', root).forEach(function (t) { t.addEventListener('click', function () { setImg(+t.getAttribute('data-thumb')); }); });
  $$('[data-nav]', root).forEach(function (b) { b.addEventListener('click', function () { setImg(S.img + +b.getAttribute('data-nav')); }); });

  /* lightbox */
  var lb = $('[data-lightbox]'), lbImg = $('[data-lb-img]'), lbCount = $('[data-lb-count]'), lbLast = null;
  function lbOpen() { lbLast = document.activeElement; lb.hidden = false; document.body.style.overflow = 'hidden'; setImg(S.img); $('[data-lb-close]').focus(); }
  function lbClose() { lb.hidden = true; document.body.style.overflow = ''; if (lbLast) lbLast.focus(); }
  $('[data-zoom]', root).addEventListener('click', lbOpen);
  $('[data-lb-close]').addEventListener('click', lbClose);
  lb.addEventListener('click', function (e) { if (e.target === lb) lbClose(); });
  $$('[data-lb-nav]').forEach(function (b) { b.addEventListener('click', function () { setImg(S.img + +b.getAttribute('data-lb-nav')); }); });
  document.addEventListener('keydown', function (e) {
    if (lb.hidden) return;
    if (e.key === 'Escape') lbClose(); else if (e.key === 'ArrowRight') setImg(S.img + 1); else if (e.key === 'ArrowLeft') setImg(S.img - 1);
  });

  /* ---------- options ---------- */
  function renderOptions() {
    $$('[data-color]', root).forEach(function (b) {
      var k = b.getAttribute('data-color');
      b.setAttribute('aria-pressed', k === S.color ? 'true' : 'false');
      var any = Object.keys(D.stock[k]).some(function (s) { return D.stock[k][s] > 0; });
      b.classList.toggle('is-out', !any);
    });
    $('[data-color-name]', root).textContent = COLOR[S.color].name;
    $$('[data-size]', root).forEach(function (b) {
      var s = b.getAttribute('data-size');
      b.setAttribute('aria-pressed', s === S.size ? 'true' : 'false');
      b.classList.toggle('is-out', stockOf(S.color, s) === 0);
    });
    $('[data-size-name]', root).textContent = S.size || 'seleziona una taglia';
  }

  function demand() {
    var map = {};
    if (S.bundle === 1) { if (S.size) map[S.color + '|' + S.size] = S.qty; return { map: map, missing: !S.size }; }
    var missing = false;
    rows.forEach(function (r) {
      var c = $('[data-brow-color]', r).value, s = $('[data-brow-size]', r).value;
      if (!s) { missing = true; return; }
      map[c + '|' + s] = (map[c + '|' + s] || 0) + 1;
    });
    return { map: map, missing: missing };
  }

  function business(days) {
    var d = new Date(), n = 0;
    while (n < days) { d.setDate(d.getDate() + 1); if (d.getDay() !== 0) n++; }
    return d;
  }
  var fd = new Intl.DateTimeFormat('it-IT', { weekday: 'short', day: 'numeric', month: 'short' });

  function renderStatus() {
    var dm = demand(), state = 'idle', msg;
    var worst = 'in', low = null;
    Object.keys(dm.map).forEach(function (k) {
      var p = k.split('|'), q = D.stock[p[0]][p[1]], need = dm.map[k];
      if (q === 0 || need > q) { worst = 'out'; msg = q === 0 ? 'Esaurito: ' + COLOR[p[0]].name + ' ' + p[1] : 'Disponibili solo ' + q + ' pezzi: ' + COLOR[p[0]].name + ' ' + p[1]; }
      else if (q <= 3 && worst !== 'out') { worst = 'low'; low = q; }
    });
    if (dm.missing && worst !== 'out') { state = 'idle'; msg = S.bundle === 1 ? 'Seleziona una taglia per vedere la disponibilità' : 'Scegli colore e taglia per tutte e 3 le maglie'; }
    else if (worst === 'out') { state = 'out'; }
    else if (worst === 'low') { state = 'low'; msg = 'Ultimi ' + low + ' pezzi disponibili'; }
    else { state = 'in'; msg = 'Disponibile'; }
    stockEl.setAttribute('data-state', state);
    stockEl.innerHTML = '<i></i><span>' + msg + '</span>';
    notify.hidden = state !== 'out';
    var out = state === 'out';
    addBtn.disabled = out; addBtn.textContent = out ? 'Esaurito' : 'Aggiungi al carrello';
    $('[data-pickup]', root).textContent = out ? 'Non disponibile per il ritiro in questa combinazione' : 'Pronto in 2 ore a San Giorgio a Cremano';
    $('[data-eta]', root).textContent = out ? 'Spedizione gratuita oltre 49 €' : 'Consegna stimata tra ' + fd.format(business(2)) + ' e ' + fd.format(business(4));
    renderSticky();
  }

  function renderPrice() {
    var p = D.price;
    if (S.bundle === 1) { priceEl.innerHTML = fmt(p); priceNote.textContent = 'IVA inclusa'; }
    else { priceEl.innerHTML = fmt(p * 2) + ' <s style="font-size:18px;font-weight:500;color:var(--muted)">' + fmt(p * 3) + '</s>'; priceNote.textContent = '3 maglie, la terza in omaggio'; }
    stickyPrice.textContent = S.bundle === 1 ? fmt(p) : fmt(p * 2);
  }

  function renderSticky() {
    if (S.bundle === 3) stickyVar.textContent = 'Offerta 3x2 · 3 maglie';
    else stickyVar.textContent = S.size ? COLOR[S.color].name + ' · taglia ' + S.size : 'Seleziona colore e taglia';
  }

  function clearErr() { errEl.hidden = true; optSize.classList.remove('is-invalid'); $$('select.is-invalid', root).forEach(function (s) { s.classList.remove('is-invalid'); }); }

  /* events: colour / size */
  $$('[data-color]', root).forEach(function (b) {
    b.addEventListener('click', function () {
      S.color = b.getAttribute('data-color'); setImg(COLOR[S.color].img);
      if (S.bundle === 3 && !rowsTouched) rows.forEach(function (r) { $('[data-brow-color]', r).value = S.color; });
      clearErr(); renderOptions(); renderStatus();
    });
  });
  $$('[data-size]', root).forEach(function (b) {
    b.addEventListener('click', function () {
      S.size = b.getAttribute('data-size');
      if (S.bundle === 3 && !rowsTouched) rows.forEach(function (r) { $('[data-brow-size]', r).value = S.size; });
      clearErr(); renderOptions(); renderStatus();
    });
  });

  /* bundle */
  var rowsTouched = false;
  $$('input[name="bundle"]', root).forEach(function (r) {
    r.addEventListener('change', function () {
      S.bundle = +r.value;
      $$('.bundle', root).forEach(function (l) { l.classList.toggle('is-active', $('input', l).checked); });
      rowsWrap.hidden = S.bundle === 1;
      buyRow.classList.toggle('is-bundle', S.bundle === 3);
      if (S.bundle === 3 && !rowsTouched) rows.forEach(function (row) { $('[data-brow-color]', row).value = S.color; $('[data-brow-size]', row).value = S.size; });
      clearErr(); renderPrice(); renderStatus();
    });
  });
  rows.forEach(function (r) {
    $$('select', r).forEach(function (s) { s.addEventListener('change', function () { rowsTouched = true; s.classList.remove('is-invalid'); clearErr(); renderStatus(); }); });
  });

  /* quantity */
  $$('[data-qty-step]', root).forEach(function (b) {
    b.addEventListener('click', function () { S.qty = Math.max(1, Math.min(10, S.qty + +b.getAttribute('data-qty-step'))); qtyOut.textContent = S.qty; renderStatus(); });
  });

  /* notify */
  $('[data-notify-btn]', root).addEventListener('click', function () {
    var i = $('#notify-email'), ok = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(i.value.trim());
    window.IC.toast(ok ? 'Ti avviseremo appena torna disponibile' : 'Inserisci un indirizzo email valido'); if (ok) i.value = '';
  });

  /* ---------- add to cart ---------- */
  function line(color, size, free) {
    var c = COLOR[color];
    return { id: D.id + '-' + color + '-' + size + (free ? '-omaggio' : ''), t: D.title + ' — ' + c.name + ' / ' + size + (free ? ' (in omaggio)' : ''), p: free ? 0 : D.price, free: !!free, img: D.thumbs[c.img] };
  }
  function add() {
    if (addBtn.disabled) return;
    var dm = demand();
    if (dm.missing) {
      errEl.hidden = false;
      if (S.bundle === 1) { errEl.textContent = 'Seleziona una taglia per continuare.'; optSize.classList.add('is-invalid'); optSize.scrollIntoView({ behavior: 'smooth', block: 'center' }); }
      else {
        errEl.textContent = 'Scegli la taglia di tutte e 3 le maglie.';
        rows.forEach(function (r) { var s = $('[data-brow-size]', r); if (!s.value) s.classList.add('is-invalid'); });
        rowsWrap.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
      return;
    }
    clearErr();
    if (S.bundle === 1) { window.IC.add(line(S.color, S.size), S.qty, true); return; }
    rows.forEach(function (r, k) { window.IC.add(line($('[data-brow-color]', r).value, $('[data-brow-size]', r).value, k === 2), 1, k === 2); });
  }
  addBtn.addEventListener('click', add);
  $('[data-sticky-add]').addEventListener('click', function () {
    if (demand().missing) { (S.bundle === 1 ? optSize : rowsWrap).scrollIntoView({ behavior: 'smooth', block: 'center' }); add(); } else add();
  });

  /* sticky bar: visible once the main buy row has scrolled above the viewport */
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (es) {
      var e = es[0], show = !e.isIntersecting && e.boundingClientRect.bottom < 200;
      sticky.hidden = false; sticky.classList.toggle('is-visible', show); document.body.classList.toggle('has-sticky', show);
    }, { rootMargin: '-140px 0px 0px 0px' }).observe(buyRow);
  }

  /* share + copy */
  var href = encodeURIComponent(location.href);
  $$('.pp__share a', root).forEach(function (a) { a.href = a.getAttribute('href') + (a.href.indexOf('wa.me') > -1 ? encodeURIComponent(D.title + ' ') : '') + href; });
  var cp = $('[data-copy]', root);
  if (cp) cp.addEventListener('click', function () {
    (navigator.clipboard ? navigator.clipboard.writeText(location.href) : Promise.reject()).then(function () { window.IC.toast('Link copiato'); }, function () { window.IC.toast('Copia non disponibile'); });
  });

  renderOptions(); renderPrice(); renderStatus();
})();
