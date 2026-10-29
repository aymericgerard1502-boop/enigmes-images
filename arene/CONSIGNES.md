# Arène — consignes de production quotidienne

Compte TikTok @arenemedia (nom affiché « Arène »). **Format « Si ça passe »** (depuis le 28/10/2026) : chaque jour, une mesure ou une proposition politique d'actualité traduite en effets concrets « pour toi » (en euros, pour un profil type : étudiant, salarié au Smic, retraité, famille…), racontée en voix off par l'arbitre, avec sous-titres mot à mot et cartes animées. Fin : POUR ou CONTRE ? Bio : « L'actu politique en 1 min ⚖️ / Les faits. Les deux camps. / POUR ou CONTRE ? 👇 ».
L'ancien format (`video_arene.py`, dossier `episodes/`) n'est plus utilisé.

## Ligne éditoriale (non négociable)
- Neutralité : un argument POUR et un argument CONTRE, de même longueur et même mise en forme (cartes `camp`), attribués à des groupes ou institutions. Aucun parti pris, aucun mot qui juge un camp. Chaque argument est formulé comme ses défenseurs le formuleraient.
- Tout est sourcé : chaque chiffre, vote, date et argument vient d'un article de presse ou d'une source officielle consultée le jour même (LCP, Public Sénat, AFP, Le Monde, Le Figaro, Les Échos, franceinfo, Assemblée, Sénat…). Au moins deux sources, idéalement de sensibilités différentes. En cas de doute sur un chiffre, on le retire.
- Arguments attribués à des groupes, partis ou institutions, jamais de citation inventée. Pas de citation mot pour mot de plus de quelques mots.
- Sujets exclus : faits divers, procès en cours visant une personne, drames humains (attentats, morts), rumeurs, sujets sans débat réel. On choisit des sujets de politique publique : budget, fiscalité, retraites, travail, logement, école, santé, sécurité, immigration (traitée sur les faits et les mesures, jamais sur des personnes), énergie, écologie, Europe, institutions.
- Sujet d'actualité (vote, annonce, rapport, proposition de loi des 7 derniers jours), différent des sujets déjà traités dans `journal.csv` sur les 30 derniers jours.

- Calculs « pour toi » : uniquement à partir de chiffres publiés (barèmes, montants, taux officiels ou simulations de presse citées). Toujours préciser l'hypothèse à l'écran (ex. « avec un gel total », « pour une retraite de base de 1 500 € »). Jamais de calcul inventé ; si le mécanisme n'est pas encore fixé, le dire.
- Série « Si [candidat] est élu » : seulement si tous les grands candidats peuvent être traités sur le même modèle, à partir de leurs mesures annoncées. Pas de photo de personnalité (droits) : nom en grand.

## Production
1. Cloner le dépôt sans télécharger les vieux fichiers :
   `git clone --depth 1 --filter=blob:none --no-checkout https://github.com/aymericgerard1502-boop/enigmes-images && cd enigmes-images && git sparse-checkout set --no-cone 'arene/generateur/*' 'arene/episodes-si/*' 'arene/*.md' 'arene/*.csv' 'arene/.gitignore' && git checkout -q main`
2. Lire `arene/journal.csv`. Si une ligne existe déjà pour aujourd'hui, s'arrêter (rien à faire).
3. Installer la voix : `pip install --break-system-packages piper-tts scipy`, puis télécharger le modèle dans `arene/voix/` (ignoré par git) :
   `mkdir -p arene/voix && for e in onnx onnx.json; do curl -sL -o arene/voix/fr_FR-tom-medium.$e https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/tom/medium/fr_FR-tom-medium.$e; done`
   (le domaine huggingface.co et *.hf.co doivent être autorisés ; si le téléchargement échoue, ne rien publier et le signaler à Aymeric).
4. Chercher le sujet du jour (recherche web), lire au moins deux articles complets. Vérifier où en est le texte (commission, séance, Sénat, rejet…) au jour même : l'actualité parlementaire change vite.
5. Écrire l'épisode `arene/episodes-si/AAAA-MM-JJ_slug.json` sur le modèle de `arene/episodes-si/prototype_gel-retraites.json` : phrases courtes (≤ 20 mots).
   - `dit` = texte prononcé : nombres sans espace (« 1260 euros », « 31 euros 50 »), pas d'abréviations ni de symboles.
   - `affiche` = sous-titre : typographie normale (« 1 260 € »), `**mot**` en rouge sur les faits clés, avec parcimonie.
   - `carte` = nouvelle carte à l'écran (types : titre, seuil, calcul, compteur, cumul, checks, camp, tampon, cta) ; les temps d'apparition (`at`) sont en secondes depuis le début de la carte.
   - `geste` de l'arbitre : siffle (ouverture), pointe, carton (chiffre choc), deux (fin).
   - Structure : accroche « Si … passe, voilà ce que [toi / ta grand-mère / ton loyer…] » → la règle → le calcul pour un profil → le chiffre choc → ce qui ne change pas → POUR → CONTRE → où en est le texte → « Alors, pour ou contre ? Ton camp en commentaire. »
   - **Amélioration continue** : lire `arene/AMELIORATIONS.md` avant d'écrire. Appliquer UNIQUEMENT le changement de la vague en cours, en plus des réglages déjà validés. Ne jamais tester une idée de la liste d'attente avant son tour : un seul changement à la fois, sinon on ne sait pas ce qui a marché.
6. Générer : `python3 arene/generateur/video_si.py arene/episodes-si/<fichier>.json arene/videos/AAAA-MM-JJ_slug.mp4 arene/voix` (environ 5 min ; PIL, numpy, scipy, ffmpeg, polices Inter dans /usr/share/fonts/opentype/inter/).
7. Contrôle qualité : la toute première image (t = 0) doit montrer la question d'accroche entière (miniature TikTok). Puis une image toutes les 4 s : rien ne déborde, ne se chevauche ou n'est coupé, chaque chiffre affiché correspond aux sources et au texte prononcé. Corriger et régénérer si besoin. Vidéo < 90 Mo.
8. Publier le fichier dans le dépôt (commit + push sur main, auteur « Aymeric » <aymericgerard@icloud.com>), vérifier que `https://raw.githubusercontent.com/aymericgerard1502-boop/enigmes-images/main/arene/videos/<fichier>.mp4` répond 200.
9. Heure de publication : **aléatoire chaque jour**, pour éviter un rythme mécanique. La tirer au hasard avec `python3 -c "import random; m=random.randint(12*60+5, 21*60+25); print(f'{m//60:02d}:{m%60:02d}')"`, au moins 45 minutes après l'heure actuelle (sinon retirer). La noter dans le journal.
   Mode de publication — Metricool gratuit = 20 publications par mois :
   - compter dans `journal.csv` les lignes du mois en cours avec `mode=metricool`. Moins de 20 → programmer dans Metricool (createScheduledPost, blogId 7485124, réseau tiktok, aujourd'hui à l'heure tirée ci-dessous, Europe/Paris, autoPublish true, tiktokData.title = la question d'accroche, privacyOption PUBLIC_TO_EVERYONE, isAigc true car la voix est synthétique, media = l'URL raw GitHub).
   - sinon → mode `manuel` : envoyer la vidéo et sa légende à Aymeric (SendUserFile status proactive, puis SendUserMessage avec la légende prête à copier) pour qu'il la publie à la main vers l'heure tirée en cochant « contenu généré par IA ».
10. Légende : la question d'accroche + 🗳️, une phrase de contexte factuelle, « Et toi : POUR ou CONTRE ? 👇 », puis 5-7 hashtags (#politique #debat #actualite + thème).
11. Ajouter la ligne au `journal.csv` (date;slug;sujet;mode;sources) et pousser.
12. Bilan de vague : si la veille était le dernier jour d'une vague (voir `AMELIORATIONS.md`), récupérer dans Metricool (getAnalyticsDataByMetrics, brandId 7485124, TKPO02/TKPO07/TKPO08/TKPO09/TKPO10) les vues, likes, commentaires et partages de chaque vidéo de la vague, les comparer à la vague précédente, et envoyer ce bilan à Aymeric en lui demandant pour 2 ou 3 vidéos le temps de visionnage moyen, le % de visionnage complet et les nouveaux abonnés (TikTok Studio). Ne pas lancer la vague suivante sans sa décision : continuer la vague en cours en attendant.
13. Message final à Aymeric en une ou deux phrases : le sujet du jour, l'heure de publication tirée, le mode. Si quelque chose a échoué, dire précisément quoi.
