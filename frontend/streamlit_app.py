import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Строительный калькулятор", layout="wide")
st.title("🏗️ Прогноз стоимости строительства")

API_URL = "http://localhost:8000"

# Инициализация payload в session_state
if "payload" not in st.session_state:
    st.session_state.payload = {}

# ============================================================
# Вкладка 1: Калькулятор
tab1, tab2 = st.tabs(["📊 Калькулятор", "📈 Аналитика"])

with tab1:
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
        st.session_state.payload = {
            "wall_material": wall_material,
            "avg_house_area": avg_house_area,
            "avg_construction_period": avg_construction_period,
            "foundation_type": foundation_type,
            "roof_type": roof_type,
            "usage_count": usage_count
        }
        try:
            response = requests.post(f"{API_URL}/predict", json=st.session_state.payload)
            if response.status_code == 200:
                st.success(f"💰 Прогноз стоимости: {response.json()['predicted_cost']:,.0f} руб.")
            else:
                st.error("❌ Ошибка сервиса")
        except:
            st.error("❌ Не удалось подключиться к сервису")

    # Регион (визуальный элемент)
    regions = ['Москва', 'Санкт-Петербург', 'Краснодар', 'Екатеринбург', 'Новосибирск']
    st.selectbox("📍 Регион строительства", regions)

# Вкладка 2: Аналитика
with tab2:
    st.subheader("📈 Анализ зависимости стоимости от параметров")

    if st.session_state.get("payload"):
        payload = st.session_state.payload

        # График цены площади 
        st.markdown("**Зависимость стоимости от площади**")
        areas = np.linspace(50, 500, 10)
        prices_area = []
        for area in areas:
            p = payload.copy()
            p["avg_house_area"] = area
            try:
                r = requests.post(f"{API_URL}/predict", json=p)
                if r.status_code == 200:
                    prices_area.append(r.json()["predicted_cost"])
                else:
                    prices_area.append(None)
            except:
                prices_area.append(None)

        valid = [(a, pr) for a, pr in zip(areas, prices_area) if pr is not None]
        if valid:
            areas_v, prices_v = zip(*valid)
            fig, ax = plt.subplots(figsize=(6, 3))
            ax.plot(areas_v, prices_v, marker='o', linestyle='-', color='blue')
            ax.set_xlabel('Площадь (м²)')
            ax.set_ylabel('Стоимость (руб.)')
            ax.grid(True)
            st.pyplot(fig)
        else:
            st.warning("Не удалось построить график")

        # -График цены и срока
        st.markdown("**Зависимость стоимости от срока строительства**")
        periods = np.linspace(6, 24, 10)
        prices_time = []
        for period in periods:
            p = payload.copy()
            p["avg_construction_period"] = period
            try:
                r = requests.post(f"{API_URL}/predict", json=p)
                if r.status_code == 200:
                    prices_time.append(r.json()["predicted_cost"])
                else:
                    prices_time.append(None)
            except:
                prices_time.append(None)

        valid_t = [(t, pr) for t, pr in zip(periods, prices_time) if pr is not None]
        if valid_t:
            periods_v, prices_t_v = zip(*valid_t)
            fig2, ax2 = plt.subplots(figsize=(6, 3))
            ax2.plot(periods_v, prices_t_v, marker='s', linestyle='-', color='green')
            ax2.set_xlabel('Срок строительства (мес.)')
            ax2.set_ylabel('Стоимость (руб.)')
            ax2.grid(True)
            st.pyplot(fig2)
        else:
            st.warning("Не удалось построить график")

        # Диаграмма материалов 
        st.markdown("**Сравнение стоимости по материалам стен**")
        materials = ['монолит', 'кирпич', 'панель']
        prices_mat = []
        for mat in materials:
            p = payload.copy()
            p["wall_material"] = mat
            try:
                r = requests.post(f"{API_URL}/predict", json=p)
                if r.status_code == 200:
                    prices_mat.append(r.json()["predicted_cost"])
                else:
                    prices_mat.append(None)
            except:
                prices_mat.append(None)

        valid_m = [(m, pr) for m, pr in zip(materials, prices_mat) if pr is not None]
        if valid_m:
            names_m, prices_m = zip(*valid_m)
            fig3, ax3 = plt.subplots(figsize=(5, 3))
            ax3.bar(names_m, prices_m, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
            ax3.set_xlabel('Материал стен')
            ax3.set_ylabel('Стоимость (руб.)')
            ax3.grid(True, axis='y')
            st.pyplot(fig3)
        else:
            st.warning("Не удалось построить график")

        # Диаграмма фундаменты
        st.markdown("**Сравнение стоимости по типу фундамента**")
        foundations = ['ленточный', 'свайный', 'плитный']
        prices_found = []
        for found in foundations:
            p = payload.copy()
            p["foundation_type"] = found
            try:
                r = requests.post(f"{API_URL}/predict", json=p)
                if r.status_code == 200:
                    prices_found.append(r.json()["predicted_cost"])
                else:
                    prices_found.append(None)
            except:
                prices_found.append(None)

        valid_f = [(f, pr) for f, pr in zip(foundations, prices_found) if pr is not None]
        if valid_f:
            names_f, prices_f = zip(*valid_f)
            fig4, ax4 = plt.subplots(figsize=(5, 3))
            ax4.bar(names_f, prices_f, color=['purple', 'orange', 'red'])
            ax4.set_xlabel('Тип фундамента')
            ax4.set_ylabel('Стоимость (руб.)')
            ax4.grid(True, axis='y')
            st.pyplot(fig4)
        else:
            st.warning("Не удалось построить график")

    else:
        st.info("ℹ️ Сначала выполните расчёт в вкладке «Калькулятор»")

