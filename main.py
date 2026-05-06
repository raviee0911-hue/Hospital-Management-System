from patient import Patient
from doctor import Doctor


def patient_menu():
    while True:
        print("\n--- PATIENT MENU ---")
        print("1. Add Patient")
        print("2. View Patient")
        print("3. Update Patient")
        print("4. Delete Patient")
        print("5. Get Bill")
        print("6. Back")

        choice = input("Enter choice: ")

        if choice == '1':
            Patient.add_patient()
        elif choice == '2':
            try:
                Patient.view_patient()
            except Exception as e:
                print(e)
        elif choice == '3':
            Patient.update_patient()
        elif choice == '4':
            try:
                patient_id = input("Enter Patient ID: ").strip()
                Patient.delete_patient(patient_id)
            except Exception as e:
                print(e)
        elif choice == '5':
            Patient.get_bill()
        elif choice == '6':
            break

        else:
            print("Invalid choice!")


def doctor_menu():
    while True:
        print("\n--- DOCTOR MENU ---")
        print("1. Add Doctor")
        print("2. View Doctors")
        print("3. Back")

        choice = input("Enter choice: ")

        if choice == '1':
            Doctor.add_doctor()
        elif choice == '2':
            Doctor.view_doctors()
        elif choice == '3':
            break
        else:
            print("Invalid choice!")


def main():
    while True:
        print("\n=============HOSPITAL MANAGEMENT SYSTEM=============")
        print("1. Patient Management")
        print("2. Doctor Management")
        print("3. Exit")


        ch = input("Enter choice: ")

        if ch == '1':
             patient_menu()
        elif ch == '2':
            doctor_menu()
        elif ch == '3':
            print("Thank you for visiting!")
            break
        else:
            print("Invalid choice!")


if __name__ == "__main__":
    main()
