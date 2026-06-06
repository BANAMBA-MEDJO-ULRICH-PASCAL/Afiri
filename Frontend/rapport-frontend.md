# Rapport Front-end - Afiri

## Présentation du produit et de ses fonctionnalités

Afiri est une application web orientée carrière, destinée principalement aux étudiants et aux jeunes profils en début de parcours professionnel. Son objectif est de faciliter la transition entre les études et le monde du travail en proposant un espace simple pour découvrir des opportunités, valoriser son profil et obtenir des recommandations adaptées.

Le produit se présente sous deux formes complémentaires : une page d'accueil publique qui explique la valeur de la plateforme, et une interface applicative mobile-first qui regroupe les fonctionnalités principales. L'application met l'accent sur les stages, alternances, jobs étudiants et premières expériences professionnelles, avec une approche adaptée au contexte local africain.

### Fonctionnalités principales

La page d'accueil présente Afiri comme une plateforme carrière dédiée aux étudiants. Elle met en avant les bénéfices du service, les étapes d'utilisation, les types de fonctionnalités proposées et un appel à l'action vers la création de compte ou l'exploration des offres.

La page d'authentification permet à l'utilisateur de se connecter ou de s'inscrire. Elle contient aussi un parcours de récupération de mot de passe avec saisie d'e-mail, code de confirmation, nouveau mot de passe et état de succès. L'inscription distingue deux rôles possibles : étudiant et entreprise.

L'écran d'accueil de l'application affiche un résumé du profil de l'utilisateur, un indicateur de complétion et une liste d'offres recommandées. Chaque offre contient un intitulé, une entreprise, une localisation, une durée et un bouton de candidature.

La page des offres regroupe les opportunités disponibles. Elle propose une barre de recherche et des filtres par type d'offre, comme stage, remote, plein temps ou temps partiel. Les offres sont présentées sous forme de cartes lisibles, avec un accès rapide au détail.

La page de détail d'une offre affiche les informations principales d'une opportunité : titre, entreprise, localisation, durée, date limite, description, compatibilité avec le profil et conseil personnalisé pour postuler. Elle propose également un bouton de candidature.

La page profil fonctionne comme un mini-CV étudiant. Elle montre l'identité de l'utilisateur, sa formation, le niveau de complétion du profil, ses compétences, son expérience et des actions liées au CV ou au partage du profil.

La partie quiz/orientation existe sous deux formes. La page `quizz.html` affiche une page en construction, tandis que `questionnaire.html` contient un questionnaire interactif fonctionnel. Ce questionnaire évalue les préférences et le niveau de l'utilisateur, puis propose un résultat avec des types d'offres recommandées.

## Captures d'écran des pages

### Page d'accueil publique

![Page d'accueil publique](captures/01-landing.png)

### Authentification

![Page d'authentification](captures/02-authentification.png)

### Accueil de l'application

![Accueil de l'application](captures/03-accueil.png)

### Liste des offres

![Liste des offres](captures/04-offres.png)

### Détail d'une offre

![Détail d'une offre](captures/05-detail-offre.png)

### Profil utilisateur

![Profil utilisateur](captures/06-profil.png)

### Page quiz en construction

![Page quiz en construction](captures/07-quiz-construction.png)

### Questionnaire d'orientation

![Questionnaire d'orientation](captures/08-questionnaire.png)

## Interface utilisateur et expérience

L'interface d'Afiri adopte une approche mobile-first. Les pages de l'application sont contenues dans un format proche d'un écran de smartphone, avec une largeur maximale de 430 pixels. Ce choix est cohérent avec la cible étudiante, car l'utilisation mobile est souvent prioritaire pour consulter des offres, compléter un profil ou postuler rapidement.

L'expérience utilisateur repose sur une navigation simple et constante. Les pages principales de l'application utilisent une barre de navigation inférieure donnant accès à l'accueil, aux offres, au quiz et au profil. Ce modèle facilite l'accès aux sections essentielles sans surcharger l'écran.

Le design visuel utilise des couleurs chaudes et identifiables : orange pour les actions principales, bordeaux pour les titres et éléments importants, jaune et vert pour les accents visuels et les indicateurs positifs. Cette palette donne une identité jeune, dynamique et professionnelle à la plateforme.

Les contenus sont organisés sous forme de cartes. Ce choix améliore la lisibilité, surtout sur mobile, car chaque information est regroupée dans un bloc clair : offre, compétence, détail, conseil ou action. Les espaces, les arrondis et les ombres légères créent une interface moderne sans rendre l'expérience trop complexe.

L'application utilise plusieurs éléments interactifs pour guider l'utilisateur : filtres d'offres, recherche, boutons de candidature, transitions entre pages, états actifs dans la navigation, changement d'état du bouton après candidature et progression dans le questionnaire. Ces éléments rendent le prototype plus vivant et donnent une impression d'application complète.

L'authentification bénéficie d'une interface animée avec changement de vues dans une même carte. Cela permet de passer de la connexion à l'inscription ou à la récupération de mot de passe sans rupture visuelle forte. Le questionnaire utilise aussi une progression claire avec pourcentage, barre de progression, boutons de retour/continuer et résultat final.

## Choix technologiques Front-end

Le front-end est développé avec HTML, CSS et JavaScript natif. Ce choix permet de créer un prototype léger, facilement exécutable dans un navigateur, sans dépendre d'un framework ou d'une étape de compilation. Pour un projet de démonstration ou une maquette fonctionnelle, cette approche est efficace car elle réduit la complexité technique et facilite la compréhension du code.

HTML est utilisé pour structurer les pages, les formulaires, les cartes d'offres, la navigation et les sections de contenu. Chaque page correspond à un écran distinct, ce qui rend l'architecture simple à comprendre : `index.html` pour la landing page, `signup.html` pour l'authentification, `app.html` pour l'accueil, `offres.html` pour la liste des offres, `detail-offre.html` pour le détail, `profil.html` pour le mini-CV et `questionnaire.html` pour le quiz interactif.

CSS est utilisé pour construire toute l'identité visuelle. Le fichier `styliste.css` centralise la majorité du design de l'application, notamment les variables de couleurs, la typographie, les cartes, la navigation, les boutons, les formulaires et les écrans mobiles. Le fichier `landing.css` est séparé afin de gérer les styles spécifiques à la page d'accueil publique. Cette séparation permet de garder une landing page plus expressive sans perturber le style de l'application.

Le projet utilise des variables CSS dans `:root` pour définir les couleurs, les espacements, la largeur maximale de l'application, les polices et les ombres. Ce choix facilite la cohérence graphique et rend les modifications plus rapides : changer une couleur principale ou une largeur globale peut se faire à un seul endroit.

JavaScript natif est utilisé dans `main.js` pour ajouter l'interactivité. Il gère la recherche d'offres, les filtres, le changement d'état du bouton de candidature, les transitions de navigation, l'affichage dynamique du détail d'une offre à partir d'un identifiant dans l'URL, ainsi que le fonctionnement du questionnaire d'orientation.

Les polices Google Fonts Montserrat et Poppins sont utilisées pour donner une hiérarchie visuelle claire. Montserrat sert principalement aux titres pour renforcer l'impact, tandis que Poppins est utilisée pour les textes d'interface afin de garder une bonne lisibilité.

L'utilisation de SVG intégrés directement dans le HTML permet d'afficher des icônes de navigation, de recherche, de retour et d'options sans dépendre d'une bibliothèque externe. Cela contribue à la légèreté du prototype et garantit que les icônes restent disponibles même sans installation supplémentaire.

Enfin, le choix d'une architecture statique rend l'application simple à présenter, tester et partager. Les données des offres sont simulées côté front-end, ce qui suffit pour démontrer le parcours utilisateur. Dans une version complète, ces données pourraient ensuite être remplacées par une API et une base de données sans modifier entièrement l'interface.
