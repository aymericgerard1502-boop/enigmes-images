#!/usr/bin/env python3
"""Extrait les énigmes 7 à 24 du Train des Neiges (PDF intérieur du livre), les vérifie avec un solveur
et choisit, pour la vidéo, le plus petit sous-ensemble d'indices du livre qui suffit à répondre à la question.

Usage : python3 extraire_train.py <interieur.pdf> [--ecrire]
"""
import itertools, json, os, re, subprocess, sys, unicodedata
import numpy as np, pdfplumber

PDF = sys.argv[1]
KIT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SLUG = "Le-Train-des-Neiges"
PAGES = {j: (14 + (j - 7) if j <= 12 else 21 + (j - 13) if j <= 18 else 28 + (j - 19)) for j in range(7, 25)}
MAX_INDICES = 5

def norm(t):
    t = unicodedata.normalize("NFD", t.replace("’", "'").lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn").strip()

def texte(p, layout=False):
    a = ["pdftotext", "-f", str(p), "-l", str(p)] + (["-layout"] if layout else []) + [PDF, "-"]
    return subprocess.run(a, capture_output=True, text=True).stdout

# ---------------------------------------------------------------- coupables (pages de solutions)
coupables = []
for p in range(39, 43):
    for ln in texte(p, True).splitlines():
        coupables += re.findall(r"Coupable : (\S+) \(([^)]+)\)", ln)
assert len(coupables) == 24, len(coupables)

# ---------------------------------------------------------------- lecture d'une page d'énigme
def lire(jour):
    p = PAGES[jour]
    L = [l.strip() for l in texte(p).splitlines() if l.strip()]
    assert re.match(rf"{jour}(ER)? DÉCEMBRE", L[0]), (jour, L[0])
    titre = L[1]; i = 2; inc = []
    while L[i] != "PLAN DES LIEUX": inc.append(L[i]); i += 1
    incident = " ".join(inc)
    # plan : rectangles + mots à l'intérieur
    with pdfplumber.open(PDF) as pdf:
        pg = pdf.pages[p - 1]
        words = [w for w in pg.extract_words(extra_attrs=["upright"]) if w["upright"]]
        def y_of(txt): return next(w for w in words if w["text"] == txt)["top"]
        y_plan, y_ind = y_of("PLAN"), y_of("INDICES")
        x_susp = next(w for w in words if w["text"] == "SUSPECTS")["x0"]
        formes = pg.rects + pg.curves   # intérieur : rectangles jointifs ; extérieur : cadres arrondis reliés par des pointillés
        rects = [r for r in formes if y_plan < r["top"] < y_ind and r["x1"] < x_susp + 5 and r["width"] > 40 and r["height"] > 25]
        cells = []
        for r in rects:
            inside = [w for w in words if r["x0"] <= w["x0"] and w["x1"] <= r["x1"] and r["top"] <= w["top"] and w["bottom"] <= r["bottom"]]
            if inside:
                inside.sort(key=lambda w: (round(w["top"]), w["x0"]))
                cells.append(dict(label=" ".join(w["text"] for w in inside), box=(r["x0"], r["top"], r["x1"], r["bottom"])))
        # question : mots droits sous « QUESTION », dans la colonne de droite
        q = next(w for w in words if w["text"] == "QUESTION")
        y_q = q["top"]; y_ib = next(w for w in words if w["text"] == "INDICES")["bottom"]
        zi = pg.crop((0, y_ib + 1, pg.width, y_q - 1)).filter(lambda o: o.get("object_type") != "char" or o.get("upright", True))
        texte_indices = zi.extract_text()
        zone = pg.crop((q["x0"] - 2, q["bottom"] + 1, pg.width, min(pg.height, q["bottom"] + 60)))
        zone = zone.filter(lambda o: o.get("object_type") != "char" or o.get("upright", True))
        question = " ".join(zone.extract_text(x_tolerance=1.2).split())
        question = re.sub(r"\s+\?", " ?", question[: question.index("?") + 1])
    # suspects / objets / indices (texte brut)
    labels = {c["label"] for c in cells}
    j = L.index("SUSPECTS"); k = L.index("OBJETS"); m = L.index("INDICES"); n = L.index("QUESTION")
    suspects = [l.split()[0] for l in L[j + 1:k] if l not in labels and l[0].isupper() and l.split()[0] in CAST]
    obj_txt = " ".join(l for l in L[k + 1:m] if l not in labels)
    objets = [o.strip(" .") for o in re.split(r",\s*", obj_txt) if o.strip(" .")]
    indices, cur = [], None
    for l in [x.strip() for x in texte_indices.splitlines() if x.strip()]:
        mm = re.match(r"^(\d+)\.\s+(.*)$", l)
        if mm: cur = mm.group(2); indices.append(cur)
        elif indices: indices[-1] += " " + l
    indices = [re.sub(r"\.\s+\S{1,3}$", ".", " ".join(x.split())) for x in indices]   # lettres parasites des en-têtes inclinés
    return dict(jour=jour, titre=titre, incident=incident, cells=cells, question=question,
                suspects=suspects, objets=objets, indices=indices, page=p)

CAST = "Jacques Constance Gabriel Mathilde Edmond Tatiana Nicolas Clara Henri Margaux Ulysse Bertille Samuel".split()

# ---------------------------------------------------------------- logique
def voisins(cells):
    n = len(cells); A = np.zeros((n, n), bool)
    for a, b in itertools.combinations(range(n), 2):
        x0, y0, x1, y1 = cells[a]["box"]; u0, v0, u1, v1 = cells[b]["box"]; t = 30   # écart max entre deux cases voisines
        horiz = (0 <= u0 - x1 < t or 0 <= x0 - u1 < t or abs(x1 - u0) < 3 or abs(u1 - x0) < 3) and min(y1, v1) - max(y0, v0) > 10
        vert = (0 <= v0 - y1 < t or 0 <= y0 - v1 < t or abs(y1 - v0) < 3 or abs(v1 - y0) < 3) and min(x1, u1) - max(x0, u0) > 10
        A[a, b] = A[b, a] = horiz or vert
    return A

def salle(phrase, rooms):
    ph = norm(phrase); best = None
    for i, r in enumerate(rooms):
        k = ph.find(norm(r))
        if k >= 0 and (best is None or k < best[0]): best = (k, i)
    if best is None: raise ValueError(f"lieu inconnu : {phrase} / {rooms}")
    return best[1]

def objet(phrase, objs):
    ph = norm(phrase)
    for i, o in enumerate(objs):
        if norm(o) == ph: return i
    for i, o in enumerate(objs):
        if ph.endswith(norm(o).split(" ", 1)[-1]): return i
    raise ValueError(f"objet inconnu : {phrase} / {objs}")

def compiler(ind, P, rooms, objs):
    """-> fonction (loc[N,n], obj[N,n], A) -> bool[N] ; loc/obj : salle/objet de chaque suspect pour chaque cas."""
    s = ind.replace("’", "'").rstrip(".")
    pers = {nm: i for i, nm in enumerate(P)}
    def ref(t):   # renvoie f(loc,obj) -> indice de la personne (N,)
        t = t.strip()
        m = re.match(r"^(?:la|La) personne qui avait (.+)$", t)
        if m:
            o = objet(m.group(1), objs); return lambda loc, ob: np.argmax(ob == o, axis=1)
        if t in pers: i = pers[t]; return lambda loc, ob: np.full(len(loc), i)
        raise ValueError("référence : " + t)
    def L_(f): return lambda loc, ob: loc[np.arange(len(loc)), f(loc, ob)]
    V = r"(?:une pièce voisine de celle|un lieu voisin de celui)"
    m = re.match(r"^Ni (\w+) ni (\w+) n'avai(?:en)?t (.+)$", s)
    if m:
        a, b, o = pers[m.group(1)], pers[m.group(2)], objet(m.group(3), objs)
        return lambda loc, ob, A: (ob[:, a] != o) & (ob[:, b] != o)
    m = re.match(r"^(\w+) et (\w+) (ne )?se trouvaient (?:pas )?dans des (?:pièces voisines|lieux voisins)$", s)
    if m:
        a, b, neg = pers[m.group(1)], pers[m.group(2)], bool(m.group(3))
        return lambda loc, ob, A: A[loc[:, a], loc[:, b]] != neg
    m = re.match(rf"^(.+?) (ne )?se trouvait (?:pas )?dans {V} de (.+)$", s)
    if m:
        f, g, neg = L_(ref(m.group(1))), L_(ref(m.group(3))), bool(m.group(2))
        return lambda loc, ob, A: A[f(loc, ob), g(loc, ob)] != neg
    m = re.match(r"^(.+?) (n')?avait (?:pas )?(.+)$", s)
    if m and not m.group(1).lower().startswith("la personne"):
        a, o, neg = pers[m.group(1)], objet(m.group(3), objs), bool(m.group(2))
        return lambda loc, ob, A: (ob[:, a] == o) != neg
    m = re.match(r"^(.+?) (n')?(?:était|se trouvait) (?:pas )?(.+)$", s)
    if m:
        f, r, neg = L_(ref(m.group(1))), salle(m.group(3), rooms), bool(m.group(2))
        return lambda loc, ob, A: (f(loc, ob) == r) != neg
    raise ValueError("indice non compris : " + ind)

def resoudre(d):
    P, rooms = d["suspects"], [c["label"] for c in d["cells"]]
    objs = [o for o in d["objets"]]; n = len(P)
    assert len(rooms) == n == len(objs), (d["jour"], P, rooms, objs)
    A = voisins(d["cells"])
    perms = np.array(list(itertools.permutations(range(n))))
    loc = np.repeat(perms, len(perms), axis=0); ob = np.tile(perms, (len(perms), 1))
    masks = [compiler(c, P, rooms, objs)(loc, ob, A) for c in d["indices"]]
    ok = np.logical_and.reduce(masks)
    sols = np.where(ok)[0]
    qr = salle(d["question"].replace("Qui se trouvait", ""), rooms)
    d["question"] = f"Qui se trouvait {phrase_lieu(rooms[qr], d)} ?"
    rep = np.argmax(loc == qr, axis=1)          # qui est dans la salle de la question
    res = dict(n_solutions=len(sols), rooms=rooms, A=A, loc=loc, ob=ob, masks=masks, qr=qr, rep=rep)
    if len(sols) == 1:
        s = sols[0]; res["solution"] = {P[i]: (rooms[loc[s, i]], objs[ob[s, i]]) for i in range(n)}
        res["coupable"] = P[rep[s]]
    # Version vidéo : 5 affirmations au plus. On part des indices du livre et, si besoin, on ajoute au plus
    # 2 « faits établis par Rose » (la place d'un autre suspect, tirée de la solution du livre).
    # Chaque affirmation est nécessaire, aucune ne donne la réponse seule ; on minimise les faits puis la longueur.
    stmts = [(d["indices"][i], masks[i], "livre") for i in range(len(masks))]
    if len(sols) == 1:
        s0 = sols[0]
        for i in range(n):
            if i != rep[s0]:
                txt = f"{P[i]} était {phrase_lieu(rooms[loc[s0, i]], d)}."
                stmts.append((txt, loc[:, i] == loc[s0, i], "fait"))
        n_lieux = len(stmts)
        for i in range(n):   # faits d'objets, utilisés seulement en dernier recours
            o = objs[ob[s0, i]]; o = o[0].lower() + o[1:]
            stmts.append((f"{P[i]} avait {o}.", ob[:, i] == ob[s0, i], "fait"))
    def suffit(sub):
        if not sub: return False
        mk = np.logical_and.reduce([stmts[i][1] for i in sub])
        return mk.any() and len(set(rep[mk])) == 1
    seuls = {i for i in range(len(stmts)) if suffit((i,))}
    best = None
    for kmax, fmax, lmin, objets_ok in ((5, 2, 2, False), (6, 3, 2, False), (6, 3, 1, False), (6, 3, 1, True), (7, 4, 1, True)):
        candidats = [i for i in range(len(stmts)) if i not in seuls and (objets_ok or len(sols) != 1 or i < n_lieux)]
        cands = []
        for k in range(3, kmax + 1):
            for sub in itertools.combinations(candidats, k):
                nf = sum(stmts[i][2] == "fait" for i in sub)
                if nf > fmax or k - nf < lmin or not suffit(sub): continue
                if any(suffit(tuple(x for x in sub if x != i)) for i in sub): continue
                cands.append((sum(len(stmts[i][0]) for i in sub) + 45 * nf, sub))
        if cands: best = min(cands)[1]; break
    res["video"] = [(stmts[i][0], stmts[i][2]) for i in best] if best else []
    best = [i for i in best if i < len(masks)] if best else []
    res["sous_ensemble"] = list(best) if best else []
    return res

LIEUX = {  # formes longues, reprises de la formulation du livre
    "Bibliothèque": "dans la bibliothèque", "Cabine de luxe": "dans la cabine de luxe", "Chapelle": "à la chapelle",
    "Compartiment du chef": "dans le compartiment du chef", "Cuisine": "dans la cuisine", "Escalier": "dans l'escalier",
    "Fourgon": "dans le fourgon", "Fumoir": "dans le fumoir", "Gare": "à la gare", "Grand salon": "dans le grand salon",
    "Hôtel": "à l'hôtel de la gare", "Patinoire": "à la patinoire", "Plateforme": "sur la plateforme",
    "Remise": "dans la remise des chasse-neige", "Salle d'attente": "dans la salle d'attente",
    "Salle à manger": "dans la salle à manger", "Téléphérique": "au téléphérique", "Vestiaire": "au vestiaire",
    "Voiture-bar": "dans la voiture-bar", "Voiture-salon": "dans la voiture-salon", "Véranda": "dans la véranda",
    "Wagon-restaurant": "dans le wagon-restaurant", "Épicerie": "à l'épicerie"}

def phrase_lieu(room, d):
    """Forme longue (« dans la cabine de luxe »)."""
    if room in LIEUX: return LIEUX[room]
    for t in d["indices"] + [d["question"]]:
        for m in re.finditer(r"(?:était|se trouvait) (?:pas )?((?:dans|à|au|aux|sur|sous|devant)\b[^.?]*)", t.replace("’", "'")):
            ph = m.group(1).strip()
            if "voisin" in ph: continue
            try:
                if salle(ph, [room]) == 0: return ph
            except ValueError: pass
    return "dans " + ("l'" if norm(room)[0] in "aeiouyh" else "le ") + room.lower()

def grille(cells, A):
    """Place de chaque lieu (ligne, colonne) et paires voisines, pour redessiner le plan dans la vidéo."""
    def groupes(vals):
        vals = sorted(vals); g = [[vals[0]]]
        for v in vals[1:]:
            (g[-1].append(v) if v - g[-1][-1] < 25 else g.append([v]))
        return [sum(x) / len(x) for x in g]
    ys = groupes([c["box"][1] for c in cells]); xs = groupes([c["box"][0] for c in cells])
    near = lambda v, L: min(range(len(L)), key=lambda i: abs(L[i] - v))
    cases = [{"lieu": c["label"], "ligne": near(c["box"][1], ys), "col": near(c["box"][0], xs)} for c in cells]
    vois = [[cells[a]["label"], cells[b]["label"]] for a in range(len(cells)) for b in range(a + 1, len(cells)) if A[a, b]]
    return {"cases": cases, "voisins": vois}

if __name__ == "__main__":
    out = []
    for j in range(7, 25):
        d = lire(j)
        r = resoudre(d)
        cp, cl = coupables[j - 1]
        flag = "OK" if r["n_solutions"] == 1 and r.get("coupable") == cp else "!!"
        sub = r["sous_ensemble"]
        nf = sum(1 for _, k in r["video"] if k == "fait")
        print(f"{flag} {j:2d} {d['titre'][:26]:26s} {len(d['suspects'])} susp. {len(d['indices']):2d} ind. -> coupable {r.get('coupable')} (livre {cp}) ; vidéo : {len(r['video'])} affirmations dont {nf} fait(s)")
        if flag != "OK":
            print("   salles", r["rooms"], "\n   objets", d["objets"], "\n   question", d["question"]); print("   ", d["indices"])
        sol = r.get("solution", {})
        out.append({"num": j, "titre": d["titre"], "incident": d["incident"],
                    "question_lieu": [r["rooms"][r["qr"]], d["question"].replace("Qui se trouvait", "").strip(" ?")],
                    "coupable": r.get("coupable"),
                    "solution": {p: {"lieu": [l, phrase_lieu(l, d)], "objet": [o.split(" ", 1)[-1] if o.split(" ")[0].lower() in ("le", "la", "les", "l'") else o, o[0].lower() + o[1:]]} for p, (l, o) in sol.items()},
                    "indices": [t for t, _ in r["video"]],
                    "faits_ajoutes": [t for t, k in r["video"] if k == "fait"],
                    "indices_livre": d["indices"],
                    "image": f"enigmes/{SLUG}_enigme{j:02d}.png", "page": d["page"],
                    "plan_grille": grille(d["cells"], r["A"])})
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "train_7_24.json"), "w"), ensure_ascii=False, indent=1)
    if "--ecrire" in sys.argv:   # ajout à enigmes.json + image de chaque page
        path = os.path.join(KIT, "enigmes.json"); livres = json.load(open(path))
        b = next(x for x in livres if x["slug"] == SLUG)
        b["enigmes"] = [e for e in b["enigmes"] if e["num"] < 7] + [{k: v for k, v in e.items() if k != "page"} for e in out]
        if not b.get("amazon"): b["amazon"] = "https://www.amazon.fr/dp/B0HNNJBKS7"
        json.dump(livres, open(path, "w"), ensure_ascii=False, indent=1)
        for e in out:
            subprocess.run(["pdftoppm", "-r", "200", "-png", "-f", str(e["page"]), "-l", str(e["page"]), "-singlefile", PDF,
                            os.path.join(KIT, e["image"][:-4])], check=True)
        print("enigmes.json :", len(b["enigmes"]), "énigmes du Train des Neiges")
