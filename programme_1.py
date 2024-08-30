import os
import numpy as np
import pandas as pd
import pvlib
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, HourLocator
from datetime import datetime
import time as tm
import streamlit as st
import plotly.graph_objects as go
import json
import requests

def simulate_imu_data(accel_mean=0, accel_std=1, gyro_mean=0, gyro_std=0.1, mag_mean=0, mag_std=1):
    accel_data = np.random.normal(accel_mean, accel_std, 3)
    gyro_data = np.random.normal(gyro_mean, gyro_std, 3)
    mag_data = np.random.normal(mag_mean, mag_std, 3)
    return accel_data, gyro_data, mag_data

def calculate_orientation(accel_data, mag_data):
    ax, ay, az = accel_data
    mx, my, mz = mag_data
    roll = np.arctan2(ay, az)
    pitch = np.arctan2(-ax, np.sqrt(ay**2 + az**2))
    mag_x = mx * np.cos(pitch) + mz * np.sin(pitch)
    mag_y = mx * np.sin(roll) * np.sin(pitch) + my * np.cos(roll) - mz * np.sin(roll) * np.cos(pitch)
    yaw = np.arctan2(-mag_y, mag_x)
    return np.degrees(roll), np.degrees(pitch), np.degrees(yaw)

def calculate_velocity(accel_data, previous_velocity, delta_time):
    # Intégration de l'accélération pour obtenir la vitesse : v = u + at
    new_velocity = previous_velocity + accel_data * delta_time
    return new_velocity

def estimate_vehicle_speed(velocity):
    # Calcul de la norme du vecteur de vitesse (vitesse totale)
    velocity_total = np.linalg.norm(velocity)
    return velocity_total

def estimate_battery_level():
    return np.random.randint(0, 101)

def estimate_operating_time():
    return np.random.randint(0, 13)

def simulate_gps_data(lat_mean=31.6802337, lon_mean=-8.0440754, lat_std=0.001, lon_std=0.001):
    latitude = np.random.normal(lat_mean, lat_std) 
    longitude = np.random.normal(lon_mean, lon_std)
    return latitude, longitude

def simulate_light_level(min_level=300, max_level=800):
    return np.random.uniform(min_level, max_level)

def simulate_temperature(min_temp=15, max_temp=35):
    return np.random.uniform(min_temp, max_temp)

def simulate_humidity(min_humidity=30, max_humidity=90):
    return np.random.uniform(min_humidity, max_humidity)

# Simulation Functions
def currently_produced_energy():
    """Simulates the currently produced energy by the solar panel."""
    return np.random.uniform(1, 5)

def simulate_sun_sensor(latitudes, longitudes, timestamps):
    solar_positions = []
    for lat, lon, timestamp in zip(latitudes, longitudes, timestamps):
        solar_position = pvlib.solarposition.get_solarposition(timestamp, lat, lon)
        solar_positions.append(solar_position)
    return solar_positions

def simulate_actuator_movements(solar_positions, current_light_level):
    panel_angles = []
    for _, position in solar_positions.iterrows():
        if position['elevation'] < 0 or current_light_level < 200:
            elevation_angle = 0
            azimuth_angle = 0
        else:
            elevation_angle = position['elevation']
            azimuth_angle = position['azimuth']
        panel_angles.append((elevation_angle, azimuth_angle))
    return panel_angles

def process_angles(elevation_angle, azimuth_angle, yaw, pitch):
    if elevation_angle != 0 and azimuth_angle != 0:
        compensated_elevation = elevation_angle - pitch
        compensated_azimuth = azimuth_angle - yaw
    else:
        compensated_elevation = 0
        compensated_azimuth = 0
    return compensated_elevation, compensated_azimuth

def main():
    # Conditions initiales pour la vitesse
    initial_velocity = np.array([0, 0, 0])  # En supposant que la vitesse initiale est nulle
    previous_velocity = initial_velocity
    delta_time = 1  # Intervalle de temps entre chaque lecture des données IMU (en secondes)

    while True:
        current_light_level = simulate_light_level()
        current_temperature = simulate_temperature()
        current_humidity = simulate_humidity()
        current_datetime = datetime.now()
        now = datetime.now().replace(minute=0, second=0, microsecond=0)
        timestamps = now # Utilisation d'une chaîne au lieu d'une liste
        latitude, longitude = simulate_gps_data()
        latitudes = [latitude]
        longitudes = [longitude]
        solar_positions = simulate_sun_sensor(latitudes, longitudes, [now])
        solar_positions_df = pd.concat(solar_positions).reset_index(drop=True)
        panel_angles = simulate_actuator_movements(solar_positions_df, current_light_level)
        panel_angles_df = pd.DataFrame(panel_angles, columns=['elevation_angle', 'azimuth_angle'])
        accel_data, gyro_data, mag_data = simulate_imu_data()
        roll, pitch, yaw = calculate_orientation(accel_data, mag_data)
        # Process angles
        compensated_elevation, compensated_azimuth = process_angles(
            panel_angles_df['elevation_angle'][0], 
            panel_angles_df['azimuth_angle'][0], 
            yaw, pitch
        )

        # Vitesse
        accel_data = simulate_imu_data()
        velocity = calculate_velocity(accel_data, previous_velocity, delta_time)
        previous_velocity = velocity
        velocity_total = estimate_vehicle_speed(velocity)

        # Définir les valeurs d'énergie et d'angle
        current_energy = currently_produced_energy()

        battery_level = estimate_battery_level()
        operating_time = estimate_operating_time()

        # Créer le dictionnaire pour affichage
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")
        formatted_timestamps = timestamps.strftime("%Y-%m-%d %H:%M:%S.%f")
        new_data = {
            'datetime': formatted_datetime,   # Utilisation directe de la chaîne
            'timestamp': formatted_timestamps,  # Utilisation directe de la chaîne
            'latitude': latitude,  # Valeur flottante
            'longitude': longitude,  # Valeur flottante
            'sun_elevation': float(solar_positions_df['elevation'][0]),  # Valeur flottante
            'sun_azimuth': float(solar_positions_df['azimuth'][0]),  # Valeur flottante
            'panel_elevation': float(panel_angles_df['elevation_angle'][0]),  # Valeur flottante
            'panel_azimuth': float(panel_angles_df['azimuth_angle'][0]),  # Valeur flottante
            'processed_elevation': float(compensated_elevation),  # Valeur flottante
            'processed_azimuth': float(compensated_azimuth),  # Valeur flottante
            'orientation_north': float(yaw),  # Valeur flottante
            'pitch': float(pitch),  # Valeur flottante
            'roll': float(roll),  # Valeur flottante
            'current_light_level': float(current_light_level),  # Valeur flottante
            'temperature': float(current_temperature),  # Valeur flottante
            'humidity': float(current_humidity),  # Valeur flottante
            'velocity_total': float(velocity_total),  # Valeur flottante
            'current_energy': float(current_energy),  # Valeur flottante
            'battery_level': int(battery_level),  # Valeur entière
            'operating_time': int(operating_time)  # Valeur entière
        }

        # Afficher le JSON pour vérifier son contenu
        #json_payload = json.dumps(new_data, indent=4)
        #print("JSON Payload being sent:\n", json_payload)

        # Envoyer la requête POST
        response = requests.post("http://192.168.174.45:8000/send_data/", json=new_data)
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Content: {response.text}")

        tm.sleep(1)

if __name__ == "__main__":
    main()
