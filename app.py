import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- Configuration ---
st.set_page_config(
    page_title="Surgical Case Log",
    page_icon="⚕️",
    layout="wide"
)

# --- Data File ---
DATA_FILE = "surgical_log.csv"

# --- Helper Functions ---
def load_data():
    """Load data from CSV or create an empty DataFrame if it doesn't exist."""
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        # Define the columns based on your provided fields
        return pd.DataFrame(columns=[
            'Number', 'Patient_ID', 'Age', 'Date', 'Hospital', 'Consultant',
            'Diagnosis', 'Procedure', 'Anaesthesia', 'Outcome', 'Notes',
            'My_Role', 'Primary_Surgeon', 'Assistant'
        ])

def save_data(df):
    """Save the DataFrame to the CSV file."""
    df.to_csv(DATA_FILE, index=False)

def to_excel(df):
    """Converts a DataFrame to an Excel file in memory for downloading."""
    from io import BytesIO
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='SurgicalLog')
    processed_data = output.getvalue()
    return processed_data

# --- Main Application ---
st.title("👨‍⚕️ Personal Surgical Case Logbook")
st.markdown("A secure and simple way to log your surgical cases.")

# Load existing data
df = load_data()

# --- Tabbed Interface ---
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "➕ Add New Case", "📖 View Full Log"])

# --- TAB 1: Dashboard ---
with tab1:
    st.header("Your Surgical Dashboard")
    if not df.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Cases Logged", len(df))
        col2.metric("Complicated Cases", len(df[df['Outcome'] == 'Complicated']))
        col3.metric("Primary Surgeon Cases", len(df[df['My_Role'] == 'Primary Surgeon']))

        st.subheader("Cases by Procedure Type")
        procedure_counts = df['Procedure'].value_counts()
        st.bar_chart(procedure_counts)

        st.subheader("Cases by Hospital")
        hospital_counts = df['Hospital'].value_counts()
        st.bar_chart(hospital_counts)
    else:
        st.info("No cases logged yet. Add a case to see your dashboard.")

# --- TAB 2: Add New Case ---
with tab2:
    st.header("Enter New Case Details")
    with st.form("case_form", clear_on_submit=True):
        # Using a two-column layout for the form
        c1, c2 = st.columns(2)
        
        # Column 1
        patient_id = c1.text_input("Patient ID (non-identifiable)", help="Use a unique code like '2025-001', not the actual MRN.")
        age = c1.number_input("Patient Age", min_value=0, max_value=120)
        case_date = c1.date_input("Date of Surgery", value=datetime.now())
        hospital = c1.text_input("Hospital")
        consultant = c1.text_input("Consultant", value="Your Name")
        diagnosis = c1.text_area("Diagnosis")
        procedure = c1.text_area("Procedure")

        # Column 2
        anaesthesia = c2.selectbox("Anaesthesia", ["General", "Spinal", "Epidural", "Regional", "Local", "Sedation"])
        outcome = c2.radio("Outcome", ["Uneventful", "Complicated"])
        my_role = c2.selectbox("My Role", ["Primary Surgeon", "Assistant", "Observer"])
        primary_surgeon = c2.text_input("Primary Surgeon")
        assistant = c2.text_input("Assistant(s)")
        notes = c2.text_area("Notes / Key Learnings")

        # Submit button
        submitted = st.form_submit_button("Log Case")

        if submitted:
            # Create a new entry dictionary
            new_case_number = (df['Number'].max() + 1) if not df.empty else 1
            new_entry = {
                'Number': new_case_number,
                'Patient_ID': patient_id,
                'Age': age,
                'Date': case_date.strftime('%Y-%m-%d'),
                'Hospital': hospital,
                'Consultant': consultant,
                'Diagnosis': diagnosis,
                'Procedure': procedure,
                'Anaesthesia': anaesthesia,
                'Outcome': outcome,
                'Notes': notes,
                'My_Role': my_role,
                'Primary_Surgeon': primary_surgeon,
                'Assistant': assistant
            }
            
            # Append to the DataFrame
            new_df = pd.DataFrame([new_entry])
            df = pd.concat([df, new_df], ignore_index=True)
            
            # Save the updated data
            save_data(df)
            st.success("Case successfully logged! 🎉")

# --- TAB 3: View Full Log ---
with tab3:
    st.header("Complete Case Log")
    
    if not df.empty:
        # Filtering options
        st.markdown("Filter your log:")
        col_filter1, col_filter2 = st.columns(2)
        filter_procedure = col_filter1.text_input("Search by Procedure")
        filter_diagnosis = col_filter2.text_input("Search by Diagnosis")

        # Apply filters
        filtered_df = df
        if filter_procedure:
            filtered_df = filtered_df[filtered_df['Procedure'].str.contains(filter_procedure, case=False, na=False)]
        if filter_diagnosis:
            filtered_df = filtered_df[filtered_df['Diagnosis'].str.contains(filter_diagnosis, case=False, na=False)]
        
        st.dataframe(filtered_df)

        # Excel download
        st.download_button(
            label="📥 Download Log as Excel",
            data=to_excel(filtered_df),
            file_name="surgical_log.xlsx",
            mime="application/vnd.ms-excel"
        )
    else:
        st.warning("Your log is empty. Please add a case.")
