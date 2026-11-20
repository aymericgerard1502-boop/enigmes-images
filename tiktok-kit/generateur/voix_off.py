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
TEMPO = {"pocket": 0.90}          # Pocket parle vite (~185 mots/min) : ralenti à ~165 pour une voix posée
VERIFIER = {"pocket", "chatter"}  # moteurs autorégressifs : chaque morceau est réécouté par Whisper

def pour_moteur(s):
    """Texte envoyé au moteur : la ponctuation de suspension est rendue par nos silences."""
    s = s.replace("…", ".").replace("⏸", "").strip()
    return s

_ASR = None
def transcrire(a):
    global _ASR
    if _ASR is None:
        from faster_whisper import WhisperModel
        _ASR = WhisperModel(os.environ.get("ASR_MODELE", "small"), device="cpu", compute_type="int8")
    x = np.linspace(0, len(a) - 1, int(len(a) * 16000 / SR)); a16 = np.interp(x, np.arange(len(a)), a).astype(np.float32)
    segs, _ = _ASR.transcribe(a16, language="fr", beam_size=3)
    return " ".join(s.text for s in segs)

def _norm(t):
    import unicodedata
    t = unicodedata.normalize("NFD", t.lower()); t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", t.replace("huit", "8")).strip()

def ressemblance(attendu, entendu):
    import difflib
    return difflib.SequenceMatcher(None, _norm(attendu), _norm(entendu)).ratio()

def _tempo(a, f):
    if abs(f - 1) < 1e-3: return a
    with tempfile.TemporaryDirectory() as d:
        i, o = os.path.join(d, "i.wav"), os.path.join(d, "o.wav")
        with wave.open(i, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(a, -1, 1) * 32767).astype("<i2").tobytes())
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", i, "-af", f"atempo={f}", o], check=True)
        return lire_wav(o)

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

def rogner(a, avant=0.06, apres=0.08):
    """Retire blancs, souffles et bruits de fin, sans mordre sur les attaques douces (t, p, f, s).
    Début : seuil -34 dB sous le niveau de la parole ; fin : -26 dB (fenêtre 20 ms)."""
    if not len(a): return a
    n = int(0.02 * SR); env = np.sqrt(np.convolve(a ** 2, np.ones(n) / n, mode="same"))
    parole = np.percentile(env, 90)
    deb = np.where(env > max(parole * 0.02, 5e-4))[0]; fin = np.where(env > max(parole * 0.05, 1e-3))[0]
    idx = np.array([deb[0], fin[-1]]) if len(deb) and len(fin) else np.array([], int)
    if not len(idx): return a[:0]
    a = a[max(0, idx[0] - int(avant * SR)): idx[-1] + int(apres * SR)].copy()
    fi, fo = int(0.008 * SR), int(0.03 * SR)
    a[:fi] *= np.linspace(0, 1, fi); a[-fo:] *= np.linspace(1, 0, fo)
    return a

def _lancer(moteur, jobs, d, ref):
    jp = os.path.join(d, "jobs.json"); json.dump(jobs, open(jp, "w"), ensure_ascii=False)
    cmd = [PY[moteur], WORKER, moteur, jp, d] + ([ref] if moteur not in ("kokoro", "pocket") else [])
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: raise RuntimeError(r.stderr[-3000:])

def voix(lignes, moteur="kokoro", ref=None, log=False, essais=3, seuil=0.8):
    """-> {clé: (audio, silence_final)} ; chaque morceau est rogné, vérifié (moteurs autorégressifs), puis espacé."""
    ref = ref or REF_DEFAUT
    plan, jobs = [], []
    for k, txt in lignes:
        ids = []
        for s, p in decouper(txt):
            jid = f"c{len(jobs):03d}"; jobs.append({"id": jid, "text": pour_moteur(s), "seed": 7}); ids.append((jid, p))
        plan.append((k, ids))
    garde = os.environ.get("VOIX_GARDER")
    with tempfile.TemporaryDirectory() as d:
        _lancer(moteur, jobs, d, ref)
        sons = {j["id"]: rogner(lire_wav(os.path.join(d, j["id"] + ".wav"))) for j in jobs}
        score = {}
        if moteur in VERIFIER:
            for essai in range(essais):
                for j in jobs:
                    if j["id"] not in score or score[j["id"]][0] < seuil:
                        sc = ressemblance(j["text"], transcrire(sons[j["id"]]))
                        if j["id"] not in score or sc > score[j["id"]][0]: score[j["id"]] = (sc, sons[j["id"]])
                a_refaire = [dict(j, seed=101 + essai * 37 + n) for n, j in enumerate(jobs) if score[j["id"]][0] < seuil]
                if log: print(f"essai {essai + 1} : {len(a_refaire)} morceau(x) à refaire", [round(score[j['id']][0], 2) for j in jobs])
                if not a_refaire or essai == essais - 1: break
                _lancer(moteur, a_refaire, d, ref)
                for j in a_refaire:
                    sons[j["id"]] = rogner(lire_wav(os.path.join(d, j["id"] + ".wav")))
            sons = {k: v[1] for k, v in score.items()}
        if garde:
            os.makedirs(garde, exist_ok=True)
            for j in jobs:
                with wave.open(os.path.join(garde, j["id"] + ".wav"), "wb") as w:
                    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(sons[j["id"]], -1, 1) * 32767).astype("<i2").tobytes())
        res = {}
        for k, ids in plan:
            parts = []
            for i, (jid, p) in enumerate(ids):
                parts.append(_tempo(sons[jid], TEMPO.get(moteur, 1.0)))
                if i < len(ids) - 1: parts.append(np.zeros(int(p * SR), np.float32))
            a = np.concatenate(parts) if parts else np.zeros(1, np.float32)
            res[k] = (a / (np.abs(a).max() + 1e-6) * 0.9, ids[-1][1] if ids else 0.3)
    return res

if __name__ == "__main__":
    for s, p in decouper(" ".join(sys.argv[1:]) or "Toi, tu trouves le coupable avant Rose ? Alors… ⏸ qui se trouvait au belvédère ?"):
        print(f"{p:.2f}  {s}")
