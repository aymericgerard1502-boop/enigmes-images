"""Générateur d'épingles Pinterest 1000x1500 (Les Enquêtes de Rose Le Guen).
Sources : ../tiktok-kit/couvertures/<slug>.jpg et ../tiktok-kit/enigmes/<slug>_enigmeNN.png
Usage : python3 pins.py lot3   -> écrit ../lot3/*.jpg
"""
import os, sys, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.join(HERE, '..', 'tiktok-kit')
FD = '/usr/share/fonts/truetype/crosextra/'
W, H = 1000, 1500
NAVY, NAVY2 = (16, 26, 49), (28, 42, 74)
PURPLE, PURPLE2 = (24, 20, 52), (40, 32, 80)
GOLD, ORANGE, RED = (246, 196, 77), (240, 140, 50), (198, 40, 40)
CREAM, SOFT = (251, 246, 236), (205, 210, 225)
OUT = None


def F(name, size):
    return ImageFont.truetype(FD + name + '.ttf', size)


SERIF_B = lambda s: F('Caladea-Bold', s)
SERIF_I = lambda s: F('Caladea-Italic', s)
SANS = lambda s: F('Carlito-Regular', s)
SANS_B = lambda s: F('Carlito-Bold', s)


def gradient(c1, c2):
    im = Image.new('RGB', (W, H), c1)
    d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3)))
    return im


def stars(im, seed=3, n=70):
    r = random.Random(seed)
    d = ImageDraw.Draw(im)
    for _ in range(n):
        x, y = r.randint(0, W), r.randint(0, H)
        s = r.choice([1, 1, 2])
        d.ellipse([x, y, x + s, y + s], fill=(230, 230, 250))


def wrap(d, text, font, width):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=font) <= width:
            cur = t
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def text_block(d, text, font, y, fill, width=860, lh=1.18):
    lines = [l for para in text.split('\n') for l in wrap(d, para, font, width)]
    for ln in lines:
        d.text(((W - d.textlength(ln, font=font)) / 2, y), ln, font=font, fill=fill)
        y += int(font.size * lh)
    return y


def spaced(d, text, font, y, fill, spacing=4):
    total = sum(d.textlength(c, font=font) for c in text) + spacing * (len(text) - 1)
    x = (W - total) / 2
    for c in text:
        d.text((x, y), c, font=font, fill=fill)
        x += d.textlength(c, font=font) + spacing
    return y + font.size


def shadow_paste(im, tile, x, y, radius=18, offset=12, alpha=150, rounded=0):
    sh = Image.new('L', (tile.width + radius * 4, tile.height + radius * 4), 0)
    ImageDraw.Draw(sh).rectangle([radius * 2, radius * 2, radius * 2 + tile.width, radius * 2 + tile.height], fill=alpha)
    sh = sh.filter(ImageFilter.GaussianBlur(radius))
    im.paste(Image.new('RGB', sh.size, (0, 0, 0)), (x - radius * 2 + offset // 2, y - radius * 2 + offset), sh)
    if rounded:
        m = Image.new('L', tile.size, 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, tile.width - 1, tile.height - 1], rounded, fill=255)
        im.paste(tile, (x, y), m)
    else:
        im.paste(tile, (x, y))


def cover(slug, w):
    c = Image.open(os.path.join(KIT, 'couvertures', slug + '.jpg')).convert('RGB')
    return c.resize((w, round(w * c.height / c.width)), Image.LANCZOS)


def puzzle_crop(slug, num):
    p = Image.open(os.path.join(KIT, 'enigmes', f'{slug}_enigme{num:02d}.png')).convert('RGB')
    g = ImageOps.invert(p.convert('L')).point(lambda v: 255 if v > 40 else 0)
    x0, y0, x1, y1 = g.crop((0, 0, p.width, p.height - 260)).getbbox()
    pad = 60
    return p.crop((max(0, x0 - pad), max(0, y0 - pad), min(p.width, x1 + pad), y1 + pad))


def footer_brand(d, y=1438):
    spaced(d, "MAËL KERJEAN  ·  LES ENQUÊTES DE ROSE LE GUEN", SANS_B(22), y, SOFT, 2)


def bg(theme, seed):
    im = gradient(*((PURPLE, PURPLE2) if theme == 'purple' else (NAVY, NAVY2)))
    stars(im, seed=seed)
    return im


def pin_teaser(name, slug, num, label, headline, line1, line2, theme='navy', accent=GOLD):
    im = bg(theme, len(name))
    d = ImageDraw.Draw(im)
    y = spaced(d, label, SANS_B(28), 56, accent, 4) + 22
    y = text_block(d, headline, SERIF_B(72), y, GOLD, width=880, lh=1.1) + 26
    pc = puzzle_crop(slug, num)
    cw = 880
    ch = round(cw * pc.height / pc.width)
    if ch > H - y - 330:
        ch = H - y - 330
        cw = round(ch * pc.width / pc.height)
    shadow_paste(im, pc.resize((cw, ch), Image.LANCZOS), (W - cw) // 2, y, rounded=14)
    y += ch + 44
    shadow_paste(im, cover(slug, 190), 70, y, radius=12, offset=8)
    tx = 300
    d.text((tx, y + 18), line1, font=SERIF_B(46), fill=CREAM)
    yy = y + 82
    for ln in wrap(d, line2, SANS(30), 640):
        d.text((tx, yy), ln, font=SANS(30), fill=SOFT)
        yy += 38
    d.rounded_rectangle([tx, yy + 14, tx + 330, yy + 70], 28, fill=RED)
    t = "Solution dans le livre"
    d.text((tx + (330 - d.textlength(t, font=SANS_B(27))) / 2, yy + 26), t, font=SANS_B(27), fill=CREAM)
    im.save(os.path.join(OUT, name + '.jpg'), quality=92)


def pin_hero(name, slug, label, headline, bullets, theme='navy', accent=GOLD, cover_w=620):
    im = bg(theme, len(name) * 7)
    d = ImageDraw.Draw(im)
    y = spaced(d, label, SANS_B(30), 60, accent, 4) + 24
    y = text_block(d, headline, SERIF_B(70), y, GOLD, width=880, lh=1.1) + 34
    cv = cover(slug, cover_w)
    shadow_paste(im, cv, (W - cover_w) // 2, y, radius=22, offset=16, alpha=190)
    y += cv.height + 46
    for b in bullets:
        d.ellipse([100, y + 15, 116, y + 31], fill=accent)
        for ln in wrap(d, b, SANS(37), 780):
            d.text((138, y), ln, font=SANS(37), fill=CREAM)
            y += 46
        y += 12
    footer_brand(d)
    im.save(os.path.join(OUT, name + '.jpg'), quality=92)


def pin_series5(name, label, headline, sub):
    im = bg('navy', 21)
    d = ImageDraw.Draw(im)
    y = spaced(d, label, SANS_B(28), 56, GOLD, 4) + 22
    y = text_block(d, headline, SERIF_B(70), y, GOLD, width=880, lh=1.1) + 6
    y = text_block(d, sub, SERIF_I(34), y, CREAM, width=840) + 30
    slugs = ['Le-Train-des-Neiges', 'La-Nuit-de-l-Ankou', 'Les-Santons-de-Minuit',
             'Tempete-sur-Belle-Ile', 'Vendanges-tardives']
    cw, gap = 280, 30
    ch = round(cw * 2200 / 1700)
    x0 = (W - 3 * cw - 2 * gap) // 2
    for i, s in enumerate(slugs[:3]):
        shadow_paste(im, cover(s, cw), x0 + i * (cw + gap), y, radius=12, offset=8)
    y2 = y + ch + gap
    x1 = (W - 2 * cw - gap) // 2
    for i, s in enumerate(slugs[3:]):
        shadow_paste(im, cover(s, cw), x1 + i * (cw + gap), y2, radius=12, offset=8)
    text_block(d, "Énigmes logiques à solution unique · dès 12 ans", SANS_B(32), y2 + ch + 36, CREAM)
    footer_brand(d)
    im.save(os.path.join(OUT, name + '.jpg'), quality=92)


def lot3():
    pin_teaser('21_train-enigme-3-decembre', 'Le-Train-des-Neiges', 3, "ÉNIGME DU 3 DÉCEMBRE",
               "Qui a arraché le bouquet de houx ?", "24 énigmes comme celle-ci",
               "Le Train des Neiges, calendrier de l'Avent d'enquête")
    pin_hero('22_train-avent-sans-chocolat', 'Le-Train-des-Neiges', "UN CALENDRIER DE L'AVENT SANS CHOCOLAT",
             "Pour ceux qui préfèrent les énigmes",
             ["Une énigme logique par jour, du 1er au 24 décembre",
              "Un train bloqué par la neige, un coupable à bord",
              "Dès 12 ans · solutions incluses"])
    pin_teaser('23_santons-lettre-pere-noel', 'Les-Santons-de-Minuit', 8, "ÉNIGME DE NOËL · PROVENCE",
               "Qui a écrit la lettre au Père Noël ?", "40 énigmes comme celle-ci",
               "Les Santons de Minuit, une enquête de Noël en Provence")
    pin_series5('24_serie-offrez-une-enquete', "VOUS AIMEZ LE CLUEDO ?",
                "Offrez une enquête à Noël", "5 livres-jeux d'enquête pour adultes, à résoudre soi-même.")
    pin_teaser('25_belle-ile-sardine', 'Tempete-sur-Belle-Ile', 5, "ÉNIGME GRATUITE · BELLE-ÎLE",
               "Qui a enfermé Sardine ?", "40 énigmes comme celle-ci",
               "Tempête sur Belle-Île, une enquête au cœur de la Bretagne")
    pin_teaser('26_train-enigme-4-decembre', 'Le-Train-des-Neiges', 4, "ÉNIGME DU 4 DÉCEMBRE",
               "Qui a pris le sifflet du contrôleur ?", "24 énigmes comme celle-ci",
               "Le Train des Neiges, calendrier de l'Avent d'enquête")
    pin_teaser('27_vendanges-panier-du-midi', 'Vendanges-tardives', 4, "ÉNIGME GRATUITE · ALSACE",
               "Qui a ouvert le panier du midi ?", "40 énigmes comme celle-ci",
               "Vendanges tardives, une enquête dans les vignes d'Alsace")
    pin_hero('28_train-a-offrir-avant-decembre', 'Le-Train-des-Neiges', "À OFFRIR AVANT LE 1ER DÉCEMBRE",
             "Le cadeau qui dure jusqu'à Noël",
             ["Offert fin novembre, il occupe tout le mois de décembre",
              "Une énigme chaque jour, seul ou en famille",
              "Dès 12 ans · solutions incluses"])
    pin_teaser('29_santons-creche-derangee', 'Les-Santons-de-Minuit', 3, "ÉNIGME DE NOËL · PROVENCE",
               "Qui a dérangé la crèche ?", "40 énigmes comme celle-ci",
               "Les Santons de Minuit, une enquête de Noël en Provence")
    pin_hero('30_ankou-veillees-hiver', 'La-Nuit-de-l-Ankou', "VEILLÉES D'HIVER",
             "Des légendes bretonnes à résoudre au coin du feu",
             ["40 énigmes et une enquête finale dans un manoir breton",
              "Des frissons, jamais d'horreur",
              "Dès 12 ans · solutions incluses"], theme='purple', accent=ORANGE)


if __name__ == '__main__':
    lot = sys.argv[1] if len(sys.argv) > 1 else 'lot3'
    OUT = os.path.join(HERE, '..', lot)
    os.makedirs(OUT, exist_ok=True)
    globals()[lot]()
    print(sorted(os.listdir(OUT)))
