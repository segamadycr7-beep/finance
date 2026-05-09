 1   import streamlit as st
       2 - from streamlit_gsheets import GSheetsConnection
       2   import pandas as pd
       3   import plotly.express as px
       4 + import requests
       5   from datetime import datetime
       6
       7   # Configuration de la page
      10   st.title("👪 Finance Familiale Partagée")
      11   st.markdown("---")
      12
      13 - # 1. Connexion à Google Sheets
      14 - # Note : Pour que cela fonctionne en ligne, il faudra configurer les secrets dans Streamlit Cloud
      13 + # 1. Récupération des secrets
      14   try:
      16 -     conn = st.connection("gsheets", type=GSheetsConnection)
      17 -     df = conn.read(ttl="10m")
      15 +     SHEET_URL = st.secrets["connections"]["gsheets"]["spreadsheet"]
      16 +     API_URL = st.secrets["connections"]["gsheets"]["api_url"]
      17   except:
      19 -     st.error("⚠️ Connexion Google Sheets non configurée. L'application tourne en mode démo.")
      18 +     st.error("⚠️ Configuration manquante dans les Secrets.")
      19 +     st.stop()
      20 +
      21 + # Lecture des données (via Pandas pour la simplicité en lecture seule)
      22 + @st.cache_data(ttl=60)
      23 + def load_data():
      24 +     csv_url = SHEET_URL.replace("/edit#gid=", "/export?format=csv&gid=")
      25 +     return pd.read_csv(csv_url)
      26 +
      27 + try:
      28 +     df = load_data()
      29 + except:
      30       df = pd.DataFrame(columns=["Utilisateur", "Date", "Categorie", "Montant", "Description"])
      31
      22 - # 2. Identification de l'utilisateur
      ══════════════════════════════════════════════════════════════════════════════════════════════════════════════
      32 + # 2. Identification
      33   st.sidebar.header("👤 Utilisateur")
      34   nom_utilisateur = st.sidebar.text_input("Ton Prénom", value="Maiga")
      35
      26 - # 3. Formulaire d'ajout (Sidebar)
      ══════════════════════════════════════════════════════════════════════════════════════════════════════════════
      36 + # 3. Formulaire d'ajout
      37   st.sidebar.markdown("---")
      38   st.sidebar.header("➕ Nouvelle Dépense")
      39   with st.sidebar.form("ajout_depense"):
      44       submit = st.form_submit_button("Enregistrer")
      45
      46       if submit and nom_utilisateur:
      37 -         new_row = pd.DataFrame([{
      ══════════════════════════════════════════════════════════════════════════════════════════════════════════════
      47 +         payload = {
      48               "Utilisateur": nom_utilisateur,
      49               "Date": date.strftime("%Y-%m-%d"),
      50               "Categorie": cat,
      51               "Montant": montant,
      52               "Description": desc
      43 -         }])
      44 -         df = pd.concat([df, new_row], ignore_index=True)
      45 -         # Ici on écrira dans Google Sheets après configuration
      46 -         st.sidebar.success(f"Dépense de {nom_utilisateur} enregistrée !")
      47 -         st.cache_data.clear()
      48 -         st.rerun()
      53 +         }
      54 +         # Envoi à l'API Google Script
      55 +         response = requests.post(API_URL, json=payload)
      56 +         if response.status_code == 200:
      57 +             st.sidebar.success(f"Dépense enregistrée !")
      58 +             st.cache_data.clear()
      59 +             st.rerun()
      60 +         else:
      61 +             st.sidebar.error("Erreur de connexion.")
      62
      50 - # 4. Filtrage des données pour l'utilisateur actuel
      51 - if not df.empty:
      ══════════════════════════════════════════════════════════════════════════════════════════════════════════════
      63 + # 4. Dashboard
      64 + if not df.empty and nom_utilisateur:
      65       df_user = df[df['Utilisateur'] == nom_utilisateur]
      53 - else:
      54 -     df_user = pd.DataFrame()
      ══════════════════════════════════════════════════════════════════════════════════════════════════════════════
      66 +     if not df_user.empty:
      67 +         st.sidebar.markdown("---")
      68 +         budget = st.sidebar.number_input("Budget Mensuel", value=200000)
      69 +
      70 +         # Correction pour les dates
      71 +         df_user['Date'] = pd.to_datetime(df_user['Date'])
      72 +         depense_mois = df_user[df_user['Date'].dt.month == datetime.now().month]['Montant'].sum()
      73 +
      74 +         col1, col2 = st.columns(2)
      75 +         col1.metric(f"Dépenses de {nom_utilisateur}", f"{depense_mois:,.0f} FCFA")
      76 +         col2.metric("Reste", f"{budget - depense_mois:,.0f} FCFA")
      77 +
      78 +         st.progress(min(depense_mois / budget, 1.0))
      79
      56 - # 5. Dashboard
      57 - if not df_user.empty:
      58 -     # Budget Perso
      59 -     st.sidebar.markdown("---")
      60 -     budget = st.sidebar.number_input("Mon Budget Mensuel", value=200000)
      61 -
      62 -     depense_mois = df_user[pd.to_datetime(df_user['Date']).dt.month ==
         datetime.now().month]['Montant'].sum()
      63 -
      64 -     col1, col2 = st.columns(2)
      65 -     col1.metric(f"Dépenses de {nom_utilisateur}", f"{depense_mois:,.0f} FCFA")
      66 -     col2.metric("Reste du Budget", f"{budget - depense_mois:,.0f} FCFA")
      67 -
      68 -     st.progress(min(depense_mois / budget, 1.0))
      ══════════════════════════════════════════════════════════════════════════════════════════════════════════════
      80 +         c1, c2 = st.columns(2)
      81 +         fig_pie = px.pie(df_user, values='Montant', names='Categorie', title="Répartition")
      82 +         c1.plotly_chart(fig_pie, use_container_width=True)
      83 +
      84 +         fig_hist = px.bar(df_user, x='Date', y='Montant', color='Categorie', title="Historique")
      85 +         c2.plotly_chart(fig_hist, use_container_width=True)
      86
