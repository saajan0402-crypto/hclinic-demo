"""pages.json から各ページのアコーディオン中身を集め、Figma抽出（data2）と突き合わせる"""
import json, os, re, glob, difflib
ROOT = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(ROOT, 'data2', 'pages.json')))
ACC = {}
for fn in sorted(glob.glob(os.path.join(ROOT, 'data2', 'a[0-9].json'))): ACC.update(json.load(open(fn)))

def clean(s): return re.sub(r'[⟦⟧⟪⟫]', '', s or '')
def norm(s): return re.sub(r'[\s　⟦⟧⟪⟫「」（）()・、。？?！!：:]', '', s or '').lstrip('Q')

def collect(p):
    T, I = [], []
    def walk(b):
        if isinstance(b, list) and b and isinstance(b[0], str):
            k = b[0]
            if k == 'acc': T.append({'key': b[1], 'body': [['p', b[2]]]})
            elif k == 'acc_s': T.append({'key': '@lead', 'body': [['p', b[1]]]})
            elif k == 'acclist':
                for t, s, body in b[1]: I.append({'key': t, 'body': [['p', body]]})
            elif k == 'faq':
                for q, a in b[1]: I.append({'key': q, 'body': [['a', a]]})
            elif k == 'accb':
                for t, s, blocks in b[1]: I.append({'key': t, 'body': blocks})
            else:
                for x in b[1:]: walk(x)
        elif isinstance(b, list):
            for x in b: walk(x)
        elif isinstance(b, dict):
            for v in b.values(): walk(v)
    walk(p['secs'])
    return T, I

def match(no):
    p = next(x for x in P if x['no'] == no)
    T, I = collect(p)
    out = []
    used = set()
    for a in ACC.get(no, {}).get('accs', []):
        kind, key = a[0], a[2]
        cands = T if kind == 't' else I
        best, bs = None, 0
        for i, c in enumerate(cands):
            if (kind, i) in used: continue
            if key == '@lead' or c['key'] == '@lead':
                s = 1.0 if key == c['key'] else 0
            else:
                nk, nc = norm(key), norm(c['key'])
                s = 1.0 if nc.startswith(nk[:12]) else difflib.SequenceMatcher(None, nk, nc[:len(nk)]).ratio()
            if s > bs: best, bs = i, s
        if best is not None and bs >= 0.55:
            used.add((kind, best)); out.append((a, cands[best], bs))
        else: out.append((a, None, bs))
    return out

if __name__ == '__main__':
    for no in sorted(ACC):
        r = match(no)
        miss = [(a[0], a[2], round(s, 2)) for a, c, s in r if c is None]
        low = [(a[2], c['key'][:18], round(s, 2)) for a, c, s in r if c and s < 1]
        print(no, len(r), 'miss', miss, 'low', low)
