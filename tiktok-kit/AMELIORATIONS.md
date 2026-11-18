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
Changement : fin « Sur Amazon : Maël Kerjean » au lieu de « Lien en bio ».
Résultat (au 07/11) : 1 810 vues (~360 par vidéo) · 4,0 s de visionnage moyen (2,5 à 3 s sauf « Le prix effacé », Santons, 8,7 s) · 3 likes · 0 commentaire · 0 partage.
Conclusion : deuxième mesure de l'ancien format ; personne n'atteint l'écran de fin, la redirection ne peut pas encore être évaluée.

### Vague 2 (2 → 7 nov., 6 vidéos) : rupture, nouveau format « mini-histoire »
Exception assumée à la règle du changement unique : l'ancien format ne retenait personne (2 s), on repart d'une nouvelle base validée par Aymeric le 27/10.
Résultat (5 vidéos mesurées au 07/11, celle du 7 pas encore remontée) : 3 799 vues (**~760 par vidéo, ×2,1**) · **5,3 s** de visionnage moyen (4,3 à 6,7 s, ×1,8) · **89 likes** (×30) · 1 commentaire · **2 partages** (les premiers).
Meilleures : « La valise échangée » (Train des Neiges) 6,7 s et 18 likes ; « Le télégramme envolé » (Belle-Île) 29 likes.
Conclusion : le nouveau format est nettement meilleur sur toutes les mesures. Mais 5,3 s sur ~42 s : la plupart partent pendant l'histoire, avant le 1er indice (~13 s).
Décision d'Aymeric : en attente (bilan envoyé le 08/11).

### Vague 2 prolongée (9 → 11 nov., 3 vidéos, format inchangé) — en attendant la décision
Publiées avec un jour de décalage (rien le 8 nov., programmation faite trop tard) : Train des Neiges 3 (9 nov. 18:46), Santons de Minuit 5 (10 nov. 21:33), Train des Neiges 4 (11 nov. 17:39). Les fichiers gardent leur nom daté du 8, 9 et 10.
Correctif de mise en page sans effet sur le format : plus de « ? » orphelin dans la barre de question.

### Vague 3 (12 → 17 nov., 6 vidéos)
Décision d'Aymeric (09/11) : 0 vente KDP depuis le début, 28 abonnés, 136 j'aime. Il valide le changement et demande en plus d'améliorer la qualité globale (voix, musique, illustrations).
**Changement principal : vidéo courte (27 à 30 s), énigme beaucoup plus tôt** : accroche seule (2 s), histoire en une phrase avec les suspects affichés en même temps, 1er indice vers 5 s (au lieu de 13 s), minuteur 5 s (au lieu de 8).
**Qualité (demandée par Aymeric, liée au même objectif de rétention)** : voix plus rapide (0.78) et traitée (égalisation, compression, légère pièce) ; musique stéréo plus riche (batterie feutrée, célesta en arpèges, réverbération) ; effets sonores (whoosh aux transitions, ding à chaque indice, montée avant le minuteur, battement de cœur, accord de révélation) ; volume normalisé à -14 LUFS ; Rose avec une loupe et un liseré de lumière ; zoom lent sur le décor ; rebond des textes ; vignettage et grain ; neige/pluie qui continue derrière les indices.
Attention : comme plusieurs choses changent, on attribue le résultat à l'ensemble « format court + finition ».
Hypothèse : temps moyen de visionnage > 8 s (contre 5,3 s), plus de commentaires.
Résultat (au 18/11) : 4 438 vues (~740 par vidéo, stable) · **3,9 s de visionnage moyen (contre 5,3 s, −27 %)** · 157 likes (~26 par vidéo contre ~23) · 0 commentaire · 3 partages.
Détail : seule « La place réservée » (Train, 12/11) tient 5,35 s ; les 5 autres entre 3,1 et 4,0 s. Meilleure en likes : « Le chant interrompu » (Santons) 47 likes, mais 3,6 s.
Pour comparaison, vague 2 prolongée (4 vidéos, 7 → 11 nov., format long) : ~750 vues · 5,3 s · ~23 likes par vidéo.
Conclusion : hypothèse non validée. Raccourcir n'a pas retenu plus longtemps : les gens partent dans les 2 à 4 premières secondes, donc le début compte plus que la longueur. Le gros titre seul (sans scène ni histoire) retient moins bien que l'ouverture narrative de la vague 2. Les likes progressent un peu, les commentaires restent à 0.
Décision d'Aymeric : en attente (bilan envoyé le 18/11).

### Vague 3 prolongée (18 → 20 nov., 3 vidéos, format inchangé) — en attendant la décision
Santons de Minuit 8 « La lettre au Père Noël » (18/11 18:09), Tempête sur Belle-Île 6 « Le piano muet » (19/11 20:14), Santons de Minuit 9 « Le lavoir gelé » (20/11 18:52). Programmées dans Buffer.

## Liste d'attente (une idée par vague, dans cet ordre sauf décision contraire)
1. Vidéo plus courte (≤ 30 s) : histoire en 2 phrases, indices plus rapides.
2. Accroche tournée vers le spectateur : « Toi, tu trouves le coupable en 8 secondes ? » au lieu de la question sur l'objet.
3. Réponse en vidéo le lendemain (début de la vidéo suivante : « Hier, c'était Jacques ! »), pour fidéliser.
4. Série numérotée « L'enquête du jour n° X » avec Rose et Sardine comme fil rouge.
5. Voix légèrement plus rapide (0.76) ou autre voix.
6. Décembre : calendrier de l'Avent en direct (1 énigme du Train des Neiges par jour, du 1er au 24).
