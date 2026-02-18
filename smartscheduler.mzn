% --- Paramètres ---
int: nb_cours;
int: nb_profs;
int: nb_salles;
int: nb_groupes;
int: nb_creneaux;
int: nb_seances;

array[1..nb_salles] of int: capacite_salle;
array[1..nb_groupes] of int: effectif_groupe;

array[1..nb_groupes, 1..nb_cours] of int: groupe_suit_cours;
array[1..nb_profs, 1..nb_cours] of int: prof_peut_enseigner;
array[1..nb_profs, 1..nb_creneaux] of int: prof_disponible;
array[1..nb_salles, 1..nb_cours] of int: salle_compatible_cours;

array[1..nb_creneaux] of int: jour_creneau;
array[1..nb_creneaux] of int: heure_debut_creneau;

array[1..nb_seances] of int: seance_cours;
array[1..nb_seances] of int: seance_groupe;

% --- Variables de décision ---
array[1..nb_seances] of var 1..nb_profs: seance_prof;
array[1..nb_seances] of var 1..nb_salles: seance_salle;
array[1..nb_seances] of var 1..nb_creneaux: seance_creneau;

% --- Contraintes ---
constraint
  forall(s in 1..nb_seances) (
    % Professeur doit pouvoir enseigner le cours
    prof_peut_enseigner[seance_prof[s], seance_cours[s]] = 1 /\
    % Professeur disponible à ce créneau
    prof_disponible[seance_prof[s], seance_creneau[s]] = 1 /\
    % Salle compatible avec le cours
    salle_compatible_cours[seance_salle[s], seance_cours[s]] = 1 /\
    % Salle doit avoir une capacité suffisante
    capacite_salle[seance_salle[s]] >= effectif_groupe[seance_groupe[s]]
  );

% Pas de conflit de profs ou de salles sur le même créneau
constraint
  forall(i,j in 1..nb_seances where i < j) (
    (seance_creneau[i] != seance_creneau[j]) \/
    (seance_prof[i] != seance_prof[j] /\ seance_salle[i] != seance_salle[j])
  );

% --- Objectif (optionnel : minimiser les créneaux tardifs) ---
var int: max_creneau = max([heure_debut_creneau[seance_creneau[s]] | s in 1..nb_seances]);
solve satisfy;

% --- Sortie ---
output [
  if fix(seance_prof[s]) > 0 then
    "seance(\(seance_cours[s]),\(seance_groupe[s]),\(seance_prof[s]),\(seance_salle[s]),\(seance_creneau[s]))\n"
  else "" endif
  | s in 1..nb_seances
];
