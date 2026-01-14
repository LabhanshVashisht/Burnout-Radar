# 🧠 Burnout Radar

**Burnout Radar** is a student-focused wellness and workload monitoring system designed to detect early burnout signals, explain their causes, and visualize academic pressure in a calm, non-judgmental interface.

This project is **not a motivation app**. It is an **early-warning and awareness system** that helps students understand pressure before it turns into burnout.

---

## 🎯 Project Objective

Burnout Radar helps college students:

* Visualize workload and pressure clearly
* Understand *why* burnout risk is increasing
* Take early, informed action before performance and mental health decline

The focus is **clarity over motivation** and **control over guilt**.

---

## 🚀 Core Features

### 🖥️ Student Dashboard (UI Module)

* Clean, card-based interface
* Profile overview with tasks and calendar context
* Google Calendar (read-only) integration
* Daily workload visibility
* Privacy-first design
* Responsive for desktop and mobile

---

### 📅 Calendar-Aware Workload Tracking

* Reads upcoming classes, exams, and deadlines
* Visualizes workload density
* Read-only access (no event modification)
* Calendar permissions can be revoked anytime

---

### 📊 Burnout Analysis Engine (Logic Module)

* Burnout Risk Score (0–100)
* Historical trend visualization
* Factor-wise burnout breakdown
* "What-if" simulations (e.g., effect of extra sleep)
* Manual save control (no automatic or background writes)

---

### 🤖 AI-Powered Burnout Explanation

* Powered by **Google Gemini**
* Explains:

  * Why the burnout level is high or low
  * Key contributing factors
  * Realistic, actionable suggestions
* Uses both behavioral data and user-written context

---

## 🔐 Demo Login Credentials

For demonstration and evaluation purposes:

* **Username:** Simi
* **Password:** 1234

---

## 🧩 Technology Stack

### Frontend / UI

* HTML
* CSS
* JavaScript

### Backend / Logic

* Python
* Streamlit application architecture

### Calendar Integration

* Google Calendar API (read-only)

### Storage

* Firebase Firestore (cloud persistence)
* Local per-user JSON files (fast demo updates)

### AI Engine

* Google Gemini (`gemini-2.5-flash`)

---

## 📁 Project Structure

```text
Burnout-Radar/
│
├── app.py                      # Streamlit entry point
├── style.css                   # Styling for HTML dashboard
├── script.js                   # UI helpers
├── index.html                  # Advanced HTML dashboard
│
├── users_data/                 # Per-user local data
│   ├── simi.json
│   ├── nauman.json
│   └── rohit.json
│
├── firebase_key.json            # Firebase service account key
└── README.md
```

---

## 🔐 User Data Handling & Privacy

* Each user has a **separate local JSON file**
* Data is written **only when the user clicks Save**
* No background auto-saving
* No cross-user overwrites
* Firebase is used for:

  * Cloud persistence
  * Analytics
  * Demo credibility

The system is designed to respect user control and consent.

---

## 🧠 Burnout Score Logic (High-Level)

Burnout is calculated using weighted, non-linear factors:

* Sleep debt
* Screen time overload
* Task and deadline pressure
* Mood decline

Extreme behavior (very low sleep, excessive screen time) is penalized more heavily than small fluctuations, making the score more realistic and sensitive.

---

## ▶️ How to Run the Project

### 1️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 2️⃣ Environment Configuration (.env)

Create a `.env` file in the project root with the following contents:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Make sure this file is **not committed to version control**.

---

### 3️⃣ Firebase Configuration (Service Account)

This project uses **Firebase Firestore** for cloud data persistence.

To enable Firebase access:

1. Create a Firebase project from the Firebase Console.
2. Generate a **Service Account key** from:
   Project Settings → Service Accounts → Generate new private key
3. Download the JSON file and place it in the project root as:

```text
firebase_key.json
```

---

### 4️⃣ Run the Streamlit App

```bash
streamlit run app.py
```

---

### 5️⃣ (Optional) Run HTML Dashboard

```bash
python -m http.server 8000
```

Open in browser:

```
http://localhost:8000/index.html?user=simi
```

---

---

## 📌 Future Improvements

* Proper authentication (OAuth / Firebase Auth)
* Multi-day history per user
* Burnout prediction (next-day / next-week)
* AI response caching
* Report export (PDF)
* Mobile app wrapper

---

## 👥 Team

* **Team Name:** Chicklers
* **Event:** Innovate 3.0
* **Domain:** AI · Mental Health · Student Technology

---

If something looks calm and simple here, it’s because a lot of chaos was removed on purpose.
