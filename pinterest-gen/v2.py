"""Épingles Pinterest « v2 » : calques transparents 1000x1500 (couverture réelle + textes)
posés par Cloudinary sur un décor photo généré (aucune couverture redessinée par l'IA)."""
import math, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

W, H = 1000, 1500
ROOT = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.join(ROOT, '..', 'tiktok-kit')
FD = '/home/claude/fonts/'
NAVY = (18, 28, 52); GOLD = (232, 186, 82); CREAM = (250, 245, 235); RED = (178, 34, 38); WHITE = (255, 255, 255)


def font(name, size):
    paths = {
        'title': 'playfair-display/files/playfair-display-latin-800-normal.woff2',
        'title7': 'playfair-display/files/playfair-display-latin-700-normal.woff2',
        'titleI': 'playfair-display/files/playfair-display-latin-700-italic.woff2',
        'serifI': 'cormorant-garamond/files/cormorant-garamond-latin-600-italic.woff2',
        'sans': 'montserrat/files/montserrat-latin-500-normal.woff2',
        'sansB': 'montserrat/files/montserrat-latin-700-normal.woff2',
        'sansX': 'montserrat/files/montserrat-latin-800-normal.woff2',
        'script': 'great-vibes/files/great-vibes-latin-400-normal.woff2',
    }
    return ImageFont.truetype(FD + paths[name], size)


def cover(slug):
    return Image.open(os.path.join(KIT, 'couvertures', slug + '.jpg')).convert('RGB')


# ---------- livres ----------
def shadow_of(rgba, blur, opacity, offset=(0, 0)):
    a = rgba.split()[3]
    pad = blur * 3
    sh = Image.new('L', (rgba.width + 2 * pad, rgba.height + 2 * pad), 0)
    sh.paste(a, (pad + offset[0], pad + offset[1]))
    sh = sh.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * opacity))
    out = Image.new('RGBA', sh.size, (0, 0, 0, 0)); out.putalpha(sh)
    return out, pad


def book_flat(slug, w, angle, light=(255, 238, 210), thick=10):
    """Livre posé à plat vu de dessus : couverture + tranche de pages + reflet doux."""
    cv = cover(slug); h = round(w * cv.height / cv.width)
    cv = cv.resize((w, h), Image.LANCZOS).convert('RGBA')
    # léger dégradé de lumière chaude (ne modifie pas le dessin)
    g = Image.new('RGBA', (w, h)); gd = ImageDraw.Draw(g)
    for y in range(h):
        t = y / h
        gd.line([(0, y), (w, y)], fill=light + (int(38 * (1 - t)),))
    cv = Image.alpha_composite(cv, g)
    book = Image.new('RGBA', (w + thick, h + thick), (0, 0, 0, 0)); bd = ImageDraw.Draw(book)
    # tranche (pages) en bas et à droite
    for i in range(thick, 0, -1):
        c = 236 - (i % 3) * 10
        bd.rectangle([i, i, w - 1 + i, h - 1 + i], fill=(c, c - 6, c - 16, 255))
    book.paste(cv, (0, 0), cv)
    bd.rectangle([0, 0, w - 1, h - 1], outline=(0, 0, 0, 60))
    book = book.rotate(angle, expand=True, resample=Image.BICUBIC)
    return book


def paste_with_shadow(canvas, obj, cx, cy, blur=18, opacity=0.55, offset=(14, 22), contact=True):
    x, y = int(cx - obj.width / 2), int(cy - obj.height / 2)
    sh, pad = shadow_of(obj, blur, opacity, offset)
    canvas.alpha_composite(sh, (x - pad, y - pad))
    if contact:
        sh2, pad2 = shadow_of(obj, 4, 0.45, (2, 4))
        canvas.alpha_composite(sh2, (x - pad2, y - pad2))
    canvas.alpha_composite(obj, (x, y))


def persp_coeffs(src, dst):
    m = []
    for (x, y), (u, v) in zip(dst, src):
        m.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); m.append([0, 0, 0, x, y, 1, -v * x, -v * y])
    A = np.array(m, dtype=float); B = np.array(src, dtype=float).reshape(8)
    return np.linalg.solve(A, B).tolist()


def book_persp(canvas, slug, quad, thick=16, light=(255, 200, 140)):
    """Livre à plat sur une table vue en perspective. quad = TL, TR, BR, BL (coordonnées canvas)."""
    cv = cover(slug).convert('RGBA'); w, h = cv.size
    g = Image.new('RGBA', (w, h)); gd = ImageDraw.Draw(g)
    for y in range(h):
        gd.line([(0, y), (w, y)], fill=light + (int(46 * (1 - y / h)),))
    cv = Image.alpha_composite(cv, g)
    (tl, tr, br, bl) = quad
    # ombre portée large + ombre de contact
    sh = Image.new('L', (W, H), 0); sd = ImageDraw.Draw(sh)
    sd.polygon([(tl[0] - 6, tl[1] + 10), (tr[0] + 18, tr[1] + 14), (br[0] + 26, br[1] + 30), (bl[0] - 4, bl[1] + 30)], fill=200)
    sh = sh.filter(ImageFilter.GaussianBlur(22))
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); lay.putalpha(sh.point(lambda v: int(v * 0.75)))
    canvas.alpha_composite(lay)
    # épaisseur : face avant (pages) sous le bord bas
    side = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sdd = ImageDraw.Draw(side)
    sdd.polygon([bl, br, (br[0], br[1] + thick), (bl[0], bl[1] + thick)], fill=(226, 214, 192, 255))
    for k in range(1, thick, 3):
        sdd.line([(bl[0], bl[1] + k), (br[0], br[1] + k)], fill=(200, 186, 160, 255))
    sdd.polygon([tr, br, (br[0], br[1] + thick), (tr[0], tr[1] + thick * 0.55)], fill=(214, 200, 176, 255))
    canvas.alpha_composite(side)
    co = persp_coeffs([(0, 0), (w, 0), (w, h), (0, h)], quad)
    warped = cv.transform((W, H), Image.PERSPECTIVE, co, Image.BICUBIC)
    canvas.alpha_composite(warped)


# ---------- textes ----------
def tw(d, t, f, track=0):
    return d.textlength(t, font=f) + track * (len(t) - 1)


def text(d, xy, t, f, fill, anchor='la', track=0, shadow=None):
    x, y = xy
    width = tw(d, t, f, track)
    if anchor[0] == 'm': x -= width / 2
    elif anchor[0] == 'r': x -= width
    if shadow:
        for dx, dy, col in shadow:
            _draw_tracked(d, (x + dx, y + dy), t, f, col, track)
    _draw_tracked(d, (x, y), t, f, fill, track)


def _draw_tracked(d, xy, t, f, fill, track):
    if not track:
        d.text(xy, t, font=f, fill=fill); return
    x, y = xy
    for ch in t:
        d.text((x, y), ch, font=f, fill=fill); x += d.textlength(ch, font=f) + track


def soft_text_shadow(canvas, draw_fn, blur=10, opacity=0.8):
    m = Image.new('RGBA', canvas.size, (0, 0, 0, 0)); draw_fn(ImageDraw.Draw(m), (0, 0, 0, 255))
    a = m.split()[3].filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(min(255, v * opacity * 1.6)))
    lay = Image.new('RGBA', canvas.size, (0, 0, 0, 0)); lay.putalpha(a)
    canvas.alpha_composite(lay)


def signature(canvas, y=1418):
    """Signature identique sur toutes les épingles."""
    d = ImageDraw.Draw(canvas)
    f1 = font('script', 40); f2 = font('sansB', 15)
    t1 = 'Maël Kerjean'; t2 = 'LES ENQUÊTES DE ROSE LE GUEN'
    w = max(tw(d, t1, f1), tw(d, t2, f2, 2.5)) + 64
    x0 = (W - w) / 2
    pill = Image.new('RGBA', canvas.size, (0, 0, 0, 0)); pd = ImageDraw.Draw(pill)
    pd.rounded_rectangle([x0, y, x0 + w, y + 66], radius=33, fill=NAVY + (232,))
    sh, pad = shadow_of(pill, 8, 0.35, (0, 4)); canvas.alpha_composite(sh, (-pad, -pad))
    canvas.alpha_composite(pill)
    d = ImageDraw.Draw(canvas)
    text(d, (W / 2, y + 2), t1, f1, GOLD, anchor='ma')
    text(d, (W / 2, y + 46), t2, f2, CREAM, anchor='ma', track=2.5)


def sticker(canvas, cx, cy, r, lines, fill=RED, color=CREAM, angle=-12):
    s = Image.new('RGBA', (2 * r + 20, 2 * r + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(s)
    d.ellipse([10, 10, 10 + 2 * r, 10 + 2 * r], fill=fill + (255,))
    d.ellipse([18, 18, 2 + 2 * r, 2 + 2 * r], outline=color + (200,), width=2)
    tot = sum(l[1].size + 4 for l in lines); y = 10 + r - tot / 2
    for t, f in lines:
        text(d, (10 + r, y), t, f, color, anchor='ma'); y += f.size + 4
    s = s.rotate(angle, expand=True, resample=Image.BICUBIC)
    paste_with_shadow(canvas, s, cx, cy, blur=6, opacity=0.4, offset=(3, 5), contact=False)


# ---------- styles ----------
KICK = "LIVRE-JEU D'ENQUÊTE"


def style_A(slug, title, sub, stamp=None):
    """Flat-lay cosy (plaid tartan) : carte titre crème en haut, livre au centre."""
    c = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    card = Image.new('RGBA', (W, H), (0, 0, 0, 0)); cd = ImageDraw.Draw(card)
    cd.rounded_rectangle([60, 56, 940, 356], radius=28, fill=CREAM + (244,))
    sh, pad = shadow_of(card, 16, 0.45, (0, 10)); c.alpha_composite(sh, (-pad, -pad)); c.alpha_composite(card)
    d = ImageDraw.Draw(c)
    text(d, (W / 2, 84), KICK, font('sansB', 21), RED, anchor='ma', track=4)
    ft = font('title', 62)
    for i, line in enumerate(title):
        text(d, (W / 2, 118 + i * 74), line, ft, NAVY, anchor='ma')
    text(d, (W / 2, 286), sub, font('sans', 27), (70, 64, 60), anchor='ma')
    paste_with_shadow(c, book_flat(slug, 500, 4), 500, 900, blur=20, opacity=0.6, offset=(16, 26))
    if stamp:
        sticker(c, 795, 590, 92, stamp)
    signature(c)
    return c


def style_B(slug, title, sub, stamp=None):
    """Coin du feu cinématique : titre blanc sur bokeh, livre à plat sur la table en perspective."""
    c = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    grad = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(grad)
    for y in range(560):
        a = int(205 * (1 - y / 560) ** 1.3); gd.line([(0, y), (W, y)], fill=(10, 6, 4, a))
    c.alpha_composite(grad)
    ft = font('title', 74); fk = font('sansB', 21); fs = font('serifI', 40)

    def draw_all(d, col=None):
        text(d, (W / 2, 70), KICK, fk, col or GOLD, anchor='ma', track=5)
        for i, line in enumerate(title):
            text(d, (W / 2, 108 + i * 88), line, ft, col or WHITE, anchor='ma')
        text(d, (W / 2, 290), sub, fs, col or (255, 228, 190), anchor='ma')
    soft_text_shadow(c, lambda d, col: draw_all(d, col), blur=12, opacity=0.9)
    draw_all(ImageDraw.Draw(c))
    book_persp(c, slug, [(345, 960), (705, 975), (760, 1352), (282, 1330)])
    if stamp:
        sticker(c, 190, 985, 84, stamp, angle=-10)
    signature(c, y=1418)
    return c


def style_C(slug, title, sub, stamp=None):
    """Kraft lumineux : titre marine aligné à gauche, livre légèrement tourné au centre."""
    c = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    text(d, (72, 64), KICK, font('sansB', 21), RED, track=4)
    ft = font('title', 70)
    for i, line in enumerate(title):
        text(d, (68, 98 + i * 82), line, ft, NAVY)
    y = 98 + len(title) * 82 + 14
    d.line([(72, y), (172, y)], fill=RED, width=4)
    text(d, (72, y + 18), sub, font('sans', 27), (64, 56, 50))
    paste_with_shadow(c, book_flat(slug, 470, -6, light=(255, 250, 240)), 520, 830, blur=16, opacity=0.38, offset=(-14, 20))
    if stamp:
        sticker(c, 790, 560, 88, stamp, angle=12)
    signature(c)
    return c


if __name__ == '__main__':
    out = os.path.join(ROOT, '..', 'v2', 'proto'); os.makedirs(out, exist_ok=True)
    stamp = [('À OUVRIR', font('sansX', 22)), ('le 1er', font('titleI', 34)), ('DÉCEMBRE', font('sansX', 22))]
    t2 = ["Calendrier de l'Avent", 'pour adultes']
    t3 = ['Calendrier', "de l'Avent", 'pour adultes']
    sub = '24 énigmes · une par jour jusqu’à Noël'
    style_A('Le-Train-des-Neiges', t2, sub, stamp).save(os.path.join(out, 'ov_A.png'))
    style_B('Le-Train-des-Neiges', t2, sub, stamp).save(os.path.join(out, 'ov_B.png'))
    style_C('Le-Train-des-Neiges', t3, '24 énigmes, une par jour', stamp).save(os.path.join(out, 'ov_C.png'))
    print('ok')


# =====================================================================
# PRODUCTION : héros (livre en scène) et teasers (fiche d'énigme en scène)
# =====================================================================
def card_A(c, kicker, title, sub, top=56, kick_col=RED, size=62, dark=False):
    lines = len(title)
    h = 84 + lines * (size + 12) + 64
    card = Image.new('RGBA', (W, H), (0, 0, 0, 0)); cd = ImageDraw.Draw(card)
    cd.rounded_rectangle([60, top, 940, top + h], radius=28, fill=(NAVY if dark else CREAM) + (246,))
    if dark: kick_col = GOLD
    sh, pad = shadow_of(card, 16, 0.45, (0, 10)); c.alpha_composite(sh, (-pad, -pad)); c.alpha_composite(card)
    d = ImageDraw.Draw(c)
    text(d, (W / 2, top + 28), kicker, font('sansB', 21), kick_col, anchor='ma', track=4)
    ft = font('title', size)
    for i, line in enumerate(title):
        text(d, (W / 2, top + 62 + i * (size + 12)), line, ft, CREAM if dark else NAVY, anchor='ma')
    text(d, (W / 2, top + 62 + lines * (size + 12) + 12), sub, font('sans', 26), (225, 214, 196) if dark else (70, 64, 60), anchor='ma')
    return top + h


def head_B(c, kicker, title, sub, size=74):
    grad = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(grad)
    for y in range(600):
        a = int(215 * (1 - y / 600) ** 1.3); gd.line([(0, y), (W, y)], fill=(8, 6, 6, a))
    c.alpha_composite(grad)
    ft = font('title', size); fk = font('sansB', 21); fs = font('serifI', 40)

    def draw_all(d, col=None):
        text(d, (W / 2, 66), kicker, fk, col or GOLD, anchor='ma', track=5)
        for i, line in enumerate(title):
            text(d, (W / 2, 102 + i * (size + 14)), line, ft, col or WHITE, anchor='ma')
        text(d, (W / 2, 112 + len(title) * (size + 14)), sub, fs, col or (255, 228, 190), anchor='ma')
    soft_text_shadow(c, lambda d, col: draw_all(d, col), blur=12, opacity=0.9)
    draw_all(ImageDraw.Draw(c))


def sheet(slug, num, w, angle):
    """Fiche d'énigme réelle (rendu du livre) recadrée sur son contenu, comme une feuille posée."""
    p = Image.open(os.path.join(KIT, 'enigmes', f'{slug}_enigme{num:02d}.png')).convert('RGB')
    arr = np.asarray(p.convert('L')); rows = np.where(arr.min(axis=1) < 200)[0]
    bottom = min(p.height, int(rows[rows < p.height * 0.85].max()) + 70)
    p = p.crop((40, 30, p.width - 40, bottom))
    h = round(w * p.height / p.width)
    p = p.resize((w, h), Image.LANCZOS).convert('RGBA')
    paper = Image.new('RGBA', (w + 2, h + 2), (252, 250, 244, 255)); paper.alpha_composite(p, (1, 1))
    ImageDraw.Draw(paper).rectangle([0, 0, w + 1, h + 1], outline=(0, 0, 0, 40))
    return paper.rotate(angle, expand=True, resample=Image.BICUBIC)


def mirror_quad(q):
    tl, tr, br, bl = q
    return [(W - tr[0], tr[1]), (W - tl[0], tl[1]), (W - bl[0], bl[1]), (W - br[0], br[1])]


# positions propres à chaque décor (calculées sur l'aperçu du décor recadré en 2:3)
SCENES = {
    'A':  dict(style='A', public='pins/proto/bg_A_flatlay', book=(500, 900), stamp=(795, 590)),
    'A2': dict(style='A', public='pins/bg/A2_tartan_vert', book=(500, 880), stamp=(790, 570)),
    'A3': dict(style='A', public='pins/bg/A3_bordeaux_loupe', book=(500, 880), stamp=(790, 570)),
    'A4': dict(style='A', public='pins/bg/A4_provence', book=(500, 880), stamp=(790, 570), dark=True),
    'A5': dict(style='A', public='pins/bg/A5_paquets', book=(500, 880), stamp=(790, 570)),
    'B3': dict(style='B', public='pins/bg/B3_sapin_cadeaux', quad=[(300, 930), (700, 935), (770, 1290), (230, 1285)], stamp=(845, 1080)),
    'B4': dict(style='B', public='pins/bg/B4_salon_loupe', quad=[(470, 860), (820, 872), (875, 1185), (430, 1175)], stamp=(190, 720)),
    'B':  dict(style='B', public='pins/proto/bg_B_coinfeu', quad=[(345, 960), (705, 975), (760, 1352), (282, 1330)], stamp=(190, 985)),
    'B2': dict(style='B', public='pins/bg/B2_fenetre_neige', quad=[(252, 838), (592, 843), (652, 1152), (182, 1146)], stamp=(820, 1255)),
}


def hero(scene, slug, kicker, title, sub, stamp=None, flip=False, book_w=500):
    S = SCENES[scene]; c = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    if S['style'] == 'A':
        bottom = card_A(c, kicker, title, sub, dark=S.get('dark', False))
        cx, cy = S['book']; cy = max(cy, bottom + 40 + book_w * 0.65)
        paste_with_shadow(c, book_flat(slug, book_w, 4 if not flip else -4), cx, cy, blur=20, opacity=0.6, offset=(16, 26))
        if stamp:
            sticker(c, cx + book_w * 0.59, cy - book_w * 0.6, 92, stamp)
    else:
        head_B(c, kicker, title, sub)
        q = S['quad'] if not flip else mirror_quad(S['quad'])
        book_persp(c, slug, q)
        if stamp:
            sx, sy = S['stamp']; sticker(c, W - sx if flip else sx, sy, 84, stamp, angle=-10)
    signature(c)
    return c


def teaser(scene, slug, num, kicker, title, sub, thumb=True):
    S = SCENES[scene]; c = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    if S['style'] == 'A':
        bottom = card_A(c, kicker, title, sub, size=56, dark=S.get('dark', False))
        sh = sheet(slug, num, 820, -1.5)
        cy = bottom + 30 + sh.height / 2
    else:
        head_B(c, kicker, title, sub, size=64)
        sh = sheet(slug, num, 800, 1.5)
        cy = 120 + len(title) * 78 + 90 + sh.height / 2
    paste_with_shadow(c, sh, 500, cy, blur=16, opacity=0.55, offset=(10, 18))
    if thumb:
        b = book_flat(slug, 230, 8, thick=6)
        paste_with_shadow(c, b, 815, min(1290, cy + sh.height / 2 + 40), blur=12, opacity=0.55, offset=(8, 14))
    signature(c)
    return c


def stamp_avent():
    return [('À OUVRIR', font('sansX', 22)), ('le 1er', font('titleI', 34)), ('DÉCEMBRE', font('sansX', 22))]


def stamp_2en1():
    return [('2 LIVRES', font('sansX', 22)), ('en 1', font('titleI', 38)), ('64 ÉNIGMES', font('sansX', 19))]


SERIES = ['Tempete-sur-Belle-Ile', 'Les-Santons-de-Minuit', 'Vendanges-tardives', 'La-Nuit-de-l-Ankou', 'Le-Train-des-Neiges']


def series(scene, kicker, title, sub, flip=False):
    """Les 5 livres de la série en éventail sur un décor vu de dessus."""
    S = SCENES[scene]; c = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    bottom = card_A(c, kicker, title, sub, dark=S.get('dark', False))
    top = bottom + 30
    pos = [(195, top + 215, -5), (500, top + 205, 2), (805, top + 215, 6), (345, top + 590, 4), (655, top + 590, -4)]
    for k in range(5):
        x, y, a = pos[k]
        paste_with_shadow(c, book_flat(SERIES[k], 270, a, thick=7), x, y, blur=14, opacity=0.5, offset=(9, 16))
    signature(c)
    return c
