# Arène — consignes de production quotidienne

Compte TikTok @arenemedia (nom affiché « Arène »). Format « Pour ou contre ? » : chaque jour, un sujet politique français qui divise, les faits sourcés, le meilleur argument de chaque camp, puis la question au public. Bio : « L'actu politique en 1 min ⚖️ / Les faits. Les deux camps. / POUR ou CONTRE ? 👇 ».

## Ligne éditoriale (non négociable)
- Neutralité : les deux camps ont le même temps d'écran, le même nombre d'arguments (3 chacun) et la même mise en forme. Aucun parti pris, aucun mot qui juge un camp. Chaque argument est formulé comme ses défenseurs le formuleraient.
- Tout est sourcé : chaque chiffre, vote, date et argument vient d'un article de presse ou d'une source officielle consultée le jour même (LCP, Public Sénat, AFP, Le Monde, Le Figaro, Les Échos, franceinfo, Assemblée, Sénat…). Au moins deux sources, idéalement de sensibilités différentes. En cas de doute sur un chiffre, on le retire.
- Arguments attribués à des groupes, partis ou institutions, jamais de citation inventée. Pas de citation mot pour mot de plus de quelques mots.
- Sujets exclus : faits divers, procès en cours visant une personne, drames humains (attentats, morts), rumeurs, sujets sans débat réel. On choisit des sujets de politique publique : budget, fiscalité, retraites, travail, logement, école, santé, sécurité, immigration (traitée sur les faits et les mesures, jamais sur des personnes), énergie, écologie, Europe, institutions.
- Sujet d'actualité (vote, annonce, rapport, proposition de loi des 7 derniers jours), différent des sujets déjà traités dans `journal.csv` sur les 30 derniers jours.

## Production
1. Cloner le dépôt sans télécharger les vieux fichiers :
   `git clone --depth 1 --filter=blob:none --no-checkout https://github.com/aymericgerard1502-boop/enigmes-images && cd enigmes-images && git sparse-checkout set --no-cone 'arene/*' && git checkout -q main`
2. Lire `arene/journal.csv`. Si une ligne existe déjà pour aujourd'hui, s'arrêter (rien à faire).
3. Chercher le sujet du jour (recherche web), lire au moins deux articles complets.
4. Écrire l'épisode `arene/episodes/AAAA-MM-JJ_slug.json` sur le modèle de `arene/episodes/ep001_abattement_retraites.json` :
   hook (4,5 s) → texte « CE QUI S'EST PASSÉ » (9 s) → compare OU vote (8-9 s, uniquement avec des chiffres vérifiés ; sinon un second écran texte) → camp POUR (12,5 s, 3 arguments) → camp CONTRE (12,5 s, 3 arguments) → texte « Rien n'est joué » ou « Et maintenant ? » (5,5 s) → cta (8 s). Durée totale ≥ 65 s (obligatoire pour la rémunération TikTok). `**mot**` = surlignage rouge, avec parcimonie, sur les faits et chiffres, et autant dans chaque camp. Phrases courtes (≤ 20 mots par argument). La ligne `source` cite les médias utilisés.
5. Générer : `python3 arene/generateur/video_arene.py <episode.json> arene/videos/AAAA-MM-JJ_slug.mp4` (environ 3 min ; nécessite PIL, numpy, scipy, ffmpeg et les polices Inter dans /usr/share/fonts/opentype/inter/ — installer `fonts-inter` si absentes).
6. Contrôle qualité : extraire une image toutes les 7 s (`ffmpeg -ss T -i video.mp4 -frames:v 1 ...`), les regarder toutes. Rien ne doit déborder, se chevaucher ou être coupé ; chaque chiffre doit correspondre aux sources. Corriger et régénérer si besoin. Vidéo < 90 Mo.
7. Publier le fichier dans le dépôt (commit + push sur main, auteur « Aymeric » <aymericgerard@icloud.com>), vérifier que l'URL `https://raw.githubusercontent.com/aymericgerard1502-boop/enigmes-images/main/arene/videos/<fichier>.mp4` répond 200.
8. Mode de publication — Metricool gratuit = 20 publications par mois :
   - compter dans `journal.csv` les lignes du mois en cours avec `mode=metricool`. S'il y en a moins de 20 → programmer dans Metricool (outil createScheduledPost, blogId 7485124, réseau tiktok, aujourd'hui 18:30 Europe/Paris, autoPublish true, tiktokData.title = la question du hook, privacyOption PUBLIC_TO_EVERYONE, isAigc false, media = l'URL raw GitHub).
   - sinon → mode `manuel` : envoyer la vidéo et sa légende à Aymeric (SendUserFile, status proactive, puis SendUserMessage avec la légende prête à copier) pour qu'il la publie à la main à 18h30.
9. Légende : question du hook + emoji 🗳️, une phrase de contexte factuelle, « Et toi : POUR ou CONTRE ? 👇 », puis 5-7 hashtags (#politique #debat #actualite + thème).
10. Ajouter la ligne au `journal.csv` (date;slug;sujet;mode;sources) et pousser.
11. Message final à Aymeric en une ou deux phrases : le sujet du jour, l'heure de publication, le mode. Si quelque chose a échoué, dire précisément quoi.
