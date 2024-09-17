import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime
import os
import matplotlib.pyplot as plt
import time as tmmm 
from streamlit_option_menu import option_menu
import Enviromental_Data
import UGV_Monitoring
import Report_Alarm
import requests

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

def plot_energy_histories(monthly_sums, consumption):
    """Plots energy production and consumption histories and displays them in Streamlit."""
    
    # Define month names
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    # Plotting
    plt.figure(figsize=(12, 5))  # Smaller figure size for compact view

    # Adjust subplot parameters to shift the first plot to the left
    plt.subplot(1, 2, 1, position=[0.1, 0.15, 0.4, 0.7])
    plt.bar(month_names, monthly_sums, color='coral', alpha=0.7, label='Energy Produced')
    plt.xlabel('Month')
    plt.ylabel('Energy (Watts)')
    plt.title('Energy Production History', fontsize=15)
    plt.xticks(rotation=45, fontsize=8)
    plt.yticks(fontsize=8)
    plt.grid(True)

    # Plot energy consumption
    plt.subplot(1, 2, 2)
    plt.bar(month_names, consumption, color='cornflowerblue', alpha=0.7, label='Energy Consumed')
    plt.xlabel('Month')
    plt.ylabel('Energy (Watts)')
    plt.title('Energy Consumption History', fontsize=15)
    plt.xticks(rotation=45, fontsize=8)
    plt.yticks(fontsize=8)
    plt.grid(True)

    plt.tight_layout()
    
    # Display in Streamlit
    st.pyplot(plt)

def main_loop():
    """Main loop to simulate periodic updates."""
    st.title('Dashboard')
    selected = option_menu(
        menu_title=None,
        options=["Solar panel monitoring", "UGV monitoring", "Environmental DATA", "Report and Alarm Notifications"],
        icons=["lightning charge", "ev-front", "graph-up", "alarm"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {
                "padding": "0!important",
                "font-size": "20px",
                "background-color": "#ccd8eb",
            },
            "nav-link": {
                "font-size": "15px",
                "text-align": "middle",
                "margin": "0px",
                "--hover-color": "#516ac4",
            },
            "nav-link-selected": {
                "background-color": "#516ac4",
            },
        }
    )

    if selected == "Solar panel monitoring":
        st.markdown("<h1 style='text-align: center; font-size: 22px; color: royalblue; margin-top: 10px;'>Solar Panel Monitoring</h1>", unsafe_allow_html=True)

        # Create placeholder elements
        placeholder = st.empty()
        
        while True:
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
                # Filtrer les données pour n'inclure que celles du jour en cours
                start_of_day = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                end_of_day = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)

                # Sélectionner uniquement les colonnes d'intérêt
                columns_to_keep = ['datetime', 'current_energy']
                df_fil = df[columns_to_keep]

                # Convertir la colonne 'datetime' en objets datetime
                df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
                # Filtrer les données pour inclure uniquement celles du jour en cours
                df_filtered = df[(df['datetime'] >= start_of_day) & (df['datetime'] <= end_of_day)]
                daily_energy_filtered = df_filtered['current_energy']

                # Filtrer les données pour ne conserver que celles de l'année en cours
                df_fil['datetime'] = pd.to_datetime(df_fil['datetime'], errors='coerce')
                current_year = datetime.now().year
                filtered_data = df_fil[df_fil['datetime'].dt.year == current_year]
                # Créer une liste pour stocker la somme des énergies pour chaque mois
                months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                monthly_sums = []

                # Calculer la somme des 'current_energy' pour chaque mois et l'ajouter à la liste
                for month_index in range(1, 13):
                    # Sélectionner les données du mois actuel
                    month_data = filtered_data[filtered_data['datetime'].dt.month == month_index]
                    # Calculer la somme de 'current_energy' pour ce mois
                    month_sum = month_data['current_energy'].sum()/3600
                    # Ajouter la somme à la liste
                    monthly_sums.append(month_sum)
                # Initialize the consumption list to store cumulative values
                consumption = []
                cumulative_sum = 0
                for value in monthly_sums:
                    cumulative_sum += value  # Add the current value to the cumulative sum
                    consumption.append(cumulative_sum) 
                
                data = data[-1]
                with placeholder.container():
                    # Define energy and angle values
                    current_energy = data.get('current_energy', 'N/A')
                    daily_produced_energy = daily_energy_filtered.sum() / 3600
                    lifetime_total_energy = df['current_energy'].sum() / 3600
                    total_capacity = 100
                    daily_produced_energy = round(float(daily_produced_energy), 2)
                    lifetime_total_energy = round(float(lifetime_total_energy), 2)
                    total_capacity = round(float(total_capacity), 2)
                    panel_elevation = data.get('processed_elevation', 'N/A')
                    panel_azimuth = data.get('processed_azimuth', 'N/A')
                    if current_energy != 'N/A':
                        current_energy = round(float(current_energy), 2)
                    if panel_elevation != 'N/A':
                        panel_elevation = round(float(panel_elevation), 2)
                    if panel_azimuth != 'N/A':
                        panel_azimuth = round(float(panel_azimuth), 2)

                    # Custom CSS for styling
                    st.markdown("""
                    <style>
                    .large-font {
                        font-size:16px !important;
                        font-weight: bold;
                    }
                    
                    .value-box {
                        border: 2px  gray; 
                        border-radius: 8px;
                        padding: 15px; 
                        text-align: center;
                        margin-bottom: 15px;
                        position: relative;
                        font-size: 12px;
                        background-color: #cbdbf5; 
                    }
                    .unit {
                        font-size: 12px;
                        color:#769ddb;
                        position: absolute;
                        bottom: 3px;
                        right: 10px;
                    }
                    .orange-title {
                        color: #325080;
                        font-size: 13px;
                        margin-bottom: 5px;
                        margin-top: 20px; /* Adjusted margin */
                            
                    }
                    .content {
                        padding-top: 10px;
                            
                    }
                    </style>
                    """, unsafe_allow_html=True)

                    # Define layout
                    col1, col2 = st.columns(2)

                    # Column 1
                    with col1:
                        st.markdown("<div class='orange-title'>Currently Produced Energy</div>", unsafe_allow_html=True)
                        st.markdown(
                            f"<div class='value-box'><span class='large-font'>{current_energy if isinstance(current_energy, float) else 'N/A'}</span><div class='unit'>Wh</div></div>",
                            unsafe_allow_html=True)
                        st.markdown("<div class='orange-title'>maximum power</div>", unsafe_allow_html=True)
                        st.markdown(
                            f"<div class='value-box'><span class='large-font'>{total_capacity if isinstance(total_capacity, float) else 'N/A'}</span><div class='unit'>W</div></div>",
                            unsafe_allow_html=True)
                        st.markdown("<div class='orange-title'>Panel Elevation</div>", unsafe_allow_html=True)
                        st.markdown(
                            f"<div class='value-box'><span class='large-font'>{panel_elevation if isinstance(panel_elevation, float) else 'N/A'}</span><div class='unit'>°</div></div>",
                            unsafe_allow_html=True)
                    # Column 2
                    with col2:
                        st.markdown("<div class='orange-title'>daily produced energy</div>", unsafe_allow_html=True)
                        st.markdown(
                            f"<div class='value-box'><span class='large-font'>{daily_produced_energy if isinstance(daily_produced_energy, float) else 'N/A'}</span><div class='unit'>Wh</div></div>",
                            unsafe_allow_html=True)
                        st.markdown("<div class='orange-title'>Lifetime Energy</div>", unsafe_allow_html=True)
                        st.markdown(
                            f"<div class='value-box'><span class='large-font'>{lifetime_total_energy if isinstance(lifetime_total_energy, float) else 'N/A'}</span><div class='unit'>Wh</div></div>",
                            unsafe_allow_html=True)
                        st.markdown("<div class='orange-title'>Panel Azimuth</div>", unsafe_allow_html=True)
                        st.markdown(
                            f"<div class='value-box'><span class='large-font'>{panel_azimuth if isinstance(panel_azimuth, float) else 'N/A'}</span><div class='unit'>°</div></div>",
                            unsafe_allow_html=True)
                    # Plot energy histories
                    st.markdown("<h2 style='text-align: center; margin-bottom: 30px; font-size: 20px;'>Energy Production and Consumption History</h2>", unsafe_allow_html=True)
                    plot_energy_histories(monthly_sums, consumption)

            tmmm.sleep(1)

    elif selected == 'Environmental DATA':
        placeholder = st.empty()
        while True:
            with placeholder.container():
                Enviromental_Data.main()
            tmmm.sleep(1)  

    elif selected == 'UGV monitoring':
        placeholder = st.empty()
        while True:
            with placeholder.container():
                UGV_Monitoring.main1()  
            tmmm.sleep(1)  

    elif selected == 'Report and Alarm Notifications':
        Report_Alarm.run_periodically() 

if __name__ == "__main__":
    main_loop()
