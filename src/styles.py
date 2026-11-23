import streamlit as st

def inject_custom_animations():
    """Ін'єкція кастомних стилів, колірної гами та анімацій у Streamlit."""
    st.markdown("""
        <style>
        /* 1. ГЛОБАЛЬНІ КОЛЬОРИ ТА ФОН */
        .stApp {
            background-color: #23150C !important;
            color: #FAF8F5 !important;
        }

        /* 2. ТЕКСТ ТА ЗАГОЛОВКИ */
        h1, h2, h3, h4, h5, h6, label, .stCaption {
            color: #FAF8F5 !important;
        }
        
        .stCaption {
            color: #D2CEC6 !important;
        }

        /* 3. КНОПКИ (Bronze Gold Accent) */
        div.stButton > button {
            background-color: #C69B7B !important;
            color: #23150C !important;
            border: 1px solid #8C6343 !important;
            font-weight: bold !important;
            border-radius: 8px !important;
            transition: transform 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease !important;
        }
        
        div.stButton > button:hover {
            background-color: #D2CEC6 !important;
            transform: translateY(-2px) scale(1.01) !important;
            box-shadow: 0px 4px 14px rgba(198, 155, 123, 0.3) !important;
        }

        div.stButton > button:active {
            transform: translateY(0px) scale(0.98) !important;
        }

        /* 4. ПОЛЯ ВВОДУ ТА СЕЛЕКТБОКСИ (Warm Sand Surface) */
        div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
            background-color: #301A09 !important;
            border: 1px solid #533722 !important;
            color: #FAF8F5 !important;
            border-radius: 8px !important;
        }

        input {
            color: #FAF8F5 !important;
        }

        /* 5. КАРТКИ ТА ЕКСПАНДЕРИ (Warm Muted Brown Borders & Sand Cards) */
        div[data-testid="stExpander"] {
            background-color: #301A09 !important;
            border: 1px solid #8C6343 !important;
            border-radius: 8px !important;
            color: #FAF8F5 !important;
            transition: all 0.3s ease-in-out;
        }

        /* 6. АНІМАЦІЯ ПОЯВИ (FadeInUp) */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(18px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .element-container, div[data-testid="stForm"] {
            animation: fadeInUp 0.4s ease-out forwards;
        }

        /* 7. ACCESSIBILITY (Захист від мерехтіння) */
        @media (prefers-reduced-motion: reduce) {
            *, ::before, ::after {
                animation-duration: 0.01ms !important;
                transition-duration: 0.01ms !important;
            }
        }
        </style>
    """, unsafe_allow_html=True)