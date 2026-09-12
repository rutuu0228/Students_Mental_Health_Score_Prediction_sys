import joblib
import pandas as pd

from gemini_chatbot import chat_with_gemini
from feature_analysis import (
    analyze_student_features,
    create_ai_feature_context,
    get_score_category
)


# ============================================================
# LOAD MODEL
# ============================================================

preprocessor = joblib.load("Models/preprocessor.pkl")
model = joblib.load("Models/final_random_forest.pkl")


# ============================================================
# PREDICTION
# ============================================================

def predict_mental_health_score(student_data):

    input_df = pd.DataFrame([student_data])

    processed_data = preprocessor.transform(input_df)

    prediction = model.predict(processed_data)[0]

    return round(float(prediction), 2)


# ============================================================
# CREATE COMPLETE AI CONTEXT
# ============================================================

def create_prediction_context(student_data):

    # Predict score
    score = predict_mental_health_score(student_data)

    # Analyze student's features
    analysis = analyze_student_features(
        student_data,
        model=model,
        preprocessor=preprocessor
    )

    # Create Gemini-friendly context
    ai_context = create_ai_feature_context(
        student_data,
        score,
        analysis
    )

    # Add score category
    ai_context["category"] = get_score_category(score)

    return ai_context


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    sample_student = {

        "Name": "Rutu",

        "Age": 20,

        "Gender": "Female",

        "Academic_Level":
            "Undergraduate",

        "Most_Used_Platform":
            "Instagram",

        "Purpose_Of_Use":
            "Entertainment",

        "Avg_Daily_Usage_Hours":
            7.2,

        "Daily_Unlocks":
            95,

        "Study_Hours":
            6,

        "Physical_Activity_Hours":
            1,

        "Sleep_Hours_Per_Night":
            5,

        "Stress_Level":
            "High",

        "Country_Processed":
            "India"
    }


    # Name is not a model feature
    model_student_data = sample_student.copy()

    model_student_data.pop(
        "Name",
        None
    )


    # Create prediction context
    prediction_context = create_prediction_context(
        model_student_data
    )


    # Display prediction
    print("\n" + "=" * 60)
    print("STUDENT MENTAL HEALTH PREDICTION")
    print("=" * 60)

    print(
        "\nStudent:",
        sample_student["Name"]
    )

    print(
        "Predicted Score:",
        prediction_context["score"]
    )

    print(
        "Category:",
        prediction_context["category"]
    )


    # Display attention areas
    print(
        "\n🔴 AREAS NEEDING ATTENTION:"
    )

    for item in prediction_context[
        "needs_attention"
    ]:

        print(
            f"- {item['area']}: "
            f"{item['current_value']}"
        )


    # Display watch areas
    print(
        "\n🟡 AREAS THAT CAN IMPROVE:"
    )

    for item in prediction_context[
        "watch"
    ]:

        print(
            f"- {item['area']}: "
            f"{item['current_value']}"
        )


    # Display stable areas
    print(
        "\n🟢 FAVORABLE AREAS:"
    )

    for item in prediction_context[
        "stable"
    ]:

        print(
            f"- {item['area']}: "
            f"{item['current_value']}"
        )


    # Ask Gemini
    print(
        "\nAsking Gemini for "
        "personalized guidance..."
    )


    response = chat_with_gemini(

        "Please explain my result and "
        "give me personalized guidance.",

        prediction_context,

        student_name=sample_student[
            "Name"
        ]
    )


    print("\n" + "=" * 60)
    print("GEMINI AI ASSISTANT")
    print("=" * 60)

    print(response)