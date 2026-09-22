import os
import streamlit as st
import pandas as pd
import psycopg2
import plotly.graph_objects as go
from dotenv import load_dotenv
from streamlit_autorefresh import st_autorefresh

# Charger les variables d'environnement locales si présentes
load_dotenv()

# Configuration de la page Streamlit (Mode large + Titre stylé)
st.set_page_config(
    page_title="OrbitalPulse | ISS Live Telemetry",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Rafraîchit automatiquement la page toutes les 10 secondes (10000 ms)
count = st_autorefresh(interval=10000, limit=None, key="iss_refresh")

# --- CSS CUSTOM "BADASS" (Style Spatial / Cyberpunk sombre) ---
st.markdown("""
    <style>
    .main {
        background-color: #0b0f19;
        color: #e2e8f0;
    }
    h1, h2, h3 {
        font-family: 'Helvetica Neue', sans-serif;
        color: #38bdf8 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stMetricValue {
        color: #38bdf8 !important;
        font-weight: 700;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONNEXION BASE DE DONNÉES ---
@st.cache_resource
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            database=os.getenv("POSTGRES_DB", "orbitalpulse"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres")
        )
        return conn
    except Exception as e:
        return None

def fetch_telemetry_history():
    conn = get_db_connection()
    if not conn:
        return None
    try:
        # Récupération des 40 derniers points pour dessiner la traînée de l'ISS
        query = """
            SELECT latitude, longitude, altitude, velocity, visibility, captured_at
            FROM iss_telemetry
            ORDER BY captured_at DESC
            LIMIT 40;
        """
        df = pd.read_sql(query, conn)
        if not df.empty:
            # Remettre dans l'ordre chronologique pour tracer la ligne de la trajectoire
            df = df.iloc[::-1].reset_index(drop=True)
        return df
    except Exception:
        return None

# --- HEADER DU DASHBOARD ---
st.title("🛰️ OrbitalPulse // Live ISS Telemetry Hub")
st.markdown("Suivi orbital en temps réel, alimenté par le pipeline K8s et visualisé via Plotly 3D Globe.")

# Récupération de l'historique des données
df_history = fetch_telemetry_history()

if df_history is not None and not df_history.empty:
    latest = df_history.iloc[-1] # Le point le plus récent
    lat = latest['latitude']
    lon = latest['longitude']
    alt = latest['altitude']
    vel = latest['velocity']
    vis = latest['visibility']
    time = latest['captured_at']

    # --- BANDEAU DE MÉTRIQUES ---
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric(label="Latitude", value=f"{lat:.4f}°")
    with col2:
        st.metric(label="Longitude", value=f"{lon:.4f}°")
    with col3:
        st.metric(label="Altitude", value=f"{alt:.2f} km")
    with col4:
        st.metric(label="Vitesse", value=f"{vel:,.0f} km/h")
    with col5:
        st.metric(label="Visibilité", value=f"{vis}".upper())

    st.markdown("---")

    # --- INTÉGRATION GLOBE 3D PLOTLY AVEC TRAJECTOIRE ---
    st.subheader("🌍 Vue Spatiale 3D (Trajectoire Orbitale)")

    fig = go.Figure()

    # 1. Trajectoire passée (ligne pointillée/atténuée avec points précédents)
    if len(df_history) > 1:
        fig.add_trace(go.Scattergeo(
            lat=df_history['latitude'][:-1],
            lon=df_history['longitude'][:-1],
            mode='lines+markers',
            name='Trajectoire récente',
            line=dict(width=2, color='#38bdf8'),
            marker=dict(size=3, color='#38bdf8', opacity=0.4)
        ))

    # 2. Position actuelle de l'ISS (point principal mis en avant)
    fig.add_trace(go.Scattergeo(
        lat=[lat],
        lon=[lon],
        mode='markers+text',
        name='ISS Actuelle',
        text=['ISS'],
        textposition='top center',
        textfont=dict(color='white', size=12),
        marker=dict(
            size=14,
            color='#38bdf8',
            symbol='circle',
            line=dict(width=2, color='white')
        )
    ))

   # Utilisation de la projection orthographique valide
    fig.update_geos(
        projection_type="orthographic",
        bgcolor="#0b0f19",
        oceancolor="#1e293b",
        landcolor="#334155",
        showcountries=True,
        countrycolor="#475569",
        showocean=True,
        showland=True,
        center=dict(lat=lat, lon=lon)
    )

    fig.update_layout(
        paper_bgcolor="#0b0f19",
        plot_bgcolor="#0b0f19",
        margin=dict(l=20, r=20, t=20, b=20),
        height=700, # Hauteur généreuse pour que ça respire
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

    st.caption(f"Dernière synchronisation des données : {time} UTC")

else:
    st.warning("⚠️ Aucune donnée de télémétrie disponible dans la base de données. Assurez-vous que le collecteur a bien injecté des données.")