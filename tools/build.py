"""Figmaの書き出し画像（img_src/NN.png：幅750px＝2倍）＋抽出データ（data/*.json）からデモサイトを生成する"""
import json, os, re, glob, hashlib, shutil, html, io, base64
from PIL import Image, ImageFont
import accdata

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
    m = re.match(r'SP｜No\.(\d+) (.+)（([^（）]+)）$', p['name'])
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
    n = 0
    for si, sec in enumerate(slices):
        parts = []
        for c in sec['chunks']:
            if c.get('panel'):
                parts.append(c['panel']); continue
            hs = ''.join(c['hot'])
            anc = ''.join(f'<span class="anc" id="{a}" style="top:{(ay - c["top"]) / c["h"] * 100:.3f}%"></span>' for a, ay in c['anc'])
            load = 'eager' if n < 3 else 'lazy'
            parts.append(f'<div class="ch" style="aspect-ratio:{W}/{c["h"]}"><img src="{base}assets/p/{no}/{n:02d}.webp" alt="" width="{W * S}" height="{round(c["h"] * S)}" loading="{load}" decoding="async">{hs}{anc}</div>')
            n += 1
        cls = 'sl' + (' fv' if si == 0 else ' rv')
        secs.append(f'<section class="{cls}">{"".join(parts)}</section>')
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

FONT = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
CRUMB = {'TOP': '01', '性病検査': '04', '自費診療': '15', '当院について': '23', 'お知らせ': '26'}

LEAD = json.load(open(os.path.join(ROOT, 'data2', 'lead.json')))
BOLD = ImageFont.truetype(os.path.join(ROOT, 'fonts', 'NotoSansJP.ttf'), 30); BOLD.set_variation_by_axes([700])

def footer_html(base, cur, bg):
    gs = []
    for g, nos in MENU:
        li = ''.join(f'<li><a class="fsl{" cur" if n == cur else ""}" href="{base}{URL[n].lstrip("/")}"{" aria-current=page" if n == cur else ""}>{esc(TITLE[n])}</a></li>' for n in nos)
        gs.append(f'<div class="fsg"><button class="fsh" aria-expanded="false">{g}<i></i></button><div class="fsp"><div class="ap-in"><ul>{li}</ul></div></div></div>')
    return f'<div class="fsm" style="background:{bg}">{"".join(gs)}</div>'

def render_blocks(bl, base):
    out = []
    for b in bl:
        k = b[0]
        if k == 'p': out.append(f'<p>{esc(accdata.clean(b[1]))}</p>')
        elif k == 'a': out.append(f'<p class="ap-ans"><b>A.</b>{esc(accdata.clean(b[1]))}</p>')
        elif k == 'cap': out.append(f'<p class="ap-cap">{esc(accdata.clean(b[1]))}</p>')
        elif k == 'table':
            rows = b[1]
            th = ''.join(f'<th>{esc(accdata.clean(c))}</th>' for c in rows[0])
            td = ''.join('<tr>' + ''.join(f'<td>{esc(accdata.clean(c))}</td>' for c in r) + '</tr>' for r in rows[1:])
            out.append(f'<div class="ap-tw"><table><thead><tr>{th}</tr></thead><tbody>{td}</tbody></table></div>')
        elif k == 'more' and len(b) > 2 and b[2] in URL:
            out.append(f'<a class="ap-more" href="{base}{URL[b[2]].lstrip("/")}">{esc(accdata.clean(b[1]))}<span>→</span></a>')
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
        if no in LEAD:  # 「リード文の続きを読む」→「もっと詳しく読む」
            from PIL import ImageDraw
            x, y, w, h = LEAD[no]
            bg = im.getpixel((round(x * 2 - 6), round((y + h / 2) * 2)))
            dr = ImageDraw.Draw(im)
            dr.rectangle(tuple(round(v) for v in (x * 2 - 4, y * 2 - 2, (x + w) * 2 + 4, (y + h) * 2 + 2)), fill=bg)
            dr.text((x * 2, (y + h / 2) * 2 - 3), 'もっと詳しく読む', font=BOLD, fill=(198, 90, 30), anchor='lm')
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
        # スライス（セクション単位）→ アコーディオン位置でさらに分割
        px = lambda x, y: '#%02x%02x%02x' % im.getpixel((min(im.width - 1, round(x * sc)), min(im.height - 1, round(y * sc))))
        def dark(x0, x1, y):
            c = min((im.getpixel((xx, round(y * sc))) for xx in range(round(x0 * sc), round(x1 * sc) + 1)), key=sum)
            return '#%02x%02x%02x' % c
        def strip(top, x0, x1):
            best = None
            for yy in range(top - 2, top - 12, -1):
                ln = im.crop((0, round(yy * sc), im.width, round(yy * sc) + 1))
                inner = ln.crop((round(x0 * sc), 0, round(x1 * sc), 1)).convert('L')
                v = max(inner.getdata()) - min(inner.getdata())
                if best is None or v < best[0]: best = (v, ln)
            buf = io.BytesIO(); best[1].save(buf, 'PNG', optimize=True)
            return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()
        slices = []
        for a, b in zip(pts, pts[1:]):
            if hdr and a == hdr[1]: continue
            if fx and a == fx[1]: continue
            slices.append({'top': a, 'bot': b})
        accs = accdata.match(no) if no in accdata.ACC else []
        bodybg = next((px(a[6][0] + 4, a[6][1] + 30) for a, c, _ in accs if a[0] == 'i' and a[1] and a[6]), '#fffaf5')
        ops = []
        for k, (a, c, _) in enumerate(accs):
            kind, op, key, row, pm, item, body = a
            rid = f'ap{k}'
            rmid = row[1] + row[3] / 2
            if kind == 'i':
                cut, res = row[1] + row[3] - 13, item[1] + item[3]
                st = f'margin-left:{item[0] / W * 100:.3f}%;width:{item[2] / W * 100:.3f}%;--bg:{px(item[0] + 6, rmid)};--bd:{dark(item[0] - 1, item[0] + 2, rmid)};--bb:{bodybg}'
                inner = '<div class="ap-pad"></div>'
                sec_bg = strip(item[1], item[0], item[0] + item[2])
            else:
                cut = row[1] + row[3] - 3; res = item[1] + item[3] - 3
                st = f'margin-left:{row[0] / W * 100:.3f}%;width:{row[2] / W * 100:.3f}%;--bg:{px(row[0] + 2, rmid)}'
                inner = ''
                sec_bg = strip(row[1], row[0], row[0] + row[2])
            content = render_blocks(c['body'], base) if c else ''
            panel = (f'<div class="apw" style="background:url({sec_bg}) 0 0/100% 100% no-repeat"><div class="ap ap-{kind}{" open" if op else ""}" id="{rid}" style="{st}">{inner}'
                     f'<div class="ap-g"><div class="ap-in"><div class="ap-b">{content}</div></div></div></div></div>')
            ops.append({'cut': cut, 'res': res, 'panel': panel, 'id': rid, 'open': op, 'row': row, 'pm': pm, 'kind': kind, 'key': key,
                        'pmc': px(pm[0] + 3, pm[1] + pm[3] / 2), 'pmg': px(pm[0] + pm[2] / 2, pm[1] + pm[3] / 2)})
        ft = next((k for k in ks if k[0].startswith('フッター')), None)
        if ft:
            fy = ft[1]
            ops.append({'cut': fy + 272, 'res': fy + 650, 'panel': footer_html(base, no, px(8, fy + 300)), 'row': None})
        ops.sort(key=lambda o: o['cut'])
        for sec in slices:
            t = sec['top']; ch = []
            for o in ops:
                if sec['top'] <= o['cut'] < sec['bot']:
                    if o['cut'] > t: ch.append({'top': t, 'h': o['cut'] - t, 'hot': [], 'anc': []})
                    ch.append({'panel': o['panel']})
                    t = o['res']
            if sec['bot'] > t: ch.append({'top': t, 'h': sec['bot'] - t, 'hot': [], 'anc': []})
            sec['chunks'] = ch
        chunks = [c for sec in slices for c in sec['chunks'] if not c.get('panel')]
        def find(y):
            for s in chunks:
                if s['top'] <= y < s['top'] + s['h']: return s
            return None
        lost = 0
        for o in ops:
            if not o['row']: continue
            row, pm = o['row'], o['pm']
            s = find(row[1] + 3)
            if not s: continue
            hb = min(row[1] + row[3], s['top'] + s['h'])
            r = '12px' if o['kind'] == 'i' else '0'
            s['hot'].append(f'<button class="hs hs-acc" data-acc="{o["id"]}" aria-expanded="{"true" if o["open"] else "false"}" aria-controls="{o["id"]}" aria-label="{esc(o["key"])}" '
                            f'style="left:{row[0] / W * 100:.3f}%;top:{(row[1] - s["top"]) / s["h"] * 100:.3f}%;width:{row[2] / W * 100:.3f}%;height:{(hb - row[1]) / s["h"] * 100:.3f}%;border-radius:{r} {r} 0 0"></button>')
            s['hot'].append(f'<span class="pmx{" on" if o["open"] else ""}" data-pm="{o["id"]}" style="left:{(pm[0] - .5) / W * 100:.3f}%;top:{(pm[1] - .5 - s["top"]) / s["h"] * 100:.3f}%;width:{(pm[2] + 1) / W * 100:.3f}%;height:{(pm[3] + 1) / s["h"] * 100:.3f}%;--c:{o["pmc"]};--g:{o["pmg"]}"></span>')
        # パンくず
        for txt, x, y, w, h, fs in accdata.ACC.get(no, {}).get('crumbs', []):
            s = find(y + h / 2)
            if not s: continue
            f = ImageFont.truetype(FONT, fs * 10)
            segs = [g.strip() for g in txt.split('＞')]
            pos = 0
            for i, g in enumerate(segs):
                pre = ' ＞ '.join(segs[:i]) + (' ＞ ' if i else '')
                x0 = x + f.getlength(pre) / 10; x1 = x0 + f.getlength(g) / 10
                to = CRUMB.get(g) or next((n for n, t in TITLE.items() if t == g), None)
                if i == len(segs) - 1 or not to: continue
                hh = 30; yy = y + h / 2 - hh / 2
                s['hot'].append(f'<a class="hs hs-link hs-bc" href="{base}{URL[to].lstrip("/")}" aria-label="{esc(g)}" style="left:{(x0 - 4) / W * 100:.3f}%;top:{(yy - s["top"]) / s["h"] * 100:.3f}%;width:{(x1 - x0 + 8) / W * 100:.3f}%;height:{hh / s["h"] * 100:.3f}%;border-radius:6px"></a>')
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
        if ft:
            fy = ft[1]
            for args in ((20, fy + 219, 112, 22, 'tel', 'href="tel:0362056944"', '電話'), (20, fy + 657, 44, 40, 'sns', 'data-act="sns"', 'X'), (74, fy + 657, 105, 40, 'sns', 'data-act="sns"', 'Instagram')):
                x, y, w, h, k, attr, lab = args
                s_ = find(y + h / 2)
                if s_: s_['hot'].append(hot(x, y, w, h, s_['top'], s_['h'], k, attr, lab))
        # 固定バー（全ページ共通）
        fixed_rel = [f'<button class="hs hs-line" data-act="line" style="left:2.1%;top:14.5%;width:30.8%;height:71%;border-radius:12px" aria-label="LINE予約"></button>',
                     f'<button class="hs hs-web" data-act="web" style="left:34.5%;top:14.5%;width:30.8%;height:71%;border-radius:12px" aria-label="Web予約"></button>',
                     f'<a class="hs hs-tel" href="tel:0362056944" style="left:67.1%;top:14.5%;width:30.7%;height:71%;border-radius:12px" aria-label="電話相談"></a>']
        d = os.path.join(PUB, 'assets', 'p', no); os.makedirs(d, exist_ok=True)
        for i, c in enumerate(chunks):
            im.crop((0, round(c['top'] * sc), im.width, min(im.height, round((c['top'] + c['h']) * sc)))).save(os.path.join(d, f'{i:02d}.webp'), quality=82, method=5)
        pd = os.path.join(PUB, p['url'].strip('/')) if p['url'].strip('/') else PUB
        os.makedirs(pd, exist_ok=True)
        open(os.path.join(pd, 'index.html'), 'w').write(page_html(p, slices, fixed_rel))
        report.append(f"{no}: {len(chunks)}枚 リンク{sum(len(c['hot']) for c in chunks)} アコーディオン{len(ops)} 未対応{sum(1 for a, c, _ in accs if not c)}")
    print('\n'.join(report))

if __name__ == '__main__':
    build()
