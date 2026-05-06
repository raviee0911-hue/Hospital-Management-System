from database import get_connection
from random import choice


def suggest_doctor(disease):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT d.*
        FROM doctors d
        JOIN diseases dis ON d.department = dis.department
        WHERE dis.disease = %s
    """, (disease,))

    doctors = cursor.fetchall()
    if not doctors :
        cursor.execute("""
                SELECT * FROM doctors WHERE department = %s
            """, ("General",))
        doctors = cursor.fetchall()

    connection.close()
    return choice(doctors) if doctors else None
