from fastapi import FastAPI

from Backend.api.routes.prediction import router as prediction_router
from Backend.api.routes.chatbot import router as chatbot_router


app = FastAPI(
    title="Mental Health Prediction System"
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(prediction_router)
app.include_router(chatbot_router)