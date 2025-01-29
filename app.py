import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

# Charger les données géolocalisées
@st.cache_data
def load_data():
    return pd.read_csv("spotify_with_geo.csv")  # Assure-toi d'avoir ce fichier

df = load_data()

# Titre de l'application
st.title("📍 Spotify Streaming Map")
st.write("Carte interactive des lieux où j'ai écouté de la musique sur Spotify.")

# Créer une carte Folium
map_spotify = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=5)
marker_cluster = MarkerCluster().add_to(map_spotify)

# Ajouter les marqueurs
for idx, row in df.dropna(subset=['latitude', 'longitude']).iterrows():
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=f"{row['track']} - {row['artist']}<br>Écouté à {row['city']}, {row['region']}, {row['country_full']}",
        tooltip=row['track']
    ).add_to(marker_cluster)

# Afficher la carte dans Streamlit
st_folium(map_spotify, width=800, height=500)