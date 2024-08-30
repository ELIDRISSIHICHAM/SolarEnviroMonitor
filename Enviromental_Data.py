# Enviromental data
import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime
import time as t
import os
import matplotlib.pyplot as plt
import seaborn as sns
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

# Set Seaborn style for better aesthetics
sns.set(style="whitegrid")

def plot_temperature_history(time_stamps_filtered, temperature_filtered, start_of_day, end_of_day):
    plt.figure(figsize=(8, 4))
    plt.xlim([start_of_day, end_of_day])
    plt.plot(time_stamps_filtered, temperature_filtered, marker='o', color='green', linestyle='-', linewidth=2, markersize=6)
    plt.xlabel('Hour', fontsize=12)
    plt.ylabel('Temperature (°C)', fontsize=12)
    plt.title('Temperature History', fontsize=14, loc='center')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    st.pyplot(plt)

def plot_humidity_history(time_stamps_filtered,humidity_filtered,start_of_day,end_of_day):

    plt.figure(figsize=(8, 4))
    plt.xlim([start_of_day, end_of_day])
    plt.plot(time_stamps_filtered, humidity_filtered, marker='o', color='royalblue', linestyle='-', linewidth=2, markersize=6)
    plt.xlabel('Hour', fontsize=12)
    plt.ylabel('Humidity (%)', fontsize=12)
    plt.title('Humidity History', fontsize=14, loc='center')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    st.pyplot(plt)

def plot_light_level_history(time_stamps_filtered, light_levels_filtered, start_of_day, end_of_day):
    plt.figure(figsize=(8, 4))
    plt.xlim([start_of_day, end_of_day])
    plt.plot(time_stamps_filtered, light_levels_filtered, marker='o', color='darkorange', linestyle='-', linewidth=2, markersize=6)
    plt.xlabel('Hour', fontsize=12)
    plt.ylabel('Light Level (lux)', fontsize=12)
    plt.title('Light Level History', fontsize=14, loc='center')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    st.pyplot(plt)

def main():
    st.markdown("<h1 style='text-align: center; font-size: 24px; color: royalblue;'>Environmental Data</h1>", unsafe_allow_html=True)
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

        # Convertir la colonne 'datetime' en objets datetime
        df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
        # Filtrer les données pour inclure uniquement celles du jour en cours
        df_filtered = df[(df['datetime'] >= start_of_day) & (df['datetime'] <= end_of_day)]

        # Mettre à jour le tracé en fonction des données filtrées
        time_stamps_filtered = df_filtered['datetime']
        light_levels_filtered = df_filtered['current_light_level']
        temperature_filtered = df_filtered['temperature']
        humidity_filtered = df_filtered['humidity']
        data = data[-1]
    
        temperature = data.get('temperature', 'N/A')
        humidity = data.get('humidity', 'N/A')
        light_level = data.get('current_light_level', 'N/A')
        if temperature != 'N/A':
            temperature = round(float(temperature), 2)
        if humidity != 'N/A':
            humidity = round(float(humidity), 2)
        if light_level != 'N/A':
           light_level = round(float(light_level), 2)
        # CSS to style the container and title
        st.markdown(
            """
            <style>
            .container-wrapper {
                display: flex;
                align-items: flex-start;
                gap: 90px;
            }
            .left-container {
                border: 2px  royalblue;
                border-radius: 10px;
                padding: 15px;
                text-align: center;
                height: 90px;
                width: 200px;
                position: relative;
                background-color:  #cbdbf5;
                margin-top: 15px;
                margin-bottom: 70px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                box-shadow: 2px 4px 8px rgba(0, 0, 0, 0.1);
            }
            .container-title {
                font-size: 15px;
                position: center;
                top: 15px;
                left: 0;
                width: 100%;
                text-align: top;
                color: royalblue;
                font-weight: bold;
            }
            .container-unit {
                font-size: 16px;
                position: right bottom;
                color: royalblue;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        col1, col2, col3 = st.columns([2, 2, 2])

        with col1:
            st.markdown(
                f"""
                <div class="left-container">
                    <div class="container-title">Temperature</div>
                    <div style="font-size: 24px; font-weight: bold;">{temperature}</div>
                    <div class="container-unit">°C</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                f"""
                <div class="left-container">
                    <div class="container-title">humidity</div>
                    <div style="font-size: 24px; font-weight: bold;">{humidity}</div>
                    <div class="container-unit">%</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col3:
            st.markdown(
                f"""
                <div class="left-container">
                    <div class="container-title">light level</div>
                    <div style="font-size: 24px; font-weight: bold;">{light_level}</div>
                    <div class="container-unit">lux</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        col4 = st.columns(1)[0]
    
        with col4:
            st.subheader("Temperature History")
            plot_temperature_history(time_stamps_filtered, temperature_filtered, start_of_day, end_of_day)
        col5 = st.columns(1)[0]
        with col5:
            st.subheader("humidity History")
            plot_humidity_history(time_stamps_filtered,humidity_filtered,start_of_day,end_of_day)
        col6 = st.columns(1)[0]
        with col6:
            st.subheader("light_level History")
            plot_light_level_history(time_stamps_filtered, light_levels_filtered, start_of_day, end_of_day) 