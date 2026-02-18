"""
prolog_bridge.py - Pont Python ↔ Prolog (CLP/Fd) via pyDatalog

Ce module :
 Lit le fichier Prolog (.pl) smartscheduler.pl
 Crée les faits dans pyDatalog
 Définit les règles logiques (prérequis transitifs, compatibilité salle/cours)
 Fournit des fonctions pour récupérer ces informations depuis Python
"""

from pyDatalog import pyDatalog

# --- Déclaration des termes pyDatalog ---
pyDatalog.create_terms(
    "X,Y,Z,C,G,P,S,Cr,Cap,T,"
    "cours,prof,salle,groupe,"
    "type_cours,prerequis,effectif,capacite,"
    "type_salle,besoin_salle,dispo,peut_enseigner,"
    "prerequis_transitif,salle_compatible,enseignant_pour_cours"
)

# --- Lecture du fichier Prolog ---
def lire_fichier_pl(chemin="smartscheduler.pl"):
    """
    Lit le fichier Prolog et retourne un dictionnaire avec tous les faits.
    """
    donnees = {
        "cours": [], "prof": [], "salle": [], "groupe": [],
        "type_cours": [], "prerequis": [], "effectif": [], "capacite": [],
        "type_salle": [], "besoin_salle": [], "dispo": [], "peut_enseigner": []
    }

    with open(chemin, "r", encoding="utf-8") as f:
        for ligne in f:
            ligne = ligne.strip()
            if not ligne or ligne.startswith("%") or ":-" in ligne:
                continue
            if "(" not in ligne or not ligne.endswith(")."):
                continue

            nom = ligne.split("(")[0].strip()
            contenu = ligne.split("(")[1].replace(").","")
            args = [a.strip() for a in contenu.split(",")]

            # Ignorer les variables (commencent par majuscule)
            if any(a[0].isupper() for a in args):
                continue

            if nom in donnees:
                donnees[nom].append(args)

    return donnees

# --- Charger les faits dans pyDatalog ---
def charger_dans_pyDatalog(donnees):
    for args in donnees["cours"]:
        +cours(args[0])
    for args in donnees["prof"]:
        +prof(args[0])
    for args in donnees["salle"]:
        +salle(args[0])
    for args in donnees["groupe"]:
        +groupe(args[0])
    for args in donnees["type_cours"]:
        +type_cours(args[0], args[1])
    for args in donnees["prerequis"]:
        +prerequis(args[0], args[1])
    for args in donnees["effectif"]:
        +effectif(args[0], int(args[1]))
    for args in donnees["capacite"]:
        +capacite(args[0], int(args[1]))
    for args in donnees["type_salle"]:
        +type_salle(args[0], args[1])
    for args in donnees["besoin_salle"]:
        +besoin_salle(args[0], args[1])
    for args in donnees["dispo"]:
        +dispo(args[0], args[1])
    for args in donnees["peut_enseigner"]:
        +peut_enseigner(args[0], args[1])

# --- Définition des règles logiques ---
def definir_regles():
    """
    Définit :
    - prerequis transitifs
    - compatibilité salle/cours
    - enseignants pour chaque cours
    """
    prerequis_transitif(X,Z) <= prerequis(X,Z)
    prerequis_transitif(X,Z) <= prerequis(X,Y) & prerequis_transitif(Y,Z)

    salle_compatible(C,S) <= besoin_salle(C,T) & type_salle(S,T)
    enseignant_pour_cours(P,C) <= peut_enseigner(P,C)

# --- Fonctions pour récupérer des informations ---
def get_prerequis(cours_id=None):
    if cours_id:
        resultat = prerequis_transitif(X,cours_id)
    else:
        resultat = prerequis_transitif(X,Y)
    return [(str(l[0]), cours_id) if cours_id else (str(l[0]), str(l[1])) for l in resultat]

def get_salles_compatibles(cours_id=None):
    if cours_id:
        resultat = salle_compatible(cours_id,S)
    else:
        resultat = salle_compatible(C,S)
    return [(cours_id,str(l[0])) if cours_id else (str(l[0]),str(l[1])) for l in resultat]

def get_enseignants_pour_cours(cours_id=None):
    if cours_id:
        resultat = enseignant_pour_cours(P,cours_id)
    else:
        resultat = enseignant_pour_cours(P,C)
    return [(str(l[0]),cours_id) if cours_id else (str(l[0]),str(l[1])) for l in resultat]

# --- Charger la base complète ---
def charger_base(chemin="smartscheduler.pl"):
    donnees = lire_fichier_pl(chemin)
    charger_dans_pyDatalog(donnees)
    definir_regles()
    return donnees

# --- Test ---
if __name__ == "__main__":
    donnees = charger_base()
    print("Cours :", [c[0] for c in donnees["cours"]])
    print("Profs :", [p[0] for p in donnees["prof"]])
    print("--- Prérequis transitifs ---")
    for p in get_prerequis():
        print(" ", p)
