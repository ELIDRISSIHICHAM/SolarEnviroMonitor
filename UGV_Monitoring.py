import time as tmm
from datetime import datetime
import numpy as np
import pandas as pd
import os
import plotly.graph_objects as go
import streamlit as st
import matplotlib.pyplot as plt
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

def plot_gauge(indicator_number, indicator_color, indicator_suffix, indicator_title, max_bound):
    fig = go.Figure(
        go.Indicator(
            value=indicator_number,
            mode="gauge+number",
            domain={"x": [0, 0.75], "y": [0, 0.75]},
            number={"suffix": indicator_suffix, "font.size": 16},
            gauge={"axis": {"range": [0, max_bound], "tickwidth": 2}, "bar": {"color": indicator_color}},
            title={"text": indicator_title, "font": {"size": 20}},
        )
    )
    fig.update_layout(
        height=200,
        margin=dict(l=10, r=10, t=50, b=10, pad=8),
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_speed_history(time_stamps_filtered,velocity_total_filtered,start_of_day, end_of_day):

    plt.figure(figsize=(20, 15))
    plt.xlim([start_of_day, end_of_day])
    plt.plot(time_stamps_filtered, velocity_total_filtered, marker='o', color='dodgerblue', linestyle='-', linewidth=2, markersize=30)
    plt.xlabel('Hours', fontsize=30)
    plt.ylabel('Speed Variation (km/h)', fontsize=30)
    plt.title('Speed History', fontsize=34, loc='center')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    st.pyplot(plt)

def main1():
    st.markdown("<h1 style='text-align: center; font-size: 22px; color: royalblue;'>UGV Monitoring</h1>", unsafe_allow_html=True)

    data = get_sensor_data()
    #st.write("Données récupérées :", data)  # Affiche les données pour vérifier leur contenu
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

        # Convertir la colonne 'datetime' en objets datetime
        df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
        # Filtrer les données pour inclure uniquement celles du jour en cours
        df_filtered = df[(df['datetime'] >= start_of_day) & (df['datetime'] <= end_of_day)]
        
        # Mettre à jour le tracé en fonction des données filtrées
        time_stamps_filtered = df_filtered['datetime']
        velocity_total_filtered = df_filtered['velocity_total']
        data = data[-1]

        # Create containers to update plots dynamically
        col1, col2, col3 = st.columns(3)
        col5, col6 = st.columns(2)

        # Update gauges
        with col1:
            plot_gauge(
                indicator_number=data.get('velocity_total', 0),  # Default to 0 if key is missing
                indicator_color="#0068C9",
                indicator_suffix="km/h",
                indicator_title="Vehicle Speed",
                max_bound=100,
            )

        with col2:
            plot_gauge(
                indicator_number=data.get('battery_level', 0),  # Default to 0 if key is missing
                indicator_color="#00f94b",
                indicator_suffix="%",
                indicator_title="Battery Level",
                max_bound=100,
            )

        with col3:
            plot_gauge(
                indicator_number=data.get('operating_time', 0),  # Default to 0 if key is missing
                indicator_color="#f9a600",
                indicator_suffix="min",
                indicator_title="Operating Time",
                max_bound=180,
            )

        # Update map
        st.subheader("UGV Location")
        lat = data.get('latitude', 0)  # Default to 0 if key is missing
        lon = data.get('longitude', 0)  # Default to 0 if key is missing
        fig_map = go.Figure(go.Scattermapbox(
            mode="markers+text",
            lon=[lon],
            lat=[lat],
            marker=dict(size=14),
            text=["Vehicle Position"],
            textposition="top right"
        ))
        fig_map.update_layout(
            mapbox=dict(
                style="open-street-map",
                center=dict(lat=lat, lon=lon),
                zoom=15
            ),
            margin=dict(l=0, r=0, t=0, b=0)
        )
        st.plotly_chart(fig_map, use_container_width=True)

        # Update position and speed history
        with col5:
            st.subheader("Position History")
            st.write(df)

        with col6:
            st.subheader("Speed History")
            plot_speed_history(time_stamps_filtered,velocity_total_filtered,start_of_day, end_of_day)

if __name__ == "__main__":
    main1()
# Call the main1 function directly if the option "UGV monitoring" is selected
# main1() should be called where appropriate in your Streamlit app
