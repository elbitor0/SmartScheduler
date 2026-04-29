# SmartScheduler

SmartScheduler est un système de génération automatique d'emplois du temps universitaires, développé dans le cadre du module de Programmation Logique et par Contraintes en L2 Informatique.

Le projet combine deux paradigmes complémentaires. La programmation logique, en Prolog, sert à modéliser la base de connaissances : cours, prérequis, enseignants, salles, créneaux et leurs relations. La programmation par contraintes, en MiniZinc, prend ensuite le relais pour résoudre le problème d'allocation des séances aux créneaux disponibles, en respectant toutes les contraintes (capacités des salles, disponibilités des profs, non-chevauchement, etc.). Une interface web réalisée avec Streamlit permet de visualiser les emplois du temps générés et de les exporter.

## Prérequis

Avant de lancer le projet, il faut avoir trois outils installés sur la machine.

D'abord Python 3.8 ou une version plus récente (le projet a été testé avec Python 3.13). Ensuite SWI-Prolog, à télécharger sur le site officiel https://www.swi-prolog.org/download/stable. Et enfin MiniZinc en version 2.8 ou supérieure, disponible sur https://www.minizinc.org/software.html.

Pour SWI-Prolog et MiniZinc, il faut bien penser à les ajouter au PATH du système au moment de l'installation, sinon les commandes `swipl` et `minizinc` ne seront pas reconnues dans le terminal.

## Installation

Une fois les outils ci-dessus installés, place-toi dans le dossier du projet :

```powershell
cd SmartScheduler
```

Puis installe les paquets Python nécessaires :

```powershell
py -m pip install -r requirements.txt
```

Cela installe pyswip (le pont entre Python et SWI-Prolog), minizinc (le pont vers le solveur), streamlit (pour l'interface web) et pandas (pour la manipulation des tableaux de données).

## Utilisation

Le moyen le plus simple d'utiliser SmartScheduler est de lancer l'interface web :

```powershell
py -m streamlit run app.py
```

Streamlit ouvre automatiquement le navigateur sur http://localhost:8501. L'interface est organisée en trois onglets. L'onglet Données affiche les statistiques de la base de connaissances, la liste des prérequis, les créneaux disponibles et les habilitations des enseignants. L'onglet Planning lance la génération de l'emploi du temps : une grille hebdomadaire colorée montre les séances par groupe, et trois vues détaillées permettent de filtrer par groupe, par enseignant ou par salle. L'onglet Export propose le téléchargement du planning généré au format CSV.

Une version en ligne de commande est aussi disponible si tu préfères travailler dans le terminal :

```powershell
py main.py
```

Et pour interroger directement la base Prolog dans un mode interactif :

```powershell
swipl -s smartscheduler.pl
```

Une fois dans l'invite `?-`, tu peux tester par exemple `planning_valide.` pour vérifier que toutes les contraintes sont satisfaites, ou `afficher_planning.` pour afficher le planning séance par séance directement en console.

## Structure du projet

Le code est organisé autour de cinq fichiers principaux. La base de connaissances Prolog est séparée en deux. Le fichier `facts.pl` contient uniquement les faits, c'est-à-dire les données brutes : cours, professeurs, salles, créneaux, capacités, disponibilités, prérequis. Le fichier `smartscheduler.pl` regroupe les règles et les contraintes : prédicats de validation du planning, détection de cycles dans les prérequis, calcul des prérequis transitifs, et tous les utilitaires d'affichage.

Du côté Python, le fichier `prolog_bridge.py` charge la base Prolog grâce à pyswip et expose des fonctions pour en extraire les données sous forme de dictionnaires Python. Le fichier `minizinc_bridge.py` se charge ensuite de traduire ces données dans le format attendu par MiniZinc, de lancer le solveur, puis de reformater la solution renvoyée. Le modèle CSP en lui-même est dans `smartscheduler.mzn`, qui définit les variables de décision (à quel prof, quelle salle et quel créneau attribuer chaque séance) et les contraintes à respecter.

Enfin, `app.py` contient toute l'interface web Streamlit avec son thème sombre, sa grille hebdomadaire et ses vues filtrées, tandis que `main.py` propose une version en ligne de commande plus minimaliste pour les tests rapides.

Le dossier `tests/` contient les tests unitaires de la partie Prolog. Pour les lancer :

```powershell
swipl -g run_tests -t halt -s tests/test_scheduler.pl
```

## Auteurs

Nour, étudiante en L2 Informatique.
