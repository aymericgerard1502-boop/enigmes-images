#!/usr/bin/env python3
"""Synthèse brute, une phrase (ou une proposition) par appel, dans l'environnement du moteur.

Usage : <python du moteur> voix_worker.py <moteur> <jobs.json> <dossier_sortie> [voix_ref.wav]
jobs.json = [{"id": "c000", "text": "..."}, ...] -> <dossier_sortie>/c000.wav (mono, float32)

Moteurs (gratuits, poids sous licence commerciale) :
  kokoro   Kokoro-82M, voix ff_siwis (Apache 2.0 ; données SIWIS CC BY 4.0)
  pocket   Kyutai Pocket TTS, français (CC BY 4.0), clonage sur voix_ref
  chatter  Resemble AI Chatterbox Multilingual (MIT), clonage sur voix_ref
  moss     OpenMOSS MOSS-TTS-Nano 100M, ONNX CPU (Apache 2.0), clonage sur voix_ref
"""
import json, os, sys, wave
import numpy as np

def save(path, a, sr):
    a = np.asarray(a, dtype=np.float32).reshape(-1)
    a = np.clip(a, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(int(sr))
        w.writeframes((a * 32767).astype("<i2").tobytes())

def main():
    eng, jobs, out = sys.argv[1], json.load(open(sys.argv[2])), sys.argv[3]
    ref = sys.argv[4] if len(sys.argv) > 4 else None
    os.makedirs(out, exist_ok=True)
    if eng == "kokoro":
        from kokoro import KPipeline
        pipe = KPipeline(lang_code="f", repo_id="hexgrad/Kokoro-82M")
        speed = float(os.environ.get("KOKORO_SPEED", "0.92"))
        def synth(t):
            return np.concatenate([np.asarray(a) for _, _, a in pipe(t, voice="ff_siwis", speed=speed)]), 24000
    elif eng == "pocket":
        import torch
        from pocket_tts import TTSModel
        torch.manual_seed(7)
        m = TTSModel.load_model(language="french")
        st = m.get_state_for_audio_prompt(ref)
        def synth(t):
            return m.generate_audio(st, t).numpy(), m.sample_rate
    elif eng == "chatter":
        import torch
        from chatterbox.mtl_tts import ChatterboxMultilingualTTS
        torch.manual_seed(7)
        m = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
        ex = float(os.environ.get("CB_EXAG", "0.35")); cfg = float(os.environ.get("CB_CFG", "0.4"))
        def synth(t):
            w = m.generate(t, language_id="fr", audio_prompt_path=ref, exaggeration=ex, cfg_weight=cfg, temperature=0.7)
            return w.squeeze().numpy(), m.sr
    elif eng == "moss":
        src = os.environ.get("MOSS_SRC", "/home/claude/tts/moss-src")
        sys.path.insert(0, src); os.chdir(src)
        from onnx_tts_runtime import OnnxTtsRuntime
        rt = OnnxTtsRuntime(model_dir=os.environ.get("MOSS_MODELS"), thread_count=os.cpu_count() or 2)
        def synth(t):
            tmp = os.path.join(out, "_moss_tmp.wav")
            r = rt.synthesize(text=t, prompt_audio_path=ref, output_audio_path=tmp, seed=7)
            import soundfile as sf
            a, sr = sf.read(tmp, dtype="float32")
            if a.ndim > 1: a = a.mean(1)
            return a, sr
    else:
        sys.exit(f"moteur inconnu : {eng}")
    for j in jobs:
        a, sr = synth(j["text"])
        save(os.path.join(out, j["id"] + ".wav"), a, sr)
        print(j["id"], round(len(np.asarray(a).reshape(-1)) / sr, 2), flush=True)

if __name__ == "__main__":
    main()
