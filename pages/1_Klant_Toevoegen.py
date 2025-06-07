import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime
import re
import hashlib

# Initialize Supabase client
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
    return supabase

class AuthManager:
    def __init__(self):
        self.supabase = init_supabase()
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username, password, email):
        """Register a new user"""
        try:
            # Check if username already exists
            existing = self.supabase.table('users').select('id').eq('username', username).execute()
            if existing.data:
                return False, "Gebruikersnaam bestaat al!"
            
            # Check if email already exists
            existing_email = self.supabase.table('users').select('id').eq('email', email).execute()
            if existing_email.data:
                return False, "E-mail bestaat al!"
            
            result = self.supabase.table('users').insert({
                'username': username,
                'password_hash': self.hash_password(password),
                'email': email
            }).execute()
            return True, "Account succesvol aangemaakt!"
        except Exception as e:
            return False, f"Fout bij aanmaken account: {e}"
    
    def login_user(self, username, password):
        """Login user"""
        try:
            result = self.supabase.table('users').select('id, username, email').eq(
                'username', username
            ).eq('password_hash', self.hash_password(password)).execute()
            
            if result.data:
                return True, result.data[0]
            return False, "Ongeldige gebruikersnaam of wachtwoord!"
        except Exception as e:
            return False, f"Inlogfout: {e}"

class ClientDB:
    def __init__(self):
        self.supabase = init_supabase()
    
    def add_client(self, name, email, licence_plate, user_id):
        """Add a new client for specific user"""
        try:
            result = self.supabase.table('client').insert({
                'name': name,
                'email': email,
                'licence_plate': licence_plate.upper(),
                'user_id': user_id
            }).execute()
            return True, "Klant succesvol toegevoegd!"
        except Exception as e:
            error_msg = str(e)
            if "duplicate key" in error_msg.lower():
                return False, "E-mail of kenteken bestaat al!"
            return False, f"Fout bij toevoegen klant: {error_msg}"
    
    def get_user_clients(self, user_id):
        """Get all clients for specific user only"""
        try:
            result = self.supabase.table('client').select(
                'id, name, email, licence_plate, created_at'
            ).eq('user_id', user_id).order('created_at', desc=True).execute()
            return result.data
        except Exception as e:
            st.error(f"Fout bij ophalen klanten: {e}")
            return []
    
    def search_user_clients(self, search_term, user_id):
        """Search clients by name, email, or licence plate for specific user only"""
        try:
            result = self.supabase.table('client').select(
                'id, name, email, licence_plate, created_at'
            ).eq('user_id', user_id).or_(
                f"name.ilike.%{search_term}%,"
                f"email.ilike.%{search_term}%,"
                f"licence_plate.ilike.%{search_term}%"
            ).execute()
            return result.data
        except Exception as e:
            st.error(f"Fout bij zoeken klanten: {e}")
            return []
    
    def update_client(self, client_id, name, email, licence_plate, user_id):
        """Update client information (only if belongs to user)"""
        try:
            result = self.supabase.table('client').update({
                'name': name,
                'email': email,
                'licence_plate': licence_plate.upper()
            }).eq('id', client_id).eq('user_id', user_id).execute()
            return True, "Klant succesvol bijgewerkt!"
        except Exception as e:
            return False, f"Fout bij bijwerken klant: {e}"
    
    def delete_client(self, client_id, user_id):
        """Delete a client (only if belongs to user)"""
        try:
            result = self.supabase.table('client').delete().eq('id', client_id).eq('user_id', user_id).execute()
            return True, "Klant succesvol verwijderd!"
        except Exception as e:
            return False, f"Fout bij verwijderen klant: {e}"

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_licence_plate(plate):
    """Basic licence plate validation"""
    if len(plate.strip()) < 2:
        return False
    return True

def show_login_page():
    """Display login/register page"""
    st.title("🚗 Klant Kenteken Beheer")
    st.markdown("---")
    
    auth = AuthManager()
    
    # Check for auto-login from saved credentials
    if 'remembered_credentials' in st.session_state:
        creds = st.session_state.remembered_credentials
        success, result = auth.login_user(creds['username'], creds['password'])
        if success:
            st.session_state.logged_in = True
            st.session_state.user_info = result
            st.success("Automatisch ingelogd!")
            st.rerun()
        else:
            # Remove invalid saved credentials
            del st.session_state.remembered_credentials
    
    tab1, tab2 = st.tabs(["Inloggen", "Registreren"])
    
    with tab1:
        st.header("Inloggen")
        
        # Get saved credentials if available
        saved_username = st.session_state.get('saved_username', '')
        saved_password = st.session_state.get('saved_password', '')
        
        with st.form("login_form"):
            username = st.text_input("Gebruikersnaam", value=saved_username)
            password = st.text_input("Wachtwoord", type="password", value=saved_password)
            remember_me = st.checkbox("Onthoud mijn gegevens", value=bool(saved_username))
            login_submit = st.form_submit_button("Inloggen", type="primary")
            
            if login_submit:
                if username and password:
                    success, result = auth.login_user(username, password)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.user_info = result
                        
                        # Handle remember me functionality
                        if remember_me:
                            st.session_state.saved_username = username
                            st.session_state.saved_password = password
                            st.session_state.remembered_credentials = {
                                'username': username,
                                'password': password
                            }
                        else:
                            # Clear saved credentials if remember me is not checked
                            st.session_state.pop('saved_username', None)
                            st.session_state.pop('saved_password', None)
                            st.session_state.pop('remembered_credentials', None)
                        
                        st.success("Succesvol ingelogd!")
                        st.rerun()
                    else:
                        st.error(result)
                else:
                    st.error("Vul alle velden in!")
        
        # Clear saved credentials button
        if saved_username:
            if st.button("🗑️ Vergeet opgeslagen gegevens"):
                st.session_state.pop('saved_username', None)
                st.session_state.pop('saved_password', None)
                st.session_state.pop('remembered_credentials', None)
                st.success("Opgeslagen gegevens gewist!")
                st.rerun()
    
    with tab2:
        st.header("Nieuw Account Aanmaken")
        with st.form("register_form"):
            new_username = st.text_input("Nieuwe Gebruikersnaam")
            new_email = st.text_input("E-mail Adres")
            new_password = st.text_input("Wachtwoord", type="password")
            confirm_password = st.text_input("Bevestig Wachtwoord", type="password")
            register_submit = st.form_submit_button("Account Aanmaken", type="primary")
            
            if register_submit:
                errors = []
                
                if not new_username.strip():
                    errors.append("Gebruikersnaam is vereist")
                elif len(new_username.strip()) < 3:
                    errors.append("Gebruikersnaam moet minimaal 3 karakters zijn")
                
                if not new_email.strip():
                    errors.append("E-mail is vereist")
                elif not validate_email(new_email.strip()):
                    errors.append("Voer een geldig e-mailadres in")
                
                if not new_password:
                    errors.append("Wachtwoord is vereist")
                elif len(new_password) < 6:
                    errors.append("Wachtwoord moet minimaal 6 karakters zijn")
                
                if new_password != confirm_password:
                    errors.append("Wachtwoorden komen niet overeen")
                
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    success, message = auth.register_user(new_username.strip(), new_password, new_email.strip().lower())
                    if success:
                        st.success(message)
                    else:
                        st.error(message)

def main():
    st.set_page_config(
        page_title="Klant Kenteken Beheer",
        page_icon="🚗",
        layout="wide"
    )
    
    # Check if user is logged in
    if not st.session_state.get('logged_in', False):
        show_login_page()
        return
    
    # User is logged in, show main application
    st.title("🚗 Klant Kenteken Beheer")
    
    # Sidebar with user info and logout
    st.sidebar.title("Welkom!")
    st.sidebar.info(f"Ingelogd als: **{st.session_state.user_info['username']}**")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("Uitloggen"):
            # Keep credentials if they were saved
            keep_credentials = st.session_state.get('remembered_credentials') is not None
            if keep_credentials:
                saved_username = st.session_state.get('saved_username')
                saved_password = st.session_state.get('saved_password')
                remembered_creds = st.session_state.get('remembered_credentials')
            
            st.session_state.clear()
            
            # Restore saved credentials if they existed
            if keep_credentials:
                st.session_state.saved_username = saved_username
                st.session_state.saved_password = saved_password
                st.session_state.remembered_credentials = remembered_creds
            
            st.rerun()
    
    with col2:
        if st.button("Vergeet mij"):
            if st.session_state.get('confirm_forget'):
                # Clear everything including saved credentials
                st.session_state.clear()
                st.success("Alle gegevens gewist!")
                st.rerun()
            else:
                st.session_state.confirm_forget = True
                st.warning("Klik nogmaals om te bevestigen")
    
    st.sidebar.markdown("---")
    
    # Initialize database
    db = ClientDB()
    
    # Navigation
    st.sidebar.title("Navigatie")
    page = st.sidebar.selectbox(
        "Kies een optie",
        ["Nieuwe Klant Toevoegen", "Alle Klanten Bekijken", "Klanten Zoeken", "Klanten Beheren"]
    )
    
    user_id = st.session_state.user_info['id']
    
    if page == "Nieuwe Klant Toevoegen":
        show_add_client(db, user_id)
    elif page == "Alle Klanten Bekijken":
        show_all_clients(db, user_id)
    elif page == "Klanten Zoeken":
        show_search_clients(db, user_id)
    elif page == "Klanten Beheren":
        show_manage_clients(db, user_id)

def show_add_client(db, user_id):
    """Display form to add new client"""
    st.header("Nieuwe Klant Toevoegen")
    
    with st.form("client_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input(
                "Klant Naam *",
                placeholder="Jan Jansen",
                help="Volledige naam van de klant"
            )
            email = st.text_input(
                "E-mail Adres *",
                placeholder="jan.jansen@email.com",
                help="Geldig e-mailadres"
            )
        
        with col2:
            licence_plate = st.text_input(
                "Kenteken *",
                placeholder="AB-123-C",
                help="Voertuig kenteken"
            )
            st.empty()
        
        submit = st.form_submit_button("Klant Toevoegen", type="primary")
        
        if submit:
            errors = []
            
            if not name.strip():
                errors.append("Naam is vereist")
            
            if not email.strip():
                errors.append("E-mail is vereist")
            elif not validate_email(email.strip()):
                errors.append("Voer een geldig e-mailadres in")
            
            if not licence_plate.strip():
                errors.append("Kenteken is vereist")
            elif not validate_licence_plate(licence_plate.strip()):
                errors.append("Voer een geldig kenteken in")
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                success, message = db.add_client(
                    name.strip(),
                    email.strip().lower(),
                    licence_plate.strip(),
                    user_id
                )
                
                if success:
                    st.success(message)
                else:
                    st.error(message)

def show_all_clients(db, user_id):
    """Display all clients for current user"""
    st.header("Alle Klanten")
    
    clients = db.get_user_clients(user_id)
    
    if clients:
        df = pd.DataFrame(clients)
        df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
        
        df_display = df.rename(columns={
            'name': 'Naam',
            'email': 'E-mail',
            'licence_plate': 'Kenteken',
            'created_at': 'Toegevoegd op'
        })
        
        st.dataframe(
            df_display[['Naam', 'E-mail', 'Kenteken', 'Toegevoegd op']],
            use_container_width=True,
            hide_index=True
        )
        
        # Statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Totaal Klanten", len(clients))
        with col2:
            st.metric("Vandaag Toegevoegd", 
                     len([c for c in clients if c['created_at'][:10] == datetime.now().strftime('%Y-%m-%d')]))
        with col3:
            st.metric("Deze Maand", 
                     len([c for c in clients if c['created_at'][:7] == datetime.now().strftime('%Y-%m')]))
        
        # Download option
        csv = df_display.to_csv(index=False)
        st.download_button(
            label="📥 Download als CSV",
            data=csv,
            file_name=f"klanten_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("Geen klanten gevonden. Voeg je eerste klant toe via 'Nieuwe Klant Toevoegen'.")

def show_search_clients(db, user_id):
    """Display search functionality"""
    st.header("Klanten Zoeken")
    
    search_term = st.text_input(
        "Zoek op naam, e-mail of kenteken",
        placeholder="Voer zoekterm in...",
        help="Zoeken is niet hoofdlettergevoelig en zoekt gedeeltelijke tekst"
    )
    
    if search_term:
        clients = db.search_user_clients(search_term, user_id)
        
        if clients:
            st.success(f"{len(clients)} klant(en) gevonden")
            
            df = pd.DataFrame(clients)
            df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
            
            df_display = df.rename(columns={
                'name': 'Naam',
                'email': 'E-mail',
                'licence_plate': 'Kenteken',
                'created_at': 'Toegevoegd op'
            })
            
            st.dataframe(
                df_display[['Naam', 'E-mail', 'Kenteken', 'Toegevoegd op']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("Geen klanten gevonden die overeenkomen met je zoekterm.")

def show_manage_clients(db, user_id):
    """Display client management interface"""
    st.header("Klanten Beheren")
    
    clients = db.get_user_clients(user_id)
    
    if not clients:
        st.info("Geen klanten om te beheren. Voeg eerst klanten toe.")
        return
    
    client_options = {f"{c['name']} ({c['email']})": c for c in clients}
    selected_client_key = st.selectbox("Selecteer een klant om te beheren:", list(client_options.keys()))
    
    if selected_client_key:
        selected_client = client_options[selected_client_key]
        
        st.subheader("Klant Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**Naam:** {selected_client['name']}")
            st.info(f"**E-mail:** {selected_client['email']}")
        
        with col2:
            st.info(f"**Kenteken:** {selected_client['licence_plate']}")
            st.info(f"**Toegevoegd:** {pd.to_datetime(selected_client['created_at']).strftime('%Y-%m-%d %H:%M')}")
        
        st.subheader("Acties")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✏️ Klant Bewerken", type="secondary"):
                st.session_state.editing_client = selected_client['id']
        
        with col2:
            if st.button("🗑️ Klant Verwijderen", type="secondary"):
                if st.session_state.get('confirm_delete') == selected_client['id']:
                    success, message = db.delete_client(selected_client['id'], user_id)
                    if success:
                        st.success(message)
                        st.session_state.pop('confirm_delete', None)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.session_state.confirm_delete = selected_client['id']
                    st.warning("Klik nogmaals om verwijdering te bevestigen")
        
        # Edit form
        if st.session_state.get('editing_client') == selected_client['id']:
            st.subheader("Klant Bewerken")
            
            with st.form("edit_client_form"):
                new_name = st.text_input("Naam", value=selected_client['name'])
                new_email = st.text_input("E-mail", value=selected_client['email'])
                new_licence_plate = st.text_input("Kenteken", value=selected_client['licence_plate'])
                
                col1, col2 = st.columns(2)
                with col1:
                    update_submit = st.form_submit_button("Klant Bijwerken", type="primary")
                with col2:
                    cancel_submit = st.form_submit_button("Annuleren")
                
                if update_submit:
                    if new_name.strip() and new_email.strip() and new_licence_plate.strip():
                        if validate_email(new_email.strip()):
                            success, message = db.update_client(
                                selected_client['id'],
                                new_name.strip(),
                                new_email.strip().lower(),
                                new_licence_plate.strip(),
                                user_id
                            )
                            if success:
                                st.success(message)
                                st.session_state.pop('editing_client', None)
                                st.rerun()
                            else:
                                st.error(message)
                        else:
                            st.error("Voer een geldig e-mailadres in")
                    else:
                        st.error("Alle velden zijn vereist")
                
                if cancel_submit:
                    st.session_state.pop('editing_client', None)
                    st.rerun()

if __name__ == "__main__":
    main()




