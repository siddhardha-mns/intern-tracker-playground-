import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

# Constants
DATA_FOLDER = "data"
HISTORY_FOLDER = "history"
TECH_LEADS = [
    "nikhil", "Edla Divyansh Teja", "GANNARAM DHRUV",
    "Satwik Rakhelkar", "Gadagoju Srikar", "Hasini Parre", "Shiva Kumar ambotu",
    "Puneeth Peela", "Ch.Bhuvana Sri", "Guni Sreepranav", "Sai Kartikeyan Koduri",
    "Sudheer Kumar"
]

# Use secret for Super Admin password
SUPER_ADMIN_PASSWORD = st.secrets.get("SUPER_ADMIN_PASSWORD", "")

# Ensure folders exist
os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(HISTORY_FOLDER, exist_ok=True)

# Session State for Login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.tech_lead = None
    st.session_state.is_super_admin = False

if not st.session_state.logged_in:
    st.title("Tech Lead Login")
    tab1, tab2 = st.tabs(["Tech Lead Login", "Super Admin"])

    with tab1:
        username = st.text_input("Enter your full name")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username in TECH_LEADS and password == st.secrets.get(username, ""):
                st.session_state.logged_in = True
                st.session_state.tech_lead = username
                st.session_state.is_super_admin = False
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        st.subheader("Super Admin Access")
        super_admin_password = st.text_input("Super Admin Password", type="password", key="super_admin_pass")
        if st.button("Super Admin Login"):
            if super_admin_password == SUPER_ADMIN_PASSWORD:
                st.session_state.logged_in = True
                st.session_state.tech_lead = "Super Admin"
                st.session_state.is_super_admin = True
                st.success("Super Admin login successful!")
                st.rerun()
            else:
                st.error("Invalid super admin password")

    st.stop()

# Define current lead and admin status
tech_lead = st.session_state.tech_lead
is_super_admin = st.session_state.is_super_admin

def load_lead_data(lead_name):
    file_path = os.path.join(DATA_FOLDER, f"{lead_name.replace(' ', '_')}.csv")
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return pd.DataFrame()

def display_summary_stats(data):
    total_interns = len(data)
    offer_letters = len(data[data['Received Offer letter'] == 'Yes'])
    cohort1 = len(data[data['Cohort'] == 'Cohort 1'])
    cohort2 = len(data[data['Cohort'] == 'Cohort 2'])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Interns", total_interns)
    col2.metric("Cohort 1", cohort1)
    col3.metric("Cohort 2", cohort2)
    col4.metric("Offer Letters", offer_letters)

# Sidebar navigation
if is_super_admin:
    st.sidebar.title("Super Admin Dashboard")
    page = st.sidebar.selectbox("Navigate to:", [
        "All Tech Leads Overview",
        "Download All Reports",
        "Progress Tracking"
    ])
else:
    st.sidebar.title(f"Welcome, {tech_lead}")
    page = st.sidebar.selectbox("Navigate to:", [
        "Add/Update Intern",
        "View All Interns",
        "Edit Intern",
        "Delete Intern",
        "Change History"
    ])

# Load current data
data_file = os.path.join(DATA_FOLDER, f"{tech_lead.replace(' ', '_')}.csv")
if not is_super_admin:
    df = pd.read_csv(data_file) if os.path.exists(data_file) else pd.DataFrame()

# Admin Pages
if is_super_admin:
    if page == "All Tech Leads Overview":
        st.title("All Tech Leads Overview")
        all_data = []
        stats = {}
        for lead in TECH_LEADS:
            df = load_lead_data(lead)
            if not df.empty:
                df["Tech Lead"] = lead
                all_data.append(df)
                stats[lead] = {
                    "Total": len(df),
                    "Cohort 1": len(df[df["Cohort"] == "Cohort 1"]),
                    "Cohort 2": len(df[df["Cohort"] == "Cohort 2"]),
                    "Offer Letters": len(df[df["Received Offer letter"] == "Yes"])
                }
        if all_data:
            all_combined = pd.concat(all_data, ignore_index=True)
            st.dataframe(pd.DataFrame(stats).T)
            display_summary_stats(all_combined)

            # Filtering
            filter_college = st.text_input("Filter by College")
            filter_year = st.selectbox("Filter by Year", ["All", "1", "2", "3", "4"])

            if filter_college:
                all_combined = all_combined[all_combined['College'].str.contains(filter_college, case=False)]
            if filter_year != "All":
                all_combined = all_combined[all_combined['Year'] == filter_year]

            st.dataframe(all_combined)

        else:
            st.info("No data found.")

    elif page == "Download All Reports":
        st.title("Download Reports")
        all_data = []
        for lead in TECH_LEADS:
            df = load_lead_data(lead)
            if not df.empty:
                df["Tech Lead"] = lead
                all_data.append(df)
        if all_data:
            all_combined = pd.concat(all_data, ignore_index=True)
            st.download_button("Download All", all_combined.to_csv(index=False), "all_tech_leads.csv")
            st.dataframe(all_combined.head(10))

    elif page == "Progress Tracking":
        st.title("Progress Tracking")
        all_data = []
        for lead in TECH_LEADS:
            df = load_lead_data(lead)
            if not df.empty:
                df["Tech Lead"] = lead
                all_data.append(df)
        if all_data:
            combined = pd.concat(all_data, ignore_index=True)
            total = len(combined)
            gl = combined['GitLab Acc (README.md)'].notna().sum()
            st_app = combined['Streamlit app and Deployment'].notna().sum()
            hf = combined['Huggingface+streamlit integration'].notna().sum()
            dc = (combined['Data Collection (started?)'] == 'Yes').sum()

            st.metric("GitLab", f"{gl}/{total}")
            st.metric("Streamlit", f"{st_app}/{total}")
            st.metric("HF Integration", f"{hf}/{total}")
            st.metric("Data Collection", f"{dc}/{total}")

# Tech Lead Intern Management
else:
    if page == "View All Interns":
        st.title("All Interns")

        filter_college = st.text_input("Filter by College")
        filter_year = st.selectbox("Filter by Year", ["All", "1", "2", "3", "4"])

        filtered_df = df.copy()
        if filter_college:
            filtered_df = filtered_df[filtered_df['College'].str.contains(filter_college, case=False)]
        if filter_year != "All":
            filtered_df = filtered_df[filtered_df['Year'] == filter_year]

        st.dataframe(filtered_df)
        display_summary_stats(filtered_df)

    elif page == "Change History":
        st.title("Change History")
        history_file = os.path.join(HISTORY_FOLDER, f"{tech_lead.replace(' ', '_')}_history.json")
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                history = json.load(f)
            for entry in reversed(history):
                st.json(entry)
        else:
            st.info("No history found.")

    else:
        exec(open("tech_lead_pages.py").read())

# Export individual data
if not is_super_admin:
    st.sidebar.download_button("Export My Interns", df.to_csv(index=False), f"{tech_lead.replace(' ', '_')}_interns.csv")

# Logout
st.sidebar.markdown("---")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.tech_lead = None
    st.session_state.is_super_admin = False
    st.rerun()
