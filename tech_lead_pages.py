import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

DATA_FOLDER = "data"
HISTORY_FOLDER = "history"

tech_lead = st.session_state.tech_lead

data_file = os.path.join(DATA_FOLDER, f"{tech_lead.replace(' ', '_')}.csv")
history_file = os.path.join(HISTORY_FOLDER, f"{tech_lead.replace(' ', '_')}_history.json")

def save_data(df):
    df.to_csv(data_file, index=False)

def save_history(action, intern_data):
    entry = {
        "action": action,
        "data": intern_data,
        "timestamp": datetime.now().isoformat()
    }
    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            history = json.load(f)
    else:
        history = []
    history.append(entry)
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=2)

if not os.path.exists(data_file):
    df = pd.DataFrame(columns=[
        "Name", "College", "Year", "GitLab Acc (README.md)",
        "Streamlit app and Deployment", "Huggingface+streamlit integration",
        "Data Collection (started?)", "Received Offer letter", "Cohort"
    ])
    save_data(df)
else:
    df = pd.read_csv(data_file)

if page == "Add/Update Intern":
    st.title("Add or Update Intern")
    with st.form("intern_form"):
        name = st.text_input("Intern Name")
        college = st.text_input("College")
        year = st.selectbox("Year", ["1", "2", "3", "4"])
        gitlab = st.text_input("GitLab Acc (README.md)")
        streamlit_app = st.text_input("Streamlit app and Deployment")
        huggingface = st.text_input("Huggingface+streamlit integration")
        data_collection = st.selectbox("Data Collection (started?)", ["", "Yes", "No"])
        offer_letter = st.selectbox("Received Offer letter", ["", "Yes", "No"])
        cohort = st.selectbox("Cohort", ["Cohort 1", "Cohort 2"])
        submitted = st.form_submit_button("Submit")

        if submitted:
            existing_index = df[df['Name'] == name].index
            intern_data = {
                "Name": name,
                "College": college,
                "Year": year,
                "GitLab Acc (README.md)": gitlab,
                "Streamlit app and Deployment": streamlit_app,
                "Huggingface+streamlit integration": huggingface,
                "Data Collection (started?)": data_collection,
                "Received Offer letter": offer_letter,
                "Cohort": cohort
            }
            if not existing_index.empty:
                df.loc[existing_index[0]] = intern_data
                save_history("Updated", intern_data)
            else:
                df = df.append(intern_data, ignore_index=True)
                save_history("Added", intern_data)
            save_data(df)
            st.success("Intern data saved.")

elif page == "Edit Intern":
    st.title("Edit Intern")
    selected_name = st.selectbox("Select Intern", df['Name'].tolist())
    selected_row = df[df['Name'] == selected_name].iloc[0]

    with st.form("edit_form"):
        college = st.text_input("College", selected_row['College'])
        year = st.selectbox("Year", ["1", "2", "3", "4"], index=int(selected_row['Year']) - 1)
        gitlab = st.text_input("GitLab Acc (README.md)", selected_row['GitLab Acc (README.md)'])
        streamlit_app = st.text_input("Streamlit app and Deployment", selected_row['Streamlit app and Deployment'])
        huggingface = st.text_input("Huggingface+streamlit integration", selected_row['Huggingface+streamlit integration'])
        data_collection = st.selectbox("Data Collection (started?)", ["", "Yes", "No"], index=["", "Yes", "No"].index(selected_row['Data Collection (started?)']))
        offer_letter = st.selectbox("Received Offer letter", ["", "Yes", "No"], index=["", "Yes", "No"].index(selected_row['Received Offer letter']))
        cohort = st.selectbox("Cohort", ["Cohort 1", "Cohort 2"], index=["Cohort 1", "Cohort 2"].index(selected_row['Cohort']))
        submitted = st.form_submit_button("Save Changes")

        if submitted:
            updated_data = {
                "Name": selected_name,
                "College": college,
                "Year": year,
                "GitLab Acc (README.md)": gitlab,
                "Streamlit app and Deployment": streamlit_app,
                "Huggingface+streamlit integration": huggingface,
                "Data Collection (started?)": data_collection,
                "Received Offer letter": offer_letter,
                "Cohort": cohort
            }
            df.loc[df['Name'] == selected_name] = updated_data
            save_data(df)
            save_history("Edited", updated_data)
            st.success("Changes saved.")

elif page == "Delete Intern":
    st.title("Delete Intern")
    selected_name = st.selectbox("Select Intern to Delete", df['Name'].tolist())
    if st.button("Delete"):
        df = df[df['Name'] != selected_name]
        save_data(df)
        save_history("Deleted", {"Name": selected_name})
        st.success(f"Intern '{selected_name}' deleted.")
