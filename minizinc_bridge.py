"""
minizinc_bridge.py - Pont Python ↔ MiniZinc

 Transforme les données Prolog/pyDatalog en format .dzn
 Lance MiniZinc
 Lit et décode les résultats
"""

import subprocess

# --- Convertir les identifiants en indices numériques ---
def creer_index(liste):
    idx = {}
    for i, item in enumerate(liste, start=1):
        idx[item[0]] = i
    return idx

JOURS = {"lundi":1,"mardi":2,"mercredi":3,"jeudi":4,"vendredi":5}

def ecrire_matrice(nom, matrice):
    texte = nom + " = ["
    for ligne in matrice:
        texte += "| " + ", ".join(map(str, ligne)) + "\n"
    texte += " |];\n"
    return texte

# --- Générer .dzn ---
def generer_dzn(donnees, chemin_sortie="smartscheduler.dzn"):
    idx_cours = creer_index(donnees["cours"])
    idx_profs = creer_index(donnees["prof"])
    idx_salles = creer_index(donnees["salle"])
    idx_groupes = creer_index(donnees["groupe"])
    idx_creneaux = creer_index(donnees["creneau"])

    nb_cours = len(idx_cours)
    nb_profs = len(idx_profs)
    nb_salles = len(idx_salles)
    nb_groupes = len(idx_groupes)
    nb_creneaux = len(idx_creneaux)

    # Capacités
    capacite_salle = [0]*nb_salles
    for s,c in donnees["capacite"]:
        capacite_salle[idx_salles[s]-1] = int(c)
    effectif_groupe = [0]*nb_groupes
    for g,e in donnees["effectif"]:
        effectif_groupe[idx_groupes[g]-1] = int(e)

    # Matrices
    groupe_suit = [[0]*nb_cours for _ in range(nb_groupes)]
    for g,c in donnees["valide"]:
        g_i = idx_groupes[g]-1
        c_i = idx_cours[c]-1
        groupe_suit[g_i][c_i] = 1

    prof_enseigne = [[0]*nb_cours for _ in range(nb_profs)]
    for p,c in donnees["peut_enseigner"]:
        p_i = idx_profs[p]-1
        c_i = idx_cours[c]-1
        prof_enseigne[p_i][c_i] = 1

    prof_dispo = [[0]*nb_creneaux for _ in range(nb_profs)]
    for p,cr in donnees["dispo"]:
        p_i = idx_profs[p]-1
        cr_i = idx_creneaux[cr]-1
        prof_dispo[p_i][cr_i] = 1

    salle_compat = [[0]*nb_cours for _ in range(nb_salles)]
    type_salle = {s:t for s,t in donnees["type_salle"]}
    besoin_cours = {c:t for c,t in donnees["besoin_salle"]}
    for s in idx_salles:
        for c in idx_cours:
            if type_salle.get(s) == besoin_cours.get(c):
                s_i = idx_salles[s]-1
                c_i = idx_cours[c]-1
                salle_compat[s_i][c_i] = 1

    # Creneaux
    jour_creneau = [1]*nb_creneaux
    heure_debut = [8]*nb_creneaux
    for cr,jour,hd,_ in donnees["creneau"]:
        if cr in idx_creneaux:
            i = idx_creneaux[cr]-1
            jour_creneau[i] = JOURS.get(jour,1)
            heure_debut[i] = int(hd)

    # Séances
    seance_cours = []
    seance_groupe = []
    for g,c in donnees["valide"]:
        seance_groupe.append(idx_groupes[g])
        seance_cours.append(idx_cours[c])
    nb_seances = len(seance_cours)

    # --- Écriture fichier .dzn ---
    with open(chemin_sortie,"w",encoding="utf-8") as f:
        f.write(f"nb_cours={nb_cours};\nnb_profs={nb_profs};\nnb_salles={nb_salles};\n")
        f.write(f"nb_groupes={nb_groupes};\nnb_creneaux={nb_creneaux};\nnb_seances={nb_seances};\n\n")
        f.write(f"capacite_salle={capacite_salle};\n")
        f.write(f"effectif_groupe={effectif_groupe};\n\n")
        f.write(ecrire_matrice("groupe_suit_cours",groupe_suit))
        f.write(ecrire_matrice("prof_peut_enseigner",prof_enseigne))
        f.write(ecrire_matrice("prof_disponible",prof_dispo))
        f.write(ecrire_matrice("salle_compatible_cours",salle_compat))
        f.write(f"jour_creneau={jour_creneau};\nheure_debut_creneau={heure_debut};\n\n")
        f.write(f"seance_cours={seance_cours};\nseance_groupe={seance_groupe};\n")

    # Mappings pour décodage
    mappings = {
        "cours": {v:k for k,v in idx_cours.items()},
        "profs": {v:k for k,v in idx_profs.items()},
        "salles": {v:k for k,v in idx_salles.items()},
        "groupes": {v:k for k,v in idx_groupes.items()},
        "creneaux": {v:k for k,v in idx_creneaux.items()},
    }
    return chemin_sortie,mappings

# --- Appel MiniZinc ---
def appeler_minizinc(mzn="smartscheduler.mzn",dzn="smartscheduler.dzn",solveur="gecode",timeout=30):
    cmd=["minizinc","--solver",solveur,"--time-limit",str(timeout*1000),mzn,dzn]
    try:
        res=subprocess.run(cmd,capture_output=True,text=True,timeout=timeout+10)
        if res.returncode!=0 and res.stderr:
            print("ERREUR MiniZinc:",res.stderr[:300])
        return res.stdout
    except FileNotFoundError:
        print("MiniZinc non installé !")
        return ""
    except subprocess.TimeoutExpired:
        print("Timeout MiniZinc")
        return ""

# --- Lecture des résultats ---
def lire_resultats(texte,mappings):
    seances=[]
    for l in texte.split("\n"):
        l=l.strip()
        if l.startswith("seance(") and l.endswith(")"):
            vals=list(map(int,l[7:-1].split(",")))
            seances.append({
                "cours": mappings["cours"].get(vals[0],f"cours_{vals[0]}"),
                "groupe": mappings["groupes"].get(vals[1],f"groupe_{vals[1]}"),
                "prof": mappings["profs"].get(vals[2],f"prof_{vals[2]}"),
                "salle": mappings["salles"].get(vals[3],f"salle_{vals[3]}"),
                "creneau": mappings["creneaux"].get(vals[4],f"creneau_{vals[4]}")
            })
    return seances

# --- Pipeline complet ---
def generer_emploi_du_temps(donnees,solveur="gecode",timeout=30):
    chemin,mappings=generer_dzn(donnees)
    sortie=appeler_minizinc(dzn=chemin,solveur=solveur,timeout=timeout)
    if not sortie or "UNSATISFIABLE" in sortie:
        print("Aucune solution trouvée")
        return None
    return lire_resultats(sortie,mappings)
