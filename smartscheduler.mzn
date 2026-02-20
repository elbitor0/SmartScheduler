% Paramètres principaux

int: nbCours;
int: nbProfs;
int: nbSalles;
int: nbGroupes;
int: nbCreneaux;
int: nbSeances;

array[1..nbSalles] of int: capaciteSalle; % capacité des salles
array[1..nbGroupes] of int: tailleGroupe; % nombre d'étudiants par groupe

array[1..nbGroupes, 1..nbCours] of int: groupeSuitCours;
array[1..nbProfs, 1..nbCours] of int: profPeutFaire;
array[1..nbProfs, 1..nbCreneaux] of int: profEstDispo;
array[1..nbSalles, 1..nbCours] of int: salleOK;

array[1..nbCreneaux] of int: jourCreneau;
array[1..nbCreneaux] of int: heureDebut;

array[1..nbSeances] of int: seanceCours;
array[1..nbSeances] of int: seanceGroupe;


% Variables de décision

array[1..nbSeances] of var 1..nbProfs: profSeance;
array[1..nbSeances] of var 1..nbSalles: salleSeance;
array[1..nbSeances] of var 1..nbCreneaux: creneauSeance;


% Contraintes principales

constraint
forall(s in 1..nbSeances) (
% 1 Verifie que le prof sait enseigner ce cours
profPeutFaire[profSeance[s], seanceCours[s]] = 1 /\

% 2 Vérifie la disponibilite du prof
profEstDispo[profSeance[s], creneauSeance[s]] = 1 /\

% 3 Verifie compatibilite salle-cours
salleOK[salleSeance[s], seanceCours[s]] = 1 /\

% 4 Verifie capacite suffisante
capaciteSalle[salleSeance[s]] >= tailleGroupe[seanceGroupe[s]]

);


% Verifie si pas de conflits

constraint
forall(i in 1..nbSeances, j in 1..nbSeances where i < j) (

% Verifie sii même créneau, alors pas même prof et pas même salle
(creneauSeance[i] != creneauSeance[j]) \/
(
  profSeance[i] != profSeance[j] /\
  salleSeance[i] != salleSeance[j]
)

);

% Objectif

var int: dernierCreneauUtilise =
max([heureDebut[creneauSeance[s]] | s in 1..nbSeances]);

solve satisfy;

% Sortie

output [
if fix(profSeance[s]) > 0 then
"seance(" ++
show(seanceCours[s]) ++ "," ++
show(seanceGroupe[s]) ++ "," ++
show(profSeance[s]) ++ "," ++
show(salleSeance[s]) ++ "," ++
show(creneauSeance[s]) ++
")\n"
else
""
endif
| s in 1..nbSeances
];