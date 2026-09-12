import os

from dotenv import load_dotenv
from google import genai


# ============================================================
# GEMINI SETUP
# ============================================================

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

previous_interaction_id = None


# ============================================================
# SYSTEM INSTRUCTION
# ============================================================

SYSTEM_INSTRUCTION = """

You are a warm, humble and supportive AI assistant inside a
Student Mental Health Score Prediction System.

Your job is to explain the student's result in simple,
friendly and non-technical language.

============================================================
SCORE INTERPRETATION
============================================================

The application provides a project-defined score category.

Use the supplied category EXACTLY as provided.

Do NOT calculate, modify or reinterpret the category.

Project score categories:

1.0 - 3.9  = Low
4.0 - 6.9  = Moderate
7.0 - 8.9  = Good
9.0 - 10.0 = Excellent / Stable

Say:

"Your score falls in the Moderate range."

Do NOT say:

"Your mental health is Moderate."

This score is meant for self-reflection and is not a
medical diagnosis.

============================================================
FEATURE ANALYSIS
============================================================

The application provides three groups:

🔴 AREAS NEEDING ATTENTION

These are the most important areas to focus on.

🟡 AREAS THAT CAN IMPROVE

These are not necessarily serious concerns, but they can
still be improved.

🟢 FAVORABLE AREAS

These are currently favorable according to the project's
analysis and should be maintained.

IMPORTANT:

Keep the exact order in which the application provides
each group.

Do NOT reorder the areas.

============================================================
DAILY PHONE UNLOCKS
============================================================

Use these EXACT project-defined interpretations:

≤ 30
🟢 Favorable

31–50
🟢 Good / maintain

51–100
🟡 Can improve

101–200
🟠 Needs attention

> 200
🔴 High attention

Do not change these ranges.

Do not invent different ranges.

Example:

95 daily phone unlocks means:

🟡 Can improve

It does NOT mean Favorable.

============================================================
RESPONSE RULES
============================================================

Use the student's name naturally.

Use the student's actual values.

Do not invent values.

Do not invent qualitative labels for numerical values.

For example:

Correct:
"Daily phone unlocks (95): You can work on reducing
unnecessary phone checking."

Incorrect:
"Daily phone unlocks (95): Your phone usage is low."

Give one short practical suggestion for each area.

Keep the response concise.

Avoid unnecessary generic advice when specific feature
analysis is already available.

============================================================
STUDENT-FACING LANGUAGE
============================================================

DO NOT mention:

- Random Forest
- Machine Learning model
- ML model
- Dataset
- Backend
- Feature importance
- Permutation importance
- Counterfactual analysis
- Estimated score change
- Technical implementation

These are internal application details.

The student should only receive useful personal guidance.

============================================================
IMPORTANT MEDICAL BOUNDARIES
============================================================

Never diagnose a mental health disorder.

Never prescribe medication.

Never claim the score is medically accurate.

Never claim that a specific feature causes a mental
health condition.

Use supportive and non-judgmental language.

============================================================
RECOMMENDED RESPONSE FORMAT
============================================================

Dear [Name] ❤️

Your Mental Health Score is [score], which falls in the
[category] range.

🔴 Areas to focus on:
- [Area + value + short suggestion]
- [Area + value + short suggestion]

🟡 Can improve:
- [Area + value + short suggestion]

🟢 Keep doing:
- [Area + value + encouragement]

End with ONE short, warm and encouraging sentence.

Do not over-praise.

Do not use excessive emotional language.

============================================================
SAFETY
============================================================

If the student mentions self-harm, suicide, harming
themselves, or immediate danger, respond seriously and
compassionately.

Encourage them to contact a trusted person and qualified
emergency or mental-health support immediately.

"""


# ============================================================
# CHAT FUNCTION
# ============================================================

def chat_with_gemini(
    user_message,
    prediction_context=None,
    student_name="Student"
):

    global previous_interaction_id


    # --------------------------------------------------------
    # Prediction context
    # --------------------------------------------------------

    if prediction_context:

        score = prediction_context.get(
            "score",
            "Not available"
        )

        category = prediction_context.get(
            "category",
            "Not available"
        )

        needs_attention = prediction_context.get(
            "needs_attention",
            []
        )

        watch = prediction_context.get(
            "watch",
            []
        )

        stable = prediction_context.get(
            "stable",
            []
        )


        context_text = f"""

STUDENT NAME:
{student_name}

PREDICTED SCORE:
{score}

SCORE CATEGORY:
{category}


🔴 AREAS NEEDING ATTENTION:

"""


        if needs_attention:

            for item in needs_attention:

                context_text += (
                    f"- {item.get('area')}: "
                    f"{item.get('current_value')} "
                    f"({item.get('interpretation')})\n"
                )

        else:

            context_text += "- None\n"


        context_text += """

🟡 AREAS THAT CAN IMPROVE:

"""


        if watch:

            for item in watch:

                context_text += (
                    f"- {item.get('area')}: "
                    f"{item.get('current_value')} "
                    f"({item.get('interpretation')})\n"
                )

        else:

            context_text += "- None\n"


        context_text += """

🟢 FAVORABLE AREAS:

"""


        if stable:

            for item in stable:

                context_text += (
                    f"- {item.get('area')}: "
                    f"{item.get('current_value')} "
                    f"({item.get('interpretation')})\n"
                )

        else:

            context_text += "- None\n"


        context_text += f"""

STUDENT QUESTION:

{user_message}

"""


        user_input = context_text


    else:

        user_input = f"""

STUDENT NAME:

{student_name}


STUDENT QUESTION:

{user_message}

"""


    # --------------------------------------------------------
    # Gemini interaction
    # --------------------------------------------------------

    if previous_interaction_id is None:

        response = client.interactions.create(

            model="gemini-3.6-flash",

            input=(
                SYSTEM_INSTRUCTION
                + "\n\n"
                + user_input
            )
        )

    else:

        response = client.interactions.create(

            model="gemini-3.6-flash",

            input=user_input,

            previous_interaction_id=
                previous_interaction_id
        )


    # Save conversation
    previous_interaction_id = response.id


    return response.output_text


# ============================================================
# STANDALONE CHATBOT TEST
# ============================================================

if __name__ == "__main__":

    print(
        "Student Mental Health AI Assistant"
    )

    print(
        "Type 'exit' to stop.\n"
    )


    while True:

        user_message = input(
            "You: "
        )


        if user_message.lower() == "exit":

            break


        reply = chat_with_gemini(
            user_message
        )


        print("\nAI:")
        print(reply)
        print()