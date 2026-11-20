#!/usr/bin/env python3
"""Arène — format « Si ça passe » : voix off, sous-titres mot à mot, cartes animées, arbitre narrateur.
Usage : python3 video_si.py <episode.json> <sortie.mp4> [dossier_voix]
Le dossier de voix contient les modèles Piper (.onnx + .onnx.json). Par défaut : $ARENE_VOIX ou ./voix"""
import json, math, os, re, subprocess, sys, tempfile, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import musique

W, H, FPS = 1080, 1920, 30
F = '/usr/share/fonts/opentype/inter/'
BLACKI = F + 'InterDisplay-BlackItalic.otf'
BLACK = F + 'InterDisplay-Black.otf'
XBOLD = F + 'InterDisplay-ExtraBold.otf'
BOLD = F + 'Inter-Bold.otf'
SEMI = F + 'Inter-SemiBold.otf'
MONO = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'
BG = (13, 13, 15)
INK = (20, 20, 22)
CREAM = (243, 238, 226)
WHITE = (250, 248, 244)
GREY = (120, 118, 114)
DIM = (92, 90, 88)
RED = (226, 45, 38)
DRED = (150, 22, 24)
GREEN = (46, 170, 98)
SKIN = (238, 196, 160)
SKIN_D = (214, 166, 128)
HAIR = (52, 38, 30)
X0, X1 = 80, 940

_f = {}
def font(p, s):
    if (p, s) not in _f:
        _f[(p, s)] = ImageFont.truetype(p, s)
    return _f[(p, s)]

def ease(x):
    x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3

def ease_back(x):
    x = max(0.0, min(1.0, x)); c = 1.7
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

def fr_typo(t):
    t = re.sub(r'(\d) (?=\d)', '\\1\u00a0', t)
    t = re.sub(r' (?=[€%:?!;»])', '\u00a0', t)
    return t

# ---------------------------------------------------------------- voix
def synthesize(phrases, voix_dir, voix_cfg):
    """Synthèse phrase par phrase : texte normalisé (prononciation), rythme légèrement varié selon la ponctuation."""
    from piper import PiperVoice, SynthesisConfig
    from prononciation import normaliser, mots_suspects
    model = os.path.join(voix_dir, voix_cfg['modele'] + '.onnx')
    v = PiperVoice.load(model)
    base = voix_cfg.get('vitesse', 0.9)
    sr = None; out = []
    for ph in phrases:
        txt = normaliser(ph['dit'])
        for w, p in mots_suspects(txt, v):
            print(f'⚠ prononciation à vérifier : « {w} » → {p}', file=sys.stderr)
        ls = base + (0.04 if txt.rstrip().endswith('?') else 0.0)
        cfg = SynthesisConfig(speaker_id=voix_cfg.get('locuteur'), length_scale=ls, noise_scale=0.62, noise_w_scale=0.82)
        chunks = list(v.synthesize(txt, cfg))
        sr = chunks[0].sample_rate
        a = np.concatenate([c.audio_float_array for c in chunks]).astype(np.float32)
        env = np.abs(a) > 0.02
        if env.any():
            i0 = max(0, np.argmax(env) - int(0.03 * sr)); i1 = min(len(a), len(a) - np.argmax(env[::-1]) + int(0.08 * sr))
            a = a[i0:i1]
        out.append(a)
    return out, sr

SR_OUT = 48000

def traiter_voix(voice, sr):
    """Chaîne studio : rééchantillonnage 48 kHz, chaleur, présence, de-esser, compression douce, petite pièce."""
    tmpd = tempfile.mkdtemp(); fin = os.path.join(tmpd, 'v_in.wav'); fout = os.path.join(tmpd, 'v_out.wav')
    with wave.open(fin, 'wb') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr)
        wf.writeframes((np.clip(voice, -1, 1) * 32767).astype(np.int16).tobytes())
    chain = ('aresample=48000:resampler=soxr:precision=28,highpass=f=75,lowpass=f=10500,'
             'equalizer=f=170:t=q:w=0.9:g=2.5,equalizer=f=450:t=q:w=1.2:g=-2,equalizer=f=3200:t=q:w=1.4:g=2.5,'
             'deesser=i=0.35:m=0.5:f=0.5,acompressor=threshold=0.1:ratio=3:attack=8:release=120:makeup=1.8,'
             'aecho=0.9:0.9:22|41:0.07|0.04')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', fin, '-af', chain, '-ac', '1', '-ar', str(SR_OUT), fout], check=True)
    with wave.open(fout) as wf:
        y = np.frombuffer(wf.readframes(wf.getnframes()), np.int16).astype(np.float32) / 32768
    return y

def sifflet(sr, dur=0.34):
    """Coup de sifflet d'arbitre synthétique (trille)."""
    t = np.arange(int(dur * sr)) / sr
    trille = 0.55 + 0.45 * np.sign(np.sin(2 * np.pi * 28 * t))
    ton = np.sin(2 * np.pi * 3050 * t + 6 * np.sin(2 * np.pi * 28 * t)) + 0.25 * np.sin(2 * np.pi * 6100 * t)
    env = np.minimum(1, t / 0.015) * np.minimum(1, (dur - t) / 0.06)
    rng = np.random.default_rng(11)
    souffle = np.convolve(rng.standard_normal(len(t)), np.ones(6) / 6, mode='same') * 0.08
    return ((ton * trille + souffle) * env * 0.28).astype(np.float32)

def impact(sr, dur=0.9):
    t = np.arange(int(dur * sr)) / sr
    boom = np.sin(2 * np.pi * np.cumsum(42 + 90 * np.exp(-t * 16)) / sr) * np.exp(-t * 4.5)
    rng = np.random.default_rng(12)
    crack = rng.standard_normal(len(t)) * np.exp(-t * 60) * 0.35
    return ((boom + crack) * 0.55).astype(np.float32)

def word_timings(text, dur):
    """Répartit les mots affichés sur la durée de la phrase, au prorata des lettres (approximation suffisante)."""
    words = [x for x in text.split(' ') if x]
    w = np.array([len(re.sub(r'[^\wÀ-ÿ€%]', '', x)) + 1.5 for x in words], dtype=float)
    cum = np.concatenate([[0], np.cumsum(w)]) / w.sum() * dur * 0.97
    return [(words[i], cum[i], cum[i + 1]) for i in range(len(words))]

# ---------------------------------------------------------------- arbitre
class Arbitre:
    """Personnage original : arbitre à maillot rayé, sifflet, cartons. Dessiné en vectoriel (x2 puis réduit)."""
    S = 2
    def __init__(self):
        self.w, self.h = 560, 660
    def render(self, t, mouth, geste, gt):
        S = self.S; w, h = self.w * S, self.h * S
        im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        bob = math.sin(t * 2.2) * 6 * S
        cx = w // 2; base = h
        # --- corps (maillot rayé) ---
        top = int(base - 300 * S + bob * 0.4)
        body = Image.new('RGBA', (w, h), (0, 0, 0, 0)); bd = ImageDraw.Draw(body)
        bd.rounded_rectangle((cx - 190 * S, top, cx + 190 * S, base + 60 * S), radius=110 * S, fill=WHITE + (255,))
        stripe = Image.new('RGBA', (w, h), (0, 0, 0, 0)); sd = ImageDraw.Draw(stripe)
        for k in range(-6, 7):
            x = cx + k * 46 * S
            sd.rectangle((x - 11 * S, top, x + 11 * S, base + 60 * S), fill=INK + (255,))
        mask = body.getchannel('A')
        stripe.putalpha(Image.fromarray(np.minimum(np.asarray(stripe.getchannel('A')), np.asarray(mask))))
        im.alpha_composite(body); im.alpha_composite(stripe)
        # col
        d.polygon([(cx - 60 * S, top + 6 * S), (cx, top + 70 * S), (cx + 60 * S, top + 6 * S)], fill=INK + (255,))
        # --- bras ---
        def arm(side, ang, card=None):
            sx = cx + side * 160 * S; sy = top + 70 * S
            L = 170 * S
            ex = sx + side * math.sin(ang) * L; ey = sy - math.cos(ang) * L
            d.line((sx, sy, ex, ey), fill=WHITE + (255,), width=64 * S)
            d.line((sx, sy, ex, ey), fill=INK + (255,), width=4 * S)
            d.ellipse((ex - 34 * S, ey - 34 * S, ex + 34 * S, ey + 34 * S), fill=SKIN + (255,))
            if card:
                cw, ch = 92 * S, 130 * S
                d.rounded_rectangle((ex - cw / 2, ey - ch - 10 * S, ex + cw / 2, ey - 10 * S), radius=10 * S, fill=card + (255,))
                d.ellipse((ex - 34 * S, ey - 34 * S, ex + 34 * S, ey + 34 * S), fill=SKIN + (255,))
        down = math.radians(168)
        if geste == 'carton':
            a = down + (math.radians(10) - down) * ease_back(gt / 0.45)
            arm(-1, down); arm(1, a, card=RED)
        elif geste == 'pointe':
            a = down + (math.radians(70) - down) * ease(gt / 0.35)
            arm(-1, down); arm(1, a)
        elif geste == 'deux':
            a = down + (math.radians(25) - down) * ease_back(gt / 0.45)
            arm(-1, a, card=RED); arm(1, a, card=CREAM)
        elif geste == 'siffle':
            a = down + (math.radians(150) - down) * ease(gt / 0.3)
            arm(-1, down); arm(1, math.radians(150 - 8 * math.sin(gt * 8)))
        else:
            arm(-1, down + math.radians(2 * math.sin(t * 1.7))); arm(1, down - math.radians(2 * math.sin(t * 1.9)))
        # --- tête ---
        hy = top - 150 * S + bob; hr = 128 * S
        d.ellipse((cx - 30 * S, top - 40 * S, cx + 30 * S, top + 20 * S), fill=SKIN_D + (255,))  # cou
        d.ellipse((cx - hr - 14 * S, hy - 10 * S, cx - hr + 26 * S, hy + 50 * S), fill=SKIN_D + (255,))  # oreilles
        d.ellipse((cx + hr - 26 * S, hy - 10 * S, cx + hr + 14 * S, hy + 50 * S), fill=SKIN_D + (255,))
        d.ellipse((cx - hr, hy - hr, cx + hr, hy + hr), fill=SKIN + (255,))
        # cheveux courts
        d.chord((cx - hr - 4 * S, hy - hr - 16 * S, cx + hr + 4 * S, hy + hr * 0.55), 180, 360, fill=HAIR + (255,))
        d.ellipse((cx - hr + 6 * S, hy - 40 * S, cx + hr - 6 * S, hy + hr - 6 * S), fill=SKIN + (255,))
        # yeux + clignement
        blink = ((t + 1.5) % 3.7) < 0.12
        for sx in (-48, 48):
            ex, ey = cx + sx * S, hy + 4 * S
            if blink:
                d.line((ex - 18 * S, ey, ex + 18 * S, ey), fill=INK + (255,), width=6 * S)
            else:
                d.ellipse((ex - 19 * S, ey - 24 * S, ex + 19 * S, ey + 24 * S), fill=WHITE + (255,))
                d.ellipse((ex - 11 * S, ey - 12 * S, ex + 11 * S, ey + 14 * S), fill=INK + (255,))
                d.ellipse((ex - 2 * S, ey - 8 * S, ex + 5 * S, ey - 1 * S), fill=WHITE + (255,))
            lift = 6 * S * min(1.0, mouth * 1.5)
            d.line((ex - 26 * S, ey - 44 * S - lift, ex + 22 * S, ey - 48 * S - lift), fill=HAIR + (255,), width=10 * S)
        # bouche synchronisée sur la voix
        my = hy + 72 * S; mw = 44 * S; mh = (6 + 34 * min(1.0, mouth)) * S
        if geste == 'siffle':
            d.ellipse((cx - 16 * S, my - 16 * S, cx + 16 * S, my + 16 * S), fill=(60, 30, 30, 255))
            d.rounded_rectangle((cx + 4 * S, my - 12 * S, cx + 70 * S, my + 14 * S), radius=8 * S, fill=(200, 200, 205, 255))
        else:
            d.rounded_rectangle((cx - mw / 2, my - mh / 2, cx + mw / 2, my + mh / 2), radius=int(min(mw, mh) / 2), fill=(70, 26, 28, 255))
            if mh > 16 * S:
                d.rectangle((cx - mw / 2 + 6 * S, my - mh / 2 + 2 * S, cx + mw / 2 - 6 * S, my - mh / 2 + 9 * S), fill=WHITE + (255,))
        # sifflet au cordon (au repos)
        if geste != 'siffle':
            d.line((cx - 50 * S, top + 10 * S, cx, top + 110 * S, cx + 50 * S, top + 10 * S), fill=RED + (255,), width=5 * S)
            d.rounded_rectangle((cx - 22 * S, top + 104 * S, cx + 30 * S, top + 130 * S), radius=10 * S, fill=(200, 200, 205, 255))
        return im.resize((int(self.w * 0.85), int(self.h * 0.85)), Image.LANCZOS)

# ---------------------------------------------------------------- cartes
def paper(w, h, tilt=0, label=None):
    """Fiche crème façon dossier."""
    im = Image.new('RGBA', (w + 40, h + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((26, 30, w + 26, h + 30), radius=18, fill=(0, 0, 0, 120))
    d.rounded_rectangle((14, 14, w + 14, h + 14), radius=18, fill=CREAM + (255,))
    for y in range(110, h, 54):
        d.line((44, y, w - 16, y), fill=(222, 214, 198, 255), width=2)
    if label:
        d.text((48, 40), label, font=font(MONO, 30), fill=DRED + (255,))
        d.line((14, 92, w + 14, 92), fill=RED + (255,), width=4)
    return im

def text_center(d, cx, y, txt, f, fill):
    tw = f.getlength(txt); d.text((cx - tw / 2, y), txt, font=f, fill=fill)

def card_titre(c, t, dur):
    im = paper(820, 520, label=c.get('label', 'DOSSIER'))
    d = ImageDraw.Draw(im)
    y = 140
    for line in c['lignes']:
        f = font(BLACK, c.get('taille', 104))
        d.text((54, y), fr_typo(line), font=f, fill=INK + (255,)); y += int(c.get('taille', 104) * 1.05)
    return im, 1.0 if t < 0 else ease_back(t / 0.5)

def card_seuil(c, t, dur):
    im = paper(820, 520, label=c.get('label', 'LA RÈGLE')); d = ImageDraw.Draw(im)
    d.text((54, 128), fr_typo(c['titre']), font=font(XBOLD, 52), fill=INK + (255,))
    bx0, bx1, by = 60, 790, 300
    split = bx0 + (bx1 - bx0) * c.get('part', 0.45)
    p = ease(t / 1.2)
    d.rounded_rectangle((bx0, by, bx1, by + 70), radius=14, fill=(225, 218, 204, 255))
    if p > 0:
        d.rounded_rectangle((bx0, by, bx0 + (split - bx0) * min(1, p * 2), by + 70), radius=14, fill=GREEN + (255,))
    if p > 0.5:
        q = (p - 0.5) * 2
        d.rounded_rectangle((split, by, split + (bx1 - split) * q, by + 70), radius=14, fill=RED + (255,))
    d.line((split, by - 30, split, by + 100), fill=INK + (255,), width=6)
    text_center(d, split, by + 110, fr_typo(c['seuil']), font(BLACK, 54), INK + (255,))
    d.text((bx0, by - 64), c['gauche'], font=font(BOLD, 34), fill=GREEN + (255,))
    f = font(BOLD, 34); d.text((bx1 - f.getlength(c['droite']), by - 64), c['droite'], font=f, fill=RED + (255,))
    return im, ease_back(t / 0.45)

def card_calcul(c, t, dur):
    im = paper(820, 620, label=c.get('label', 'LE CALCUL')); d = ImageDraw.Draw(im)
    rows = c['lignes']  # [libellé, valeur, apparition (fraction de la durée)]
    y = 140
    for lib, val, at in rows:
        a = ease((t - at) / 0.35)
        if a <= 0:
            y += 100; continue
        col = (INK if not val.startswith('−') else RED) + (int(255 * a),)
        d.text((54, y + 10), fr_typo(lib), font=font(SEMI, 38), fill=(70, 66, 60, int(255 * a)))
        f = font(BLACK, 62); vv = fr_typo(val)
        d.text((790 - f.getlength(vv), y), vv, font=f, fill=col)
        y += 100
    if c.get('total'):
        lib, val, at = c['total']; a = ease((t - at) / 0.4)
        if a > 0:
            d.line((54, y + 4, 790, y + 4), fill=INK + (int(255 * a),), width=5)
            d.text((54, y + 34), fr_typo(lib), font=font(XBOLD, 42), fill=INK + (int(255 * a),))
            f = font(BLACK, 92); vv = fr_typo(val)
            d.text((790 - f.getlength(vv), y + 10), vv, font=f, fill=RED + (int(255 * a),))
    return im, ease_back(t / 0.45)

def card_compteur(c, t, dur):
    """Gros chiffre qui défile jusqu'à sa valeur, avec légende."""
    im = Image.new('RGBA', (900, 560), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    p = ease(t / 1.3)
    v = c['valeur'] * p
    txt = c.get('prefixe', '') + (f"{v:,.0f}".replace(',', '\u00a0') if c.get('entier', True) else f"{v:,.2f}".replace(',', '\u00a0').replace('.', ',')) + c.get('suffixe', '')
    f = font(BLACK, c.get('taille', 190))
    col = RED if c.get('rouge', True) else WHITE
    d.text((450 - f.getlength(txt) / 2, 60), txt, font=f, fill=col + (255,))
    y = 60 + c.get('taille', 190) + 40
    for line in c.get('legende', []):
        fl = font(XBOLD, 54); d.text((450 - fl.getlength(fr_typo(line)) / 2, y), fr_typo(line), font=fl, fill=WHITE + (255,)); y += 66
    return im, ease_back(t / 0.35)

def card_cumul(c, t, dur):
    im = paper(820, 560, label=c.get('label', 'ET ÇA S\'ADDITIONNE')); d = ImageDraw.Draw(im)
    vals = c['valeurs']; mx = max(vals)
    n = len(vals); bw = 120; gap = (730 - n * bw) / (n - 1); base = 470
    for i, v in enumerate(vals):
        a = ease((t - 0.25 * i) / 0.5)
        hgt = 300 * v / mx * a
        x = 60 + i * (bw + gap)
        d.rounded_rectangle((x, base - hgt, x + bw, base), radius=10, fill=RED + (255,))
        text_center(d, x + bw / 2, base + 14, c['annees'][i], font(BOLD, 30), INK + (255,))
        if a > 0.9:
            text_center(d, x + bw / 2, base - hgt - 52, fr_typo(f"−{v} €"), font(BLACK, 40), INK + (255,))
    return im, ease_back(t / 0.45)

def card_checks(c, t, dur):
    im = paper(820, 120 + 130 * len(c['lignes']), label=c.get('label', 'À SAVOIR')); d = ImageDraw.Draw(im)
    y = 140
    for i, (ok, line) in enumerate(c['lignes']):
        a = ease((t - i * c.get('pas', 1.2)) / 0.3)
        if a > 0:
            col = GREEN if ok else (GREY if ok is None else RED)
            d.ellipse((54, y + 4, 114, y + 64), fill=col + (int(255 * a),))
            mark = '✓' if ok else ('?' if ok is None else '✕')
            text_center(d, 84, y + 6, mark, font('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 44), WHITE + (int(255 * a),))
            d.text((140, y + 6), fr_typo(line), font=font(XBOLD, 46), fill=INK + (int(255 * a),))
        y += 130
    return im, ease_back(t / 0.45)

def card_camp(c, t, dur):
    im = Image.new('RGBA', (900, 640), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    pour = c['camp'] == 'POUR'
    col = CREAM if pour else RED; fg = INK if pour else WHITE
    tag = font(BLACKI, 120); tw = tag.getlength(c['camp'])
    d.rounded_rectangle((40, 20, 40 + tw + 60, 170), radius=16, fill=col + (255,))
    d.text((70, 22), c['camp'], font=tag, fill=fg + (255,))
    d.text((44, 196), c['qui'], font=font(SEMI, 36), fill=GREY + (255,))
    a = ease((t - 0.5) / 0.35)
    y = 270
    for line in c['lignes']:
        f = font(XBOLD, 64)
        d.text((44, y), fr_typo(line), font=f, fill=WHITE + (int(255 * a),)); y += 80
    return im, ease_back(t / 0.4)

def card_tampon(c, t, dur):
    im = Image.new('RGBA', (900, 640), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    # tampon « REJETÉ » qui s'écrase
    s = 1 + 1.2 * (1 - ease(t / 0.25))
    st = Image.new('RGBA', (700, 220), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
    sd.rounded_rectangle((8, 8, 692, 212), radius=20, outline=RED + (255,), width=14)
    f = font(BLACK, 130); sd.text((350 - f.getlength(c['tampon']) / 2, 30), c['tampon'], font=f, fill=RED + (255,))
    st = st.rotate(-8, expand=True, resample=Image.BICUBIC)
    st = st.resize((int(st.width * s), int(st.height * s)), Image.LANCZOS)
    im.alpha_composite(st, (max(0, 450 - st.width // 2), max(0, 150 - st.height // 2)) if s < 1.5 else (0, 0))
    d.text((60, 330), fr_typo(c['sous']), font=font(SEMI, 40), fill=GREY + (255,))
    a = ease((t - c.get('apres', 1.4)) / 0.4)
    if a > 0:
        f2 = font(BLACK, 92)
        d.rounded_rectangle((50, 410, 50 + f2.getlength(fr_typo(c['suite'])) + 60, 540), radius=16, fill=CREAM + (int(255 * a),))
        d.text((80, 418), fr_typo(c['suite']), font=f2, fill=INK + (int(255 * a),))
    return im, 1.0

def card_cta(c, t, dur):
    im = Image.new('RGBA', (900, 640), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    f = font(BLACKI, 150)
    a1 = ease_back(t / 0.4); a2 = ease_back((t - 0.35) / 0.4)
    for i, (txt, col, fg, a) in enumerate([('POUR', CREAM, INK, a1), ('CONTRE', RED, WHITE, a2)]):
        if a <= 0: continue
        y = 40 + i * 230
        tw = f.getlength(txt)
        box = Image.new('RGBA', (int(tw + 80), 200), (0, 0, 0, 0)); bd = ImageDraw.Draw(box)
        bd.rounded_rectangle((0, 0, tw + 80, 196), radius=20, fill=col + (255,))
        bd.text((40, 6), txt, font=f, fill=fg + (255,))
        sc = max(0.01, a)
        box = box.resize((max(1, int(box.width * sc)), max(1, int(box.height * sc))), Image.LANCZOS)
        im.alpha_composite(box, (60, y))
    d.text((64, 520), fr_typo(c.get('appel', 'Ton camp en commentaire ↓')), font=font(BOLD, 48), fill=WHITE + (255,))
    return im, 1.0

def card_choc(c, t, dur):
    """Ouverture : le chiffre en jeu, énorme, dès l'image 0 ; arrive avec un léger « punch »."""
    im = Image.new('RGBA', (1000, 700), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    # bandeau de contexte : on montre d'emblée que c'est une loi en débat, pas une offre
    tag = fr_typo(c.get('tag', 'SI LA LOI PASSE'))
    ft = font(MONO, 34); tw = ft.getlength(tag)
    d.rounded_rectangle((500 - tw / 2 - 22, 0, 500 + tw / 2 + 22, 54), radius=10, fill=CREAM + (255,))
    d.text((500 - tw / 2, 8), tag, font=ft, fill=INK + (255,))
    val = fr_typo(c['valeur'])
    size = 300
    while font(BLACK, size).getlength(val) > 900 and size > 120:
        size -= 10
    f = font(BLACK, size)
    d.text((500 - f.getlength(val) / 2 + 8, 88), val, font=f, fill=(0, 0, 0, 170))
    d.text((500 - f.getlength(val) / 2, 80), val, font=f, fill=RED + (255,))
    y = 80 + int(size * 1.05) + 20
    for line in c.get('legende', '').split('\n'):
        if not line:
            continue
        fl = font(XBOLD, 64); L = fr_typo(line)
        d.text((500 - fl.getlength(L) / 2, y), L, font=fl, fill=WHITE + (255,)); y += 76
    sc = 1.14 - 0.14 * ease(t / 0.28)
    return im, sc

CARDS = dict(choc=card_choc, titre=card_titre, seuil=card_seuil, calcul=card_calcul, compteur=card_compteur, cumul=card_cumul,
             checks=card_checks, camp=card_camp, tampon=card_tampon, cta=card_cta)

# ---------------------------------------------------------------- fond et sous-titres
def make_background(ep):
    im = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(im)
    for x in range(0, W, 60):
        d.line((x, 0, x, H), fill=(22, 22, 25), width=1)
    for y in range(0, H, 60):
        d.line((0, y, W, y), fill=(22, 22, 25), width=1)
    im = im.convert('RGBA'); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 9, H), fill=RED + (255,)); d.rectangle((W - 10, 0, W, H), fill=RED + (255,))
    d.text((48, 52), ep.get('rubrique', 'SI ÇA PASSE'), font=font(MONO, 30), fill=RED + (255,))
    f = font(BLACKI, 64); d.text((W - 48 - f.getlength('Arène'), 36), 'Arène', font=f, fill=WHITE + (255,))
    d.text((48, 98), ep['source'], font=font(SEMI, 26), fill=DIM + (255,))
    return im

def draw_subtitle(canvas, words, t, force_page=None, reveal=False):
    """Sous-titres mot à mot, par pages de 3 lignes : mot prononcé en blanc, à venir en gris, mots **clés** en rouge."""
    if not words:
        return
    f = font(BLACK, 72); space = f.getlength(' ')
    lines, cur, cw = [], [], 0
    for (wd, a, b, hl) in words:
        wl = f.getlength(wd)
        if cur and cw + space + wl > X1 - X0 + 20:
            lines.append((cur, cw)); cur, cw = [], 0
        cw += (space if cur else 0) + wl; cur.append((wd, a, b, hl, wl))
    if cur: lines.append((cur, cw))
    npg = math.ceil(len(lines) / 3); per = math.ceil(len(lines) / npg)
    pages = [lines[i:i + per] for i in range(0, len(lines), per)]
    pg = 0
    for i, p in enumerate(pages):
        if p[0][0][0][1] <= t:
            pg = i
    if force_page == 'tout':
        pages = [lines[:4]]; pg = 0
    elif force_page is not None:
        pg = force_page
    d = ImageDraw.Draw(canvas)
    y = 205
    for ws, lw in pages[pg]:
        x = (W - lw) / 2
        for wd, a, b, hl, wl in ws:
            said = t >= a
            if reveal and not said:
                x += wl + space
                continue
            col = (RED if hl else WHITE) if said else DIM
            yy = y - (8 * (1 - ease((t - a) / 0.12)) if a <= t < b else 0)
            d.text((x + 4, yy + 5), wd, font=f, fill=(0, 0, 0, 160))
            d.text((x, yy), wd, font=f, fill=col + (255,))
            x += wl + space
        y += 84

def parse_hl(text):
    out = []; on = False
    for part in text.split('**'):
        for w in part.split(' '):
            if w:
                out.append((w, on))
        on = not on
    return out

# ---------------------------------------------------------------- rendu
def render(ep, outp, voix_dir):
    phrases = ep['phrases']
    audios, sr0 = synthesize(phrases, voix_dir, ep['voix'])
    choc = ep.get('choc')
    rngp = np.random.default_rng(3)
    starts, t = [], (0.32 if choc else 0.12)
    durs = []
    for ph, a in zip(phrases, audios):
        d = len(a) / sr0
        starts.append(t); durs.append(d)
        end = ph['dit'].rstrip()[-1:]
        gap = {'?': 0.40, '!': 0.30, ':': 0.22}.get(end, 0.26) + rngp.uniform(-0.04, 0.04)
        t += d + gap
    total = t + 1.2
    sr = SR_OUT
    N = int(total * sr)
    raw = np.zeros(int(total * sr0) + 1, np.float32)
    for s0, a in zip(starts, audios):
        i = int(s0 * sr0); raw[i:i + len(a)] += a[:len(raw) - i]
    raw /= max(1e-6, np.abs(raw).max()); raw *= 0.9
    voice = traiter_voix(raw, sr0)[:N]
    voice = np.pad(voice, (0, max(0, N - len(voice))))
    voice /= max(1e-6, np.abs(voice).max()); voice *= 0.92
    # enveloppe pour la bouche
    hop = sr // FPS
    env = np.array([np.sqrt(np.mean(voice[i * hop:(i + 1) * hop] ** 2)) if i * hop < N else 0.0 for i in range(int(total * FPS) + 2)])
    env = np.nan_to_num(env)
    env = np.clip(env / (np.percentile(env[env > 0.01], 90) if (env > 0.01).any() else 1), 0, 1.2)
    # musique de fond, baissée sous la voix
    mus = musique.build(total, starts[0], starts[1:])
    mus = np.interp(np.arange(N) / sr, np.arange(len(mus)) / musique.SR, mus[:, 0]).astype(np.float32)
    duck = np.repeat(np.clip(env * 1.4, 0, 1), hop)[:N]; duck = np.pad(duck, (0, max(0, N - len(duck))))
    k = int(0.15 * sr); duck = np.convolve(duck, np.ones(k) / k, mode='same')
    mix = voice + mus * (0.15 - 0.08 * duck)
    if choc:
        w = sifflet(sr); mix[:len(w)] += w
        b = impact(sr); mix[:len(b)] += b
    mix = np.tanh(mix * 1.05); mix *= 0.95 / np.abs(mix).max()
    tmpd = tempfile.mkdtemp(); wav = os.path.join(tmpd, 'a.wav')
    with wave.open(wav, 'wb') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr); wf.writeframes((mix * 32767).astype(np.int16).tobytes())
    audios = [np.zeros(int(d * sr)) for d in durs]  # durées à la nouvelle fréquence, pour les sous-titres

    # timings des mots affichés
    subs = []
    for s, a, ph in zip(starts, audios, phrases):
        toks = parse_hl(fr_typo(ph.get('affiche', ph['dit'])))
        tm = word_timings(' '.join(w for w, _ in toks), len(a) / sr)
        assert len(tm) == len(toks)
        subs.append([(w, s + ta, s + tb, hl) for (w, hl), (_, ta, tb) in zip(toks, tm)])
    # cartes : chaque phrase peut ouvrir une nouvelle carte qui reste jusqu'à la suivante
    card_spans = []
    for i, ph in enumerate(phrases):
        if i == 0 and choc:
            card_spans.append([0.0, None, dict(choc, type='choc')])
        elif 'carte' in ph:
            card_spans.append([starts[i], None, ph['carte']])
    for j in range(len(card_spans)):
        card_spans[j][1] = card_spans[j + 1][0] if j + 1 < len(card_spans) else total
    gestes = [((0.0 if (i == 0 and choc) else starts[i]), ph['geste']) for i, ph in enumerate(phrases) if ph.get('geste')]

    base = make_background(ep)
    arb = Arbitre()
    rng = np.random.default_rng(5)
    grains = [np.kron(rng.normal(0, 3.5, (H // 2, W // 2)), np.ones((2, 2))).astype(np.float32) for _ in range(4)]
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-i', wav, '-c:v', 'libx264', '-preset', 'medium', '-crf', '21', '-maxrate', '7M', '-bufsize', '14M', '-pix_fmt', 'yuv420p',
           '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '48000', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', outp]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    nfr = int(total * FPS)
    for fi in range(nfr):
        tg = fi / FPS
        c = base.copy()
        # sous-titres de la phrase en cours (ou la dernière dite)
        k = max([i for i, s in enumerate(starts) if s <= tg + 0.05] or [0])
        if choc:
            draw_subtitle(c, subs[k], tg, reveal=(k == 0))  # accroche révélée mot à mot, pas de mur de texte
        else:
            draw_subtitle(c, subs[k], tg if fi > 0 else 999, force_page='tout' if fi == 0 else None)  # image 0 : accroche entière (miniature)
        # carte
        for s, e, cd in card_spans:
            if s - 0.05 <= tg < e or (fi == 0 and s == card_spans[0][0]):
                lt = tg - s if (fi > 0 or cd['type'] == 'choc') else 5
                im, sc = CARDS[cd['type']](cd, lt, e - s)
                fade = 1.0 if tg < e - 0.18 else max(0, (e - tg) / 0.18)
                sc = max(0.05, sc)
                if sc != 1.0:
                    im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BILINEAR)
                if fade < 1:
                    im.putalpha(im.getchannel('A').point(lambda v: int(v * fade)))
                cx, cy = W // 2, 860
                if cd['type'] == 'choc' and lt < 0.22:  # petite secousse à l'impact
                    cx += int(10 * math.sin(lt * 90)); cy += int(6 * math.cos(lt * 70))
                c.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))
        # arbitre
        g, gt = None, 0
        for s, gg in gestes:
            if s <= tg < s + 3.0:
                g, gt = gg, tg - s
        m = env[min(fi, len(env) - 1)]
        a_im = arb.render(tg, m, g, gt)
        c.alpha_composite(a_im, (20, 1185))
        # barre de progression
        ImageDraw.Draw(c).rectangle((10, H - 14, 10 + int((W - 20) * tg / total), H - 6), fill=RED + (255,))
        arr = np.asarray(c.convert('RGB')).astype(np.float32) + grains[(fi // 4) % 4][..., None]
        pr.stdin.write(np.clip(arr, 0, 255).astype(np.uint8).tobytes())
    pr.stdin.close(); pr.wait()
    print(f'ok {outp} ({total:.1f} s)')

if __name__ == '__main__':
    ep = json.load(open(sys.argv[1], encoding='utf-8'))
    vd = sys.argv[3] if len(sys.argv) > 3 else os.environ.get('ARENE_VOIX', os.path.join(os.getcwd(), 'voix'))
    render(ep, sys.argv[2], vd)
