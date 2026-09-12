import pandas as pd
import joblib
from pathlib import Path


# ============================================================
# SCORE CATEGORY
# ============================================================

def get_score_category(score):
    """
    Project-defined Mental Health Score interpretation.
    """

    if score < 4.0:
        return "Low"

    elif score < 7.0:
        return "Moderate"

    elif score < 9.0:
        return "Good"

    else:
        return "Excellent / Stable"


# ============================================================
# FEATURE RULES
# ============================================================

FEATURE_RULES = {

    # --------------------------------------------------------
    # DAILY SCREEN USAGE
    # --------------------------------------------------------

    "Avg_Daily_Usage_Hours": {

        "label": "Daily screen usage",

        "direction": "lower_is_better",

        "attention": lambda x: x > 6.3,

        "stable": lambda x: x <= 3.8,

        "reference": 3.1,

        "attention_message":
            "Your daily screen usage is relatively high. "
            "Gradually reducing unnecessary screen time may "
            "be a useful area to focus on.",

        "stable_message":
            "Your daily screen usage is in a favorable range. "
            "Try to maintain this healthy balance."
    },


    # --------------------------------------------------------
    # DAILY PHONE UNLOCKS
    # --------------------------------------------------------

    "Daily_Unlocks": {

        "label": "Daily phone unlocks",

        "direction": "lower_is_better",

        # Exact project interpretation requested
        "categories": [

            {
                "min": float("-inf"),
                "max": 30,
                "status": "stable",
                "interpretation": "Favorable",
                "emoji": "🟢"
            },

            {
                "min": 31,
                "max": 50,
                "status": "stable",
                "interpretation": "Good / maintain",
                "emoji": "🟢"
            },

            {
                "min": 51,
                "max": 100,
                "status": "watch",
                "interpretation": "Can improve",
                "emoji": "🟡"
            },

            {
                "min": 101,
                "max": 200,
                "status": "attention",
                "interpretation": "Needs attention",
                "emoji": "🟠"
            },

            {
                "min": 201,
                "max": float("inf"),
                "status": "attention",
                "interpretation": "High attention",
                "emoji": "🔴"
            }
        ],

        "reference": 30,

        "attention_message":
            "You are checking your phone quite frequently. "
            "Try reducing unnecessary phone checking, especially "
            "during study and focused time.",

        "watch_message":
            "Your phone unlock frequency can be improved. "
            "Try reducing unnecessary phone checking during "
            "study, work, and focused time.",

        "stable_message":
            "Your daily phone unlocks are in a favorable range. "
            "Keep maintaining this mindful phone usage."
    },


    # --------------------------------------------------------
    # STUDY HOURS
    # --------------------------------------------------------

    "Study_Hours": {

        "label": "Study hours",

        "direction": "higher_is_better",

        "attention": lambda x: x <= 1.5,

        "stable": lambda x: x > 4.2,

        "reference": 5.1,

        "attention_message":
            "Your study time is relatively low. "
            "A simple and consistent study routine may help "
            "you stay academically balanced.",

        "stable_message":
            "Your study routine is in a favorable range. "
            "Keep maintaining a consistent study schedule "
            "with enough breaks."
    },


    # --------------------------------------------------------
    # PHYSICAL ACTIVITY
    # --------------------------------------------------------

    "Physical_Activity_Hours": {

        "label": "Physical activity",

        "direction": "higher_is_better",

        "attention": lambda x: x <= 1.3,

        "stable": lambda x: x > 2.2,

        "reference": 2.6,

        "attention_message":
            "Your physical activity is relatively low. "
            "Adding some regular movement, walking, or exercise "
            "may be a useful habit.",

        "stable_message":
            "Your physical activity is in a favorable range. "
            "Keep this habit consistent."
    },


    # --------------------------------------------------------
    # SLEEP
    # --------------------------------------------------------

    "Sleep_Hours_Per_Night": {

        "label": "Sleep",

        "direction": "higher_is_better",

        "attention": lambda x: x <= 5.6,

        "stable": lambda x: x > 7.5,

        "reference": 8.2,

        "attention_message":
            "Your sleep duration is relatively low. "
            "Gradually working toward a more regular and "
            "sufficient sleep routine may be helpful.",

        "stable_message":
            "Your sleep duration is in a favorable range. "
            "Try to keep a consistent sleep routine."
    },


    # --------------------------------------------------------
    # STRESS
    # --------------------------------------------------------

    "Stress_Level": {

        "label": "Stress level",

        "direction": "lower_is_better",

        "attention":
            lambda x: str(x).strip().lower()
            in {"high", "very high"},

        "stable":
            lambda x: str(x).strip().lower() == "low",

        "reference": "Low",

        "attention_message":
            "Your reported stress level is high. "
            "Consider adding regular breaks, relaxation time, "
            "and healthy ways of managing academic pressure.",

        "stable_message":
            "Your reported stress level is low. "
            "Keep maintaining the habits that help you "
            "manage stress."
    }
}


# ============================================================
# DAILY UNLOCK CLASSIFICATION
# ============================================================

def classify_daily_unlocks(value):
    """
    Apply the exact project-defined Daily Unlocks scale.
    """

    value = float(value)

    for category in FEATURE_RULES["Daily_Unlocks"]["categories"]:

        if category["min"] <= value <= category["max"]:

            return {
                "status": category["status"],
                "interpretation": category["interpretation"],
                "emoji": category["emoji"]
            }

    return {
        "status": "watch",
        "interpretation": "Can improve",
        "emoji": "🟡"
    }


# ============================================================
# GENERIC FEATURE STATUS
# ============================================================

def get_feature_status(feature, value):

    # Special handling for Daily Unlocks
    if feature == "Daily_Unlocks":
        return classify_daily_unlocks(value)

    rule = FEATURE_RULES[feature]

    if rule["attention"](value):

        return {
            "status": "attention",
            "interpretation": "Needs attention",
            "emoji": "🔴"
        }

    elif rule["stable"](value):

        return {
            "status": "stable",
            "interpretation": "Favorable",
            "emoji": "🟢"
        }

    else:

        return {
            "status": "watch",
            "interpretation": "Can improve",
            "emoji": "🟡"
        }


# ============================================================
# FEATURE ANALYSIS
# ============================================================

def analyze_student_features(
    student_data,
    model=None,
    preprocessor=None
):

    needs_attention = []
    stable = []
    watch = []

    base_score = None

    # --------------------------------------------------------
    # Base prediction
    # --------------------------------------------------------

    if model is not None and preprocessor is not None:

        input_df = pd.DataFrame([student_data])

        processed_data = preprocessor.transform(input_df)

        base_score = float(
            model.predict(processed_data)[0]
        )

    # --------------------------------------------------------
    # Analyze each actionable feature
    # --------------------------------------------------------

    for feature, rule in FEATURE_RULES.items():

        if feature not in student_data:
            continue

        value = student_data[feature]

        item = {
            "feature": feature,
            "label": rule["label"],
            "value": value
        }

        # ----------------------------------------------------
        # Model-based estimated improvement
        # ----------------------------------------------------

        if (
            base_score is not None
            and "reference" in rule
        ):

            counterfactual = student_data.copy()

            counterfactual[feature] = rule["reference"]

            cf_df = pd.DataFrame([counterfactual])

            cf_processed = preprocessor.transform(cf_df)

            cf_score = float(
                model.predict(cf_processed)[0]
            )

            item["estimated_score_change"] = round(
                cf_score - base_score,
                2
            )

        # ----------------------------------------------------
        # Classification
        # ----------------------------------------------------

        status = get_feature_status(
            feature,
            value
        )

        item["status"] = status["status"]

        item["interpretation"] = status[
            "interpretation"
        ]

        item["emoji"] = status["emoji"]

        # ----------------------------------------------------
        # Messages
        # ----------------------------------------------------

        if feature == "Daily_Unlocks":

            if status["status"] == "watch":

                item["message"] = rule[
                    "watch_message"
                ]

            elif status["status"] == "stable":

                item["message"] = rule[
                    "stable_message"
                ]

            else:

                item["message"] = rule[
                    "attention_message"
                ]

        else:

            if status["status"] == "attention":

                item["message"] = rule[
                    "attention_message"
                ]

            elif status["status"] == "stable":

                item["message"] = rule[
                    "stable_message"
                ]

            else:

                item["message"] = (
                    f"{rule['label']} can be improved. "
                    "Keep an eye on this area and maintain "
                    "a healthy routine."
                )

        # ----------------------------------------------------
        # Put item into correct group
        # ----------------------------------------------------

        if status["status"] == "attention":

            needs_attention.append(item)

        elif status["status"] == "stable":

            stable.append(item)

        else:

            watch.append(item)

    # --------------------------------------------------------
    # Rank attention areas by estimated improvement
    # --------------------------------------------------------

    if base_score is not None:

        needs_attention.sort(
            key=lambda x: x.get(
                "estimated_score_change",
                0
            ),
            reverse=True
        )

        watch.sort(
            key=lambda x: x.get(
                "estimated_score_change",
                0
            ),
            reverse=True
        )

    return {
        "needs_attention": needs_attention,
        "stable": stable,
        "watch": watch
    }


# ============================================================
# CREATE GEMINI CONTEXT
# ============================================================

def create_ai_feature_context(
    student_data,
    score,
    analysis
):

    category = get_score_category(score)

    context = {

        "score": round(
            float(score),
            2
        ),

        "category": category,

        "needs_attention": [],

        "watch": [],

        "stable": []
    }

    # --------------------------------------------------------
    # Areas needing attention
    # --------------------------------------------------------

    for item in analysis["needs_attention"]:

        context["needs_attention"].append({

            "area": item["label"],

            "current_value":
                item["value"],

            "interpretation":
                item["interpretation"],

            "message":
                item["message"],

            "estimated_score_change":
                item.get(
                    "estimated_score_change"
                )
        })

    # --------------------------------------------------------
    # Watch / can improve
    # --------------------------------------------------------

    for item in analysis["watch"]:

        context["watch"].append({

            "area": item["label"],

            "current_value":
                item["value"],

            "interpretation":
                item["interpretation"],

            "message":
                item["message"],

            "estimated_score_change":
                item.get(
                    "estimated_score_change"
                )
        })

    # --------------------------------------------------------
    # Stable areas
    # --------------------------------------------------------

    for item in analysis["stable"]:

        context["stable"].append({

            "area": item["label"],

            "current_value":
                item["value"],

            "interpretation":
                item["interpretation"],

            "message":
                item["message"]
        })

    return context


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    # Project-root-safe paths
    PROJECT_ROOT = Path(
        __file__
    ).resolve().parent.parent

    preprocessor = joblib.load(
        PROJECT_ROOT
        / "Models"
        / "preprocessor.pkl"
    )

    model = joblib.load(
        PROJECT_ROOT
        / "Models"
        / "final_random_forest.pkl"
    )

    # --------------------------------------------------------
    # Sample student
    # --------------------------------------------------------

    sample_student = {

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

    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    input_df = pd.DataFrame([
        sample_student
    ])

    processed_data = preprocessor.transform(
        input_df
    )

    score = float(
        model.predict(processed_data)[0]
    )

    # --------------------------------------------------------
    # Analysis
    # --------------------------------------------------------

    analysis = analyze_student_features(
        sample_student,
        model=model,
        preprocessor=preprocessor
    )

    ai_context = create_ai_feature_context(
        sample_student,
        score,
        analysis
    )

    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("STUDENT MENTAL HEALTH FEATURE ANALYSIS")
    print("=" * 60)

    print(
        "\nScore:",
        ai_context["score"]
    )

    print(
        "Category:",
        ai_context["category"]
    )

    print("\n🔴 AREAS NEEDING ATTENTION:")

    for item in ai_context[
        "needs_attention"
    ]:

        print(
            f"- {item['area']}: "
            f"{item['current_value']} "
            f"→ {item['interpretation']}"
        )

    print("\n🟡 AREAS THAT CAN IMPROVE:")

    for item in ai_context[
        "watch"
    ]:

        print(
            f"- {item['area']}: "
            f"{item['current_value']} "
            f"→ {item['interpretation']}"
        )

    print("\n🟢 FAVORABLE AREAS:")

    for item in ai_context[
        "stable"
    ]:

        print(
            f"- {item['area']}: "
            f"{item['current_value']} "
            f"→ {item['interpretation']}"
        )