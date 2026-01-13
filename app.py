import streamlit as st
import pandas as pd
import numpy as np
import openai
import datetime
import matplotlib.pyplot as plt

import firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

import streamlit.components.v1 as components

params = st.query_params
username = params.get("user")

if not username:
    st.error("Not logged in. Please log in from the website.")
    st.stop()

username = username.lower()


# -------- CONFIG --------
st.set_page_config(page_title="Burnout Radar", layout="centered")

st.title("🧠 Burnout Radar")
st.subheader("Predict burnout before it hits")

# -------- INPUTS -----------

st.markdown("### Enter today’s data")

col1, col2 = st.columns(2)

with col1:
    sleep = st.slider("😴 Sleep (hours)", 0.0, 12.0, 7.0)
    screen = st.slider("📱 Screen Time (hours)", 0.0, 16.0, 6.0)

with col2:
    tasks = st.slider("📋 Tasks today", 0, 10, 3)
    mood = st.slider("🙂 Mood (1 = terrible, 5 = great)", 1, 5, 3)

if st.button("😈 Simulate Bad Day"):
    sleep = 4.0
    screen = 10.0
    tasks = 7
    mood = 2

# -------- BURNOUT LOGIC --------

sleep_score = max(0, (8 - sleep) / 8)
screen_score = min(screen / 10, 1)
task_score = min(tasks / 8, 1)
mood_score = (5 - mood) / 4

sleep_penalty = sleep_score ** 1.5
screen_penalty = screen_score ** 1.3

burnout_raw = (
    0.35 * sleep_penalty +
    0.25 * screen_penalty +
    0.25 * task_score +
    0.15 * mood_score
)

burnout_score = int(min(100, burnout_raw * 100))

# -------- STATUS --------

if burnout_score < 35:
    status = "Low"
    color = "🟢"
    message = "You're functioning well. Keep protecting your energy."
elif burnout_score < 70:
    status = "Moderate"
    color = "🟡"
    message = "You're overloaded. Small changes now will help."
else:
    status = "High"
    color = "🔴"
    message = "You're near burnout. Recovery is needed."

st.markdown(f"## Burnout Status: {color} **{status}**")
st.info(message)

# -------- FIREBASE SAVE --------
today = datetime.date.today().isoformat()

user_ref = db.collection("users").document(username).collection("burnout_logs")

# Save only once per day
if "last_saved" not in st.session_state:
    st.session_state.last_saved = None

if st.session_state.last_saved != today:
    user_ref.document(today).set({
        "date": today,
        "sleep": sleep,
        "screen": screen,
        "tasks": tasks,
        "mood": mood,
        "burnout": burnout_score,
        "timestamp": firestore.SERVER_TIMESTAMP
    })
    st.session_state.last_saved = today

# -------- LOAD HISTORY --------
docs = user_ref.order_by("timestamp").stream()

data = []
for d in docs:
    data.append(d.to_dict())

if data:
    history = pd.DataFrame(data)
    history["date"] = pd.to_datetime(history["date"])
else:
    history = pd.DataFrame(columns=["date", "burnout"])

# -------- TABS --------
st.subheader("📊 Burnout Insights")

tab1, tab2 = st.tabs(["📈 Trend", "🥧 Breakdown"])

# -------- TREND --------
with tab1:
    if not history.empty:
        st.line_chart(history.set_index("date")["burnout"])

        if len(history) >= 3:
            trend = history["burnout"].diff().mean()
            tomorrow = min(100, max(0, burnout_score + trend))
            st.metric("Tomorrow’s predicted burnout", int(tomorrow))
    else:
        st.write("No data yet.")

# -------- PIE --------
with tab2:
    healthy = max(0, 100 - burnout_score)
    stress = min(burnout_score, 70)
    burnout = max(0, burnout_score - 70)

    labels = ["Functioning", "Overloaded", "Burnout"]
    sizes = [healthy, stress, burnout]

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
        0.25 * screen_penalty +
        0.25 * task_score +
        0.15 * mood_score
    ) * 100

    st.success(f"Your burnout would drop to {int(improved_burnout)}")

# -------- AI EXPLANATION --------
st.subheader("Why is your burnout like this?")

if st.button("Get AI Explanation"):
    prompt = f"""
    A student has:
    Sleep: {sleep} hours
    Screen time: {screen} hours
    Tasks: {tasks}
    Mood: {mood}/5
    Burnout score: {burnout_score}/100

    Explain why burnout is high or low and give 3 actionable tips.
    """

    # --- OPENAI INTEGRATION ----
    