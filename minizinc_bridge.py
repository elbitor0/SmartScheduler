
from minizinc import Model, Solver, Instance

JOURS = {
    "lundi": 1,
    "mardi": 2,
    "mercredi": 3,
    "jeudi": 4,
    "vendredi": 5
}

def preparer_donnees(donnees):

    idx_c = {c: i+1 for i, c in enumerate(donnees["cours"])}
    idx_p = {p: i+1 for i, p in enumerate(donnees["prof"])}
    idx_s = {s: i+1 for i, s in enumerate(donnees["salle"])}
    idx_g = {g: i+1 for i, g in enumerate(donnees["groupe"])}
    idx_cr = {c[0]: i+1 for i, c in enumerate(donnees["creneau"])}

    nc = len(idx_c)
    np = len(idx_p)
    ns = len(idx_s)
    ng = len(idx_g)
    ncr = len(idx_cr)

    cap = [0] * ns
    for s, c in donnees["capacite"]:
        cap[idx_s[s]-1] = int(c)

    eff = [0] * ng
    for g, e in donnees["effectif"]:
        eff[idx_g[g]-1] = int(e)

    g_suit = [[0]*nc for _ in range(ng)]
    for g, c in donnees["valide"]:
        g_suit[idx_g[g]-1][idx_c[c]-1] = 1

    p_ens = [[0]*nc for _ in range(np)]
    for p, c in donnees["peut_enseigner"]:
        p_ens[idx_p[p]-1][idx_c[c]-1] = 1

    p_dis = [[0]*ncr for _ in range(np)]
    for p, cr in donnees["dispo"]:
        p_dis[idx_p[p]-1][idx_cr[cr]-1] = 1

    ts = {s: t for s, t in donnees["type_salle"]}
    bc = {c: t for c, t in donnees["besoin_salle"]}

    s_comp = [[0]*nc for _ in range(ns)]
    for s in idx_s:
        for c in idx_c:
            if ts.get(s) == bc.get(c):
                s_comp[idx_s[s]-1][idx_c[c]-1] = 1

    jours = [1] * ncr
    heures = [8] * ncr

    for cr, j, h1, _ in donnees["creneau"]:
        jours[idx_cr[cr]-1] = JOURS.get(j, 1)
        heures[idx_cr[cr]-1] = int(h1)

    sc = []
    sg = []

    for g, c in donnees["a_planifier"]:
        sc.append(idx_c[c])
        sg.append(idx_g[g])

    data = {
        "nbCours": nc,
        "nbProfs": np,
        "nbSalles": ns,
        "nbGroupes": ng,
        "nbCreneaux": ncr,
        "nbSeances": len(sc),

        "capaciteSalle": cap,
        "tailleGroupe": eff,
        "groupeSuitCours": g_suit,
        "profPeutFaire": p_ens,
        "profEstDispo": p_dis,
        "salleOK": s_comp,
        "jourCreneau": jours,
        "heureDebut": heures,

        "seanceCours": sc,
        "seanceGroupe": sg,
    }

    maps = {
        "cours": {v: k for k, v in idx_c.items()},
        "profs": {v: k for k, v in idx_p.items()},
        "salles": {v: k for k, v in idx_s.items()},
        "groupes": {v: k for k, v in idx_g.items()},
        "creneaux": {v: k for k, v in idx_cr.items()},
    }

    return data, maps


def solve(model_file, data):
    model = Model(model_file)
    solver = Solver.lookup("gecode")
    instance = Instance(solver, model)

    for key in data:
        instance[key] = data[key]

    return instance.solve()


def generer_emploi_du_temps(donnees, model_file="smartscheduler.mzn"):
    data, maps = preparer_donnees(donnees)
    result = solve(model_file, data)

    if result.solution is None:
        print("Aucune solution trouvee")
        return None

    seances = []

    for i in range(data["nbSeances"]):
        seances.append({
            "cours": maps["cours"][data["seanceCours"][i]],
            "groupe": maps["groupes"][data["seanceGroupe"][i]],
            "prof": maps["profs"][result["profSeance"][i]],
            "salle": maps["salles"][result["salleSeance"][i]],
            "creneau": maps["creneaux"][result["creneauSeance"][i]],
        })

    return seances
