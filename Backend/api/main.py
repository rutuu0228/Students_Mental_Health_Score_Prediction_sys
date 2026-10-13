from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.prediction import router as prediction_router
from api.routes.chatbot import router as chatbot_router


app = FastAPI(
    title="Mental Health Prediction System"
)


# Allow the Lovable frontend and local development to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(prediction_router)
app.include_router(chatbot_router)