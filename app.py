import streamlit as st
from src.components import render_header, render_history_section
from src.styles import inject_custom_animations
from src.state import (
    init_store, 
    action_add_scenario, 
    action_set_loading
)

# 1. Ініціалізація глобального стану та стилів
init_store()
inject_custom_animations()

# 2. Відображення шапки
render_header()

# 3. Форма налаштувань генерації
st.subheader("⚙️ Налаштування генерації")
topic = st.text_input("Введіть тему відео:")
tone = st.selectbox("Оберіть тон:", ["Експертний", "Розважальний", "Мотиваційний"])

if st.button("🚀 Згенерувати сценарій"):
    if not topic.strip():
        st.warning("Будь ласка, введіть тему!")
    else:
        action_set_loading(True)
        with st.spinner("⏳ Gemini генерує ваш контент..."):
            fake_result = f"### 🎯 Хук\nУвага! {topic}\n\n### 📝 Текст\nОсновна частина сценарію..."
            action_add_scenario(topic, fake_result, tone)
            action_set_loading(False)
            st.success("Сценарій успішно створено!")

st.markdown("---")

# 4. Відображення секції історії
render_history_section()