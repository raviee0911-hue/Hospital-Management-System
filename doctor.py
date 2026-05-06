import random
from database import get_connection

class Doctor:

    @staticmethod
    def create_table():
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            doctor_id varchar(10) PRIMARY KEY,
            name varchar(100) NOT NULL,
            age INT,
            gender varchar(10) NOT NULL,
            department varchar(100) NOT NULL,
            experience INT,
            fees INT not null
        )
        """)
        connection.commit()
        connection.close()

    @staticmethod
    def add_doctor():

        Doctor.create_table()
        name = input("Doctor Name: ").title()
        age = int(input("Age: "))
        gender = input("Gender: ").title()
        department = input("Department/Specialist example  ('General', 'Neurology', ''Cardiology'): ").title().strip()
        experience = int(input("Experience (years): "))
        fees = int(input("Consultation Fees: "))

        doctor_id = "DR" + str(random.randint(10000, 99999))

        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO doctors VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (doctor_id, name, age, gender, department, experience, fees))

        connection.commit()
        connection.close()
        print(f"Doctor {name} added successfully and Doctor ID: {doctor_id}")



    @staticmethod
    def view_doctors():

        print("\n" + "=" * 90)
        print(f"{'ID':<10} {'Name':<15} {'Age':<5} {'Gender':<8} {'Dept':<15} {'Exp':<5} {'Fees':<8}")
        print("=" * 90)

        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM doctors")
        rows = cursor.fetchall()
        connection.close()

        if not rows:
            print("No doctors found!")
            return

        for row in rows:
            print(f"{row[0]:<10} {row[1]:<15} {row[2]:<5} {row[3]:<8} {row[4]:<15} {row[5]:<5} ₹{row[6]:<8}")



