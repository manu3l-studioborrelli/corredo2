/* Il Corredo 2 — homepage interactions (vanilla JS, no dependencies) */
(function () {
  'use strict';
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var fmt = function (n) { return '€' + n.toFixed(2).replace('.', ','); };
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- announcement rotator ---------- */
  (function () {
    var root = $('[data-rotator]'); if (!root) return;
    var items = $$('.announce__track p', root), i = 0, t;
    function show(n) { i = (n + items.length) % items.length; items.forEach(function (p, k) { p.classList.toggle('is-active', k === i); }); }
    function auto() { clearInterval(t); if (!reduce) t = setInterval(function () { show(i + 1); }, 4500); }
    $('[data-ann-prev]', root).addEventListener('click', function () { show(i - 1); auto(); });
    $('[data-ann-next]', root).addEventListener('click', function () { show(i + 1); auto(); });
    auto();
  })();

  /* ---------- sticky header shadow ---------- */
  var header = $('#header');
  var topBtn = $('.top');
  window.addEventListener('scroll', function () {
    header.classList.toggle('is-stuck', window.scrollY > 60);
    if (topBtn) topBtn.classList.toggle('show', window.scrollY > 900);
  }, { passive: true });
  if (topBtn) topBtn.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' }); });

  /* ---------- drawers / overlay ---------- */
  var overlay = $('.overlay'), openDrawer = null, lastFocus = null;
  function open(id) {
    var d = document.getElementById(id); if (!d) return;
    close();
    lastFocus = document.activeElement;
    d.classList.add('is-open'); overlay.classList.add('is-open'); d.setAttribute('aria-hidden', 'false');
    document.documentElement.classList.add('is-locked'); document.body.style.overflow = 'hidden'; openDrawer = d;
    var f = $('button, a, input', d); if (f) setTimeout(function () { f.focus({ preventScroll: true }); }, 340);
  }
  function close() {
    if (!openDrawer) return;
    openDrawer.classList.remove('is-open'); openDrawer.setAttribute('aria-hidden', 'true');
    overlay.classList.remove('is-open'); document.body.style.overflow = ''; document.documentElement.classList.remove('is-locked');
    openDrawer = null; if (lastFocus) lastFocus.focus();
  }
  $$('[data-open]').forEach(function (b) { b.addEventListener('click', function () { open(b.getAttribute('data-open')); }); });
  $$('[data-close]').forEach(function (b) { b.addEventListener('click', close); });
  overlay.addEventListener('click', close);
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { close(); $$('.nav__item.is-open').forEach(function (n) { n.classList.remove('is-open'); }); } });

  /* drawer accordion */
  $$('.dlink[data-acc]').forEach(function (b) {
    b.addEventListener('click', function () {
      var sub = document.getElementById(b.getAttribute('data-acc'));
      var exp = b.getAttribute('aria-expanded') === 'true';
      $$('.dlink[data-acc]').forEach(function (o) { o.setAttribute('aria-expanded', 'false'); document.getElementById(o.getAttribute('data-acc')).classList.remove('is-open'); });
      if (!exp) { b.setAttribute('aria-expanded', 'true'); sub.classList.add('is-open'); }
    });
  });

  /* ---------- mega menu (hover + focus + click) ---------- */
  $$('.nav__item[data-mega]').forEach(function (item) {
    var timer;
    var link = $('.nav__link', item);
    function show() { clearTimeout(timer); $$('.nav__item.is-open').forEach(function (n) { if (n !== item) n.classList.remove('is-open'); }); item.classList.add('is-open'); link.setAttribute('aria-expanded', 'true'); }
    function hide() { timer = setTimeout(function () { item.classList.remove('is-open'); link.setAttribute('aria-expanded', 'false'); }, 140); }
    item.addEventListener('mouseenter', show); item.addEventListener('mouseleave', hide);
    item.addEventListener('focusin', show);
    item.addEventListener('focusout', function (e) { if (!item.contains(e.relatedTarget)) hide(); });
    link.addEventListener('click', function (e) { if (e.target.closest('.i')) { e.preventDefault(); item.classList.toggle('is-open'); } });
  });

  /* ---------- hero slideshow ---------- */
  (function () {
    var hero = $('[data-hero]'); if (!hero) return;
    var slides = $$('.slide', hero), bar = $('.hero__bar i', hero), cur = $('[data-hero-cur]', hero), i = 0, t;
    var wrap = $('.hero__track', hero);
    hero.className = hero.className.replace(/hero--\w+/g, '');
    function go(n) {
      i = (n + slides.length) % slides.length;
      slides.forEach(function (s, k) { s.classList.toggle('is-active', k === i); s.setAttribute('aria-hidden', k === i ? 'false' : 'true'); });
      var theme = slides[i].className.match(/slide--(\w+)/);
      hero.className = hero.className.replace(/hero--\w+/g, '').trim() + (theme ? ' hero--' + theme[1] : '');
      if (cur) cur.textContent = i + 1;
      bar.classList.remove('run'); void bar.offsetWidth; if (!reduce) bar.classList.add('run');
      clearTimeout(t); if (!reduce) t = setTimeout(function () { go(i + 1); }, 6000);
    }
    $$('[data-hero-prev]', hero).forEach(function (b) { b.addEventListener('click', function () { go(i - 1); }); });
    $$('[data-hero-next]', hero).forEach(function (b) { b.addEventListener('click', function () { go(i + 1); }); });
    var sx = null;
    wrap.addEventListener('touchstart', function (e) { sx = e.touches[0].clientX; }, { passive: true });
    wrap.addEventListener('touchend', function (e) { if (sx === null) return; var dx = e.changedTouches[0].clientX - sx; if (Math.abs(dx) > 40) go(i + (dx < 0 ? 1 : -1)); sx = null; }, { passive: true });
    document.addEventListener('visibilitychange', function () { if (document.hidden) clearTimeout(t); else go(i); });
    go(0);
  })();

  /* ---------- generic carousels ---------- */
  $$('[data-carousel]').forEach(function (c) {
    var track = $('.carousel__track', c), prev = $('.carousel__btn--prev', c), next = $('.carousel__btn--next', c);
    function upd() {
      if (!prev) return;
      prev.disabled = track.scrollLeft < 8;
      next.disabled = track.scrollLeft + track.clientWidth >= track.scrollWidth - 8;
    }
    function step() { var f = track.firstElementChild; return (f ? f.getBoundingClientRect().width + 14 : 240) * (window.innerWidth > 1100 ? 3 : 2); }
    if (prev) { prev.addEventListener('click', function () { track.scrollBy({ left: -step(), behavior: 'smooth' }); }); next.addEventListener('click', function () { track.scrollBy({ left: step(), behavior: 'smooth' }); }); }
    track.addEventListener('scroll', upd, { passive: true }); window.addEventListener('resize', upd); upd();
  });

  /* ---------- tabs ---------- */
  $$('[data-tabs]').forEach(function (wrap) {
    var tabs = $$('[role="tab"]', wrap), panels = $$('[role="tabpanel"]', wrap);
    function sel(tab) {
      tabs.forEach(function (t) { t.setAttribute('aria-selected', t === tab ? 'true' : 'false'); t.tabIndex = t === tab ? 0 : -1; });
      panels.forEach(function (p) { p.hidden = p.id !== tab.getAttribute('aria-controls'); });
      $$('[data-carousel] .carousel__track', wrap).forEach(function (tr) { tr.dispatchEvent(new Event('scroll')); });
    }
    tabs.forEach(function (t, k) {
      t.addEventListener('click', function () { sel(t); });
      t.addEventListener('keydown', function (e) {
        var d = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[e.key]; if (!d) return;
        e.preventDefault(); var n = tabs[(k + d + tabs.length) % tabs.length]; n.focus(); sel(n);
      });
    });
  });

  /* ---------- countdowns ---------- */
  var cds = $$('[data-countdown]');
  function pad(n) { return String(n).padStart(2, '0'); }
  function tick() {
    cds.forEach(function (el) {
      var end = el.getAttribute('data-countdown') === 'daily' ? (function () { var d = new Date(); d.setHours(24, 0, 0, 0); return d; })() : new Date(el.getAttribute('data-countdown'));
      var s = Math.max(0, Math.floor((end - new Date()) / 1000));
      var v = [Math.floor(s / 86400), Math.floor(s % 86400 / 3600), Math.floor(s % 3600 / 60), s % 60];
      $$('b', el).forEach(function (b, k) { b.textContent = pad(v[k]); });
    });
  }
  if (cds.length) { tick(); setInterval(tick, 1000); }

  /* ---------- wishlist ---------- */
  var wishCount = $('[data-wish-count]'), wishN = 0;
  function setBadge(el, n) { el.textContent = n; el.setAttribute('data-zero', n === 0 ? 'true' : 'false'); }
  document.addEventListener('click', function (e) {
    var w = e.target.closest('.wish'); if (!w) return;
    var on = w.getAttribute('aria-pressed') !== 'true';
    w.setAttribute('aria-pressed', on ? 'true' : 'false'); wishN += on ? 1 : -1; setBadge(wishCount, wishN);
    toast(on ? 'Aggiunto ai preferiti' : 'Rimosso dai preferiti');
  });

  /* ---------- toast ---------- */
  var toastEl = $('.toast'), toastT;
  function toast(msg) { $('span', toastEl).textContent = msg; toastEl.classList.add('show'); clearTimeout(toastT); toastT = setTimeout(function () { toastEl.classList.remove('show'); }, 2200); }

  /* ---------- cart ---------- */
  var FREE = 49, cart = [], cartCount = $('[data-cart-count]'), list = $('[data-cart-list]'), sub = $('[data-cart-sub]'), ship = $('[data-cart-ship]'), shipBar = $('[data-cart-bar]');
  function render() {
    var n = 0, total = 0;
    cart.forEach(function (it) { n += it.q; total += it.q * it.p; });
    setBadge(cartCount, n); sub.textContent = fmt(total);
    var left = FREE - total;
    ship.innerHTML = left > 0 ? 'Ti mancano <strong>' + fmt(left) + '</strong> per la spedizione gratuita' : '🎉 Hai diritto alla <strong>spedizione gratuita</strong>';
    shipBar.style.width = Math.min(100, total / FREE * 100) + '%';
    if (!cart.length) {
      list.innerHTML = '<div class="cart-empty"><svg class="ico" viewBox="0 0 64 64"><use href="#i-gift"/></svg><p><strong>Il carrello è vuoto</strong></p><p>Scopri le nostre offerte e riempilo di cose belle.</p></div>'; return;
    }
    list.innerHTML = cart.map(function (it, k) {
      return '<div class="cart-item"><div class="art"><img src="' + it.img + '" alt=""></div>' +
        '<div><h4>' + it.t + '</h4><div class="qty"><button data-q="-1" data-k="' + k + '" aria-label="Diminuisci"><svg class="i"><use href="#u-minus"/></svg></button><output>' + it.q + '</output><button data-q="1" data-k="' + k + '" aria-label="Aumenta"><svg class="i"><use href="#u-plus"/></svg></button></div></div>' +
        '<div style="text-align:right"><strong>' + fmt(it.p * it.q) + '</strong><br><button class="rm" data-rm="' + k + '">Rimuovi</button></div></div>';
    }).join('');
  }
  function add(d, qty, openCart) {
    var f = cart.filter(function (c) { return c.id === d.id; })[0];
    if (f) f.q += qty; else cart.push({ id: d.id, t: d.t, p: d.p, q: qty, img: d.img });
    render(); if (openCart) open('cart'); else toast('Aggiunto al carrello');
  }
  document.addEventListener('click', function (e) {
    var a = e.target.closest('[data-add]');
    if (a) {
      var card = a.closest('[data-product]') || a;
      var art = $('.art', card);
      add({ id: a.getAttribute('data-id'), t: a.getAttribute('data-title'), p: parseFloat(a.getAttribute('data-price')), img: a.getAttribute('data-img') || '' }, a.hasAttribute('data-qty') ? parseInt($('[data-qty-out]').textContent, 10) : 1, a.hasAttribute('data-open-cart'));
      return;
    }
    var q = e.target.closest('[data-q][data-k]');
    if (q) { var it = cart[+q.getAttribute('data-k')]; it.q += +q.getAttribute('data-q'); if (it.q < 1) cart.splice(+q.getAttribute('data-k'), 1); render(); return; }
    var r = e.target.closest('[data-rm]'); if (r) { cart.splice(+r.getAttribute('data-rm'), 1); render(); }
  });
  render();

  /* ---------- product showcase ---------- */
  (function () {
    var sc = $('[data-showcase]'); if (!sc) return;
    var main = $('[data-gal-main]', sc);
    $$('[data-thumb]', sc).forEach(function (b) {
      b.addEventListener('click', function () {
        $$('[data-thumb]', sc).forEach(function (o) { o.setAttribute('aria-current', 'false'); }); b.setAttribute('aria-current', 'true');
        $('img', main).src = $('img', b).src.replace(/w=\d+/, 'w=900');
      });
    });
    $$('.sw', sc).forEach(function (s) {
      s.addEventListener('click', function () {
        $$('.sw', sc).forEach(function (o) { o.setAttribute('aria-pressed', 'false'); }); s.setAttribute('aria-pressed', 'true');
        $('[data-sw-name]', sc).textContent = s.getAttribute('aria-label');
      });
    });
    $$('.chip', sc).forEach(function (c) {
      c.addEventListener('click', function () { $$('.chip', sc).forEach(function (o) { o.setAttribute('aria-pressed', 'false'); }); c.setAttribute('aria-pressed', 'true'); $('[data-size-name]', sc).textContent = c.textContent; });
    });
    var out = $('[data-qty-out]', sc);
    $$('[data-qty-step]', sc).forEach(function (b) {
      b.addEventListener('click', function () { out.textContent = Math.max(1, Math.min(10, parseInt(out.textContent, 10) + parseInt(b.getAttribute('data-qty-step'), 10))); });
    });
  })();

  /* ---------- newsletter ---------- */
  var nf = $('[data-newsletter]');
  if (nf) nf.addEventListener('submit', function (e) {
    e.preventDefault();
    var inp = $('input', nf), msg = $('small', nf), ok = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(inp.value.trim());
    msg.className = ok ? 'ok' : ''; msg.textContent = ok ? 'Grazie! Ti abbiamo iscritto alla newsletter.' : 'Email non valida';
    if (ok) inp.value = '';
  });

  /* ---------- search form (design only) ---------- */
  $$('[data-search]').forEach(function (f) { f.addEventListener('submit', function (e) { e.preventDefault(); toast('Ricerca disponibile nella versione finale'); }); });

  /* ---------- review note ---------- */
  var note = $('.note'); if (note) $('button', note).addEventListener('click', function () { note.remove(); });

  /* ---------- reveal on scroll ---------- */
  var rv = $$('.reveal');
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (es) { es.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } }); }, { rootMargin: '0px 0px -8% 0px' });
    rv.forEach(function (el) { io.observe(el); });
  } else rv.forEach(function (el) { el.classList.add('in'); });
})();
