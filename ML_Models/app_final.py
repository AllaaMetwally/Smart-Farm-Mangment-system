import streamlit as st
import pandas as pd
import joblib


from catboost import CatBoostClassifier  
model = CatBoostClassifier()
model = joblib.load("models/catboost_model.pkl")

st.title("Animal Health Prediction 🐑🐓🐄")


weight = st.number_input("Weight", min_value=1.0, max_value=200.0, step=0.5)
age = st.number_input("Age (months)", min_value=0, max_value=120, step=1)
days_since_vaccine = st.number_input("Days Since Vaccine", min_value=0, max_value=365, step=1)
animal_type = st.selectbox("Animal Type", ["Chicken", "Sheep", "Goat", "Cow", "Unknown"])
symptoms = st.selectbox("Symptoms", ["Weakness", "Fever", "No symptoms", "Unknown"])
treatment = st.selectbox("Treatment", ["No treatment", "Medication A", "Unknown"])


row = {
    'Weight': weight,
    'Age': age,
    'Days_Since_Vaccine': days_since_vaccine,
    'Weight_Age_Ratio': weight / (age + 1),
    'Vaccine_Recent': 1 if days_since_vaccine <= 30 else 0,
    'Type': animal_type,
    'Symptoms': symptoms,
    'Treatment': treatment
}
df_input = pd.DataFrame([row])


if st.button("Predict Health Status"):
    pred = model.predict(df_input)[0]
    st.success(f"Predicted Health Status: {pred}")
