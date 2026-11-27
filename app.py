import time
from datetime import datetime, timedelta
import streamlit as st
import requests

try:
    from src.styles import inject_custom_animations
except Exception:
    def inject_custom_animations():
        pass

API_URL = "http://127.0.0.1:8000/api/v1"

st.set_page_config(page_title="SMM AI Generator", page_icon="✨", layout="wide")
inject_custom_animations()

# --- ФІРМОВА ПАЛІТРА: DEEP CHOCOLATE (#23150C) + WARM CREAMY BRONZE (#C69B7B) + ESPRESSO (#46230a) ---
st.markdown(
    """
    <style>
    /* 1. Верхня панель Streamlit у шоколадному кольорі (#23150C) */
    header[data-testid="stHeader"] {
        background-color: #23150C !important;
        border-bottom: 1px solid #8C6343 !important;
    }
    header[data-testid="stHeader"] button,
    header[data-testid="stHeader"] span,
    header[data-testid="stHeader"] svg {
        color: #DFCBB6 !important;
        fill: #DFCBB6 !important;
    }

    .block-container {
        padding-top: 2.6rem !important;
    }

    /* 2. ГОЛОВНИЙ ФОН УСЬОГО САЙТУ — Deep Chocolate (#23150C / #301A09) */
    .stApp {
        background: linear-gradient(180deg, #23150C 0%, #301A09 60%, #23150C 100%) !important;
        color: #DFCBB6 !important;
    }

    /* 3. Текст на темному шоколадному фоні — напівматовий кремовий (#DFCBB6 / #EFE2D4) */
    .stApp h1, .stApp h2, .stApp h3, .stApp h4 {
        color: #EFE2D4 !important;
    }
    .stApp p, .stApp label, .stApp span, .stApp div, .stApp li {
        color: #DFCBB6;
    }
    .stApp .stCaption, .stApp small {
        color: #C9B29B !important;
    }

    /* 4. КАРТКИ (на сторінках профілю, тарифів, результату) */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(180deg, #D1A98A 0%, #C69B7B 100%) !important;
        border: 1.5px solid #46230a !important;
        border-radius: 16px !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.38) !important;
        padding: 12px !important;
        transition: border-color 0.25s ease, transform 0.2s ease !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #DFCBB6 !important;
    }

    /* Темний шоколадний текст усередині світлих бежевих карток */
    div[data-testid="stVerticalBlockBorderWrapper"] h1,
    div[data-testid="stVerticalBlockBorderWrapper"] h2,
    div[data-testid="stVerticalBlockBorderWrapper"] h3,
    div[data-testid="stVerticalBlockBorderWrapper"] h4,
    div[data-testid="stVerticalBlockBorderWrapper"] p,
    div[data-testid="stVerticalBlockBorderWrapper"] label,
    div[data-testid="stVerticalBlockBorderWrapper"] span,
    div[data-testid="stVerticalBlockBorderWrapper"] div,
    div[data-testid="stVerticalBlockBorderWrapper"] li {
        color: #23150C !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] .stCaption,
    div[data-testid="stVerticalBlockBorderWrapper"] small {
        color: #46230a !important;
    }

    /* Картка форми генерації (темно-шоколадна з тонкою рамкою) */
    div[data-testid="stForm"] {
        background: rgba(35, 21, 12, 0.55) !important;
        border: 1.5px solid #6E4A2E !important;
        border-radius: 18px !important;
        padding: 20px !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3) !important;
    }

    /* 5. ПЕРЕМИКАЧІ БЕЗ КРАПОК (режим створення та тривалість відео) — світяться при наведенні */
    div[data-testid="stRadio"] div[role="radiogroup"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 2px 0 !important;
        gap: 10px !important;
        flex-wrap: wrap !important;
    }

    /* Повністю ховаємо стандартні крапки radio */
    div[data-testid="stRadio"] div[role="radiogroup"] label > div:first-child {
        display: none !important;
    }

    /* Стиль кожної кнопки-опції (неактивний стан) */
    div[data-testid="stRadio"] div[role="radiogroup"] label {
        background: rgba(198, 155, 123, 0.14) !important;
        border: 1.5px solid #6E4A2E !important;
        border-radius: 12px !important;
        padding: 8px 16px !important;
        margin: 0 !important;
        cursor: pointer !important;
        transition: all 0.25s ease !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label p,
    div[data-testid="stRadio"] div[role="radiogroup"] label span {
        color: #DFCBB6 !important;
        font-weight: 600 !important;
    }

    /* Ефект світіння при наведенні курсора */
    div[data-testid="stRadio"] div[role="radiogroup"] label:hover {
        background: rgba(198, 155, 123, 0.30) !important;
        border-color: #C69B7B !important;
        box-shadow: 0 0 14px rgba(198, 155, 123, 0.55) !important;
        transform: translateY(-1px);
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label:hover p {
        color: #EFE2D4 !important;
    }

    /* Активна (обрана) опція — кремово-бронзова */
    div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(135deg, #D1A98A 0%, #C69B7B 100%) !important;
        border: 1.5px solid #EFE2D4 !important;
        box-shadow: 0 0 14px rgba(198, 155, 123, 0.5) !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) p,
    div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) span {
        color: #23150C !important;
        font-weight: 700 !important;
    }

    /* 6. КНОПКИ НАВІГАЦІЇ В ШАПЦІ (без крапок, світяться при наведенні) */
    div[data-testid="stHorizontalBlock"]:first-of-type .stButton > button[kind="secondary"] {
        background: transparent !important;
        color: #DFCBB6 !important;
        border: 1px solid transparent !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        box-shadow: none !important;
        padding: 6px 12px !important;
        transition: all 0.25s ease !important;
    }
    div[data-testid="stHorizontalBlock"]:first-of-type .stButton > button[kind="secondary"] p {
        color: #DFCBB6 !important;
        font-weight: 600 !important;
    }
    div[data-testid="stHorizontalBlock"]:first-of-type .stButton > button[kind="secondary"]:hover {
        background: rgba(198, 155, 123, 0.22) !important;
        color: #EFE2D4 !important;
        border: 1px solid #C69B7B !important;
        box-shadow: 0 0 14px rgba(198, 155, 123, 0.55) !important;
        transform: translateY(-1px);
    }
    div[data-testid="stHorizontalBlock"]:first-of-type .stButton > button[kind="secondary"]:hover p {
        color: #EFE2D4 !important;
    }

    div[data-testid="stHorizontalBlock"]:first-of-type .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #D1A98A 0%, #C69B7B 100%) !important;
        color: #23150C !important;
        border: 1.5px solid #EFE2D4 !important;
        border-radius: 12px !important;
        box-shadow: 0 0 14px rgba(198, 155, 123, 0.5) !important;
    }
    div[data-testid="stHorizontalBlock"]:first-of-type .stButton > button[kind="primary"] p {
        color: #23150C !important;
        font-weight: 700 !important;
    }

    /* 7. УСІ ІНШІ КНОПКИ НА СТОРІНЦІ */
    .stButton > button,
    .stButton > button[kind="primary"],
    .stButton > button[kind="secondary"],
    div[data-testid="stFormSubmitButton"] > button,
    div[data-testid="stFormSubmitButton"] > button[kind="primary"] {
        background: linear-gradient(135deg, #D1A98A 0%, #C69B7B 100%) !important;
        color: #23150C !important;
        border: 1.5px solid #46230a !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        box-shadow: 0 3px 10px rgba(35, 21, 12, 0.25) !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button p,
    .stButton > button[kind="primary"] p,
    div[data-testid="stFormSubmitButton"] > button p {
        color: #23150C !important;
        font-weight: 700 !important;
    }

    .stButton > button:hover:not(:disabled),
    .stButton > button[kind="primary"]:hover:not(:disabled),
    .stButton > button[kind="secondary"]:hover:not(:disabled),
    div[data-testid="stFormSubmitButton"] > button:hover:not(:disabled) {
        background: #46230a !important;
        color: #EFE2D4 !important;
        border-color: #DFCBB6 !important;
        box-shadow: 0 0 12px rgba(198, 155, 123, 0.45) !important;
        transform: translateY(-1px);
    }
    .stButton > button:hover:not(:disabled) p,
    .stButton > button[kind="primary"]:hover:not(:disabled) p,
    div[data-testid="stFormSubmitButton"] > button:hover:not(:disabled) p {
        color: #EFE2D4 !important;
    }

    .stButton > button:disabled,
    .stButton > button[kind="primary"]:disabled {
        background: #A87E5F !important;
        color: #23150C !important;
        border: 1.5px solid #46230a !important;
        opacity: 0.85 !important;
    }
    .stButton > button:disabled p {
        color: #23150C !important;
    }

    /* 8. Поля вводу та SELECTBOX (максимальний пріоритет для перекриття сірого блоку стрілки!) */
    div[data-testid="stTextInputRootElement"],
    div[data-testid="stTextInput"] div[data-baseweb="input"],
    div[data-testid="stTextInput"] div[data-baseweb="base-input"],
    div[data-testid="stNumberInput"] div[data-baseweb="input"],
    div[data-testid="stTextArea"] div[data-baseweb="textarea"] {
        background-color: #C69B7B !important;
        border: 1.5px solid #46230a !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }

    /* Підпис над selectbox залишається прозорим */
    div[data-testid="stSelectbox"] [data-testid="stWidgetLabel"],
    div[data-testid="stSelectbox"] [data-testid="stWidgetLabel"] * {
        background-color: transparent !important;
        color: #DFCBB6 !important;
    }

    /* Перебиваємо високу специфічність BaseWeb для всього контейнера selectbox разом зі стрілкою */
    div[data-testid="stSelectbox"][data-testid="stSelectbox"][data-testid="stSelectbox"][data-testid="stSelectbox"] [data-baseweb="select"],
    div[data-testid="stSelectbox"][data-testid="stSelectbox"][data-testid="stSelectbox"][data-testid="stSelectbox"] [data-baseweb="select"] > div,
    div[data-testid="stSelectbox"][data-testid="stSelectbox"][data-testid="stSelectbox"][data-testid="stSelectbox"] [data-baseweb="select"] > div > div,
    div[data-testid="stSelectbox"][data-testid="stSelectbox"][data-testid="stSelectbox"][data-testid="stSelectbox"] [data-baseweb="select"] div {
        background: #C69B7B !important;
        background-color: #C69B7B !important;
        color: #23150C !important;
        font-weight: 600 !important;
    }

    div[data-testid="stSelectbox"][data-testid="stSelectbox"][data-testid="stSelectbox"][data-testid="stSelectbox"] [data-baseweb="select"] > div {
        border: 1.5px solid #46230a !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }

    div[data-testid="stSelectbox"][data-testid="stSelectbox"][data-testid="stSelectbox"][data-testid="stSelectbox"] [data-baseweb="select"] span {
        background: transparent !important;
        color: #23150C !important;
        font-weight: 600 !important;
    }

    div[data-testid="stSelectbox"][data-testid="stSelectbox"][data-testid="stSelectbox"][data-testid="stSelectbox"] svg {
        fill: #23150C !important;
        color: #23150C !important;
        background: transparent !important;
    }

    /* Випадаючий список варіантів */
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] ul,
    ul[data-baseweb="menu"],
    li[role="option"] {
        background-color: #C69B7B !important;
        color: #23150C !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
    }
    li[role="option"]:hover,
    li[role="option"][aria-selected="true"] {
        background-color: #46230a !important;
        color: #EFE2D4 !important;
    }

    div[data-testid="stTextInputRootElement"] > div,
    div[data-baseweb="input"] > div {
        background-color: #C69B7B !important;
        border: none !important;
    }

    input, textarea {
        background-color: #C69B7B !important;
        color: #23150C !important;
        font-weight: 600 !important;
        -webkit-text-fill-color: #23150C !important;
    }

    input::placeholder, textarea::placeholder {
        color: #46230a !important;
        opacity: 0.78 !important;
        -webkit-text-fill-color: #46230a !important;
    }

    /* Кнопка-око для перегляду пароля */
    div[data-testid="stTextInput"] button,
    div[data-testid="stTextInputRootElement"] button {
        background-color: #C69B7B !important;
        border: none !important;
        box-shadow: none !important;
        color: #23150C !important;
    }
    div[data-testid="stTextInput"] button:hover,
    div[data-testid="stTextInputRootElement"] button:hover {
        background-color: #C69B7B !important;
        transform: none !important;
    }
    div[data-testid="stTextInput"] button svg,
    div[data-testid="stTextInputRootElement"] button svg {
        fill: #23150C !important;
        color: #23150C !important;
    }

    div[data-testid="stTextInputRootElement"]:focus-within,
    div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within,
    div[data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within,
    textarea:focus {
        border-color: #EFE2D4 !important;
        box-shadow: 0 0 0 2px rgba(223, 203, 182, 0.45) !important;
    }

    /* 9. Вкладки Вхід / Реєстрація */
    button[data-baseweb="tab"] {
        color: #C9B29B !important;
        font-weight: 600 !important;
    }
    button[data-baseweb="tab"]:hover {
        color: #EFE2D4 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #EFE2D4 !important;
        border-bottom: 3px solid #C69B7B !important;
    }

    /* 10. Сповіщення (info / success / warning / error) */
    div[data-testid="stAlert"] {
        background-color: #3A2110 !important;
        border: 1px solid #C69B7B !important;
        border-radius: 12px !important;
    }
    div[data-testid="stAlert"] p, div[data-testid="stAlert"] div {
        color: #EFE2D4 !important;
    }

    /* 11. Експандери та картка згенерованого результату */
    details {
        background-color: #D1A98A !important;
        border: 1.5px solid #46230a !important;
        border-radius: 12px !important;
    }
    details summary, details p, details span, details div {
        color: #23150C !important;
    }

    .result-showcase-header {
        background: linear-gradient(135deg, #46230a 0%, #23150C 100%);
        border: 1.5px solid #DFCBB6;
        border-radius: 14px;
        padding: 16px 20px;
        margin-bottom: 14px;
    }
    .result-showcase-header h3 {
        color: #EFE2D4 !important;
    }
    .result-badge {
        display: inline-block;
        background-color: #C69B7B;
        color: #23150C !important;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 700;
        margin-right: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "user" not in st.session_state:
    st.session_state.user = None
if "nav_page" not in st.session_state:
    st.session_state.nav_page = "🏠 Головна"
if "payment_notice" not in st.session_state:
    st.session_state.payment_notice = None
if "checkout_plan" not in st.session_state:
    st.session_state.checkout_plan = None

PLAN_INFO = {
    "free": {"name": "⚡ Старт (Безкоштовно)", "price": 0.00, "daily_limit": 2},
    "pro": {"name": "🚀 Креатор PRO", "price": 99.00, "daily_limit": 4},
    "business": {"name": "👑 Експерт / Бренд", "price": 199.00, "daily_limit": 6},
}


def format_ua_datetime(iso_str: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "")) + timedelta(hours=2)
        return dt.strftime("%d.%m.%Y о %H:%M")
    except Exception:
        return iso_str


def has_access(user_plan: str, required_plan: str) -> bool:
    hierarchy = {"free": 0, "pro": 1, "business": 2}
    return hierarchy.get(user_plan, 0) >= hierarchy.get(required_plan, 0)


def sync_user_and_quota(user: dict) -> tuple[dict, dict]:
    try:
        sub_r = requests.get(f"{API_URL}/users/{user['id']}/subscription", timeout=5)
        if sub_r.status_code == 200:
            user = sub_r.json()
            st.session_state.user = user
    except Exception:
        pass

    plan = user.get("plan", "free")
    default_lim = PLAN_INFO.get(plan, PLAN_INFO["free"])["daily_limit"]
    quota = {"plan": plan, "limit": default_lim, "used": 0, "remaining": default_lim}
    try:
        q_r = requests.get(f"{API_URL}/users/{user['id']}/quota", timeout=5)
        if q_r.status_code == 200:
            quota = q_r.json()
    except Exception:
        pass
    return user, quota


# --- ЕКРАН ВХОДУ ТА РЕЄСТРАЦІЇ ---
if st.session_state.user is None:
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        st.markdown(
            """
            <div style="text-align: center; padding: 12px 0 20px 0;">
                <h1 style="margin-bottom: 6px; font-size: 2.5rem; color: #EFE2D4;">✨ SMM AI Generator</h1>
                <p style="font-size: 1.05rem; color: #DFCBB6; margin: 0;">
                    Генератор вірусних сценаріїв та ідей для Reels і TikTok на базі ШІ
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tab_login, tab_register = st.tabs(["🔑 Вхід", "📝 Реєстрація"])

        with tab_login:
            with st.form("login_form"):
                login_email = st.text_input("Електронна пошта", placeholder="name@example.com")
                login_password = st.text_input("Пароль", type="password")
                login_submitted = st.form_submit_button("Увійти", use_container_width=True)

            if login_submitted:
                if not login_email.strip() or not login_password:
                    st.warning("Введіть пошту та пароль.")
                else:
                    try:
                        resp = requests.post(
                            f"{API_URL}/auth/login",
                            json={"email": login_email, "password": login_password},
                            timeout=10,
                        )
                        if resp.status_code == 200:
                            st.session_state.user = resp.json()
                            st.session_state.nav_page = "🏠 Головна"
                            st.session_state.checkout_plan = None
                            st.rerun()
                        else:
                            st.error(resp.json().get("detail", "Помилка входу"))
                    except requests.exceptions.ConnectionError:
                        st.error("Сервер FastAPI не запущено!")

        with tab_register:
            with st.form("register_form"):
                col1, col2 = st.columns(2)
                with col1:
                    reg_first_name = st.text_input("Ім'я", placeholder="Роксолана")
                with col2:
                    reg_last_name = st.text_input("Прізвище", placeholder="Дідух")
                reg_email = st.text_input("Електронна пошта", placeholder="name@example.com")
                reg_password = st.text_input("Пароль (мінімум 6 символів)", type="password")
                reg_submitted = st.form_submit_button("Зареєструватися", use_container_width=True)

            if reg_submitted:
                if not all([reg_first_name.strip(), reg_last_name.strip(), reg_email.strip(), reg_password]):
                    st.warning("Будь ласка, заповніть усі поля.")
                else:
                    try:
                        resp = requests.post(
                            f"{API_URL}/auth/register",
                            json={
                                "first_name": reg_first_name,
                                "last_name": reg_last_name,
                                "email": reg_email,
                                "password": reg_password,
                            },
                            timeout=10,
                        )
                        if resp.status_code == 201:
                            st.session_state.user = resp.json()
                            st.session_state.nav_page = "🏠 Головна"
                            st.session_state.checkout_plan = None
                            st.rerun()
                        else:
                            st.error(resp.json().get("detail", "Помилка реєстрації"))
                    except requests.exceptions.ConnectionError:
                        st.error("Сервер FastAPI не запущено!")

# --- ОСНОВНИЙ ІНТЕРФЕЙС ПІСЛЯ ВХОДУ ---
else:
    user, quota = sync_user_and_quota(st.session_state.user)
    user_plan = user.get("plan", "free")
    days_left = user.get("days_left", 0)

    # --- ШАПКА З НАВІГАЦІЄЮ БЕЗ КРАПОК ---
    h_logo, h_nav1, h_nav2, h_nav3, h_plan, h_exit = st.columns([2.1, 1.15, 2.0, 1.35, 2.6, 0.95])

    with h_logo:
        st.markdown(
            "<div style='padding-top: 4px; font-size: 1.35rem; font-weight: 800; color: #EFE2D4;'>"
            "✨ SMM AI Generator</div>",
            unsafe_allow_html=True,
        )

    with h_nav1:
        if st.button(
            "🏠 Головна",
            key="nav_btn_home",
            type="primary" if st.session_state.nav_page == "🏠 Головна" else "secondary",
            use_container_width=True,
        ):
            st.session_state.nav_page = "🏠 Головна"
            st.session_state.payment_notice = None
            st.session_state.checkout_plan = None
            st.rerun()

    with h_nav2:
        if st.button(
            "👤 Особисті дані та історія",
            key="nav_btn_profile",
            type="primary" if st.session_state.nav_page == "👤 Особисті дані та історія" else "secondary",
            use_container_width=True,
        ):
            st.session_state.nav_page = "👤 Особисті дані та історія"
            st.session_state.payment_notice = None
            st.session_state.checkout_plan = None
            st.rerun()

    with h_nav3:
        if st.button(
            "ℹ️ Все про сайт",
            key="nav_btn_about",
            type="primary" if st.session_state.nav_page == "ℹ️ Все про сайт" else "secondary",
            use_container_width=True,
        ):
            st.session_state.nav_page = "ℹ️ Все про сайт"
            st.session_state.payment_notice = None
            st.session_state.checkout_plan = None
            st.rerun()

    with h_plan:
        plan_title = PLAN_INFO.get(user_plan, PLAN_INFO["free"])["name"]
        if user_plan in {"pro", "business"}:
            st.markdown(
                f"<div style='padding-top: 8px; font-size: 13px; color: #DFCBB6; text-align: right;'>"
                f"<b style='color: #EFE2D4;'>{plan_title}</b> &nbsp;|&nbsp; "
                f"⏳ <b style='color: #EFE2D4;'>{days_left} дн.</b> &nbsp;|&nbsp; "
                f"<b style='color: #EFE2D4;'>{quota['remaining']}/{quota['limit']}</b></div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"<div style='padding-top: 8px; font-size: 13px; color: #DFCBB6; text-align: right;'>"
                f"<b style='color: #EFE2D4;'>{plan_title}</b> &nbsp;|&nbsp; "
                f"Сьогодні: <b style='color: #EFE2D4;'>{quota['remaining']}/{quota['limit']}</b></div>",
                unsafe_allow_html=True,
            )

    with h_exit:
        if st.button("🚪 Вийти", key="nav_btn_logout", type="primary", use_container_width=True):
            st.session_state.user = None
            st.session_state.payment_notice = None
            st.session_state.checkout_plan = None
            st.rerun()

    st.markdown("<hr style='margin: 8px 0 18px 0; border-color: #8C6343;'>", unsafe_allow_html=True)

    # ==========================================
    # 1. СТОРІНКА: ГОЛОВНА
    # ==========================================
    if st.session_state.nav_page == "🏠 Головна":
        _, main_col, _ = st.columns([0.5, 4.2, 0.5])
        with main_col:
            # Ліворуч — привітання, праворуч — бежева картка зі шкалою лімітів
            greet_col, quota_col = st.columns([1.15, 1.35], vertical_alignment="center")

            with greet_col:
                st.subheader(f"👋 Вітаємо, {user['first_name']} {user['last_name']}!")
                st.markdown(
                    "<p style='font-size: 1.05rem; color: #DFCBB6; margin-top: -6px;'>"
                    "✨ Декілька кліків — і сценарії та поради готові!</p>",
                    unsafe_allow_html=True,
                )

            with quota_col:
                percent = int((quota["remaining"] / quota["limit"]) * 100) if quota["limit"] > 0 else 0
                sub_caption = (
                    f"⏳ Абонемент <b>{PLAN_INFO[user_plan]['name']}</b> діє ще <b>{days_left} дн.</b> "
                    f"(потім повернеться на «Старт»). Оновлення о <b>00:00</b>."
                    if user_plan in {"pro", "business"}
                    else "🕛 Денний ліміт автоматично оновлюється щодня після <b>00:00</b>."
                )

                st.markdown(
                    f"""
                    <div style="
                        background: linear-gradient(180deg, #D1A98A 0%, #C69B7B 100%);
                        border: 1.5px solid #46230a;
                        border-radius: 16px;
                        padding: 14px 18px;
                        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.35);
                    ">
                        <div style="font-size: 15px; color: #23150C; margin-bottom: 8px;">
                            ⚡ <b>Доступно генерацій на сьогодні:</b>
                            <b>{quota['remaining']} із {quota['limit']}</b>
                            <span style="color: #46230a;"><i>(використано: {quota['used']})</i></span>
                        </div>
                        <div style="
                            width: 100%;
                            height: 10px;
                            background-color: #EFE2D4;
                            border: 1px solid #46230a;
                            border-radius: 999px;
                            overflow: hidden;
                            margin-bottom: 8px;
                        ">
                            <div style="
                                width: {percent}%;
                                height: 100%;
                                background: linear-gradient(90deg, #46230a 0%, #23150C 100%);
                                border-radius: 999px;
                            "></div>
                        </div>
                        <div style="font-size: 12.5px; color: #46230a; line-height: 1.35;">
                            {sub_caption}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if quota["remaining"] == 0 and user_plan != "business":
                    next_plan = "pro" if user_plan == "free" else "business"
                    st.write("")
                    if st.button("💳 Збільшити ліміт", type="primary", use_container_width=True):
                        st.session_state.checkout_plan = next_plan
                        st.session_state.payment_notice = (
                            "Денний ліміт вичерпано. Оплатіть вищий тариф, щоб отримати більше генерацій:"
                        )
                        st.session_state.nav_page = "ℹ️ Все про сайт"
                        st.rerun()

            st.write("")

            if quota["remaining"] == 0:
                st.error(
                    f"🚫 На сьогодні ви використали всі **{quota['limit']}** генерації за тарифом "
                    f"**{PLAN_INFO[user_plan]['name']}**. Нові спроби з'являться після **00:00** або після оплати вищого тарифу."
                )

            # Вибір режиму БЕЗ КРАПОК (світиться при наведенні)
            mode = st.radio(
                "Що ви хочете створити?",
                ["🎬 Створити сценарій відео", "💡 Поради (підказки)"],
                horizontal=True,
            )

            # --- РЕЖИМ 1: СТВОРЕННЯ СЦЕНАРІЮ ВІДЕО ---
            if mode == "🎬 Створити сценарій відео":
                duration_options = {
                    "20 с — Безкоштовно": ("20 с", "free"),
                    "30 с — Креатор PRO 💎 (99 грн)": ("30 с", "pro"),
                    "40 с — Експерт / Бренд 👑 (199 грн)": ("40 с", "business"),
                }

                with st.form("scenario_form"):
                    topic = st.text_input(
                        "Назва / тема відео",
                        placeholder="Наприклад: 3 фішки монтажу, які втримують увагу глядача",
                    )
                    tone = st.selectbox(
                        "🎭 Тон подачі відео",
                        ["Експертний", "Розважальний", "Мотиваційний", "Провокаційний"],
                    )
                    # Вибір секунд усередині картки ПІСЛЯ назви і тону (без крапок, світиться при наведенні)
                    selected_duration_label = st.radio(
                        "⏱️ Оберіть тривалість відео:",
                        list(duration_options.keys()),
                        horizontal=True,
                        key="video_duration_radio",
                    )
                    st.write("")
                    submitted = st.form_submit_button(
                        "🚀 Згенерувати сценарій відео",
                        use_container_width=True,
                        disabled=(quota["remaining"] <= 0),
                    )

                if submitted:
                    clean_duration, req_plan = duration_options[selected_duration_label]
                    if not has_access(user_plan, req_plan):
                        st.session_state.checkout_plan = req_plan
                        st.session_state.payment_notice = (
                            f"Тривалість відео **{clean_duration}** входить у тариф **{PLAN_INFO[req_plan]['name']}** "
                            f"({PLAN_INFO[req_plan]['price']:.2f} грн / 30 днів)."
                        )
                        st.session_state.nav_page = "ℹ️ Все про сайт"
                        st.rerun()
                    elif not topic.strip():
                        st.warning("Будь ласка, введіть назву відео.")
                    else:
                        with st.spinner(f"ШІ створює сценарій на {clean_duration}..."):
                            try:
                                response = requests.post(
                                    f"{API_URL}/scenarios/generate",
                                    json={
                                        "topic": topic,
                                        "tone": tone,
                                        "content_type": "scenario",
                                        "option_label": clean_duration,
                                        "user_id": user["id"],
                                    },
                                    timeout=40,
                                )
                                if response.status_code in (200, 201):
                                    res_data = response.json()
                                    st.session_state.last_generated = {
                                        "badge": f"🎬 Сценарій відео • {clean_duration} • {tone}",
                                        "topic": res_data["topic"],
                                        "content": res_data["content"],
                                    }
                                    st.rerun()
                                else:
                                    detail = response.json().get("detail", response.text)
                                    st.error(f"Помилка: {detail}")
                            except requests.exceptions.ConnectionError:
                                st.error("Сервер FastAPI не запущено!")

            # --- РЕЖИМ 2: ПОРАДИ (ПІДКАЗКИ) ---
            else:
                tips_options = {
                    "8 порад — Безкоштовно": ("8 порад", "free"),
                    "14 порад — Креатор PRO 💎 (99 грн)": ("14 порад", "pro"),
                    "18 порад + розписані дії — Експерт / Бренд 👑 (199 грн)": ("18 порад + дії", "business"),
                }

                with st.form("tips_form"):
                    tips_topic = st.text_input(
                        "Назва / тема для порад",
                        placeholder="Наприклад: Як просувати сторінку салону краси в Instagram",
                    )
                    # Вибір кількості порад усередині картки ПІСЛЯ назви (без крапок, світиться при наведенні)
                    selected_tips_label = st.radio(
                        "📋 Оберіть кількість порад:",
                        list(tips_options.keys()),
                        horizontal=True,
                        key="tips_count_radio",
                    )
                    st.write("")
                    tips_submitted = st.form_submit_button(
                        "💡 Згенерувати поради",
                        use_container_width=True,
                        disabled=(quota["remaining"] <= 0),
                    )

                if tips_submitted:
                    clean_tips_option, req_plan = tips_options[selected_tips_label]
                    if not has_access(user_plan, req_plan):
                        st.session_state.checkout_plan = req_plan
                        st.session_state.payment_notice = (
                            f"Пакет **{clean_tips_option}** входить у тариф **{PLAN_INFO[req_plan]['name']}** "
                            f"({PLAN_INFO[req_plan]['price']:.2f} грн / 30 днів)."
                        )
                        st.session_state.nav_page = "ℹ️ Все про сайт"
                        st.rerun()
                    elif not tips_topic.strip():
                        st.warning("Будь ласка, введіть назву теми для порад.")
                    else:
                        with st.spinner(f"ШІ готує добірку ({clean_tips_option})..."):
                            try:
                                response = requests.post(
                                    f"{API_URL}/scenarios/generate",
                                    json={
                                        "topic": tips_topic,
                                        "tone": "Поради",
                                        "content_type": "tips",
                                        "option_label": clean_tips_option,
                                        "user_id": user["id"],
                                    },
                                    timeout=50,
                                )
                                if response.status_code in (200, 201):
                                    res_data = response.json()
                                    st.session_state.last_generated = {
                                        "badge": f"💡 Добірка порад • {clean_tips_option}",
                                        "topic": res_data["topic"],
                                        "content": res_data["content"],
                                    }
                                    st.rerun()
                                else:
                                    detail = response.json().get("detail", response.text)
                                    st.error(f"Помилка: {detail}")
                            except requests.exceptions.ConnectionError:
                                st.error("Сервер FastAPI не запущено!")

            # --- ГАРНЕ ОФОРМЛЕННЯ ЗГЕНЕРОВАНОГО РЕЗУЛЬТАТУ ---
            if "last_generated" in st.session_state and st.session_state.last_generated:
                gen = st.session_state.last_generated
                st.write("")
                with st.container(border=True):
                    st.markdown(
                        f"""
                        <div class="result-showcase-header">
                            <span class="result-badge">{gen['badge']}</span>
                            <span class="result-badge">✅ Збережено в історію</span>
                            <h3 style="margin: 10px 0 0 0; color: #EFE2D4;">{gen['topic']}</h3>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.markdown(gen["content"])
                st.session_state.last_generated = None

    # ==========================================
    # 2. СТОРІНКА: ОСОБИСТІ ДАНІ ТА ІСТОРІЯ
    # ==========================================
    elif st.session_state.nav_page == "👤 Особисті дані та історія":
        prof_col, pass_col = st.columns([1.4, 1])

        with prof_col:
            with st.container(border=True):
                st.subheader("👤 Редагування особистих даних")
                with st.form("profile_edit_form"):
                    p_c1, p_c2 = st.columns(2)
                    with p_c1:
                        new_first = st.text_input("Ім'я", value=user["first_name"])
                    with p_c2:
                        new_last = st.text_input("Прізвище", value=user["last_name"])
                    new_email = st.text_input("Електронна пошта", value=user["email"])

                    save_profile = st.form_submit_button("💾 Зберегти зміни профілю", use_container_width=True)

                if save_profile:
                    try:
                        upd_resp = requests.put(
                            f"{API_URL}/users/{user['id']}",
                            json={
                                "first_name": new_first,
                                "last_name": new_last,
                                "email": new_email,
                            },
                            timeout=10,
                        )
                        if upd_resp.status_code == 200:
                            st.session_state.user = upd_resp.json()
                            st.success("Особисті дані успішно оновлено!")
                            st.rerun()
                        else:
                            st.error(upd_resp.json().get("detail", "Не вдалося оновити дані."))
                    except requests.exceptions.ConnectionError:
                        st.error("Сервер FastAPI не запущено!")

        with pass_col:
            with st.container(border=True):
                st.subheader("🔐 Зміна пароля")
                with st.form("password_change_form"):
                    old_pass = st.text_input("Поточний пароль", type="password")
                    new_pass = st.text_input("Новий пароль (від 6 символів)", type="password")
                    confirm_pass = st.text_input("Підтвердіть новий пароль", type="password")
                    save_pass = st.form_submit_button("🔑 Оновити пароль", use_container_width=True)

                if save_pass:
                    if not old_pass or not new_pass:
                        st.warning("Заповніть усі поля пароля.")
                    elif new_pass != confirm_pass:
                        st.error("Новий пароль та підтвердження не збігаються.")
                    else:
                        try:
                            pass_resp = requests.put(
                                f"{API_URL}/users/{user['id']}/password",
                                json={"old_password": old_pass, "new_password": new_pass},
                                timeout=10,
                            )
                            if pass_resp.status_code == 200:
                                st.success("✅ Пароль успішно змінено!")
                            else:
                                st.error(pass_resp.json().get("detail", "Помилка зміни пароля."))
                        except requests.exceptions.ConnectionError:
                            st.error("Сервер FastAPI не запущено!")

        st.divider()

        h_col1, h_col2 = st.columns([3, 1])
        with h_col1:
            st.subheader("📚 Історія ваших генерацій")
        with h_col2:
            only_favorites = st.checkbox("⭐ Тільки улюблені")

        try:
            history_response = requests.get(
                f"{API_URL}/scenarios/history",
                params={"user_id": user["id"]},
                timeout=10,
            )
            if history_response.status_code == 200:
                scenarios = history_response.json()
                if only_favorites:
                    scenarios = [s for s in scenarios if s.get("is_favorite")]

                if not scenarios:
                    if only_favorites:
                        st.info("У вас поки що немає улюблених записів. Натисніть зірочку біля потрібного!")
                    else:
                        st.info("Історія порожня. Перейдіть на «Головну» та згенеруйте перший сценарій або поради!")
                else:
                    for item in scenarios:
                        fav_icon = "⭐" if item.get("is_favorite") else "☆"
                        type_badge = "💡 Поради" if item.get("content_type") == "tips" else "🎬 Сценарій"
                        opt_label = item.get("option_label", "")
                        formatted_date = format_ua_datetime(item["created_at"])

                        with st.container(border=True):
                            header_col, fav_col, del_col = st.columns([6, 1.5, 1.2])
                            with header_col:
                                st.markdown(f"#### {fav_icon} {item['topic']}")
                                st.caption(
                                    f"{type_badge} (**{opt_label}**)  |  🎭 {item['tone']}  |  🕒 **{formatted_date}**"
                                )
                            with fav_col:
                                btn_label = "💔 З улюблених" if item.get("is_favorite") else "⭐ В улюблені"
                                if st.button(btn_label, key=f"fav_{item['id']}", use_container_width=True):
                                    requests.patch(
                                        f"{API_URL}/scenarios/{item['id']}",
                                        json={"is_favorite": not item.get("is_favorite")},
                                        timeout=10,
                                    )
                                    st.rerun()
                            with del_col:
                                if st.button("🗑️ Видалити", key=f"del_{item['id']}", use_container_width=True):
                                    requests.delete(
                                        f"{API_URL}/scenarios/{item['id']}",
                                        timeout=10,
                                    )
                                    st.rerun()

                            content_col, note_col = st.columns([2, 1])
                            with content_col:
                                with st.expander("📄 Переглянути повний результат генерації", expanded=False):
                                    st.markdown(item["content"])
                            with note_col:
                                note_text = st.text_area(
                                    "📝 Ваші замітки:",
                                    value=item.get("notes", ""),
                                    placeholder="Наприклад: зняти у п'ятницю, додати трендовий звук...",
                                    key=f"note_input_{item['id']}",
                                    height=100,
                                )
                                if st.button("💾 Зберегти замітку", key=f"save_note_{item['id']}", use_container_width=True):
                                    patch_resp = requests.patch(
                                        f"{API_URL}/scenarios/{item['id']}",
                                        json={"notes": note_text},
                                        timeout=10,
                                    )
                                    if patch_resp.status_code == 200:
                                        st.toast("Замітку збережено в базу!", icon="✅")
        except requests.exceptions.ConnectionError:
            st.error("Сервер FastAPI не запущено!")

    # ==========================================
    # 3. СТОРІНКА: ВСЕ ПРО САЙТ ТА ОПЛАТА
    # ==========================================
    elif st.session_state.nav_page == "ℹ️ Все про сайт":
        st.subheader("ℹ️ Все про платформу SMM AI Generator")

        about1, about2, about3 = st.columns(3)

        with about1:
            with st.container(border=True):
                st.markdown("#### 👩‍💻 Хто створив та безпека даних")
                st.markdown(
                    "**Авторка проєкту:** Дідух Роксолана\n\n"
                    "**Рік заснування:** 2026\n\n"
                    "🔒 **Повний захист даних:** усі паролі шифруються криптографічним алгоритмом "
                    "**PBKDF2-SHA256** із унікальною сіллю. Ваші особисті сценарії, замітки та налаштування "
                    "прив'язані виключно до вашого облікового запису і недоступні стороннім особам."
                )

        with about2:
            with st.container(border=True):
                st.markdown("#### 🎯 Для чого потрібен цей сайт")
                st.markdown(
                    "Платформа створена для **SMM-спеціалістів, блогерів, експертів та підприємців**, "
                    "які розвивають Instagram Reels і TikTok.\n\n"
                    "Замість годин роздумів над тим, що зняти, сервіс миттєво формує:\n"
                    "• готові сценарії під точний хронометраж (20, 30 або 40 секунд);\n"
                    "• практичні добірки порад із покроковими діями для росту охоплень."
                )

        with about3:
            with st.container(border=True):
                st.markdown("#### 🏆 Наші плюси та переваги на ринку")
                st.markdown(
                    "✔ **Чиста українська мова** без суржику й машинного перекладу;\n\n"
                    "✔ **Розумний таймінг** — текст чітко розрахований під секунди ролика;\n\n"
                    "✔ **Власний робочий простір** — історія генерацій, папка «Улюблене» та нотатки до зйомок в одному місці;\n\n"
                    "✔ **Доступна ціна** — від безкоштовного старту до преміум-можливостей за ціною однієї кави."
                )

        st.divider()

        # --- ВІКНО ОПЛАТИ ОБРАНОГО ТАРИФУ ---
        if st.session_state.checkout_plan in {"pro", "business"}:
            target_plan = st.session_state.checkout_plan
            plan_data = PLAN_INFO[target_plan]
            exact_price = plan_data["price"]

            _, pay_col, _ = st.columns([1, 2.2, 1])
            with pay_col:
                if st.session_state.payment_notice:
                    st.info(f"ℹ️ {st.session_state.payment_notice}")

                with st.container(border=True):
                    st.subheader(f"💳 Оплата тарифу: {plan_data['name']}")
                    st.markdown(
                        f"**Термін дії абонемента:** 30 днів (щоденний відлік)\n\n"
                        f"**Сума до сплати:** `{exact_price:.2f} грн`"
                    )

                    with st.form("checkout_form"):
                        card_num = st.text_input(
                            "Номер банківської картки (16 цифр)",
                            value="4441 1144 5566 7788",
                            max_chars=19,
                        )
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            card_exp = st.text_input("Термін (ММ/РР)", value="09/28", max_chars=5)
                        with c2:
                            card_cvv = st.text_input("CVV", value="777", type="password", max_chars=3)
                        with c3:
                            amount_input = st.number_input(
                                "Сума оплати (грн)",
                                min_value=0.00,
                                value=exact_price,
                                step=0.01,
                                format="%.2f",
                            )

                        btn_pay, btn_cancel = st.columns(2)
                        with btn_pay:
                            confirm_pay = st.form_submit_button(
                                f"✅ Оплатити {exact_price:.2f} грн",
                                type="primary",
                                use_container_width=True,
                            )
                        with btn_cancel:
                            cancel_pay = st.form_submit_button(
                                "← Назад до тарифів",
                                use_container_width=True,
                            )

                    if cancel_pay:
                        st.session_state.checkout_plan = None
                        st.session_state.payment_notice = None
                        st.rerun()

                    if confirm_pay:
                        try:
                            pay_resp = requests.post(
                                f"{API_URL}/users/{user['id']}/pay",
                                json={
                                    "plan": target_plan,
                                    "amount_paid": amount_input,
                                    "card_number": card_num,
                                    "card_expiry": card_exp,
                                    "card_cvv": card_cvv,
                                },
                                timeout=10,
                            )
                            if pay_resp.status_code == 200:
                                st.session_state.user = pay_resp.json()
                                st.session_state.checkout_plan = None
                                st.session_state.payment_notice = None
                                st.success(
                                    f"🎉 Все пройшло добре! Оплату {amount_input:.2f} грн підтверджено. "
                                    f"Тариф **{plan_data['name']}** активовано на **30 днів**. Переходимо на головну..."
                                )
                                time.sleep(2)
                                st.session_state.nav_page = "🏠 Головна"
                                st.rerun()
                            else:
                                err_msg = pay_resp.json().get("detail", "Помилка проведення платежу.")
                                st.error(f"❌ Помилка оплати: {err_msg}")
                        except requests.exceptions.ConnectionError:
                            st.error("Сервер FastAPI не запущено!")

            st.divider()

        # --- ТАРИФИ ТА ОПЛАТА ---
        if user_plan in {"pro", "business"}:
            st.success(
                f"✅ Ваш поточний тариф: **{PLAN_INFO[user_plan]['name']}**  |  "
                f"⏳ Залишилось днів у цьому тарифі: **{days_left} дн.** "
                f"(діє до `{user.get('plan_end_date')}`, після завершення повернеться на «Старт»)."
            )

        st.subheader("💎 Тарифи та підписка")
        st.caption("Оберіть оптимальний план для щоденної роботи з контентом:")

        plan1, plan2, plan3 = st.columns(3)

        with plan1:
            with st.container(border=True):
                st.markdown("### ⚡ Старт (Безкоштовно)")
                st.markdown("## 0.00 грн / міс")
                st.caption("Базовий доступ для знайомства з платформою")
                st.markdown(
                    "✔ До **2 генерацій на день** (оновлення о 00:00)\n\n"
                    "✔ Сценарії відео тривалістю **20 с**\n\n"
                    "✔ Генерація **8 порад** за темою\n\n"
                    "✔ Збереження історії, замітки та «Улюблене»"
                )
                is_current = user_plan == "free"
                if st.button(
                    "✅ Ваш поточний тариф" if is_current else "Перейти на Старт",
                    type="primary",
                    disabled=is_current,
                    use_container_width=True,
                    key="plan_free",
                ):
                    r = requests.post(
                        f"{API_URL}/users/{user['id']}/pay",
                        json={"plan": "free", "amount_paid": 0.0},
                        timeout=10,
                    )
                    if r.status_code == 200:
                        st.session_state.user = r.json()
                        st.rerun()

        with plan2:
            with st.container(border=True):
                st.markdown("### 🚀 Креатор PRO")
                st.markdown("## 99.00 грн / 30 днів")
                st.caption("Для активних блогерів та SMM-спеціалістів")
                st.markdown(
                    "✔ До **4 генерацій на день** (оновлення о 00:00)\n\n"
                    "✔ Сценарії відео тривалістю **20 с та 30 с**\n\n"
                    "✔ Генерація до **14 порад** за темою\n\n"
                    "✔ Покращена деталізація хуків та озвучки"
                )
                is_current = user_plan == "pro"
                if st.button(
                    f"✅ Активний (залишилось {days_left} дн.)" if is_current else "💳 Обрати за 99.00 грн",
                    type="primary",
                    disabled=is_current,
                    use_container_width=True,
                    key="plan_pro",
                ):
                    st.session_state.checkout_plan = "pro"
                    st.session_state.payment_notice = None
                    st.rerun()

        with plan3:
            with st.container(border=True):
                st.markdown("### 👑 Експерт / Бренд")
                st.markdown("## 199.00 грн / 30 днів")
                st.caption("Максимальні можливості для брендів та експертів")
                st.markdown(
                    "✔ До **6 генерацій на день** (оновлення о 00:00)\n\n"
                    "✔ Сценарії відео **20 с, 30 с та 40 с**\n\n"
                    "✔ **18 порад + розписані покрокові дії**\n\n"
                    "✔ Повноцінні стратегії просування"
                )
                is_current = user_plan == "business"
                if st.button(
                    f"✅ Активний (залишилось {days_left} дн.)" if is_current else "💳 Обрати за 199.00 грн",
                    type="primary",
                    disabled=is_current,
                    use_container_width=True,
                    key="plan_biz",
                ):
                    st.session_state.checkout_plan = "business"
                    st.session_state.payment_notice = None
                    st.rerun()