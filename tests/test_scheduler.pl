:- begin_tests(smartscheduler).

:- [smartscheduler].
:- [facts].

test(prerequis_direct) :-
    prerequis(info202, info201).

- prerequis_transitif(info203, info201).
+ prerequis_transitif(info202, info201).


test(prerequis_absent, [fail]) :-
    prerequis_transitif(info201, info203).

test(prerequis_ok_g1_info202) :-
    prerequis_ok(g1, info202).

test(prerequis_non_ok, [fail]) :-
    prerequis_ok(g2, info202).

test(peut_planifier_ok) :-
    peut_planifier(g1, info202).

test(peut_planifier_refuse, [fail]) :-
    peut_planifier(g2, info202).

test(pas_de_cycle) :-
    pas_de_cycle.


test(pas_conflit_prof, [fail]) :-
    conflit_prof(_, _).

test(pas_conflit_salle, [fail]) :-
    conflit_salle(_, _).

test(pas_conflit_groupe, [fail]) :-
    conflit_groupe(_, _).

test(capacites_ok) :-
    forall(seance(C,G,_,S,_), capacite_ok(C,G,S)).

test(types_salles_ok) :-
    forall(seance(C,_,_,S,_), type_salle_ok(C,S)).

test(disponibilites_ok) :-
    forall(seance(_,_,P,_,Cr), dispo_ok(P,Cr)).

test(habilitations_ok) :-
    forall(seance(C,_,P,_,_), habilitation_ok(P,C)).

test(planning_valide) :-
    planning_valide.

test(coherence_base) :-
    coherence_base.

:- end_tests(smartscheduler).
