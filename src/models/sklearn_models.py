import numpy as np
import torch
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.multioutput import MultiOutputRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

def get_random_forest_model():
    base_rf = RandomForestRegressor(n_estimators=100, random_state=42)
    model = make_pipeline(StandardScaler(), MultiOutputRegressor(base_rf))
    return model

def get_ridge_model():
    base_ridge = Ridge(alpha=1.0)
    model = make_pipeline(StandardScaler(), MultiOutputRegressor(base_ridge))
    return model
