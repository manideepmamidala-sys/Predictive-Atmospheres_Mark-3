from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import traceback
import uvicorn
import os
from contextlib import asynccontextmanager
import pandas as pd
from pathlib import Path

from src.config import get_config
from src.services.container import ServiceContainer

# Global cache for the container
pa_container = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global pa_container
    print("Initializing ServiceContainer and loading Predictive Atmospheres model...")
    # This automatically loads artifacts/models/random_forest.joblib inside its property
    pa_container = ServiceContainer(config=get_config())
    # trigger lazy load
    _ = pa_container.model
    yield

app = FastAPI(title="Predictive Atmospheres API", lifespan=lifespan)

# Add CORS Middleware
vercel_url = os.environ.get("VERCEL_URL", "https://predictive-atmospheres.vercel.app")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[vercel_url, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PredictionRequest(BaseModel):
    length_m: float
    width_m: float
    height_m: float
    num_doors: int
    door_area_m2: float
    num_windows: int
    window_area_m2: float
    daylight_factor_pct: float
    illuminance_lux: float
    cct_k: float
    walkable_floor_area_m2: float
    room_volume_m3: float
    space_use_type: str

@app.post("/predict")
async def predict(request: PredictionRequest):
    if pa_container is None:
        raise HTTPException(status_code=503, detail="Model container not initialized.")
        
    try:
        # Map fields to what the PredictionService expects
        features_dict = {
            'Length_m': request.length_m,
            'Width_m': request.width_m,
            'Height_m': request.height_m,
            'Num_Doors': float(request.num_doors),
            'Door_Area_m2': request.door_area_m2,
            'Num_Windows': float(request.num_windows),
            'Window_Area_m2': request.window_area_m2,
            'Daylight_Factor_pct': request.daylight_factor_pct,
            'Illuminance_lux': request.illuminance_lux,
            'CCT_K': request.cct_k,
            'Walkable_Floor_Area_m2': request.walkable_floor_area_m2,
            'Volume_m3': request.room_volume_m3,
            'Day_or_Night_Day': 1.0,
            'Day_or_Night_Night': 0.0,
            'Type_of_Space_Bedroom': 1.0 if request.space_use_type.lower() == 'bedroom' else 0.0,
            'Type_of_Space_Living Room': 1.0 if request.space_use_type.lower() == 'living room' else 0.0,
            'Type_of_Space_Workplace': 1.0 if request.space_use_type.lower() == 'workplace' else 0.0,
            'Type_of_Space_Classroom': 1.0 if request.space_use_type.lower() == 'classroom' else 0.0,
            'Type_of_Space_Cafeteria': 1.0 if request.space_use_type.lower() == 'cafeteria' else 0.0,
            'Length_to_Width_Ratio': request.length_m / max(request.width_m, 0.1),
            'Floor_Area_m2': request.length_m * request.width_m,
            'Wall_Area_m2': 2 * (request.length_m * request.height_m + request.width_m * request.height_m),
        }
        
        # Calculate derived ratio fields to avoid prediction failure if not passed
        features_dict['Door_to_Wall_Ratio'] = (request.door_area_m2 * request.num_doors) / max(features_dict['Wall_Area_m2'], 1.0)
        features_dict['Window_to_Wall_Ratio'] = (request.window_area_m2 * request.num_windows) / max(features_dict['Wall_Area_m2'], 1.0)
        features_dict['Walkable_to_Floor_Ratio'] = request.walkable_floor_area_m2 / max(features_dict['Floor_Area_m2'], 1.0)

        prediction = pa_container.prediction_service.predict_with_confidence(features_dict, n_passes=10)
        
        return {
            "neuro_score": float(prediction.neuro_score),
            "valence": float(prediction.valence),
            "arousal": float(prediction.arousal),
            "confidence_pct": float(prediction.confidence_score * 100),
            "atmospheric_label": str(prediction.atmosphere)
        }
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"CRITICAL API CRASH:\n{error_trace}")
        raise HTTPException(status_code=500, detail=str(e))

class OptimizeRequest(BaseModel):
    target_neuro_score: float

@app.post("/inverse-optimize")
async def optimize(request: OptimizeRequest):
    if pa_container is None:
        raise HTTPException(status_code=503, detail="Model container not initialized.")
        
    try:
        raw_result = pa_container.optimization_service.optimize_for_target(
            target_score=request.target_neuro_score
        )
        safe_result = {
            "length": float(raw_result.length),
            "width": float(raw_result.width),
            "height": float(raw_result.height),
            "predicted_valence": float(raw_result.predicted_valence),
            "predicted_arousal": float(raw_result.predicted_arousal),
            "neuro_score": float(raw_result.neuro_score),
            "target_achieved": float(raw_result.target_achieved),
            "samples_evaluated": int(raw_result.samples_evaluated),
            "full_features": {str(k): float(v) for k, v in raw_result.full_features.items()}
        }
        return safe_result
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"CRITICAL API CRASH:\n{error_trace}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok", "model_loaded": pa_container is not None}

@app.get("/config")
async def get_configuration():
    return {"version": "1.0", "status": "active"}

@app.get("/data/fusion")
async def get_fusion_data():
    try:
        data_path = Path(__file__).resolve().parent / "data" / "processed" / "fusion_analysis.parquet"
        if not data_path.exists():
            raise HTTPException(status_code=404, detail="Data not found")
        df = pd.read_parquet(data_path)
        # Convert to records format and handle NaNs/Infs for JSON parsing
        return df.fillna(0).to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
