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

# ✅ Sélectionner une année avec un slider affichant une graduation
selected_year = st.select_slider(
    "Sélectionnez une année :",
    options=years,
    format_func=lambda x: str(x) if x % 1 == 0 else "",  # Affiche uniquement les graduations des années
)

st.session_state.selected_year = selected_year

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