from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from models import ScenarioDB, UserDB


class IAIService(ABC):
    @abstractmethod
    def generate_content(
        self,
        topic: str,
        tone: str,
        content_type: str,
        option_label: str,
    ) -> str:
        pass


class IAuthService(ABC):
    @abstractmethod
    def register_user(self, first_name: str, last_name: str, email: str, password: str) -> UserDB:
        pass

    @abstractmethod
    def authenticate_user(self, email: str, password: str) -> UserDB:
        pass

    @abstractmethod
    def update_user_profile(self, user_id: int, first_name: str, last_name: str, email: str) -> UserDB:
        pass

    @abstractmethod
    def change_password(self, user_id: int, old_password: str, new_password: str) -> None:
        pass

    @abstractmethod
    def process_payment_and_activate(
        self,
        user_id: int,
        plan: str,
        amount_paid: float,
        card_number: str,
        card_expiry: str,
        card_cvv: str,
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_user_subscription_status(self, user_id: int) -> Dict[str, Any]:
        pass


class IScenarioService(ABC):
    @abstractmethod
    def get_daily_quota(self, user_id: int) -> Dict[str, Any]:
        pass

    @abstractmethod
    def create_scenario(
        self,
        topic: str,
        tone: str,
        content_type: str = "scenario",
        option_label: str = "20 с",
        user_id: Optional[int] = None,
    ) -> ScenarioDB:
        pass

    @abstractmethod
    def get_all_scenarios(self, user_id: Optional[int] = None) -> List[ScenarioDB]:
        pass

    @abstractmethod
    def update_scenario_meta(
        self,
        scenario_id: int,
        notes: Optional[str] = None,
        is_favorite: Optional[bool] = None,
    ) -> ScenarioDB:
        pass

    @abstractmethod
    def delete_scenario(self, scenario_id: int) -> None:
        pass