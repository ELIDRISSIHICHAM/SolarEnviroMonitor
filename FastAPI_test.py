from fastapi import FastAPI
from pydantic import BaseModel

# Définir un modèle de données pour les données des capteurs
class SensorData(BaseModel):
    datetime: str
    timestamp: str
    latitude: float
    longitude: float
    sun_elevation: float
    sun_azimuth: float
    panel_elevation: float
    panel_azimuth: float
    processed_elevation: float
    processed_azimuth: float
    orientation_north: float
    pitch: float
    current_light_level: float 
    temperature: float
    humidity: float
    velocity_total: float
    current_energy: float
    battery_level: float
    operating_time: float

app = FastAPI()

# Liste pour stocker toutes les données reçues
sensor_data_list = []

@app.get("/")
async def read_root():
    return {"message": "Hello World"}

# Endpoint pour recevoir les données du véhicule
@app.post("/send_data/")
async def receive_data(new_data: SensorData):
    sensor_data_list.append(new_data)
    return {"status": "Data received successfully"}

# Endpoint pour envoyer toutes les données du capteur enregistrées
@app.get("/get_data/")
async def get_data():
    if sensor_data_list:
        # Envoyer toutes les données et vider la liste après l'envoi
        data_to_send = sensor_data_list.copy()
        sensor_data_list.clear()
        return data_to_send
    return {"error": "No data available"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
