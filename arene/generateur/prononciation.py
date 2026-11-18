#!/usr/bin/env python3
"""Arène — préparation du texte prononcé pour la voix Piper (fr_FR-tom-medium).

Le moteur lit à l'anglaise les sigles et les mots qu'il ne connaît pas (« Bercy » → « beur-si »,
« APL » → « apeul », « −30 € » → « maïnus »). Ce module réécrit le texte `dit` avant la synthèse :
symboles, sigles, noms propres, puis signale tout mot encore lu à l'anglaise.

Usage autonome : python3 prononciation.py <episode.json> [dossier_voix]  → liste les mots suspects.
"""
import re, sys, json, os

# Mots à réécrire tels quels (clé = forme écrite, insensible à la casse sauf sigles).
RESPELL = {
    'Bercy': 'Bersi', 'Vody': 'Vodi', 'Crous': 'Crousse', 'Parcoursup': 'Parcour-soupe',
    'Insee': 'Insé', 'Ehpad': 'É-pade', 'EHPAD': 'É-pade', 'Medef': 'Médef', 'MEDEF': 'Médef',
    'LIOT': 'Liotte', 'Liot': 'Liotte', 'streaming': 'strimingue', 'Netflix': 'Nètflix',
    'TikTok': 'Tic Toc', 'Airbnb': 'Air-bi-enne-bi', 'Uber': 'Ubeur', 'Smic': 'Smic', 'SMIC': 'Smic',
    'CAF': 'Caf', 'URSSAF': 'Urssaf', 'UNEF': 'Unef', 'OTAN': 'Otan', 'ONU': 'Onu', 'ADEME': 'Adème',
    'ANAH': 'Ana', 'CROUS': 'Crousse', 'Sécu': 'Sécu', 'NUPES': 'Nupesse', 'COP': 'Cop',
    'Unédic': 'Unédic', 'UNEDIC': 'Unédic', 'CNIL': 'Cnil', 'INSEE': 'Insé',
}
# Sigles qui se prononcent comme un mot (sinon : épelés lettre par lettre).
SIGLES_MOTS = {'PACS', 'SAMU', 'SMUR', 'ZAD', 'ISF', 'IFI'}  # ISF/IFI : épelés aussi en vrai → retirés ci-dessous
SIGLES_MOTS -= {'ISF', 'IFI'}

UNITES = [
    (r'(\d)\s*Md€', r'\1 milliards d’euros'), (r'(\d)\s*M€', r'\1 millions d’euros'), (r'(\d)\s*k€', r'\1 mille euros'),
    (r'€\s*/\s*mois', 'euros par mois'), (r'€\s*/\s*an', 'euros par an'), (r'€\s*/\s*jour', 'euros par jour'),
    (r'(\d)\s*€', r'\1 euros'), (r'€', 'euros'),
    (r'(\d)\s*%', r'\1 pour cent'),
    (r'(\d)\s*cl\b', r'\1 centilitres'), (r'(\d)\s*km\b', r'\1 kilomètres'), (r'(\d)\s*m²', r'\1 mètres carrés'),
    (r'(\d)\s*h\b', r'\1 heures'), (r'(\d)\s*Go\b', r'\1 gigaoctets'),
    (r'\bn°\s*', 'numéro '), (r'\bart\.\s*', 'article '), (r'\bvs\b', 'contre'),
]
ANGLAIS = set('ɜɪʊʌɹæɒθðŋ') | {'ː', 'aɪ', 'əʊ', 'eɪ'}


def normaliser(texte):
    t = texte.replace(' ', ' ').replace(' ', ' ')
    # signes devant un nombre : −30 → moins 30, +52 → plus 52
    t = re.sub(r'[−–]\s*(?=\d)', 'moins ', t)
    t = re.sub(r'(?<![\w])-\s*(?=\d)', 'moins ', t)
    t = re.sub(r'\+\s*(?=\d)', 'plus ', t)
    # nombres : « 1 475 » reste lisible par le moteur ; « 2,05 » aussi ; on retire les espaces fines déjà faites
    for pat, rep in UNITES:
        t = re.sub(pat, rep, t)
    # mots réécrits
    for k, v in RESPELL.items():
        flags = 0 if k.isupper() else re.IGNORECASE
        t = re.sub(r'(?<![\w-])' + re.escape(k) + r'(?![\w-])', v, t, flags=flags)
    # sigles en capitales (2 à 6 lettres) : épelés « A.P.L. »
    def sigle(m):
        s = m.group(0)
        if s in SIGLES_MOTS:
            return s.capitalize()
        return '.'.join(s) + '.'
    t = re.sub(r'\b[A-Z]{2,6}\b', sigle, t)
    t = re.sub(r'(?<![\d,])\b1 euros', '1 euro', t)
    t = re.sub(r'(?<![\d])\b1(,\d+)? (milliard|million)s', r'1\1 \2', t)
    t = re.sub(r'\.\.', '.', t)
    t = re.sub(r'\s{2,}', ' ', t).strip()
    return t


def mots_suspects(texte, voix):
    """Renvoie les mots que le moteur lirait encore à l'anglaise (phonèmes absents du français)."""
    out = []
    for w in re.findall(r"[\wÀ-ÿ'’.-]+", texte):
        ph = ''.join(''.join(p) for p in voix.phonemize(w))
        if any(a in ph for a in ANGLAIS):
            out.append((w, ph))
    return out


if __name__ == '__main__':
    from piper import PiperVoice
    ep = json.load(open(sys.argv[1], encoding='utf-8'))
    vd = sys.argv[2] if len(sys.argv) > 2 else os.environ.get('ARENE_VOIX', 'voix')
    v = PiperVoice.load(os.path.join(vd, ep['voix']['modele'] + '.onnx'))
    bad = 0
    for ph in ep['phrases']:
        n = normaliser(ph['dit'])
        s = mots_suspects(n, v)
        print('•', n)
        for w, p in s:
            bad += 1; print('   ⚠ lu à l’anglaise :', w, '→', p)
    print('OK' if not bad else f'{bad} mot(s) à réécrire dans « dit »')
