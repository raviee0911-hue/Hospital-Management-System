import random
import os
import re
from database import get_connection
from suggest_doctor import suggest_doctor

class Patient:
    @staticmethod
    def create_patient_table():
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            patient_id VARCHAR(10) PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            age INT NOT NULL,
            gender VARCHAR(10) NOT NULL,
            phone VARCHAR(10) NOT NULL,
            disease VARCHAR(50) NOT NULL,
            address VARCHAR(70) NOT NULL,
            doctor_id VARCHAR(10) NOT NULL,
            doctor_fees INT NOT NULL,
            bed_days INT,
            FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
        )
        """)
        connection.commit()
        connection.close()

    @staticmethod
    def add_patient():
        Patient.create_patient_table()

        name = input("Patient Name: ").strip().title()
        age = int(input("Patient Age: "))
        gender = input("Patient Gender: ").strip().title()
        phone = input("Patient Phone No: ").strip()
        disease = input("Patient Disease: ").strip().title()
        address = input("Patient Address: ").strip().title()

        if not re.match(r"^[6-9]\d{9}$", phone):
            print("Invalid phone number!")
            return

        doctor = suggest_doctor(disease)
        if not doctor:
            print("No doctors available! Suggested to add a doctor!")
            return



        bed_days = 0
        if input("Need bed? (y/n): ").lower() == 'y':
            bed_days = int(input("Days: "))

        patient_id = "PE" + str(random.randint(111111, 999999))

        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT disease FROM diseases WHERE disease=%s", (disease,))
        if not cursor.fetchone():
            print("Invalid Disease!")
            return
        else:
            cursor.execute("""
        INSERT INTO patients 
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (patient_id, name, age, gender, phone, disease,
              address, doctor[0], doctor[6], bed_days))

        connection.commit()
        connection.close()
        print(f"Note, Patient {name} added successfully and Patient ID is {patient_id}")
        print(f"Suggested Doctor: {doctor[1]} ({doctor[4]})")

    @staticmethod
    def view_patient():
        choice = input("View Patient using PatientID or Patient phone number 'ID' or 'PH': ").strip().lower()
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        if choice == 'id':
            patient_id = input("Enter Patient ID: ").strip()
            cursor.execute("SELECT * FROM patients WHERE patient_id=%s", (patient_id,))
        elif choice == "ph":
            patient_ph = input("Enter Patient phone number: ").strip()
            cursor.execute("SELECT * FROM patients WHERE phone=%s", (patient_ph,))
        else:
            print("Patient not found!")
            return
        row = cursor.fetchone()
        connection.close()



        print("\n--- Patient Details ---")
        print("Patient ID:", row["patient_id"])
        print("Patient Name:", row["name"])
        print("Patient Age:", row["age"])
        print("Patient Gender:", row["gender"])
        print("Patient Phone No:", row["phone"])
        print("Patient Disease:", row["disease"])
        print("Patient Address:", row["address"])
        print("Patient Bed Days:", row["bed_days"])

    @staticmethod
    def update_patient():
        choice = input("Updating Patient using PatientID or Patient phone number.  'ID' or 'PH': ").strip().lower()
        connection = get_connection()
        cursor = connection.cursor()

        name = input("New Patient Name: ").title().strip()
        age = int(input("New Age: "))
        gender = input("New Gender: ").title().strip()
        phone = input("New Phone: ").strip()
        disease = input("New Disease: ").title().strip()
        address = input("New Address: ").strip()
        if choice == 'id':
            patient_id = input("Enter Patient ID: ").strip()
            cursor.execute("""
                    UPDATE patients 
                    SET name=%s, age=%s, gender=%s, phone=%s, disease=%s, address=%s
                    WHERE patient_id=%s
                    """, (name, age, gender, phone, disease, address, patient_id))
        elif choice == "ph":
            patient_ph = input("Enter Patient phone number: ").strip()
            cursor.execute("""
                    UPDATE patients 
                    SET name=%s, age=%s, gender=%s, phone=%s, disease=%s, address=%s
                    WHERE phone=%s
                    """, (name, age, gender, phone, disease, address, patient_ph))
        else:
            print("Patient not found!")
            return

        connection.commit()
        connection.close()
        print("Patient updated successfully!")

    @staticmethod
    def delete_patient(patient_id):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM patients WHERE patient_id=%s", (patient_id,))
        connection.commit()
        connection.close()
        print("Patient deleted!")

    @staticmethod
    def get_bill():
        choice = input("Get Bill of Patient using PatientID or Patient phone number.  'ID' or 'PH': ").strip().lower()
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        if choice == 'id':
            patient_id = input("Enter Patient ID: ").strip()
            cursor.execute("SELECT * FROM patients WHERE patient_id=%s", (patient_id,))
        elif choice == "ph":
            patient_ph = input("Enter Patient phone number: ").strip()
            cursor.execute("SELECT * FROM patients WHERE phone=%s", (patient_ph,))
        else:
            print("Patient not found!")
            return
        row = cursor.fetchone()
        cursor.execute("SELECT name FROM doctors WHERE doctor_id=%s", (row["doctor_id"],))
        doctor_name = cursor.fetchone()
        connection.close()

        if not row:
            print("Patient not found!")
            return
        bed_cost = row["bed_days"] * 1500
        total = row["doctor_fees"] + 300 + (row["bed_days"] * 1500)

        home_dir = os.path.expanduser("~")
        downloads_dir = os.path.join(home_dir, "Downloads")
        os.makedirs(downloads_dir, exist_ok=True)
        file_name = row["patient_id"] + ".txt"
        file_path = os.path.join(downloads_dir, file_name)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"""                       LKDC CARE HOSPITAL & DIAGNOSTIC CENTER                         \n
            -------------------------------  BILL-----------------------------------\n
        Patient ID: {row["patient_id"]}\n
        Doctor Fees: {row["doctor_fees"]}\n
        Hospital Charges: 300\n
        Bed Charges: {bed_cost}\n
        TOTAL: {total}\n
        
        --------------------------Patient Details---------------------------\n
        Patient Name: {row["name"]}                 Patient Age: {row["age"]}\n
        Patient Gender: {row["gender"]}             Patient Phone: {row["phone"]}\n
        Patient Disease: {row["disease"]}           Patient Admitted Days: {row["bed_days"]}\n
        Assigned Doctor Name:  {doctor_name["name"]}\n
        Patient Address:  {row["address"]}""")

        print("Patient Bill Generated successfully!")

