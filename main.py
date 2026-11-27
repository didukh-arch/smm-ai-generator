from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from dependencies import get_scenario_service, get_auth_service
from services.interfaces import IScenarioService, IAuthService
from services.scenario_service import (
    BusinessValidationError,
    DuplicateScenarioError,
    PlanRestrictionError,
    DailyLimitExceededError,
    ScenarioNotFoundError,
)
from services.auth_service import (
    AuthError,
    UserAlreadyExistsError,
    InvalidCredentialsError,
    PaymentValidationError,
)

app = FastAPI(title="SMM AI Generator API", version="2.6.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class UserRegister(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserUpdate(BaseModel):
    first_name: str
    last_name: str
    email: str


class PasswordChange(BaseModel):
    old_password: str
    new_password: str


class PaymentRequest(BaseModel):
    plan: str
    amount_paid: float
    card_number: str = ""
    card_expiry: str = ""
    card_cvv: str = ""


class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    plan: str
    days_left: int = 0
    plan_end_date: Optional[str] = None

    class Config:
        from_attributes = True


class QuotaResponse(BaseModel):
    plan: str
    limit: int
    used: int
    remaining: int


class ScenarioCreate(BaseModel):
    topic: str
    tone: str = "Експертний"
    content_type: str = "scenario"
    option_label: str = "20 с"
    user_id: Optional[int] = None


class ScenarioUpdateMeta(BaseModel):
    notes: Optional[str] = None
    is_favorite: Optional[bool] = None


class ScenarioResponse(BaseModel):
    id: int
    topic: str
    content_type: str
    option_label: str
    tone: str
    content: str
    notes: str
    is_favorite: bool
    created_at: datetime
    user_id: Optional[int] = None

    class Config:
        from_attributes = True


@app.post("/api/v1/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    data: UserRegister,
    auth_service: IAuthService = Depends(get_auth_service),
):
    try:
        user = auth_service.register_user(
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            password=data.password,
        )
        return auth_service.get_user_subscription_status(user.id)
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except AuthError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.post("/api/v1/auth/login", response_model=UserResponse)
def login(
    data: UserLogin,
    auth_service: IAuthService = Depends(get_auth_service),
):
    try:
        user = auth_service.authenticate_user(email=data.email, password=data.password)
        return auth_service.get_user_subscription_status(user.id)
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@app.get("/api/v1/users/{user_id}/subscription", response_model=UserResponse)
def get_subscription(
    user_id: int,
    auth_service: IAuthService = Depends(get_auth_service),
):
    try:
        return auth_service.get_user_subscription_status(user_id=user_id)
    except AuthError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.put("/api/v1/users/{user_id}", response_model=UserResponse)
def update_profile(
    user_id: int,
    data: UserUpdate,
    auth_service: IAuthService = Depends(get_auth_service),
):
    try:
        user = auth_service.update_user_profile(
            user_id=user_id,
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
        )
        return auth_service.get_user_subscription_status(user.id)
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except AuthError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.put("/api/v1/users/{user_id}/password")
def change_user_password(
    user_id: int,
    data: PasswordChange,
    auth_service: IAuthService = Depends(get_auth_service),
):
    try:
        auth_service.change_password(
            user_id=user_id,
            old_password=data.old_password,
            new_password=data.new_password,
        )
        return {"status": "ok", "message": "Пароль успішно змінено!"}
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except AuthError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.post("/api/v1/users/{user_id}/pay", response_model=UserResponse)
def pay_and_activate_plan(
    user_id: int,
    data: PaymentRequest,
    auth_service: IAuthService = Depends(get_auth_service),
):
    try:
        return auth_service.process_payment_and_activate(
            user_id=user_id,
            plan=data.plan,
            amount_paid=data.amount_paid,
            card_number=data.card_number,
            card_expiry=data.card_expiry,
            card_cvv=data.card_cvv,
        )
    except PaymentValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except AuthError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.get("/api/v1/users/{user_id}/quota", response_model=QuotaResponse)
def get_user_quota(
    user_id: int,
    scenario_service: IScenarioService = Depends(get_scenario_service),
):
    return scenario_service.get_daily_quota(user_id=user_id)


@app.post(
    "/api/v1/scenarios/generate",
    response_model=ScenarioResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_scenario(
    data: ScenarioCreate,
    scenario_service: IScenarioService = Depends(get_scenario_service),
):
    try:
        return scenario_service.create_scenario(
            topic=data.topic,
            tone=data.tone,
            content_type=data.content_type,
            option_label=data.option_label,
            user_id=data.user_id,
        )
    except DailyLimitExceededError as e:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e))
    except PlanRestrictionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except DuplicateScenarioError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except BusinessValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Помилка сервера: {str(e)}",
        )


@app.get("/api/v1/scenarios/history", response_model=List[ScenarioResponse])
def get_history(
    user_id: Optional[int] = None,
    scenario_service: IScenarioService = Depends(get_scenario_service),
):
    return scenario_service.get_all_scenarios(user_id=user_id)


@app.patch("/api/v1/scenarios/{scenario_id}", response_model=ScenarioResponse)
def update_scenario_meta(
    scenario_id: int,
    data: ScenarioUpdateMeta,
    scenario_service: IScenarioService = Depends(get_scenario_service),
):
    try:
        return scenario_service.update_scenario_meta(
            scenario_id=scenario_id,
            notes=data.notes,
            is_favorite=data.is_favorite,
        )
    except ScenarioNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.delete("/api/v1/scenarios/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scenario(
    scenario_id: int,
    scenario_service: IScenarioService = Depends(get_scenario_service),
):
    try:
        scenario_service.delete_scenario(scenario_id=scenario_id)
    except ScenarioNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))