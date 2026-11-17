/* Katalog J.K.FOOD
   1) nezávazná poptávka: tlačítka „Do poptávky“ u výrobků a lišta dole (sortiment.html i stránky kategorií),
      výběr se pamatuje v prohlížeči a odešle se přes poptávkový formulář na úvodní stránce (index.html?produkty=…)
   2) katalog na sortiment.html: hledání, filtry (skupina + kategorie), stránkování „Načíst další“, stav v adrese */
(() => {
  const EN = document.documentElement.lang === 'en';
  const T = EN ? {
    add: 'Add to enquiry', added: 'In enquiry', addAria: 'Add to enquiry: ', remove: 'Remove: ',
    plural: n => n === 1 ? 'product' : 'products',
    inEnq: n => '<span class="enq-w">' + (n === 1 ? 'product' : 'products') + ' </span>in your enquiry',
    count: n => n + ' ' + (n === 1 ? 'product' : 'products'),
    countOf: (n, all) => n + ' of ' + all + ' products',
    shown: (a, b) => 'Showing ' + a + ' of ' + b, more: n => 'Load ' + n + ' more',
    heroFound: n => n + ' ' + (n === 1 ? 'product' : 'products') + ' found', heroShow: 'show in catalogue',
    removeFilter: 'Remove filter: ', search: 'Search: ', clearAll: 'Clear all',
    groupP: 'group', catP: 'category'
  } : {
    add: 'Do poptávky', added: 'V poptávce', addAria: 'Do poptávky: ', remove: 'Odebrat: ',
    plural: n => n === 1 ? 'produkt' : n >= 2 && n <= 4 ? 'produkty' : 'produktů',
    inEnq: n => '<span class="enq-w">' + (n === 1 ? 'produkt' : n >= 2 && n <= 4 ? 'produkty' : 'produktů') + ' </span>v poptávce',
    count: n => n + ' ' + (n === 1 ? 'produkt' : n >= 2 && n <= 4 ? 'produkty' : 'produktů'),
    countOf: (n, all) => n + ' z ' + all + ' produktů',
    shown: (a, b) => 'Zobrazeno ' + a + ' z ' + b, more: n => 'Načíst dalších ' + n,
    heroFound: n => 'Nalezeno: ' + n + ' ' + (n === 1 ? 'produkt' : n >= 2 && n <= 4 ? 'produkty' : 'produktů'), heroShow: 'zobrazit v katalogu',
    removeFilter: 'Zrušit filtr: ', search: 'Hledáno: ', clearAll: 'Zrušit vše',
    groupP: 'skupina', catP: 'kategorie'
  };
  const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  /* ================= nezávazná poptávka ================= */
  const KEY = 'jk-poptavka';
  const load = () => {
    try { const a = JSON.parse(localStorage.getItem(KEY) || '[]'); return Array.isArray(a) ? a.filter(x => typeof x === 'string').slice(0, 100) : []; }
    catch (e) { return []; }
  };
  const save = () => { try { localStorage.setItem(KEY, JSON.stringify(enq)); } catch (e) { /* soukromé okno: výběr platí jen na této stránce */ } };
  let enq = load();

  const bar = document.getElementById('enq');
  const list = bar && bar.querySelector('.enq-list');
  const toggleBtn = bar && bar.querySelector('.enq-toggle');

  // odkazy „Do poptávky“ (bez JavaScriptu vedou na formulář) se chovají jako přepínací tlačítka
  const upgrade = root => root.querySelectorAll('a.kat-add').forEach(a => { a.setAttribute('role', 'button'); });
  const paint = root => root.querySelectorAll('.kat-add').forEach(b => {
    const on = enq.includes(b.dataset.n);
    b.setAttribute('aria-pressed', on);
    b.classList.toggle('on', on);
    const t = b.querySelector('.kat-add-t'); if (t) t.textContent = on ? T.added : T.add;
  });
  const setList = open => {
    if (!bar) return;
    list.hidden = !open; toggleBtn.setAttribute('aria-expanded', open);
    bar.classList.toggle('open', open);
  };
  const renderBar = () => {
    if (!bar) return;
    const n = enq.length;
    bar.hidden = !n;
    document.body.classList.toggle('has-enq', !!n);
    if (!n) { setList(false); return; }
    bar.querySelector('.enq-n').textContent = n;
    bar.querySelector('.enq-t').innerHTML = T.inEnq(n);
    bar.querySelector('.enq-send').href = 'index.html?produkty=' + encodeURIComponent(enq.join('|')) + '#kontakt';
    list.querySelector('ul').innerHTML = enq.map(x =>
      `<li><span>${esc(x)}</span><button type="button" class="enq-rm" data-n="${esc(x)}" aria-label="${esc(T.remove + x)}">×</button></li>`).join('');
  };
  const refresh = () => { paint(document); renderBar(); };
  const toggle = name => {
    enq = enq.includes(name) ? enq.filter(x => x !== name) : [...enq, name];
    save(); refresh();
  };

  document.addEventListener('click', e => {
    const add = e.target.closest('.kat-add');
    if (add) { e.preventDefault(); toggle(add.dataset.n); return; }
    const rm = e.target.closest('.enq-rm');
    if (rm) {
      const li = rm.closest('li'), next = li.nextElementSibling || li.previousElementSibling;
      toggle(rm.dataset.n);
      const f = next && list.querySelector(`.enq-rm[data-n="${CSS.escape(next.querySelector('.enq-rm').dataset.n)}"]`);
      (f || (enq.length ? toggleBtn : document.getElementById('obsah')))?.focus?.();
      return;
    }
    if (e.target.closest('.enq-clear')) { enq = []; save(); refresh(); return; }
    if (e.target.closest('.enq-toggle')) { setList(list.hidden); return; }
    if (bar && !bar.hidden && !list.hidden && !bar.contains(e.target)) setList(false);
  });
  // „Do poptávky“ jako odkaz: mezerník musí fungovat jako u tlačítka
  document.addEventListener('keydown', e => {
    if (e.key === ' ' && e.target.matches && e.target.matches('a.kat-add')) { e.preventDefault(); toggle(e.target.dataset.n); }
    if (e.key === 'Escape' && bar && !list.hidden) { setList(false); toggleBtn.focus(); }
  });
  addEventListener('storage', e => { if (e.key === KEY) { enq = load(); refresh(); } });   // změna v jiné záložce

  upgrade(document);
  refresh();

  /* ================= katalog (jen sortiment.html) ================= */
  const dataEl = document.getElementById('katData');
  if (!dataEl) return;
  const D = JSON.parse(dataEl.textContent);
  const PAGE = D.page || 30;
  const fold = s => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
  const groupOf = {};
  D.groups.forEach(g => g.cats.forEach(c => { groupOf[c] = g.id; }));
  const items = D.items.map(([n, c, s], i) => ({ n, c, s, i, f: fold(n), h: fold(n + ' ' + s + ' ' + D.cats[c].name) }));
  const ALL = items.length;

  const $ = id => document.getElementById(id);
  const listEl = $('katList'), countEl = $('katCount'), activeEl = $('katActive'), shownEl = $('katShown');
  const moreWrap = $('katMore'), moreBtn = $('katMoreBtn'), emptyEl = $('katEmpty'), askEl = $('katEmptyAsk');
  const q = $('q'), q0 = $('q0'), qClear = $('qClear'), heroMeta = $('heroMeta');
  const side = document.querySelector('.kat-side'), filterBtn = side.querySelector('.kat-filter-btn'), badge = side.querySelector('.kat-badge');
  const radios = [...document.querySelectorAll('input[name="skupina"]')];
  const boxes = [...document.querySelectorAll('input[name="kategorie"]')];
  const cgroups = [...document.querySelectorAll('.kat-cg')];
  const resets = [...document.querySelectorAll('.kat-reset')];
  const heroMetaHTML = heroMeta.innerHTML;

  const state = { q: '', g: '', cats: new Set(), limit: PAGE };
  let results = items;

  const toks = () => fold(state.q).trim().split(/\s+/).filter(Boolean);
  const inFilters = it => (!state.g || groupOf[it.c] === state.g) && (!state.cats.size || state.cats.has(it.c));
  const hl = (name, t) => {
    if (!t.length) return esc(name);
    const i = fold(name).indexOf(t[0]);
    if (i < 0) return esc(name);
    return esc(name.slice(0, i)) + '<mark>' + esc(name.slice(i, i + t[0].length)) + '</mark>' + esc(name.slice(i + t[0].length));
  };
  const row = (it, t) => {
    const c = D.cats[it.c].name, on = enq.includes(it.n);
    const meta = esc(c) + (it.s !== c ? ' <span>· ' + esc(it.s) + '</span>' : '');
    return `<li class="kat-row"><span class="kat-name">${hl(it.n, t)}</span><span class="kat-meta">${meta}</span>` +
      `<button type="button" class="kat-add${on ? ' on' : ''}" data-n="${esc(it.n)}" aria-label="${esc(T.addAria + it.n)}" aria-pressed="${on}">` +
      `<span class="kat-add-ic" aria-hidden="true"></span><span class="kat-add-t">${on ? T.added : T.add}</span></button></li>`;
  };

  // čeština skloňuje (klobása → klobásy, šunka → šunkový, párek → párky): delší slova hledáme bez poslední
  // hlásky, a když ani tak nic nenajdeme, zkusíme o další znak kratší
  const stems = (t, k) => t.map(x => x.length >= 5 - k + 1 ? x.slice(0, Math.max(3, x.length - k)) : x);
  const any = t => items.some(it => t.every(x => it.h.includes(x)) && inFilters(it));
  function compute() {
    let t = stems(toks(), 1);
    if (t.length && !any(t)) { const s = stems(toks(), 2); if (any(s)) t = s; }
    const mq = it => t.every(x => it.h.includes(x));
    const byQ = t.length ? items.filter(mq) : items;
    // počty u filtrů: skupiny podle hledání, kategorie podle hledání a skupiny
    const gc = { '': byQ.length }; D.groups.forEach(g => { gc[g.id] = 0; });
    const cc = {}; D.cats.forEach((_, i) => { cc[i] = 0; });
    byQ.forEach(it => { gc[groupOf[it.c]]++; if (!state.g || groupOf[it.c] === state.g) cc[it.c]++; });
    let res = byQ.filter(inFilters);
    if (t.length) {      // nejdřív výrobky, jejichž název hledaným slovem začíná
      const score = it => it.f.startsWith(t[0]) ? 0 : it.f.includes(' ' + t[0]) ? 1 : it.f.includes(t[0]) ? 2 : 3;
      res = res.map(it => [score(it), it]).sort((a, b) => a[0] - b[0] || a[1].i - b[1].i).map(x => x[1]);
    }
    return { t, res, gc, cc };
  }

  function render(append) {
    const { t, res, gc, cc } = compute();
    results = res;
    const shown = Math.min(state.limit, res.length);
    if (append) {
      const from = listEl.children.length;
      listEl.insertAdjacentHTML('beforeend', res.slice(from, shown).map(it => row(it, t)).join(''));
    } else {
      listEl.innerHTML = res.slice(0, shown).map(it => row(it, t)).join('');
    }
    const filtered = t.length || state.g || state.cats.size;
    countEl.textContent = filtered ? T.countOf(res.length, ALL) : T.count(ALL);
    shownEl.textContent = T.shown(shown, res.length);
    moreWrap.hidden = !res.length;
    moreBtn.hidden = shown >= res.length;
    moreBtn.textContent = T.more(Math.min(PAGE, res.length - shown));
    emptyEl.hidden = res.length > 0;
    listEl.hidden = !res.length;
    if (!res.length) askEl.href = 'index.html' + (state.q.trim() ? '?produkt=' + encodeURIComponent(state.q.trim()) : '') + '#kontakt';

    // filtry: počty, skryté kategorie mimo vybranou skupinu
    document.querySelectorAll('[data-cnt]').forEach(el => {
      const [k, v] = el.dataset.cnt.split(':');
      const n = k === 'g' ? gc[v] : cc[v];
      el.textContent = n;
      el.closest('.kat-opt').classList.toggle('dis', !n && !(k === 'c' ? state.cats.has(+v) : state.g === v));
    });
    radios.forEach(r => { r.checked = r.value === state.g; });
    boxes.forEach(b => { b.checked = state.cats.has(+b.value); });
    cgroups.forEach(g => { g.hidden = !!state.g && g.dataset.g !== state.g; g.classList.toggle('solo', !!state.g); });
    const nf = (state.g ? 1 : 0) + state.cats.size;
    badge.hidden = !nf; badge.textContent = nf;
    resets.forEach(b => { if (b.closest('.kat-filters')) b.hidden = !filtered; });

    // aktivní filtry jako odebíratelné štítky
    const chips = [];
    if (state.q.trim()) chips.push(['q', '', T.search + '„' + state.q.trim() + '“']);
    if (state.g) chips.push(['g', state.g, D.groups.find(g => g.id === state.g).name]);
    state.cats.forEach(c => chips.push(['c', c, D.cats[c].name]));
    activeEl.innerHTML = chips.map(([k, v, label]) =>
      `<button type="button" class="kat-chip" data-k="${k}" data-v="${esc(v)}" aria-label="${esc(T.removeFilter + label)}">${esc(label)}</button>`).join('') +
      (chips.length > 1 ? `<button type="button" class="kat-clear">${T.clearAll}</button>` : '');

    // úvod: živý počet výsledků pod hledáním
    heroMeta.innerHTML = t.length ? `${esc(T.heroFound(res.length))} · <a href="#katalog">${T.heroShow}</a>` : heroMetaHTML;
    qClear.hidden = !state.q;
  }

  function syncURL() {
    const p = new URLSearchParams();
    if (state.q.trim()) p.set('q', state.q.trim());
    if (state.g) p.set(T.groupP, state.g);
    if (state.cats.size) p.set(T.catP, [...state.cats].map(c => D.cats[c].id).join(','));
    const s = p.toString();
    history.replaceState(null, '', location.pathname + (s ? '?' + s : '') + location.hash);
  }
  const update = () => { state.limit = PAGE; render(); syncURL(); };

  const scrollToCatalog = () => {
    $('katalog').scrollIntoView({ block: 'start' });
    $('kat-title').focus({ preventScroll: true });
  };
  const setGroup = g => {
    state.g = g;
    if (g) state.cats.forEach(c => { if (groupOf[c] !== g) state.cats.delete(c); });
  };
  const resetAll = () => { state.q = ''; q.value = q0.value = ''; state.g = ''; state.cats.clear(); update(); };

  // hledání: pole v úvodu a v katalogu jsou propojená
  let timer;
  const onInput = e => {
    state.q = e.target.value;
    (e.target === q ? q0 : q).value = state.q;
    clearTimeout(timer); timer = setTimeout(update, 90);
  };
  q.addEventListener('input', onInput);
  q0.addEventListener('input', onInput);
  $('heroSearch').addEventListener('submit', e => { e.preventDefault(); clearTimeout(timer); update(); scrollToCatalog(); });
  q.addEventListener('keydown', e => { if (e.key === 'Escape' && q.value) { e.preventDefault(); q.value = q0.value = state.q = ''; update(); } });
  qClear.addEventListener('click', () => { q.value = q0.value = state.q = ''; update(); q.focus(); });

  radios.forEach(r => r.addEventListener('change', () => { setGroup(r.value); update(); }));
  boxes.forEach(b => b.addEventListener('change', () => {
    const c = +b.value;
    b.checked ? state.cats.add(c) : state.cats.delete(c);
    update();
  }));
  resets.forEach(b => b.addEventListener('click', () => { resetAll(); q.focus(); }));

  activeEl.addEventListener('click', e => {
    const chip = e.target.closest('.kat-chip');
    if (chip) {
      const { k, v } = chip.dataset;
      if (k === 'q') { state.q = ''; q.value = q0.value = ''; }
      if (k === 'g') state.g = '';
      if (k === 'c') state.cats.delete(+v);
      update();
      (activeEl.querySelector('.kat-chip') || q).focus();
    } else if (e.target.closest('.kat-clear')) { resetAll(); q.focus(); }
  });

  moreBtn.addEventListener('click', () => {
    const from = listEl.children.length;
    state.limit += PAGE; render(true);
    const first = listEl.children[from];
    if (moreBtn.hidden && first) first.querySelector('.kat-add').focus();
  });

  // mobil: filtry v rozbalovacím panelu
  filterBtn.addEventListener('click', () => {
    const open = !side.classList.contains('open');
    side.classList.toggle('open', open); filterBtn.setAttribute('aria-expanded', open);
  });

  // karty skupin a kategorie v nich filtrují katalog přímo na stránce
  document.querySelector('.kat-cards').addEventListener('click', e => {
    const a = e.target.closest('[data-group], [data-cat]');
    if (!a) return;
    e.preventDefault();
    state.q = ''; q.value = q0.value = '';
    state.cats.clear();
    if (a.dataset.group) setGroup(a.dataset.group);
    else {
      const c = D.cats.findIndex(x => x.id === a.dataset.cat);
      state.g = groupOf[c]; state.cats.add(c);
    }
    update(); scrollToCatalog();
  });

  // výchozí stav z adresy: ?q=…&skupina=…&kategorie=a,b  nebo  #sk-<kategorie> (odkazy z anglických stránek)
  const P = new URLSearchParams(location.search);
  state.q = P.get('q') || '';
  const g = P.get(T.groupP);
  if (g && D.groups.some(x => x.id === g)) state.g = g;
  (P.get(T.catP) || '').split(',').forEach(id => { const c = D.cats.findIndex(x => x.id === id); if (c >= 0) state.cats.add(c); });
  const h = decodeURIComponent(location.hash.slice(1));
  const legacy = window.KAT_LEGACY || {};
  if (legacy[h]) { location.replace(legacy[h]); return; }      // staré odkazy sortiment.html#maso → stránka kategorie
  if (h.startsWith('sk-')) {
    const c = D.cats.findIndex(x => x.id === h.slice(3));
    if (c >= 0) { state.cats.add(c); state.g = groupOf[c]; }
  }
  q.value = q0.value = state.q;
  if (state.q || state.g || state.cats.size) {
    update();
    if (h.startsWith('sk-')) requestAnimationFrame(scrollToCatalog);
  } else render();
})();
