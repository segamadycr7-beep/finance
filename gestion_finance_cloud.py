import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# CONFIGURATION DE LA PAGE
st.set_page_config(page_title="Finance Maiga", layout="wide", page_icon="💰")

st.title("💰 Ma Gestion Finance")
st.markdown("---")

# 1. RÉCUPÉRATION DES SECRETS
try:
    # Récupère les liens configurés dans les "Secrets" de Streamlit Cloud
    SHEET_URL = st.secrets["connections"]["gsheets"]["spreadsheet"]
    API_URL = st.secrets["connections"]["gsheets"]["api_url"]
except:
    st.error("⚠️ Erreur : Configurez les 'Secrets' dans Streamlit Cloud (spreadsheet et api_url).")
    st.stop()

# 2. LECTURE DES DONNÉES
@st.cache_data(ttl=60)
def load_data():
    # Convertit l'URL de partage en URL d'export CSV pour lecture directe
    csv_url = SHEET_URL.split("/edit")[0] + "/export?format=csv"
    return pd.read_csv(csv_url)

try:
    df = load_data()
except:
    # Si le fichier est vide ou introuvable, crée une structure vide
    df = pd.DataFrame(columns=["Utilisateur", "Date", "Categorie", "Montant", "Description"])

# 3. INTERFACE UTILISATEUR
nom = st.sidebar.text_input("Ton Prénom", value="Maiga")

st.sidebar.markdown("---")
st.sidebar.header("➕ Ajouter une dépense")

with st.sidebar.form("add_form"):
    date = st.date_input("Date", datetime.now())
    cat = st.selectbox("Catégorie", ["Logement", "Alimentation", "Transport", "Loisirs", "Santé", "Education", "Autres"])
    montant = st.number_input("Montant (FCFA)", min_value=0, step=100)
    desc = st.text_input("Description")
    
    submit = st.form_submit_button("Enregistrer")
    
    if submit and nom:
        # Prépare les données à envoyer
        payload = {
            "Utilisateur": nom,
            "Date": str(date),
            "Categorie": cat,
            "Montant": montant,
            "Description": desc
        }
        # Envoie les données au script Google (Apps Script)
        try:
            res = requests.post(API_URL, json=payload)
            if res.status_code == 200:
                st.sidebar.success("✅ Enregistré avec succès !")
                st.cache_data.clear() # Force le rechargement des données
                st.rerun()
            else:
                st.sidebar.error(f"❌ Erreur API : {res.status_code}")
        except Exception as e:
            st.sidebar.error(f"❌ Erreur de connexion : {e}")

# 4. AFFICHAGE DES RÉSULTATS
if not df.empty:
    # Filtre les données pour l'utilisateur actuel
    df_user = df[df['Utilisateur'] == nom]
    
    if not df_user.empty:
        # Indicateurs
        total = df_user['Montant'].sum()
        st.metric(f"Total des dépenses de {nom}", f"{total:,.0f} FCFA")
        
        # Tableau
        st.markdown("### 📋 Historique")
        st.dataframe(df_user.sort_values(by="Date", ascending=False), use_container_width=True)
        
        # Graphique simple
        fig = px.pie(df_user, values='Montant', names='Categorie', title="Répartition par catégorie")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(f"Bonjour {nom} ! Aucune donnée enregistrée pour le moment.")
else:
    st.info("La base de données est vide. Ajoutez une première dépense !")
