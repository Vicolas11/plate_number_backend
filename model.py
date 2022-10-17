from joblib import load
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

def model():
    modelPath = os.path.join(PROJECT_ROOT, 'model/RandomForest.pkl')
    model = load(modelPath)
    return model
