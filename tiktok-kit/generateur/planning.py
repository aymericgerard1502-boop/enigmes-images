#!/usr/bin/env python3
"""Planning des vidéos TikTok + légendes. Usage : python3 planning.py [--render]"""
import json, os, sys, subprocess
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
KIT = os.path.join(ROOT, "tiktok-kit")
PLAN = [  # date, slug, num
    ("2026-10-18", "La-Nuit-de-l-Ankou", 1), ("2026-10-19", "Tempete-sur-Belle-Ile", 1),
    ("2026-10-20", "La-Nuit-de-l-Ankou", 2), ("2026-10-21", "Vendanges-tardives", 1),
    ("2026-10-22", "La-Nuit-de-l-Ankou", 3), ("2026-10-23", "Les-Santons-de-Minuit", 1),
    ("2026-10-24", "La-Nuit-de-l-Ankou", 4), ("2026-10-25", "Tempete-sur-Belle-Ile", 2),
    ("2026-10-26", "La-Nuit-de-l-Ankou", 5), ("2026-10-27", "Vendanges-tardives", 2),
]
TAGS = {"La-Nuit-de-l-Ankou": "#halloween #legendebretonne", "Tempete-sur-Belle-Ile": "#bretagne #belleile",
        "Vendanges-tardives": "#alsace #vendanges", "Les-Santons-de-Minuit": "#provence #noel",
        "Le-Train-des-Neiges": "#calendrierdelavent #noel"}
livres = {l["slug"]: l for l in json.load(open(os.path.join(KIT, "enigmes.json")))}

def enigme(slug, num): return next(e for e in livres[slug]["enigmes"] if e["num"] == num)

def items():
    out, prev = [], None
    for date, slug, num in PLAN:
        e, l = enigme(slug, num), livres[slug]
        n = 24 if "Neiges" in l["livre"] else 40
        lines = [f"🔍 {e['titre']} : qui se trouvait {e['question_lieu'][1]} ?",
                 "Ton suspect en commentaire 👇 Réponse demain sur le compte."]
        if prev:
            pe = enigme(*prev)
            lines.append(f"✅ Réponse d'hier (« {pe['titre']} ») : {pe['coupable']} !")
        lines.append(f"📖 {n} énigmes comme celle-ci dans « {l['livre']} » (lien en bio)")
        lines.append(f"#enigme #trouvelecoupable #enquete #cassetete #livrejeu #booktokfrance {TAGS[slug]}")
        fn = f"tiktok-videos/{date}_{slug}_{num:02d}.mp4"
        out.append(dict(date=date, slug=slug, num=num, file=fn, caption="\n".join(lines), coupable=e["coupable"]))
        prev = (slug, num)
    return out

if __name__ == "__main__":
    its = items()
    json.dump(its, open(os.path.join(ROOT, "tiktok-videos", "planning.json"), "w"), ensure_ascii=False, indent=1)
    if "--render" in sys.argv:
        gen = os.path.join(os.path.dirname(os.path.abspath(__file__)), "video_enigme.py")
        def run(it): return subprocess.run(["python3", gen, it["slug"], str(it["num"]), os.path.join(ROOT, it["file"])], capture_output=True, text=True).stdout.strip()
        with ThreadPoolExecutor(4) as ex:
            for r in ex.map(run, its): print(r)
