import streamlit as st

st.title("👤 Gebruiker Toevoegen")

with st.form("user_form"):
    name = st.text_input("Naam")
    email = st.text_input("E-mail")
    plate = st.text_input("Kenteken", placeholder="Bijv. GGX11S")

    submitted = st.form_submit_button("Toevoegen")
    if submitted:
        st.success(f"Gebruiker {name} met kenteken {plate} toegevoegd!")
        # Optional: Save to database or file here
