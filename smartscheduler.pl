%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% SmartScheduler - Règles / Contraintes
%% - Les DONNÉES sont dans facts.pl
%% - Ici : contraintes + vérification planning + règles utiles
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

:- [facts].
:- use_module(library(clpfd)).

% ===================================================================
% RÈGLES UTILES
% ===================================================================

% Prérequis transitifs (CL1) :
% P est un prérequis direct ou indirect de Cours
prerequis_transitif(Cours, P) :- prerequis(Cours, P).
prerequis_transitif(Cours, P) :- prerequis(Cours, X), prerequis_transitif(X, P).

% vrai si Groupe a validé tous les prérequis directs ET transitifs du cours
prerequis_ok(Groupe, Cours) :-
    forall(prerequis_transitif(Cours, P), valide(Groupe, P)).

% cours planifiables : demandés + prérequis ok
peut_planifier(G, C) :-
    a_planifier(G, C),
    prerequis_ok(G, C).

% Liste des cours qu'un groupe peut planifier cette semaine
cours_disponibles(Groupe, ListeCours) :-
    findall(C, peut_planifier(Groupe, C), ListeCours).

% ===================================================================
% DÉTECTION DE CYCLES (CL2)
% ===================================================================

% chemin_prereq(C, D, Visite) : il existe un chemin de C vers D
% dans le graphe des prérequis, sans repasser par les nœuds déjà visités
chemin_prereq(C, D, _Vis) :- prerequis(C, D).
chemin_prereq(C, D, Vis) :-
    prerequis(C, X),
    \+ member(X, Vis),
    chemin_prereq(X, D, [X|Vis]).

% cycle_prerequis(C) : vrai si C est son propre prérequis transitif
cycle_prerequis(C) :-
    cours(C),
    chemin_prereq(C, C, [C]).

% pas_de_cycle : vrai si la base ne contient aucun cycle
pas_de_cycle :- \+ cycle_prerequis(_).

% ===================================================================
% (TEMPORAIRE) PLAN À LA MAIN POUR TESTER
% => plus tard : remplacé par MiniZinc / CLPFD (génération)
% ===================================================================

seance(info201, g1, martin, amphi1, c1).
seance(info202, g1, martin, a101, c3).
seance(info203, g1, dupont, lab3, c2).

seance(info201, g2, martin, amphi1, c2).
seance(info203, g2, dupont, lab3, c4).

% ===================================================================
% CONTRAINTES (VALIDATION DU PLANNING)
% ===================================================================

% 1) un prof ne peut pas avoir 2 séances au même créneau
conflit_prof(P, Creneau) :-
    seance(C1, G1, P, S1, Creneau),
    seance(C2, G2, P, S2, Creneau),
    (C1 \= C2 ; G1 \= G2 ; S1 \= S2).

% 2) une salle ne peut pas être utilisée 2 fois au même créneauad
conflit_salle(Salle, Creneau) :-
    seance(C1, G1, P1, Salle, Creneau),
    seance(C2, G2, P2, Salle, Creneau),
    (C1 \= C2 ; G1 \= G2 ; P1 \= P2).

% 3) un groupe ne peut pas avoir 2 séances au même créneau
conflit_groupe(Groupe, Creneau) :-
    seance(C1, Groupe, P1, S1, Creneau),
    seance(C2, Groupe, P2, S2, Creneau),
    (C1 \= C2 ; P1 \= P2 ; S1 \= S2).

% 4) capacité salle >= effectif groupe
capacite_ok(Cours, Groupe, Salle) :-
    seance(Cours, Groupe, _, Salle, _),
    effectif(Groupe, E),
    capacite(Salle, Cap),
    E =< Cap.

% 5) type de salle adapté au cours
type_salle_ok(Cours, Salle) :-
    seance(Cours, _, _, Salle, _),
    besoin_salle(Cours, TypeBesoin),
    type_salle(Salle, TypeBesoin).

% 6) prof disponible sur ce créneau
dispo_ok(Prof, Creneau) :-
    seance(_, _, Prof, _, Creneau),
    dispo(Prof, Creneau).

% 7) prof habilité à enseigner le cours
habilitation_ok(Prof, Cours) :-
    seance(Cours, _, Prof, _, _),
    peut_enseigner(Prof, Cours).

% 8) pas de cours incompatibles dans le même planning groupe (CL4)
incompatibilite_ok(Groupe, Cours) :-
    \+ (incompatible(Cours, Autre), a_planifier(Groupe, Autre)).

% ===================================================================
% VALIDATEUR GLOBAL
% ===================================================================

planning_valide :-
    \+ conflit_prof(_, _),
    \+ conflit_salle(_, _),
    \+ conflit_groupe(_, _),
    forall(seance(C,G,P,S,Cr), (
        capacite_ok(C,G,S),
        type_salle_ok(C,S),
        dispo_ok(P,Cr),
        habilitation_ok(P,C),
        prerequis_ok(G,C),
        incompatibilite_ok(G,C)
    )).

% ===================================================================
% COHÉRENCE DE LA BASE (OF2)
% ===================================================================

coherence_base :-
    ( pas_de_cycle
      -> write('OK : aucun cycle dans les prerequis')
      ;  (cycle_prerequis(C),
          format('ERREUR : cycle detecte pour ~w', [C])) ),
    nl,
    ( forall(seance(C,_,P,_,_), peut_enseigner(P,C))
      -> write('OK : toutes les habilitations sont respectees')
      ;  write('ERREUR : un prof enseigne un cours non habilite') ),
    nl,
    ( forall(seance(C,_,_,S,_), type_salle_ok(C,S))
      -> write('OK : tous les types de salles sont adequats')
      ;  write('ERREUR : type de salle inadequat pour un cours') ),
    nl.

% ===================================================================
% AFFICHAGE DU PLANNING
% ===================================================================

% Affiche tout le planning, groupe par groupe
afficher_planning :-
    forall(groupe(G), planning_par_groupe(G)).

% Affiche le planning d'un groupe donné
planning_par_groupe(G) :-
    format("~n=== Planning du groupe ~w ===~n", [G]),
    forall(
        seance(C, G, P, S, Cr),
        ( creneau(Cr, Jour, Debut, Fin),
          format("  ~w | creneau ~w | Prof: ~w | Salle: ~w | ~w ~wh-~wh~n",
                 [C, Cr, P, S, Jour, Debut, Fin]) )
    ).

% Affiche le planning d'un enseignant donné
planning_par_prof(Prof) :-
    format("~n=== Planning du prof ~w ===~n", [Prof]),
    forall(
        seance(C, G, Prof, S, Cr),
        ( creneau(Cr, Jour, Debut, Fin),
          format("  ~w (groupe ~w) | Salle: ~w | ~w ~wh-~wh~n",
                 [C, G, S, Jour, Debut, Fin]) )
    ).

% Affiche le planning d'une salle donnée
planning_par_salle(Salle) :-
    format("~n=== Planning de la salle ~w ===~n", [Salle]),
    forall(
        seance(C, G, P, Salle, Cr),
        ( creneau(Cr, Jour, Debut, Fin),
          format("  ~w (groupe ~w) | Prof: ~w | ~w ~wh-~wh~n",
                 [C, G, P, Jour, Debut, Fin]) )
    ).

% ===================================================================
% DEBUG
% ===================================================================

liste_conflits :-
    (conflit_prof(P,C),   format("Conflit PROF ~w au créneau ~w~n",[P,C]), fail ; true),
    (conflit_salle(S,C),  format("Conflit SALLE ~w au créneau ~w~n",[S,C]), fail ; true),
    (conflit_groupe(G,C), format("Conflit GROUPE ~w au créneau ~w~n",[G,C]), fail ; true).
