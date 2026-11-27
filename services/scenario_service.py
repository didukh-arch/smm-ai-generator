from datetime import datetime, timedelta, date
from typing import List, Optional, Dict, Any
from sqlalchemy import func
from sqlalchemy.orm import Session

from models import ScenarioDB, UserDB
from services.interfaces import IScenarioService, IAIService


class BusinessValidationError(Exception):
    pass


class DuplicateScenarioError(BusinessValidationError):
    pass


class PlanRestrictionError(BusinessValidationError):
    pass


class DailyLimitExceededError(BusinessValidationError):
    pass


class ScenarioNotFoundError(BusinessValidationError):
    pass


class ScenarioService(IScenarioService):
    ALLOWED_TONES = {"Експертний", "Розважальний", "Мотиваційний", "Провокаційний", "Поради"}
    FORBIDDEN_WORDS = {"спам", "казино", "шахрайство"}
    MIN_TOPIC_LENGTH = 4
    MAX_TOPIC_LENGTH = 150

    PLAN_DAILY_LIMITS = {
        "free": 2,
        "pro": 4,
        "business": 6,
    }

    PRO_OPTIONS = {"30 с", "14 порад"}
    BUSINESS_OPTIONS = {"40 с", "18 порад + дії"}

    def __init__(self, db: Session, ai_service: IAIService):
        self.db = db
        self.ai_service = ai_service

    @staticmethod
    def _get_kyiv_today() -> date:
        # Поточна дата за київським часом (після 00:00 автоматично починається новий день)
        return (datetime.utcnow() + timedelta(hours=2)).date()

    def _sync_user_daily_counter(self, user: UserDB) -> None:
        today = self._get_kyiv_today()
        if user.last_usage_date != today:
            user.daily_used = 0
            user.last_usage_date = today
            self.db.commit()
            self.db.refresh(user)

    def get_daily_quota(self, user_id: int) -> Dict[str, Any]:
        user = self.db.query(UserDB).filter(UserDB.id == user_id).first()
        if not user:
            return {"plan": "free", "limit": 2, "used": 0, "remaining": 2}

        self._sync_user_daily_counter(user)
        limit = self.PLAN_DAILY_LIMITS.get(user.plan, 2)
        remaining = max(0, limit - user.daily_used)
        return {
            "plan": user.plan,
            "limit": limit,
            "used": user.daily_used,
            "remaining": remaining,
        }

    def _check_plan_and_quota(self, option_label: str, user_id: Optional[int]) -> Optional[UserDB]:
        if user_id is None:
            return None

        user = self.db.query(UserDB).filter(UserDB.id == user_id).first()
        if not user:
            return None

        today = self._get_kyiv_today()
        # Якщо платний абонемент закінчився — автоматично повертаємо на «Старт»
        if user.plan in {"pro", "business"} and (user.plan_end_date is None or user.plan_end_date <= today):
            user.plan = "free"
            user.plan_end_date = None
            self.db.commit()
            self.db.refresh(user)

        # Оновлюємо денний лічильник, якщо настав новий день після 00:00
        self._sync_user_daily_counter(user)

        # Перевіряємо доступ до платних опцій
        if option_label in self.PRO_OPTIONS and user.plan not in {"pro", "business"}:
            raise PlanRestrictionError(
                f"Опція «{option_label}» доступна лише у тарифах «Креатор PRO» або «Бізнес / Агенція»."
            )

        if option_label in self.BUSINESS_OPTIONS and user.plan != "business":
            raise PlanRestrictionError(
                f"Опція «{option_label}» доступна лише у тарифі «Бізнес / Агенція»."
            )

        # Перевіряємо денний ліміт генерацій
        daily_limit = self.PLAN_DAILY_LIMITS.get(user.plan, 2)
        if user.daily_used >= daily_limit:
            raise DailyLimitExceededError(
                f"Ви вичерпали денний ліміт генерацій ({daily_limit} з {daily_limit}) для вашого тарифу. "
                "Ліміт оновиться після 00:00 або ви можете підвищити тариф."
            )

        return user

    def _validate_business_rules(
        self,
        topic: str,
        tone: str,
        content_type: str,
        option_label: str,
        user_id: Optional[int],
    ) -> tuple[str, Optional[UserDB]]:
        user = self._check_plan_and_quota(option_label, user_id)

        clean_topic = " ".join(topic.strip().split())
        if len(clean_topic) < self.MIN_TOPIC_LENGTH:
            raise BusinessValidationError(
                f"Назва занадто коротка (мінімум {self.MIN_TOPIC_LENGTH} символи)."
            )

        if len(clean_topic) > self.MAX_TOPIC_LENGTH:
            raise BusinessValidationError(
                f"Назва перевищує ліміт у {self.MAX_TOPIC_LENGTH} символів."
            )

        if content_type == "scenario" and tone not in self.ALLOWED_TONES:
            raise BusinessValidationError(f"Недопустимий тон подачі «{tone}».")

        lower_topic = clean_topic.lower()
        for word in self.FORBIDDEN_WORDS:
            if word in lower_topic:
                raise BusinessValidationError(f"Назва містить заборонене слово: «{word}».")

        query = self.db.query(ScenarioDB).filter(
            func.lower(ScenarioDB.topic) == lower_topic,
            ScenarioDB.content_type == content_type,
            ScenarioDB.option_label == option_label,
            ScenarioDB.tone == tone,
        )
        if user_id is not None:
            query = query.filter(ScenarioDB.user_id == user_id)

        existing = query.first()
        if existing:
            raise DuplicateScenarioError(
                f"У вас вже є така генерація «{clean_topic}» ({option_label}) під ID #{existing.id}."
            )

        return clean_topic, user

    def create_scenario(
        self,
        topic: str,
        tone: str,
        content_type: str = "scenario",
        option_label: str = "20 с",
        user_id: Optional[int] = None,
    ) -> ScenarioDB:
        validated_topic, user = self._validate_business_rules(
            topic, tone, content_type, option_label, user_id
        )
        generated_content = self.ai_service.generate_content(
            topic=validated_topic,
            tone=tone,
            content_type=content_type,
            option_label=option_label,
        )

        db_scenario = ScenarioDB(
            topic=validated_topic,
            content_type=content_type,
            option_label=option_label,
            tone=tone if content_type == "scenario" else "Поради",
            content=generated_content,
            notes="",
            is_favorite=False,
            user_id=user_id,
        )
        self.db.add(db_scenario)

        # Збільшуємо лічильник використаних сьогодні генерацій
        if user is not None:
            user.daily_used += 1
            user.last_usage_date = self._get_kyiv_today()

        self.db.commit()
        self.db.refresh(db_scenario)
        return db_scenario

    def get_all_scenarios(self, user_id: Optional[int] = None) -> List[ScenarioDB]:
        query = self.db.query(ScenarioDB)
        if user_id is not None:
            query = query.filter(ScenarioDB.user_id == user_id)
        return query.order_by(ScenarioDB.created_at.desc()).all()

    def update_scenario_meta(
        self,
        scenario_id: int,
        notes: Optional[str] = None,
        is_favorite: Optional[bool] = None,
    ) -> ScenarioDB:
        scenario = self.db.query(ScenarioDB).filter(ScenarioDB.id == scenario_id).first()
        if not scenario:
            raise ScenarioNotFoundError("Запис не знайдено.")

        if notes is not None:
            scenario.notes = notes.strip()
        if is_favorite is not None:
            scenario.is_favorite = is_favorite

        self.db.commit()
        self.db.refresh(scenario)
        return scenario

    def delete_scenario(self, scenario_id: int) -> None:
        scenario = self.db.query(ScenarioDB).filter(ScenarioDB.id == scenario_id).first()
        if not scenario:
            raise ScenarioNotFoundError("Запис не знайдено.")

        self.db.delete(scenario)
        self.db.commit()