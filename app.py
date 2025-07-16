import streamlit as st
import pandas as pd
import os
from datetime import datetime
import json

# Constants
DATA_FOLDER = "data"
HISTORY_FOLDER = "history"
TEAM_FOLDER = "teams"
TECH_LEADS = [
    "nikhil", "Edla Divyansh Teja", "GANNARAM DHRUV",
    "Satwik Rakhelkar", "Gadagoju Srikar", "Hasini Parre", "Shiva Kumar ambotu",
    "Puneeth Peela", "Ch.Bhuvana Sri", "Guni Sreepranav", "Sai Kartikeyan Koduri",
    "Sudheer Kumar"
]

# Add this near the top, after TECH_LEADS
TEAM_NUMBERS = {
    "Satwik Rakhelkar": "1",
    "Gadagoju Srikar": "2",
    "Puneeth Peela": "3",
    "Shiva Kumar ambotu": "4",
    "nikhil": "5",
    "Sai Kartikeyan Koduri": "6",
    "Guni Sreepranav": "7",
    "Hasini Parre": "8",
    "Ch.Bhuvana Sri": "9",
    "GANNARAM DHRUV": "10",
    "Edla Divyansh Teja": "11",
    "Sudheer Kumar": "12"
}

# Ensure folders exist
os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(HISTORY_FOLDER, exist_ok=True)
os.makedirs(TEAM_FOLDER, exist_ok=True)

# Auth system using Streamlit secrets
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.tech_lead = None
    st.session_state.is_super_admin = False

if not st.session_state.logged_in:
    st.title("Tech Lead Login")
    
    # Super Admin Login Section
    st.markdown("---")
    st.subheader("Super Admin Panel")
    super_admin_username = st.text_input("Super Admin Username")
    super_admin_password = st.text_input("Super Admin Password", type="password")
    
    if st.button("Super Admin Login"):
        if super_admin_username == "admin" and super_admin_password == st.secrets.get("admin_password", "admin123"):
            st.session_state.logged_in = True
            st.session_state.tech_lead = "Super Admin"
            st.session_state.is_super_admin = True
            st.success("Super Admin login successful!")
            st.rerun()
        else:
            st.error("Invalid super admin credentials")
    
    st.markdown("---")
    st.subheader("Tech Lead Login")
    username = st.text_input("Enter your full name")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in TECH_LEADS and st.secrets["tech_leads"].get(username, "") == password:
            st.session_state.logged_in = True
            st.session_state.tech_lead = username
            st.session_state.is_super_admin = False
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid credentials")
    st.stop()

tech_lead = st.session_state.tech_lead
is_super_admin = st.session_state.is_super_admin

# File paths
data_file = os.path.join(DATA_FOLDER, f"{tech_lead.replace(' ', '_')}.csv")
history_file = os.path.join(HISTORY_FOLDER, f"{tech_lead.replace(' ', '_')}_history.csv")

# Load data
def load_data():
    if os.path.exists(data_file):
        return pd.read_csv(data_file)
    else:
        return pd.DataFrame(columns=[
            "Name", "Cohort", "Team(eg :2 or 3)", "GitLab User Name", "Year", "Received Offer letter", "College",
            "GitLab Acc (README.md)", "GitLab Acc Link",
            "Innings Courses (Python & AI)", "Huggingchat/Dify", "Huggingchat Link",
            "Streamlit app and Deployment", "Streamlit Link",
            "Huggingface+streamlit integration", "HF+Streamlit Link",
            "Pushed Apps onto GitLab", "Data Collection (started?)", "Size of Data",
            "Can go to any other places", "Blockers?", "Remarks", "Active"
        ])

# Save history function
def save_history(intern_name, action, old_data="", new_data="", changed_fields=None):
    change_time = datetime.now().isoformat()
    history_entry = {
        "Time": change_time, 
        "Intern": intern_name, 
        "Action": action, 
        "Old": str(old_data), 
        "New": str(new_data),
        "Changed_Fields": json.dumps(changed_fields) if changed_fields else ""
    }
    
    # Load existing history or create new
    if os.path.exists(history_file):
        hist_df = pd.read_csv(history_file)
        hist_df = pd.concat([hist_df, pd.DataFrame([history_entry])], ignore_index=True)
    else:
        hist_df = pd.DataFrame([history_entry])
    
    hist_df.to_csv(history_file, index=False)

# Team management functions
def load_teams():
    """Load teams for the current tech lead"""
    team_file = os.path.join(TEAM_FOLDER, f"{tech_lead.replace(' ', '_')}_teams.json")
    st.write("[DEBUG] Loading teams from:", team_file)
    if os.path.exists(team_file):
        with open(team_file, 'r') as f:
            return json.load(f)
    return {}

def save_teams(teams):
    """Save teams for the current tech lead"""
    team_file = os.path.join(TEAM_FOLDER, f"{tech_lead.replace(' ', '_')}_teams.json")
    st.write("[DEBUG] Saving teams to:", team_file)
    with open(team_file, 'w') as f:
        json.dump(teams, f, indent=2)

def get_available_interns():
    """Get list of interns available for team creation"""
    if df.empty:
        return []
    return df["Name"].tolist()

# Navigation sidebar
st.sidebar.title(f"Welcome, {tech_lead}")

# Logout button
if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.session_state.tech_lead = None
    st.session_state.is_super_admin = False
    st.rerun()

# Super Admin Panel
if is_super_admin:
    st.title("Super Admin Panel")
    st.subheader("All Tech Lead Reports")
    
    # Team selection for super admin
    st.subheader("👥 Team Selection")
    team_filter_text = st.text_input(
        "Enter team names to filter (comma-separated, e.g., 'Team A, Team B' or leave empty for all teams):"
    )
    
    # Parse team filter
    selected_teams = []
    if team_filter_text:
        selected_teams = [team.strip() for team in team_filter_text.split(",") if team.strip()]
    else:
        # If no filter specified, include all teams
        selected_teams = None
    
    # Load all tech lead data
    all_reports = []
    tech_lead_stats = {}
    
    for tech_lead_name in TECH_LEADS:
        tech_lead_file = os.path.join(DATA_FOLDER, f"{tech_lead_name.replace(' ', '_')}.csv")
        if os.path.exists(tech_lead_file):
            tech_df = pd.read_csv(tech_lead_file)
            if not tech_df.empty:
                # Filter by team if team column exists
                if "Team" in tech_df.columns and selected_teams:
                    tech_df = tech_df[tech_df["Team"].isin(selected_teams)]
                
                if not tech_df.empty:
                    all_reports.append(tech_df)
                    tech_lead_stats[tech_lead_name] = {
                        "total_interns": len(tech_df),
                        "cohort_1": len(tech_df[tech_df["Cohort"] == "Cohort 1"]),
                        "cohort_2": len(tech_df[tech_df["Cohort"] == "Cohort 2"]),
                        "offers_received": len(tech_df[tech_df["Received Offer letter"] == "Yes"]),
                        "apps_pushed": len(tech_df[tech_df["Pushed Apps onto GitLab"] == "Yes"]),
                        "data_collection_started": len(tech_df[tech_df["Data Collection (started?)"] == "Yes"])
                    }
    
    # Progress Overview
    st.subheader("📊 Progress Overview")
    if tech_lead_stats:
        col1, col2, col3 = st.columns(3)
        
        total_interns = sum(stats["total_interns"] for stats in tech_lead_stats.values())
        total_offers = sum(stats["offers_received"] for stats in tech_lead_stats.values())
        total_apps = sum(stats["apps_pushed"] for stats in tech_lead_stats.values())
        
        with col1:
            st.metric("Total Interns", total_interns)
        with col2:
            st.metric("Offers Received", total_offers)
        with col3:
            st.metric("Apps Pushed to GitLab", total_apps)
        
        # Tech Lead Performance Table
        st.subheader("👥 Tech Lead Performance")
        performance_data = []
        for tech_lead_name, stats in tech_lead_stats.items():
            performance_data.append({
                "Tech Lead": tech_lead_name,
                "Total Interns": stats["total_interns"],
                "Cohort 1": stats["cohort_1"],
                "Cohort 2": stats["cohort_2"],
                "Offers Received": stats["offers_received"],
                "Apps Pushed": stats["apps_pushed"],
                "Data Collection Started": stats["data_collection_started"]
            })
        
        performance_df = pd.DataFrame(performance_data)
        st.dataframe(performance_df, use_container_width=True)
        
        # Download combined report
        if all_reports:
            combined_df = pd.concat(all_reports, ignore_index=True)
            st.subheader("📥 Download Reports")
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    "📊 Download Combined Report",
                    combined_df.to_csv(index=False),
                    file_name=f"all_tech_leads_combined_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
            with col2:
                # Download individual tech lead reports
                selected_tech_lead = st.selectbox("Download Individual Report:", TECH_LEADS)
                if selected_tech_lead in tech_lead_stats:
                    tech_lead_file = os.path.join(DATA_FOLDER, f"{selected_tech_lead.replace(' ', '_')}.csv")
                    if os.path.exists(tech_lead_file):
                        individual_df = pd.read_csv(tech_lead_file)
                        # Filter by selected teams
                        if "Team" in individual_df.columns and selected_teams:
                            individual_df = individual_df[individual_df["Team"].isin(selected_teams)]
                        st.download_button(
                            f"📄 Download {selected_tech_lead} Report",
                            individual_df.to_csv(index=False),
                            file_name=f"{selected_tech_lead.replace(' ', '_')}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
    else:
        st.info("No tech lead reports found.")
    
    # Cohort Analysis
    st.subheader("📈 Cohort Analysis")
    if all_reports:
        combined_df = pd.concat(all_reports, ignore_index=True)
        
        col1, col2 = st.columns(2)
        with col1:
            cohort_counts = combined_df["Cohort"].value_counts()
            st.write("**Cohort Distribution:**")
            for cohort, count in cohort_counts.items():
                st.write(f"{cohort}: {count} interns")
        
        with col2:
            offer_counts = combined_df["Received Offer letter"].value_counts()
            st.write("**Offer Status:**")
            for status, count in offer_counts.items():
                st.write(f"{status}: {count} interns")
    
    st.stop()

page = st.sidebar.selectbox("Navigate to:", [
    "Add/Update Intern", 
    "View All Interns", 
    "Edit Intern", 
    "Delete Intern", 
    "Change History"
] + (["🚀 Project Teams"] if not is_super_admin else []))

df = load_data()

# Ensure 'Active' column exists in df
if 'Active' not in df.columns:
    df['Active'] = 'Yes'

def safe_is_inactive(df, m):
    df_match = df[df['Name'] == m]
    if not df_match.empty:
        return df_match['Active'].values[0] == 'No'
    return False

# Add/Update Intern
if page == "Add/Update Intern":
    try:
        st.title("Add or Update Intern")
        filtered_df = df # No need to filter by team here, as it's handled by the page selection
        intern_names = ["New"] + filtered_df["Name"].dropna().astype(str).tolist()
        selected_intern = st.selectbox("Select Intern to Update (or leave as 'New' to add):", intern_names)
        if selected_intern != "New" and selected_intern in df["Name"].values:
            intern_data = df[df["Name"] == selected_intern].iloc[0].to_dict()
        else:
            intern_data = {}
        with st.form("intern_form"):
            name = st.text_input("Name", value=intern_data.get("Name", ""))
            cohort = st.selectbox("Cohort", ["Cohort 1", "Cohort 2"], index=["Cohort 1", "Cohort 2"].index(intern_data.get("Cohort", "Cohort 1")) if intern_data.get("Cohort") in ["Cohort 1", "Cohort 2"] else 0)
            if is_super_admin:
                team = st.text_input("Team(eg :2 or 3)", value=intern_data.get("Team(eg :2 or 3)", ""))
            else:
                team = st.text_input("Team(eg :2 or 3)", value=TEAM_NUMBERS.get(tech_lead, ""), disabled=True)
            values = {
                "GitLab User Name": st.text_input("GitLab User Name", value=intern_data.get("GitLab User Name", "")),
                "Year": st.selectbox("Year", ["1", "2", "3", "4"], index=["1", "2", "3", "4"].index(str(intern_data.get("Year", "1"))) if str(intern_data.get("Year", "1")) in ["1", "2", "3", "4"] else 0),
                "Received Offer letter": st.selectbox("Received Offer letter", ["Yes", "No"], index=["Yes", "No"].index(intern_data.get("Received Offer letter", "Yes")) if intern_data.get("Received Offer letter") in ["Yes", "No"] else 0),
                "College": st.text_input("College", value=intern_data.get("College", "")),
                "GitLab Acc (README.md)": st.text_input("GitLab Acc (README.md)", value=intern_data.get("GitLab Acc (README.md)", "")),
                "GitLab Acc Link": st.text_input("GitLab Acc Link", value=intern_data.get("GitLab Acc Link", "")),
                "Innings Courses (Python & AI)": st.text_input("Innings Courses (Python & AI)", value=intern_data.get("Innings Courses (Python & AI)", "")),
                "Huggingchat/Dify": st.text_input("Huggingchat/Dify", value=intern_data.get("Huggingchat/Dify", "")),
                "Huggingchat Link": st.text_input("Huggingchat Link", value=intern_data.get("Huggingchat Link", "")),
                "Streamlit app and Deployment": st.text_input("Streamlit app and Deployment", value=intern_data.get("Streamlit app and Deployment", "")),
                "Streamlit Link": st.text_input("Streamlit Link", value=intern_data.get("Streamlit Link", "")),
                "Huggingface+streamlit integration": st.text_input("Huggingface+streamlit integration", value=intern_data.get("Huggingface+streamlit integration", "")),
                "HF+Streamlit Link": st.text_input("HF+Streamlit Link", value=intern_data.get("HF+Streamlit Link", "")),
                "Pushed Apps onto GitLab": st.selectbox("Pushed Apps onto GitLab", ["Yes", "No"], index=["Yes", "No"].index(intern_data.get("Pushed Apps onto GitLab", "Yes")) if intern_data.get("Pushed Apps onto GitLab") in ["Yes", "No"] else 0),
                "Data Collection (started?)": st.selectbox("Data Collection (started?)", ["Yes", "No"], index=["Yes", "No"].index(intern_data.get("Data Collection (started?)", "Yes")) if intern_data.get("Data Collection (started?)") in ["Yes", "No"] else 0),
                "Size of Data": st.text_input("Size of Data", value=intern_data.get("Size of Data", "")),
                "Can go to any other places": st.text_input("Can go to any other places", value=intern_data.get("Can go to any other places", "")),
                "Blockers?": st.text_area("Blockers?", value=intern_data.get("Blockers?", "")),
                "Remarks": st.text_area("Remarks", value=intern_data.get("Remarks", ""))
            }
            submitted = st.form_submit_button("Save")
            if submitted and name:
                new_row = {"Name": name, "Cohort": cohort, "Team(eg :2 or 3)": team}
                new_row.update(values)
                if 'Team' in new_row:
                    del new_row['Team']
                if name in df["Name"].values:
                    old_row = df[df["Name"] == name].iloc[0].to_dict()
                    for k, v in new_row.items():
                        df.loc[df["Name"] == name, k] = v
                    if 'Team' in df.columns:
                        df = df.drop(columns=['Team'])
                    save_history(name, "Updated", old_row, new_row)
                    st.success("Intern data updated successfully.")
                else:
                    if 'Team' in df.columns:
                        df = df.drop(columns=['Team'])
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    save_history(name, "Added", "", new_row)
                    st.success("Intern added successfully.")
                df.to_csv(data_file, index=False)
    except Exception as e:
        st.error(f"[ERROR] {e}")

# View All Interns
elif page == "View All Interns":
    try:
        st.title("All Interns")
        col1, col2 = st.columns(2)
        with col1:
            cohort_filter = st.selectbox("Select Cohort", ["All", "Cohort 1", "Cohort 2"])
        if is_super_admin:
            with col2:
                team_filter = st.text_input("Filter by Team (leave empty for all)")
        else:
            team_filter = ""
        filtered_df = df # No need to filter by team here, as it's handled by the page selection
        if cohort_filter != "All":
            filtered_df = filtered_df[filtered_df["Cohort"] == cohort_filter]
        if is_super_admin and team_filter and "Team(eg :2 or 3)" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["Team(eg :2 or 3)"].astype(str).str.contains(team_filter, case=False, na=False)]
        if not filtered_df.empty:
            st.dataframe(filtered_df, use_container_width=True)
            st.download_button(
                "Download CSV", 
                filtered_df.to_csv(index=False), 
                file_name=f"{tech_lead.replace(' ', '_')}_interns_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
        else:
            st.info("No interns found.")
    except Exception as e:
        st.error(f"[ERROR] {e}")

# Edit Intern
elif page == "Edit Intern":
    try:
        st.title("Edit Intern")
        filtered_df = df # No need to filter by team here, as it's handled by the page selection
        if filtered_df.empty:
            st.info("No interns to edit.")
        else:
            intern_names = filtered_df["Name"].tolist()
            selected_intern = st.selectbox("Select Intern to Edit", ["None"] + intern_names)
            if selected_intern != "None":
                intern_data = df[df["Name"] == selected_intern].iloc[0].to_dict()
                st.subheader(f"Editing: {selected_intern}")
                with st.form("edit_intern_form"):
                    st.write("Select fields to edit:")
                    fields_to_edit = {}
                    edit_cohort = st.checkbox("Edit Cohort")
                    if edit_cohort:
                        fields_to_edit["Cohort"] = st.selectbox("Cohort", ["Cohort 1", "Cohort 2"], index=0 if intern_data["Cohort"] == "Cohort 1" else 1)
                    # Team number is fixed for tech leads
                    edit_team = st.checkbox("Edit Team") if is_super_admin else False
                    if edit_team:
                        current_team = intern_data.get("Team(eg :2 or 3)", "")
                        fields_to_edit["Team(eg :2 or 3)"] = st.text_input("Team(eg :2 or 3)", value=current_team)
                    # Other fields
                    field_mapping = {
                        "GitLab User Name": "text",
                        "Year": "selectbox",
                        "Received Offer letter": "selectbox",
                        "College": "text",
                        "GitLab Acc (README.md)": "text",
                        "GitLab Acc Link": "text",
                        "Innings Courses (Python & AI)": "text",
                        "Huggingchat/Dify": "text",
                        "Huggingchat Link": "text",
                        "Streamlit app and Deployment": "text",
                        "Streamlit Link": "text",
                        "Huggingface+streamlit integration": "text",
                        "HF+Streamlit Link": "text",
                        "Pushed Apps onto GitLab": "selectbox",
                        "Data Collection (started?)": "selectbox",
                        "Size of Data": "text",
                        "Can go to any other places": "text",
                        "Blockers?": "textarea",
                        "Remarks": "textarea"
                    }
                    for field, input_type in field_mapping.items():
                        edit_field = st.checkbox(f"Edit {field}")
                        if edit_field:
                            current_value = intern_data.get(field, "")
                            if input_type == "text":
                                fields_to_edit[field] = st.text_input(f"{field}", value=current_value)
                            elif input_type == "textarea":
                                fields_to_edit[field] = st.text_area(f"{field}", value=current_value)
                            elif input_type == "selectbox":
                                if field == "Year":
                                    options = ["1", "2", "3", "4"]
                                    index = options.index(current_value) if current_value in options else 0
                                    fields_to_edit[field] = st.selectbox(f"{field}", options, index=index)
                                elif field in ["Received Offer letter", "Pushed Apps onto GitLab", "Data Collection (started?)"]:
                                    options = ["Yes", "No"]
                                    index = options.index(current_value) if current_value in options else 0
                                    fields_to_edit[field] = st.selectbox(f"{field}", options, index=index)
                    # Place the submit buttons INSIDE the form
                    col1, col2 = st.columns(2)
                    with col1:
                        update_submitted = st.form_submit_button("Update Intern")
                    with col2:
                        submit_submitted = st.form_submit_button("Submit Changes")
                    if (update_submitted or submit_submitted) and fields_to_edit:
                        old_data = intern_data.copy()
                        # Update only the selected fields
                        for field, value in fields_to_edit.items():
                            df.loc[df["Name"] == selected_intern, field] = value
                        # Save changes
                        df.to_csv(data_file, index=False)
                        # Save history with changed fields
                        changed_fields = list(fields_to_edit.keys())
                        new_data = df[df["Name"] == selected_intern].iloc[0].to_dict()
                        save_history(selected_intern, "Updated", old_data, new_data, changed_fields)
                        st.success(f"Updated {len(fields_to_edit)} field(s) for {selected_intern}")
                        st.rerun()
    except Exception as e:
        st.error(f"[ERROR] {e}")

# --- Enhanced Delete Intern logic with Inactive status ---
# Ensure 'Active' column exists in df
if 'Active' not in df.columns:
    df['Active'] = 'Yes'

elif page == "Delete Intern":
    try:
        st.title("Delete Intern")
        # Add status filter
        status_options = ["All", "Active", "Inactive", "Academic Break"]
        selected_status = st.selectbox("Filter interns by status:", status_options)
        # Filter the dataframe based on status
        if selected_status != "All":
            filtered_df = df[df["Active"] == ("Yes" if selected_status == "Active" else selected_status)]
        else:
            filtered_df = df
        if filtered_df.empty:
            st.info("No interns to delete.")
        else:
            intern_names = filtered_df["Name"].tolist()
            selected_intern = st.selectbox("Select Intern to Delete", ["None"] + intern_names)
            if selected_intern != "None":
                intern_data = df[df["Name"] == selected_intern].iloc[0].to_dict()
                st.subheader(f"Intern Details:")
                st.write(f"**Name:** {intern_data['Name']}")
                st.write(f"**Cohort:** {intern_data['Cohort']}")
                st.write(f"**College:** {intern_data.get('College', 'N/A')}")
                st.write(f"**Year:** {intern_data.get('Year', 'N/A')}")
                st.write(f"**Status:** {intern_data.get('Active', 'Yes')}")
                # Option to update status directly
                st.markdown("---")
                st.write("### Update Intern Status")
                new_status = st.selectbox("Set status to:", ["Active", "Inactive", "Academic Break"], index=["Yes", "No", "Academic Break"].index(intern_data.get("Active", "Yes")) if intern_data.get("Active", "Yes") in ["Yes", "No", "Academic Break"] else 0)
                if st.button("Update Status"):
                    df.loc[df["Name"] == selected_intern, "Active"] = ("Yes" if new_status == "Active" else new_status)
                    df.to_csv(data_file, index=False)
                    st.success(f"Status for {selected_intern} updated to {new_status}.")
                    st.rerun()
                # Check if intern is in any team and show the team name
                teams = load_teams()
                in_team = False
                team_name_found = None
                for tname, team in teams.items():
                    if selected_intern in team['members']:
                        in_team = True
                        team_name_found = tname
                        break
                if in_team:
                    st.info(f"This intern is a member of team: {team_name_found}")
                st.warning("⚠️ This action cannot be undone!")
                col1, col2, col3 = st.columns(3)
                if in_team:
                    with col1:
                        if st.button("Mark as Inactive", type="secondary"):
                            df.loc[df["Name"] == selected_intern, "Active"] = "No"
                            df.to_csv(data_file, index=False)
                            st.success(f"Intern {selected_intern} marked as inactive.")
                            st.rerun()
                    with col2:
                        if st.button("Mark as Academic Break", type="secondary"):
                            df.loc[df["Name"] == selected_intern, "Active"] = "Academic Break"
                            df.to_csv(data_file, index=False)
                            st.success(f"Intern {selected_intern} marked as on academic break.")
                            st.rerun()
                    with col3:
                        if st.button("Cancel"):
                            st.rerun()
                else:
                    with col1:
                        if st.button("🗑️ Delete Intern", type="secondary"):
                            df = df[df["Name"] != selected_intern]
                            df.to_csv(data_file, index=False)
                            save_history(selected_intern, "Deleted", intern_data, "")
                            st.success(f"Intern {selected_intern} has been deleted.")
                            st.rerun()
                    with col2:
                        if st.button("Cancel"):
                            st.rerun()
    except Exception as e:
        st.error(f"[ERROR] {e}")

# Change History
elif page == "Change History":
    try:
        st.title("Change History")
        if os.path.exists(history_file):
            hist_df = pd.read_csv(history_file)
            if not is_super_admin:
                hist_df = hist_df[hist_df["Intern"].isin(df["Name"])] # Use df directly here
            if not hist_df.empty:
                # Get unique intern names from history
                intern_names = hist_df["Intern"].unique().tolist()
                selected_intern = st.selectbox("Select Intern to View History", ["All"] + intern_names)
                
                if selected_intern != "All":
                    filtered_hist = hist_df[hist_df["Intern"] == selected_intern]
                    st.subheader(f"History for: {selected_intern}")
                else:
                    filtered_hist = hist_df
                    st.subheader("All Changes")
                
                # Display history
                for index, row in filtered_hist.iterrows():
                    with st.expander(f"{row['Time']} - {row['Action']} - {row['Intern']}"):
                        st.write(f"**Action:** {row['Action']}")
                        st.write(f"**Time:** {row['Time']}")
                        st.write(f"**Intern:** {row['Intern']}")
                        
                        # Show changed fields if available
                        if pd.notna(row.get('Changed_Fields', '')) and row['Changed_Fields']:
                            try:
                                changed_fields = json.loads(row['Changed_Fields'])
                                st.write(f"**Changed Fields:** {', '.join(changed_fields)}")
                            except:
                                pass
                        
                        if row['Action'] == "Updated":
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write("**Before:**")
                                st.code(row['Old'])
                            with col2:
                                st.write("**After:**")
                                st.code(row['New'])
                        elif row['Action'] == "Added":
                            st.write("**Added Data:**")
                            st.code(row['New'])
                        elif row['Action'] == "Deleted":
                            st.write("**Deleted Data:**")
                            st.code(row['Old'])
            else:
                st.info("No history available.")
        else:
            st.info("No history file found.")
    except Exception as e:
        st.error(f"[ERROR] {e}")

# --- Refactored Project Teams tab for per-member progress tracking ---

elif page == "🚀 Project Teams":
    try:
        st.title("🚀 Project Teams")
        
        # Load existing teams
        teams = load_teams()
        # MIGRATION: Convert any old teams with 'members' as a list to dict format, and add team_progress if missing
        changed = False
        for team in teams.values():
            if isinstance(team.get('members'), list):
                team['members'] = {m: {
                    "Phase 0: Ideation & Mission": "",
                    "Week 1: MVP Build": "",
                    "Week 2: Testing & Iteration": "",
                    "Weeks 3-4: User Acquisition": "",
                    "Post-Internship Vision": ""
                } for m in team['members']}
                changed = True
            if 'team_progress' not in team:
                team['team_progress'] = {
                    "Phase 0: Ideation & Mission": "",
                    "Week 1: MVP Build": "",
                    "Week 2: Testing & Iteration": "",
                    "Weeks 3-4: User Acquisition": "",
                    "Post-Internship Vision": ""
                }
                changed = True
        if changed:
            save_teams(teams)
        available_interns = get_available_interns()
        
        # Check if a team is selected for detailed view
        if "selected_team" in st.session_state and st.session_state.selected_team:
            selected_team_name = st.session_state.selected_team
            if selected_team_name in teams:
                team_data = teams[selected_team_name]
                st.subheader(f"📋 Team: {selected_team_name}")
                team_member_names = []
                for m in team_data['members'].keys():
                    if m in df['Name'].values:
                        is_inactive = safe_is_inactive(df, m)
                        team_member_names.append(m + (' (Inactive)' if is_inactive else ''))
                    else:
                        team_member_names.append(m + ' (Not in CSV)')
                st.write(f"**Team Members:** {', '.join(team_member_names)}")
                st.subheader("📊 Overall Team Progress")
                for section in [
                    "Phase 0: Ideation & Mission",
                    "Week 1: MVP Build",
                    "Week 2: Testing & Iteration",
                    "Weeks 3-4: User Acquisition",
                    "Post-Internship Vision"
                ]:
                    st.text_area(section, value=team_data['team_progress'].get(section, ""), disabled=True, key=f"{selected_team_name}_overall_{section}")
                st.subheader("📊 Project Progress (Per Member)")
                for member, progress in team_data['members'].items():
                    st.markdown(f"**{member}**")
                    for section in [
                        "Phase 0: Ideation & Mission",
                        "Week 1: MVP Build",
                        "Week 2: Testing & Iteration",
                        "Weeks 3-4: User Acquisition",
                        "Post-Internship Vision"
                    ]:
                        st.text_area(section, value=progress.get(section, ""), disabled=True, key=f"{selected_team_name}_{member}_{section}")
                if st.button("⬅ Back to Team Dashboard"):
                    del st.session_state.selected_team
                    st.rerun()
            else:
                st.error("Selected team not found!")
                del st.session_state.selected_team
                st.rerun()
        else:
            # Team Creation Section
            st.subheader("➕ Create New Team")
            with st.form("create_team_form"):
                team_name = st.text_input("Team Name (must be unique)")
                used_interns = []
                for team in teams.values():
                    if isinstance(team.get('members'), dict):
                        used_interns.extend(team['members'].keys())
                    elif isinstance(team.get('members'), list):
                        used_interns.extend(team['members'])
                available_for_team = [intern for intern in available_interns if intern not in used_interns]
                if len(available_for_team) < 5:
                    st.warning(f"⚠️ Only {len(available_for_team)} interns available. Need at least 5 interns to create a team.")
                    team_members = []
                else:
                    st.write(f"**Available Interns:** {len(available_for_team)} interns")
                    team_members = st.multiselect(
                        "Select exactly 5 team members:",
                        available_for_team,
                        max_selections=5
                    )
                st.markdown("**Initial Overall Team Progress (Optional):**")
                phase_0 = st.text_area("Phase 0: Ideation & Mission (Team)", height=100)
                week_1 = st.text_area("Week 1: MVP Build (Team)", height=100)
                week_2 = st.text_area("Week 2: Testing & Iteration (Team)", height=100)
                weeks_3_4 = st.text_area("Weeks 3-4: User Acquisition (Team)", height=100)
                vision = st.text_area("Post-Internship Vision (Team)", height=100)
                create_submitted = st.form_submit_button("Create Team")
                if create_submitted:
                    if not team_name:
                        st.error("Please enter a team name.")
                    elif team_name in teams:
                        st.error("Team name already exists. Please choose a different name.")
                    elif len(team_members) != 5:
                        st.error("Please select exactly 5 team members.")
                    else:
                        teams[team_name] = {
                            "team_progress": {
                                "Phase 0: Ideation & Mission": phase_0,
                                "Week 1: MVP Build": week_1,
                                "Week 2: Testing & Iteration": week_2,
                                "Weeks 3-4: User Acquisition": weeks_3_4,
                                "Post-Internship Vision": vision
                            },
                            "members": {m: {
                                "Phase 0: Ideation & Mission": "",
                                "Week 1: MVP Build": "",
                                "Week 2: Testing & Iteration": "",
                                "Weeks 3-4: User Acquisition": "",
                                "Post-Internship Vision": ""
                            } for m in team_members}
                        }
                        save_teams(teams)
                        teams = load_teams()
                        st.success(f"Team '{team_name}' created successfully!")
                        st.rerun()
            # Team Management Section
            if teams:
                st.markdown("---")
                st.subheader("📋 My Teams – Click to View Progress")
                for team_name in teams.keys():
                    if st.button(f"👥 {team_name}", key=f"team_{team_name}"):
                        st.session_state.selected_team = team_name
                        st.rerun()
                # Team Progress Update Section
                st.markdown("---")
                st.subheader("✏️ Update Team Progress (Overall & Per Member)")
                selected_team_for_update = st.selectbox("Select Team to Update:", list(teams.keys()))
                if selected_team_for_update:
                    team_data = teams[selected_team_for_update]
                    member_options = ["Overall Team"] + list(team_data['members'].keys())
                    selected_member = st.selectbox("Select Member to Update:", member_options)
                    with st.form("update_team_progress"):
                        if selected_member == "Overall Team":
                            st.markdown("**Update Overall Team Progress:**")
                            updated_team_phase_0 = st.text_area(
                                "Phase 0: Ideation & Mission (Team)",
                                value=team_data['team_progress'].get("Phase 0: Ideation & Mission", ""),
                                height=100
                            )
                            updated_team_week_1 = st.text_area(
                                "Week 1: MVP Build (Team)",
                                value=team_data['team_progress'].get("Week 1: MVP Build", ""),
                                height=100
                            )
                            updated_team_week_2 = st.text_area(
                                "Week 2: Testing & Iteration (Team)",
                                value=team_data['team_progress'].get("Week 2: Testing & Iteration", ""),
                                height=100
                            )
                            updated_team_weeks_3_4 = st.text_area(
                                "Weeks 3-4: User Acquisition (Team)",
                                value=team_data['team_progress'].get("Weeks 3-4: User Acquisition", ""),
                                height=100
                            )
                            updated_team_vision = st.text_area(
                                "Post-Internship Vision (Team)",
                                value=team_data['team_progress'].get("Post-Internship Vision", ""),
                                height=100
                            )
                            update_submitted = st.form_submit_button("Update Progress")
                            if update_submitted:
                                team_data['team_progress'] = {
                                    "Phase 0: Ideation & Mission": updated_team_phase_0,
                                    "Week 1: MVP Build": updated_team_week_1,
                                    "Week 2: Testing & Iteration": updated_team_week_2,
                                    "Weeks 3-4: User Acquisition": updated_team_weeks_3_4,
                                    "Post-Internship Vision": updated_team_vision
                                }
                                team_data['members'][selected_member] = {
                                    "Phase 0: Ideation & Mission": updated_team_phase_0,
                                    "Week 1: MVP Build": updated_team_week_1,
                                    "Week 2: Testing & Iteration": updated_team_week_2,
                                    "Weeks 3-4: User Acquisition": updated_team_weeks_3_4,
                                    "Post-Internship Vision": updated_team_vision
                                }
                                save_teams(teams)
                                teams = load_teams()
                                st.success(f"Overall team progress updated for '{selected_team_for_update}'!")
                                st.rerun()
                        else:
                            st.markdown(f"**Update Progress for {selected_member}:**")
                            member_progress = team_data['members'][selected_member]
                            updated_phase_0 = st.text_area(
                                "Phase 0: Ideation & Mission (Member)",
                                value=member_progress.get("Phase 0: Ideation & Mission", ""),
                                height=100
                            )
                            updated_week_1 = st.text_area(
                                "Week 1: MVP Build (Member)",
                                value=member_progress.get("Week 1: MVP Build", ""),
                                height=100
                            )
                            updated_week_2 = st.text_area(
                                "Week 2: Testing & Iteration (Member)",
                                value=member_progress.get("Week 2: Testing & Iteration", ""),
                                height=100
                            )
                            updated_weeks_3_4 = st.text_area(
                                "Weeks 3-4: User Acquisition (Member)",
                                value=member_progress.get("Weeks 3-4: User Acquisition", ""),
                                height=100
                            )
                            updated_vision = st.text_area(
                                "Post-Internship Vision (Member)",
                                value=member_progress.get("Post-Internship Vision", ""),
                                height=100
                            )
                            update_submitted = st.form_submit_button("Update Progress")
                            if update_submitted:
                                team_data['members'][selected_member] = {
                                    "Phase 0: Ideation & Mission": updated_phase_0,
                                    "Week 1: MVP Build": updated_week_1,
                                    "Week 2: Testing & Iteration": updated_week_2,
                                    "Weeks 3-4: User Acquisition": updated_weeks_3_4,
                                    "Post-Internship Vision": updated_vision
                                }
                                save_teams(teams)
                                teams = load_teams()
                                st.success(f"Progress updated for member '{selected_member}' in team '{selected_team_for_update}'!")
                                st.rerun()
                # CSV Export Section
                st.markdown("---")
                st.subheader("📥 Export Team Progress (Overall & Per Member)")
                csv_data = []
                for team_name, team_data in teams.items():
                    for member, progress in team_data['members'].items():
                        row = {
                            "Team Name": team_name,
                            "Member Name": member,
                            "Phase 0 (Team)": team_data['team_progress'].get("Phase 0: Ideation & Mission", ""),
                            "Week 1 (Team)": team_data['team_progress'].get("Week 1: MVP Build", ""),
                            "Week 2 (Team)": team_data['team_progress'].get("Week 2: Testing & Iteration", ""),
                            "Weeks 3-4 (Team)": team_data['team_progress'].get("Weeks 3-4: User Acquisition", ""),
                            "Vision (Team)": team_data['team_progress'].get("Post-Internship Vision", ""),
                            "Phase 0 (Member)": progress.get("Phase 0: Ideation & Mission", ""),
                            "Week 1 (Member)": progress.get("Week 1: MVP Build", ""),
                            "Week 2 (Member)": progress.get("Week 2: Testing & Iteration", ""),
                            "Weeks 3-4 (Member)": progress.get("Weeks 3-4: User Acquisition", ""),
                            "Vision (Member)": progress.get("Post-Internship Vision", "")
                        }
                        csv_data.append(row)
                if csv_data:
                    csv_df = pd.DataFrame(csv_data)
                    csv_string = csv_df.to_csv(index=False)
                    st.download_button(
                        "📥 Export My Team Progress",
                        csv_string,
                        file_name=f"{tech_lead.replace(' ', '_')}_team_progress_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                # --- Delete Team Section ---
                st.markdown("---")
                st.subheader("🗑️ Delete a Team")
                team_names_for_delete = list(teams.keys())
                if team_names_for_delete:
                    team_to_delete = st.selectbox("Select Team to Delete:", team_names_for_delete, key="delete_team_select")
                    if st.button("Delete Team", key="delete_team_btn"):
                        st.session_state.pending_delete_team = team_to_delete
                if "pending_delete_team" in st.session_state and st.session_state.pending_delete_team == team_to_delete:
                    confirm = st.checkbox(f"Are you sure you want to delete team '{team_to_delete}'? This cannot be undone.", key="delete_team_confirm")
                    if confirm and st.button("Confirm Delete", key="confirm_delete_team_btn"):
                        del teams[team_to_delete]
                        save_teams(teams)
                        teams = load_teams()
                        del st.session_state.pending_delete_team
                        if "selected_team" in st.session_state and st.session_state.selected_team == team_to_delete:
                            del st.session_state.selected_team
                        st.success(f"Team '{team_to_delete}' deleted successfully!")
                        st.rerun()
                else:
                    st.info("No teams to delete.")
            else:
                st.info("No teams created yet. Create your first team above!")
    except Exception as e:
        st.error(f"[ERROR] {e}")

# Download Data Section
st.sidebar.markdown("---")
st.sidebar.subheader("Download Data")
if not df.empty:
    st.sidebar.download_button(
        "📥 Download All Data",
        df.to_csv(index=False),
        file_name=f"{tech_lead.replace(' ', '_')}_all_interns_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
    cohort_download = st.sidebar.selectbox("Download by Cohort:", ["All", "Cohort 1", "Cohort 2"])
    if cohort_download != "All":
        filtered_download_df = df[df["Cohort"] == cohort_download]
        st.sidebar.download_button(
            f"📥 Download {cohort_download}",
            filtered_download_df.to_csv(index=False),
            file_name=f"{tech_lead.replace(' ', '_')}_{cohort_download.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    if is_super_admin and "Team(eg :2 or 3)" in df.columns:
        team_download_text = st.sidebar.text_input("Download by Team (enter team name):")
        if team_download_text:
            filtered_team_df = df[df["Team(eg :2 or 3)"].astype(str).str.contains(team_download_text, case=False, na=False)]
            if not filtered_team_df.empty:
                st.sidebar.download_button(
                    f"📥 Download Team: {team_download_text}",
                    filtered_team_df.to_csv(index=False),
                    file_name=f"{tech_lead.replace(' ', '_')}_{team_download_text.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.sidebar.info(f"No interns found for team: {team_download_text}")

# Footer
st.sidebar.markdown("---")
st.sidebar.write(f"Total Interns: {len(df)}")
if not df.empty:
    cohort_counts = df["Cohort"].value_counts()
    for cohort, count in cohort_counts.items():
        st.sidebar.write(f"{cohort}: {count}")
