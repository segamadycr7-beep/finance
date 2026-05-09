import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime

# Configuration de la page
st.set_page_config(page_title="Family Finance Cloud", layout="wide", page_icon="💰")

st.title("👪 Finance Familiale Partagée")
st.markdown("---")

# 1. Connexion à Google Sheets
# Note : Pour que cela fonctionne en ligne, il faudra configurer les secrets dans Streamlit Cloud
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl="10m")
except:
    st.error("⚠️ Connexion Google Sheets non configurée. L'application tourne en mode démo.")
    df = pd.DataFrame(columns=["Utilisateur", "Date", "Categorie", "Montant", "Description"])

# 2. Identification de l'utilisateur
st.sidebar.header("👤 Utilisateur")
nom_utilisateur = st.sidebar.text_input("Ton Prénom", value="Maiga")

# 3. Formulaire d'ajout (Sidebar)
st.sidebar.markdown("---")
st.sidebar.header("➕ Nouvelle Dépense")
with st.sidebar.form("ajout_depense"):
    date = st.date_input("Date", datetime.now())
    cat = st.selectbox("Catégorie", ["Logement", "Alimentation", "Transport", "Loisirs", "Santé", "Education", "Autres"])
    montant = st.number_input("Montant", min_value=0.0, step=100.0)
    desc = st.text_input("Description")
    submit = st.form_submit_button("Enregistrer")

    if submit and nom_utilisateur:
        new_row = pd.DataFrame([{
            "Utilisateur": nom_utilisateur,
            "Date": date.strftime("%Y-%m-%d"),
            "Categorie": cat,
            "Montant": montant,
            "Description": desc
        }])
        df = pd.concat([df, new_row], ignore_index=True)
        # Ici on écrira dans Google Sheets après configuration
        st.sidebar.success(f"Dépense de {nom_utilisateur} enregistrée !")
        st.cache_data.clear()
        st.rerun()

# 4. Filtrage des données pour l'utilisateur actuel
if not df.empty:
    df_user = df[df['Utilisateur'] == nom_utilisateur]
else:
    df_user = pd.DataFrame()

# 5. Dashboard
if not df_user.empty:
    # Budget Perso
    st.sidebar.markdown("---")
    budget = st.sidebar.number_input("Mon Budget Mensuel", value=200000)
    
    depense_mois = df_user[pd.to_datetime(df_user['Date']).dt.month == datetime.now().month]['Montant'].sum()
    
    col1, col2 = st.columns(2)
    col1.metric(f"Dépenses de {nom_utilisateur}", f"{depense_mois:,.0f} FCFA")
    col2.metric("Reste du Budget", f"{budget - depense_mois:,.0f} FCFA")
    
    st.progress(min(depense_mois / budget, 1.0))

    # Graphiques
    c1, c2 = st.columns(2)
    fig_pie = px.pie(df_user, values='Montant', names='Categorie', title="Mes Dépenses par Poste")
    c1.plotly_chart(fig_pie, use_container_width=True)
    
    fig_hist = px.bar(df_user, x='Date', y='Montant', color='Categorie', title="Mon Historique Temporel")
    c2.plotly_chart(fig_hist, use_container_width=True)

    st.markdown("### 📋 Mes dernières transactions")
    st.dataframe(df_user.sort_values(by="Date", ascending=False), use_container_width=True)
else:
    st.info(f"Bonjour {nom_utilisateur} ! Ajoute ta première dépense pour voir ton tableau de bord.")
