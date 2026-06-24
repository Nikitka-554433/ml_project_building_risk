import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Строительный калькулятор", layout="wide")
st.title("Прогноз стоимости строительства")
API_URL = "http://localhost:8000"

with st.form("prediction_form"):
    col1, col2 = st.columns(2)
    with col1:
        wall_material = st.selectbox("Материал стен", ["монолит", "кирпич", "панель"])
        avg_house_area = st.number_input("Ср. площадь дома (м²)", min_value=20.0, value=100.0)
        avg_construction_period = st.number_input("Срок строительства (мес)", min_value=6.0, value=18.0)
    with col2:
        foundation_type = st.selectbox("Тип фундамента", ["ленточный", "свайный", "плитный"])
        roof_type = st.selectbox("Тип крыши", ["скатная", "плоская"])
        usage_count = st.number_input("Кол-во использований", min_value=1, value=50)
    submitted = st.form_submit_button("Рассчитать")

if submitted:
    payload = {
        "wall_material": wall_material,
        "avg_house_area": avg_house_area,
        "avg_construction_period": avg_construction_period,
        "foundation_type": foundation_type,
        "roof_type": roof_type,
        "usage_count": usage_count
    }
    try:
        response = requests.post(f"{API_URL}/predict", json=payload)
        if response.status_code == 200:
            st.success(f"Прогноз стоимости: {response.json()['predicted_cost']:,.0f} руб.")
        else:
            st.error("Ошибка сервиса")
    except:
        st.error("Не удалось подключиться к сервису")
