import streamlit as st
import pandas as pd
from fpdf import FPDF
import os
import builtins
import re
import altair as alt
from datetime import datetime
import random
from doctor import Doctor
from patient import Patient
from database import get_connection

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Hospital Management System",
    page_icon="🏥",
    layout="wide"
)

# -------------------------------------------------
# STYLE
# -------------------------------------------------

st.markdown("""
<style>
/* ===== FULL BACKGROUND ===== */
.stApp {
    background:
    linear-gradient(120deg, rgba(2,6,23,0.85), rgba(15,23,42,0.85)),
    url("https://images.unsplash.com/photo-1523050854058-8df90110c9f1");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* ===== GLASS MAIN CONTAINER ===== */
.block-container {
    background: rgba(15, 23, 42, 0.75);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    padding: 2.5rem;
    border-radius: 20px;
    box-shadow: 0 20px 50px rgba(0,0,0,0.7);
}

/* ===== HEADINGS ===== */
h1, h2, h3 {
    color: #f8fafc !important;
    font-weight: 700;
}

/* ===== LABELS & TEXT ===== */
label, p, span, div {
    color: #e5e7eb !important;
}

/* ===== INPUTS ===== */
input, textarea, select {
    background: rgba(2,6,23,0.9) !important;
    color: white !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
}

/* ===== SELECT BOX ===== */
div[data-baseweb="select"] {
    background: rgba(2,6,23,0.9) !important;
    border-radius: 12px !important;
}

/* ===== MULTISELECT TAGS ===== */
div[data-baseweb="tag"] {
    background: linear-gradient(135deg, #ef4444, #f97316) !important;
    color: white !important;
    font-weight: 600;
    border-radius: 8px;
}

/* ===== CHART PANELS ===== */
iframe {
    background: rgba(2,6,23,0.9) !important;
    border-radius: 18px;
    padding: 10px;
}

/* ===== METRIC CARDS ===== */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #020617, #0f172a);
    border-radius: 16px;
    padding: 18px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.6);
}

/* ===== SIDEBAR ===== */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020617, #064e3b);
}
</style>
""", unsafe_allow_html=True)



# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
st.sidebar.title("🏥 LKDC CARE HOSPITAL")
menu = st.sidebar.radio("Navigation", ["Doctor Management", "Patient Management", "Analytics"])

# -------------------------------------------------
# HELPERS
# -------------------------------------------------
def fetch_doctors():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM doctors", conn)
    conn.close()
    return df

def get_patient_by_id_or_phone(value):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    if value.isdigit() and len(value) == 10:
        cur.execute("SELECT * FROM patients WHERE phone=%s", (value,))
    else:
        cur.execute("SELECT * FROM patients WHERE patient_id=%s", (value,))

    patient = cur.fetchone()
    conn.close()
    return patient

def generate_pdf_bill(row, doctor_name):
    path = os.path.join(os.path.expanduser("~"), "Downloads", f"{row['patient_id']}.pdf")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "LKDC CARE HOSPITAL & DIAGNOSTIC CENTER", ln=True, align="C")

    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, "123, Main Road, Chennai - 600001", ln=True, align="C")
    pdf.cell(0, 8, "Phone: +91-9876543210", ln=True, align="C")

    pdf.ln(5)
    pdf.cell(0, 8, "-" * 140, ln=True)

    # Bill meta
    today = datetime.now().strftime("%d-%m-%Y")
    pdf.cell(0, 8, f"Bill No: {row['patient_id']}        Date: {today}", ln=True)

    pdf.ln(5)

    # Patient Info
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "Patient Details", ln=True)
    pdf.set_font("Arial", "", 11)

    pdf.cell(0, 8, f"Patient Name : {row['name']}", ln=True)
    pdf.cell(0, 8, f"Age / Gender : {row['age']} / {row['gender']}", ln=True)
    pdf.cell(0, 8, f"Phone        : {row['phone']}", ln=True)
    pdf.cell(0, 8, f"Disease      : {row['disease']}", ln=True)
    pdf.cell(0, 8, f"Doctor       : {doctor_name}", ln=True)
    pdf.cell(0, 8, f"Address      : {row['address']}", ln=True)

    pdf.ln(5)
    pdf.cell(0, 8, "-" * 140, ln=True)

    # Charges
    doctor_fee = row["doctor_fees"]
    hospital_charge = 300
    bed_charge = row["bed_days"] * 1500
    total = doctor_fee + hospital_charge + bed_charge

    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "Charges", ln=True)
    pdf.set_font("Arial", "", 11)

    pdf.cell(0, 8, f"Doctor Consultation Fees : Rs. {doctor_fee}", ln=True)
    pdf.cell(0, 8, f"Hospital Charges         : Rs. {hospital_charge}", ln=True)
    pdf.cell(0, 8, f"Bed Charges ({row['bed_days']} days) : Rs. {bed_charge}", ln=True)

    pdf.ln(3)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"TOTAL AMOUNT : Rs. {total}", ln=True)

    pdf.ln(15)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, "Signature of Hospital Authority", ln=True)

    pdf.output(path)
    return path

# =================================================
# DOCTOR MANAGEMENT
# =================================================
if menu == "Doctor Management":
    st.title("👨‍⚕️ Doctor Management")

    tab1, tab2 = st.tabs(["➕ Add Doctor", "📋 View Doctors"])


    # ---------------- ADD DOCTOR ----------------
    # ---------------- ADD DOCTOR ----------------
    with tab1:

        # Fetch departments from diseases table
        def fetch_departments():
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT DISTINCT department FROM diseases")
            data = cur.fetchall()
            conn.close()
            return [d[0] for d in data]


        department_list = fetch_departments()

        with st.form("add_doctor_form"):
            name = st.text_input("Doctor Name")
            age = st.number_input("Age", min_value=21, max_value=80, step=1)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            phone = st.text_input("Mobile Number", max_chars=10)  # only for validation
            department = st.selectbox("Department", department_list)
            experience = st.number_input("Experience (Years)", min_value=0, max_value=60, step=1)
            fees = st.number_input("Consultation Fees", min_value=0)

            submit_doc = st.form_submit_button("Add Doctor")

            if submit_doc:
                # Phone validation
                if not re.fullmatch(r"[6-9]\d{9}", phone):
                    st.error("❌ Invalid mobile number")

                else:
                    # IMPORTANT: order must match doctor.py inputs
                    inputs = iter([
                        name,
                        str(age),
                        gender,
                        department,
                        str(experience),
                        str(fees)
                    ])
                    builtins.input = lambda _: next(inputs)

                    # Call original CLI function
                    Doctor.add_doctor()

                    # Fetch the SAME doctor just inserted
                    conn = get_connection()
                    cur = conn.cursor(dictionary=True)
                    cur.execute("""
                        SELECT doctor_id, name, department
                        FROM doctors
                        WHERE name = %s AND department = %s
                        ORDER BY doctor_id DESC
                        LIMIT 1
                    """, (name, department))
                    doctor = cur.fetchone()
                    conn.close()

                    st.markdown(f"""
                    <div style="
                    padding:18px;
                    background: linear-gradient(135deg, #022c22, #064e3b);
                    color:#d1fae5;
                    border-left:6px solid #22c55e;
                    border-radius:12px;
                    font-size:16px;
                    font-weight:600;
                    box-shadow:0 10px 30px rgba(0,0,0,0.6);
                    ">✅
                    <b>Doctor {doctor["name"]}</b> added successfully and 
                    <b>Doctor ID:</b> {doctor["doctor_id"]}
                    </div>
                    """, unsafe_allow_html=True)

    with tab2:
        st.dataframe(fetch_doctors(), use_container_width=True)



# =================================================
# PATIENT MANAGEMENT
# =================================================
if menu == "Patient Management":
    st.title("🧑‍⚕️ Patient Management")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["➕ Add Patient", "🔍 View Patient", "✏️ Update Patient", "❌ Delete", "🧾 Bill"]
    )

    # -------------------------------------------------
    # HELPER: GET PATIENT BY ID OR PHONE
    # -------------------------------------------------
    def get_patient_by_id_or_phone(value):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        if value.isdigit() and len(value) == 10:
            cur.execute("SELECT * FROM patients WHERE phone=%s", (value,))
        else:
            cur.execute("SELECT * FROM patients WHERE patient_id=%s", (value,))

        patient = cur.fetchone()
        conn.close()
        return patient

    # ---------------- ADD PATIENT ----------------
    with tab1:
        def fetch_diseases():
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT disease FROM diseases")
            data = cur.fetchall()
            conn.close()
            return [d[0] for d in data]


        disease_list = fetch_diseases()

        # -------- PATIENT DETAILS --------
        name = st.text_input("Patient Name")
        age = st.number_input("Age", min_value=0, max_value=120)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        phone = st.text_input("Mobile Number", max_chars=10)
        disease = st.selectbox("Disease", disease_list)
        address = st.text_input("Address")

        # -------- ADMISSION DETAILS --------
        st.markdown("### 🛏 Admission Details")
        bed = st.checkbox("Need Bed?")

        bed_days = st.number_input(
            "Bed Days",
            min_value=0,
            step=1,
            disabled=not bed
        )

        # -------- SUBMIT BUTTON (LAST) --------
        submit_add = st.button("Add Patient")

        # -------- LOGIC --------
        if submit_add:
            if not re.fullmatch(r"[6-9]\d{9}", phone):
                st.error("❌ Invalid mobile number")
            else:
                inputs = iter([
                    name, str(age), gender, phone,
                    disease, address,
                    "y" if bed else "n",
                    str(bed_days if bed else 0)
                ])
                builtins.input = lambda _: next(inputs)

                Patient.add_patient()

                # Fetch patient
                conn = get_connection()
                cur = conn.cursor(dictionary=True)
                cur.execute("""
                    SELECT patient_id, name, disease 
                    FROM patients 
                    WHERE phone = %s
                    LIMIT 1
                """, (phone,))
                patient = cur.fetchone()

                patient_id = patient["patient_id"]

                # Doctor suggestion
                cur.execute("""
                    SELECT name, department
                    FROM doctors
                    WHERE department = (
                        SELECT department FROM diseases WHERE disease = %s
                    )
                    ORDER BY experience DESC
                    
                """, (disease,))
                doctors = cur.fetchall()
                doctor = random.choice(doctors)

                if not doctor:
                    cur.execute("""
                        SELECT name, department
                        FROM doctors
                        WHERE department = 'General'
                        ORDER BY RAND()
                        
                    """)
                    doctors = cur.fetchall()
                    doctor = random.choice(doctors)

                conn.close()

                st.markdown(f"""
                <div style="
                padding:18px;
                background: linear-gradient(135deg, #022c22, #064e3b);
                color:#d1fae5;
                border-left:6px solid #22c55e;
                border-radius:12px;
                font-size:16px;
                font-weight:600;
                box-shadow:0 10px 30px rgba(0,0,0,0.6);
                ">
                ✅ Patient <b>{name}</b> added successfully<br>
                🆔 Patient ID: <b>{patient_id}</b><br>
                👨‍⚕️ Suggested Doctor: <b>{doctor["name"]}</b> ({doctor["department"]})
                </div>
                """, unsafe_allow_html=True)

    # ---------------- VIEW PATIENT ----------------
    with tab2:
        search = st.text_input("Patient ID or Phone Number", key="view_search")
        if st.button("View Patient"):
            patient = get_patient_by_id_or_phone(search)
            if patient:
                st.table(patient)
            else:
                st.error("❌ Patient not found")

    # ---------------- UPDATE PATIENT ----------------
    with tab3:
        search = st.text_input("Patient ID or Phone Number", key="update_search")

        if st.button("Load Patient"):
            patient = get_patient_by_id_or_phone(search)
            if patient:
                st.session_state["update_patient"] = patient
            else:
                st.error("❌ Patient not found")

        if "update_patient" in st.session_state:
            p = st.session_state["update_patient"]

            raw_age = int(p.get("age", 0))
            safe_age = raw_age if 0 <= raw_age <= 120 else 0

            with st.form("update_patient_form"):
                name = st.text_input("Name", value=p["name"])

                age = st.number_input(
                    "Age",
                    value=safe_age,
                    min_value=0,
                    max_value=120
                )

                gender = st.selectbox(
                    "Gender",
                    ["Male", "Female", "Other"],
                    index=["Male", "Female", "Other"].index(p["gender"])
                )

                phone = st.text_input("Phone", value=p["phone"])
                disease = st.text_input("Disease", value=p["disease"])
                address = st.text_input("Address", value=p["address"])

                submit_update = st.form_submit_button("Update Patient")

                if submit_update:
                    if not re.fullmatch(r"[6-9]\d{9}", phone):
                        st.error("❌ Invalid mobile number")
                    else:
                        conn = get_connection()
                        cur = conn.cursor()
                        cur.execute("""
                            UPDATE patients SET
                            name=%s, age=%s, gender=%s,
                            phone=%s, disease=%s, address=%s
                            WHERE patient_id=%s
                        """, (name, age, gender, phone, disease, address, p["patient_id"]))
                        conn.commit()
                        conn.close()

                        del st.session_state["update_patient"]
                        st.success("✅ Patient updated successfully")

    # ---------------- DELETE PATIENT ----------------
    with tab4:
        pid = st.text_input("Patient ID", key="delete_pid")
        confirm = st.checkbox("⚠️ I confirm permanent deletion")

        if st.button("Delete Patient"):
            if not pid:
                st.warning("Enter Patient ID")
            elif not confirm:
                st.error("Please confirm deletion")
            else:
                Patient.delete_patient(pid)
                st.success(f"✅ Patient {pid} deleted successfully")

    # ---------------- BILL ----------------
    with tab5:
        search = st.text_input("Patient ID or Phone Number", key="bill_search")

        if st.button("Generate PDF Bill"):
            patient = get_patient_by_id_or_phone(search)

            if not patient:
                st.error("❌ Patient not found")
            else:
                conn = get_connection()
                cur = conn.cursor(dictionary=True)
                cur.execute(
                    "SELECT name FROM doctors WHERE doctor_id=%s",
                    (patient["doctor_id"],)
                )
                doctor = cur.fetchone()
                conn.close()

                path = generate_pdf_bill(patient, doctor["name"])
                st.success("📄 Bill generated successfully")
                st.write(path)




# =================================================
# ANALYTICS (SIDE BY SIDE DASHBOARD)
# =================================================
if menu == "Analytics":
    st.title("📊 Hospital Analytics Dashboard")

    conn = get_connection()

    # ----------- DOCTOR FILTER -----------
    doctors_df = pd.read_sql("SELECT name FROM doctors", conn)
    doctor_names = doctors_df["name"].tolist()

    selected_doctors = st.multiselect(
        "Select Doctor(s)",
        options=doctor_names,
        default=doctor_names
    )

    # Build WHERE safely
    if selected_doctors:
        doctor_tuple = tuple(selected_doctors)
        where_clause = f"WHERE d.name IN {doctor_tuple}"
    else:
        where_clause = ""

    # ----------- TOTAL HOSPITAL INCOME -----------
    total_income_df = pd.read_sql(f"""
        SELECT 
        SUM(d.fees + 300 + (p.bed_days * 1500)) AS total_income
        FROM patients p
        JOIN doctors d ON p.doctor_id = d.doctor_id
        {where_clause}
    """, conn)

    total_income = total_income_df["total_income"][0] or 0
    st.metric("💰 Total Hospital Income", f"₹ {int(total_income)}")

    st.divider()

    # ----------- DOCTOR PERFORMANCE -----------
    doctor_income_df = pd.read_sql(f"""
        SELECT 
        d.name AS Doctor,
        SUM(d.fees + 300 + (p.bed_days * 1500)) AS Income
        FROM patients p
        JOIN doctors d ON p.doctor_id = d.doctor_id
        {where_clause}
        GROUP BY d.name
        ORDER BY Income DESC
    """, conn)

    chart_doctor = alt.Chart(doctor_income_df).mark_bar().encode(
        x=alt.X("Doctor", sort="-y"),
        y="Income",
        color=alt.Color("Doctor", legend=None),
        tooltip=["Doctor", "Income"]
    ).properties(title="Doctor-wise Income", height=350)

    # ----------- DEPARTMENT PERFORMANCE -----------
    dept_income_df = pd.read_sql(f"""
        SELECT 
        d.department AS Department,
        SUM(d.fees + 300 + (p.bed_days * 1500)) AS Income
        FROM patients p
        JOIN doctors d ON p.doctor_id = d.doctor_id
        {where_clause}
        GROUP BY d.department
        ORDER BY Income DESC
    """, conn)

    chart_dept = alt.Chart(dept_income_df).mark_bar().encode(
        x=alt.X("Department", sort="-y"),
        y="Income",
        color=alt.Color("Department"),
        tooltip=["Department", "Income"]
    ).properties(title="Department-wise Income", height=350)

    # ----------- ROW 1 -----------
    col1, col2 = st.columns(2)
    with col1:
        st.altair_chart(chart_doctor, use_container_width=True)
    with col2:
        st.altair_chart(chart_dept, use_container_width=True)

    st.divider()

    # ----------- DISEASE COUNT -----------
    disease_count_df = pd.read_sql(f"""
        SELECT 
        p.disease AS Disease,
        COUNT(*) AS No_of_Patients
        FROM patients p
        JOIN doctors d ON p.doctor_id = d.doctor_id
        {where_clause}
        GROUP BY p.disease
        ORDER BY No_of_Patients DESC
    """, conn)

    chart_disease = alt.Chart(disease_count_df).mark_bar().encode(
        x=alt.X("Disease", sort="-y"),
        y="No_of_Patients",
        color=alt.Color("Disease"),
        tooltip=["Disease", "No_of_Patients"]
    ).properties(title="Disease-wise Patients", height=350)

    # ----------- ROW 2 -----------
    col3, col4 = st.columns(2)
    with col3:
        st.altair_chart(chart_disease, use_container_width=True)
    with col4:
        st.dataframe(disease_count_df, use_container_width=True)

    conn.close()
