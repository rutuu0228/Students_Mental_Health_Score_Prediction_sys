from fastapi import APIRouter

from Backend.api.schemas import ChatInput
from Backend.gemini_chatbot import chat_with_gemini


router = APIRouter(
    prefix="/chat",
    tags=["Chatbot"]
)


@router.post("")
def chat(chat_input: ChatInput):

    response = chat_with_gemini(
        chat_input.message
    )

    return {
        "response": response
    }