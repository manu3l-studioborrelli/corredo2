/* Il Corredo 2 — category page: filters, sort, layout, load more (vanilla JS) */
(function () {
  'use strict';
  var root = document.querySelector('[data-catalog]'); if (!root) return;
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var PAGE = 24;

  var grid = $('[data-grid]', root), cards = $$('.pcard', grid);
  var inputs = $$('input[data-f]', document), chips = $$('[data-chip]', document);
  var sortSel = $('[data-sort]', root), tagsEl = $('[data-active-tags]', root), emptyEl = $('[data-empty]', root);
  var moreWrap = $('[data-loadmore]', root), moreBtn = $('[data-more]', root), bar = $('[data-bar]', root);
  var shown = PAGE;

  /* sticky toolbar sits right under the sticky header */
  var header = document.getElementById('header');
  function setHeader() { if (header) document.documentElement.style.setProperty('--header-h', header.offsetHeight + 'px'); }
  setHeader(); window.addEventListener('resize', setHeader);

  function picked(name) { return inputs.filter(function (i) { return i.getAttribute('data-f') === name && i.checked; }).map(function (i) { return i.value; }); }
  function flag(name) { var i = inputs.filter(function (x) { return x.getAttribute('data-f') === name; })[0]; return !!(i && i.checked); }
  function sel() { return { avail: flag('avail'), offer: flag('offer'), sub: picked('sub'), brand: picked('brand'), color: picked('color'), aud: picked('aud'), season: picked('season'), price: picked('price') }; }

  function inBand(price, bands) {
    if (price === '') return false;
    var v = parseFloat(price);
    return bands.some(function (b) { var r = b.split('-'); return v >= +r[0] && v < +r[1]; });
  }
  function match(c, s) {
    var d = c.dataset;
    if (s.avail && d.stock === 'out') return false;
    if (s.offer && d.offer !== '1') return false;
    if (s.sub.length && s.sub.indexOf(d.sub) < 0) return false;
    if (s.brand.length && s.brand.indexOf(d.brand) < 0) return false;
    if (s.aud.length) { var as = d.aud.split(' '); if (!s.aud.some(function (x) { return as.indexOf(x) > -1; })) return false; }
    if (s.season.length && s.season.indexOf(d.season) < 0) return false;
    if (s.color.length) { var cs = d.colors.split(','); if (!s.color.some(function (x) { return cs.indexOf(x) > -1; })) return false; }
    if (s.price.length && !inBand(d.price, s.price)) return false;
    return true;
  }
  var collator = new Intl.Collator('it');
  var sorters = {
    featured: function (a, b) { return +a.dataset.i - +b.dataset.i; },
    'price-asc': function (a, b) { return price(a, 1e9) - price(b, 1e9) || +a.dataset.i - +b.dataset.i; },
    'price-desc': function (a, b) { return price(b, -1) - price(a, -1) || +a.dataset.i - +b.dataset.i; },
    az: function (a, b) { return collator.compare(a.dataset.title, b.dataset.title); },
    za: function (a, b) { return collator.compare(b.dataset.title, a.dataset.title); }
  };
  function price(c, none) { return c.dataset.price === '' ? none : parseFloat(c.dataset.price); }

  function labelOf(i) {
    var l = i.closest('label'); if (!l) return i.value;
    var clone = l.cloneNode(true); $$('small,i,input', clone).forEach(function (n) { n.remove(); });
    return clone.textContent.trim();
  }
  function renderTags() {
    var out = [], n = 0;
    inputs.forEach(function (i) {
      if (!i.checked) return; n++;
      out.push('<button type="button" class="tag-x" data-rm="' + inputs.indexOf(i) + '">' + labelOf(i) + '</button>');
    });
    tagsEl.innerHTML = n ? out.join('') + '<button type="button" class="tag-x tag-x--clear" data-reset>Rimuovi tutti</button>' : '';
    $$('[data-filter-n]', document).forEach(function (b) { b.textContent = n; b.hidden = !n; });
  }
  function syncChips() {
    var subs = picked('sub');
    chips.forEach(function (c) {
      var v = c.getAttribute('data-chip');
      c.classList.toggle('is-active', v === '' ? subs.length === 0 : (subs.length === 1 && subs[0] === v));
    });
  }

  function apply(keepShown) {
    if (!keepShown) shown = PAGE;
    var s = sel(), list = cards.filter(function (c) { return match(c, s); });
    list.sort(sorters[sortSel.value] || sorters.featured);
    var frag = document.createDocumentFragment();
    cards.forEach(function (c) { c.hidden = true; });
    cards.filter(function (c) { return list.indexOf(c) < 0; }).forEach(function (c) { frag.appendChild(c); });
    list.forEach(function (c, k) { c.hidden = k >= shown; grid.insertBefore(c, null); });
    grid.appendChild(frag);
    var total = list.length, vis = Math.min(shown, total);
    $$('[data-total],[data-total2],[data-show-n]', document).forEach(function (e) { e.textContent = e.hasAttribute('data-total2') ? cards.length : total; });
    $$('[data-total2]', document).forEach(function (e) { e.textContent = total; });
    $$('[data-shown]', document).forEach(function (e) { e.textContent = vis; });
    if (bar) bar.style.width = (total ? vis / total * 100 : 0) + '%';
    emptyEl.hidden = total > 0;
    moreWrap.hidden = total === 0;
    moreBtn.hidden = vis >= total;
    renderTags(); syncChips();
  }

  /* events */
  inputs.forEach(function (i) { i.addEventListener('change', function () { apply(); }); });
  sortSel.addEventListener('change', function () { apply(); });
  moreBtn.addEventListener('click', function () { shown += PAGE; apply(true); });
  chips.forEach(function (c) {
    c.addEventListener('click', function () {
      var v = c.getAttribute('data-chip');
      inputs.forEach(function (i) { if (i.getAttribute('data-f') === 'sub') i.checked = v !== '' && i.value === v; });
      apply();
    });
  });
  document.addEventListener('click', function (e) {
    var rm = e.target.closest('[data-rm]');
    if (rm) { inputs[+rm.getAttribute('data-rm')].checked = false; apply(); return; }
    if (e.target.closest('[data-reset]')) { inputs.forEach(function (i) { i.checked = false; }); apply(); }
  });
  $$('[data-layout]', root).forEach(function (b) {
    b.addEventListener('click', function () {
      var list = b.getAttribute('data-layout') === 'list';
      root.classList.toggle('is-list', list);
      $$('[data-layout]', root).forEach(function (o) { o.setAttribute('aria-pressed', o === b ? 'true' : 'false'); });
    });
  });

  /* ?sub=slug preselects a subcategory / category */
  try {
    var want = new URLSearchParams(location.search).get('sub');
    if (want) inputs.forEach(function (i) { if (i.getAttribute('data-f') === 'sub' && i.value === want) i.checked = true; });
    var sort = new URLSearchParams(location.search).get('sort'); if (sort && sorters[sort]) sortSel.value = sort;
  } catch (e) { /* old browsers */ }
  apply();
})();
