"""
Interface web Streamlit pour SmartScheduler.

Lancement :
    py -m streamlit run app.py
"""
import streamlit as st
import pandas as pd

from prolog_bridge import charger_base, get_donnees, requete
from minizinc_bridge import generer_emploi_du_temps


# ===================================================================
# Configuration générale
# ===================================================================
st.set_page_config(
    page_title="SmartScheduler",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ===================================================================
# CSS personnalisé pour un look pro
# ===================================================================
st.markdown(
    """
<style>
/* Container principal */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1400px;
}

/* Titre principal en gradient (lisible sur fond sombre) */
.app-title {
    font-size: 2.5rem;
    font-weight: 800;
    background: linear-gradient(90deg, #818CF8 0%, #C084FC 50%, #F472B6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    line-height: 1.1;
}
.app-subtitle {
    color: #94A3B8;
    font-size: 1.05rem;
    margin-top: 0.25rem;
    margin-bottom: 0;
}

/* Cartes des metrics */
[data-testid="stMetric"] {
    background-color: #1E293B;
    padding: 1rem 1.25rem;
    border-radius: 12px;
    border: 1px solid #334155;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
    transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    border-color: #818CF8;
    box-shadow: 0 6px 20px rgba(129, 140, 248, 0.2);
}
[data-testid="stMetricLabel"] {
    font-size: 0.85rem !important;
    color: #94A3B8 !important;
    font-weight: 500 !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.85rem !important;
    font-weight: 700 !important;
    color: #F1F5F9 !important;
}

/* Onglets */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    border-bottom: 1px solid #334155;
}
.stTabs [data-baseweb="tab"] {
    padding: 12px 24px;
    border-radius: 8px 8px 0 0;
    font-weight: 500;
    color: #94A3B8;
}
.stTabs [aria-selected="true"] {
    background-color: #312E81;
    color: #C7D2FE !important;
    font-weight: 600;
}

/* Boutons primaires en gradient */
.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #6366F1, #8B5CF6);
    border: none;
    color: white !important;
    font-weight: 600;
    padding: 0.6rem 1.5rem;
    transition: all 0.15s ease;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(90deg, #818CF8, #A78BFA);
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(129, 140, 248, 0.45);
}

/* Boutons secondaires */
.stButton > button:not([kind="primary"]) {
    border: 1px solid #334155;
    background-color: #1E293B;
    color: #CBD5E1;
    font-weight: 500;
}
.stButton > button:not([kind="primary"]):hover {
    border-color: #818CF8;
    color: #C7D2FE;
    background-color: #312E81;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #0B1120;
    border-right: 1px solid #1E293B;
}
[data-testid="stSidebar"] h3 {
    color: #F1F5F9;
    font-size: 1rem !important;
    font-weight: 600;
    margin-bottom: 0.5rem;
}
[data-testid="stSidebar"] hr {
    border-color: #334155 !important;
}

/* Containers avec border (cartes) */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 12px !important;
    border-color: #334155 !important;
    background-color: #1E293B !important;
    padding: 1.25rem !important;
}

/* Expanders */
.streamlit-expanderHeader,
[data-testid="stExpander"] summary {
    font-weight: 500;
    color: #CBD5E1;
}

/* Tableaux */
[data-testid="stDataFrame"] {
    border-radius: 8px;
    overflow: hidden;
}

/* Inputs (textarea, text_input) */
.stTextInput input, .stTextArea textarea {
    background-color: #0F172A !important;
    color: #F1F5F9 !important;
    border-color: #334155 !important;
}

/* Alertes */
.stAlert {
    border-radius: 10px;
    background-color: #1E293B;
}

/* Divider */
hr {
    border-color: #334155 !important;
}
</style>
""",
    unsafe_allow_html=True,
)


# ===================================================================
# En-tête
# ===================================================================
st.markdown(
    """
<div style="display:flex; align-items:center; gap:1rem; margin-bottom:0.5rem;">
    <div style="font-size:3rem; line-height:1;">📅</div>
    <div>
        <div class="app-title">SmartScheduler</div>
        <p class="app-subtitle">Génération automatique d'emplois du temps · L2 Informatique</p>
    </div>
</div>
""",
    unsafe_allow_html=True,
)
st.divider()


# ===================================================================
# Sidebar
# ===================================================================
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    fichier_pl = st.text_input("📄 Fichier Prolog", "smartscheduler.pl")
    fichier_mzn = st.text_input("🧩 Modèle MiniZinc", "smartscheduler.mzn")

    st.divider()

    st.markdown("### 🔧 Actions")
    if st.button("🔄 Recharger la base", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

    st.divider()

    st.markdown(
        """
##### 📚 À propos

Système intelligent de génération d'emplois du temps universitaires sous contraintes.

**Stack technique**
- 🦉 **Prolog** — base de connaissances
- 🧩 **MiniZinc** — résolution CSP
- 🐍 **Python** + Streamlit — interface
"""
    )


# ===================================================================
# Chargement Prolog
# ===================================================================
if "donnees" not in st.session_state:
    try:
        with st.spinner("Chargement de la base Prolog..."):
            charger_base(fichier_pl)
            st.session_state["donnees"] = get_donnees()
    except Exception as e:
        st.error(f"❌ Impossible de charger la base Prolog : {e}")
        st.info("Vérifie que SWI-Prolog est installé et dans le PATH.")
        st.stop()

donnees = st.session_state["donnees"]

# Tables de correspondance créneaux
creneau_label = {
    cr_id: f"{jour.capitalize()} {h1}h–{h2}h"
    for cr_id, jour, h1, h2 in donnees["creneau"]
}
creneau_jour = {cr: j for cr, j, _, _ in donnees["creneau"]}
creneau_heure = {cr: h1 for cr, _, h1, _ in donnees["creneau"]}

JOURS_ORDRE = ["lundi", "mardi", "mercredi", "jeudi", "vendredi"]


# ===================================================================
# Onglets principaux
# ===================================================================
onglet_donnees, onglet_planning, onglet_export = st.tabs(
    ["📂  Données", "📊  Planning", "📥  Export"]
)


# ===================================================================
# Onglet 1 — Données
# ===================================================================
with onglet_donnees:
    st.markdown("### 📈 Vue d'ensemble")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Cours", len(donnees["cours"]))
    c2.metric("Enseignants", len(donnees["prof"]))
    c3.metric("Salles", len(donnees["salle"]))
    c4.metric("Groupes", len(donnees["groupe"]))
    c5.metric("Créneaux", len(donnees["creneau"]))

    st.markdown("####")

    col_a, col_b = st.columns(2)

    with col_a:
        with st.container(border=True):
            st.markdown("##### 🔗 Prérequis")
            prerequis = requete("prerequis(X, Y)")
            if prerequis:
                df = pd.DataFrame(
                    [{"Cours": r["X"], "Prérequis": r["Y"]} for r in prerequis]
                )
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("Aucun prérequis défini.")

        with st.container(border=True):
            st.markdown("##### 📌 Cours à planifier")
            df_plan = pd.DataFrame(
                [{"Groupe": g, "Cours": c} for g, c in donnees["a_planifier"]]
            )
            st.dataframe(df_plan, use_container_width=True, hide_index=True)

    with col_b:
        with st.container(border=True):
            st.markdown("##### 🕐 Créneaux disponibles")
            df_cr = pd.DataFrame(
                [
                    {"Id": cr, "Jour": j.capitalize(), "Début": f"{h1}h", "Fin": f"{h2}h"}
                    for cr, j, h1, h2 in donnees["creneau"]
                ]
            )
            st.dataframe(df_cr, use_container_width=True, hide_index=True)

        with st.container(border=True):
            st.markdown("##### 👨‍🏫 Habilitations")
            df_ens = pd.DataFrame(
                [{"Prof": p, "Cours": c} for p, c in donnees["peut_enseigner"]]
            )
            st.dataframe(df_ens, use_container_width=True, hide_index=True)


# ===================================================================
# Onglet 2 — Planning
# ===================================================================
with onglet_planning:
    col_btn, _ = st.columns([1, 3])
    with col_btn:
        if st.button(
            "🚀 Générer l'emploi du temps",
            type="primary",
            use_container_width=True,
        ):
            with st.spinner("⏳ Résolution en cours..."):
                try:
                    planning = generer_emploi_du_temps(donnees, fichier_mzn)
                except Exception as e:
                    st.error(f"❌ Erreur MiniZinc : {e}")
                    st.stop()

                if planning is None:
                    st.error("❌ Aucune solution trouvée — contraintes incompatibles ?")
                    st.stop()

                st.session_state["planning"] = planning
                st.toast(f"✅ {len(planning)} séances planifiées !", icon="🎉")

    if "planning" not in st.session_state:
        st.info("👆 Clique sur le bouton ci-dessus pour générer un emploi du temps.")
    else:
        planning = st.session_state["planning"]
        df = pd.DataFrame(planning)
        df["créneau (lisible)"] = df["creneau"].map(creneau_label)
        df["jour"] = df["creneau"].map(creneau_jour)
        df["heure"] = df["creneau"].map(creneau_heure)

        # ---- Indicateurs ----
        st.markdown("### 📈 Indicateurs")
        i1, i2, i3, i4 = st.columns(4)
        i1.metric("Séances", len(df))
        i2.metric("Salles utilisées", df["salle"].nunique())
        i3.metric("Profs mobilisés", df["prof"].nunique())
        i4.metric("Créneaux occupés", df["creneau"].nunique())

        st.markdown("####")

        # ---- Vue grille hebdomadaire par groupe ----
        st.markdown("### 🗓️ Emploi du temps hebdomadaire")

        groupes = sorted(df["groupe"].unique())
        sous_onglets = st.tabs([f"👥 Groupe {g}" for g in groupes])

        heures_uniques = sorted(set(df["heure"].tolist()))
        index_heures = [f"{h}h–{h+2}h" for h in heures_uniques]

        for idx, g in enumerate(groupes):
            with sous_onglets[idx]:
                df_g = df[df["groupe"] == g]

                grille = pd.DataFrame(
                    "—",
                    index=index_heures,
                    columns=[j.capitalize() for j in JOURS_ORDRE],
                )

                for _, row in df_g.iterrows():
                    jour = row["jour"].capitalize()
                    heure = f"{row['heure']}h–{row['heure']+2}h"
                    if jour in grille.columns and heure in grille.index:
                        grille.loc[heure, jour] = (
                            f"{row['cours']}\n{row['prof']} • {row['salle']}"
                        )

                def style_cell(val):
                    if val == "—":
                        return (
                            "background-color: #0F172A; "
                            "color: #475569; "
                            "text-align: center;"
                        )
                    return (
                        "background-color: #312E81; "
                        "color: #C7D2FE; "
                        "font-weight: 500;"
                    )

                styled = grille.style.map(style_cell)
                st.dataframe(styled, use_container_width=True, height=300)

        st.markdown("####")

        # ---- Vues filtrées ----
        st.markdown("### 🔍 Vues détaillées")
        col1, col2, col3 = st.columns(3)

        with col1:
            with st.container(border=True):
                st.markdown("##### 👥 Par groupe")
                for g in sorted(df["groupe"].unique()):
                    with st.expander(f"Groupe {g}"):
                        st.dataframe(
                            df[df["groupe"] == g][
                                ["cours", "prof", "salle", "créneau (lisible)"]
                            ],
                            use_container_width=True,
                            hide_index=True,
                        )

        with col2:
            with st.container(border=True):
                st.markdown("##### 👨‍🏫 Par enseignant")
                for p in sorted(df["prof"].unique()):
                    with st.expander(f"Prof {p}"):
                        st.dataframe(
                            df[df["prof"] == p][
                                ["cours", "groupe", "salle", "créneau (lisible)"]
                            ],
                            use_container_width=True,
                            hide_index=True,
                        )

        with col3:
            with st.container(border=True):
                st.markdown("##### 🏛️ Par salle")
                for s in sorted(df["salle"].unique()):
                    with st.expander(f"Salle {s}"):
                        st.dataframe(
                            df[df["salle"] == s][
                                ["cours", "groupe", "prof", "créneau (lisible)"]
                            ],
                            use_container_width=True,
                            hide_index=True,
                        )

        st.markdown("####")

        # ---- Tableau global ----
        with st.container(border=True):
            st.markdown("##### 📋 Tableau complet")
            st.dataframe(
                df[["groupe", "cours", "prof", "salle", "créneau (lisible)"]],
                use_container_width=True,
                hide_index=True,
            )


# ===================================================================
# Onglet 3 — Export
# ===================================================================
with onglet_export:
    if "planning" not in st.session_state:
        st.info("📌 Génère d'abord un planning dans l'onglet « Planning ».")
    else:
        df = pd.DataFrame(st.session_state["planning"])
        df["créneau (lisible)"] = df["creneau"].map(creneau_label)

        st.markdown("### 📥 Téléchargement")

        col_a, col_b = st.columns([1, 2])
        with col_a:
            with st.container(border=True):
                st.markdown("##### 📄 Format CSV")
                st.caption("Compatible Excel, Google Sheets, LibreOffice…")
                csv = df.to_csv(index=False).encode("utf-8-sig")
                st.download_button(
                    "📥 Télécharger CSV",
                    data=csv,
                    file_name="emploi_du_temps.csv",
                    mime="text/csv",
                    type="primary",
                    use_container_width=True,
                )

        with col_b:
            with st.container(border=True):
                st.markdown("##### 👁️ Aperçu du fichier")
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                    height=320,
                )
