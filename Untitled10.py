import pandas as pd
import matplotlib as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from imblearn.over_sampling import SMOTE
from sklearn.ensemble import RandomForestClassifier

df = pd.read_csv("Stress Dataset.csv") 
df.drop(columns=["Have you been dealing with anxiety or tension recently?.1"], inplace=True) 
df = df.drop_duplicates(keep = "first") 
rename_dict = {
    "Gender": "Gender",
    "Age": "Age",
    "Have you recently experienced stress in your life?": "Recent Stress",
    "Have you noticed a rapid heartbeat or palpitations?": "Rapid Heartbeat",
    "Have you been dealing with anxiety or tension recently?": "Anxiety/Tension",
    "Do you face any sleep problems or difficulties falling asleep?": "Sleep Issues",
    "Have you been getting headaches more often than usual?": "Frequent Headaches",
    "Do you get irritated easily?": "Irritability",
    "Do you have trouble concentrating on your academic tasks?": "Concentration Issues",
    "Have you been feeling sadness or low mood?": "Sadness/Low Mood",
    "Have you been experiencing any illness or health issues?": "Health Issues",
    "Do you often feel lonely or isolated?": "Loneliness/Isolation",
    "Do you feel overwhelmed with your academic workload?": "Overwhelmed by Work",
    "Are you in competition with your peers, and does it affect you?": "Peer Competition",
    "Do you find that your relationship often causes you stress?": "Relationship Stress",
    "Are you facing any difficulties with your professors or instructors?": "Professors Issues",
    "Is your working environment unpleasant or stressful?": "Work Environment Stress",
    "Do you struggle to find time for relaxation and leisure activities?": "Lack of Leisure Time",
    "Is your hostel or home environment causing you difficulties?": "Home Issues",
    "Do you lack confidence in your academic performance?": "Lack of Academic Confidence",
    "Do you lack confidence in your choice of academic subjects?": "Lack of Subject Confidence",
    "Academic and extracurricular activities conflicting for you?": "Activities Conflict",
    "Do you attend classes regularly?": "Class Attendance",
    "Have you gained/lost weight?": "Weight Change",
    "Which type of stress do you primarily experience?": "Type of Stress"
}
df.rename(columns=rename_dict, inplace=True) 
df["Type of Stress"] = df["Type of Stress"].map({
    "Eustress (Positive Stress) - Stress that motivates and enhances performance.": 1,
    "No Stress - Currently experiencing minimal to no stress.": 2,
    "Distress (Negative Stress) - Stress that causes anxiety and impairs well-being.": 3
}) 
df = df[df["Age"] <= 50] 

df['Overall Stress Level'] = df[['Recent Stress', 'Anxiety/Tension', 'Overwhelmed by Work', 'Relationship Stress']].sum(axis=1) 

df['Health and Well-being Issues'] = df[['Sleep Issues', 'Frequent Headaches', 'Health Issues', 'Sadness/Low Mood', 'Irritability']].sum(axis=1) 

df['Academic Challenges'] = df[['Concentration Issues', 'Lack of Academic Confidence', 'Lack of Subject Confidence', 'Class Attendance']].sum(axis=1) 

df['Social and Environmental Stressors'] = df[['Loneliness/Isolation', 'Peer Competition', 'Professors Issues', 'Work Environment Stress', 'Home Issues']].sum(axis=1) 

df['Lifestyle Factors'] = df[['Lack of Leisure Time', 'Activities Conflict', 'Weight Change']].sum(axis=1) 
X = df.drop("Type of Stress", axis=1)
y = df["Type of Stress"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=45) 
smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X_train, y_train)

X_train_final, X_test_final, y_train_final, y_test_final = train_test_split(X_resampled, y_resampled, test_size=0.2, random_state=42) 
model = RandomForestClassifier(random_state=42)
model.fit(X_train_final, y_train_final) 
y_pred = model.predict(X_test_final)
print("Accuracy:", accuracy_score(y_test_final, y_pred))
print("Classification Report:\n", classification_report(y_test_final, y_pred))

def predict_user_input(user_input):
    user_data = pd.DataFrame([user_input], columns=X.columns[:24])
    user_data['Overall Stress Level'] = user_data.iloc[:, [4, 3, 12, 14]].sum(axis=1)
    user_data['Health and Well-being Issues'] = user_data.iloc[:, [5, 6, 10, 9, 7]].sum(axis=1)
    user_data['Academic Challenges'] = user_data.iloc[:, [8, 19, 20, 22]].sum(axis=1)
    user_data['Social and Environmental Stressors'] = user_data.iloc[:, [11, 13, 15, 16, 18]].sum(axis=1)
    user_data['Lifestyle Factors'] = user_data.iloc[:, [17, 21, 23]].sum(axis=1)
    prediction = model.predict(user_data)
    return prediction[0]

user_input = [1, 20, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
predicted_stress = predict_user_input(user_input)
print("Predicted Type of Stress:", predicted_stress) 