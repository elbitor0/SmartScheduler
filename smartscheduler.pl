%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% SmartScheduler - Starter Prolog (v1)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% ====== ENTITÉS ======
cours(info201).
cours(info202).
cours(info203).

prof(martin).
prof(dupont).

salle(a101).
salle(lab3).

groupe(g1).
groupe(g2).

% ====== ATTRIBUTS ======
type_cours(info201, cm).
type_cours(info202, td).
type_cours(info203, tp).

prerequis(info202, info201)
prerequis(info203, info202)

valide(g1, info201)
valide(g2, info201)
valide(g2, info202)

effectif(g1, 35).
effectif(g2, 30).

capacite(a101, 40).
capacite(lab3, 35).

type_salle(a101, td).
type_salle(lab3, labo).

besoin_salle(info201, amphi).
besoin_salle(info202, td).
besoin_salle(info203, labo).

% ====== CRÉNEAUX ======
creneau(c1, lundi, 10, 12).
creneau(c2, lundi, 14, 16).
creneau(c3, mardi, 10, 12).
creneau(c4, mercredi, 10, 12).

% ====== DISPONIBILITÉS ======
dispo(martin, c1).
dispo(martin, c3).
dispo(dupont, c2).
dispo(dupont, c4).

% ====== ENSEIGNEMENT ======
peut_enseigner(martin, info201).
peut_enseigner(martin, info202).
peut_enseigner(dupont, info203).

% ====== PLAN ======
seance(info201, g1, martin, a101, c1).
seance(info202, g1, martin, a101, c3).
seance(info203, g1, dupont, lab3, c2).

seance(info201, g2, martin, a101, c3).
seance(info203, g2, dupont, lab3, c4).

% ====== CONTRAINTES ======
conflit_prof(P, Creneau) :-
    seance(C1, G1, P, S1, Creneau),
    seance(C2, G2, P, S2, Creneau),
    (C1 \= C2 ; G1 \= G2 ; S1 \= S2).

conflit_salle(Salle, Creneau) :-
    seance(C1, G1, P1, Salle, Creneau),
    seance(C2, G2, P2, Salle, Creneau),
    (C1 \= C2 ; G1 \= G2 ; P1 \= P2).

conflit_groupe(Groupe, Creneau) :-
    seance(C1, Groupe, P1, S1, Creneau),
    seance(C2, Groupe, P2, S2, Creneau),
    (C1 \= C2 ; P1 \= P2 ; S1 \= S2).

capacite_ok(Cours, Groupe, Salle) :-
    seance(Cours, Groupe, _, Salle, _),
    effectif(Groupe, E),
    capacite(Salle, Cap),
    E =< Cap.

type_salle_ok(Cours, Salle) :-
    seance(Cours, _, _, Salle, _),
    besoin_salle(Cours, TypeBesoin),
    type_salle(Salle, TypeBesoin).

dispo_ok(Prof, Creneau) :-
    seance(_, _, Prof, _, Creneau),
    dispo(Prof, Creneau).

prerequis_ok(Groupe, Cour) :-
    prerequis(Prerequis, Cour),
    valide(Groupe,Prerequis).

habilitation_ok(Prof, Cours) :-
    seance(Cours, _, Prof, _, _),
    peut_enseigner(Prof, Cours).

planning_valide :-
    \+ conflit_prof(_, _),
    \+ conflit_salle(_, _),
    \+ conflit_groupe(_, _),
    forall(seance(C,G,P,S,Cr), (
        capacite_ok(C,G,S),
        type_salle_ok(C,S),
        dispo_ok(P,Cr),
        habilitation_ok(P,C),
        prerequis_ok(G,C)
    )).

liste_conflits :-
    (conflit_prof(P,C),   format("Conflit PROF ~w au créneau ~w~n",[P,C]), fail ; true),
    (conflit_salle(S,C),  format("Conflit SALLE ~w au créneau ~w~n",[S,C]), fail ; true),
    (conflit_groupe(G,C), format("Conflit GROUPE ~w au créneau ~w~n",[G,C]), fail ; true).
