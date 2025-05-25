import streamlit as st
import requests

# RDW API endpoints
BASE_VEHICLE_URL = "https://opendata.rdw.nl/resource/m9d7-ebf2.json"
BASE_FUEL_URL = "https://opendata.rdw.nl/resource/8ys7-d773.json"

def fetch_vehicle_data(plate):
    """Fetch basic vehicle info"""
    try:
        response = requests.get(f"{BASE_VEHICLE_URL}?kenteken={plate}", timeout=10)
        if response.status_code == 200 and response.json():
            return response.json()[0]
    except:
        pass
    return None

def fetch_fuel_data(plate):
    """Fetch fuel/emissions info"""
    try:
        response = requests.get(f"{BASE_FUEL_URL}?kenteken={plate}", timeout=10)
        if response.status_code == 200 and response.json():
            return response.json()[0]
    except:
        pass
    return None

def format_date(date_str):
    """Format date for display"""
    if date_str:
        return date_str[:10]
    return "Niet beschikbaar"

def format_value(value, unit=""):
    """Format value with unit"""
    if value:
        return f"{value} {unit}".strip()
    return "Niet beschikbaar"

# Streamlit UI
st.set_page_config(
    page_title="RDW Voertuig Informatie", 
    page_icon="🚗",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    text-align: center;
    padding: 2rem;
    background: linear-gradient(90deg, #1f4e79 0%, #2c5aa0 100%);
    color: white;
    border-radius: 10px;
    margin-bottom: 2rem;
}
.info-section {
    background: white;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.stButton > button {
    background: #1f4e79;
    color: white;
    border: none;
    border-radius: 5px;
    padding: 0.5rem 2rem;
    font-weight: bold;
    width: 100%;
}
.stButton > button:hover {
    background: #2c5aa0;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🚗 RDW Voertuig Informatie</h1>
    <p>Zoek officiële voertuiggegevens op kenteken</p>
</div>
""", unsafe_allow_html=True)

# Search section
st.markdown("### 🔍 Kenteken Opzoeken")

col1, col2, col3 = st.columns([3, 1, 1])

with col1:
    plate_input = st.text_input(
        "Voer kenteken in", 
        placeholder="Bijvoorbeeld: GGX11S",
        max_chars=10
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)  # Add space to align with input field
    search_button = st.button("🔍 Zoeken")

with col3:
    st.markdown("<br>", unsafe_allow_html=True)  # Add space to align with input field
    clear_button = st.button("🗑️ Wissen")
    if clear_button:
        st.rerun()

if search_button:
    if plate_input:
        # Clean the input - remove spaces and convert to uppercase
        plate = plate_input.replace(" ", "").replace("-", "").upper()
        
        with st.spinner(f"Gegevens ophalen voor {plate}..."):
            vehicle = fetch_vehicle_data(plate)
            fuel = fetch_fuel_data(plate)

        if vehicle or fuel:
            st.success(f"✅ Gegevens gevonden voor kenteken **{plate}**")
            
            # Vehicle Information
            if vehicle:
                st.markdown('<div class="info-section">', unsafe_allow_html=True)
                st.markdown("### 🚗 Algemene Voertuiggegevens")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Kenteken:** {vehicle.get('kenteken', 'N/A')}")
                    st.write(f"**Merk:** {vehicle.get('merk', 'N/A')}")
                    st.write(f"**Model:** {vehicle.get('handelsbenaming', 'N/A')}")
                    st.write(f"**Voertuigsoort:** {vehicle.get('voertuigsoort', 'N/A')}")
                    st.write(f"**Kleur:** {vehicle.get('eerste_kleur', 'N/A')}")
                
                with col2:
                    st.write(f"**Eerste toelating:** {format_date(vehicle.get('datum_eerste_toelating'))}")
                    st.write(f"**APK vervaldatum:** {format_date(vehicle.get('vervaldatum_apk'))}")
                    st.write(f"**Aantal zitplaatsen:** {format_value(vehicle.get('aantal_zitplaatsen'))}")
                    st.write(f"**Aantal deuren:** {format_value(vehicle.get('aantal_deuren'))}")
                    st.write(f"**Carrosserie:** {vehicle.get('inrichting', 'N/A')}")
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Technical Information
                st.markdown('<div class="info-section">', unsafe_allow_html=True)
                st.markdown("### ⚙️ Technische Gegevens")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Massa leeg:** {format_value(vehicle.get('massa_ledig_voertuig'), 'kg')}")
                    st.write(f"**Massa rijklaar:** {format_value(vehicle.get('massa_rijklaar'), 'kg')}")
                    st.write(f"**Max. massa:** {format_value(vehicle.get('toegestane_maximum_massa_voertuig'), 'kg')}")
                
                with col2:
                    st.write(f"**Aantal wielen:** {format_value(vehicle.get('aantal_wielen'))}")
                    st.write(f"**Aantal assen:** {format_value(vehicle.get('aantal_assen'))}")
                    st.write(f"**Cilinder inhoud:** {format_value(vehicle.get('cilinderinhoud'), 'cm³')}")
                
                st.markdown('</div>', unsafe_allow_html=True)

            # Fuel Information
            if fuel:
                st.markdown('<div class="info-section">', unsafe_allow_html=True)
                st.markdown("### ⛽ Brandstof & Emissies")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Brandstof:** {fuel.get('brandstof_omschrijving', 'N/A')}")
                    st.write(f"**CO₂ uitstoot:** {format_value(fuel.get('co2_uitstoot_gecombineerd'), 'g/km')}")
                    st.write(f"**Brandstofverbruik:** {format_value(fuel.get('brandstofverbruik_gecombineerd'), 'l/100km')}")
                
                with col2:
                    electric_range = fuel.get('actieradius_elektrisch')
                    if electric_range and electric_range != '0':
                        st.write(f"**Elektrische actieradius:** {electric_range} km")
                    else:
                        st.write(f"**Elektrische actieradius:** Niet van toepassing")
                    
                    energy_label = fuel.get('energielabel')
                    if energy_label:
                        st.write(f"**Energielabel:** {energy_label}")
                
                st.markdown('</div>', unsafe_allow_html=True)

        else:
            st.error(f"❌ Geen gegevens gevonden voor kenteken **{plate}**")
            st.info("Controleer of het kenteken correct is ingevoerd.")

    else:
        st.error("⚠️ Voer een kenteken in om te zoeken.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <small>Gegevens van RDW Open Data</small>
</div>
""", unsafe_allow_html=True)

