# ResQAlert 🚨
### AI-Driven Disaster Prediction, Warning, and Response System

> A Python-based intelligent early warning platform that predicts natural disasters using real-time weather data and machine learning, and delivers automated multi-channel alerts to communities and emergency responders.

---

## 📌 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [System Architecture](#system-architecture)
- [Modules](#modules)
- [Installation](#installation)
- [Usage](#usage)
- [Machine Learning Models](#machine-learning-models)
- [Alert System](#alert-system)

---

## Overview

Natural disasters such as **floods, droughts, and heatwaves** claim thousands of lives annually, with existing prediction systems often hampered by delayed data processing, static thresholds, and inefficient alert mechanisms.

**ResQAlert** addresses these shortcomings by integrating real-time weather APIs, advanced ML models, automated multi-channel alerts, and geospatial safe-zone recommendations into a unified, accessible platform. It is designed for both **community members** and **emergency response authorities**, offering prediction, preparedness, and post-disaster coordination — all in one system.

---

## Key Features

- 🌦️ **Real-Time Disaster Prediction** — Forecasts floods, droughts, and heatwaves using live and historical weather data from public APIs (OpenWeatherMap)
- 📊 **Interactive Dashboard** — Built with Streamlit/Flask; displays live forecasts, trend graphs, confidence scores, and alert history
- 📲 **Automated Multi-Channel Alerts** — Sends warnings via SMS, email, and voice notifications, with support for local languages (via gTTS & Googletrans)
- 🗺️ **Safe Zone Recommender** — Interactive geospatial map showing high-risk areas, safe zones, and evacuation routes (Folium / Google Maps API)
- 🤖 **Disaster Preparedness Chatbot** — NLP-powered assistant to guide users on safety measures, emergency protocols, and distress signal detection
- 🚑 **Post-Disaster Coordination Module** — Assists rescue teams and authorities in organizing response efforts
- 🔒 **Secure & Scalable Architecture** — Modular design with role-based access, encrypted storage, and support for future expansion to new disaster types and regions

---

## Tech Stack

| Category | Tools / Libraries |
|---|---|
| **Language** | Python 3.x |
| **Machine Learning** | scikit-learn, TensorFlow/Keras (Decision Tree, Logistic Regression, LSTM) |
| **Data Processing** | pandas, NumPy |
| **Visualization** | matplotlib, seaborn, Folium |
| **Web Framework** | Streamlit / Flask |
| **Weather API** | OpenWeatherMap API |
| **Alert & Messaging** | Twilio (SMS), SMTP (Email), gTTS (Voice) |
| **Language Support** | Googletrans |
| **Database** | SQLite / PostgreSQL / MySQL |
| **Version Control** | Git |
| **IDE** | VS Code / Jupyter Notebook |

---

## System Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     ResQAlert Platform                    │
├──────────────┬──────────────────────────┬────────────────┤
│  Data Layer  │     AI/ML Engine          │  Alert System  │
│              │                           │                │
│ OpenWeather  │  Decision Tree            │  SMS (Twilio)  │
│    API       │  Logistic Regression      │  Email (SMTP)  │
│              │  LSTM Networks            │  Voice (gTTS)  │
│  SQLite /    │                           │  Local Lang    │
│  PostgreSQL  │  Risk Classifier          │  (Googletrans) │
├──────────────┴──────────────────────────┴────────────────┤
│                    Dashboard (Streamlit/Flask)            │
│   Prediction Panel | Alert Log | Safe Zone Map | Chatbot │
└──────────────────────────────────────────────────────────┘
```

---

## Modules

### 1. Data Collection & Storage
- Fetches live weather parameters (temperature, humidity, rainfall, wind speed) via OpenWeatherMap API
- Stores historical and real-time data in a structured database (SQLite/PostgreSQL)
- Automated preprocessing pipeline for model-ready feature engineering

### 2. AI Prediction Engine
- Trains on historical weather datasets to classify disaster risk levels
- Models: **Decision Tree**, **Logistic Regression**, and **LSTM** (for time-series forecasting)
- Outputs confidence scores and risk classifications per region

### 3. Alert Management System
- Automatically triggers alerts when prediction thresholds are exceeded
- Delivers notifications via **SMS** (Twilio), **Email** (SMTP), and **Voice** (gTTS)
- Supports multi-language alerts for regional accessibility

### 4. Interactive Dashboard
- Central hub for monitoring real-time weather conditions and disaster probabilities
- Displays time-series trend graphs, prediction confidence, and alert history
- Region/time-based filtering for targeted monitoring

### 5. Safe Zone Recommender
- Geospatial map (Folium) highlighting high-risk zones, safe locations, and evacuation routes
- Dynamically updated based on live prediction output

### 6. Disaster Preparedness Chatbot
- NLP-based assistant for safety guidance and emergency protocol information
- Detects distress signals and escalates to emergency services
- Supports voice interaction and local language responses

### 7. Post-Disaster Coordination Module
- Interface for rescue teams and authorities to coordinate relief operations
- Tracks and logs active alerts, affected areas, and response status

---

## Installation

### Prerequisites
- Python 3.x
- pip
- Git
- Internet connection (for API access)

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/sanjayKumarR-404/ResQAlert.git
cd ResQAlert

# 2. Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your API keys:
#   OPENWEATHER_API_KEY=your_key
#   TWILIO_ACCOUNT_SID=your_sid
#   TWILIO_AUTH_TOKEN=your_token
#   SMTP_EMAIL=your_email
#   SMTP_PASSWORD=your_password

# 5. Initialize the database
python setup_db.py

# 6. Run the application
streamlit run app.py
# or
python app.py   # if using Flask
```

---

## Usage

1. **Launch the dashboard** — Opens in your browser at `http://localhost:8501` (Streamlit) or `http://localhost:5000` (Flask)
2. **Select a region** — Choose a geographical area to monitor
3. **View live predictions** — Disaster risk indicators and confidence scores update in real time
4. **Configure alerts** — Set up your preferred notification channel (SMS / email / voice) in User Preferences
5. **Explore the Safe Zone Map** — Visualize evacuation routes and safe areas
6. **Use the Chatbot** — Ask for preparedness tips or report a distress situation

---

## Machine Learning Models

| Model | Use Case | Accuracy Range |
|---|---|---|
| Decision Tree | Multi-hazard risk classification | 85–92% |
| Logistic Regression | Binary disaster probability | 85–92% |
| LSTM (Long Short-Term Memory) | Time-series flood forecasting | Optimized with VD algorithm |

> Models are trained on historical weather datasets and continuously validated against incoming real-time data.

---

## Alert System

ResQAlert supports three alert delivery channels:

| Channel | Technology | Description |
|---|---|---|
| SMS | Twilio API | Instant text alerts to registered mobile numbers |
| Email | SMTP | Detailed alert emails with weather summary |
| Voice | gTTS + Googletrans | Audio alerts in local/regional languages |

Alerts include: disaster type, severity level, affected region, timestamp, and recommended action.

---

## Hardware Requirements

| Component | Minimum |
|---|---|
| Processor | Intel Core i3 or higher |
| RAM | 4 GB |
| Storage | 1 GB free space |
| Network | Internet required (API access) |
| Optional | Microphone/Speaker for voice alerts |

---
