(() => {
  const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  requestAnimationFrame(() => document.body.classList.add('ready'));
  window.addEventListener('pageshow', e => { if (e.persisted) document.body.classList.remove('leaving'); document.body.classList.add('ready'); });
  // スクロールで表示
  const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), {rootMargin: '0px 0px -8% 0px', threshold: 0.06});
  $$('.rv').forEach((s, i) => { if (i < 1) s.classList.add('in'); else io.observe(s); });
  // ヘッダー・固定バー・トップへ戻る
  const hdr = $('.hdr'), fbar = $('.fbar');
  const tt = document.createElement('button'); tt.className = 'totop'; tt.setAttribute('aria-label', 'ページの先頭へ'); tt.textContent = '↑'; document.body.appendChild(tt);
  tt.addEventListener('click', () => window.scrollTo({top: 0, behavior: reduce ? 'auto' : 'smooth'}));
  let lastY = 0, ticking = false;
  const onScroll = () => { const y = window.scrollY;
    hdr.classList.toggle('scrolled', y > 8);
    hdr.classList.toggle('hide', y > 420 && y > lastY + 4 && !document.body.classList.contains('menu-open'));
    if (y < lastY - 4) hdr.classList.remove('hide');
    fbar.classList.toggle('on', y > 160);
    tt.classList.toggle('on', y > 900);
    lastY = y; ticking = false; };
  window.addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, {passive: true});
  onScroll();
  // タップの波紋
  document.addEventListener('pointerdown', e => { const h = e.target.closest('.hs'); if (!h) return;
    const r = h.getBoundingClientRect(), d = Math.max(r.width, r.height) * 2.2, s = document.createElement('span');
    s.className = 'rp'; s.style.cssText = `width:${d}px;height:${d}px;left:${e.clientX - r.left - d / 2}px;top:${e.clientY - r.top - d / 2}px`;
    h.appendChild(s); setTimeout(() => s.remove(), 600); });
  // ページ遷移（フェード）
  document.addEventListener('click', e => { const a = e.target.closest('a[href]'); if (!a) return;
    const href = a.getAttribute('href');
    if (a.hasAttribute('data-anchor')) { e.preventDefault(); const t = document.getElementById(href.slice(1)); if (!t) return;
      const top = t.getBoundingClientRect().top + window.scrollY - hdr.offsetHeight - 8; hdr.classList.remove('hide');
      window.scrollTo({top, behavior: reduce ? 'auto' : 'smooth'}); return; }
    if (href.startsWith('tel:') || a.target === '_blank' || e.metaKey || e.ctrlKey) return;
    e.preventDefault(); closeMenu(); document.body.classList.add('leaving'); setTimeout(() => { location.href = a.href; }, reduce ? 0 : 180); });
  // 予約ボタン（デモ）
  const toast = $('.toast'); let tm;
  const say = m => { toast.textContent = m; toast.classList.add('on'); clearTimeout(tm); tm = setTimeout(() => toast.classList.remove('on'), 2200); };
  $$('[data-act]').forEach(b => b.addEventListener('click', () => say(({line: 'デモのため、LINE予約には移動しません', web: 'デモのため、Web予約には移動しません', ai: 'AIチャットはデモでは起動しません'})[b.dataset.act] || 'デモ表示です')));
  // メニュー
  const menu = $('.menu');
  const openMenu = () => { menu.classList.add('open'); menu.setAttribute('aria-hidden', 'false'); document.body.classList.add('menu-open');
    $$('.mi', menu).forEach((m, i) => m.style.transitionDelay = (reduce ? 0 : 60 + i * 18) + 'ms'); };
  function closeMenu() { menu.classList.remove('open'); menu.setAttribute('aria-hidden', 'true'); document.body.classList.remove('menu-open'); $$('.mi', menu).forEach(m => m.style.transitionDelay = '0ms'); }
  $$('.hs-menu').forEach(b => b.addEventListener('click', openMenu));
  $('.menu-close').addEventListener('click', closeMenu);
  menu.addEventListener('click', e => { if (e.target === menu) closeMenu(); });
  // ページ内リンクの着地点へ（URLの#付きで来た場合）
  if (location.hash) { const t = document.getElementById(location.hash.slice(1)); if (t) setTimeout(() => window.scrollTo({top: t.getBoundingClientRect().top + scrollY - hdr.offsetHeight - 8}), 50); }
})();
