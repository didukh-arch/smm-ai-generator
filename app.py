import streamlit as st
import requests
from src.styles import inject_custom_animations

API_URL = "http://127.0.0.1:8000/api/v1"

st.set_page_config(page_title="SMM AI Generator", page_icon="✨", layout="centered")
inject_custom_animations()

st.title("✨ SMM AI Generator")
st.caption("Генератор вірусних сценаріїв для Reels та TikTok на базі ШІ")

with st.form("scenario_form"):
    topic = st.text_input("Тема відео", placeholder="Наприклад: Як набрати першу 1000 підписників у Reels")
    tone = st.selectbox("Тон подачі", ["Експертний", "Розважальний", "Мотиваційний", "Провокаційний"])
    submitted = st.form_submit_button("Згенерувати сценарій")

if submitted:
    if not topic.strip():
        st.warning("Будь ласка, введіть тему відео.")
    else:
        with st.spinner("ШІ створює сценарій та зберігає у базу даних..."):
            try:
                response = requests.post(
                    f"{API_URL}/scenarios/generate",
                    json={"topic": topic, "tone": tone},
                    timeout=30
                )
                if response.status_code == 200:
                    result = response.json()
                    st.success("Сценарій готовий та збережений у базу smm_generator.db!")
                    st.markdown(result["content"])
                else:
                    try:
                        error_detail = response.json().get("detail", response.text)
                    except Exception:
                        error_detail = f"Код {response.status_code}: {response.text}"
                    st.error(f"Помилка сервера: {error_detail}")
            except requests.exceptions.ConnectionError:
                st.error("Сервер FastAPI не запущено! Запусти його у першому терміналі.")

st.divider()
st.subheader("📚 Історія збережених сценаріїв (із БД)")

try:
    history_response = requests.get(f"{API_URL}/scenarios/history", timeout=10)
    if history_response.status_code == 200:
        scenarios = history_response.json()
        if not scenarios:
            st.info("У базі даних поки що порожньо. Згенеруй перший сценарій!")
        else:
            for item in scenarios:
                with st.expander(f"#{item['id']} | {item['topic']} ({item['tone']})"):
                    st.markdown(item["content"])
except requests.exceptions.ConnectionError:
    st.caption("⚠️ Запустіть бекенд FastAPI, щоб завантажити історію з бази даних.")