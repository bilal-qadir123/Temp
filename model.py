import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import SMOTE 
from sklearn.metrics import accuracy_score 

df = pd.read_csv("Stress Dataset.csv")
df.drop(columns=["Have you been dealing with anxiety or tension recently?.1"], inplace=True)
df = df.drop_duplicates(keep="first")

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

mapping_dict = {
    "Gender": {"Female": 0, "Male": 1}, 
    "Recent Stress": {"Not-at-all": 1, "Mild": 2, "Moderate": 3, "High": 4, "Very-high": 5},
    "Rapid Heartbeat": {"Never": 1, "Rarely": 2, "Sometimes": 3, "Often": 4, "Always": 5},
    "Anxiety/Tension": {"None": 1, "Mild": 2, "Moderate": 3, "Severe": 4, "Extreme": 5},
    "Sleep Issues": {"Never": 1, "Rarely": 2, "Sometimes": 3, "Often": 4, "Always": 5},
    "Frequent Headaches": {"Never": 1, "Rarely": 2, "Sometimes": 3, "Often": 4, "Always": 5},
    "Irritability": {"Not-at-all": 1, "Rarely": 2, "Sometimes": 3, "Often": 4, "Very-often": 5},
    "Concentration Issues": {"No": 1, "Rarely": 2, "Sometimes": 3, "Often": 4, "Very-often": 5},
    "Sadness/Low Mood": {"Never": 1, "Rarely": 2, "Sometimes": 3, "Often": 4, "Always": 5},
    "Health Issues": {"None": 1, "Mild": 2, "Moderate": 3, "Severe": 4, "Very-severe": 5},
    "Loneliness/Isolation": {"Never": 1, "Rarely": 2, "Sometimes": 3, "Often": 4, "Always": 5},
    "Overwhelmed by Work": {"Not-at-all": 1, "Rarely": 2, "Sometimes": 3, "Often": 4, "Very-often": 5},
    "Peer Competition": {"Not-at-all": 1, "Mildly": 2, "Moderately": 3, "Strongly": 4, "Very-strongly": 5},
    "Relationship Stress": {"Never": 1, "Rarely": 2, "Sometimes": 3, "Often": 4, "Always": 5},
    "Professors Issues": {"None": 1, "Mild": 2, "Moderate": 3, "Severe": 4, "Very-severe": 5},
    "Work Environment Stress": {"Not-at-all": 1, "Slightly": 2, "Moderately": 3, "Very": 4, "Extremely": 5},
    "Lack of Leisure Time": {"Never": 1, "Rarely": 2, "Sometimes": 3, "Often": 4, "Always": 5},
    "Home Issues": {"No-issues": 1, "Minor-issues": 2, "Moderate-issues": 3, "Severe-issues": 4, "Very-severe-issues": 5},
    "Lack of Academic Confidence": {"Very-confident": 1, "Somewhat-confident": 2, "Neutral": 3, "Somewhat-lacking": 4, "Lacking-confidence": 5},
    "Lack of Subject Confidence": {"Very-confident": 1, "Somewhat-confident": 2, "Neutral": 3, "Somewhat-lacking": 4, "Lacking-confidence": 5},
    "Activities Conflict": {"No": 1, "Rarely": 2, "Sometimes": 3, "Often": 4, "Always": 5},
    "Class Attendance": {"Always": 1, "Frequently": 2, "Sometimes": 3, "Rarely": 4, "Never": 5},
    "Weight Change": {"No-change": 1, "Slight-change": 2, "Moderate-change": 3, "Large-change": 4, "Significant-change": 5},
}

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
accuracy = accuracy_score(y_test_final, y_pred)
print(f"Model Accuracy: {accuracy * 100:.2f}%")  # Print accuracy

def preprocess_user_input(form_data):
    user_input = {
        'Gender': mapping_dict["Gender"].get(form_data.get('gender'), 0),
        'Age': int(form_data.get('age')),
        'Recent Stress': mapping_dict["Recent Stress"].get(form_data.get('stress'), 0),
        'Rapid Heartbeat': mapping_dict["Rapid Heartbeat"].get(form_data.get('rapid_heartbeat'), 0),
        'Anxiety/Tension': mapping_dict["Anxiety/Tension"].get(form_data.get('anxiety_tension'), 0),
        'Sleep Issues': mapping_dict["Sleep Issues"].get(form_data.get('sleep_issues'), 0),
        'Frequent Headaches': mapping_dict["Frequent Headaches"].get(form_data.get('frequent_headaches'), 0),
        'Irritability': mapping_dict["Irritability"].get(form_data.get('irritability'), 0),
        'Concentration Issues': mapping_dict["Concentration Issues"].get(form_data.get('concentration_issues'), 0),
        'Sadness/Low Mood': mapping_dict["Sadness/Low Mood"].get(form_data.get('sadness_low_mood'), 0),
        'Health Issues': mapping_dict["Health Issues"].get(form_data.get('health_issues'), 0),
        'Loneliness/Isolation': mapping_dict["Loneliness/Isolation"].get(form_data.get('loneliness_isolation'), 0),
        'Overwhelmed by Work': mapping_dict["Overwhelmed by Work"].get(form_data.get('overwhelmed_by_work'), 0),
        'Peer Competition': mapping_dict["Peer Competition"].get(form_data.get('peer_competition'), 0),
        'Relationship Stress': mapping_dict["Relationship Stress"].get(form_data.get('relationship_stress'), 0),
        'Professors Issues': mapping_dict["Professors Issues"].get(form_data.get('professors_issues'), 0),
        'Work Environment Stress': mapping_dict["Work Environment Stress"].get(form_data.get('work_environment_stress'), 0),
        'Lack of Leisure Time': mapping_dict["Lack of Leisure Time"].get(form_data.get('lack_of_leisure_time'), 0),
        'Home Issues': mapping_dict["Home Issues"].get(form_data.get('home_issues'), 0),
        'Lack of Academic Confidence': mapping_dict["Lack of Academic Confidence"].get(form_data.get('lack_of_academic_confidence'), 0),
        'Lack of Subject Confidence': mapping_dict["Lack of Subject Confidence"].get(form_data.get('lack_of_subject_confidence'), 0),
        'Activities Conflict': mapping_dict["Activities Conflict"].get(form_data.get('activities_conflict'), 0),
        'Class Attendance': mapping_dict["Class Attendance"].get(form_data.get('class_attendance'), 0),
        'Weight Change': mapping_dict["Weight Change"].get(form_data.get('weight_change'), 0), 
    }
    user_data = pd.DataFrame([user_input], columns=X.columns[:24])
    user_data['Overall Stress Level'] = user_data.iloc[:, [4, 3, 12, 14]].sum(axis=1)
    user_data['Health and Well-being Issues'] = user_data.iloc[:, [5, 6, 10, 9, 7]].sum(axis=1)
    user_data['Academic Challenges'] = user_data.iloc[:, [8, 19, 20, 22]].sum(axis=1)
    user_data['Social and Environmental Stressors'] = user_data.iloc[:, [11, 13, 15, 16, 18]].sum(axis=1)
    user_data['Lifestyle Factors'] = user_data.iloc[:, [17, 21, 23]].sum(axis=1)
    return user_data

def predict_user_input(user_data):
    prediction = model.predict(user_data)
    return prediction[0] 