# Maël Kerjean (TikTok) — amélioration continue par vagues (méthode kaizen)

Principe : **un seul changement par vague**. Une vague = 5 à 6 vidéos consécutives (une vidéo isolée varie trop pour conclure). Le lendemain de la fin d'une vague : bilan chiffré comparé à la vague précédente, puis Aymeric décide : on garde le changement, on l'annule ou on l'ajuste. Seule la vague suivante change quelque chose. On ne modifie et ne republie jamais une vidéo déjà publiée.

Objectif : se rapprocher, vague après vague, des spectateurs qui aiment les énigmes et achètent des livres-jeux (adultes, amateurs de Cluedo / d'enquêtes, cadeaux de Noël).

Indicateurs :
- Buffer (list_posts includeMetrics, chaîne 6ad38f15778b240e2f3a9081) : vues, temps de visionnage moyen, likes, commentaires, partages.
- À demander à Aymeric (TikTok Studio / KDP) : % de visionnage complet, nouveaux abonnés, ventes KDP de la période.
- Indicateur clé tant que la rétention est faible : **temps de visionnage moyen**.

## Réglages validés (appliqués à toutes les vidéos)
- Format « mini-histoire » (tiktok-kit/generateur/tiktok_video.py) : accroche en gros titre + voix off (Piper fr_FR-tom-medium, vitesse 0.82) + musique synthétisée libre de droits ; Rose et Sardine dans le décor du livre ; 3 suspects en pastilles de couleur ; plan en tuiles ; indices un par un lus par la voix ; récap + minuteur 8 s ; fin « A, B ou C ? Dis-le en commentaire ! » + couverture + « Sur Amazon : Maël Kerjean ».
- Légende : question, réponse de la veille, livre « sur Amazon : Maël Kerjean », hashtags.
- Une vidéo par jour, heure aléatoire entre 17h20 et 21h40. Pas de lien cliquable possible (compte personnel).

## Historique des vagues

### Vague 0 — référence (18 → 27 oct., 10 vidéos, ancien format : énigme en texte, 40 s, sans voix)
9 vidéos mesurées : 3 343 vues (~260 par vidéo, pics à 913 et 651) · **2 à 3 s de visionnage moyen** · 6 likes · 0 commentaire · 0 partage. Au 27/10 : 28 abonnés, 0 vente KDP.
Diagnostic : les spectateurs partent pendant l'écran titre, avant l'énigme.

### Vague 1 (28 oct. → 1er nov., 5 vidéos, ancien format)
Changement : fin « Sur Amazon : Maël Kerjean » au lieu de « Lien en bio » (aucun lien cliquable possible).
Limite : presque personne n'atteint l'écran de fin, donc cette vague sert surtout de deuxième mesure de l'ancien format.

### Vague 2 — EN COURS (2 → 7 nov., 6 vidéos) : rupture, nouveau format « mini-histoire »
Exception assumée à la règle du changement unique : l'ancien format ne retenait personne (2 s), on repart d'une nouvelle base validée par Aymeric le 27/10.
Hypothèse : temps de visionnage moyen > 8 s, premiers commentaires (prénom du suspect).
Bilan : le 8 nov. À partir de cette vague, un seul changement à la fois.

## Liste d'attente (une idée par vague, dans cet ordre sauf décision contraire)
1. Vidéo plus courte (≤ 30 s) : histoire en 2 phrases, indices plus rapides.
2. Accroche tournée vers le spectateur : « Toi, tu trouves le coupable en 8 secondes ? » au lieu de la question sur l'objet.
3. Réponse en vidéo le lendemain (début de la vidéo suivante : « Hier, c'était Jacques ! »), pour fidéliser.
4. Série numérotée « L'enquête du jour n° X » avec Rose et Sardine comme fil rouge.
5. Voix légèrement plus rapide (0.76) ou autre voix.
6. Décembre : calendrier de l'Avent en direct (1 énigme du Train des Neiges par jour, du 1er au 24).
