#!/usr/bin/env python3
"""Voix off rythmée : synthèse phrase par phrase + vrais silences, sans chevauchement.

Règles de silence (ajoutées après chaque morceau, mesurées sur un son débarrassé de ses blancs) :
  .  !  -> 0,40 s     ?  -> 0,45 s     …  -> 0,55 s     :  ;  -> 0,25 s     ,  -> 0,15 s
  ⏸ (marqueur dans le texte) -> 0,75 s, à placer juste avant une révélation.
Une proposition de moins de 3 mots suivie d'une virgule est fusionnée avec la suivante
(« Toi, tu trouves… ») : les moteurs gèrent mieux la micro-pause eux-mêmes que sur un mot isolé.

API : lignes = voix([("hook", "Toi, tu trouves le coupable avant Rose ?"), ...], moteur="kokoro")
      -> {"hook": (audio float32 à SR, silence_final_en_s), ...}
"""
import json, os, re, subprocess, sys, tempfile, wave
import numpy as np

SR = 44100
TTS_ROOT = os.environ.get("TTS_ROOT", "/home/claude/tts")
PY = {e: os.path.join(TTS_ROOT, e, "bin", "python") for e in ("kokoro", "pocket", "chatter", "moss")}
WORKER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "voix_worker.py")
REF_DEFAUT = os.environ.get("VOIX_REF", os.path.join(TTS_ROOT, "refs", "conteuse.wav"))

PAUSES = {".": 0.40, "!": 0.40, "?": 0.45, "…": 0.55, ":": 0.25, ";": 0.25, ",": 0.15}
REVELATION = 0.75

def decouper(texte):
    """-> [(morceau, silence_après)] ; le marqueur ⏸ allonge le silence précédent."""
    out = []
    for part in re.split(r"(⏸)", texte):
        if part == "⏸":
            if out: out[-1] = (out[-1][0], max(out[-1][1], REVELATION))
            continue
        for m in re.finditer(r"[^.!?…:;,]+(?:[.!?…:;,]+|$)", part):
            s = m.group().strip()
            if not s or not re.search(r"\w", s): continue
            p = max((PAUSES.get(c, 0) for c in s[-3:] if c in PAUSES), default=0.3)
            out.append((s, p))
    fus = []
    for s, p in out:   # « Toi, » + « tu trouves… » -> une seule synthèse
        if fus and fus[-1][1] <= 0.15 and len(fus[-1][0].split()) < 3:
            fus[-1] = (fus[-1][0] + " " + s, p)
        else:
            fus.append((s, p))
    return fus

def lire_wav(path):
    with wave.open(path) as w:
        sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float32) / 32768
        if w.getnchannels() > 1: a = a.reshape(-1, w.getnchannels()).mean(1)
    if sr != SR:
        x = np.linspace(0, len(a) - 1, int(len(a) * SR / sr)); a = np.interp(x, np.arange(len(a)), a).astype(np.float32)
    return a

def rogner(a, avant=0.025, apres=0.07):
    """Retire les blancs au début et à la fin (seuil -34 dB sous le pic, fenêtre 10 ms)."""
    if not len(a): return a
    n = int(0.01 * SR); env = np.sqrt(np.convolve(a ** 2, np.ones(n) / n, mode="same"))
    seuil = max(env.max() * 0.02, 1e-3); idx = np.where(env > seuil)[0]
    if not len(idx): return a[:0]
    a = a[max(0, idx[0] - int(avant * SR)): idx[-1] + int(apres * SR)].copy()
    fi, fo = int(0.008 * SR), int(0.03 * SR)
    a[:fi] *= np.linspace(0, 1, fi); a[-fo:] *= np.linspace(1, 0, fo)
    return a

def voix(lignes, moteur="kokoro", ref=None, log=False):
    ref = ref or REF_DEFAUT
    plan, jobs = [], []
    for k, txt in lignes:
        morceaux = decouper(txt)
        ids = []
        for s, p in morceaux:
            jid = f"c{len(jobs):03d}"; jobs.append({"id": jid, "text": s}); ids.append((jid, p))
        plan.append((k, ids))
    with tempfile.TemporaryDirectory() as d:
        jp = os.path.join(d, "jobs.json"); json.dump(jobs, open(jp, "w"), ensure_ascii=False)
        cmd = [PY[moteur], WORKER, moteur, jp, d] + ([ref] if moteur != "kokoro" else [])
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode: raise RuntimeError(r.stderr[-3000:])
        if log: print(r.stdout)
        res = {}
        for k, ids in plan:
            parts = []
            for i, (jid, p) in enumerate(ids):
                parts.append(rogner(lire_wav(os.path.join(d, jid + ".wav"))))
                if i < len(ids) - 1: parts.append(np.zeros(int(p * SR), np.float32))
            a = np.concatenate(parts) if parts else np.zeros(1, np.float32)
            res[k] = (a / (np.abs(a).max() + 1e-6) * 0.9, ids[-1][1] if ids else 0.3)
    return res

if __name__ == "__main__":
    for s, p in decouper(" ".join(sys.argv[1:]) or "Toi, tu trouves le coupable avant Rose ? Alors… ⏸ qui se trouvait au belvédère ?"):
        print(f"{p:.2f}  {s}")
