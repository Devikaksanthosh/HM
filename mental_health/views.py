import os
import numpy as np
import pandas as pd
import joblib
from django.shortcuts import render

# Load the trained model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "mental_health_model.pkl")
model = joblib.load(MODEL_PATH)

def predict_mental_health(request):
    result = None  # Default result
    
    if request.method == "POST":
        # Get form data
        age = int(request.POST.get("age"))
        gender = 1 if request.POST.get("gender") == "Female" else 0
        sleep_quality = int(request.POST.get("sleep_quality"))
        physical_activity = float(request.POST.get("physical_activity"))
        social_media_use = float(request.POST.get("social_media_use"))
        work_stress = int(request.POST.get("work_stress"))
        financial_stress = int(request.POST.get("financial_stress"))
        anxiety_level = int(request.POST.get("anxiety_level"))
        depression_score = int(request.POST.get("depression_score"))

        # Create input DataFrame
        user_input = pd.DataFrame([[age, gender, sleep_quality, physical_activity, social_media_use, 
                                    work_stress, financial_stress, anxiety_level, depression_score]],
                                  columns=["Age", "Gender", "Sleep Quality", "Physical Activity",
                                           "Social Media Use", "Work Stress Level", "Financial Stress",
                                           "Anxiety Level", "Depression Score"])

        # Make prediction
        prediction = model.predict(user_input)[0]
        result = "Good" if prediction == 0 else "At Risk"

    return render(request,"predict.html", {"result": result})
