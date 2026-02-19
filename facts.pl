%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% facts.pl — Données (faits) SmartScheduler
%% Contient UNIQUEMENT des faits (pas de règles).
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% ====== ENTITÉS ======

cours(info201).
cours(info202).
cours(info203).

prof(martin).
prof(dupont).

salle(a101).
salle(lab3).
salle(amphi1).

groupe(g1).
groupe(g2).

% ====== ATTRIBUTS ======

type_cours(info201, cm).
type_cours(info202, td).
type_cours(info203, tp).

% prerequis(Cours, Prerequis)
prerequis(info202, info201).
% (si vous voulez remettre ce prerequis plus tard, assurez-vous que g1 valide info202)
% prerequis(info203, info202).

% valide(Groupe, Cours) = cours déjà validé
valide(g1, info201).
valide(g2, info201).
valide(g2, info202).

effectif(g1, 35).
effectif(g2, 30).

capacite(a101, 40).
capacite(lab3, 35).
capacite(amphi1, 120).

type_salle(a101, td).
type_salle(lab3, labo).
type_salle(amphi1, amphi).

% besoin_salle(Cours, TypeSalle)
besoin_salle(info201, amphi).
besoin_salle(info202, td).
besoin_salle(info203, labo).

% ====== CRÉNEAUX ======
% creneau(Id, Jour, Debut, Fin).
creneau(c1, lundi, 10, 12).
creneau(c2, lundi, 14, 16).
creneau(c3, mardi, 10, 12).
creneau(c4, mercredi, 10, 12).

% ====== DISPONIBILITÉS ======
% dispo(Prof, CreneauId).
dispo(martin, c1).
dispo(martin, c2).
dispo(martin, c3).
dispo(dupont, c2).
dispo(dupont, c4).

% ====== ENSEIGNEMENT ======
% peut_enseigner(Prof, Cours).
peut_enseigner(martin, info201).
peut_enseigner(martin, info202).
peut_enseigner(dupont, info203).

% ====== À PLANIFIER (input planning) ======
% a_planifier(Groupe, Cours) = cours demandés cette semaine

a_planifier(g1, info201).
a_planifier(g1, info202).
a_planifier(g1, info203).

a_planifier(g2, info201).
a_planifier(g2, info203).

% ====== INCOMPATIBILITÉS (CL4) ======
% incompatible(Cours1, Cours2) = ces deux cours ne peuvent pas être
% suivis par le même groupe dans la même semaine.
:- dynamic incompatible/2.
% Exemple : % incompatible(info201, info205).
