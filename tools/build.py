"""Figmaの書き出し画像（img_src/NN.png：幅750px＝2倍）＋抽出データ（data/*.json）からデモサイトを生成する"""
import json, os, re, glob, hashlib, shutil, html
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'site')
PUB = os.path.join(OUT, 'public')
SRC = os.path.join(ROOT, 'img_src')
S = 2  # 書き出し倍率
W = 375

pages = []
for fn in sorted(glob.glob(os.path.join(ROOT, 'data', 'd*.json'))):
    pages += json.load(open(fn))
for p in pages:
    m = re.match(r'SP｜No\.(\d+) (.+?)（(.+?)）$', p['name'])
    p['no'], p['title'], url = m.group(1), m.group(2), m.group(3)
    p['url'] = url.replace('{ID}', 'sample')
URL = {p['no']: p['url'] for p in pages}
TITLE = {p['no']: p['title'] for p in pages}

FLOW = ('ヘッダー', 'FV', 'セクション', 'セクショ', '監修医師', '監修', '予約CT', '固定バー', 'フッター')

def cuts(p):
    ks = sorted([k for k in p['kids'] if k[0].startswith(FLOW)], key=lambda k: k[1])
    pts = sorted({k[1] for k in ks} | {p['h']})
    return ks, pts

def esc(s): return html.escape(s, quote=True)

def hot(x, y, w, h, top, sh, kind, attr, label):
    r = '999px' if h <= 60 else '16px'
    pad = 2
    st = f'left:{(x - pad) / W * 100:.3f}%;top:{(y - top - pad) / sh * 100:.3f}%;width:{(w + pad * 2) / W * 100:.3f}%;height:{(h + pad * 2) / sh * 100:.3f}%;border-radius:{r}'
    tag = 'a' if kind in ('link', 'tel') else 'button'
    return f'<{tag} class="hs hs-{kind}" style="{st}" {attr} aria-label="{esc(label)}"></{tag}>'

def page_html(p, slices, fixed_rel):
    no = p['no']
    depth = p['url'].strip('/').count('/') + (1 if p['url'].strip('/') else 0)
    base = '../' * depth if depth else './'
    secs = []
    for i, s in enumerate(slices):
        hs = ''.join(s['hot'])
        anc = ''.join(f'<span class="anc" id="{a}" style="top:{(ay - s["top"]) / s["h"] * 100:.3f}%"></span>' for a, ay in s['anc'])
        cls = 'sl' + (' fv' if i == 0 else ' rv')
        load = 'eager' if i < 2 else 'lazy'
        secs.append(f'<section class="{cls}" style="aspect-ratio:{W}/{s["h"]}"><img src="{base}assets/p/{no}/{i:02d}.webp" alt="" width="{W * S}" height="{s["h"] * S}" loading="{load}" decoding="async">{hs}{anc}</section>')
    fhs = ''.join(fixed_rel)
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex,nofollow"><title>{esc(TITLE[no])}｜エイチクリニック新宿（デモ）</title>
<link rel="preload" as="image" href="{base}assets/p/{no}/00.webp"><link rel="stylesheet" href="{base}assets/app.css"></head>
<body data-base="{base}"><div class="shell">
<header class="hdr"><img src="{base}assets/header.webp" alt="エイチクリニック新宿" width="{W * S}" height="{67 * S}">
<a class="hs hs-link" href="{base}" style="left:2.5%;top:10%;width:39%;height:80%;border-radius:10px" aria-label="TOPへ"></a>
<a class="hs hs-link" href="{base}en/" style="left:47.4%;top:25%;width:17.8%;height:50%;border-radius:999px" aria-label="English"></a>
<button class="hs hs-web" data-act="web" style="left:65.9%;top:27%;width:17.9%;height:46%;border-radius:999px" aria-label="Web予約"></button>
<button class="hs hs-menu" style="left:84.7%;top:15%;width:12.9%;height:70%;border-radius:10px" aria-label="メニュー"></button></header>
<main>{''.join(secs)}</main>
<div class="fbar"><img src="{base}assets/fixed.webp" alt="" width="{W * S}" height="{62 * S}">{fhs}<button class="ai" data-act="ai" aria-label="AIチャット"><img src="{base}assets/ai.webp" alt="" width="112" height="112"></button></div>
</div>
<nav class="menu" aria-hidden="true"><div class="menu-in">
<button class="menu-close" aria-label="閉じる">×</button>
<p class="menu-ttl">MENU</p>
{menu_html(base)}
</div></nav>
<div class="toast" role="status"></div>
<script src="{base}assets/app.js" defer></script></body></html>'''

MENU = [('診療科目', ['02', '03']), ('性病検査', ['04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14']),
        ('自費診療', ['15', '16', '17', '18', '19', '20', '21']), ('クリニック', ['22', '23', '24', '25', '26', '29', '28', '30'])]
def menu_html(base):
    out = [f'<a class="mi mi-top" href="{base}">TOP</a>']
    for g, nos in MENU:
        out.append(f'<p class="mg">{g}</p><div class="mgrid">' + ''.join(f'<a class="mi" href="{base}{URL[n].lstrip("/")}">{esc(TITLE[n])}</a>' for n in nos) + '</div>')
    return ''.join(out)

def link_attr(no, base): return f'href="{base}{URL[no].lstrip("/")}"' if no in URL else ''

def build():
    if os.path.exists(PUB):
        for d in ('assets/p',):
            shutil.rmtree(os.path.join(PUB, d), ignore_errors=True)
    os.makedirs(os.path.join(PUB, 'assets', 'p'), exist_ok=True)
    report = []
    for p in pages:
        no = p['no']; src = os.path.join(SRC, f'{no}.png')
        if not os.path.exists(src): report.append(f'{no}: 画像なし'); continue
        im = Image.open(src).convert('RGB')
        sc = im.width / W
        ks, pts = cuts(p)
        hdr = next((k for k in ks if k[0].startswith('ヘッダー')), None)
        fx = next((k for k in ks if k[0].startswith('固定バー')), None)
        depth = p['url'].strip('/').count('/') + (1 if p['url'].strip('/') else 0)
        base = '../' * depth if depth else './'
        if fx:
            fy = round(fx[1] * sc)
            if no == '01':
                ai = im.crop((618, fy - 84, 730, fy + 28)).convert('RGBA')
                from PIL import ImageDraw
                mk = Image.new('L', ai.size, 0); ImageDraw.Draw(mk).ellipse((2, 2, 110, 110), fill=255); ai.putalpha(mk)
                ai.save(os.path.join(PUB, 'assets', 'ai.webp'), quality=90)
            im.paste(im.crop((612 - 260, fy - 88, 740 - 260, fy)), (612, fy - 88))
        if no == '01':
            im.crop((0, 0, im.width, round(67 * sc))).save(os.path.join(PUB, 'assets', 'header.webp'), quality=88)
            if fx: im.crop((0, round(fx[1] * sc), im.width, round((fx[1] + fx[2]) * sc))).save(os.path.join(PUB, 'assets', 'fixed.webp'), quality=88)
        # スライス
        bounds = [b for b in pts]
        slices = []
        for a, b in zip(bounds, bounds[1:]):
            if hdr and a == hdr[1]: continue
            if fx and a == fx[1]: continue
            slices.append({'top': a, 'h': b - a, 'hot': [], 'anc': []})
        def find(y):
            for s in slices:
                if s['top'] <= y < s['top'] + s['h']: return s
            return None
        # 予約CTAの汎用ボタン
        acts = [a for a in p['acts'] if not (hdr and a[2] < 67)]
        cta = next((k for k in ks if k[0].startswith('予約CT')), None)
        if cta and not any(cta[1] < a[2] < cta[1] + cta[2] for a in acts):
            acts += [['line', 35, cta[1] + 198, 305, 50], ['web', 35, cta[1] + 265, 305, 50], ['tel', 35, cta[1] + 395, 305, 62]]
        fixed_rel = []
        for k, x, y, w, h in acts:
            if fx and fx[1] <= y < fx[1] + fx[2]: continue
            s = find(y + h / 2)
            if not s: continue
            attr = 'href="tel:0362056944"' if k == 'tel' else f'data-act="{k}"'
            s['hot'].append(hot(x, y, w, h, s['top'], s['h'], k if k != 'line' else 'line', attr, k))
        for to, x, y, w, h in p['links']:
            s = find(y + h / 2)
            if not s or to not in URL: continue
            s['hot'].append(hot(x, y, w, h, s['top'], s['h'], 'link', link_attr(to, base), TITLE[to]))
        # ページ内リンク
        heads = p.get('heads', [])
        for lab, x, y, w, h in p['anchors']:
            key = lab.replace('（', '').split('・')[0][:4]
            tgt = next((hy for hy, ht in heads if hy > y and (lab[:4] in ht or key in ht)), None)
            s = find(y + h / 2)
            if not s or tgt is None: continue
            aid = 'a' + hashlib.md5(lab.encode()).hexdigest()[:6]
            ts = find(tgt + 1)
            if ts: ts['anc'].append((aid, tgt))
            s['hot'].append(hot(x, y, w, h, s['top'], s['h'], 'link', f'href="#{aid}" data-anchor', lab))
        # 固定バー（全ページ共通）
        fixed_rel = [f'<button class="hs hs-line" data-act="line" style="left:2.1%;top:14.5%;width:30.8%;height:71%;border-radius:12px" aria-label="LINE予約"></button>',
                     f'<button class="hs hs-web" data-act="web" style="left:34.5%;top:14.5%;width:30.8%;height:71%;border-radius:12px" aria-label="Web予約"></button>',
                     f'<a class="hs hs-tel" href="tel:0362056944" style="left:67.1%;top:14.5%;width:30.7%;height:71%;border-radius:12px" aria-label="電話相談"></a>']
        d = os.path.join(PUB, 'assets', 'p', no); os.makedirs(d, exist_ok=True)
        for i, s in enumerate(slices):
            im.crop((0, round(s['top'] * sc), im.width, min(im.height, round((s['top'] + s['h']) * sc)))).save(os.path.join(d, f'{i:02d}.webp'), quality=82, method=5)
        pd = os.path.join(PUB, p['url'].strip('/')) if p['url'].strip('/') else PUB
        os.makedirs(pd, exist_ok=True)
        open(os.path.join(pd, 'index.html'), 'w').write(page_html(p, slices, fixed_rel))
        report.append(f"{no}: {len(slices)}枚 リンク{sum(len(s['hot']) for s in slices)}")
    print('\n'.join(report))

if __name__ == '__main__':
    build()
