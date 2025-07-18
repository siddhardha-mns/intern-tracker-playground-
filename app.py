import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# --- Supabase Setup ---
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]
sb: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Auth State ---
if "user" not in st.session_state:
    st.session_state.user = None

def show_auth():
    st.title("Intern Tracker Login / Register")
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            try:
                res = sb.auth.sign_in_with_password({"email": email, "password": password})
                user = res.user
                if user:
                    st.session_state.user = user
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
            except Exception as e:
                st.error(f"Login failed: {e}")
    with tab2:
        name = st.text_input("Full Name", key="reg_name")
        email = st.text_input("Email", key="reg_email")
        password = st.text_input("Password", type="password", key="reg_password")
        college = st.text_input("College Name", key="reg_college")
        if st.button("Register"):
            try:
                res = sb.auth.sign_up({"email": email, "password": password})
                user = res.user
                if user:
                    sb.table("interns").insert({
                        "id": user.id,
                        "name": name,
                        "email": email,
                        "college": college,
                        "created_at": datetime.now().isoformat()
                    }).execute()
                    st.success("Registration successful! Please login.")
                else:
                    st.error("Registration failed.")
            except Exception as e:
                st.error(f"Registration failed: {e}")

if not st.session_state.user:
    show_auth()
    st.stop()

user = st.session_state.user

# --- Supabase Intern Data Functions ---
def load_interns():
    res = sb.table("interns").select("*").eq("email", user.email).execute()
    return pd.DataFrame(res.data) if res.data else pd.DataFrame()

def save_intern(data):
    res = sb.table("interns").select("id").eq("email", data["email"]).execute()
    if res.data:
        intern_id = res.data[0]["id"]
        sb.table("interns").update(data).eq("id", intern_id).execute()
    else:
        sb.table("interns").insert(data).execute()

# --- Main App Logic ---
df = load_interns()

# --- Intern Profile Section ---
st.title("Your Intern Profile")
if not df.empty:
    intern_data = df.iloc[0].to_dict()
else:
    intern_data = {"name": user.user_metadata.get("name", ""), "email": user.email, "college": ""}
with st.form("intern_form"):
    name = st.text_input("Name", value=intern_data.get("name", ""), disabled=True)
    email = st.text_input("Email", value=intern_data.get("email", ""), disabled=True)
    college = st.text_input("College", value=intern_data.get("college", ""))
    submitted = st.form_submit_button("Save")
    if submitted:
        save_intern({"name": name, "email": email, "college": college, "updated_at": datetime.now().isoformat()})
        st.success("Profile saved!")
        st.rerun()

# --- Progress Section (for this intern only) ---
st.header("Your Progress")
progress = intern_data.get("progress", "")
progress_update = st.text_area("Update your progress:", value=progress)
if st.button("Save Progress"):
    save_intern({**intern_data, "progress": progress_update, "updated_at": datetime.now().isoformat()})
    st.success("Progress updated!")
    st.rerun()

# --- History Section (for this intern only) ---
st.header("Your Change History")
history_res = sb.table("history").select("*").eq("email", user.email).order("timestamp", desc=True).execute()
history_df = pd.DataFrame(history_res.data) if history_res.data else pd.DataFrame()
if not history_df.empty:
    for _, row in history_df.iterrows():
        with st.expander(f"{row['timestamp']} - {row['action']}"):
            st.write(row.get("details", ""))
else:
    st.info("No history found.")

# --- Download CSV Section (for this intern only) ---
st.header("Download Your Data")
st.download_button(
    "Download My CSV", 
    pd.DataFrame([intern_data]).to_csv(index=False), 
    file_name=f"{user.email.replace('@', '_').replace('.', '_')}_profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
)
