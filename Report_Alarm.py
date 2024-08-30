import time as ttm
from datetime import datetime, time
import numpy as np
import pandas as pd
import os
import plotly.graph_objects as go
import streamlit as st
import matplotlib.pyplot as plt
import requests
from fpdf import FPDF
from io import BytesIO

def get_sensor_data():
    try:
        # Utiliser l'URL correcte pour récupérer les données
        response = requests.get("http://192.168.174.45:8000/get_data/")
        response.raise_for_status()
        data = response.json()
        # Assurez-vous que les données sont au format liste de dictionnaires
        if isinstance(data, dict):
            data = [data]
        
        return data
    except requests.exceptions.RequestException as e:
        st.error(f"Erreur lors de la récupération des données : {e}")
        return []

# Function to generate PDF report
def generate_pdf_report(selected_date, total_energy, operating_time, data_report_list):
    pdf = FPDF()
    pdf.add_page()

    # Ajouter les logos (décommentez ces lignes si nécessaire)
    pdf.image(r"C:\Users\WIN\Desktop\stagePython\env\UXV.png", x=10, y=10, w=27, h=27)
    pdf.image(r"C:\Users\WIN\Desktop\stagePython\env\ERME.png", x=80, y=10, w=30, h=30)
    pdf.image(r"C:\Users\WIN\Desktop\stagePython\env\Génie.png", x=120, y=10, w=33, h=33)
    pdf.image(r"C:\Users\WIN\Desktop\stagePython\env\FST.png", x=170, y=10, w=33, h=33)


    # Titre du rapport
    pdf.set_font("Arial", size=18, style='B')
    pdf.ln(40)  # Ajouter un espace après les logos
    pdf.cell(0, 10, txt="Rapport Périodique", ln=True, align='C')

    # Ajouter un horodatage
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(0, 10, txt=f"Creation date: {timestamp}", ln=True, align='L')
    pdf.cell(0, 10, txt=f"Selected date: {selected_date}", ln=True, align='L')
    pdf.cell(0, 10, txt=f"Operating time: {operating_time:.6f} H" if operating_time is not None else "Operating time: None", ln=True, align='L')
    pdf.cell(0, 10, txt=f"Total energy: {total_energy:.6f} Wh" if total_energy is not None else "Total energy: None", ln=True, align='L')
   
    # Table headers
    pdf.set_font("Arial", size=12, style='B')
    pdf.set_fill_color(200, 220, 255)  # Background color for headers
    pdf.ln(10)

       # Define cell width and height
    cell_widths = [30, 30, 30, 25, 25, 25, 30]  # Widths for each column
    cell_height = 20

    # Draw the cells without text to create the table layout
    for width in cell_widths:
        pdf.cell(width, cell_height, '', border=1, align='C', fill=True)
    pdf.ln()

     # Write the multi-line text manually inside each cell
    pdf.set_xy(10, 120)  # Adjust Y coordinate if needed

     # Column headers with manual positioning
    pdf.set_font("Arial", size=12, style='B')

    # Position and draw each header text
    pdf.cell(cell_widths[0], 12, 'Hour', border=0, align='C')  # Single-line
    pdf.cell(cell_widths[1], 12, 'Panel Elev', border=0, align='C')  # First line
    pdf.cell(cell_widths[2], 12, 'Panel Azim', border=0, align='C')  # First line
    pdf.cell(cell_widths[3], 12, 'Temp', border=0, align='C')  # First line
    pdf.cell(cell_widths[4], 12, 'Humid', border=0, align='C')  # First line
    pdf.cell(cell_widths[5], 12, 'Light Lvl', border=0, align='C')  # First line
    pdf.cell(cell_widths[6], 12, 'Batt Lvl', border=0, align='C')  # First line

    # Move to the next line for the second part of headers
    pdf.set_xy(10, 128)  # Adjust Y coordinate for second line if needed

    # Draw the second line text
    pdf.cell(cell_widths[0], 12, '', border=0)  # Empty to keep position
    pdf.cell(cell_widths[1], 12, '(°)', border=0, align='C')  # Second line
    pdf.cell(cell_widths[2], 12, '(°)', border=0, align='C')  # Second line
    pdf.cell(cell_widths[3], 12, '(°C)', border=0, align='C')  # Second line
    pdf.cell(cell_widths[4], 12, '(%)', border=0, align='C')  # Second line
    pdf.cell(cell_widths[5], 12, '(lux)', border=0, align='C')  # Second line
    pdf.cell(cell_widths[6], 12, '(%)', border=0, align='C')  # Second line
    pdf.ln()  # Move to the next line

    # Table rows
    for i, data_report in enumerate(data_report_list):
        hour = f"{i:02d}:00:00"  # Format the hour as "HH:00:00"
        if data_report is not None:
            datetime_report = data_report.get('datetime')
            processed_elevation_report = data_report.get('processed_elevation')
            processed_azimuth_report = data_report.get('processed_azimuth')
            light_level_report = data_report.get('current_light_level')
            temperature_report = data_report.get('temperature')
            humidity_report = data_report.get('humidity')
            battery_level_report = data_report.get('battery_level')
            
            pdf.cell(30, 12, datetime_report.strftime('%H:%M:%S') if datetime_report else hour, border=1, align='C')
            pdf.cell(30, 12, f"{processed_elevation_report:.6f}" if processed_elevation_report is not None else 'None', border=1, align='C')
            pdf.cell(30, 12, f"{processed_azimuth_report:.6f}" if processed_azimuth_report is not None else 'None', border=1, align='C')
            pdf.cell(25, 12, f"{temperature_report:.2f}" if temperature_report is not None else 'None', border=1, align='C')
            pdf.cell(25, 12, f"{humidity_report:.2f}" if humidity_report is not None else 'None', border=1, align='C')
            pdf.cell(25, 12, f"{light_level_report:.2f}" if light_level_report is not None else 'None', border=1, align='C')
            pdf.cell(30, 12, f"{battery_level_report:.2f}" if battery_level_report is not None else 'None', border=1, align='C')
            pdf.ln()  # Move to the next line
        else:
            # Si data_report est None, ajouter une ligne avec 'None' pour chaque colonne
            pdf.cell(30, 12, hour, border=1, align='C')
            pdf.cell(30, 12, 'None', border=1, align='C')
            pdf.cell(30, 12, 'None', border=1, align='C')
            pdf.cell(25, 12, 'None', border=1, align='C')
            pdf.cell(25, 12, 'None', border=1, align='C')
            pdf.cell(25, 12, 'None', border=1, align='C')
            pdf.cell(30, 12, 'None', border=1, align='C')
            pdf.ln()  # Move to the next line

    # Générer le PDF sous forme de bytes
    pdf_output = pdf.output(dest='S').encode('latin1')
    
    # Convertir les bytes en objet BytesIO
    pdf_output_io = BytesIO(pdf_output)

    return pdf_output_io

def setup_alarm_controls():
    st.markdown("<h1 style='text-align: center; font-size: 22px; color: royalblue;'>Report and Alarm Notifications</h1>", unsafe_allow_html=True)
    st.write("")
    st.markdown("<h1 style='text-align: left; font-size: 22px;'>Day Selection and PDF Report Download</h1>", unsafe_allow_html=True)
    st.write("")
    col1, coll2= st.columns([2, 2])
    with col1:
        selected_date = st.date_input("Sélectionnez une date", datetime.now().date(), format="YYYY/MM/DD", key="selected_date")
    with coll2:
        d_p = st.empty()
    st.write("")
    st.markdown("<h1 style='text-align: left; font-size: 22px;'>Alarm Control Panel: Battery, Temperature, Light Level, and Humidity</h1>", unsafe_allow_html=True)
    st.write("")
    
    # Initialize alarm states if not already set
    if 'battery_alarm_active' not in st.session_state:
        st.session_state.battery_alarm_active = False
    if 'temperature_alarm_active' not in st.session_state:
        st.session_state.temperature_alarm_active = False
    if 'light_level_alarm_active' not in st.session_state:
        st.session_state.light_level_alarm_active = False
    if 'humidity_alarm_active' not in st.session_state:
        st.session_state.humidity_alarm_active = False

    # Initialize alarm thresholds
    battery_min, battery_max = None, None
    temperature_min, temperature_max = None, None
    light_level_min, light_level_max = None, None
    humidity_min, humidity_max = None, None

    col1, col2, col4_battery = st.columns([1, 2, 2])

    # Battery alarm controls
    with col1:
        if st.button("Enable battery alarm", key="battery_alarm_button"):
            st.session_state.battery_alarm_active = True

    with col2:
        if st.session_state.battery_alarm_active:
            st.write("Define thresholds for battery alarm :")
            battery_min = st.number_input("Minimum Battery Value (%)", min_value=0.0, format="%.2f", key="battery_min")
            battery_max = st.number_input("Maximum Battery Value (%)", min_value=0.0, format="%.2f", key="battery_max")
    with col4_battery:
        b_p = st.empty()
        
    st.write("")      
    st.write("")
    
    # Temperature alarm controls
    col1, col2, col4_Temperature = st.columns([1, 2, 2])
    with col1:
        if st.button("Enable Temperature Alarm", key="temperature_alarm_button"):
            st.session_state.temperature_alarm_active = True

    with col2:
        if st.session_state.temperature_alarm_active:
            st.write("Define thresholds for temperature alarm :")
            temperature_min = st.number_input("Minimum Temperature Value (°C)", min_value=-100.0, format="%.2f", key="temperature_min")
            temperature_max = st.number_input("Maximum Temperature Value (°C)", min_value=-100.0, format="%.2f", key="temperature_max")
    with col4_Temperature:
        t_p = st.empty()
     
    st.write("")
    
    # Light level alarm controls
    col1, col2, col4_light = st.columns([1, 2, 2])
    with col1:
        if st.button("Enable light level alarm", key="light_level_alarm_button"):
            st.session_state.light_level_alarm_active = True

    with col2:
        if st.session_state.light_level_alarm_active:
            st.write("Define thresholds for light level alarm :")
            light_level_min = st.number_input("Minimum Light Level Value", min_value=0.0, format="%.2f", key="light_level_min")
            light_level_max = st.number_input("Maximum Light Level Value", min_value=0.0, format="%.2f", key="light_level_max")
    with col4_light:
        l_p = st.empty()
       
    st.write("")
    
    # Humidity alarm controls
    col1, col2, col4_humidity = st.columns([1, 2, 2])
    with col1:
        if st.button("Enable humidity alarm", key="humidity_alarm_button"):
            st.session_state.humidity_alarm_active = True

    with col2:
        if st.session_state.humidity_alarm_active:
            st.write("Define thresholds for humidity alarm :")
            humidity_min = st.number_input("Minimum Humidity Value (%)", min_value=0.0, format="%.2f", key="humidity_min")
            humidity_max = st.number_input("Maximum Humidity Value (%)", min_value=0.0, format="%.2f", key="humidity_max")
    with col4_humidity:
        h_p = st.empty()

    return d_p, b_p, t_p, h_p,l_p, coll2, col4_battery, col4_Temperature, col4_light, col4_humidity, selected_date, battery_min, battery_max, temperature_min, temperature_max, light_level_min, light_level_max, humidity_min, humidity_max

def main3(d_p, b_p, t_p, h_p,l_p, coll2, col4_battery, col4_Temperature, col4_light, col4_humidity, selected_date, battery_min, battery_max, temperature_min, temperature_max, light_level_min, light_level_max, humidity_min, humidity_max):
    
    start_of_day = datetime.combine(selected_date, time.min)
    end_of_day = datetime.combine(selected_date, time.max)

    data = get_sensor_data()
    if data:
        new_df = pd.DataFrame(data)
        if os.path.exists('position_data.csv'):
            try:
                existing_df = pd.read_csv('position_data.csv', on_bad_lines='skip')
                df = pd.concat([existing_df, new_df], ignore_index=True)
            except pd.errors.EmptyDataError:
                df = new_df
        else:
            df = new_df
        df.to_csv('position_data.csv', index=False)
        
        # Convertir la colonne 'datetime' en objets datetime
        df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')

        # Filtrer les données pour n'inclure que celles du jour sélectionné
        df_filtered = df[(df['datetime'] >= start_of_day) & (df['datetime'] <= end_of_day)]

        total_energy = df_filtered['total_energy'].dropna().iloc[-1] if not df_filtered['total_energy'].dropna().empty else None
        operating_time = df_filtered['operating_time'].dropna().iloc[-1] if not df_filtered['operating_time'].dropna().empty else None

        # Sélectionner uniquement les colonnes d'intérêt
        columns_to_keep = ['datetime', 'processed_elevation', 'processed_azimuth', 'current_light_level', 'temperature', 'humidity', 'battery_level']
        df_filtered = df_filtered[columns_to_keep]
        
        # Créer 24 listes pour chaque heure de la journée
        hourly_data = []
        for hour in range(24):
            start_time = datetime.combine(selected_date, time(hour, 0, 0))
            end_time = datetime.combine(selected_date, time(hour, 59, 59))
            hourly_data.append(df_filtered[(df_filtered['datetime'] >= start_time) & (df_filtered['datetime'] <= end_time)])
        
        # Créer une liste contenant la première valeur de chaque liste horaire
        first_values = []
        for hourly_list in hourly_data:
            if not hourly_list.empty:  # Vérifier si la liste horaire n'est pas vide
                first_values.append(hourly_list.iloc[0])  # Ajouter la première valeur
            else:
                first_values.append(None)  # Ajouter None si la liste est vide
        data_report_list = first_values

        data = data[-1]
        temperature = data.get('temperature', 'N/A')
        humidity = data.get('humidity', 'N/A')
        light_level = data.get('current_light_level', 'N/A')
        battery_level = data.get('battery_level', 'N/A')
        if temperature != 'N/A':
            temperature = round(float(temperature), 2)
        if humidity != 'N/A':
            humidity = round(float(humidity), 2)
        if light_level != 'N/A':
            light_level = round(float(light_level), 2)
        if battery_level != 'N/A':
            battery_level = round(float(battery_level), 2)
                 
        # Check battery level against thresholds
        with col4_battery:
            if st.session_state.battery_alarm_active:
                if battery_level != 'N/A':
                    if battery_level < battery_min:
                        b_p.error(f"🔋⚠️ Alert: Battery level too low. {battery_level} is less than {battery_min}")
                    elif battery_level >= battery_max:
                        b_p.error(f"🔋⚠️ Alert: Battery level too high. {battery_level} exceeds {battery_max}")
                    else:
                        b_p.success(f"🔋 Battery level is within the safe range: {battery_level}")

        # Check temperature against thresholds
        with col4_Temperature :
            if st.session_state.temperature_alarm_active:
                if temperature != 'N/A':
                    if temperature < temperature_min:
                        t_p.error(f"🌡️⚠️ Alert: Temperature too low. {temperature} is less than {temperature_min}")
                    elif temperature > temperature_max:
                        t_p.error(f"🌡️⚠️ Alert: Temperature too high. {temperature} exceeds {temperature_max}")
                    else:
                        t_p.success(f"🌡️ Temperature is within the safe range: {temperature}")

        # Check light level against thresholds
        with col4_light :
            if st.session_state.light_level_alarm_active:
                if light_level != 'N/A':
                    if light_level < light_level_min:
                        l_p.error(f"🔆⚠️ Alert: Light level too low. {light_level} is less than {light_level_min}")
                    elif light_level > light_level_max:
                        l_p.error(f"🔆⚠️ Alert: Light level too high. {light_level} exceeds {light_level_max}")
                    else:
                        l_p.success(f"🔆 Light level is within the safe range: {light_level}")

        # Check humidity against thresholds
        with col4_humidity :
            if st.session_state.humidity_alarm_active:
                if humidity != 'N/A':
                    if humidity < humidity_min:
                        h_p.error(f"💧⚠️ Alert: Humidity too low. {humidity} is less than {humidity_min}")
                    elif humidity > humidity_max:
                        h_p.error(f"💧⚠️ Alert: Humidity too high. {humidity} exceeds {humidity_max}")
                    else:
                        h_p.success(f"💧 Humidity is within the safe range: {humidity}")
        # Generate PDF report
        pdf_file = generate_pdf_report(selected_date, total_energy, operating_time, data_report_list)

        # Ajouter un bouton de téléchargement pour le PDF
        with coll2:
            d_p.download_button(
                label="Download the PDF report",
                data=pdf_file,
                file_name=f"rapport_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pdf",
                mime="application/pdf"
            )
def run_periodically():
    placeholder = st.empty()
    d_p, b_p, t_p, h_p,l_p, coll2, col4_battery, col4_Temperature, col4_light, col4_humidity, selected_date, battery_min, battery_max, temperature_min, temperature_max, light_level_min, light_level_max, humidity_min, humidity_max = setup_alarm_controls()
    while True:
        with placeholder.container():
            main3(d_p, b_p, t_p, h_p,l_p, coll2, col4_battery, col4_Temperature, col4_light, col4_humidity, selected_date, battery_min, battery_max, temperature_min, temperature_max, light_level_min, light_level_max, humidity_min, humidity_max)
        ttm.sleep(1)

if __name__ == "__main__":
    run_periodically()