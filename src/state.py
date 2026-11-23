import streamlit as st

# 1. STORE INITIALIZATION
def init_store():
    """Створює глобальні змінні в st.session_state."""
    if "history" not in st.session_state:
        st.session_state["history"] = []
    if "is_loading" not in st.session_state:
        st.session_state["is_loading"] = False

# 2. ACTIONS / DISPATCHERS
def action_add_scenario(topic: str, content: str, tone: str):
    """Додає новий сценарій до історії."""
    new_item = {
        "topic": topic,
        "content": content,
        "tone": tone
    }
    st.session_state["history"].append(new_item)

def action_set_loading(status: bool):
    """Змінює статус завантаження."""
    st.session_state["is_loading"] = status

def action_clear_history():
    """Очищає історію."""
    st.session_state["history"] = []

# 3. SELECTORS
def select_history():
    """Повертає список усіх сценаріїв."""
    return st.session_state.get("history", [])

def select_history_count():
    """Повертає кількість сценаріїв в історії."""
    return len(st.session_state.get("history", []))

def select_is_loading():
    """Повертає статус завантаження."""
    return st.session_state.get("is_loading", False)