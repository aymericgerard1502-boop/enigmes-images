#!/usr/bin/env python3
"""Format « mini-histoire » : scène animée (style des couvertures) avec Rose et Sardine,
3 temps d'histoire, puis l'énigme avec minuteur et l'écran final.

Usage : python3 story_video.py <slug-livre> <num-enigme> <sortie.mp4>
"""
import math, os, random, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import video_enigme as V
from video_enigme import W, H, FPS, F, GOLD, ORANGE, RED, WHITE, MUTED, LX, RX, ease, text_block, paste_alpha

INK = (13, 11, 31)            # silhouettes
INK2 = (22, 19, 46)
CREAM = (250, 240, 214)
WARM = (255, 205, 110)
GROUND_Y = 1700               # pieds des personnages

# ---------------------------------------------------------------- décors
def sky(top=(18, 16, 42), bot=(44, 36, 88)):
    g = np.linspace(0, 1, H)[:, None, None]
    arr = (np.array(top) * (1 - g) + np.array(bot) * g).repeat(W, 1)
    return Image.fromarray(arr.astype("uint8")).convert("RGBA")

def stars(seed=3, n=120, ymax=1000):
    rnd = random.Random(seed)
    return [(rnd.randrange(W), rnd.randrange(ymax), rnd.choice([1, 1, 2]), rnd.random() * 6.28) for _ in range(n)]

def draw_stars(d, st, t):
    for x, y, r, ph in st:
        c = int(130 + 90 * (0.5 + 0.5 * math.sin(t * 2 + ph)))
        d.ellipse((x - r, y - r, x + r, y + r), fill=(c, c, min(255, c + 25)))

def mountains(d):
    d.polygon([(0, 1080), (160, 880), (330, 1010), (520, 780), (720, 990), (880, 860), (1080, 1000), (1080, 1300), (0, 1300)], fill=(58, 56, 110))
    for px, py in [(160, 880), (520, 780), (880, 860)]:
        d.polygon([(px, py), (px - 48, py + 55), (px - 18, py + 45), (px, py + 62), (px + 20, py + 44), (px + 50, py + 56)], fill=(225, 228, 245))
    d.polygon([(0, 1180), (260, 1030), (470, 1150), (700, 1000), (930, 1130), (1080, 1060), (1080, 1350), (0, 1350)], fill=(40, 38, 82))

def pine(d, x, base, h, col=INK2):
    for k in range(3):
        w = h * (0.42 - k * 0.1); yt = base - h + k * h * 0.22
        d.polygon([(x, yt), (x - w, yt + h * 0.45), (x + w, yt + h * 0.45)], fill=col)
    d.rectangle((x - 6, base - 12, x + 6, base), fill=col)

def scene_train_static():
    im = sky(); d = ImageDraw.Draw(im)
    mountains(d)
    for x, h in [(40, 260), (120, 200), (990, 240), (1060, 180)]:
        pine(d, x, 1360, h)
    # rails
    d.rectangle((0, 1372, W, 1382), fill=(70, 66, 120))
    # quai
    d.rectangle((0, 1400, W, H), fill=(33, 29, 66))
    d.rectangle((0, 1400, W, 1412), fill=GOLD)
    for x in range(0, W, 120):
        d.line((x, 1412, x - 160, H), fill=(40, 35, 78), width=3)
    # réverbère
    d.rectangle((842, 1020, 852, 1700), fill=INK)
    d.rectangle((815, 1000, 879, 1028), fill=INK)
    return im

def lamp_glow(t):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    a = int(70 + 15 * math.sin(t * 7) * math.sin(t * 3.1))
    for r, al in [(260, a // 3), (170, a // 2), (90, a)]:
        d.ellipse((847 - r, 1060 - r, 847 + r, 1060 + r), fill=(255, 200, 110, al))
    L = L.filter(ImageFilter.GaussianBlur(40))
    d = ImageDraw.Draw(L); d.rectangle((822, 1028, 872, 1060), fill=(255, 214, 140, 255))
    return L

def train_layer(xoff):
    L = Image.new("RGBA", (W + 1400, 420), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    y0 = 40
    # wagons
    for k in range(3):
        x = 60 + k * 360
        d.rounded_rectangle((x, y0 + 120, x + 340, y0 + 300), 14, fill=(30, 26, 62))
        d.rectangle((x, y0 + 290, x + 340, y0 + 300), fill=INK)
        for j in range(4):
            wx = x + 22 + j * 80
            d.rectangle((wx, y0 + 150, wx + 58, y0 + 210), fill=WARM)
        for wx in (x + 60, x + 280):
            d.ellipse((wx - 24, y0 + 290, wx + 24, y0 + 338), fill=INK)
    # locomotive
    x = 60 + 3 * 360
    d.rectangle((x, y0 + 150, x + 260, y0 + 300), fill=INK)
    d.rectangle((x - 10, y0 + 90, x + 110, y0 + 300), fill=INK)
    d.rectangle((x + 20, y0 + 120, x + 80, y0 + 170), fill=WARM)
    d.rectangle((x + 190, y0 + 70, x + 230, y0 + 150), fill=INK)
    d.polygon([(x + 260, y0 + 300), (x + 320, y0 + 330), (x + 260, y0 + 250)], fill=INK)
    for wx in (x + 50, x + 130, x + 210):
        d.ellipse((wx - 34, y0 + 270, wx + 34, y0 + 338), fill=INK2)
    d.ellipse((x + 236, y0 + 200, x + 256, y0 + 220), fill=WARM)
    return L, x + 210  # position de la cheminée

def smoke(d, cx, t, cy=1030):
    for k in range(7):
        ph = (t * 0.6 + k / 7) % 1
        r = 18 + ph * 40
        x = cx + 20 - ph * 200 + 14 * math.sin(k * 2.1 + t)
        y = cy - 10 - ph * 220
        a = int(120 * (1 - ph) ** 1.5)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(200, 202, 230, a))

def snow(d, t, seed=9, n=170):
    rnd = random.Random(seed)
    for _ in range(n):
        x0, y0, sp, r = rnd.randrange(W), rnd.randrange(H), rnd.uniform(60, 160), rnd.choice([2, 3, 3, 4])
        y = (y0 + t * sp) % H; x = (x0 + 25 * math.sin(t * 0.8 + y0)) % W
        d.ellipse((x - r, y - r, x + r, y + r), fill=(240, 242, 255, 210))

# ---------------------------------------------------------------- personnages
def rose(d, x, base, t):
    """Rose Le Guen : chignon, manteau long, écharpe rouge, canne."""
    sway = 2 * math.sin(t * 1.4)
    d.rectangle((x - 30, base - 70, x - 12, base), fill=INK)
    d.rectangle((x + 10, base - 70, x + 28, base), fill=INK)
    d.polygon([(x - 62, base - 300), (x + 58, base - 300), (x + 92, base - 62), (x - 96, base - 62)], fill=INK)
    d.ellipse((x - 64, base - 330, x + 60, base - 270), fill=INK)  # épaules
    d.rectangle((x - 16, base - 345, x + 14, base - 315), fill=INK)  # cou
    hx, hy = x + sway, base - 385
    d.ellipse((hx - 40, hy - 44, hx + 40, hy + 44), fill=INK)
    d.ellipse((hx - 62, hy - 64, hx - 22, hy - 24), fill=INK)  # chignon
    d.ellipse((hx + 18, hy - 6, hx + 30, hy + 6), outline=GOLD, width=3)  # lunettes
    # écharpe
    d.polygon([(x - 46, base - 330), (x + 44, base - 330), (x + 40, base - 300), (x - 44, base - 300)], fill=RED)
    d.polygon([(x + 18, base - 305), (x + 44, base - 305), (x + 36 + sway * 2, base - 200), (x + 12 + sway * 2, base - 205)], fill=RED)
    # bras + canne
    d.line((x + 50, base - 280, x + 110, base - 170), fill=INK, width=26)
    d.line((x + 112, base - 175, x + 132, base), fill=(90, 62, 40), width=9)
    d.ellipse((x + 98, base - 186, x + 124, base - 160), fill=INK)

def sardine(d, x, base, t):
    """Sardine : basset, longues oreilles, collier rouge, queue qui remue."""
    sniff = 4 * math.sin(t * 9) if (t % 4) < 1.6 else 0
    d.ellipse((x - 110, base - 120, x + 110, base - 40), fill=INK)
    for lx in (x - 80, x - 50, x + 50, x + 80):
        d.rectangle((lx - 10, base - 60, lx + 10, base), fill=INK)
    ang = math.radians(-40 + 25 * math.sin(t * 8))
    tx, ty = x - 104, base - 96
    d.line((tx, ty, tx - 70 * math.cos(ang), ty + 70 * math.sin(ang)), fill=INK, width=14)
    hx, hy = x + 120, base - 118 + sniff
    d.ellipse((hx - 48, hy - 40, hx + 40, hy + 34), fill=INK)
    d.polygon([(hx + 24, hy - 4), (hx + 92, hy + 26), (hx + 84, hy + 50), (hx + 20, hy + 34)], fill=INK)
    d.ellipse((hx + 80, hy + 26, hx + 98, hy + 44), fill=(40, 30, 40))
    d.ellipse((hx - 34, hy - 14, hx + 4, hy + 92), fill=INK2)  # oreille
    d.rectangle((x + 74, base - 120, x + 88, base - 78), fill=RED)  # collier
    d.ellipse((hx + 6, hy - 10, hx + 18, hy + 2), fill=GOLD)

def ticket(d, x, y, t):
    g = int(60 + 40 * math.sin(t * 5))
    d.ellipse((x - 70, y - 40, x + 70, y + 40), fill=(255, 220, 140, g))
    d.polygon([(x - 46, y - 18), (x + 6, y - 22), (x - 2, y - 6), (x + 8, y + 4), (x - 2, y + 20), (x - 46, y + 22)], fill=CREAM)
    d.polygon([(x + 18, y - 20), (x + 52, y - 16), (x + 50, y + 22), (x + 16, y + 18), (x + 24, y + 6), (x + 14, y - 4)], fill=CREAM)
    d.line((x - 38, y - 4, x - 12, y - 4), fill=RED, width=4)

# ---------------------------------------------------------------- histoire
def beats(livre, e):
    noms = sorted(e["solution"].keys())
    return [
        e["incident"],
        "Rose Le Guen mène l'enquête. Sardine a déjà flairé une piste.",
        f"{', '.join(noms[:-1])} ou {noms[-1]} : l'un d'eux ment. À toi de jouer.",
    ]

def caption_layer(text, big=False):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    f = F("Caladea-Bold.ttf", 64 if big else 58)
    lines = V.wrap(d, text, f, RX - LX - 40)
    lh = int(f.size * 1.25); hgt = len(lines) * lh + 60
    y0 = 300
    d.rounded_rectangle((LX - 20, y0, RX + 20, y0 + hgt), 30, fill=(13, 11, 31, 205))
    y = y0 + 30
    for ln in lines:
        d.text((LX + 20, y), ln, font=f, fill=WHITE); y += lh
    return L

def tag_layer(livre):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    bf = F("Carlito-Bold.ttf", 40); t = "ÉNIGME DU JOUR · TROUVE LE COUPABLE"
    bw = int(d.textlength(t, font=bf)) + 60; bx = (W - bw) // 2
    d.rounded_rectangle((bx, 150, bx + bw, 220), 35, fill=GOLD)
    d.text((bx + 30, 164), t, font=bf, fill=V.NAVY_TOP)
    sf = F("Carlito-Bold.ttf", 36)
    s = f"LES ENQUÊTES DE ROSE LE GUEN · {livre['livre'].upper()}"
    d.text(((W - d.textlength(s, font=sf)) / 2, 238), s, font=sf, fill=ORANGE)
    return L

# ---------------------------------------------------------------- montage
def build(slug, num, out, secs=15):
    livre, e = V.load(slug, num)
    plan = V.crop_plan(os.path.join(V.KIT, e["image"]))
    cover = Image.open(os.path.join(V.KIT, livre["couverture"])).convert("RGB")
    n_enigmes = 24 if "Neiges" in livre["livre"] else 40
    static = scene_train_static()
    st = stars()
    train, chimney = train_layer(0)
    caps = [caption_layer(b, i == 0) for i, b in enumerate(beats(livre, e))]
    tag = tag_layer(livre)
    base, clues, qy = V.board_layers(livre, e, plan)
    board = Image.new("RGBA", (W, H), (0, 0, 0, 0)); board.alpha_composite(base)
    for C in clues: board.alpha_composite(C)
    board.alpha_composite(V.banner_layer(secs))
    cta = V.cta_layer(livre, cover, n_enigmes, sorted(e["solution"].keys()))

    B = [0.0, 4.2, 7.6, 11.0]          # début de chaque temps / fin de l'histoire
    t_board = B[3]; t_cta = t_board + secs; dur = t_cta + 4.5
    tmp = out + ".wav"
    V.make_audio(tmp, dur, [B[1], B[2]], t_board, secs)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", tmp, "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    qcache = {}
    for fi in range(int(dur * FPS)):
        t = fi / FPS
        fr = static.copy(); d = ImageDraw.Draw(fr, "RGBA")
        draw_stars(d, st, t)
        fr.alpha_composite(lamp_glow(t))
        xt = int(-1400 * (1 - ease(min(1, t / 4.0)))) + 0     # le train entre en gare
        fr.alpha_composite(train, (xt - 60, 1010))
        smoke(d, xt - 60 + chimney, t)
        rose(d, 250, GROUND_Y, t)
        sardine(d, 560, GROUND_Y, t)
        if t > B[1]:
            ticket(d, 760, GROUND_Y - 14, t)
        snow(d, t)
        # histoire
        if t < t_board + 0.4:
            paste_alpha(fr, tag, 1 - ease((t - t_board + 0.1) / 0.4) if t > t_board - 0.1 else 1)
            for i in range(3):
                if B[i] <= t < B[i + 1] + 0.3:
                    a = min(1 if i == 0 else ease((t - B[i]) / 0.35), 1 - ease((t - B[i + 1] + 0.05) / 0.3))
                    paste_alpha(fr, caps[i], a, 0 if i == 0 else (1 - ease((t - B[i]) / 0.35)) * 20)
        # énigme
        if t >= t_board:
            dim = Image.new("RGBA", (W, H), (13, 11, 31, int(225 * ease((t - t_board) / 0.5))))
            fr.alpha_composite(dim)
            if t < t_cta + 0.4:
                el = t - t_board; rem = max(1, secs - int(el)); key = (rem, round(min(1, el / secs) * 90))
                if key not in qcache: qcache[key] = V.question_layer(e, qy, rem, key[1] / 90)
                fo = 1 - ease((t - t_cta + 0.1) / 0.4) if t > t_cta - 0.1 else 1
                paste_alpha(fr, board, min(ease(el / 0.5), fo))
                paste_alpha(fr, qcache[key], min(ease(el / 0.5), fo))
        if t >= t_cta:
            fr.alpha_composite(Image.new("RGBA", (W, H), (13, 11, 31, int(120 * ease((t - t_cta) / 0.5)))))
            paste_alpha(fr, cta, ease((t - t_cta) / 0.6), (1 - ease((t - t_cta) / 0.6)) * 40)
        p.stdin.write(fr.convert("RGB").tobytes())
    p.stdin.close(); p.wait(); os.remove(tmp)
    return dict(duree=round(dur, 1), coupable=e["coupable"], titre=e["titre"])

if __name__ == "__main__":
    print(build(sys.argv[1], int(sys.argv[2]), sys.argv[3]))


# ================================================================ décors par livre
def _rain(d, t, seed=5, n=140):
    rnd = random.Random(seed)
    for _ in range(n):
        x0, y0, sp = rnd.randrange(W + 300), rnd.randrange(H), rnd.uniform(900, 1400)
        y = (y0 + t * sp) % H; x = (x0 - (y * 0.35)) % (W + 300) - 150
        d.line((x, y, x - 14, y + 42), fill=(190, 205, 235, 150), width=3)

def _clouds(d, t, cols=((30, 36, 66, 230), (40, 46, 80, 220))):
    for k, (cy, sp, sz) in enumerate([(260, 18, 1.0), (420, 30, 1.3), (600, 12, 0.9)]):
        cx = (k * 400 + t * sp) % (W + 700) - 350
        for dx, dy, r in [(0, 0, 110), (120, -30, 130), (250, 10, 100), (-110, 20, 90)]:
            rr = r * sz
            d.ellipse((cx + dx - rr, cy + dy - rr * 0.6, cx + dx + rr, cy + dy + rr * 0.6), fill=cols[k % 2])

def scene_belle_ile():
    im = sky((12, 16, 36), (30, 42, 76)); d = ImageDraw.Draw(im)
    d.polygon([(560, 1290), (650, 1190), (780, 1150), (940, 1160), (1080, 1210), (1080, 1300)], fill=INK)
    x = 860
    d.polygon([(x - 62, 1180), (x + 62, 1180), (x + 42, 760), (x - 42, 760)], fill=CREAM)
    for k in range(3):
        y1 = 1180 - 140 * k - 70; y2 = y1 - 70
        f1 = 62 - (1180 - y1) * 20 / 420; f2 = 62 - (1180 - y2) * 20 / 420
        d.polygon([(x - f1, y1), (x + f1, y1), (x + f2, y2), (x - f2, y2)], fill=RED)
    d.rectangle((x - 50, 752, x + 50, 770), fill=INK)
    d.rectangle((x - 34, 690, x + 34, 752), fill=GOLD)
    d.polygon([(x - 46, 690), (x + 46, 690), (x, 640)], fill=INK)
    d.rectangle((0, 1290, W, 1470), fill=(22, 38, 70))
    d.rectangle((0, 1460, W, H), fill=(34, 32, 60))
    d.rectangle((0, 1460, W, 1472), fill=CREAM)
    for k in range(9):
        d.line((k * 130, 1472, k * 130 - 90, H), fill=(28, 26, 52), width=4)
    def back(fr, dd, t):
        _clouds(dd, t)
        ang = math.radians(200 + 30 * math.sin(t * 0.9))
        for spread, al in [(0.16, 18), (0.08, 26)]:
            p1 = (x + 1600 * math.cos(ang - spread), 721 + 1600 * math.sin(ang - spread))
            p2 = (x + 1600 * math.cos(ang + spread), 721 + 1600 * math.sin(ang + spread))
            dd.polygon([(x, 721), p1, p2], fill=(255, 230, 150, al))
        for k in range(6):
            yy = 1300 + k * 28; ph = t * (1.6 + k * 0.3) + k
            pts = [(xx, yy + 8 * math.sin(xx / 70 + ph)) for xx in range(0, W + 40, 40)]
            dd.line(pts, fill=(70, 100, 150, 170), width=4)
        if (t % 7.3) < 0.12:
            fr.alpha_composite(Image.new("RGBA", (W, H), (230, 235, 255, 55)))
    def front(fr, dd, t): _rain(dd, t)
    return dict(static=im, back=back, front=front)

def scene_vendanges():
    im = sky((14, 14, 38), (46, 38, 86)); d = ImageDraw.Draw(im)
    d.ellipse((800, 250, 940, 390), fill=CREAM); d.ellipse((835, 260, 935, 360), fill=(228, 218, 190))
    d.polygon([(0, 1010), (200, 880), (420, 960), (620, 900), (860, 1000), (1080, 930), (1080, 1300), (0, 1300)], fill=(40, 38, 84))
    cx = 230; d.rectangle((cx - 70, 820, cx + 50, 900), fill=INK)
    for k in range(5): d.rectangle((cx - 70 + k * 26, 802, cx - 56 + k * 26, 822), fill=INK)
    d.rectangle((cx + 10, 760, cx + 50, 830), fill=INK)
    d.polygon([(0, 1150), (300, 1040), (640, 1110), (1080, 1020), (1080, 1460), (0, 1460)], fill=(56, 52, 112))
    for r in range(9):
        y = 1080 + r * 42
        for xx in range(-40, W, 34):
            d.ellipse((xx, y + (xx % 3) * 2, xx + 18, y + 12), fill=(38, 34, 80))
    houses = [(60, 190), (280, 170), (470, 210), (700, 180), (900, 200)]
    for hx, hw in houses:
        top = 1240
        d.rectangle((hx, top, hx + hw, 1460), fill=(30, 26, 60))
        d.polygon([(hx - 14, top), (hx + hw / 2, top - 120), (hx + hw + 14, top)], fill=INK)
        for xx in (hx + 20, hx + hw - 70):
            d.rectangle((xx, top + 50, xx + 50, top + 110), fill=WARM)
        d.line((hx, top + 140, hx + hw, top + 140), fill=(90, 70, 60), width=6)
        d.line((hx + 10, top + 140, hx + hw / 2, top + 40), fill=(90, 70, 60), width=6)
        d.line((hx + hw - 10, top + 140, hx + hw / 2, top + 40), fill=(90, 70, 60), width=6)
    d.rectangle((0, 1460, W, H), fill=(32, 28, 62)); d.rectangle((0, 1460, W, 1472), fill=GOLD)
    def back(fr, dd, t):
        g = int(18 + 6 * math.sin(t * 2))
        for r in (150, 120, 95):
            dd.ellipse((870 - r, 320 - r, 870 + r, 320 + r), fill=(250, 240, 214, g))
    def front(fr, dd, t):
        rnd = random.Random(4)
        for _ in range(26):
            x0, y0, sp = rnd.randrange(W), rnd.randrange(H), rnd.uniform(70, 130)
            y = (y0 + t * sp) % H; x = (x0 + 60 * math.sin(t * 1.3 + y0)) % W
            a = t * 3 + y0; col = rnd.choice([(214, 120, 50, 230), (190, 60, 50, 230), (240, 180, 70, 230)])
            dd.polygon([(x + 12 * math.cos(a), y + 12 * math.sin(a)), (x + 6 * math.cos(a + 2), y + 6 * math.sin(a + 2)),
                        (x - 12 * math.cos(a), y - 12 * math.sin(a)), (x + 6 * math.cos(a - 2), y + 6 * math.sin(a - 2))], fill=col)
    return dict(static=im, back=back, front=front)

def scene_santons():
    im = sky((16, 14, 40), (42, 34, 82)); d = ImageDraw.Draw(im)
    for cx in (90, 1000):
        d.ellipse((cx - 34, 980, cx + 34, 1440), fill=INK)
    blocks = [(0, 1210, 200), (180, 1170, 170), (520, 1190, 200), (700, 1230, 190), (870, 1180, 210)]
    wins = []
    for bx, top, bw in blocks:
        d.rectangle((bx, top, bx + bw, 1460), fill=(30, 26, 60))
        d.polygon([(bx - 10, top), (bx + bw + 10, top), (bx + bw, top - 26), (bx, top - 26)], fill=(150, 70, 50))
        for k in range(2):
            wx = bx + 30 + k * (bw - 90); wins.append((wx, top + 60))
    tx = 400
    d.rectangle((tx - 70, 860, tx + 70, 1460), fill=CREAM)
    d.polygon([(tx - 80, 860), (tx + 80, 860), (tx, 760)], fill=(150, 70, 50))
    d.ellipse((tx - 42, 920, tx + 42, 1004), fill=(240, 230, 200), outline=INK, width=6)
    d.line((tx, 962, tx, 932), fill=INK, width=5); d.line((tx, 962, tx + 22, 962), fill=INK, width=5)
    d.rectangle((tx - 28, 1060, tx + 28, 1160), fill=INK)
    d.rectangle((0, 1460, W, H), fill=(36, 30, 64)); d.rectangle((0, 1460, W, 1472), fill=GOLD)
    for r in range(6):
        for c in range(14):
            d.rounded_rectangle((c * 82 + (r % 2) * 41 - 20, 1490 + r * 70, c * 82 + (r % 2) * 41 + 50, 1540 + r * 70), 10, outline=(46, 40, 80), width=3)
    def back(fr, dd, t):
        s = 34 + 8 * math.sin(t * 3); cx, cy = 880, 300
        dd.polygon([(cx, cy - s * 2), (cx + s * 0.35, cy - s * 0.35), (cx + s * 2, cy), (cx + s * 0.35, cy + s * 0.35),
                    (cx, cy + s * 2), (cx - s * 0.35, cy + s * 0.35), (cx - s * 2, cy), (cx - s * 0.35, cy - s * 0.35)], fill=GOLD)
        for k, (wx, wy) in enumerate(wins):
            on = 0.5 + 0.5 * math.sin(t * 1.7 + k * 1.3) > 0.15
            dd.rectangle((wx, wy, wx + 46, wy + 60), fill=WARM if on else (60, 50, 70))
        pts = [(xx, 1120 + 90 * ((xx - 540) / 540) ** 2) for xx in range(0, W + 1, 20)]
        dd.line(pts, fill=(20, 18, 40), width=3)
        cols = [RED, GOLD, (90, 214, 200), (255, 140, 200)]
        for k, (xx, yy) in enumerate(pts[1::3]):
            on = math.sin(t * 4 + k * 0.9) > -0.3
            c = cols[k % 4] if on else (60, 56, 80)
            dd.ellipse((xx - 9, yy + 4, xx + 9, yy + 22), fill=c)
    def front(fr, dd, t):
        rnd = random.Random(11)
        for _ in range(40):
            x0, y0 = rnd.randrange(W), rnd.randrange(1300)
            a = int(120 + 120 * math.sin(t * 2 + x0))
            if a > 0: dd.ellipse((x0 - 2, y0 - 2, x0 + 2, y0 + 2), fill=(255, 240, 200, min(255, a)))
    return dict(static=im, back=back, front=front)

def scene_train():
    im = scene_train_static(); st = stars(); tr, chim = train_layer(0)
    def back(fr, dd, t):
        draw_stars(dd, st, t); fr.alpha_composite(lamp_glow(t))
        xt = int(-1400 * (1 - ease(min(1, t / 3.5))))
        fr.alpha_composite(tr, (xt - 60, 1010)); smoke(dd, xt - 60 + chim, t)
    def front(fr, dd, t): snow(dd, t)
    return dict(static=im, back=back, front=front)

def make_scene(slug):
    return {"Le-Train-des-Neiges": scene_train, "Tempete-sur-Belle-Ile": scene_belle_ile,
            "Vendanges-tardives": scene_vendanges, "Les-Santons-de-Minuit": scene_santons}.get(slug, scene_train)()
