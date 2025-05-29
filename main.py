# main.py
import os
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import requests
from dotenv import load_dotenv

# Load .env into os.environ
load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
TOMTOM_API_KEY     = os.getenv("TOMTOM_API_KEY")
if not OPENWEATHER_API_KEY or not TOMTOM_API_KEY:
    raise RuntimeError("Set OPENWEATHER_API_KEY & TOMTOM_API_KEY in your environment")

app = FastAPI(
    title="Weather & Traffic MCP",
    version="1.0.0",
    description="Fetch current weather (OpenWeather) and live traffic (TomTom) by lat/lon",
    servers=[{"url": "http://localhost:8000"}]
)

class Location(BaseModel):
    lat: float
    lon: float

@app.get("/weather", summary="Get current weather")
def get_weather(lat: float = Query(..., description="Latitude"),
                lon: float = Query(..., description="Longitude")):
    resp = requests.get(
        "https://api.openweathermap.org/data/2.5/weather",
        params={"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY, "units": "metric"},
        timeout=5,
        verify=False
    )
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return resp.json()

@app.get("/traffic", summary="Get live traffic flow")
def get_traffic(lat: float = Query(..., description="Latitude"),
                lon: float = Query(..., description="Longitude")):
    resp = requests.get(
        "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json",
        params={"point": f"{lat},{lon}", "key": TOMTOM_API_KEY},
        timeout=5,
        verify=False
    )
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return resp.json()

# Optional health check
@app.get("/healthz", include_in_schema=False)
def healthz():
    return {"status": "ok"}
