import hashlib
import hmac
import os
import re
from datetime import datetime, timedelta, date
from typing import Dict, Any
from sqlalchemy import func
from sqlalchemy.orm import Session

from models import UserDB
from services.interfaces import IAuthService


class AuthError(Exception):
    pass


class UserAlreadyExistsError(AuthError):
    pass


class InvalidCredentialsError(AuthError):
    pass


class PaymentValidationError(AuthError):
    pass


class AuthService(IAuthService):
    EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
    MIN_PASSWORD_LENGTH = 6

    PLAN_PRICES_UAH = {
        "free": 0.00,
        "pro": 99.00,
        "business": 199.00,
    }
    SUBSCRIPTION_DAYS = 30

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _get_kyiv_today() -> date:
        return (datetime.utcnow() + timedelta(hours=2)).date()

    @staticmethod
    def _hash_password(password: str) -> str:
        salt = os.urandom(16).hex()
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000)
        return f"{salt}${dk.hex()}"

    @staticmethod
    def _verify_password(plain_password: str, stored_hash: str) -> bool:
        try:
            salt, hash_hex = stored_hash.split("$", 1)
            dk = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt.encode("utf-8"), 100_000)
            return hmac.compare_digest(dk.hex(), hash_hex)
        except ValueError:
            return False

    def _sync_subscription(self, user: UserDB) -> int:
        today = self._get_kyiv_today()

        if user.plan in {"pro", "business"}:
            if user.plan_end_date is None or user.plan_end_date <= today:
                user.plan = "free"
                user.plan_end_date = None
                self.db.commit()
                self.db.refresh(user)
                return 0
            return (user.plan_end_date - today).days

        return 0

    def _serialize_user_with_sub(self, user: UserDB) -> Dict[str, Any]:
        days_left = self._sync_subscription(user)
        return {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "plan": user.plan,
            "days_left": days_left,
            "plan_end_date": user.plan_end_date.isoformat() if user.plan_end_date else None,
        }

    def register_user(self, first_name: str, last_name: str, email: str, password: str) -> UserDB:
        clean_first = first_name.strip()
        clean_last = last_name.strip()
        clean_email = email.strip().lower()

        if len(clean_first) < 2 or len(clean_last) < 2:
            raise AuthError("Ім'я та прізвище мають містити щонайменше 2 символи.")

        if not self.EMAIL_REGEX.match(clean_email):
            raise AuthError("Введіть коректну електронну пошту.")

        if len(password) < self.MIN_PASSWORD_LENGTH:
            raise AuthError(f"Пароль має містити щонайменше {self.MIN_PASSWORD_LENGTH} символів.")

        existing_user = (
            self.db.query(UserDB)
            .filter(func.lower(UserDB.email) == clean_email)
            .first()
        )
        if existing_user:
            raise UserAlreadyExistsError("Користувач із такою поштою вже зареєстрований.")

        new_user = UserDB(
            first_name=clean_first,
            last_name=clean_last,
            email=clean_email,
            hashed_password=self._hash_password(password),
            plan="free",
            plan_end_date=None,
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def authenticate_user(self, email: str, password: str) -> UserDB:
        clean_email = email.strip().lower()
        user = (
            self.db.query(UserDB)
            .filter(func.lower(UserDB.email) == clean_email)
            .first()
        )
        if not user or not self._verify_password(password, user.hashed_password):
            raise InvalidCredentialsError("Невірна пошта або пароль.")

        self._sync_subscription(user)
        return user

    def update_user_profile(self, user_id: int, first_name: str, last_name: str, email: str) -> UserDB:
        user = self.db.query(UserDB).filter(UserDB.id == user_id).first()
        if not user:
            raise AuthError("Користувача не знайдено.")

        clean_first = first_name.strip()
        clean_last = last_name.strip()
        clean_email = email.strip().lower()

        if len(clean_first) < 2 or len(clean_last) < 2:
            raise AuthError("Ім'я та прізвище мають містити щонайменше 2 символи.")

        if not self.EMAIL_REGEX.match(clean_email):
            raise AuthError("Введіть коректну електронну пошту.")

        duplicate = (
            self.db.query(UserDB)
            .filter(func.lower(UserDB.email) == clean_email, UserDB.id != user_id)
            .first()
        )
        if duplicate:
            raise UserAlreadyExistsError("Ця пошта вже використовується іншим акаунтом.")

        user.first_name = clean_first
        user.last_name = clean_last
        user.email = clean_email
        self.db.commit()
        self.db.refresh(user)
        return user

    def change_password(self, user_id: int, old_password: str, new_password: str) -> None:
        user = self.db.query(UserDB).filter(UserDB.id == user_id).first()
        if not user:
            raise AuthError("Користувача не знайдено.")

        if not self._verify_password(old_password, user.hashed_password):
            raise InvalidCredentialsError("Поточний пароль введено невірно.")

        if len(new_password) < self.MIN_PASSWORD_LENGTH:
            raise AuthError(f"Новий пароль має містити щонайменше {self.MIN_PASSWORD_LENGTH} символів.")

        if old_password == new_password:
            raise AuthError("Новий пароль має відрізнятися від поточного.")

        user.hashed_password = self._hash_password(new_password)
        self.db.commit()

    def get_user_subscription_status(self, user_id: int) -> Dict[str, Any]:
        user = self.db.query(UserDB).filter(UserDB.id == user_id).first()
        if not user:
            raise AuthError("Користувача не знайдено.")
        return self._serialize_user_with_sub(user)

    def process_payment_and_activate(
        self,
        user_id: int,
        plan: str,
        amount_paid: float,
        card_number: str,
        card_expiry: str,
        card_cvv: str,
    ) -> Dict[str, Any]:
        if plan not in {"free", "pro", "business"}:
            raise PaymentValidationError("Обрано невідомий тарифний план.")

        user = self.db.query(UserDB).filter(UserDB.id == user_id).first()
        if not user:
            raise AuthError("Користувача не знайдено.")

        if plan == "free":
            user.plan = "free"
            user.plan_end_date = None
            self.db.commit()
            self.db.refresh(user)
            return self._serialize_user_with_sub(user)

        digits_only = "".join(ch for ch in card_number if ch.isdigit())
        if len(digits_only) != 16:
            raise PaymentValidationError("Номер картки має містити рівно 16 цифр.")

        if not re.match(r"^(0[1-9]|1[0-2])\/\d{2}$", card_expiry.strip()):
            raise PaymentValidationError("Термін дії картки вкажіть у форматі ММ/РР (наприклад, 08/28).")

        if not (card_cvv.strip().isdigit() and len(card_cvv.strip()) == 3):
            raise PaymentValidationError("CVV-код має містити 3 цифри.")

        expected_uah = self.PLAN_PRICES_UAH[plan]
        expected_kopecks = round(expected_uah * 100)
        paid_kopecks = round(amount_paid * 100)

        if paid_kopecks < expected_kopecks:
            diff_uah = (expected_kopecks - paid_kopecks) / 100
            raise PaymentValidationError(
                f"Недостатня сума оплати! Вартість тарифу: {expected_uah:.2f} грн, "
                f"введено: {amount_paid:.2f} грн (не вистачає {diff_uah:.2f} грн)."
            )

        today = self._get_kyiv_today()
        user.plan = plan
        user.plan_end_date = today + timedelta(days=self.SUBSCRIPTION_DAYS)
        self.db.commit()
        self.db.refresh(user)

        return self._serialize_user_with_sub(user)