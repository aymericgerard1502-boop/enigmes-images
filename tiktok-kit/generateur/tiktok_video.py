#!/usr/bin/env python3
"""Format TikTok : accroche en gros titre + voix off + musique, mini-histoire avec Rose et
Sardine, indices un par un en gros (noms en couleur), récap + minuteur, appel à commenter.

Usage : python3 tiktok_video.py <slug-livre> <num-enigme> <sortie.mp4> [--voix=fr_FR-tom-medium]
Voix Piper attendues dans ~/voix (fichiers .onnx + .onnx.json).
"""
import math, os, re, subprocess, sys, wave, tempfile, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import video_enigme as V
import story_video as S
from video_enigme import W, H, FPS, F, GOLD, ORANGE, RED, WHITE, MUTED, LX, RX, ease, paste_alpha

SR = 44100
VOIX_DIR = os.environ.get("VOIX_DIR", "/home/claude/voix")
NAME_COLS = [(255, 112, 112), (90, 214, 200), (186, 146, 255)]
BLACK = (8, 6, 20)

# Accroches écrites à la main (sinon : titre de l'énigme en question)
HOOKS = {
    ("Le-Train-des-Neiges", 1): "Qui a déchiré ce billet ?",
    ("Le-Train-des-Neiges", 2): "Qui a échangé les valises ?",
    ("Le-Train-des-Neiges", 3): "Qui a arraché le houx ?",
    ("Le-Train-des-Neiges", 4): "Qui a volé le sifflet ?",
    ("Les-Santons-de-Minuit", 5): "Qui a arraché l'affiche ?",
    ("Tempete-sur-Belle-Ile", 3): "Qui a touché au portrait ?",
    ("Tempete-sur-Belle-Ile", 4): "Où est passé le télégramme ?",
    ("Les-Santons-de-Minuit", 2): "Qui a effacé ce prix ?",
    ("Les-Santons-de-Minuit", 3): "Qui a dérangé la crèche ?",
    ("Les-Santons-de-Minuit", 4): "Qui a volé les marrons ?",
    ("Vendanges-tardives", 3): "Qui a oublié ces grappes ?",
    ("Le-Train-des-Neiges", 5): "Qui a changé l'étiquette ?",
    ("Les-Santons-de-Minuit", 6): "Qui a coupé la musique ?",
    ("Tempete-sur-Belle-Ile", 5): "Qui a enfermé Sardine ?",
    ("Le-Train-des-Neiges", 6): "Qui a brisé ce verre ?",
    ("Les-Santons-de-Minuit", 7): "Qui a poussé le panier ?",
    ("Vendanges-tardives", 4): "Qui a volé le munster ?",
}

# ------------------------------------------------------------------ voix
def tts(text, voice, scale=0.82):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f: path = f.name
    model = os.path.join(VOIX_DIR, voice + ".onnx")
    subprocess.run([sys.executable, "-m", "piper", "-m", model, "--length-scale", str(scale), "-f", path],
                   input=text.encode(), capture_output=True, check=True)
    w = wave.open(path); sr = w.getframerate()
    a = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float32) / 32768
    os.remove(path)
    if sr != SR:
        x = np.linspace(0, len(a) - 1, int(len(a) * SR / sr)); a = np.interp(x, np.arange(len(a)), a)
    nz = np.where(np.abs(a) > 0.01)[0]
    if len(nz): a = a[max(0, nz[0] - 800): nz[-1] + 2000]
    return a / (np.abs(a).max() + 1e-6) * 0.9

# ------------------------------------------------------------------ musique (synthèse libre de droits)
def ks_pluck(freq, dur, sr=SR, decay=0.996):
    n = int(dur * sr); p = max(2, int(sr / freq))
    buf = np.random.RandomState(int(freq)).uniform(-1, 1, p); out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = decay * 0.5 * (buf[i % p] + buf[(i + 1) % p])
    return out

def note(n): return 440 * 2 ** ((n - 69) / 12)

def music(dur, tension_from=None, tension_to=None):
    bpm = 96; e8 = 60 / bpm / 2; out = np.zeros(int((dur + 2) * SR))
    prog = [(50, [62, 65, 69]), (46, [62, 65, 70]), (43, [62, 67, 70]), (45, [61, 64, 69])]  # Dm Bb Gm A
    bass_pat = [0, 0, 7, 0, 3, 0, 7, 6]
    cache = {}
    t = 0.0; step = 0
    while t < dur:
        bar = int(step // 8) % 4; root, chord = prog[bar]
        tense = tension_from is not None and tension_from <= t < tension_to
        n = root + (0 if tense else bass_pat[step % 8])
        if n not in cache: cache[n] = ks_pluck(note(n), 0.5)
        i = int(t * SR); s = cache[n] * (0.55 if step % 2 == 0 else 0.38)
        out[i:i + len(s)] += s[: len(out) - i]
        # charleston doux sur les contretemps
        if step % 2 == 1:
            hh = np.random.RandomState(step).uniform(-1, 1, int(0.04 * SR)) * np.exp(-np.arange(int(0.04 * SR)) / 300) * 0.08
            out[i:i + len(hh)] += hh
        # cloches (célesta) en début de mesure
        if step % 8 == 0 and not tense:
            for k, cn in enumerate(chord):
                tt = np.arange(int(1.2 * SR)) / SR; j = i + int(k * e8 * SR)
                bell = (np.sin(2 * np.pi * note(cn + 12) * tt) + 0.3 * np.sin(2 * np.pi * note(cn + 24) * tt)) * np.exp(-tt * 3) * 0.09
                out[j:j + len(bell)] += bell[: max(0, len(out) - j)]
        # nappe
        if step % 8 == 0:
            tt = np.arange(int(8 * e8 * SR)) / SR
            env = np.minimum(1, tt / 0.4) * np.minimum(1, (8 * e8 - tt) / 0.4)
            pad = sum(np.sin(2 * np.pi * note(cn - 12) * tt) for cn in chord) * env * 0.035
            out[i:i + len(pad)] += pad[: len(out) - i]
        t += e8; step += 1
    return out[: int(dur * SR)]

# ------------------------------------------------------------------ texte riche
def segments(text, colored):
    """Découpe le texte en (morceau, couleur) selon une liste de (expression, couleur)."""
    segs = [(text, WHITE)]
    for phrase, col in sorted(colored, key=lambda x: -len(x[0])):
        new = []
        for s, c in segs:
            if c != WHITE: new.append((s, c)); continue
            parts = re.split("(" + re.escape(phrase) + ")", s, flags=re.I)
            for k, p in enumerate(parts):
                if p: new.append((p, col if k % 2 == 1 else WHITE))
        segs = new
    words, glue = [], False
    for s, c in segs:
        for wd in re.findall(r"\S+|\s+", s):
            if not wd.strip(): glue = False; continue
            if words and (re.fullmatch(r"[.,;:!?…»)]+", wd) or glue):
                words[-1][0] += wd
            else:
                words.append([wd, c])
            glue = True
        # un nouveau segment collé sans espace (ex. « salon » + « . ») reste attaché
    return words

def rich_lines(d, words, font, width):
    lines, cur, w = [], [], 0
    sp = d.textlength(" ", font=font)
    for wd, c in words:
        ww = d.textlength(wd, font=font)
        if cur and w + sp + ww > width: lines.append(cur); cur, w = [], 0
        cur.append((wd, c)); w += (sp if len(cur) > 1 else 0) + ww
    if cur: lines.append(cur)
    return lines

def draw_rich(d, words, font, y, width=RX - LX, stroke=0, spacing=1.18, cx=(LX + RX) / 2):
    lines = rich_lines(d, words, font, width); sp = d.textlength(" ", font=font)
    for ln in lines:
        lw = sum(d.textlength(wd, font=font) for wd, _ in ln) + sp * (len(ln) - 1)
        x = cx - lw / 2
        for wd, c in ln:
            d.text((x, y), wd, font=font, fill=c, stroke_width=stroke, stroke_fill=BLACK)
            x += d.textlength(wd, font=font) + sp
        y += int(font.size * spacing)
    return y

# ------------------------------------------------------------------ plan lisible
def plan_order(plan, places):
    """Lit l'ordre gauche→droite des 3 lieux sur le plan (OCR), sinon None."""
    import difflib
    w, h = plan.size; got = []
    for k in range(3):
        part = plan.crop((int(k * w / 3) + 12, 12, int((k + 1) * w / 3) - 12, h - 12))
        part = part.resize((part.width * 5 // 2, part.height * 5 // 2)).convert("L")
        best, score = None, 0
        for psm in ("6", "7", "11"):
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f: path = f.name
            part.save(path)
            txt = subprocess.run(["tesseract", path, "-", "--psm", psm], capture_output=True, text=True).stdout
            os.remove(path)
            for pl in places:
                r = difflib.SequenceMatcher(None, pl.lower(), txt.lower().strip()).ratio()
                if r > score: best, score = pl, r
            if score > 0.7: break
        got.append(best if score > 0.5 else None)
    missing = [pl for pl in places if pl not in got]
    if got.count(None) == 1 and len(missing) == 1: got[got.index(None)] = missing[0]
    return got if None not in got and len(set(got)) == 3 else None

def tiles_layer(order, y, h=170, fs=46):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    tw, gap = 250, 40; x0 = (W - 3 * tw - 2 * gap) / 2 - 40
    for k, name in enumerate(order):
        x = x0 + k * (tw + gap)
        d.rounded_rectangle((x, y, x + tw, y + h), 26, fill=(52, 46, 104), outline=GOLD, width=5)
        size = fs
        while True:
            f = F("Carlito-Bold.ttf", size); lines = [x for x in V.wrap(d, name, f, tw - 30) if x]
            if max(d.textlength(ln, font=f) for ln in lines) <= tw - 26 or size <= 26: break
            size -= 2
        lh = size * 1.15; cy0 = y + h / 2 - (len(lines) - 1) * lh / 2
        for j, ln in enumerate(lines):
            d.text((x + tw / 2, cy0 + j * lh), ln, font=f, fill=WHITE, anchor="mm")
        if k < 2:
            cx = x + tw + gap / 2; cy = y + h / 2
            d.line((cx - 18, cy, cx + 18, cy), fill=GOLD, width=6)
            d.polygon([(cx + 22, cy), (cx + 8, cy - 11), (cx + 8, cy + 11)], fill=GOLD)
            d.polygon([(cx - 22, cy), (cx - 8, cy - 11), (cx - 8, cy + 11)], fill=GOLD)
    return lay, y + h

# ------------------------------------------------------------------ calques
def L(): return Image.new("RGBA", (W, H), (0, 0, 0, 0))

def chips_layer(names, cols, y=250):
    lay = L(); d = ImageDraw.Draw(lay); f = F("Carlito-Bold.ttf", 44)
    ws = [d.textlength(n, font=f) + 60 for n in names]; gap = 22
    x = (W - sum(ws) - gap * (len(ws) - 1)) / 2 - 40
    for n, c, w in zip(names, cols, ws):
        d.rounded_rectangle((x, y, x + w, y + 72), 36, fill=c)
        d.text((x + 30, y + 12), n, font=f, fill=BLACK); x += w + gap
    return lay

def plan_card(plan, y, width=820):
    lay = L(); ph = int(plan.height * (width - 40) / plan.width)
    card = Image.new("RGBA", (width, ph + 40), (252, 249, 245, 255))
    card.paste(plan.resize((width - 40, ph), Image.LANCZOS), (20, 20))
    m = Image.new("L", card.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, *card.size), 24, fill=255); card.putalpha(m)
    lay.alpha_composite(card, ((W - width) // 2 - 40, y))
    return lay, y + card.height

def hook_words_of(title):
    out = []
    for w in title.upper().split():
        if out and w in ("?", "!", ":", ";"): out[-1] += "\u00a0" + w
        else: out.append(w)
    return out

def hook_layer(title, n_words_shown, last_pop):
    lay = L(); d = ImageDraw.Draw(lay)
    f = F("Carlito-Bold.ttf", 40); t = "ÉNIGME DU JOUR"
    bw = d.textlength(t, font=f) + 60; bx = (W - bw) / 2 - 40
    d.rounded_rectangle((bx, 330, bx + bw, 400), 35, fill=RED); d.text((bx + 30, 343), t, font=f, fill=WHITE)
    words = hook_words_of(title)
    shown = [[w, GOLD] for w in words[:n_words_shown]]
    big = F("Caladea-Bold.ttf", 132)
    y = draw_rich(d, shown, big, 480 - int(10 * (1 - last_pop)), width=860, stroke=8, spacing=1.08)
    if n_words_shown >= len(words):
        draw_rich(d, [["Trouve", WHITE], ["le", WHITE], ["coupable", WHITE], ["avant", WHITE], ["Rose", RED]],
                  F("Carlito-Bold.ttf", 64), y + 30, stroke=7)
    return lay

def caption_layer(words, active):
    lay = L(); d = ImageDraw.Draw(lay); f = F("Carlito-Bold.ttf", 82)
    ws = [[w, GOLD if i == active else WHITE] for i, w in enumerate(words)]
    draw_rich(d, ws, f, 520, width=820, stroke=9)
    return lay

def clue_layer(i, n, words):
    lay = L(); d = ImageDraw.Draw(lay)
    f = F("Carlito-Bold.ttf", 42); t = f"INDICE {i + 1}/{n}"
    bw = d.textlength(t, font=f) + 56; bx = (W - bw) / 2 - 40
    d.rounded_rectangle((bx, 720, bx + bw, 788), 34, fill=GOLD); d.text((bx + 28, 731), t, font=f, fill=BLACK)
    draw_rich(d, words, F("Carlito-Bold.ttf", 76), 830, width=840, stroke=0, spacing=1.2)
    return lay

def recap_layer(clue_words, y0):
    lay = L(); d = ImageDraw.Draw(lay); f = F("Carlito-Bold.ttf", 46); nf = F("Carlito-Bold.ttf", 46)
    y = y0
    for i, ws in enumerate(clue_words):
        d.text((LX, y), f"{i + 1}.", font=nf, fill=GOLD)
        lines = rich_lines(d, ws, f, RX - LX - 70); sp = d.textlength(" ", font=f)
        for ln in lines:
            x = LX + 60
            for wd, c in ln:
                d.text((x, y), wd, font=f, fill=c); x += d.textlength(wd, font=f) + sp
            y += int(f.size * 1.15)
        y += 14
    return lay, y

def suspects_layer(names, cols, shown, pops):
    lay = L(); d = ImageDraw.Draw(lay)
    r = 105; gap = 300; cx0 = W / 2 - 40 - gap
    for k in range(shown):
        cx = cx0 + k * gap; cy = 1020; p = pops[k]; rr = int(r * (0.6 + 0.4 * p))
        d.ellipse((cx - rr - 8, cy - rr - 8, cx + rr + 8, cy + rr + 8), fill=WHITE)
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=cols[k])
        bf = F("Caladea-Bold.ttf", int(120 * (0.6 + 0.4 * p)))
        d.text((cx - d.textlength(names[k][0], font=bf) / 2, cy - bf.size * 0.62), names[k][0], font=bf, fill=BLACK)
        nf = F("Carlito-Bold.ttf", 54)
        d.text((cx - d.textlength(names[k], font=nf) / 2, cy + r + 30), names[k], font=nf, fill=WHITE, stroke_width=6, stroke_fill=BLACK)
    big = F("Caladea-Bold.ttf", 96)
    draw_rich(d, [["3", GOLD], ["suspects", WHITE]], big, 700, stroke=8)
    return lay

# ------------------------------------------------------------------ montage
def build(slug, num, out, voice="fr_FR-tom-medium", secs=8):
    livre, e = V.load(slug, num)
    plan = V.crop_plan(os.path.join(V.KIT, e["image"]))
    cover = Image.open(os.path.join(V.KIT, livre["couverture"])).convert("RGB")
    n_en = 24 if "Neiges" in livre["livre"] else 40
    names = sorted(e["solution"].keys()); cols = NAME_COLS[:len(names)]
    colored = [(nm, c) for nm, c in zip(names, cols)]
    for v in e["solution"].values():
        colored.append((v["lieu"][0], GOLD))
    hook = HOOKS.get((slug, num), e["titre"] + " : qui est le coupable ?")
    q = f"Qui se trouvait {e['question_lieu'][1]} ?"
    liste = f"{names[0]}, {names[1]} ou {names[2]}"

    # --- textes parlés
    lines = [("hook", hook + " Trouve le coupable avant Rose."),
             ("setup", e["incident"]),
             ("suspects", f"Trois suspects : {', '.join(names[:-1])} et {names[-1]}. Écoute bien les indices.")]
    for i, c in enumerate(e["indices"]): lines.append((f"clue{i}", c))
    lines.append(("question", "Alors… " + q + " Tu as huit secondes."))
    lines.append(("cta", f"{liste} ? Dis-le en commentaire !"))
    audio = {k: tts(txt, voice) for k, txt in lines}

    # --- chronologie
    T, t = {}, 0.0
    for k, _ in lines:
        if k == "cta": T["timer"] = (t, t + secs); t += secs
        d = len(audio[k]) / SR + (0.35 if k.startswith("clue") else 0.25)
        if k == "hook": d = max(d, 2.6)
        T[k] = (t, t + d); t += d
    dur = t + 1.8

    # --- son : voix + musique avec effacement sous la voix + tic-tac du minuteur
    mix = np.zeros(int((dur + 1) * SR)); voice_env = np.zeros_like(mix)
    for k, _ in lines:
        i = int((T[k][0] + 0.08) * SR); a = audio[k]
        mix[i:i + len(a)] += a; voice_env[i:i + len(a)] = 1
    k = int(0.25 * SR); voice_env = np.convolve(voice_env, np.ones(k) / k, mode="same")
    mus = music(dur + 1, *T["timer"]); mus = mus / (np.abs(mus).max() + 1e-6)
    mix[: len(mus)] += mus * (0.30 - 0.20 * voice_env[: len(mus)])
    tk = np.sin(2 * np.pi * 1800 * np.arange(int(0.05 * SR)) / SR) * np.exp(-np.arange(int(0.05 * SR)) / 250) * 0.35
    for s in range(secs * 2):
        i = int((T["timer"][0] + s * 0.5) * SR); mix[i:i + len(tk)] += tk * (1 if s % 2 == 0 else 0.6)
    mix = mix[: int(dur * SR)]; mix = mix / (np.abs(mix).max() + 1e-6) * 0.95
    wav = out + ".wav"
    with wave.open(wav, "wb") as w:
        st = (np.stack([mix, mix], 1) * 32767).astype("<i2"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes())

    # --- visuels pré-calculés
    sc = S.make_scene(slug)
    still = sc["static"].copy(); dd = ImageDraw.Draw(still, "RGBA")
    sc["back"](still, dd, 4.0)
    S.rose(dd, 250, S.GROUND_Y, 0); S.sardine(dd, 560, S.GROUND_Y, 0)
    dim_bg = still.filter(ImageFilter.GaussianBlur(14)); dim_bg.alpha_composite(Image.new("RGBA", (W, H), (10, 8, 26, 205)))
    chips = chips_layer(names, cols)
    order = plan_order(plan, [v["lieu"][0] for v in e["solution"].values()])
    if order:
        pl_small, pl_end = tiles_layer(order, 370)
    else:
        pl_small, pl_end = plan_card(plan, 360)
    clue_words = [segments(c, colored) for c in e["indices"]]
    clue_lays = [clue_layer(i, len(clue_words), ws) for i, ws in enumerate(clue_words)]
    if order:
        pl_recap, pr_end = tiles_layer(order, 350, h=120, fs=38)
    else:
        pl_recap, pr_end = plan_card(plan, 350, 700)
    recap, ry = recap_layer(clue_words, pr_end + 30)
    cta = V.cta_layer(livre, cover, n_en, names)
    cap_words = {}
    setup_words = e["incident"].split()
    chunks = []; cur = []
    for wd in setup_words:
        cur.append(wd)
        if len(" ".join(cur)) > 18 or wd.endswith((".", ",")): chunks.append(cur); cur = []
    if cur: chunks.append(cur)
    tot = sum(len(" ".join(c)) for c in chunks)
    tl = []; acc = 0
    for c in chunks:
        for j, wd in enumerate(c):
            tl.append((acc / tot, c, j)); acc += len(wd) + 1
    hook_words = hook_words_of(hook)

    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    qcache = {}
    t_story_end = T["setup"][1]
    for fi in range(int(dur * FPS)):
        t = fi / FPS
        if t < t_story_end + 0.3:
            fr = sc["static"].copy(); d = ImageDraw.Draw(fr, "RGBA")
            sc["back"](fr, d, t)
            S.rose(d, 250, S.GROUND_Y, t); S.sardine(d, 560, S.GROUND_Y, t)
            if "billet" in e["incident"].lower() and t > T["setup"][0]: S.ticket(d, 760, S.GROUND_Y - 14, t)
            sc["front"](fr, d, t)
            if t < T["hook"][1]:
                fr.alpha_composite(Image.new("RGBA", (W, H), (10, 8, 26, 150)))
                el = t - T["hook"][0]; per = 0.28
                n = min(len(hook_words), 1 + int(el / per)); pop = ease(min(1, (el - (n - 1) * per) / 0.18))
                fr.alpha_composite(hook_layer(hook, n, pop))
            else:
                el = (t - T["setup"][0]) / max(0.1, (T["setup"][1] - T["setup"][0] - 0.3))
                cur = [x for x in tl if x[0] <= el]
                if cur:
                    _, c, j = cur[-1]; key = (" ".join(c), j)
                    if key not in cap_words: cap_words[key] = caption_layer(c, j)
                    fr.alpha_composite(cap_words[key])
            if t > t_story_end - 0.1:
                paste_alpha(fr, dim_bg, ease((t - t_story_end + 0.1) / 0.4))
        else:
            fr = dim_bg.copy()
            if T["suspects"][0] <= t < T["suspects"][1]:
                el = t - T["suspects"][0]; ns = min(3, 1 + int(max(0, el - 0.9) / 0.55))
                pops = [ease(min(1, (el - 0.9 - k * 0.55) / 0.2)) if el > 0.9 + k * 0.55 else 1 for k in range(3)]
                fr.alpha_composite(suspects_layer(names, cols, ns if el > 0.9 else 0, pops))
            for i in range(len(clue_lays)):
                a, b = T[f"clue{i}"]
                if a <= t < b:
                    fr.alpha_composite(chips); fr.alpha_composite(pl_small)
                    el = t - a; paste_alpha(fr, clue_lays[i], ease(el / 0.25), (1 - ease(el / 0.25)) * 40)
            if t >= T["question"][0] and t < T["cta"][0]:
                fr.alpha_composite(chips); fr.alpha_composite(pl_recap); fr.alpha_composite(recap)
                if t >= T["timer"][0]:
                    el = t - T["timer"][0]; rem = max(1, secs - int(el)); frac = min(1, el / secs)
                else:
                    rem, frac = secs, 0
                key = (rem, round(frac * 60))
                if key not in qcache: qcache[key] = V.question_layer(e, ry + 10, rem, key[1] / 60)
                fr.alpha_composite(qcache[key])
            if t >= T["cta"][0]:
                el = t - T["cta"][0]; paste_alpha(fr, cta, ease(el / 0.5), (1 - ease(el / 0.5)) * 40)
        p.stdin.write(fr.convert("RGB").tobytes())
    p.stdin.close(); p.wait(); os.remove(wav)
    return dict(duree=round(dur, 1), coupable=e["coupable"], titre=e["titre"],
                timeline={k: (round(a, 1), round(b, 1)) for k, (a, b) in T.items()})


# ================================================================== VAGUE 3 : format court + qualité
from scipy.signal import fftconvolve

def voice_fx(a):
    """Voix plus chaude et présente : coupe-bas, présence, compression douce, légère pièce."""
    with tempfile.TemporaryDirectory() as td:
        src, dst = os.path.join(td, "a.wav"), os.path.join(td, "b.wav")
        with wave.open(src, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(a, -1, 1) * 32767).astype("<i2").tobytes())
        flt = ("highpass=f=85,equalizer=f=180:t=q:w=1.2:g=2.5,equalizer=f=3200:t=q:w=1.4:g=3.5,"
               "equalizer=f=7500:t=q:w=2:g=-2,acompressor=threshold=-20dB:ratio=3.5:attack=4:release=80:makeup=2,"
               "aecho=0.85:0.5:28|52:0.10|0.06")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-af", flt, "-ar", str(SR), "-ac", "1", dst], check=True)
        w = wave.open(dst); b = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float32) / 32768
    return b / (np.abs(b).max() + 1e-6) * 0.92

def reverb(x, secs=1.6, mix=0.28, seed=1):
    n = int(secs * SR); rng = np.random.RandomState(seed)
    ir = rng.uniform(-1, 1, n) * np.exp(-np.arange(n) / (n / 5.5)); ir[0] = 1
    wet = fftconvolve(x, ir)[: len(x)]; wet /= (np.abs(wet).max() + 1e-6)
    return (1 - mix) * x / (np.abs(x).max() + 1e-6) + mix * wet

def music2(dur, timer, sfx_times):
    """Musique d'enquête stéréo : contrebasse pizz., batterie feutrée, célesta en arpèges, nappe,
    réverbération ; tension pendant le minuteur ; effets (whoosh, ding, montée, révélation)."""
    bpm = 100; e8 = 60 / bpm / 2; n = int((dur + 2) * SR)
    L_, R_ = np.zeros(n), np.zeros(n)
    prog = [(50, [62, 65, 69]), (46, [62, 65, 70]), (43, [62, 67, 70]), (45, [61, 64, 69])]
    bass_pat = [0, 0, 7, 0, 3, 0, 7, 6]
    cache = {}
    def add(buf, i, sig):
        if i >= len(buf): return
        j = min(len(buf), i + len(sig)); buf[i:j] += sig[: j - i]
    tt = np.arange(int(0.35 * SR)) / SR
    kick = np.sin(2 * np.pi * (45 + 75 * np.exp(-tt * 28)) * tt) * np.exp(-tt * 9) * 0.55
    rs = np.random.RandomState(3)
    snap = rs.uniform(-1, 1, int(0.12 * SR)) * np.exp(-np.arange(int(0.12 * SR)) / 900) * 0.12
    t = 0.0; step = 0; ts0, ts1 = timer
    while t < dur:
        bar = (step // 8) % 4; root, chord = prog[bar]; i = int(t * SR)
        tense = ts0 <= t < ts1
        nb = root + (0 if tense else bass_pat[step % 8])
        if nb not in cache: cache[nb] = ks_pluck(note(nb), 0.55)
        b = cache[nb] * (0.6 if step % 2 == 0 else 0.42); add(L_, i, b); add(R_, i, b)
        if step % 4 == 0: add(L_, i, kick); add(R_, i, kick)
        if step % 4 == 2: add(L_, i, snap * 0.9); add(R_, i, snap)
        if step % 2 == 1:
            hh = np.random.RandomState(step).uniform(-1, 1, int(0.03 * SR)) * np.exp(-np.arange(int(0.03 * SR)) / 200) * 0.05
            add(L_ if step % 4 == 1 else R_, i, hh)
        if not tense:   # célesta en arpèges (une note sur deux croches), panoramique alterné
            if step % 2 == 0:
                cn = chord[(step // 2) % 3] + 12 + (12 if (step // 6) % 2 else 0)
                tb = np.arange(int(0.9 * SR)) / SR
                bell = (np.sin(2 * np.pi * note(cn) * tb) + 0.25 * np.sin(2 * np.pi * note(cn) * 2.01 * tb)) * np.exp(-tb * 4.5) * 0.06
                add(L_, i, bell * (0.8 if step % 4 == 0 else 0.35)); add(R_, i, bell * (0.35 if step % 4 == 0 else 0.8))
        if step % 8 == 0:
            tp = np.arange(int(8 * e8 * SR)) / SR
            env = np.minimum(1, tp / 0.8) * np.minimum(1, (8 * e8 - tp) / 0.5)
            pad = sum(np.sin(2 * np.pi * note(cn - 12) * tp + k) for k, cn in enumerate(chord)) * env * (0.05 if tense else 0.032)
            add(L_, i, pad); add(R_, i, np.roll(pad, 400))
        t += e8; step += 1
    # effets sonores
    def whoosh(d=0.5):
        m = int(d * SR); x = np.random.RandomState(7).uniform(-1, 1, m)
        env = np.sin(np.linspace(0, np.pi, m)) ** 2
        k = np.linspace(2, 40, m).astype(int); y = np.array([x[max(0, j - kk):j + 1].mean() for j, kk in enumerate(k)])
        return y * env * 0.5
    W_ = whoosh()
    tb = np.arange(int(1.1 * SR)) / SR
    ding = (np.sin(2 * np.pi * 1318.5 * tb) + 0.5 * np.sin(2 * np.pi * 1975.5 * tb)) * np.exp(-tb * 5) * 0.12
    for kind, at in sfx_times:
        i = int(at * SR)
        if kind == "whoosh": add(L_, i, W_); add(R_, i, W_[::-1] * 0.8)
        if kind == "ding": add(L_, i, ding); add(R_, i, ding)
        if kind == "riser":
            m = int(1.6 * SR); tr = np.arange(m) / SR
            rz = (np.random.RandomState(9).uniform(-1, 1, m) * 0.15 + np.sin(2 * np.pi * (200 + 500 * tr / 1.6) * tr) * 0.08) * (tr / 1.6) ** 2
            add(L_, i - m, rz); add(R_, i - m, rz)
        if kind == "beat":   # battement de cœur pendant le minuteur
            hb = np.sin(2 * np.pi * 55 * tt) * np.exp(-tt * 14) * 0.6
            add(L_, i, hb); add(R_, i, hb); add(L_, i + int(0.22 * SR), hb * 0.6); add(R_, i + int(0.22 * SR), hb * 0.6)
        if kind == "reveal":
            tr = np.arange(int(2.2 * SR)) / SR
            ch = sum(np.sin(2 * np.pi * note(m_) * tr) for m_ in (62, 66, 69, 74)) * np.exp(-tr * 1.6) * 0.07
            add(L_, i, ch); add(R_, i, ch)
    L_, R_ = reverb(L_[: int(dur * SR)], seed=1), reverb(R_[: int(dur * SR)], seed=2)
    m = max(np.abs(L_).max(), np.abs(R_).max()) + 1e-6
    return np.stack([L_ / m, R_ / m], 1)

def vignette_layer():
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.6)) ** 2)
    a = (np.clip((r - 0.55) / 0.6, 0, 1) ** 1.6 * 170).astype("uint8")
    lay = Image.new("RGBA", (W, H), (4, 3, 12, 0)); lay.putalpha(Image.fromarray(a)); return lay

def grain_layers(n=6):
    out = []
    for k in range(n):
        g = np.random.RandomState(k).randint(0, 255, (H // 2, W // 2)).astype("uint8")
        im = Image.fromarray(g).resize((W, H)).convert("RGBA"); im.putalpha(7); out.append(im)
    return out

def zoom(fr, z, cx=0.5, cy=0.55):
    if z <= 1.001: return fr
    w2, h2 = int(W / z), int(H / z); x0 = int((W - w2) * cx); y0 = int((H - h2) * cy)
    return fr.crop((x0, y0, x0 + w2, y0 + h2)).resize((W, H), Image.BILINEAR)

def popped(layer, k):
    """Calque qui « rebondit » à l'apparition (k de 0 à 1)."""
    if k >= 1: return layer
    s = 0.9 + 0.1 * ease(k) + 0.03 * math.sin(k * math.pi)
    w2, h2 = int(W * s), int(H * s); sm = layer.resize((w2, h2), Image.BILINEAR)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0)); out.alpha_composite(sm, ((W - w2) // 2, (H - h2) // 2))
    if k < 1:
        a = out.getchannel("A").point(lambda v: int(v * min(1, ease(k * 1.6)))); out.putalpha(a)
    return out

def first_sentence(txt):
    m = re.match(r"(.+?[.!?…])(\s|$)", txt)
    return m.group(1) if m else txt

def build_court(slug, num, out, voice="fr_FR-tom-medium", secs=5):
    livre, e = V.load(slug, num)
    plan = V.crop_plan(os.path.join(V.KIT, e["image"]))
    cover = Image.open(os.path.join(V.KIT, livre["couverture"])).convert("RGB")
    n_en = 24 if "Neiges" in livre["livre"] else 40
    names = sorted(e["solution"].keys()); cols = NAME_COLS[:len(names)]
    colored = [(nm, c) for nm, c in zip(names, cols)] + [(v["lieu"][0], GOLD) for v in e["solution"].values()]
    hook = HOOKS.get((slug, num), e["titre"] + " : qui est le coupable ?")
    q = f"Qui se trouvait {e['question_lieu'][1]} ?"
    liste = f"{names[0]}, {names[1]} ou {names[2]}"
    story = first_sentence(e["incident"])

    lines = [("hook", hook), ("setup", story)]
    for i, c in enumerate(e["indices"]): lines.append((f"clue{i}", c))
    lines.append(("question", q + " Cinq secondes !"))
    lines.append(("cta", f"{liste} ? Réponds en commentaire !"))
    scale = 0.78
    raw = {k: tts(txt, voice, scale) for k, txt in lines}
    est = sum(len(a) for a in raw.values()) / SR + secs + 4
    if est > 31:   # trop long : on accélère un peu la lecture des indices
        for k, txt in lines:
            if k.startswith("clue"): raw[k] = tts(txt, voice, 0.72)
    audio = {k: voice_fx(a) for k, a in raw.items()}

    T, t = {}, 0.0
    for k, _ in lines:
        if k == "cta": T["timer"] = (t, t + secs); t += secs
        d = len(audio[k]) / SR + (0.22 if k.startswith("clue") else 0.15)
        if k == "hook": d = max(d, 2.0)
        T[k] = (t, t + d); t += d
    dur = t + 1.2

    sfx = [("whoosh", T["setup"][0] - 0.15), ("whoosh", T["clue0"][0] - 0.2), ("riser", T["timer"][0]),
           ("reveal", T["cta"][0]), ("whoosh", T["cta"][0] - 0.2)]
    for i in range(len(e["indices"])): sfx.append(("ding", T[f"clue{i}"][0]))
    for s_ in range(secs): sfx.append(("beat", T["timer"][0] + s_))
    mus = music2(dur, T["timer"], sfx)
    mix = np.zeros((int(dur * SR) + SR, 2)); venv = np.zeros(len(mix))
    for k, _ in lines:
        i = int((T[k][0] + 0.05) * SR); a = audio[k]
        mix[i:i + len(a), 0] += a; mix[i:i + len(a), 1] += a; venv[i:i + len(a)] = 1
    kk = int(0.3 * SR); venv = np.convolve(venv, np.ones(kk) / kk, mode="same")
    mix[: len(mus)] += mus * (0.34 - 0.22 * venv[: len(mus), None])
    tk = np.sin(2 * np.pi * 1800 * np.arange(int(0.04 * SR)) / SR) * np.exp(-np.arange(int(0.04 * SR)) / 220) * 0.25
    for s_ in range(secs * 2):
        i = int((T["timer"][0] + s_ * 0.5) * SR); mix[i:i + len(tk)] += tk[:, None]
    mix = mix[: int(dur * SR)]; mix = mix / (np.abs(mix).max() + 1e-6) * 0.95
    wav = out + ".wav"
    with wave.open(wav, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype("<i2").tobytes())

    sc = S.make_scene(slug)
    still = sc["static"].copy(); dd = ImageDraw.Draw(still, "RGBA")
    sc["back"](still, dd, 4.0); S.rose(dd, 250, S.GROUND_Y, 0); S.sardine(dd, 560, S.GROUND_Y, 0)
    dim_bg = still.filter(ImageFilter.GaussianBlur(10)); dim_bg.alpha_composite(Image.new("RGBA", (W, H), (10, 8, 26, 190)))
    vig = vignette_layer(); grains = grain_layers()
    chips = chips_layer(names, cols)
    order = plan_order(plan, [v["lieu"][0] for v in e["solution"].values()])
    pl_small = tiles_layer(order, 370)[0] if order else plan_card(plan, 360)[0]
    pl_recap, pr_end = tiles_layer(order, 350, h=120, fs=38) if order else plan_card(plan, 350, 700)
    clue_words = [segments(c, colored) for c in e["indices"]]
    clue_lays = [clue_layer(i, len(clue_words), ws) for i, ws in enumerate(clue_words)]
    recap, ry = recap_layer(clue_words, pr_end + 30)
    cta = V.cta_layer(livre, cover, n_en, names)
    hook_words = hook_words_of(hook)
    words = story.split(); chunks, cur = [], []
    for wd in words:
        cur.append(wd)
        if len(" ".join(cur)) > 18 or wd.endswith((".", ",")): chunks.append(cur); cur = []
    if cur: chunks.append(cur)
    tot = sum(len(" ".join(c)) for c in chunks); tl, acc = [], 0
    for c in chunks:
        for j, wd in enumerate(c): tl.append((acc / tot, c, j)); acc += len(wd) + 1
    cap_cache, qcache = {}, {}

    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-maxrate", "4M", "-bufsize", "8M", "-pix_fmt", "yuv420p",
           "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "44100",
           "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t_story_end = T["setup"][1]
    for fi in range(int(dur * FPS)):
        t = fi / FPS
        if t < t_story_end + 0.25:
            fr = sc["static"].copy(); d = ImageDraw.Draw(fr, "RGBA")
            sc["back"](fr, d, t); S.rose(d, 250, S.GROUND_Y, t); S.sardine(d, 560, S.GROUND_Y, t)
            if "billet" in e["incident"].lower() and t > T["setup"][0]: S.ticket(d, 760, S.GROUND_Y - 14, t)
            sc["front"](fr, d, t)
            fr = zoom(fr, 1.0 + 0.07 * min(1, t / max(1, t_story_end)))
            if t < T["hook"][1]:
                fr.alpha_composite(Image.new("RGBA", (W, H), (10, 8, 26, 140)))
                el = t; per = 0.22
                n = min(len(hook_words), 1 + int(el / per)); pop = ease(min(1, (el - (n - 1) * per) / 0.15))
                fr.alpha_composite(hook_layer(hook, n, pop))
            else:
                el0 = t - T["setup"][0]
                fr.alpha_composite(popped(chips, min(1, el0 / 0.3)))
                el = el0 / max(0.1, (T["setup"][1] - T["setup"][0] - 0.2))
                cc = [x for x in tl if x[0] <= el]
                if cc:
                    _, c, j = cc[-1]; key = (" ".join(c), j)
                    if key not in cap_cache: cap_cache[key] = caption_layer(c, j)
                    fr.alpha_composite(cap_cache[key])
            if t > t_story_end - 0.1:
                paste_alpha(fr, dim_bg, ease((t - t_story_end + 0.1) / 0.35))
        else:
            fr = dim_bg.copy()
            fx = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sc["front"](fx, ImageDraw.Draw(fx, "RGBA"), t); paste_alpha(fr, fx, 0.45)
            for i in range(len(clue_lays)):
                a, b = T[f"clue{i}"]
                if a <= t < b:
                    fr.alpha_composite(chips); fr.alpha_composite(pl_small)
                    fr.alpha_composite(popped(clue_lays[i], min(1, (t - a) / 0.22)))
            if T["question"][0] <= t < T["cta"][0]:
                fr.alpha_composite(chips); fr.alpha_composite(pl_recap); fr.alpha_composite(recap)
                if t >= T["timer"][0]:
                    el = t - T["timer"][0]; rem = max(1, secs - int(el)); frac = min(1, el / secs)
                else:
                    rem, frac = secs, 0
                key = (rem, round(frac * 60))
                if key not in qcache: qcache[key] = V.question_layer(e, ry + 10, rem, key[1] / 60)
                ql = qcache[key]
                if t >= T["timer"][0] and (t - T["timer"][0]) % 1 < 0.12:   # pulsation à chaque seconde
                    ql = popped(ql, 0.55 + (t - T["timer"][0]) % 1 * 3.5)
                fr.alpha_composite(ql)
            if t >= T["cta"][0]:
                fr.alpha_composite(popped(cta, min(1, (t - T["cta"][0]) / 0.4)))
        fr.alpha_composite(vig); fr.alpha_composite(grains[fi % len(grains)])
        p.stdin.write(fr.convert("RGB").tobytes())
    p.stdin.close(); p.wait(); os.remove(wav)
    return dict(duree=round(dur, 1), coupable=e["coupable"], titre=e["titre"],
                timeline={k: (round(a, 1), round(b, 1)) for k, (a, b) in T.items()})

if __name__ == "__main__":
    v = next((a.split("=")[1] for a in sys.argv if a.startswith("--voix=")), "fr_FR-tom-medium")
    f = build if "--long" in sys.argv else build_court   # vague 3 : format court par défaut
    print(f(sys.argv[1], int(sys.argv[2]), sys.argv[3], voice=v))
