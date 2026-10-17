#!/usr/bin/env python3
"""Génère une vidéo TikTok verticale (1080x1920) « Trouve le coupable » à partir
d'une énigme de tiktok-kit/enigmes.json.

Usage : python3 video_enigme.py <slug-livre> <num-enigme> <sortie.mp4>
"""
import json, math, os, random, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

KIT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
W, H, FPS = 1080, 1920, 30
FONTS = "/usr/share/fonts/truetype/crosextra/"
def F(name, size): return ImageFont.truetype(FONTS + name, size)

NAVY_TOP, NAVY_BOT = (24, 21, 52), (39, 31, 80)
GOLD, ORANGE, RED, WHITE, MUTED = (242, 190, 85), (217, 142, 85), (198, 45, 45), (255, 255, 255), (178, 176, 210)
LX, RX = 70, 920  # zone sûre (à droite : boutons TikTok)

# ---------- données ----------
def load(slug, num):
    livres = json.load(open(os.path.join(KIT, "enigmes.json")))
    livre = next(l for l in livres if l["slug"] == slug)
    e = next(x for x in livre["enigmes"] if x["num"] == num)
    return livre, e

def crop_plan(path):
    """Découpe le plan des lieux (cadre noir épais) sur la page d'énigme."""
    im = Image.open(path).convert("L"); a = np.array(im)
    rows = np.where((a[:1300, 100:1150] < 80).sum(1) > 500)[0]
    top, bot = rows.min(), rows.max()
    dark = a[top + 3, :1300] < 80
    runs, start = [], None
    for x, v in enumerate(list(dark) + [False]):
        if v and start is None: start = x
        if not v and start is not None: runs.append((start, x - 1)); start = None
    left, right = max(runs, key=lambda r: r[1] - r[0])
    return Image.open(path).convert("RGB").crop((left - 6, top - 6, right + 7, bot + 7))

# ---------- dessin ----------
def background():
    g = np.linspace(0, 1, H)[:, None, None]
    arr = (np.array(NAVY_TOP) * (1 - g) + np.array(NAVY_BOT) * g).repeat(W, 1)
    bg = Image.fromarray(arr.astype("uint8"))
    d = ImageDraw.Draw(bg); rnd = random.Random(7)
    for _ in range(140):
        x, y, r = rnd.randrange(W), rnd.randrange(H), rnd.choice([1, 1, 1, 2])
        c = rnd.randrange(70, 150)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(c, c, min(255, c + 20)))
    return bg

def wrap(draw, text, font, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= width: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def text_block(draw, xy, text, font, fill, width, spacing=1.25, align="left"):
    x, y = xy; lines = wrap(draw, text, font, width); lh = int(font.size * spacing)
    for ln in lines:
        if align == "center":
            draw.text((x + (width - draw.textlength(ln, font=font)) / 2, y), ln, font=font, fill=fill)
        else:
            draw.text((x, y), ln, font=font, fill=fill)
        y += lh
    return y

def paste_alpha(base, layer, alpha, dy=0):
    if alpha <= 0: return
    if alpha < 1:
        a = layer.getchannel("A").point(lambda v: int(v * alpha)); layer = layer.copy(); layer.putalpha(a)
    base.alpha_composite(layer, (0, int(dy)))

def ease(x): x = max(0, min(1, x)); return 1 - (1 - x) ** 3

# ---------- calques ----------
def layer():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))

def hook_layer(livre, n=4):
    L = layer(); d = ImageDraw.Draw(L)
    text_block(d, (LX, 560), "ÉNIGME DU JOUR", F("Carlito-Bold.ttf", 46), ORANGE, RX - LX, align="center")
    y = text_block(d, (LX, 640), "Trouve le coupable", F("Caladea-Bold.ttf", 118), GOLD, RX - LX, 1.05, "center")
    text_block(d, (LX, y + 40), f"3 suspects. {n} indices. 1 seul coupable.", F("Carlito-Regular.ttf", 50), WHITE, RX - LX, align="center")
    text_block(d, (LX, y + 120), "Tu as 10 secondes à la fin.", F("Carlito-Italic.ttf", 44), MUTED, RX - LX, align="center")
    return L

def incident_layer(livre, e):
    L = layer(); d = ImageDraw.Draw(L)
    text_block(d, (LX, 470), livre["livre"].upper(), F("Carlito-Bold.ttf", 40), ORANGE, RX - LX)
    y = text_block(d, (LX, 530), e["titre"], F("Caladea-Bold.ttf", 96), GOLD, RX - LX, 1.08)
    d.rectangle((LX, y + 25, LX + 120, y + 31), fill=RED)
    text_block(d, (LX, y + 70), e["incident"], F("Caladea-Italic.ttf", 58), WHITE, RX - LX, 1.3)
    return L

def board_layers(livre, e, plan):
    """Renvoie (fond du plateau, liste des calques d'indices, calque question, y_question)."""
    base = layer(); d = ImageDraw.Draw(base)
    text_block(d, (LX, 235), livre["livre"].upper(), F("Carlito-Bold.ttf", 36), ORANGE, RX - LX)
    yt = text_block(d, (LX, 278), e["titre"], F("Caladea-Bold.ttf", 76), GOLD, RX - LX, 1.05)
    # carte blanche avec le plan
    cw = RX - LX; pw = cw - 50; ph = int(plan.height * pw / plan.width)
    card = Image.new("RGBA", (cw, ph + 50), (252, 249, 245, 255))
    card.paste(plan.resize((pw, ph), Image.LANCZOS), (25, 25))
    mask = Image.new("L", card.size, 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, *card.size), 22, fill=255)
    card.putalpha(mask)
    ytop = yt + 20
    base.alpha_composite(card, (LX, ytop))
    y = ytop + card.height + 30
    lab, val = F("Carlito-Bold.ttf", 34), F("Carlito-Bold.ttf", 52)
    suspects = sorted(e["solution"].keys())
    objets = sorted(v["objet"][0] for v in e["solution"].values())
    d.text((LX, y), "SUSPECTS", font=lab, fill=MUTED)
    d.text((LX + 200, y - 11), "  ·  ".join(suspects), font=val, fill=WHITE)
    y += 70
    d.text((LX, y), "OBJETS", font=lab, fill=MUTED)
    y = text_block(d, (LX + 200, y - 7), ", ".join(objets), F("Carlito-Regular.ttf", 46), WHITE, RX - LX - 200, 1.2)
    y += 30
    d.text((LX, y), "INDICES", font=lab, fill=MUTED); y += 56
    clues = []
    n = len(e["indices"])
    fs = 50 if n <= 4 else (46 if n == 5 else 42)
    font = F("Carlito-Regular.ttf", fs); numf = F("Carlito-Bold.ttf", fs)
    for i, c in enumerate(e["indices"]):
        C = layer(); cd = ImageDraw.Draw(C)
        cd.text((LX, y), f"{i+1}.", font=numf, fill=GOLD)
        y = text_block(cd, (LX + 58, y), c, font, WHITE, RX - LX - 58, 1.2) + 16
        clues.append(C)
    return base, clues, y + 14

def question_layer(e, y, remaining, frac):
    L = layer(); d = ImageDraw.Draw(L)
    box = (LX - 10, y, RX + 10, y + 150)
    d.rounded_rectangle(box, 26, fill=RED)
    q = f"Qui se trouvait {e['question_lieu'][1]} ?"
    qf = F("Caladea-Bold.ttf", 50)
    while d.textlength(q, font=qf) > RX - LX - 150 and qf.size > 34: qf = F("Caladea-Bold.ttf", qf.size - 2)
    lines = wrap(d, q, qf, RX - LX - 150)
    ty = y + 75 - len(lines) * qf.size * 0.6
    for ln in lines: d.text((LX + 20, ty), ln, font=qf, fill=WHITE); ty += int(qf.size * 1.15)
    # minuteur
    cx, cy, r = RX - 60, y + 75, 52
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(140, 25, 25))
    if frac > 0:
        d.pieslice((cx - r, cy - r, cx + r, cy + r), -90, -90 + 360 * frac, fill=GOLD)
    d.ellipse((cx - r + 9, cy - r + 9, cx + r - 9, cy + r - 9), fill=RED)
    nf = F("Carlito-Bold.ttf", 54); s = str(remaining)
    d.text((cx - d.textlength(s, font=nf) / 2, cy - 33), s, font=nf, fill=WHITE)
    return L

def cta_layer(livre, cover, n_enigmes):
    L = layer(); d = ImageDraw.Draw(L)
    y = text_block(d, (LX, 230), "Ton suspect en commentaire", F("Caladea-Bold.ttf", 82), GOLD, RX - LX, 1.05, "center")
    text_block(d, (LX, y + 20), "Réponse demain, dans les commentaires.", F("Carlito-Regular.ttf", 46), WHITE, RX - LX, align="center")
    cw = 470; ch = int(cover.height * cw / cover.width)
    c = cover.resize((cw, ch), Image.LANCZOS).convert("RGBA")
    sh = Image.new("RGBA", (cw + 80, ch + 80), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle((40, 50, cw + 40, ch + 50), fill=(0, 0, 0, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    x0 = (LX + RX) // 2 - cw // 2; y0 = y + 130
    L.alpha_composite(sh, (x0 - 40, y0 - 40)); L.alpha_composite(c, (x0, y0))
    y2 = y0 + ch + 50
    y2 = text_block(d, (LX, y2), f"{n_enigmes} énigmes comme celle-ci", F("Caladea-Bold.ttf", 62), WHITE, RX - LX, 1.1, "center")
    bw, bh = 520, 96; bx = (LX + RX) // 2 - bw // 2
    d.rounded_rectangle((bx, y2 + 20, bx + bw, y2 + 20 + bh), 48, fill=RED)
    bf = F("Carlito-Bold.ttf", 48); t = "Lien en bio"
    d.text((bx + (bw - d.textlength(t, font=bf)) / 2, y2 + 38), t, font=bf, fill=WHITE)
    text_block(d, (LX, y2 + 140), "@maelkerjean", F("Carlito-Bold.ttf", 40), MUTED, RX - LX, align="center")
    return L

# ---------- son (synthétisé, libre de droits) ----------
def make_audio(path, dur, clue_times, tick_start, tick_n, sr=44100):
    t = np.arange(int(dur * sr)) / sr
    pad = np.zeros_like(t)
    for f, a in [(55, .5), (82.4, .35), (110, .25), (130.8, .12), (164.8, .08)]:
        pad += a * np.sin(2 * np.pi * f * t + 0.3 * np.sin(2 * np.pi * 0.07 * t))
    pad *= 0.55 + 0.45 * np.sin(2 * np.pi * 0.11 * t) ** 2
    pad *= np.minimum(1, t / 1.5) * np.minimum(1, (dur - t) / 1.5)
    out = 0.10 * pad / np.abs(pad).max()
    def add(at, sig):
        i = int(at * sr); j = min(len(out), i + len(sig)); out[i:j] += sig[: j - i]
    tt = np.arange(int(0.9 * sr)) / sr
    ding = (np.sin(2 * np.pi * 880 * tt) + .4 * np.sin(2 * np.pi * 1320 * tt)) * np.exp(-tt * 6) * 0.10
    for c in clue_times: add(c, ding)
    tk = np.arange(int(0.05 * sr)) / sr
    tick = np.sin(2 * np.pi * 2000 * tk) * np.exp(-tk * 120) * 0.22
    for k in range(tick_n): add(tick_start + k, tick)
    tl = np.arange(int(1.6 * sr)) / sr
    reveal = sum(np.sin(2 * np.pi * f * tl) for f in (523, 659, 784)) * np.exp(-tl * 2.5) * 0.06
    add(tick_start + tick_n, reveal)
    pcm = (np.clip(out, -1, 1) * 32767).astype("<i2")
    st = np.stack([pcm, pcm], 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(st.tobytes())

# ---------- montage ----------
def build(slug, num, out):
    livre, e = load(slug, num)
    plan = crop_plan(os.path.join(KIT, e["image"]))
    cover = Image.open(os.path.join(KIT, livre["couverture"])).convert("RGB")
    n_enigmes = 24 if "Neiges" in livre["livre"] else 40
    bg = background()
    n = len(e["indices"])
    hook = hook_layer(livre, n)
    inc = incident_layer(livre, e)
    base, clues, qy = board_layers(livre, e, plan)
    cta = cta_layer(livre, cover, n_enigmes)

    T_HOOK, T_INC, T_BOARD, T_CLUE, T_COUNT, T_CTA = 2.8, 6.0, 2.5, 3.6, 10, 5.0
    t_inc = T_HOOK; t_board = t_inc + T_INC; t_clues = t_board + T_BOARD
    t_q = t_clues + n * T_CLUE; t_cta = t_q + T_COUNT; dur = t_cta + T_CTA
    clue_times = [t_clues + i * T_CLUE for i in range(n)]

    tmp = out + ".wav"
    make_audio(tmp, dur, clue_times, t_q, T_COUNT)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", tmp, "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    bg_rgba = bg.convert("RGBA")
    qcache = {}
    for fi in range(int(dur * FPS)):
        t = fi / FPS
        fr = bg_rgba.copy()
        if t < t_inc + 0.4:
            a = min(ease(t / 0.5), 1 - ease((t - t_inc + 0.1) / 0.4)) if t > 0.3 else ease(t / 0.5)
            paste_alpha(fr, hook, a, (1 - ease(t / 0.6)) * 40)
        if t_inc <= t < t_board + 0.4:
            a = min(ease((t - t_inc) / 0.5), 1 - ease((t - t_board + 0.1) / 0.4))
            paste_alpha(fr, inc, a, (1 - ease((t - t_inc) / 0.6)) * 40)
        if t_board <= t < t_cta + 0.4:
            fade_out = 1 - ease((t - t_cta + 0.1) / 0.4)
            paste_alpha(fr, base, min(ease((t - t_board) / 0.6), fade_out))
            for i, C in enumerate(clues):
                tc = clue_times[i]
                if t >= tc: paste_alpha(fr, C, min(ease((t - tc) / 0.4), fade_out), (1 - ease((t - tc) / 0.4)) * 25)
            if t >= t_q:
                el = t - t_q; rem = max(1, T_COUNT - int(el)); frac = min(1, el / T_COUNT)
                key = (rem, round(frac * 60))
                if key not in qcache: qcache[key] = question_layer(e, qy, rem, key[1] / 60)
                paste_alpha(fr, qcache[key], min(ease(el / 0.4), fade_out), (1 - ease(el / 0.4)) * 30)
        if t >= t_cta:
            paste_alpha(fr, cta, ease((t - t_cta) / 0.6), (1 - ease((t - t_cta) / 0.6)) * 40)
        p.stdin.write(fr.convert("RGB").tobytes())
    p.stdin.close(); p.wait(); os.remove(tmp)
    return dict(duree=round(dur, 1), coupable=e["coupable"], titre=e["titre"])

if __name__ == "__main__":
    print(build(sys.argv[1], int(sys.argv[2]), sys.argv[3]))
