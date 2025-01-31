import streamlit as st
import pandas as pd
import folium
from folium.plugins import FastMarkerCluster
from streamlit_folium import st_folium

# ✅ Charger les données avec mise en cache
@st.cache_data
def load_data():
    return pd.read_csv("spotify_with_geo.csv")

df = load_data()  # Assure-toi que le fichier existe

# ✅ Ajouter une colonne "année"
df['year'] = pd.to_datetime(df['timestamp']).dt.year

# ✅ Vérifier que df contient bien les données
if df.empty:
    st.error("Erreur : Le fichier 'spotify_with_geo.csv' est vide ou introuvable.")
    st.stop()

# ✅ Récupérer la liste des années disponibles
years = sorted(df['year'].unique())

# ✅ Initialiser `st.session_state` avec l'année la plus récente par défaut
if "selected_year" not in st.session_state:
    st.session_state.selected_year = max(years)  # Année la plus récente

# ✅ Afficher les années sous forme de boutons cliquables
st.write("### Sélectionnez une année :")
cols = st.columns(len(years))  # Créer une colonne par année

# ✅ Ajouter un bouton pour chaque année
for i, year in enumerate(years):
    if cols[i].button(str(year)):  # Si un bouton est cliqué, mise à jour de l'année sélectionnée
        st.session_state.selected_year = year

# ✅ Filtrer le DataFrame en fonction de l’année sélectionnée
selected_year = st.session_state.selected_year
df_filtered = df[df['year'] == selected_year]

# ✅ Supprimer les valeurs NaN dans latitude ou longitude
df_filtered = df_filtered.dropna(subset=['latitude', 'longitude'])

# ✅ Générer la carte Folium avec les données filtrées
if not df_filtered.empty:
    bounds = [[df_filtered['latitude'].min(), df_filtered['longitude'].min()],
              [df_filtered['latitude'].max(), df_filtered['longitude'].max()]]
    map_spotify = folium.Map()
    map_spotify.fit_bounds(bounds)
else:
    map_spotify = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=5)

# ✅ Utiliser FastMarkerCluster uniquement avec les valeurs filtrées
fast_cluster = FastMarkerCluster(df_filtered[['latitude', 'longitude']].values.tolist()).add_to(map_spotify)

# ✅ Afficher la carte avec Streamlit
st_folium(map_spotify, width=800, height=500)