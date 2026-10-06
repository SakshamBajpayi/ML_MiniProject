from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import sys
import os

# Add root to sys path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.predict import predict_single

app = FastAPI(title="Seismic Intelligence API")

# Enable CORS for the React frontend (running on port 5173 typically for Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BuildingData(BaseModel):
    geo_level_1_id: int = Field(default=10, description="Geographic sector level 1")
    geo_level_2_id: int = Field(default=0)
    geo_level_3_id: int = Field(default=0)
    count_floors_pre_eq: int = Field(default=2)
    age: int = Field(default=15)
    area_percentage: int = Field(default=5)
    height_percentage: int = Field(default=5)
    count_families: int = Field(default=1)
    
    land_surface_condition: str = Field(default='t')
    foundation_type: str = Field(default='r')
    roof_type: str = Field(default='n')
    ground_floor_type: str = Field(default='f')
    other_floor_type: str = Field(default='q')
    position: str = Field(default='s')
    plan_configuration: str = Field(default='d')
    legal_ownership_status: str = Field(default='v')
    
    has_superstructure_adobe_mud: int = Field(default=0)
    has_superstructure_mud_mortar_stone: int = Field(default=1)
    has_superstructure_stone_flag: int = Field(default=0)
    has_superstructure_cement_mortar_stone: int = Field(default=0)
    has_superstructure_mud_mortar_brick: int = Field(default=0)
    has_superstructure_cement_mortar_brick: int = Field(default=0)
    has_superstructure_timber: int = Field(default=0)
    has_superstructure_bamboo: int = Field(default=0)
    has_superstructure_rc_non_engineered: int = Field(default=0)
    has_superstructure_rc_engineered: int = Field(default=0)
    has_superstructure_other: int = Field(default=0)
    
    has_secondary_use: int = Field(default=0)
    has_secondary_use_agriculture: int = Field(default=0)
    has_secondary_use_hotel: int = Field(default=0)
    has_secondary_use_rental: int = Field(default=0)
    has_secondary_use_institution: int = Field(default=0)
    has_secondary_use_school: int = Field(default=0)
    has_secondary_use_industry: int = Field(default=0)
    has_secondary_use_health_post: int = Field(default=0)
    has_secondary_use_gov_office: int = Field(default=0)
    has_secondary_use_use_police: int = Field(default=0)
    has_secondary_use_other: int = Field(default=0)

@app.post("/api/predict")
async def predict_damage(data: BuildingData):
    try:
        features = data.model_dump()
        
        # Resolve absolute paths to the models directory safely
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        m_path = os.path.join(base_dir, 'models', 'best_model.pkl')
        p_path = os.path.join(base_dir, 'models', 'preprocessor.pkl')
        
        result = predict_single(
            features_dict=features,
            model_path=m_path,
            preprocessor_path=p_path
        )
        return {"status": "success", "data": result}
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")

@app.get("/api/health")
async def health_check():
    return {"status": "online", "system": "Seismic Inference Engine"}
