# 🐄 Animal Health Prediction Setup Guide
## 📌 Overview
A machine learning system that predicts animal health status using CatBoost classifier, with a user-friendly Streamlit web interface.


# Project Structure
        project/
        ├── Animals.csv
        ├── Animal_Health_Log.csv
        ├── model.py              # Training script
        ├── app_final.py         # Streamlit web app
        ├── catboost_model.pkl   # Saved trained model
        └── README.md
## ⚙️ Installation
        pip install pandas catboost scikit-learn joblib streamlit

## 🚀 Quick Start

1. Train the Model


        python model.py

⚠️ What this does:
- Loads Animals.csv and Animal_Health_Log.csv
- Merges and preprocesses data
- Creates features (weight/age ratio, days since vaccine, etc.)
- Trains CatBoostClassifier with balanced weights
- Saves model as catboost_model.pkl


## 2. Run the Web App

        streamlit run app_final.py        


## 🌐 Access the Model:
Once the app is running, open your browser and go to:
👉 http://localhost:8501

⚠️ App Features:
- Input animal details (weight, age, days since vaccine)
- Select type, symptoms, and treatment
- Get instant health prediction

## 📂 File Paths - IMPORTANT
All files must be in the same directory as the code.

Example code paths:
        
        These must exist at these exact locations:
        pd.read_csv(r"D:\Animals.csv")                # ← Must exist
        pd.read_csv(r"D:\Animal_Health_Log.csv")      # ← Must exist  
        joblib.dump(model, r"D:\catboost_model.pkl")  # ← Will be created

⚠️ Error if paths don't match: FileNotFoundError

