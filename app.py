import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client, PostgrestAPIError
import re

# --- Page Configuration ---
st.set_page_config(page_title="Internship Progress Tracker", layout="wide")

# --- Supabase Setup ---
# Ensure you have your Supabase URL and Key in Streamlit's secrets.
# [supabase]
# url = "YOUR_SUPABASE_URL"
# key = "YOUR_SUPABASE_KEY"
# [admin]
# email = "YOUR_ADMIN_EMAIL"
# password = "YOUR_ADMIN_PASSWORD"
try:
    SUPABASE_URL = st.secrets["supabase"]["url"]
    SUPABASE_KEY = st.secrets["supabase"]["key"]
    sb: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    ADMIN_EMAIL = st.secrets["admin"]["email"]
    ADMIN_PASSWORD = st.secrets["admin"]["password"]
except (KeyError, FileNotFoundError):
    st.error("Supabase or Admin credentials are not set in st.secrets.toml. Please add them to run the app.")
    st.stop()

# --- Data Fields ---
INTERN_FIELDS = [
    "Name", "Cohort", "Team", "GitLab User Name", "Year", "Received Offer letter", "College",
    "GitLab Acc (README.md)", "GitLab Acc Link", "Innings Courses (Python & AI)",
    "Huggingchat/Dify", "Huggingchat Link", "Streamlit app and Deployment", "Streamlit Link",
    "Huggingface+streamlit integration", "HF+Streamlit Link", "Pushed Apps onto GitLab",
    "Data Collection (started?)", "Size of Data", "Can go to any other places",
    "Blockers?", "Remarks", "Active"
]

# --- Authentication State Management ---
if "user" not in st.session_state:
    st.session_state.user = None
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

def show_auth_page():
    """Displays the login and registration forms."""
    st.title("Internship Program Tracker")
    st.markdown("Please login to view and update your progress. If you are new, please register.")
    
    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.subheader("Login")
            with st.form("login_form"):
                email = st.text_input("Email", key="login_email")
                password = st.text_input("Password", type="password", key="login_password")
                if st.form_submit_button("Login", use_container_width=True):
                    # Admin Login Check
                    if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
                        st.session_state.user = {"email": email, "id": "admin"}
                        st.session_state.is_admin = True
                        st.success("Admin login successful!")
                        st.rerun()
                    else:
                        # Regular User Login
                        try:
                            res = sb.auth.sign_in_with_password({"email": email, "password": password})
                            if res.user:
                                st.session_state.user = res.user
                                st.session_state.is_admin = False
                                st.success("Login successful!")
                                st.rerun()
                            else:
                                st.error("Login failed. Please check your credentials.")
                        except Exception as e:
                            st.error(f"An error occurred during login: {e}")

    with col2:
        with st.container(border=True):
            st.subheader("Register")
            with st.form("register_form"):
                name = st.text_input("Full Name", key="reg_name")
                college = st.text_input("College Name", key="reg_college")
                email = st.text_input("Email", key="reg_email")
                password = st.text_input("Password", type="password", key="reg_password")
                
                if st.form_submit_button("Register", use_container_width=True):
                    if not all([name, college, email, password]):
                        st.warning("Please fill out all registration fields.")
                    else:
                        try:
                            res = sb.auth.sign_up({"email": email, "password": password})
                            if res.user:
                                # This insert will now rely on the default values set in the SQL schema
                                # for fields like 'Team' and 'Year'.
                                initial_data = {
                                    "id": str(res.user.id), 
                                    "email": email, 
                                    "Name": name, 
                                    "College": college,
                                    "created_at": datetime.now().isoformat(),
                                    "updated_at": datetime.now().isoformat()
                                }
                                sb.table("interns").insert(initial_data).execute()
                                st.success("Registration successful! Please proceed to the login tab.")
                            else:
                                st.error("Registration failed. The user may already exist or there was a server issue.")
                        except Exception as e:
                            st.error(f"Registration failed: {e}")

# --- Admin Functions ---
@st.cache_data(ttl=300)
def get_all_interns_data():
    """Fetches all intern data for the admin."""
    try:
        res = sb.table("interns").select("*").execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    except Exception as e:
        st.error(f"Failed to fetch intern data: {e}")
        return pd.DataFrame()

def parse_size(size_str):
    """Parses a size string (e.g., '100MB', '1.2GB') and returns size in GB."""
    if not isinstance(size_str, str):
        return 0.0
    
    size_str = size_str.strip().upper()
    
    try:
        value_match = re.search(r'[\d\.]+', size_str)
        if not value_match:
            return 0.0
        value = float(value_match.group())

        if 'TB' in size_str:
            return value * 1024
        elif 'GB' in size_str:
            return value
        elif 'MB' in size_str:
            return value / 1024
        elif 'KB' in size_str:
            return value / (1024 * 1024)
        else:
            return 0.0
    except (ValueError, TypeError):
        return 0.0

def show_admin_dashboard():
    """Displays the admin dashboard."""
    st.title("Super Admin Dashboard")
    
    df = get_all_interns_data()
    
    if df.empty:
        st.warning("No intern data found.")
        return

    total_interns = len(df)
    total_data_gb = df['Size of Data'].apply(parse_size).sum()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Interns", f"{total_interns}")
    with col2:
        st.metric("Total Data Collected", f"{total_data_gb:.2f} GB")
    
    st.markdown("---")

    st.header("Filter and View Interns")
    colleges = sorted(df['College'].unique().tolist())
    selected_colleges = st.multiselect("Filter by College:", options=colleges, default=[])
    
    filtered_df = df[df['College'].isin(selected_colleges)] if selected_colleges else df
        
    st.dataframe(filtered_df)
    
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Filtered Data as CSV",
        data=csv,
        file_name=f"all_intern_data_{datetime.now().strftime('%Y%m%d')}.csv",
        mime='text/csv',
        use_container_width=True
    )

# --- Intern Functions ---
@st.cache_data(ttl=300)
def get_intern_profile(user_id):
    """Fetches a single intern's profile data."""
    try:
        res = sb.table("interns").select("*").eq("id", str(user_id)).single().execute()
        return res.data
    except PostgrestAPIError as e:
        if e.code == 'PGRST116':
            st.warning("Profile not found. Please save your profile to create one.")
            return None
        st.error(f"Error fetching profile: {e.message}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None

def update_intern_profile(user_id, data):
    """Updates an intern's profile data."""
    try:
        data["updated_at"] = datetime.now().isoformat()
        sb.table("interns").update(data).eq("id", str(user_id)).execute()
        return True
    except Exception as e:
        st.error(f"Failed to update profile: {e}")
        return False

def show_intern_dashboard(user):
    """Displays the dashboard for a regular intern."""
    st.title("Internship Progress Dashboard")
    st.markdown("---")
    
    intern_data = get_intern_profile(user.id)
    if intern_data is None:
        intern_data = {"id": str(user.id), "email": user.email, "Name": user.user_metadata.get('name', '')}
        for field in INTERN_FIELDS:
            if field not in intern_data:
                intern_data[field] = ""

    with st.form("intern_profile_form"):
        st.header("Your Profile and Progress")
        st.markdown("Update your details below. Your email and name are linked to your login and cannot be changed here.")
        form_inputs = {}
        
        # FIX: Helper function to safely get the index for selectbox widgets
        def safe_get_index(options, key, default_option):
            value = intern_data.get(key)
            try:
                return options.index(value)
            except (ValueError, TypeError):
                return options.index(default_option)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.text_input("Name", value=intern_data.get("Name", ""), disabled=True)
            form_inputs["Cohort"] = st.text_input("Cohort", value=intern_data.get("Cohort", ""))
            
            team_value = int(intern_data.get("Team") or 0)
            form_inputs["Team"] = st.number_input("Team (eg: 2 or 3)", value=team_value, step=1, format="%d")
            
            form_inputs["GitLab User Name"] = st.text_input("GitLab User Name", value=intern_data.get("GitLab User Name", ""))
            
            year_value = int(intern_data.get("Year") or datetime.now().year)
            form_inputs["Year"] = st.number_input("Year", value=year_value, step=1, format="%d")

            form_inputs["College"] = st.text_input("College", value=intern_data.get("College", ""), disabled=True)
            form_inputs["Active"] = st.selectbox("Active", [True, False], index=0 if intern_data.get("Active", True) else 1)
        with col2:
            st.subheader("Project Links")
            form_inputs["GitLab Acc Link"] = st.text_input("GitLab Account Link", value=intern_data.get("GitLab Acc Link", ""))
            form_inputs["Huggingchat Link"] = st.text_input("Huggingchat/Dify Link", value=intern_data.get("Huggingchat Link", ""))
            form_inputs["Streamlit Link"] = st.text_input("Streamlit App Link", value=intern_data.get("Streamlit Link", ""))
            form_inputs["HF+Streamlit Link"] = st.text_input("HuggingFace+Streamlit Link", value=intern_data.get("HF+Streamlit Link", ""))
        with col3:
            st.subheader("Task Status")
            task_status_options = ["Completed", "In Progress", "Not Started"]
            yes_no_options = ["Yes", "No"]
            
            form_inputs["Received Offer letter"] = st.selectbox("Received Offer letter?", yes_no_options, index=safe_get_index(yes_no_options, "Received Offer letter", "No"))
            form_inputs["GitLab Acc (README.md)"] = st.selectbox("GitLab README.md Complete?", yes_no_options, index=safe_get_index(yes_no_options, "GitLab Acc (README.md)", "No"))
            form_inputs["Innings Courses (Python & AI)"] = st.selectbox("Innings Courses", task_status_options, index=safe_get_index(task_status_options, "Innings Courses (Python & AI)", "Not Started"))
            form_inputs["Huggingchat/Dify"] = st.selectbox("Huggingchat/Dify Task", task_status_options, index=safe_get_index(task_status_options, "Huggingchat/Dify", "Not Started"))
            form_inputs["Streamlit app and Deployment"] = st.selectbox("Streamlit App Task", task_status_options, index=safe_get_index(task_status_options, "Streamlit app and Deployment", "Not Started"))
            form_inputs["Huggingface+streamlit integration"] = st.selectbox("HF+Streamlit Integration", task_status_options, index=safe_get_index(task_status_options, "Huggingface+streamlit integration", "Not Started"))
            form_inputs["Pushed Apps onto GitLab"] = st.selectbox("Pushed App to GitLab?", yes_no_options, index=safe_get_index(yes_no_options, "Pushed Apps onto GitLab", "No"))

        st.markdown("---")
        st.subheader("Data Collection & Other Info")
        d_col1, d_col2 = st.columns(2)
        with d_col1:
            form_inputs["Data Collection (started?)"] = st.selectbox("Data Collection Started?", yes_no_options, index=safe_get_index(yes_no_options, "Data Collection (started?)", "No"))
            form_inputs["Size of Data"] = st.text_input("Size of Data (e.g., 100MB, 1.2GB)", value=intern_data.get("Size of Data", ""))
            form_inputs["Can go to any other places"] = st.selectbox("Willing to relocate?", yes_no_options, index=safe_get_index(yes_no_options, "Can go to any other places", "No"))
        with d_col2:
            form_inputs["Blockers?"] = st.text_area("Blockers?", value=intern_data.get("Blockers?", ""), help="Describe any issues blocking your progress.")
            form_inputs["Remarks"] = st.text_area("Remarks", value=intern_data.get("Remarks", ""), help="Any other comments or remarks.")

        if st.form_submit_button("Save Profile", use_container_width=True):
            if update_intern_profile(user.id, form_inputs):
                st.success("Your profile has been saved successfully!")
                st.cache_data.clear()
                st.rerun()

    st.markdown("---")
    st.header("Download Your Data")
    download_data = {field: intern_data.get(field, "") for field in INTERN_FIELDS}
    download_data.update({"email": user.email, "id": str(user.id)})
    df_download = pd.DataFrame([download_data])
    csv = df_download.to_csv(index=False).encode('utf-8')
    st.download_button("Download My Data as CSV", csv, f"{user.email.split('@')[0]}_profile.csv", 'text/csv', use_container_width=True)


# --- Main App Logic ---
if not st.session_state.user:
    show_auth_page()
    st.stop()

# --- Sidebar and Logout ---
welcome_name = "Admin" if st.session_state.is_admin else st.session_state.user.email
st.sidebar.title(f"Welcome, {welcome_name}!")
if st.sidebar.button("Logout"):
    if not st.session_state.is_admin:
        sb.auth.sign_out()
    st.session_state.user = None
    st.session_state.is_admin = False
    st.rerun()

# --- Main Content Router ---
if st.session_state.get("is_admin"):
    show_admin_dashboard()
else:
    show_intern_dashboard(st.session_state.user)
