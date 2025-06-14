import streamlit as st
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh
# Database connection details
db_config = {
    "host": "82.180.143.66",
    "user": "u263681140_students",
    "password": "testStudents@123",
    "database": "u263681140_students"
}

# Hardcoded login credentials (you can expand with a secure auth system)
VALID_USERNAME = "admin"
VALID_PASSWORD = "rithealth"

# Function to get full data from table
def fetch_data():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM RITHealth ORDER BY id ASC")
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return pd.DataFrame(data)
    except mysql.connector.Error as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()

# Function to get latest data
def fetch_latest_data():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM RITHealth ORDER BY id DESC LIMIT 1")
        data = cursor.fetchone()
        cursor.close()
        conn.close()
        return data
    except mysql.connector.Error as e:
        st.error(f"Database error: {e}")
        return None

# Login UI
st.title("RIT Health Monitor - Secure Login")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            st.session_state.logged_in = True
            st.success("Login successful")
            
        else:
            st.error("Invalid username or password")
else:
    # Tabs after login
    # Auto-refresh every 5 seconds (only after login)

    # Tabs after login
    tab1, tab2, tab3 = st.tabs(["📊 Last Value", "📈 Graphs", "📋 All Data"])

    with tab1:
        st.subheader("Latest Health Record")
        latest_data = fetch_latest_data()
        if latest_data:
            col1, col2, col3 = st.columns(3)
            col1.metric("Heart Rate", f"{latest_data['HeartRate']} bpm")
            col2.metric("Oxygen Level", f"{latest_data['Oxygen']} %")
            col3.metric("Temperature", f"{latest_data['Temp']} °C")
            st.write(f"**Recorded at:** {latest_data['DateTime']}")
        else:
            st.warning("No data found.")
    #    
    with tab2:
        st.subheader("Health Data Trends")
        df = fetch_data()
        if not df.empty:
            df['DateTime'] = pd.to_datetime(df['DateTime'])
            df = df.sort_values(by='DateTime')
    
            graph_columns = {
                "HeartRate": "Heart Rate Over Time (bpm)",
                "Oxygen": "Oxygen Level Over Time (%)",
                "Temp": "Temperature Over Time (°C)"
            }
    
            for column, label in graph_columns.items():
                try:
                    df[column] = pd.to_numeric(df[column], errors='coerce')
                    st.line_chart(df.set_index('DateTime')[column], use_container_width=True)
                    st.caption(label)  # 👈 This puts the label below the chart
                except Exception as e:
                    st.warning(f"Could not plot {column}: {e}")
        else:
            st.warning("No data available for graph.")
    with tab3:
        st.subheader("Complete Health Data")
        df = fetch_data()
        if not df.empty:
            st.dataframe(df)
        else:
            st.warning("No data to display.")
    st_autorefresh(interval=10000, key="datarefresh")
