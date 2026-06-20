from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import traceback
import uvicorn
from contextlib import asynccontextmanager

from src.config import get_config
from src.services.container import ServiceContainer
from src.models.train import Trainer

# Global cache for the container
pa_container = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    On startup, instantiate the model exactly as the Streamlit app does to 
    maintain the Single Source of Truth (SSOT).
    """
    global pa_container
    print("Initializing ServiceContainer and loading Predictive Atmospheres model...")
    
    config = get_config()
    trainer = Trainer(model_type='PyTorch FFNN', config=config)
    result = trainer.train()
    
    pa_container = ServiceContainer(config=config, model=result.model)
    pa_container.set_feature_config(feature_names=result.feature_names, scaler=result.scaler)
    
    yield

app = FastAPI(title="Predictive Atmospheres API", lifespan=lifespan)

class PredictionRequest(BaseModel):
    Length_m: float
    Width_m: float
    Height_m: float
    Num_Doors: float
    Door_Area_m2: float
    Num_Windows: float
    Window_Area_m2: float
    Daylight_Factor_pct: float
    Illuminance_lux: float
    CCT_K: float
    Walkable_Floor_Area_m2: float
    Day_or_Night_Day: int = 1
    Day_or_Night_Night: int = 0

@app.post("/predict")
async def predict(request: PredictionRequest):
    if pa_container is None:
        raise HTTPException(status_code=503, detail="Model container not initialized.")
        
    try:
        features_dict = request.model_dump()
        prediction = pa_container.prediction_service.predict_with_confidence(features_dict, n_passes=50)
        
        return {
            "Valence": float(prediction.valence),
            "Arousal": float(prediction.arousal),
            "NeuroScore": float(prediction.neuro_score),
            "Confidence": float(prediction.confidence_score),
            "Atmosphere": str(prediction.atmosphere),
            "EmotionWeights": prediction.emotion_weights
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class OptimizeRequest(BaseModel):
    target_neuro_score: float

@app.post("/optimize")
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

if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
