import streamlit as st
import pandas as pd
import datetime
import json
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

st.markdown("### Enter today’s data")

col1, col2 = st.columns(2)

with col1:
    sleep = st.slider("😴 Sleep (hours)", 0.0, 12.0, 7.0)
    screen = st.slider("📱 Screen Time (hours)", 0.0, 16.0, 6.0)

with col2:
    tasks = st.slider("📋 Tasks today", 0, 10, 3)
    mood = st.slider("🙂 Mood (1 = terrible, 5 = great)", 1, 5, 3)

if st.button("😈 Simulate Bad Day"):
    sleep, screen, tasks, mood = 4, 10, 7, 2

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

# -------- WRITE LOCAL JSON (ALWAYS) --------
latest_data = {
    "user": username,
    "sleep": sleep,
    "screen": screen,
    "tasks": tasks,
    "mood": mood,
    "burnout": burnout_score,
    "status": status,
    "date": datetime.date.today().isoformat()
}

with open("latest_data.json", "w") as f:
    json.dump(latest_data, f, indent=2)

# -------- SAVE BUTTON --------
st.markdown("### 💾 Save Today’s Data")

if st.button("Save to Firebase"):
    db.collection("users") \
      .document(username) \
      .collection("burnout_logs") \
      .document(latest_data["date"]) \
      .set({
          **latest_data,
          "timestamp": firestore.SERVER_TIMESTAMP
      })

    st.success("Saved to Firebase + local JSON")

# -------- HISTORY (OPTIONAL) --------
user_ref = db.collection("users").document(username).collection("burnout_logs")
docs = user_ref.order_by("timestamp").stream()
data = [d.to_dict() for d in docs]

if data:
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    st.line_chart(df.set_index("date")["burnout"])
