"""Lot 5 (30 nov. -> 18 déc.) : 38 épingles v2, 2 par jour (13 h et 20 h), env. 70 % cadeau / 30 % énigmes."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from v2 import *

T, S, D = 'Le-Train-des-Neiges', 'Les-Santons-de-Minuit', 'Deux-enquetes-de-Noel'
BI, VT = 'Tempete-sur-Belle-Ile', 'Vendanges-tardives'
AMZ = {T: 'https://www.amazon.fr/dp/B0HNNJBKS7', S: 'https://www.amazon.fr/dp/B0HM13CCC4', D: 'https://www.amazon.fr/dp/B0HS845H1Z',
       BI: 'https://www.amazon.fr/dp/B0HLZTZPRP', VT: 'https://www.amazon.fr/dp/B0HMP5Y7WJ',
       'serie': 'https://www.amazon.fr/stores/author/B0HM88KRYF'}
B = {'enigmes': '1149895786049019780', 'cosy': '1149895786049019784', 'avent': '1149895786049019791',
     'noel': '1149895786049019793', 'bretagne': '1149895786049019795'}
VID = 'https://res.cloudinary.com/khtgpvta/video/upload/'
DUO_SUB = '2 livres-jeux d’enquête en 1 volume'
DUO_TXT = ("Deux enquêtes de Noël réunies en un seul livre : Les Santons de Minuit (40 énigmes dans un village provençal sous la neige) "
           "et Le Train des Neiges (24 énigmes en calendrier de l'Avent). 64 énigmes logiques pour démasquer le coupable, solutions détaillées.")

def P(day, hour, kind, scene=None, slug=None, **k):
    k.update(day=day, hour=hour, kind=kind, scene=scene, slug=slug); return k

PINS = [
 P('11-30', 13, 'hero', 'B3', T, stamp='avent', board='avent', kicker='DERNIER JOUR', title=["L'Avent commence", 'demain'], sub='24 énigmes, une par jour jusqu’à Noël',
   ptitle="Calendrier de l'Avent pour adultes : il commence demain", alt="Le Train des Neiges posé sur le parquet devant un sapin illuminé et des cadeaux.",
   text="L'Avent commence demain ! Le Train des Neiges est un calendrier de l'Avent d'enquête pour adultes : 24 énigmes logiques, une par jour jusqu'à Noël, à bord d'un train bloqué par la neige. Pas de chocolat, mais un coupable à démasquer la veille de Noël. Solutions incluses."),
 P('11-30', 20, 'hero', 'A4', D, stamp='2en1', board='noel', kicker='IDÉE CADEAU DE NOËL', title=['Idée cadeau', 'de Noël pour adultes'], sub=DUO_SUB,
   ptitle="Idée cadeau de Noël pour adultes : 2 livres-jeux d'enquête en 1", alt="Le livre Deux enquêtes de Noël posé sur une nappe blanche avec clémentines, figues et bougie.",
   text=DUO_TXT + " Une idée cadeau de Noël originale pour les adultes qui aiment les énigmes et les romans policiers."),
 P('12-01', 13, 'teaser', 'A3', T, num=1, board='enigmes', kicker='ÉNIGME DU 1ER DÉCEMBRE', title=['Qui a déchiré le billet ?'], sub='3 suspects, 4 indices : à vous de jouer',
   ptitle="Énigme du 1er décembre : qui a déchiré le billet ?", alt="Fiche de l'énigme du 1er décembre du Train des Neiges sur une nappe bordeaux avec loupe et thé.",
   text="Première énigme du calendrier de l'Avent ! Sur le quai, Rose ramasse un billet déchiré en deux : il était pour la voiture d'Augustin. Trois suspects, quatre indices : qui se trouvait au buffet de la gare ? Énigme logique gratuite du Train des Neiges, le calendrier de l'Avent d'enquête pour adultes."),
 P('12-01', 20, 'hero', 'B4', D, stamp='2en1', board='noel', kicker='IDÉE CADEAU', title=['Pour un fan', "d'énigmes"], sub='64 énigmes · 2 enquêtes de Noël',
   ptitle="Idée cadeau pour un fan d'énigmes : deux enquêtes de Noël", alt="Le livre Deux enquêtes de Noël sur une table basse avec loupes, vieux livres et tasse de thé, devant un sapin.",
   text=DUO_TXT + " Le cadeau idéal pour un fan d'énigmes, de casse-têtes logiques et de cosy mystery."),
 P('12-02', 13, 'video', slug=S, video='pins/video/santons_08_lettre', board='enigmes',
   ptitle="Énigme de Noël : qui a écrit la lettre au Père Noël ?",
   text="Une lettre glissée dans la boîte du Père Noël n'est pas d'un enfant : elle menace Fernand. Trois suspects, des indices, et une question : qui se trouvait près de la fontaine ? Votre suspect en commentaire ! Énigme extraite des Santons de Minuit, livre-jeu d'enquête de Noël pour adultes."),
 P('12-02', 20, 'series', 'A5', 'serie', board='noel', kicker='IDÉES CADEAUX DE NOËL', title=['Un cadeau pour chaque', "fan d'énigmes"], sub='Bretagne, Provence, Alsace, Noël…',
   ptitle="Idées cadeaux de Noël pour fans d'énigmes : 5 livres-jeux d'enquête", alt="Les cinq livres des Enquêtes de Rose Le Guen en éventail sur une table en bois avec papier cadeau et ruban rouge.",
   text="Un cadeau de Noël pour chaque amateur d'énigmes : Les Enquêtes de Rose Le Guen, cinq livres-jeux d'enquête pour adultes. Bretagne, Provence, Alsace, légendes d'Halloween ou calendrier de l'Avent : chaque livre est une enquête complète, avec des énigmes logiques à solution unique."),
 P('12-03', 13, 'hero', 'A', S, flip=True, board='noel', kicker='COSY MYSTERY DE NOËL', title=['Une enquête de Noël', 'en Provence'], sub='40 énigmes dans un village sous la neige',
   ptitle="Cosy mystery de Noël : une enquête en Provence, 40 énigmes", alt="Le livre Les Santons de Minuit posé sur un plaid écossais rouge avec bougies et oranges séchées.",
   text="Un cosy mystery de Noël à résoudre soi-même : Les Santons de Minuit, 40 énigmes logiques dans un village provençal sous la neige, entre crèche, marché de Noël et santons. Livre-jeu d'enquête pour adultes, solutions incluses. Une idée cadeau de Noël pour les amateurs de romans policiers."),
 P('12-03', 20, 'hero', 'B2', D, stamp='2en1', board='noel', kicker='IDÉE CADEAU DE NOËL', title=['Cadeau pour un', 'fan de polars'], sub='2 enquêtes de Noël à résoudre soi-même',
   ptitle="Cadeau pour un fan de polars : deux enquêtes de Noël à résoudre", alt="Le livre Deux enquêtes de Noël posé sur une table près d'une fenêtre enneigée, avec lanterne et chocolat chaud.",
   text="Un cadeau pour un amateur de romans policiers qui préfère mener l'enquête lui-même. " + DUO_TXT),
 P('12-04', 13, 'teaser', 'A2', S, num=1, board='enigmes', kicker='ÉNIGME DE NOËL · PROVENCE', title=['Qui a décapité le santon ?'], sub='3 suspects, 4 indices : à vous de jouer',
   ptitle="Énigme de Noël : qui a décapité le santon ?", alt="Fiche de l'énigme du santon décapité, extraite des Santons de Minuit, sur un plaid écossais vert.",
   text="Sur le stand de Fernand, un santon de berger a perdu la tête, cassé exprès d'un coup sec. Trois suspects, quatre indices : qui se trouvait sur le parvis ? Énigme logique gratuite extraite des Santons de Minuit, livre-jeu d'enquête de Noël pour adultes."),
 P('12-04', 20, 'hero', 'B', T, board='avent', kicker="CALENDRIER DE L'AVENT ADULTE", title=['Pas trop tard', "pour l'Avent"], sub='Rattrapez les premières énigmes en une soirée',
   ptitle="Calendrier de l'Avent pour adultes : il n'est pas trop tard", alt="Le Train des Neiges posé sur une table en bois devant un sapin illuminé et une cheminée.",
   text="Vous avez raté le 1er décembre ? Pas de panique : avec Le Train des Neiges, les premières énigmes se rattrapent en une soirée, puis on suit le rythme d'une énigme par jour jusqu'à Noël. 24 énigmes logiques, une enquête complète et des solutions détaillées."),
 P('12-05', 13, 'hero', 'A3', D, stamp='2en1', board='noel', kicker='PÈRE NOËL SECRET', title=['Une idée cadeau', 'à moins de 20 €'], sub='64 énigmes logiques à résoudre',
   ptitle="Idée cadeau Père Noël secret à moins de 20 € : un livre-jeu d'enquête", alt="Le livre Deux enquêtes de Noël sur une nappe bordeaux avec loupe, lunettes et paquet cadeau.",
   text="Une idée pour le Père Noël secret du bureau ou de la famille, à moins de 20 € : Deux enquêtes de Noël, un livre-jeu d'enquête pour adultes. " + DUO_TXT),
 P('12-05', 20, 'teaser', 'B4', T, num=4, board='enigmes', kicker='ÉNIGME DU 4 DÉCEMBRE', title=['Qui a pris le sifflet ?'], sub='3 suspects, 4 indices : à vous de jouer',
   ptitle="Énigme du 4 décembre : qui a pris le sifflet du contrôleur ?", alt="Fiche de l'énigme du 4 décembre du Train des Neiges devant une table basse avec loupes et sapin illuminé.",
   text="Le sifflet du contrôleur a disparu et le train part avec cinq minutes de retard, une première en quarante ans. Trois suspects, quatre indices : qui se trouvait dans le compartiment 7 ? Énigme logique gratuite du Train des Neiges, calendrier de l'Avent d'enquête pour adultes."),
 P('12-06', 13, 'hero', 'A4', S, board='noel', kicker='IDÉE CADEAU DE NOËL', title=['Idée cadeau', 'pour mamie'], sub='Une enquête de Noël en Provence',
   ptitle="Idée cadeau de Noël pour mamie : une enquête en Provence", alt="Le livre Les Santons de Minuit posé sur une nappe blanche avec clémentines, figues et bougie.",
   text="Une idée cadeau de Noël pour une grand-mère qui aime les énigmes et les romans policiers : Les Santons de Minuit, 40 énigmes logiques dans un village provençal sous la neige. Grand format, pages aérées, solutions détaillées."),
 P('12-06', 20, 'video', slug=T, video='pins/video/train_03_houx', board='enigmes',
   ptitle="Énigme du Train des Neiges : qui a arraché le bouquet de houx ?",
   text="Le bouquet de houx de la voiture-salon a été arraché et jeté par la fenêtre, avant même le départ. Qui se trouvait dans la voiture-salon ? Votre suspect en commentaire ! Une énigme du Train des Neiges, le calendrier de l'Avent d'enquête pour adultes."),
 P('12-07', 13, 'hero', 'B3', D, stamp='2en1', board='noel', kicker='IDÉE CADEAU DE NOËL', title=['À glisser', 'sous le sapin'], sub=DUO_SUB,
   ptitle="À glisser sous le sapin : deux enquêtes de Noël en un livre", alt="Le livre Deux enquêtes de Noël posé sur le parquet devant un sapin illuminé et des cadeaux.",
   text="Une idée cadeau à glisser sous le sapin pour les amateurs d'énigmes. " + DUO_TXT),
 P('12-07', 20, 'series', 'A3', 'serie', board='noel', kicker='IDÉES CADEAUX', title=['Cadeaux pour', 'lecteurs de polars'], sub='Une région, une saison, un coupable',
   ptitle="Idées cadeaux pour lecteurs de polars : 5 livres-jeux d'enquête", alt="Les cinq livres des Enquêtes de Rose Le Guen en éventail sur une nappe bordeaux avec loupe et lunettes.",
   text="Des idées cadeaux pour les lecteurs de romans policiers : Les Enquêtes de Rose Le Guen, des livres-jeux d'enquête où l'on démasque soi-même le coupable grâce à des énigmes logiques. Une région, une saison, un coupable : chaque livre se lit indépendamment."),
 P('12-08', 13, 'teaser', 'A', S, num=4, board='enigmes', kicker='ÉNIGME DE NOËL · PROVENCE', title=['Qui a volé les marrons ?'], sub='3 suspects, 4 indices : à vous de jouer',
   ptitle="Énigme de Noël : qui a volé les marrons chauds ?", alt="Fiche de l'énigme des marrons envolés, extraite des Santons de Minuit, sur un plaid écossais rouge.",
   text="Un cornet de marrons chauds a disparu du brasero du marché de Noël. Trois suspects, quatre indices : qui se trouvait à la boulangerie ? Énigme logique gratuite extraite des Santons de Minuit, livre-jeu d'enquête de Noël pour adultes."),
 P('12-08', 20, 'hero', 'B4', T, board='avent', kicker="CALENDRIER DE L'AVENT", title=["Jeu d'enquête", 'à faire en famille'], sub='Une énigme chaque soir jusqu’à Noël',
   ptitle="Jeu d'enquête à faire en famille : un calendrier de l'Avent d'énigmes", alt="Le Train des Neiges posé sur une table basse avec loupes et tasse de thé, devant un sapin illuminé.",
   text="Un jeu d'enquête à faire en famille chaque soir de décembre : Le Train des Neiges propose 24 énigmes logiques, une par jour jusqu'à Noël, pour démasquer ensemble le coupable. Dès 12 ans, solutions incluses."),
 P('12-09', 13, 'hero', 'A2', D, stamp='2en1', board='noel', kicker="LIVRE-JEU D'ENQUÊTE", title=['Cadeau de Noël', 'original pour adulte'], sub='64 énigmes · solutions incluses',
   ptitle="Cadeau de Noël original pour adulte : un livre-jeu d'enquête", alt="Le livre Deux enquêtes de Noël sur un plaid écossais vert avec pain d'épices et vin chaud.",
   text="Un cadeau de Noël original pour un adulte : un livre-jeu d'enquête plutôt qu'un roman. " + DUO_TXT),
 P('12-09', 20, 'teaser', 'B2', S, num=5, board='enigmes', kicker='ÉNIGME DE NOËL · PROVENCE', title=["Qui a arraché", "l'affiche ?"], sub='3 suspects, 3 indices : à vous de jouer',
   ptitle="Énigme de Noël : qui a arraché l'affiche de la mairie ?", alt="Fiche de l'énigme de l'affiche arrachée, extraite des Santons de Minuit, devant une fenêtre enneigée.",
   text="L'affiche annonçant la révélation de Fernand, le soir de Noël, a été arrachée du panneau de la mairie. Trois suspects, trois indices : qui se trouvait sous la halle ? Énigme logique gratuite extraite des Santons de Minuit."),
 P('12-10', 13, 'hero', 'B', S, board='cosy', kicker="LIVRE-JEU D'ENQUÊTE", title=['Un cosy mystery', 'de Noël'], sub='40 énigmes en Provence enneigée',
   ptitle="Un cosy mystery de Noël à résoudre : Les Santons de Minuit", alt="Le livre Les Santons de Minuit posé sur une table en bois devant un sapin et une cheminée.",
   text="Un cosy mystery de Noël dont vous êtes l'enquêteur : Les Santons de Minuit réunit 40 énigmes logiques dans un village provençal sous la neige. Plans, indices, grilles et solutions détaillées. Parfait pour les soirées d'hiver au coin du feu."),
 P('12-10', 20, 'series', 'A2', 'serie', board='noel', kicker='IDÉE CADEAU', title=['Le cadeau idéal', 'pour un détective'], sub='Les Enquêtes de Rose Le Guen',
   ptitle="Le cadeau idéal pour un détective amateur : 5 livres-jeux d'enquête", alt="Les cinq livres des Enquêtes de Rose Le Guen en éventail sur un plaid écossais vert.",
   text="Le cadeau idéal pour un détective amateur : Les Enquêtes de Rose Le Guen, cinq livres-jeux d'enquête avec des énigmes logiques à solution unique. Belle-Île, Provence, Alsace, Bretagne des légendes et calendrier de l'Avent."),
 P('12-11', 13, 'video', slug=S, video='pins/video/santons_06_chant', board='enigmes',
   ptitle="Énigme de Noël : qui a coupé la musique pendant la chorale ?",
   text="Pendant la répétition des chants de Noël sur le parvis, quelqu'un a coupé la sono. Qui se trouvait sous la halle ? Votre suspect en commentaire ! Énigme extraite des Santons de Minuit, livre-jeu d'enquête de Noël pour adultes."),
 P('12-11', 20, 'hero', 'A4', D, stamp='2en1', board='noel', kicker='NOUVEAU', title=['Deux enquêtes', 'de Noël'], sub='Les Santons de Minuit + Le Train des Neiges',
   ptitle="Deux enquêtes de Noël : Les Santons de Minuit + Le Train des Neiges", alt="Le livre Deux enquêtes de Noël posé sur une nappe blanche avec clémentines et bougie.",
   text=DUO_TXT + " Nouveau : les deux livres-jeux de Noël des Enquêtes de Rose Le Guen réunis en un volume."),
 P('12-12', 13, 'teaser', 'A5', BI, num=6, board='bretagne', kicker='ÉNIGME · BELLE-ÎLE', title=['Qui a fait taire', 'le piano ?'], sub='3 suspects, 4 indices : à vous de jouer',
   ptitle="Énigme logique : qui a fait taire le piano ?", alt="Fiche de l'énigme du piano muet, extraite de Tempête sur Belle-Île, sur une table en bois avec papier cadeau.",
   text="Une corde du vieux piano de l'hôtel a été desserrée. Quelqu'un voulait-il éviter qu'on joue, ou couvrir un bruit ? Trois suspects, quatre indices : qui se trouvait à la réception ? Énigme gratuite extraite de Tempête sur Belle-Île, livre-jeu d'enquête en Bretagne."),
 P('12-12', 20, 'hero', 'B3', T, board='avent', kicker="IL N'EST PAS TROP TARD", title=["Calendrier de l'Avent", 'pour adultes'], sub='Commencez ce soir, finissez à Noël',
   ptitle="Calendrier de l'Avent pour adultes : commencez ce soir", alt="Le Train des Neiges posé sur le parquet devant un sapin illuminé et des cadeaux.",
   text="Il n'est pas trop tard pour le calendrier de l'Avent ! Le Train des Neiges se rattrape en quelques soirées : 24 énigmes logiques, une enquête complète à bord d'un train bloqué par la neige, et le coupable démasqué la veille de Noël."),
 P('12-13', 13, 'hero', 'A', D, stamp='2en1', board='noel', kicker='IDÉE CADEAU DE NOËL', title=['Pour un ado', 'curieux'], sub='64 énigmes logiques, dès 12 ans',
   ptitle="Idée cadeau de Noël pour un ado curieux : 64 énigmes logiques", alt="Le livre Deux enquêtes de Noël posé sur un plaid écossais rouge avec bougies et chocolat chaud.",
   text="Une idée cadeau de Noël pour un ado curieux, dès 12 ans, ou pour toute la famille : " + DUO_TXT),
 P('12-13', 20, 'teaser', 'B4', S, num=7, board='enigmes', kicker='ÉNIGME DE NOËL · PROVENCE', title=['Qui a renversé', 'le panier ?'], sub='3 suspects, 5 indices : à vous de jouer',
   ptitle="Énigme de Noël : qui a renversé le panier de fougasses ?", alt="Fiche de l'énigme du panier renversé, extraite des Santons de Minuit, devant une table basse et un sapin.",
   text="Un panier de fougasses a fini dans la fontaine, et la boulangère jure qu'on l'a poussé. Trois suspects, cinq indices : qui se trouvait devant la mairie ? Énigme logique gratuite extraite des Santons de Minuit."),
 P('12-14', 13, 'series', 'A', 'serie', board='noel', kicker='IDÉES CADEAUX DE NOËL', title=['5 idées cadeaux', "pour fans d'énigmes"], sub='Une enquête complète dans chaque livre',
   ptitle="5 idées cadeaux de Noël pour fans d'énigmes", alt="Les cinq livres des Enquêtes de Rose Le Guen en éventail sur un plaid écossais rouge.",
   text="5 idées cadeaux de Noël pour les fans d'énigmes : Tempête sur Belle-Île, Les Santons de Minuit, Vendanges tardives, La Nuit de l'Ankou et Le Train des Neiges. Des livres-jeux d'enquête pour adultes, une enquête complète dans chaque livre."),
 P('12-14', 20, 'hero', 'B2', S, board='noel', kicker='IDÉE CADEAU DE NOËL', title=['Une enquête', 'au pays des santons'], sub='40 énigmes logiques, solutions incluses',
   ptitle="Idée cadeau de Noël : une enquête au pays des santons", alt="Le livre Les Santons de Minuit posé sur une table près d'une fenêtre enneigée.",
   text="Une enquête au pays des santons : 40 énigmes logiques dans un village provençal sous la neige, entre crèche, marché de Noël et suspects. Les Santons de Minuit, livre-jeu d'enquête de Noël pour adultes."),
 P('12-15', 13, 'teaser', 'A3', VT, num=5, board='enigmes', kicker='ÉNIGME · ALSACE', title=["Qui a dérangé", 'les cigognes ?'], sub='3 suspects, 3 indices : à vous de jouer',
   ptitle="Énigme logique : qui a dérangé les cigognes ?", alt="Fiche de l'énigme des cigognes dérangées, extraite de Vendanges tardives, sur une nappe bordeaux.",
   text="Quelqu'un a grimpé près du nid des cigognes, sur le toit de la cabane, et une échelle a été mal rangée. Trois suspects, trois indices : qui se trouvait au belvédère ? Énigme gratuite extraite de Vendanges tardives, livre-jeu d'enquête en Alsace."),
 P('12-15', 20, 'hero', 'B4', D, stamp='2en1', board='noel', kicker='IDÉE CADEAU', title=["Une soirée d'enquête", 'au coin du feu'], sub='2 livres-jeux en 1 · 64 énigmes',
   ptitle="Une soirée d'enquête au coin du feu : deux enquêtes de Noël", alt="Le livre Deux enquêtes de Noël sur une table basse avec loupes et tasse de thé.",
   text="Offrez des soirées d'enquête au coin du feu. " + DUO_TXT),
 P('12-16', 13, 'hero', 'A5', D, stamp='2en1', board='noel', kicker='CADEAU DE DERNIÈRE MINUTE', title=['À commander', 'pour Noël'], sub='2 enquêtes de Noël en un livre',
   ptitle="Cadeau de dernière minute pour Noël : un livre-jeu d'enquête", alt="Le livre Deux enquêtes de Noël sur une table en bois avec papier kraft et ruban rouge.",
   text="Un cadeau de dernière minute pour Noël ? " + DUO_TXT + " Pensez à commander rapidement pour une livraison avant Noël."),
 P('12-16', 20, 'teaser', 'B', BI, num=1, board='bretagne', kicker='ÉNIGME · BELLE-ÎLE', title=['Qui a fouillé', 'la valise ?'], sub='3 suspects, 4 indices : à vous de jouer',
   ptitle="Énigme logique : qui a fouillé la valise de Rose ?", alt="Fiche de l'énigme de la valise ouverte, extraite de Tempête sur Belle-Île, devant un sapin et une cheminée.",
   text="À peine arrivée à l'hôtel, Rose trouve sa valise entrouverte et son carnet feuilleté. Trois suspects, quatre indices : qui se trouvait dans la véranda ? Première énigme de Tempête sur Belle-Île, livre-jeu d'enquête en Bretagne."),
 P('12-17', 13, 'hero', 'A4', S, board='cosy', kicker="LIVRE-JEU D'ENQUÊTE", title=["Livre d'énigmes", 'pour adultes'], sub='Une enquête de Noël en Provence',
   ptitle="Livre d'énigmes pour adultes : une enquête de Noël en Provence", alt="Le livre Les Santons de Minuit posé sur une nappe blanche avec clémentines, figues et bougie.",
   text="Un livre d'énigmes pour adultes, à résoudre au chaud pendant les fêtes : Les Santons de Minuit, 40 énigmes logiques et une enquête de Noël dans un village provençal. Solutions détaillées."),
 P('12-17', 20, 'hero', 'B3', D, stamp='2en1', board='noel', kicker='IDÉE CADEAU DE NOËL', title=['Le cadeau de', 'dernière minute'], sub=DUO_SUB,
   ptitle="Le cadeau de Noël de dernière minute pour fans d'énigmes", alt="Le livre Deux enquêtes de Noël sur le parquet devant un sapin et des cadeaux.",
   text="Le cadeau de dernière minute pour les fans d'énigmes. " + DUO_TXT + " Commandez vite pour le recevoir avant Noël."),
 P('12-18', 13, 'series', 'A5', 'serie', board='noel', kicker='IDÉES CADEAUX DE NOËL', title=['Encore un cadeau', 'à trouver ?'], sub='5 enquêtes à résoudre soi-même',
   ptitle="Encore un cadeau à trouver ? 5 livres-jeux d'enquête", alt="Les cinq livres des Enquêtes de Rose Le Guen en éventail sur une table en bois avec papier cadeau.",
   text="Encore un cadeau de Noël à trouver ? Les Enquêtes de Rose Le Guen : cinq livres-jeux d'enquête pour adultes, avec des énigmes logiques et une enquête complète dans chaque livre."),
 P('12-18', 20, 'hero', 'B4', D, stamp='2en1', board='noel', kicker='NOËL APPROCHE', title=['Dernier jour', 'pour commander'], sub='Deux enquêtes de Noël en un livre',
   ptitle="Dernier jour pour commander : deux enquêtes de Noël", alt="Le livre Deux enquêtes de Noël sur une table basse avec loupes, devant un sapin.",
   text="Noël approche : dernier moment pour commander un cadeau livré à temps. " + DUO_TXT),
]

STAMPS = {'avent': stamp_avent, '2en1': stamp_2en1}

def build_url(p, i):
    if p['kind'] == 'video':
        return VID + p['video'] + '.mp4'
    pub = SCENES[p['scene']]['public']; pre = 'a_hflip/' if p.get('flip') else ''
    return (f"https://res.cloudinary.com/khtgpvta/image/upload/{pre}c_fill,ar_2:3,w_1000,h_1500/"
            f"l_pins:lot5:ov_{i:02d}/fl_layer_apply,g_north_west,x_0,y_0/q_90/{pub}.jpg")

if __name__ == '__main__':
    out = os.path.join(ROOT, '..', 'v2', 'lot5'); os.makedirs(out, exist_ok=True)
    prev = '/tmp/claude-0/-home-claude/e6385d71-496a-5de3-8d66-6851e69871dd/scratchpad/lot5'; os.makedirs(prev, exist_ok=True)
    rows = []
    for i, p in enumerate(PINS, 1):
        p = dict(p); p['n'] = i
        p['dueAt'] = f"2026-{p['day']}T{p['hour']:02d}:00:00+01:00"
        p['link'] = AMZ[p['slug']]
        p['boardServiceId'] = B[p['board']]
        if p['kind'] != 'video':
            if p['kind'] == 'hero':
                ov = hero(p['scene'], p['slug'], p['kicker'], p['title'], p['sub'],
                          stamp=STAMPS[p['stamp']]() if p.get('stamp') else None, flip=p.get('flip', False))
            elif p['kind'] == 'teaser':
                ov = teaser(p['scene'], p['slug'], p['num'], p['kicker'], p['title'], p['sub'])
            else:
                ov = series(p['scene'], p['kicker'], p['title'], p['sub'])
            ov.save(os.path.join(out, f'ov_{i:02d}.png'))
            bg = Image.open(os.path.join(ROOT, '..', 'v2', 'bg', p['scene'] + '.jpg')).convert('RGBA').resize((W, H))
            if p.get('flip'): bg = bg.transpose(Image.FLIP_LEFT_RIGHT)
            bg.alpha_composite(ov); bg.convert('RGB').resize((400, 600)).save(os.path.join(prev, f'{i:02d}.jpg'), quality=82)
        p['media'] = build_url(p, i)
        rows.append(p)
    json.dump(rows, open(os.path.join(out, 'pins.json'), 'w'), ensure_ascii=False, indent=1)
    print(len(rows), 'pins')
