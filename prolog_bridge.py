from pyswip import Prolog

prolog = Prolog()

def charger_base(fichier="smartscheduler.pl"):

    prolog.consult(fichier)

def requete(query):
   
    return list(prolog.query(query))

def get_prerequis(cours):
    results = requete(f"prerequis({cours}, X)")
    return [r["X"] for r in results]

def get_enseignants(cours):
    results = requete(f"peut_enseigner(P, {cours})")
    return [r["P"] for r in results]

def get_dispos(prof):
    results = requete(f"dispo({prof}, C)")
    return [r["C"] for r in results]

def get_salles_compatibles(cours):
    results = requete(f"besoin_salle({cours}, T), type_salle(S, T)")
    return [r["S"] for r in results]

def planning_valide():
    return bool(requete("planning_valide"))

def get_donnees():

    donnees = {
        "cours": [r["X"] for r in requete("cours(X)")],
        "prof": [r["X"] for r in requete("prof(X)")],
        "salle": [r["X"] for r in requete("salle(X)")],
        "groupe": [r["X"] for r in requete("groupe(X)")],

        "valide": [(r["G"], r["C"]) for r in requete("valide(G,C)")],
        "effectif": [(r["G"], r["E"]) for r in requete("effectif(G,E)")],
        "capacite": [(r["S"], r["C"]) for r in requete("capacite(S,C)")],

        "type_salle": [(r["S"], r["T"]) for r in requete("type_salle(S,T)")],
        "besoin_salle": [(r["C"], r["T"]) for r in requete("besoin_salle(C,T)")],

        "creneau": [
            (r["Id"], r["J"], r["H1"], r["H2"])
            for r in requete("creneau(Id,J,H1,H2)")
        ],

        "dispo": [(r["P"], r["C"]) for r in requete("dispo(P,C)")],
        "peut_enseigner": [
            (r["P"], r["C"]) for r in requete("peut_enseigner(P,C)")
        ],
        "a_planifier": [
            (r["G"], r["C"]) for r in requete("a_planifier(G,C)")
        ],
    }

    return donnees

if __name__ == "__main__":
    charger_base()
    print("Cours :", requete("cours(X)"))
    print("Prerequis info203 :", get_prerequis("info203"))
