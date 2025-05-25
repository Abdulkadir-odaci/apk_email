import streamlit as st

st.title("👤 Klant Toevoegen")

with st.form("user_form"):
    name = st.text_input("Voer de naam van de klant in")
    email = st.text_input("E-mail")
    plate = st.text_input("Kenteken", placeholder="Bijv. GGX11S")

    submitted = st.form_submit_button("Toevoegen")
    if submitted:
        st.success(f"Klant {name} met kenteken {plate} toegevoegd!")
        # Optional: Save to database or file here


