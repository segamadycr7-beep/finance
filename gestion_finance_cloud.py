import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime
# Configuration de la page
st.set_page_config(page_title="Family Finance Cloud", layout="wide", page_icon="💰")
st.title("👪 Finance Familiale Partagée")
st.markdown("---")
# 1. Récupération des secrets
try:
SHEET_URL = st.secrets["connections"]["gsheets"]["spreadsheet"]
API_URL = st.secrets["connections"]["gsheets"]["api_url"]
except:
st.error("⚠️ Configuration manquante dans les Secrets (spreadsheet ou api_url).")
st.stop()
# Lecture des données
@st.cache_data(ttl=60)
def load_data():
csv_url = SHEET_URL.split("/edit")[0] + "/export?format=csv"
return pd.read_csv(csv_url)
try:
df = load_data()
except:
df = pd.DataFrame(columns=["Utilisateur", "Date", "Categorie", "Montant", "Description"])
# 2. Identification
st.sidebar.header("👤 Utilisateur")
nom_utilisateur = st.sidebar.text_input("Ton Prénom", value="Maiga")
# 3. Formulaire d'ajout
st.sidebar.markdown("---")
st.sidebar.header("➕ Nouvelle Dépense")
with st.sidebar.form("ajout_depense"):
date = st.date_input("Date", datetime.now())
cat = st.selectbox("Catégorie", ["Logement", "Alimentation", "Transport", "Loisirs", "Santé", "Education",
"Autres"])
montant = st.number_input("Montant", min_value=0.0, step=100.0)
desc = st.text_input("Description")
submit = st.form_submit_button("Enregistrer")
if submit and nom_utilisateur:
payload = {
"Utilisateur": nom_utilisateur,
"Date": date.strftime("%Y-%m-%d"),
"Categorie": cat,
"Montant": montant,
"Description": desc
}
try:
response = requests.post(API_URL, json=payload)
if response.status_code == 200:
st.sidebar.success(f"Enregistré !")
st.cache_data.clear()
st.rerun()
else:
st.sidebar.error(f"Erreur API")
except:
st.sidebar.error(f"Erreur de connexion")
# 4. Dashboard
if not df.empty and nom_utilisateur:
if "Utilisateur" in df.columns:
df_user = df[df['Utilisateur'] == nom_utilisateur].copy()
if not df_user.empty:
st.sidebar.markdown("---")
budget = st.sidebar.number_input("Budget Mensuel", value=200000)
df_user['Date'] = pd.to_datetime(df_user['Date'])
depense_mois = df_user[df_user['Date'].dt.month == datetime.now().month]['Montant'].sum()
col1, col2 = st.columns(2)
col1.metric(f"Dépenses", f"{depense_mois:,.0f} FCFA")
col2.metric("Reste", f"{budget - depense_mois:,.0f} FCFA")
st.progress(min(depense_mois / budget, 1.0))
c1, c2 = st.columns(2)
fig_pie = px.pie(df_user, values='Montant', names='Categorie', title="Répartition")
c1.plotly_chart(fig_pie, use_container_width=True)
fig_hist = px.bar(df_user, x='Date', y='Montant', color='Categorie', title="Historique")
c2.plotly_chart(fig_hist, use_container_width=True)
st.dataframe(df_user.sort_values(by="Date", ascending=False), use_container_width=True)
else:
st.info(f"Bonjour {nom_utilisateur} ! Aucune donnée.")
else:
st.error("Titres de colonnes incorrects sur Google Sheet.")
else:
st.info("Prêt pour la saisie !")
