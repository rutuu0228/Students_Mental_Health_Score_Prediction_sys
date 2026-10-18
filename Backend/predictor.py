import os
import joblib
import pandas as pd
import requests
from pathlib import Path

from gemini_chatbot import chat_with_gemini
from feature_analysis import (
    analyze_student_features,
    create_ai_feature_context,
    get_score_category,
)

BASE_DIR = Path(__file__).resolve().parent

CLEANED_DATA_PATH = BASE_DIR / "data" / "cleaned_data.csv"
PREPROCESSOR_PATH = BASE_DIR / "models" / "preprocessor.pkl"
MODEL_PATH = BASE_DIR / "models" / "final_random_forest.pkl"

MODEL_URL = os.environ.get(
    "MODEL_URL",
    "https://github.com/rutuu0228/students-mental-health-backend/releases/download/v1.0.0/final_random_forest.pkl",
)

cleaned_data = pd.read_csv(CLEANED_DATA_PATH)
country_counts = cleaned_data["Country"].value_counts()

if not MODEL_PATH.exists():
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    response = requests.get(MODEL_URL, timeout=120)
    response.raise_for_status()

    with open(MODEL_PATH, "wb") as file:
        file.write(response.content)

preprocessor = joblib.load(PREPROCESSOR_PATH)
model = joblib.load(MODEL_PATH)


def predict_mental_health_score(student_data):
    input_df = pd.DataFrame([student_data])

    input_df["Country_Processed"] = input_df["Country"].apply(
        lambda x: "Rare_Country"
        if country_counts.get(x, 0) < 5
        else x
    )

    input_df = input_df.drop(columns=["Country"])

    processed_data = preprocessor.transform(input_df)
    prediction = model.predict(processed_data)[0]

    return round(float(prediction), 2)


def create_prediction_context(student_data):
    score = predict_mental_health_score(student_data)

    analysis = analyze_student_features(
        student_data,
        model=model,
        preprocessor=preprocessor,
    )

    ai_context = create_ai_feature_context(
        student_data,
        score,
        analysis,
    )

    ai_context["category"] = get_score_category(score)

    return ai_context


if __name__ == "__main__":
    sample_student = {
        "Name": "Rutu",
        "Age": 20,
        "Gender": "Female",
        "Academic_Level": "Undergraduate",
        "Most_Used_Platform": "Instagram",
        "Purpose_Of_Use": "Entertainment",
        "Avg_Daily_Usage_Hours": 7.2,
        "Daily_Unlocks": 95,
        "Study_Hours": 6,
        "Physical_Activity_Hours": 1,
        "Sleep_Hours_Per_Night": 5,
        "Stress_Level": "High",
        "Country_Processed": "India",
    }

    model_student_data = sample_student.copy()
    model_student_data.pop("Name", None)

    prediction_context = create_prediction_context(model_student_data)

    print("\n" + "=" * 60)
    print("STUDENT MENTAL HEALTH PREDICTION")
    print("=" * 60)
    print("\nStudent:", sample_student["Name"])
    print("Predicted Score:", prediction_context["score"])
    print("Category:", prediction_context["category"])

    print("\n🔴 AREAS NEEDING ATTENTION:")
    for item in prediction_context["needs_attention"]:
        print(f"- {item['area']}: {item['current_value']}")

    print("\n🟡 AREAS THAT CAN IMPROVE:")
    for item in prediction_context["watch"]:
        print(f"- {item['area']}: {item['current_value']}")

    print("\n🟢 FAVORABLE AREAS:")
    for item in prediction_context["stable"]:
        print(f"- {item['area']}: {item['current_value']}")

    print("\nAsking Gemini for personalized guidance...")
    response = chat_with_gemini(
        "Please explain my result and give me personalized guidance.",
        prediction_context,
        student_name=sample_student["Name"],
    )

    print("\n" + "=" * 60)
    print("GEMINI AI ASSISTANT")
    print("=" * 60)
    print(response)