import streamlit as st
import datetime
import json
import os
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from google import genai
import os

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

#genai.configure(api_key=API_KEY)
client = genai.Client(api_key=API_KEY)

# -------- FIREBASE --------
import firebase_admin
from firebase_admin import credentials, firestore

try:
    firebase_admin.get_app()
except ValueError:
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

# -------- INSIGHTS --------
st.subheader("📊 Burnout Insights")

tab1, tab2 = st.tabs(["📈 Trend", "🥧 Breakdown"])

with tab1:
    if not history_df.empty:
        st.line_chart(history_df.set_index("date")["burnout"])
    else:
        st.write("No data yet. Save your first entry.")

with tab2:
    healthy_zone = max(0, 100 - burnout_score)
    stress_zone = min(burnout_score, 70)
    burnout_zone = max(0, burnout_score - 70)

    labels = ["Functioning", "Overloaded", "Burnout"]
    sizes = [healthy_zone, stress_zone, burnout_zone]

    filtered = [(l, s) for l, s in zip(labels, sizes) if s > 0]
    labels, sizes = zip(*filtered)

    fig, ax = plt.subplots(figsize=(1.75, 1.75))
    ax.pie(
        sizes,
        labels=labels,
        autopct="%1.0f%%",
        startangle=90,
        textprops={"fontsize": 6}
    )
    ax.axis("equal")
    st.pyplot(fig)

# -------- WHAT IF SIMULATION --------
st.subheader("🧪 What if I slept 1 hour more?")

if st.button("Simulate Better Sleep"):
    improved_sleep = min(8, sleep + 1)
    new_sleep_score = max(0, (8 - improved_sleep) / 8)

    improved_burnout = (
        0.35 * (new_sleep_score ** 1.5) +
        0.25 * (screen_score ** 1.3) +
        0.25 * task_score +
        0.15 * mood_score
    ) * 100

    st.success(f"Your burnout would drop to {int(improved_burnout)}")

# -------- USER CONTEXT INPUT --------
st.markdown("### 📝 Today’s workload / pressure context")

user_context = st.text_area(
    "Briefly describe today’s stress, deadlines, exams, or anything affecting you",
    placeholder="Example: 2 assignments due, poor sleep, continuous screen time, exam anxiety",
    height=120
)

# -------- AI EXPLANATION --------
st.subheader("🤖 AI Burnout Explanation & Suggestions")

# User-written context (keep this from earlier)
# user_context = st.text_area(...)

if st.button("Ask AI for Explanation"):
    with st.spinner("Analyzing burnout pattern..."):

        prompt = f"""
You are a mental health assistant helping a student understand burnout risk.

Burnout metrics:
- Sleep: {sleep} hours
- Screen time: {screen} hours
- Tasks today: {tasks}
- Mood: {mood}/5
- Burnout score: {burnout_score}/100
- Burnout status: {status}

User's self-described context:
\"\"\"{user_context}\"\"\"

Your tasks:
1. Explain clearly why the burnout level is {status}.
2. Identify the top 2–3 contributors.
3. Give 3 realistic, actionable suggestions the student can do today.
4. Keep the tone supportive, practical, and non-judgmental.
"""

        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt,
        )

        st.markdown("#### 🧠 AI Insights")
        st.write(response.text)
