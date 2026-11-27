from fastapi import Depends
from sqlalchemy.orm import Session

from database import get_db
from services.interfaces import IAIService, IScenarioService, IAuthService
from services.groq_ai_service import GroqAIService
from services.scenario_service import ScenarioService
from services.auth_service import AuthService


def get_ai_service() -> IAIService:
    return GroqAIService()


def get_auth_service(db: Session = Depends(get_db)) -> IAuthService:
    return AuthService(db=db)


def get_scenario_service(
    db: Session = Depends(get_db),
    ai_service: IAIService = Depends(get_ai_service),
) -> IScenarioService:
    return ScenarioService(db=db, ai_service=ai_service)