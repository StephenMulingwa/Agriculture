import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from streamlit_folium import st_folium
import folium

# --- Page Configuration ---
st.set_page_config(page_title="Kenyan Market Prices", layout="wide")
st.title("🇰🇪 Kenyan Agricultural Market Prices Explorer")

# --- Secure Database Connection ---
engine = create_engine(st.secrets["database"]["url"])

# --- Load Data ---
@st.cache_data
def load_data():
    return pd.read_sql("SELECT * FROM public.data", engine)

df = load_data()
df["county"] = df["county"].str.lower().str.strip()

# --- Coordinates ---
county_coords = {
    "baringo": (0.6411, 36.0915), "bomet": (-0.7826, 35.3027), "bungoma": (0.5685, 34.5584),
    "busia": (0.4694, 34.0901), "elgeyo marakwet": (1.1436, 35.4786), "embu": (-0.5399, 37.4570),
    "garissa": (-0.4532, 39.6460), "homa bay": (-0.5272, 34.4571), "isiolo": (0.3524, 37.5822),
    "kajiado": (-1.8238, 36.7768), "kakamega": (0.2827, 34.7519), "kericho": (-0.3673, 35.2833),
    "kiambu": (-1.0333, 36.6500), "kilifi": (-3.5107, 39.9093), "kirinyaga": (-0.6590, 37.3827),
    "kisii": (-0.6817, 34.7666), "kisumu": (-0.0917, 34.7679), "kitui": (-1.3743, 38.0106),
    "kwale": (-4.1833, 39.4500), "laikipia": (0.2922, 36.7928), "lamu": (-2.2741, 40.9027),
    "machakos": (-1.5177, 37.2634), "makueni": (-1.8044, 37.6200), "mandera": (3.9376, 41.8569),
    "marsabit": (2.3264, 38.4368), "meru": (0.0471, 37.6498), "migori": (-1.0634, 34.4731),
    "mombasa": (-4.0435, 39.6682), "muranga": (-0.7833, 37.1500), "nairobi city": (-1.286389, 36.817223),
    "nakuru": (-0.3031, 36.0800), "nandi": (0.2104, 35.2544), "narok": (-1.1041, 35.8713),
    "nyamira": (-0.5631, 34.9341), "nyandarua": (-0.1806, 36.5561), "nyeri": (-0.4167, 36.9500),
    "samburu": (1.1626, 36.7202), "siaya": (0.0612, 34.2422), "taita-taveta": (-3.3169, 38.4840),
    "tana river": (-1.1917, 40.1394), "tharaka nithi": (-0.2579, 37.9294), "trans nzoia": (1.0157, 34.9869),
    "turkana": (3.3120, 35.5658), "uasin gishu": (0.4532, 35.3027), "vihiga": (0.0707, 34.7282),
    "wajir": (1.7500, 40.0500), "west pokot": (1.3057, 35.3646)
}

# --- Filter Layout ---
st.markdown("### 🔍 Filter Market Prices")

unique_commodities = sorted(df["Commodity"].dropna().unique().tolist())
unique_years = sorted(df["year"].dropna().unique().tolist())
unique_months = sorted(df["month"].dropna().unique().tolist())

col1, col2, col3 = st.columns(3)
with col1:
    selected_commodity = st.selectbox("Commodity", ["All"] + unique_commodities)
with col2:
    selected_year = st.selectbox("Year", ["All"] + unique_years)
with col3:
    selected_month = st.selectbox("Month", ["All"] + unique_months)
# --- Filtering ---
filtered_df = df.copy()

if selected_commodity != "All":
    filtered_df = filtered_df[filtered_df["Commodity"] == selected_commodity]
if selected_year != "All":
    filtered_df = filtered_df[filtered_df["year"] == selected_year]
if selected_month != "All":
    filtered_df = filtered_df[filtered_df["month"].str.lower() == selected_month.lower()]

# --- Header Info ---
header_parts = []
if selected_commodity != "All":
    header_parts.append(selected_commodity)
if selected_month != "All":
    header_parts.append(selected_month)
if selected_year != "All":
    header_parts.append(str(selected_year))
header_suffix = " - " + " ".join(header_parts) if header_parts else ""

# --- Data Table ---
if not filtered_df.empty:
    st.markdown(f"### 🛒 Market Prices{header_suffix}")
    display_df = filtered_df[["county", "market", "Commodity", "unit", "kg", "price"]].sort_values(by="price", ascending=False)
    st.dataframe(display_df.reset_index(drop=True), use_container_width=True)

    # --- Map ---
    st.markdown(f"### 🗺️ County Price Map{header_suffix}")

    # Add coordinates
    filtered_df["lat"] = filtered_df["county"].map(lambda x: county_coords.get(x.lower(), (None, None))[0])
    filtered_df["lon"] = filtered_df["county"].map(lambda x: county_coords.get(x.lower(), (None, None))[1])
    map_df = filtered_df.dropna(subset=["lat", "lon"])

    if selected_commodity != "All" and not map_df.empty:
        m = folium.Map(location=[0.1768, 37.9083], zoom_start=6, tiles="OpenStreetMap")
        for _, row in map_df.iterrows():
            popup = f"{row['county'].title()}<br><b>Ksh {row['price']}</b>"
            folium.Marker(
                location=[row["lat"], row["lon"]],
                popup=popup,
                tooltip=row["county"].title()
            ).add_to(m)
        st_folium(m, height=550, width=900)
    else:
        st.info("Map is hidden when 'All' commodities are selected to avoid clutter.")
else:
    st.warning("No data found for this selection.")
