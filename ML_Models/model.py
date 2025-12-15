import pandas as pd
from catboost import CatBoostClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

animals = pd.read_csv(r'D:\Animals.csv')
health_log = pd.read_csv(r'D:\Animal_Health_Log.csv')

health_log['Symptoms'] = health_log['Symptoms'].fillna('No symptoms')
health_log['Treatment'] = health_log['Treatment'].fillna('No treatment')

merged_df = pd.merge(health_log, animals, on='Animal_ID', how='left')


merged_df['Weight_Age_Ratio'] = merged_df['Weight'] / (merged_df['Age'] + 1)
merged_df['Days_Since_Vaccine'] = (
    pd.to_datetime(merged_df['Check_Date']) - pd.to_datetime(merged_df['Vaccination_Date'])
).dt.days.fillna(999).astype(int)
merged_df['Vaccine_Recent'] = (merged_df['Days_Since_Vaccine'] <= 30).astype(int)


y = merged_df['Health_Status']
X = merged_df[['Weight', 'Age', 'Days_Since_Vaccine', 'Weight_Age_Ratio', 'Vaccine_Recent',
               'Type', 'Symptoms', 'Treatment']]


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)


cat_features = ['Type', 'Symptoms', 'Treatment']
model = CatBoostClassifier(
    iterations=300,
    learning_rate=0.1,
    depth=6,
    auto_class_weights='Balanced',
    verbose=0,
    random_state=42
)
model.fit(X_train, y_train, cat_features=cat_features)


y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))



joblib.dump(model, r"D:\catboost_model.pkl")
print("✅ Saved: D:\\catboost_model.pkl")