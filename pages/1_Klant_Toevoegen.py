import streamlit as st
from supabase import create_client, Client

# Connect to Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.title("👤 Klant Toevoegen")

with st.form("user_form"):
    name = st.text_input("Voer de naam van de klant in")
    email = st.text_input("E-mail")
    plate = st.text_input("Kenteken", placeholder="Bijv. GGX11S")

    submitted = st.form_submit_button("Toevoegen")
    if submitted:
        if not name or not email or not plate:
            st.error("❗Alle velden zijn verplicht.")
        else:
            # Insert into Supabase
            response = supabase.table("clients").insert({
                "name": name,
                "email": email,
                "license_plate": plate
            }).execute()

            if response.error:
                st.error(f"❌ Fout bij opslaan: {response.error.message}")
            else:
                st.success(f"✅ Klant {name} met kenteken {plate} toegevoegd!")



