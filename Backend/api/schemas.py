from pydantic import BaseModel


class StudentInput(BaseModel):
    Age: int
    Gender: str
    Academic_Level: str
    Most_Used_Platform: str
    Purpose_Of_Use: str
    Avg_Daily_Usage_Hours: float
    Daily_Unlocks: int
    Study_Hours: float
    Physical_Activity_Hours: float
    Sleep_Hours_Per_Night: float
    Stress_Level: str
    Country_Processed: str

class ChatInput(BaseModel):
    message: str