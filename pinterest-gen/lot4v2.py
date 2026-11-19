"""Nouveau lot 4 (20-29 nov.) : 10 épingles v2, styles 1 (flat-lay) et 2 (coin du feu) en alternance."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from v2 import *

TRAIN, SANTONS, DUO = 'Le-Train-des-Neiges', 'Les-Santons-de-Minuit', 'Deux-enquetes-de-Noel'
AMZ = {TRAIN: 'https://www.amazon.fr/dp/B0HNNJBKS7', SANTONS: 'https://www.amazon.fr/dp/B0HM13CCC4',
       DUO: 'https://www.amazon.fr/dp/B0HS845H1Z'}
BOARD = {'enigmes': '1149895786049019780', 'avent': '1149895786049019791', 'noel': '1149895786049019793'}
SUB_T = '3 suspects, 4 indices : à vous de jouer'

PINS = [
 dict(id='41', day='2026-11-20', kind='hero', scene='A', slug=TRAIN, stamp='avent', board='avent',
      kicker="LIVRE-JEU D'ENQUÊTE", title=["Calendrier de l'Avent", 'pour adultes'], sub='24 énigmes · une par jour jusqu’à Noël'),
 dict(id='42', day='2026-11-21', kind='teaser', scene='B', slug=TRAIN, num=5, board='enigmes',
      kicker='ÉNIGME DU 5 DÉCEMBRE', title=['Qui a changé', 'la réservation ?'], sub=SUB_T),
 dict(id='43', day='2026-11-22', kind='hero', scene='A3', slug=TRAIN, stamp='avent', board='noel',
      kicker='IDÉE CADEAU DE NOËL', title=['Pour un fan', "d'énigmes"], sub='Un calendrier de l’Avent d’enquête'),
 dict(id='44', day='2026-11-23', kind='hero', scene='B2', slug=DUO, stamp='2en1', board='noel',
      kicker='IDÉE CADEAU DE NOËL', title=['Deux enquêtes', 'de Noël'], sub='Les Santons de Minuit + Le Train des Neiges'),
 dict(id='45', day='2026-11-24', kind='teaser', scene='A2', slug=TRAIN, num=2, board='enigmes',
      kicker='ÉNIGME DU 2 DÉCEMBRE', title=['Qui a échangé la valise ?'], sub=SUB_T),
 dict(id='46', day='2026-11-25', kind='hero', scene='B', slug=TRAIN, stamp='avent', board='avent',
      kicker="LIVRE-JEU D'ENQUÊTE", title=["Calendrier de l'Avent", 'pour adultes'], sub='24 énigmes · une par jour jusqu’à Noël'),
 dict(id='47', day='2026-11-26', kind='teaser', scene='A3', slug=SANTONS, num=3, board='enigmes',
      kicker='ÉNIGME DE NOËL · PROVENCE', title=['Qui a dérangé la crèche ?'], sub='3 suspects, 4 indices : à vous de jouer'),
 dict(id='48', day='2026-11-27', kind='hero', scene='B2', slug=TRAIN, stamp='avent', board='avent',
      kicker="CALENDRIER DE L'AVENT ADULTE", title=['À commander avant', 'le 1er décembre'], sub='Une énigme par jour jusqu’à Noël'),
 dict(id='49', day='2026-11-28', kind='teaser', scene='A2', slug=TRAIN, num=6, board='enigmes',
      kicker='ÉNIGME DU 6 DÉCEMBRE', title=['Qui a brisé son verre ?'], sub=SUB_T),
 dict(id='50', day='2026-11-29', kind='hero', scene='B', flip=True, slug=TRAIN, stamp='avent', board='avent',
      kicker='DERNIÈRE MINUTE', title=["L'Avent commence", 'mardi'], sub='24 énigmes à ouvrir dès le 1er décembre'),
]

STAMPS = {'avent': stamp_avent, '2en1': stamp_2en1}

if __name__ == '__main__':
    out = os.path.join(ROOT, '..', 'v2', 'lot4'); os.makedirs(out, exist_ok=True)
    prev = '/tmp/claude-0/-home-claude/e6385d71-496a-5de3-8d66-6851e69871dd/scratchpad/lot4'; os.makedirs(prev, exist_ok=True)
    for p in PINS:
        if p['kind'] == 'hero':
            ov = hero(p['scene'], p['slug'], p['kicker'], p['title'], p['sub'],
                      stamp=STAMPS[p['stamp']]() if p.get('stamp') else None, flip=p.get('flip', False))
        else:
            ov = teaser(p['scene'], p['slug'], p['num'], p['kicker'], p['title'], p['sub'])
        name = f"ov_{p['id']}"
        ov.save(os.path.join(out, name + '.png'))
        bgk = 'A' if p['scene'] == 'A' else p['scene']
        bg = Image.open(os.path.join(ROOT, '..', 'v2', 'bg', bgk + '.jpg')).convert('RGBA').resize((W, H))
        if p.get('flip'): bg = bg.transpose(Image.FLIP_LEFT_RIGHT)
        bg.alpha_composite(ov); bg.convert('RGB').resize((500, 750)).save(os.path.join(prev, name + '.jpg'), quality=85)
    json.dump(PINS, open(os.path.join(out, 'pins.json'), 'w'), ensure_ascii=False, indent=1)
    print('ok')
