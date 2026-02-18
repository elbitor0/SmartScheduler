from prolog_bridge import charger_base, get_prerequis
from minizinc_bridge import generer_emploi_du_temps

#  Charger la base Prolog ---
donnees = charger_base("smartscheduler.pl")

print("\n--- Prérequis transitifs ---")
for pre, crs in get_prerequis():
    print(f"  {pre} est prérequis de {crs}")

#  Appeler MiniZinc pour générer l'emploi du temps ---
resultat = generer_emploi_du_temps(donnees, solveur="gecode", timeout=30)

if not resultat:
    print("Aucune solution trouvée par MiniZinc.")
else:
    #  Affichage lisible ---
    print("\n===== EMPLOI DU TEMPS =====")
    for s in resultat["seances"]:
        print(f"{s['groupe']} : {s['cours']} avec {s['prof']} en {s['salle']} "
              f"({s['creneau']})")
    
    #  exporter en CSV
    try:
        from minizinc_bridge import exporter_csv
        # On peut reconstruire des infos sur les créneaux
        creneaux_info = {c[0]: (c[1], c[2], c[2]+2) for c in donnees["creneau"]}  # exemple: (jour, debut, fin)
        exporter_csv(resultat, creneaux_info, chemin="emploi_du_temps.csv")
    except Exception as e:
        print("Export CSV impossible :", e)