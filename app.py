import streamlit as st
import pandas as pd
import folium
from folium.plugins import FastMarkerCluster
from streamlit_folium import st_folium

# ✅ Charger les données avec mise en cache pour éviter les recalculs inutiles
@st.cache_data
def load_data():
    return pd.read_csv("spotify_with_geo.csv")

df = load_data()  # Assure-toi que le fichier existe

# ✅ Vérifier si df contient bien les données
if df.empty:
    st.error("Erreur : Le fichier 'spotify_with_geo.csv' est vide ou introuvable.")
    st.stop()

# Filtrer les lignes avec des valeurs NaN
df_filtered = df.dropna(subset=['latitude', 'longitude'])

# Créer la carte centrée sur la moyenne des coordonnées valides
map_spotify = folium.Map(location=[df_filtered['latitude'].mean(), df_filtered['longitude'].mean()], zoom_start=5)

# ✅ Utiliser FastMarkerCluster uniquement avec les valeurs valides
fast_cluster = FastMarkerCluster(df_filtered[['latitude', 'longitude']].values.tolist()).add_to(map_spotify)

# Afficher la carte avec Streamlit
st_folium(map_spotify, width=800, height=500)