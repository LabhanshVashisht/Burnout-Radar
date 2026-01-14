import streamlit as st
import datetime
import json
import os
import pandas as pd
import matplotlib.pyplot as plt

# -------- FIREBASE --------
import firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# -------- USER --------
params = st.query_params
username = params.get("user")

if not username:
    st.error("Not logged in")
    st.stop()

username = username.lower()

# -------- UI --------
st.set_page_config(page_title="Burnout Radar", layout="centered")
st.title("🧠 Burnout Radar")
st.subheader("Predict burnout before it hits")

# -------- INPUTS --------
st.markdown("### Enter today’s data")

col1, col2 = st.columns(2)

with col1:
    sleep = st.slider("😴 Sleep (hours)", 0.0, 12.0, 7.0)
    screen = st.slider("📱 Screen Time (hours)", 0.0, 16.0, 6.0)

with col2:
    tasks = st.slider("📋 Tasks today", 0, 10, 3)
    mood = st.slider("🙂 Mood (1 = terrible, 5 = great)", 1, 5, 3)

# -------- BURNOUT LOGIC --------
sleep_score = max(0, (8 - sleep) / 8)
screen_score = min(screen / 10, 1)
task_score = min(tasks / 8, 1)
mood_score = (5 - mood) / 4

burnout = (
    0.35 * sleep_score**1.5 +
    0.25 * screen_score**1.3 +
    0.25 * task_score +
    0.15 * mood_score
)

burnout_score = int(min(100, burnout * 100))

# -------- STATUS --------
if burnout_score < 35:
    status = "Low"
elif burnout_score < 70:
    status = "Moderate"
else:
    status = "High"

st.metric("Burnout Score", burnout_score, status)

# -------- SAVE BUTTON --------
st.markdown("### 💾 Save Today’s Data")

if st.button("Save to Firebase"):
    today = datetime.date.today().isoformat()

    data = {
        "user": username,
        "date": today,
        "sleep": sleep,
        "screen": screen,
        "tasks": tasks,
        "mood": mood,
        "burnout": burnout_score,
        "status": status
    }

    # 🔹 Save to Firebase
    db.collection("users") \
      .document(username) \
      .collection("burnout_logs") \
      .document(today) \
      .set({**data, "timestamp": firestore.SERVER_TIMESTAMP})

    # 🔹 Save to USER-SPECIFIC JSON
    os.makedirs("users_data", exist_ok=True)
    with open(f"users_data/{username}.json", "w") as f:
        json.dump(data, f, indent=2)

    st.success("Saved to Firebase and local JSON")

# -------- LOAD HISTORY FROM FIREBASE --------
user_ref = (
    db.collection("users")
      .document(username)
      .collection("burnout_logs")
)

docs = user_ref.order_by("date").stream()

history_rows = []
for doc in docs:
    history_rows.append(doc.to_dict())

if history_rows:
    history_df = pd.DataFrame(history_rows)
    history_df["date"] = pd.to_datetime(history_df["date"])
else:
    history_df = pd.DataFrame(columns=["date", "burnout"])

