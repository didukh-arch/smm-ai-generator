import streamlit as st
from src.state import select_history, select_history_count, action_clear_history

def render_header():
    """Відображає шапку сайту (Header)."""
    st.title("🎬 SMM AI Generator")
    st.caption("Твій розумний помічник для створення контенту в TikTok & Reels")
    st.markdown("---")

def render_history_section():
    """Відображає секцію історії з використанням селекторів."""
    count = select_history_count()
    st.subheader(f"📜 Історія генерацій ({count})")
    
    history = select_history()
    
    if not history:
        st.info("Історія поки порожня. Згенеруйте свій перший сценарій!")
    else:
        if st.button("🗑️ Очистити історію"):
            action_clear_history()
            st.rerun()

        for item in reversed(history):
            with st.expander(f"📌 Тема: {item['topic']} ({item['tone']})"):
                st.markdown(item["content"])