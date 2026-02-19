
from prolog_bridge import charger_base, get_donnees, requete
from minizinc_bridge import generer_emploi_du_temps

def main():

    print("Chargement de la base Prolog...")
    charger_base("smartscheduler.pl")

    print("\n--- Prérequis ---")
    for r in requete("prerequis(X, Y)"):
        print(f"{r['X']} est prérequis de {r['Y']}")

    print("\nRecuperation des donnees depuis Prolog...")
    donnees = get_donnees()

    print("Generation de l'emploi du temps avec MiniZinc...")
    resultat = generer_emploi_du_temps(donnees)

    if resultat is None:
        print("Aucune solution trouvée.")
        return

    print("\n===== EMPLOI DU TEMPS =====")
    for s in resultat:
        print(f"{s['groupe']} : {s['cours']} "
              f"avec {s['prof']} en {s['salle']} "
              f"({s['creneau']})")

if __name__ == "__main__":
    main()
