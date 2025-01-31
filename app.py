import streamlit as st
import pandas as pd
import folium
from folium.plugins import FastMarkerCluster
from streamlit_folium import st_folium
import plotly.express as px
from datetime import datetime

# ✅ Appliquer un titre principal et un sous-titre
st.title("William's Tech Portfolio")
st.subheader("Here's some projects I've worked on to improve my tech skills.")

# ✅ Ajouter le logo Spotify avant le titre "Spotify Streamings Map"
st.markdown(
    """
    <h2>
        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Spotify_icon.svg/1982px-Spotify_icon.svg.png" 
             alt="Spotify" width="40" style="vertical-align: middle; margin-right: 10px;"/>
        Spotify Streamings Map
    </h2>
    """,
    unsafe_allow_html=True
)

# ✅ Charger les données avec mise en cache pour optimiser l'exécution
@st.cache_data
def load_data():
    df = pd.read_csv("spotify_with_geo.csv")
    df['timestamp'] = pd.to_datetime(df['timestamp'])  # Conversion de la colonne timestamp
    df['year'] = df['timestamp'].dt.year
    df['month'] = df['timestamp'].dt.month
    return df

df = load_data()  # Chargement du DataFrame

# ✅ Vérifier que df contient bien les données
if df.empty:
    st.error("Erreur : Le fichier 'spotify_with_geo.csv' est vide ou introuvable.")
    st.stop()

# ✅ Calculer dynamiquement les statistiques utilisateur
start_year = 2011
current_year = datetime.now().year
months_subscribed = (current_year - start_year) * 12
spotify_cost = months_subscribed * 9.99  # Basé sur un abonnement mensuel de 9,99€
total_streams = len(df)  # Nombre total d'écoutes

# ✅ Calculer le prix payé par stream
price_per_stream = spotify_cost / total_streams if total_streams > 0 else 0

# ✅ Afficher le paragraphe dynamique
st.markdown(f"""
I've been using Spotify for a long time now. Since {start_year}, I have listened to **{total_streams:,}** songs on Spotify and have given the platform **{spotify_cost:.2f}€**. It represents about {price_per_stream:.6f}€ per stream, which is not much ! 
""")

# ✅ Sélectionner une année avec un slider interactif
years = sorted(df['year'].unique())
selected_year = st.select_slider("Sélectionnez une année :", options=years)
df_filtered = df[df['year'] == selected_year].dropna(subset=['latitude', 'longitude'])

# ✅ Générer la carte Folium avec les données filtrées
if not df_filtered.empty:
    bounds = [[df_filtered['latitude'].min(), df_filtered['longitude'].min()],
              [df_filtered['latitude'].max(), df_filtered['longitude'].max()]]
    map_spotify = folium.Map()
    map_spotify.fit_bounds(bounds)
    FastMarkerCluster(df_filtered[['latitude', 'longitude']].values.tolist()).add_to(map_spotify)
else:
    map_spotify = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=5)

# ✅ Afficher la carte avec Streamlit et récupérer l'état de la carte
map_data = st_folium(map_spotify, width=1000, height=500, returned_objects=["bounds"])

# ✅ Récupérer les clusters visibles et afficher le titre le plus écouté pour chaque cluster
if map_data and "bounds" in map_data:
    bounds = map_data["bounds"]
    min_lat, min_lon = bounds["_southWest"]["lat"], bounds["_southWest"]["lng"]
    max_lat, max_lon = bounds["_northEast"]["lat"], bounds["_northEast"]["lng"]

    # ✅ Filtrer les streams visibles sur la carte
    df_visible = df_filtered[
        (df_filtered["latitude"] >= min_lat) & (df_filtered["latitude"] <= max_lat) &
        (df_filtered["longitude"] >= min_lon) & (df_filtered["longitude"] <= max_lon)
    ]

# ✅ Trouver le titre le plus écouté par cluster visible
if not df_visible.empty:
    top_tracks = df_visible.groupby(["artist", "track"])["track"].count().reset_index(name="count")
    top_tracks = top_tracks.sort_values("count", ascending=False).head(3)  # Prendre les 3 titres les plus écoutés

    # ✅ Afficher les résultats avec l'artiste avant le titre
    st.write("🎵 **Top tracks visible on the map**:")
    for i, row in top_tracks.iterrows():
        st.write(f"🎶 **{row['artist']} - {row['track']}** - {row['count']} plays")

# ✅ Calculer le nombre de streams par mois et par année
streams_per_month = df.groupby(['year', 'month']).size().reset_index(name='count')

# ✅ Générer le graphique interactif avec Plotly
if not streams_per_month.empty:
    fig = px.line(
        streams_per_month, 
        x="month", 
        y="count", 
        color="year", 
        title="Évolution des écoutes Spotify par mois et par année",
        labels={"month": "Mois", "count": "Nombre de streams", "year": "Année"},
        markers=True
    )

    # ✅ Ajouter une légende interactive pour afficher/masquer les années
    fig.update_layout(
        xaxis=dict(tickmode="array", tickvals=list(range(1, 13)), ticktext=["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Août", "Sep", "Oct", "Nov", "Déc"]),
        legend_title_text="Cliquez sur une année pour masquer/afficher",
    )

    # ✅ Afficher le graphique
    st.plotly_chart(fig, use_container_width=True)