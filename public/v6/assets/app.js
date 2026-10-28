(() => {
  const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  requestAnimationFrame(() => document.body.classList.add('ready'));
  if (window.self !== window.top) document.documentElement.classList.add('in-frame');  // 並べて比較（iframe内）では切り替えを隠す
  window.addEventListener('pageshow', e => { if (e.persisted) document.body.classList.remove('leaving'); document.body.classList.add('ready'); });
  // スクロールで表示
  const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), {rootMargin: '0px 0px -8% 0px', threshold: 0.06});
  $$('.rv').forEach((s, i) => { if (i < 1) s.classList.add('in'); else io.observe(s); });
  // ヘッダー・固定バー・トップへ戻る
  const hdr = $('.hdr'), fbar = $('.fbar');
  const tt = document.createElement('button'); tt.className = 'totop'; tt.setAttribute('aria-label', 'ページの先頭へ'); tt.textContent = '↑'; document.body.appendChild(tt);
  tt.addEventListener('click', () => window.scrollTo({top: 0, behavior: reduce ? 'auto' : 'smooth'}));
  // ヘッダー：下へスクロール中は隠し、上へスクロールしたら出す（小さな揺れでは切り替えない）
  let lastY = window.scrollY, travel = 0, ticking = false, lockUntil = 0;
  const setHide = v => hdr.classList.toggle('hide', v);
  const onScroll = () => {
    const max = Math.max(0, document.documentElement.scrollHeight - innerHeight);
    const y = Math.min(Math.max(window.scrollY, 0), max);
    const d = y - lastY; lastY = y; ticking = false;
    hdr.classList.toggle('scrolled', y > 8);
    if (fbar) fbar.classList.toggle('on', y > 160);
    tt.classList.toggle('on', y > 900);
    if (document.body.classList.contains('menu-open') || y < hdr.offsetHeight + 24) { setHide(false); travel = 0; return; }
    if (Date.now() < lockUntil || d === 0) return;
    if ((d > 0) !== (travel > 0)) travel = 0;
    travel += d;
    if (travel > 14) setHide(true); else if (travel < -14) setHide(false);
  };
  window.addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, {passive: true});
  onScroll();
  // フッターのサイトマップ
  $$('.fsh').forEach(b => b.addEventListener('click', () => { const g = b.parentElement, o = !g.classList.contains('open');
    g.classList.toggle('open', o); b.setAttribute('aria-expanded', o);
    $$('.fsl', g).forEach((a, i) => a.style.transitionDelay = o && !reduce ? (40 + i * 22) + 'ms' : '0ms'); lockUntil = Date.now() + 500; }));
  // アコーディオン（タップで開閉）
  $$('.hs-acc').forEach(b => b.addEventListener('click', () => {
    const p = document.getElementById(b.dataset.acc); if (!p) return;
    const open = !p.classList.contains('open');
    p.classList.toggle('open', open); b.setAttribute('aria-expanded', open);
    const m = $(`[data-pm="${b.dataset.acc}"]`); if (m) m.classList.toggle('on', open);
    lockUntil = Date.now() + 500;
  }));
  // タップの波紋
  document.addEventListener('pointerdown', e => { const h = e.target.closest('.hs'); if (!h) return;
    const r = h.getBoundingClientRect(), d = Math.max(r.width, r.height) * 2.2, s = document.createElement('span');
    s.className = 'rp'; s.style.cssText = `width:${d}px;height:${d}px;left:${e.clientX - r.left - d / 2}px;top:${e.clientY - r.top - d / 2}px`;
    h.appendChild(s); setTimeout(() => s.remove(), 600); });
  // ページ遷移（フェード）
  document.addEventListener('click', e => { const a = e.target.closest('a[href]'); if (!a) return;
    const href = a.getAttribute('href');
    if (a.hasAttribute('data-anchor')) { e.preventDefault(); const t = document.getElementById(href.slice(1)); if (!t) return;
      document.documentElement.classList.add('cvx');
      const ty = t.getBoundingClientRect().top + window.scrollY, down = ty > window.scrollY;
      setTimeout(() => { const y2 = t.getBoundingClientRect().top + window.scrollY - (down ? 0 : hdr.offsetHeight) - 8; if (Math.abs(y2 - window.scrollY) > 6) window.scrollTo({top: y2, behavior: 'auto'});
        const op = a.dataset.open && document.querySelector('.hs-acc[data-acc="' + a.dataset.open + '"]'); if (op && op.getAttribute('aria-expanded') !== 'true') { op.click(); setTimeout(() => { const y3 = t.getBoundingClientRect().top + window.scrollY - hdr.offsetHeight - 8; window.scrollTo({top: y3, behavior: reduce ? 'auto' : 'smooth'}); }, 350); } }, reduce ? 50 : 1100);
      setHide(down); lockUntil = Date.now() + 1200;
      window.scrollTo({top: ty - (down ? 0 : hdr.offsetHeight) - 8, behavior: reduce ? 'auto' : 'smooth'}); return; }
    if (href.startsWith('tel:') || a.target === '_blank' || e.metaKey || e.ctrlKey) return;
    e.preventDefault(); closeMenu(); document.body.classList.add('leaving'); setTimeout(() => { location.href = a.href; }, reduce ? 0 : 180); });
  // 予約ボタン（デモ）
  const toast = $('.toast'); let tm;
  const say = m => { if (!toast) return; toast.textContent = m; toast.classList.add('on'); clearTimeout(tm); tm = setTimeout(() => toast.classList.remove('on'), 2200); };
  $$('[data-act]').forEach(b => b.addEventListener('click', () => say(({line: 'デモのため、LINE予約には移動しません', web: 'デモのため、Web予約には移動しません', ai: 'AIチャットはデモでは起動しません', sns: 'デモのため、SNSには移動しません'})[b.dataset.act] || 'デモ表示です')));
  // メニュー
  const menu = $('.menu');
  const openMenu = () => { menu.classList.add('open'); menu.setAttribute('aria-hidden', 'false'); document.body.classList.add('menu-open');
    $$('.mi', menu).forEach((m, i) => m.style.transitionDelay = (reduce ? 0 : 60 + i * 18) + 'ms'); };
  function closeMenu() { if (!menu) return; menu.classList.remove('open'); menu.setAttribute('aria-hidden', 'true'); document.body.classList.remove('menu-open'); $$('.mi', menu).forEach(m => m.style.transitionDelay = '0ms'); }
  $$('.hs-menu').forEach(b => b.addEventListener('click', openMenu));
  if (menu) { $('.menu-close').addEventListener('click', closeMenu);
  menu.addEventListener('click', e => { if (e.target === menu) closeMenu(); }); }
  // TOPスライド（背景とコピーのみ切り替え）
  $$('.hero-sl').forEach(sl => {
    const im = $$('img', sl), ds = $$('.hero-dot', sl); if (im.length < 2) return;
    let i = 0, tm = null;
    const go = n => { i = (n + im.length) % im.length; im.forEach((m, k) => m.classList.toggle('on', k === i)); ds.forEach((d, k) => d.setAttribute('aria-current', k === i ? 'true' : 'false')); };
    const play = () => { clearInterval(tm); tm = setInterval(() => { if (!document.hidden) go(i + 1); }, 5000); };
    ds.forEach(d => d.addEventListener('click', e => { e.stopPropagation(); go(+d.dataset.i); play(); }));
    let sx = null; sl.addEventListener('touchstart', e => { sx = e.touches[0].clientX; }, {passive: true});
    sl.addEventListener('touchend', e => { if (sx === null) return; const dx = e.changedTouches[0].clientX - sx; sx = null; if (Math.abs(dx) > 40) { go(i + (dx < 0 ? 1 : -1)); play(); } });
    go(0); play();
  });
  // ページ内リンクの着地点へ（URLの#付きで来た場合）
  if (location.hash) { const t = document.getElementById(location.hash.slice(1)); if (t) setTimeout(() => window.scrollTo({top: t.getBoundingClientRect().top + scrollY - hdr.offsetHeight - 8}), 50); }
})();
/* 病名タブ（v6）：タブで画像とリンクを切り替え */
document.addEventListener('click',function(e){var b=e.target.closest&&e.target.closest('.tsw-tab');if(!b)return;var w=b.closest('.tsw'),i=+b.getAttribute('data-i');
w.querySelectorAll(':scope>img').forEach(function(im,k){im.classList.toggle('on',k===i)});w.querySelectorAll('.tsp').forEach(function(p,k){p.classList.toggle('on',k===i)});});
/* バナーのスライド（v6）：左右ボタン・ドット・スワイプで1枚ずつ送る（端はループ） */
document.querySelectorAll('.bnr').forEach(function(b){var tr=b.querySelector('.bnr-tr');if(!tr)return;var ds=b.querySelectorAll('.bnr-dot'),n=+b.getAttribute('data-n'),f=+tr.getAttribute('data-f'),i=0;
function set(an){tr.style.transition=an?'':'none';tr.style.transform='translateX('+(-i*f*100)+'%)';var a=((i%n)+n)%n;ds.forEach(function(d,k){d.classList.toggle('on',k===a);d.setAttribute('aria-current',k===a?'true':'false');});if(!an)void tr.offsetWidth;}
function norm(){if(i>=n||i<0){i=((i%n)+n)%n;set(false);}}
function go(j){norm();i=j;if(i>n)i=n;if(i<-1)i=-1;set(true);}
tr.addEventListener('transitionend',function(e){if(e.target===tr)norm();});
b.querySelector('.bnr-prev').addEventListener('click',function(){norm();go(i-1);});
b.querySelector('.bnr-next').addEventListener('click',function(){norm();go(i+1);});
ds.forEach(function(d){d.addEventListener('click',function(){norm();go(+d.getAttribute('data-i'));});});
var sx=null,sy=null;b.addEventListener('touchstart',function(e){sx=e.touches[0].clientX;sy=e.touches[0].clientY;},{passive:true});
b.addEventListener('touchend',function(e){if(sx===null)return;var dx=e.changedTouches[0].clientX-sx,dy=e.changedTouches[0].clientY-sy;sx=null;if(Math.abs(dx)>40&&Math.abs(dx)>Math.abs(dy)){norm();go(i+(dx<0?1:-1));}});
set(false);});
/* 参考にしたサイト（v6）：SP単品表示は左右の余白にセクション横で、PC・狭い画面は右端のパネルで表示。並べて比較（iframe内）では出さない */
(function(){var el=document.getElementById('refdata');if(!el||window.self!==window.top)return;
var R=JSON.parse(el.textContent),pc=document.body.classList.contains('pc'),ms=[].slice.call(document.querySelectorAll('.refm'));
var esc=function(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})};
var card=function(r,i,big){return '<p class="refc-k"><span>参考にしたサイト</span>'+esc(r.label)+'</p>'+r.items.map(function(it,j){return '<figure class="refc-i"><button type="button" class="refc-img" data-r="'+i+'" data-j="'+j+'" aria-label="'+esc(it.site)+'のスクリーンショットを拡大"><img src="'+((pc||big)?it.pc:it.sp)+'" alt="'+esc(it.site)+'のスクリーンショット" loading="lazy"></button><figcaption><b>'+esc(it.site)+'</b><span>'+esc(it.cap)+'</span></figcaption></figure>'}).join('')};
// 左右の余白（SP単品・広い画面）
var side=document.createElement('div');side.className='refside';side.setAttribute('aria-label','参考にしたサイト');
R.forEach(function(r,i){var c=document.createElement('aside');c.className='refc';c.setAttribute('data-r',i);c.innerHTML=card(r,i,false);side.appendChild(c);});
if(!pc)document.body.appendChild(side);
// 右端のパネル
var tab=document.createElement('button');tab.type='button';tab.className='reftab';tab.setAttribute('aria-expanded','false');tab.setAttribute('aria-label','参考にしたサイトを表示');tab.innerHTML='<span>参<br>考<br>サ<br>イ<br>ト</span><b>'+R.length+'</b>';
var dr=document.createElement('div');dr.className='refdr';dr.setAttribute('role','dialog');dr.setAttribute('aria-label','このページで参考にしたサイト');
dr.innerHTML='<div class="refdr-h"><p>このページで参考にしたサイト</p><button type="button" class="refdr-x" aria-label="閉じる">×</button></div><p class="refdr-n">実際に公開されている医療機関のサイトを見比べ、見せ方を取り入れています。表示中のセクションの参考が色付きになります。</p><div class="refdr-l">'+R.map(function(r,i){return '<section class="refc refc-d" data-r="'+i+'">'+card(r,i,true)+'<button type="button" class="refc-go" data-r="'+i+'">このセクションへ移動 ↓</button></section>'}).join('')+'</div><p class="refdr-n">※参考サイトの角の丸みは、当院のデザインでは角ありに統一しています。</p>';
document.body.appendChild(tab);document.body.appendChild(dr);
var setOpen=function(o){document.body.classList.toggle('ref-open',o);tab.setAttribute('aria-expanded',o?'true':'false');if(o)scrollCur();};
tab.addEventListener('click',function(){setOpen(!document.body.classList.contains('ref-open'));});
dr.querySelector('.refdr-x').addEventListener('click',function(){setOpen(false);});
var docTop=function(e){return e.getBoundingClientRect().top+window.scrollY;};
dr.addEventListener('click',function(e){var g=e.target.closest('.refc-go');if(!g)return;var m=ms[+g.getAttribute('data-r')];if(m)window.scrollTo({top:docTop(m)-(document.querySelector('.hdr')||{offsetHeight:0}).offsetHeight-10,behavior:'smooth'});});
// いま見ているセクション
var cur=-1;function scrollCur(){var c=dr.querySelector('.refc-d.on');if(c&&document.body.classList.contains('ref-open'))dr.querySelector('.refdr-l').scrollTo({top:c.offsetTop-dr.querySelector('.refdr-l').offsetTop-8,behavior:'smooth'});}
function upd(){var y=window.scrollY+innerHeight*0.45,k=-1;ms.forEach(function(m,i){if(docTop(m)<=y)k=+m.getAttribute('data-r');});if(k===cur)return;cur=k;
[].forEach.call(document.querySelectorAll('.refc'),function(c){c.classList.toggle('on',+c.getAttribute('data-r')===k);});tab.classList.toggle('has',k>=0);scrollCur();}
// 余白のカード配置（左右交互・重ならないように詰める）
function lay(){if(pc)return;var w=innerWidth,cw=Math.min(300,(w-430)/2-56);document.body.classList.toggle('ref-side',cw>=200);if(cw<200)return;
var bot=[0,0],cs=side.children;for(var i=0;i<cs.length;i++){var c=cs[i],m=ms.filter(function(x){return +x.getAttribute('data-r')===i})[0];if(!m){c.style.display='none';continue;}
var sd=i%2?1:0;c.style.width=cw+'px';c.style.left=(sd?(w/2+215+28):(w/2-215-28-cw))+'px';var t=Math.max(docTop(m),bot[sd]+20);c.style.top=t+'px';bot[sd]=t+c.offsetHeight;}}
// 拡大表示
var lb=document.createElement('div');lb.className='reflb';lb.setAttribute('role','dialog');lb.setAttribute('aria-modal','true');document.body.appendChild(lb);
document.addEventListener('click',function(e){var b=e.target.closest('.refc-img');if(!b)return;var it=R[+b.getAttribute('data-r')].items[+b.getAttribute('data-j')];
lb.innerHTML='<div class="reflb-in"><button type="button" class="reflb-x" aria-label="閉じる">×</button><p class="reflb-t"><b>'+esc(it.site)+'</b>'+esc(it.cap)+'</p><div class="reflb-im"><figure><img src="'+it.pc+'" alt=""><figcaption>PC表示</figcaption></figure><figure class="sp"><img src="'+it.sp+'" alt=""><figcaption>スマホ表示</figcaption></figure></div><p class="reflb-f"><a href="'+esc(it.url)+'" target="_blank" rel="noopener">このサイトを開く（新しいタブ）</a><span>※スクリーンショットは2026年10月28日時点。角の丸みは当院のデザインでは角ありに統一しています。</span></p></div>';
lb.classList.add('on');lb.querySelector('.reflb-x').focus();});
lb.addEventListener('click',function(e){if(e.target===lb||e.target.closest('.reflb-x'))lb.classList.remove('on');});
document.addEventListener('keydown',function(e){if(e.key==='Escape'){lb.classList.remove('on');setOpen(false);}});
window.addEventListener('scroll',upd,{passive:true});window.addEventListener('resize',function(){lay();upd();});
if(window.ResizeObserver)new ResizeObserver(function(){lay();}).observe(document.querySelector('main')||document.body);
[].forEach.call(document.querySelectorAll('.refc-img img'),function(im){im.addEventListener('load',lay);});
lay();upd();})();
