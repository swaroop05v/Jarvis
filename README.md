# JARVIS: Digital Wellness AI 🧠🌱

![JARVIS Dashboard Screenshot](./Screenshots/dashboard.png) *(Note: Please place relevant screenshots in the `Screenshots` folder)*

## 🌟 Overview
**JARVIS** is a comprehensive, sophisticated AI-powered Digital Wellness platform built to help users monitor, understand, and optimize their screen time and digital habits. It accurately tracks both PC and mobile application usage, uses machine learning to predict digital fatigue and stress levels, and features Gemini Vision AI to visually analyze smartphone Digital Wellbeing screenshots for personalized insights.

---

## 🚀 Key Features

*   **Real-time Activity Tracking**: Actively monitors the current application on PC and Phone (via ADB), logging usage every 5 seconds to compute total screen time, unbroken sessions, and productivity ratios.
*   **Machine Learning Stress Prediction**: Employs a customized Decision Tree Classifier to predict your digital fatigue (Low, Medium, or High) by analyzing your screen time, night usage, unbroken usage, app context switches, and breaks.
*   **Dynamic Wellness Scoring**: Generates a live Wellness Score (0–100) penalized by stress levels, excessive screen time (>4 hours), and late-night screen configurations, while rewarding focus and regular breaks.
*   **Gemini Vision AI (Phone Insights)**: Upload a smartphone 'Digital Wellbeing' screenshot and get instant, structured JSON insights, application categorization, and actionable recommendations powered by Google's `gemini-2.5-flash` model.
*   **Smart Alerts & ADB Notifications**: Receive timely, context-aware warnings on the dashboard (e.g., "Take a Break 🪑", "Hydration Check 💧") and ADB push notifications on your phone.
*   **Immersive, Animated UI**: A beautifully designed, glassmorphic React interface featuring robust heatmaps, historical data visualizations (Recharts), and fluid user interactions (Framer Motion).

---

## 🛠️ Technology Stack

| Components | Technologies Used |
| :--- | :--- |
| **Frontend UI** | React (Vite environment), TailwindCSS (v4), Framer Motion, Recharts, Lucide-React |
| **Backend API** | Python, Flask, Flask-CORS |
| **Data Processing** | Pandas, Pillow (PIL) |
| **Machine Learning** | Scikit-Learn (`DecisionTreeClassifier`), Joblib |
| **Generative AI** | Google Generative AI (`gemini-2.5-flash`) |

---

## 📊 How It Works: Formulas & ML Insight

JARVIS relies on a fine-tuned synthesis of mathematically derived features and intelligent ML classification to determine user well-being. Look at [`formulas_and_ml_analysis.md`](./formulas_and_ml_analysis.md) for a deep dive.

1.  **Continuous Usage & Breaks**: Finds the longest unbroken streak of activity. A break is defined as any gap > 5 minutes between log entries.
2.  **Productivity Ratio**: `1 - (distracting_time / total_time)`. Distracting apps include YouTube, Instagram, Netflix, Twitter, TikTok, etc.
3.  **Wellness Score**: Starts perfectly at 100. It faces aggressive penalties for `High` stress (-40), total screen time over 4 hours, and significant activity past 10 PM.
4.  **Decision Tree Model**: Using 6 distinct features (`screen_time`, `continuous_usage`, `night_usage`, `app_switches`, `breaks`, `productive_ratio`), the lightweight AI traverses decision boundaries to deliver microsecond inferences on the user's current cognitive load.

---

## ⚙️ Getting Started

### 1. Prerequisites
*   **Node.js** (v16 or higher recommended)
*   **Python** (3.9 to 3.12 recommended)
*   **ADB (Android Debug Bridge)** (Only if you wish to track your phone or send notifications)
*   **Gemini API Key** (for the Phone Insights screenshot analysis feature)

### 2. Backend Setup
1.  Navigate into the backend directory:
    ```bash
    cd Jarvis-backend-main/backend
    ```
2.  Install Python dependencies:
    ```bash
    pip install Flask flask-cors pandas scikit-learn joblib pillow google-generativeai python-dotenv
    ```
3.  Set up your Environment Variables:
    *   Create a `.env` file in the `backend/api` directory:
        ```env
        GEMINI_API_KEY=your_gemini_api_key_here
        ```
4.  Run the Flask API Server:
    ```bash
    python api/app.py
    ```
5.  *(Optional but Required for Tracking Data)* Start the trackers in separate terminals:
    ```bash
    python api/tracker.py         # Logs PC activity
    python api/phone_tracker.py   # Logs Phone activity
    ```

### 3. Frontend Setup
1.  Navigate into the frontend project root:
    ```bash
    cd Jarvis-main
    ```
2.  Install NPM dependencies:
    ```bash
    npm install
    ```
3.  Spin up the development server:
    ```bash
    npm run dev
    ```
4.  Open the local address provided by Vite (e.g., `http://localhost:5173/`) in your browser.

---

## 📂 Project Structure

```
JARVIS_FINAL_FINAL/
│
├── Jarvis-main/                 # Dynamic React Frontend Application
│   ├── src/                     # React components, pages, pages logic
│   ├── package.json
│   └── vite.config.ts
│
├── Jarvis-backend-main/         # Python Flask Backend Platform
│   └── backend/
│       ├── api/                 # API Routes (app.py) & Trackers
│       └── ml/                  # ML Training Pipeline & Extraction Logic
│
├── Screenshots/                 # Directory to store display snippets
└── formulas_and_ml_analysis.md  # Detailed documentation on scoring & ML analysis
```

---
*Built to help you reconnect with focus, health, and a balanced digital life.*
