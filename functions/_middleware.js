// パスワード保護（Cloudflare Pages Functions）
// パスワード本体は置かず、ハッシュのみ保持。環境変数 DEMO_PASSWORD を設定するとそちらが優先されます。
const SALT = 'hclinic-demo-v1';
const HASH = '0e0e9d78ce807b439af01b73fbd81194307efeb55b9f9c568ab2e304e9ca3888';
const COOKIE = 'hc_demo';

async function sha(s) {
  const b = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s));
  return [...new Uint8Array(b)].map(x => x.toString(16).padStart(2, '0')).join('');
}
const safeBack = b => (typeof b === 'string' && b.startsWith('/') && !b.startsWith('//')) ? b : '/';

function loginPage(back, failed) {
  const html = `<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="robots" content="noindex,nofollow">
<title>エイチクリニック新宿｜デモサイト</title><style>
:root{--o:#C65A1E;--ink:#3A2C24}*{box-sizing:border-box}html,body{margin:0;height:100%}
body{font-family:"Hiragino Sans","Noto Sans JP","Yu Gothic",sans-serif;color:var(--ink);display:grid;place-items:center;padding:24px;
background:radial-gradient(120% 80% at 10% 0%,#FFF0E2 0%,#FFFBF6 55%,#FDE6CF 100%)}
.card{width:100%;max-width:360px;background:#fff;border:1.5px solid var(--o);border-radius:20px;padding:34px 26px 28px;box-shadow:0 14px 40px rgba(74,51,38,.12);
animation:in .7s cubic-bezier(.22,.61,.36,1) both}
@keyframes in{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
.logo{width:56px;height:56px;border-radius:16px;background:var(--o);color:#fff;display:grid;place-items:center;font:800 30px/1 Georgia,serif;margin:0 auto 14px}
h1{font-size:17px;text-align:center;margin:0 0 4px;letter-spacing:.04em}p.sub{font-size:12px;color:#76665C;text-align:center;margin:0 0 24px}
label{font-size:12px;font-weight:700;color:#76665C;display:block;margin-bottom:6px}
input{width:100%;font-size:16px;padding:14px 16px;border:1.5px solid #E7D9CB;border-radius:12px;outline:none;transition:border-color .2s,box-shadow .2s}
input:focus{border-color:var(--o);box-shadow:0 0 0 4px rgba(198,90,30,.12)}
button{margin-top:16px;width:100%;font-size:15px;font-weight:700;color:#fff;background:#F0562B;border:0;border-radius:999px;padding:15px;cursor:pointer;
box-shadow:4px 4px 5px rgba(0,0,0,.25),inset 4px 4px 12px rgba(255,255,255,.3);transition:transform .15s}
button:active{transform:scale(.97)}
.err{font-size:12px;color:#B3261E;margin:10px 0 0;text-align:center}.shake{animation:in .7s both,shake .4s .1s}
@keyframes shake{20%,60%{transform:translateX(-6px)}40%,80%{transform:translateX(6px)}}
.note{font-size:11px;color:#A38A74;text-align:center;margin-top:18px}
</style></head><body><form class="card${failed ? ' shake' : ''}" method="post" action="/__login">
<div class="logo">H</div><h1>エイチクリニック新宿</h1><p class="sub">ワイヤーフレーム（SP）デモサイト</p>
<label for="pw">パスワード</label><input id="pw" name="password" type="password" autocomplete="current-password" required autofocus>
<input type="hidden" name="back" value="${back.replace(/"/g, '&quot;')}">
<button type="submit">入る</button>${failed ? '<p class="err">パスワードが違います</p>' : ''}
<p class="note">関係者限定の確認用サイトです</p></form></body></html>`;
  return new Response(html, {status: 401, headers: {'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store', 'X-Robots-Tag': 'noindex, nofollow'}});
}

export async function onRequest({request, env, next}) {
  const url = new URL(request.url);
  const expected = env.DEMO_PASSWORD ? await sha(SALT + ':' + env.DEMO_PASSWORD) : HASH;
  const token = await sha('session:' + expected);
  if (url.pathname === '/__login' && request.method === 'POST') {
    const form = await request.formData();
    const pw = String(form.get('password') || ''); const back = safeBack(String(form.get('back') || '/'));
    if (await sha(SALT + ':' + pw) === expected) {
      return new Response(null, {status: 303, headers: {Location: back === '/' ? '/choose/' : back, 'Set-Cookie': `${COOKIE}=${token}; Path=/; Max-Age=2592000; HttpOnly; Secure; SameSite=Lax`}});
    }
    await new Promise(r => setTimeout(r, 600));
    return loginPage(back, true);
  }
  if (url.pathname === '/__logout') {
    return new Response(null, {status: 303, headers: {Location: '/', 'Set-Cookie': `${COOKIE}=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Lax`}});
  }
  const cookies = (request.headers.get('Cookie') || '').split(/;\s*/);
  if (cookies.includes(`${COOKIE}=${token}`)) {
    const res = await next();
    const r = new Response(res.body, res); r.headers.set('X-Robots-Tag', 'noindex, nofollow'); return r;
  }
  return loginPage(url.pathname + url.search, false);
}
