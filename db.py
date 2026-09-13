import mysql.connector
import pandas as pd
import streamlit as st

def get_db_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="Tonyrakesh@1026",
            database="world_debt_analytics",
            port=3306
        )
    except mysql.connector.Error as err:
        st.error(f"Database Connection Error: {err}")
        return None

def authenticate_user(username, password):
    conn = get_db_connection()
    if not conn:
        return None
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT user_id, username, role, branch_id 
        FROM users 
        WHERE username = %s AND password = %s
    """
    cursor.execute(query, (str(username), str(password)))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def fetch_data(query, params=None):
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df