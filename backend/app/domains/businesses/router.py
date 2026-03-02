import uuid
from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.api.deps import get_db
from app.domains.businesses.schemas import ProfileCompletionScoreRead
from app.domains.businesses.services import ProfileCompletionCalculator

router = APIRouter()

@router.get("/{id}/completion-score", response_model=ProfileCompletionScoreRead)
def get_completion_score(id: uuid.UUID, session: Session = Depends(get_db)):
    calculator = ProfileCompletionCalculator(session)
    score = calculator.calculate(id)
    return score
