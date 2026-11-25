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
Décision d'Aymeric (18/11) : 29 abonnés, toujours 0 vente KDP. Il lance la vague 4 proposée.

### Vague 3 prolongée (18 nov., 1 vidéo)
Santons de Minuit 8 « La lettre au Père Noël » (18/11 18:09). Les versions courtes du 19 et du 20 ont été remplacées par la vague 4 avant publication.

### Vague 4 (19 → 24 nov., 6 vidéos)
Base : retour au format de la vague 2 (mini-histoire, ~37 à 46 s, minuteur 8 s), qui avait le meilleur temps de visionnage (5,3 s).
**Changement unique : les 2,6 premières secondes.** Au lieu de la question sur l'objet (« Qui a fait taire le piano ? »), Rose défie le spectateur : voix « Toi, tu trouves le coupable avant Rose ? », gros titre « TOI, TU LE TROUVES AVANT ROSE ? », et les 3 suspects (pastilles + prénoms, « 3 suspects, 1 seul coupable ») visibles dès la 1re image, sans apparition progressive.
Hypothèse : moins de départs dans les 3 premières secondes, temps moyen > 6 s (contre 5,3 s en vague 2 et 3,9 s en vague 3), plus de commentaires.
Vidéos (programmées dans Buffer) : Belle-Île 6 « Le piano muet » (19/11 20:43), Santons 9 « Le lavoir gelé » (20/11 19:52), Vendanges 5 « Les cigognes dérangées » (21/11 19:14), Santons 10 « Le dernier verre » (22/11 21:21), Belle-Île 7 « La page arrachée » (23/11 21:31), Vendanges 6 « La borne déplacée » (24/11 19:26).
Résultat (25/11, sans le 24/11 trop récent : 231 vues) : ~650 vues par vidéo · **4,2 s de visionnage moyen** (3,2 à 5,6 s) · ~12 likes par vidéo · 0 commentaire · 1 partage.
Comparaison : vague 2 ~750 vues, 5,3 s, ~23 likes ; vague 3 ~740 vues, 3,9 s, ~26 likes.
Conclusion : hypothèse non validée. L'ouverture « défi » ne retient pas mieux que la vague 2 et les likes baissent de moitié. Les deux meilleures (22/11 « Le dernier verre » 5,0 s, 23/11 « La page arrachée » 5,6 s) sont aussi les plus longues : celles qui passent le cap des premières secondes regardent davantage. Le frein principal reste les 3 premières secondes, et la voix (vague 5) est la prochaine piste testée.

### Priorité avant la vague 5 : la voix off (demande d'Aymeric, 20/11)
Constat : visuel et scénario bons, mais la voix Piper « Tom » fait amateur (ton plat, mots qui se chevauchent, ponctuation et silences sautés). Les spectatrices partent après 3 à 4 s.
1. Mise en rythme (faite, `generateur/voix_off.py` + `voix_worker.py`) : synthèse phrase par phrase, blancs retirés, puis vrais silences : 0,40 s après un point, 0,45 s après « ? », 0,15 s après une virgule, 0,75 s avant une révélation (marqueur ⏸). Plus aucun chevauchement.
2. Test à l'aveugle A/B/C/D (même script de vague 4, même rythme), moteurs gratuits dont les POIDS autorisent l'usage commercial : Kokoro ff_siwis (Apache 2.0), Kyutai Pocket TTS (CC BY 4.0), Resemble Chatterbox Multilingual (MIT), OpenMOSS MOSS-TTS-Nano (Apache 2.0). Voix de référence pour le clonage : lectrice française de CML-TTS (LibriVox, CC BY 4.0). Écartés : Mistral Voxtral TTS (poids CC BY-NC 4.0, GPU 16 Go), Coqui XTTS (non commercial), services payants.
Résultat du test (20/11) : 3 versions envoyées (voix_A/B/C.mp3, correspondance gardée hors du dépôt jusqu'au choix d'Aymeric). MOSS-TTS-Nano écarté après essai : en français, le clonage invente des mots (« Ah bon… », « Juste les haïsses cigognes »). Pocket TTS : clonage verrouillé derrière une acceptation de conditions sur Hugging Face, donc voix intégrée « estelle » (enregistrement Kyutai sous CC0). Chaque phrase des moteurs autorégressifs (Pocket, Chatterbox) est réécoutée par Whisper et refaite si elle s'écarte du texte (jusqu'à 3 essais). Les phrases d'un seul mot sont fragiles (« Alors… » devenait « Allô ») : écrire « Alors, à ton avis… ⏸ ».
3. La voix choisie remplace Tom à partir de la vague 5. Aucune vidéo publiée n'est retouchée.
**Choix d'Aymeric (22/11) : voix A = Chatterbox Multilingual (MIT), clonée sur la lectrice CML-TTS 5476_3103 (CC BY 4.0), exagération 0,35, cfg 0,4.** Commande par défaut de tiktok_video.py ; `--tom` pour l'ancienne voix.

### Vague 5 — EN COURS (25 → 30 nov., 6 vidéos)
Changement unique : la voix (conteuse féminine rythmée à la place de Tom). Le reste = format de la vague 4.
Vidéos (programmées dans Buffer le 22/11) : Belle-Île 8 (25/11 18:43), Ankou 9 (26/11 18:15), Vendanges 7 (27/11 20:50), Belle-Île 9 (28/11 19:03), Ankou 10 (29/11 19:47), Vendanges 8 (30/11 20:29). Bilan : le 1er déc. Ankou choisi pour coller au persona (légendes bretonnes, paranormal doux).
Hypothèse : temps moyen > 6 s (vague 4 : 3 à 4 s selon Aymeric). Puis calendrier de l'Avent dès le 1er décembre (jours 1 à 4 programmés le 25/11 : 1/12 17:55, 2/12 19:23, 3/12 20:30, 4/12 20:36).

### Calendrier de l'Avent en direct (1er → 24 déc.) — PRÊT
- PDF intérieur reçu le 22/11. `outils/extraire_train.py` extrait les énigmes 7 à 24, traduit chaque indice en contrainte logique, et un solveur vérifie que la solution est unique et que le coupable est celui des pages de solutions du livre : 18/18 OK. Plans redessinés en grille (voisinages lus sur les plans du livre).
- Le livre demande 6 à 12 indices (4 à 5 suspects) : trop pour TikTok. Version vidéo = 3 à 6 affirmations : indices du livre choisis par le solveur (chacun nécessaire, aucun ne donne la réponse seul), complétés au besoin par 1 à 3 « faits établis » tirés de la solution du livre. Même question, même coupable que le livre ; la version complète reste dans le livre. Champs `indices_livre` et `faits_ajoutes` dans enigmes.json.
- Format : « Hier : c'était X ! » + badge « CALENDRIER DE L'AVENT · JOUR X/24 » dès la 1re image, suspects A/B/C(/D/E), fin « A, B ou C ? Tape ta lettre en commentaire ! » avec les pastilles lettre-prénom ; légende « Abonne-toi pour la suite demain ». Choix A/B/C intégré (point 1 de la vague 6 avancé).
- **24/24 vidéos rendues et poussées (23/11)**, 49 à 63 s chacune. Contrôle Whisper : tous les indices, la question et « Hier : c'était … » entendus correctement (seul écart : « Margaux » transcrit « Margot », même prononciation).
- Leçons du rendu : à l'oral, prénoms seuls (« A, Constance. B, … » faisait bégayer la voix) ; nombres écrits en lettres ; vérification Whisper à 90 % avec 4 essais ; ne jamais lancer Whisper ou un autre calcul lourd pendant un rendu (le moteur de voix monte à ~5 Go et se fait tuer) ; Whisper est libéré avant chaque nouvel essai ; `VOIX_GRAINE=<n>` pour changer de graine si un jour échoue toujours au même endroit.
- Commande : `python3 tiktok-kit/generateur/tiktok_video.py Le-Train-des-Neiges <jour> tiktok-videos/2026-12-<jj>_avent_jour<jj>.mp4 --avent` ; script de lot : relancer la boucle sur les jours manquants.

### Audience (TikTok Studio, 20/11)
90-93 % de femmes ; ~78 % de 18-34 ans (18-24 : 41-45 % ; 25-34 : 33-36 %) ; ~90 % en France. 100 % de non-abonnées, 89 % de nouvelles spectatrices : personne ne revient ni ne s'abonne.
Persona cible : femmes de 16 à 35 ans qui aiment le mystère, l'horreur douce et le paranormal. Voix : féminine, posée, conteuse, légèrement chuchotée.
Priorité : donner une raison de s'abonner → calendrier de l'Avent en direct du 1er au 24 décembre (une énigme du Train des Neiges par jour, « Jour X/24 », réponse de la veille au début de chaque vidéo). Énigmes 7 à 24 à reprendre du livre (PDF intérieur demandé à Aymeric le 20/11).
Ordre : nouvelle voix → calendrier de l'Avent dès le 1er décembre (avec le choix A/B/C si prêt) → reste de la liste.

## Liste d'attente (une idée par vague, dans cet ordre sauf décision contraire)
1. **Vague 6 (ajouté le 20/11)** : question en choix A/B/C (les 3 suspects affichés, « Tape A, B ou C ») ; commentaire épinglé par le compte ; ambiance un peu plus sombre (brume, bougies, légendes bretonnes), cohérente avec le persona.
2. Décembre : calendrier de l'Avent en direct (1 énigme du Train des Neiges par jour, du 1er au 24, « Jour X/24 », réponse de la veille en ouverture) — prioritaire, voir plus haut.
3. Réponse en vidéo le lendemain (début de la vidéo suivante : « Hier, c'était Jacques ! »), pour fidéliser (inclus dans le calendrier de l'Avent).
4. Série numérotée « L'enquête du jour n° X » avec Rose et Sardine comme fil rouge.
5. ~~Voix plus rapide ou autre voix~~ → priorité avant la vague 5 (test à l'aveugle).
6. ~~Vidéo plus courte (≤ 30 s)~~ → vague 3, non concluant.
7. ~~Accroche tournée vers le spectateur~~ → vague 4.
