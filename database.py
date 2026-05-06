import mysql.connector

def get_connection():
    connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="R@1234bin",
    database="hospital_db"
)
    return connection
