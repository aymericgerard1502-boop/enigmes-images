#!/usr/bin/env python3
"""Générateur de vidéos « Arène » (format Pour ou contre ?), 1080x1920, 30 i/s.
Usage : python3 video_arene.py <episode.json> <sortie.mp4>"""
import json, os, re, subprocess, sys, tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
F = '/usr/share/fonts/opentype/inter/'
BLACKI = F + 'InterDisplay-BlackItalic.otf'
XBOLDI = F + 'InterDisplay-ExtraBoldItalic.otf'
BOLD = F + 'Inter-Bold.otf'
SEMI = F + 'Inter-SemiBold.otf'
MED = F + 'Inter-Medium.otf'
WHITE = (245, 242, 236)
GREY = (150, 146, 140)
ACCENT = (232, 53, 43)
BG = (12, 12, 12)
X0, X1 = 80, 940  # zone sûre (l'interface TikTok mange la droite et le bas)
HERE = os.path.dirname(os.path.abspath(__file__))

_fonts = {}
def font(path, size):
    k = (path, size)
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(path, size)
    return _fonts[k]

def ease(x):
    x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3

# ---------- primitives de mise en page ----------
def rich_block(text, fpath, size, width, color=WHITE, hl=ACCENT, lh=1.18, align='left'):
    """Texte multi-lignes ; **mot** = surligné couleur accent. Renvoie une image RGBA recadrée."""
    f = font(fpath, size)
    text = re.sub(r'(\d) (?=\d)', '\\1\u00a0', text)
    text = re.sub(r' (?=[€%:?!;»])', '\u00a0', text)
    text = re.sub(r'(?<=\d) (?=(milliards?|millions?|€))', '\u00a0', text)
    words = []  # chaque mot = liste de segments (texte, surligné)
    on = False
    glue = False  # le segment précédent finissait-il collé (sans espace) ?
    for k, part in enumerate(text.split('**')):
        pieces = part.split(' ')
        for j, w in enumerate(pieces):
            if not w:
                continue
            if j == 0 and glue and words:
                words[-1].append((w, on))
            else:
                words.append([(w, on)])
        glue = bool(part) and not part.endswith(' ')
        on = not on
    space = f.getlength(' ')
    lines, cur, cw = [], [], 0
    for runs in words:
        wl = sum(f.getlength(r[0]) for r in runs)
        if cur and cw + space + wl > width:
            lines.append((cur, cw)); cur, cw = [], 0
        cw = cw + (space if cur else 0) + wl; cur.append((runs, wl))
    if cur:
        lines.append((cur, cw))
    asc, desc = f.getmetrics()
    lhpx = int(size * lh)
    img = Image.new('RGBA', (width + 40, lhpx * len(lines) + desc + 10), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, (ws, lw) in enumerate(lines):
        x = 0 if align == 'left' else (width - lw) / 2
        for runs, wl in ws:
            for r, h in runs:
                d.text((x, i * lhpx), r, font=f, fill=hl if h else color)
                x += f.getlength(r)
            x += space
    return img.crop(img.getbbox() or (0, 0, 1, 1)) if align == 'left' else img

def pill(text, size=40, bg=ACCENT, fg=WHITE, fpath=BLACKI, pad=(26, 12)):
    f = font(fpath, size)
    tw = f.getlength(text); bb = f.getbbox(text)
    th = bb[3] - bb[1]
    img = Image.new('RGBA', (int(tw + 2 * pad[0]) + 10, int(th + 2 * pad[1]) + 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, tw + 2 * pad[0], th + 2 * pad[1]), radius=10, fill=bg)
    d.text((pad[0], pad[1] - bb[1]), text, font=f, fill=fg)
    return img

def rule(width, h=4, color=WHITE, alpha=255):
    img = Image.new('RGBA', (width, h), color + (alpha,)); return img

# ---------- éléments animés ----------
class El:
    def __init__(self, img, x, y, t_in, dur=0.45, dy=36, t_out=None):
        self.img, self.x, self.y, self.t_in, self.dur, self.dy, self.t_out = img, x, y, t_in, dur, dy, t_out
    def draw(self, canvas, t, scene_alpha):
        if t < self.t_in:
            return
        p = ease((t - self.t_in) / self.dur)
        a = p * scene_alpha
        if self.t_out is not None and t > self.t_out:
            a *= max(0, 1 - (t - self.t_out) / 0.3)
        if a <= 0.01:
            return
        im = self.img
        if a < 0.999:
            im = im.copy(); im.putalpha(im.getchannel('A').point(lambda v: int(v * a)))
        canvas.alpha_composite(im, (int(self.x), int(self.y + (1 - p) * self.dy)))

class Strike:
    """Barre qui raye un élément, tracée de gauche à droite."""
    def __init__(self, x, y, w, t_in, dur=0.4, color=ACCENT, h=9):
        self.x, self.y, self.w, self.t_in, self.dur, self.color, self.h = x, y, w, t_in, dur, color, h
    def draw(self, canvas, t, sa):
        if t < self.t_in:
            return
        p = ease((t - self.t_in) / self.dur)
        lay = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
        ImageDraw.Draw(lay).rectangle((self.x, self.y, self.x + self.w * p, self.y + self.h), fill=self.color + (int(255 * sa),))
        canvas.alpha_composite(lay)

class Bar:
    """Barre de vote qui pousse, avec compteur."""
    def __init__(self, x, y, wmax, frac, value, label, t_in, color, dur=1.1):
        self.x, self.y, self.wmax, self.frac, self.value, self.label, self.t_in, self.color, self.dur = x, y, wmax, frac, value, label, t_in, color, dur
    def draw(self, canvas, t, sa):
        if t < self.t_in:
            return
        p = ease((t - self.t_in) / self.dur)
        lay = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        a = int(255 * sa * min(1, (t - self.t_in) / 0.25))
        d.text((self.x, self.y), self.label, font=font(BLACKI, 54), fill=WHITE + (a,))
        by = self.y + 82
        d.rounded_rectangle((self.x, by, self.x + self.wmax, by + 74), radius=12, fill=(40, 40, 40, a))
        wv = max(20, self.wmax * self.frac * p)
        d.rounded_rectangle((self.x, by, self.x + wv, by + 74), radius=12, fill=self.color + (a,))
        n = str(int(round(self.value * p)))
        f = font(BLACKI, 64)
        tx = self.x + wv + 22
        if tx + f.getlength(n) > self.x + self.wmax:
            tx = self.x + wv - f.getlength(n) - 22
            d.text((tx, by + 2), n, font=f, fill=BG + (a,))
        else:
            d.text((tx, by + 2), n, font=f, fill=WHITE + (a,))
        canvas.alpha_composite(lay)

# ---------- scènes ----------
def sc_hook(s, T):
    els = []
    tag = pill(s['tag'], 42)
    # visibles dès la première image : TikTok s'en sert comme miniature
    els.append(El(tag, X0, 700, -1, dy=0))
    hk = rich_block(s['texte'], BLACKI, 112, X1 - X0, lh=1.08)
    els.append(El(hk, X0, 800, -1, dy=0))
    if s.get('sous'):
        sb = rich_block(s['sous'], SEMI, 46, X1 - X0, color=GREY)
        els.append(El(sb, X0, 840 + hk.height, 1.2))
    return els

def sc_texte(s, T):
    """Titre + paragraphes qui apparaissent un à un."""
    els = []; y = 560
    if s.get('titre'):
        els.append(El(pill(s['titre'], 40, bg=WHITE, fg=BG), X0, y, 0.1)); y += 110
    t = 0.3
    for i, par in enumerate(s['lignes']):
        size = 70 if i == 0 and s.get('grand_premier', True) else 56
        fp = XBOLDI if size == 70 else BOLD
        im = rich_block(par, fp, size, X1 - X0)
        els.append(El(im, X0, y, t)); y += im.height + 60
        t += s.get('pas', 2.6)
    return els

def sc_compare(s, T):
    els = []; y = 520
    els.append(El(pill(s['titre'], 40, bg=WHITE, fg=BG), X0, y, 0.1)); y += 120
    lab = rich_block(s['libelle'], XBOLDI, 64, X1 - X0)
    els.append(El(lab, X0, y, 0.3)); y += lab.height + 70
    avant = rich_block(s['avant'], BLACKI, 150, X1 - X0, color=GREY)
    els.append(El(avant, X0, y, 1.3))
    els.append(Strike(X0 - 10, y + avant.height // 2 - 4, avant.width + 20, 2.4))
    y2 = y + avant.height + 50
    arrow = rich_block('↓', BLACKI, 90, 200, color=ACCENT)
    els.append(El(arrow, X0 + 10, y2, 2.8)); y2 += arrow.height + 40
    apres = rich_block(s['apres'], BLACKI, 150, X1 - X0)
    els.append(El(apres, X0, y2, 3.2)); y2 += apres.height + 80
    if s.get('note'):
        nt = rich_block(s['note'], BOLD, 54, X1 - X0)
        els.append(El(nt, X0, y2, 5.0))
    return els

def sc_vote(s, T):
    els = []; y = 600
    els.append(El(pill(s['titre'], 40, bg=WHITE, fg=BG), X0, y, 0.1)); y += 140
    tot = max(s['contre'], s['pour'])
    els.append(Bar(X0, y, X1 - X0, s['contre'] / tot, s['contre'], s.get('label_contre', 'CONTRE'), 0.5, ACCENT))
    els.append(Bar(X0, y + 230, X1 - X0, s['pour'] / tot, s['pour'], s.get('label_pour', 'POUR'), 1.0, WHITE))
    cap = rich_block(s['legende'], BOLD, 54, X1 - X0)
    els.append(El(cap, X0, y + 520, 2.6))
    return els

def sc_camp(s, T):
    """Arguments d'un camp : même traitement visuel pour les deux camps."""
    els = []
    big = rich_block(s['camp'], BLACKI, 200, X1 - X0)
    els.append(El(big, X0, 400, 0.1, dur=0.5, dy=50))
    sub = rich_block(s['qui'], SEMI, 44, X1 - X0, color=GREY)
    els.append(El(sub, X0, 400 + big.height + 30, 0.5))
    y = 400 + big.height + 30 + sub.height + 80
    t = 1.2
    for a in s['arguments']:
        bar = rule(8, 1, WHITE)
        im = rich_block(a, BOLD, 56, X1 - X0 - 40)
        bar = bar.resize((8, im.height))
        els.append(El(bar, X0, y, t, dy=0)); els.append(El(im, X0 + 36, y, t))
        y += im.height + 64
        t += s.get('pas', 3.6)
    return els

def sc_cta(s, T):
    els = []
    q1 = rich_block(s['question'], BLACKI, 100, X1 - X0, lh=1.05)
    els.append(El(q1, X0, 560, 0.1))
    duo = rich_block('**POUR** ou **CONTRE** ?', BLACKI, 128, X1 - X0, hl=WHITE, color=WHITE)
    y = 610 + q1.height
    els.append(El(pill('POUR', 120, bg=WHITE, fg=BG, pad=(34, 18)), X0, y, 0.6, dy=60))
    p2 = pill('CONTRE', 120, bg=WHITE, fg=BG, pad=(34, 18))
    els.append(El(rich_block('ou', BLACKI, 80, 200, color=GREY), X0, y + 200, 0.9))
    els.append(El(p2, X0, y + 300, 1.1, dy=60))
    y2 = y + 300 + p2.height + 70
    els.append(El(rich_block(s['appel'], BOLD, 54, X1 - X0), X0, y2, 1.8))
    return els

SCENES = {'hook': sc_hook, 'texte': sc_texte, 'compare': sc_compare, 'vote': sc_vote, 'camp': sc_camp, 'cta': sc_cta}

# ---------- fond ----------
def make_background(source):
    base = Image.new('RGB', (W, H), BG)
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - W * 0.5) / W) ** 2 + ((yy - H * 0.42) / H) ** 2)
    glow = np.clip(1 - r * 1.6, 0, 1) ** 2 * 22
    arr = np.asarray(base).astype(np.float32) + glow[..., None]
    base = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert('RGBA')
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    # logo en haut à droite, comme la signature d'un média ; source en haut à gauche
    wm = font(BLACKI, 112)
    d.text((W - 70 - wm.getlength('Arène'), 70), 'Arène', font=wm, fill=WHITE + (235,))
    d.text((X0, 112), source, font=font(SEMI, 30), fill=GREY + (255,))
    # grand mot en filigrane, très discret, en bas de l'écran
    big = font(BLACKI, 420)
    d.text((-30, H - 760), 'Arène', font=big, fill=WHITE + (9,))
    base.alpha_composite(lay)
    grains = []
    rng = np.random.default_rng(3)
    for _ in range(6):
        g = rng.normal(0, 4.5, (H // 2, W // 2)).astype(np.float32)
        g = np.kron(g, np.ones((2, 2), dtype=np.float32))
        grains.append(g)
    return base, grains

def render(ep, outp):
    scenes = ep['scenes']
    starts, t = [], 0.0
    for s in scenes:
        starts.append(t); t += s['duree']
    total = t
    built = [SCENES[s['type']](s, s['duree']) for s in scenes]
    base, grains = make_background(ep['source'])
    tmpd = tempfile.mkdtemp()
    wav = os.path.join(tmpd, 'm.wav')
    trans = ','.join(f'{x:.2f}' for x in starts[1:])
    subprocess.run([sys.executable, os.path.join(HERE, 'musique.py'), f'{total:.2f}', f'{starts[1]:.2f}', wav, trans], check=True, capture_output=True)
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-i', wav, '-c:v', 'libx264', '-preset', 'medium', '-crf', '22', '-tune', 'grain', '-maxrate', '6M', '-bufsize', '12M', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
           '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', outp]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    nfr = int(round(total * FPS))
    for fi in range(nfr):
        tg = fi / FPS
        k = max(i for i in range(len(scenes)) if starts[i] <= tg + 1e-9)
        tl = tg - starts[k]; dur = scenes[k]['duree']
        sa = 1.0
        if k < len(scenes) - 1 and tl > dur - 0.3:
            sa = max(0.0, (dur - tl) / 0.3)
        canvas = base.copy()
        for el in built[k]:
            el.draw(canvas, tl, sa)
        # barre de progression fine en haut
        ImageDraw.Draw(canvas).rectangle((0, 0, int(W * tg / total), 7), fill=ACCENT + (255,))
        arr = np.asarray(canvas.convert('RGB')).astype(np.float32) + grains[(fi // 5) % len(grains)][..., None]
        pr.stdin.write(np.clip(arr, 0, 255).astype(np.uint8).tobytes())
    pr.stdin.close(); pr.wait()
    print(f'ok {outp} ({total:.1f} s)')

if __name__ == '__main__':
    ep = json.load(open(sys.argv[1], encoding='utf-8'))
    render(ep, sys.argv[2])
