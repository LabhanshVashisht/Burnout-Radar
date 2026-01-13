import streamlit as st
import pandas as pd
import numpy as np
import openai
import datetime
import matplotlib.pyplot as plt

# -------- CONFIG --------
st.set_page_config(page_title="Burnout Radar", layout="centered")

st.title("🧠 Burnout Radar")
st.subheader("Predict burnout before it hits")

# -------- SIDEBAR INPUTS --------
st.sidebar.header("Daily Inputs")

sleep = st.sidebar.slider("Sleep (hours)", 0.0, 12.0, 7.0)
screen = st.sidebar.slider("Screen Time (hours)", 0.0, 16.0, 6.0)
tasks = st.sidebar.slider("Number of tasks today", 0, 10, 3)
mood = st.sidebar.slider("Mood (1 = terrible, 5 = great)", 1, 5, 3)

if st.sidebar.button("😈 Simulate Bad Day"):
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

# -------- SAVE HISTORY (ONCE PER DAY) --------

today = datetime.date.today()

new_entry = {
    "date": today,
    "burnout": burnout_score
}

try:
    history = pd.read_csv("burnout_history.csv")
    history["date"] = pd.to_datetime(history["date"]).dt.date
except:
    history = pd.DataFrame(columns=["date", "burnout"])

if "last_saved" not in st.session_state:
    st.session_state.last_saved = None

if st.session_state.last_saved != today:
    history = pd.concat([history, pd.DataFrame([new_entry])], ignore_index=True)
    history.to_csv("burnout_history.csv", index=False)
    st.session_state.last_saved = today

# -------- PIE CHART --------

st.subheader("🥧 Burnout Risk Breakdown")

healthy = max(0, 100 - burnout_score)
stress = min(burnout_score, 70)
burnout = max(0, burnout_score - 70)

labels = ["Functioning", "Overloaded", "Burnout"]
sizes = [healthy, stress, burnout]

filtered = [(l, s) for l, s in zip(labels, sizes) if s > 0]
labels, sizes = zip(*filtered)

fig, ax = plt.subplots()
ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
ax.axis("equal")
st.pyplot(fig)

# -------- LINE CHART --------

st.subheader("📈 Burnout Trend Over Time")

if not history.empty:
    history["date"] = pd.to_datetime(history["date"])
    st.line_chart(history.set_index("date")["burnout"])

    if len(history) >= 3:
        trend = history["burnout"].diff().mean()
        tomorrow = min(100, max(0, burnout_score + trend))
        st.metric("Tomorrow’s predicted burnout", int(tomorrow))
else:
    st.write("No data yet.")

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
