import mysql.connector

def pull_db():
 return mysql.connector.connect(
         host="localhost",
         user="root",
         password="matthew1129",
         database="jlpos_system"
    )