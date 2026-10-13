from fastapi import APIRouter

from api.schemas import StudentInput
from predictor import create_prediction_context


router = APIRouter(
    prefix="/predict",
    tags=["Prediction"]
)


@router.post("")
def predict(student: StudentInput):

    student_data = student.model_dump()

    prediction_context = create_prediction_context(
        student_data
    )

    return prediction_context