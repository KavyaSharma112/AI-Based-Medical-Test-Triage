# 🏥 AI Medical Test Triage System

An AI-powered web application that predicts risk levels for:

* 🫘 Kidney Disease
* ❤️ Heart Disease
* 🫀 Liver Disease
* 🩸 Diabetes

based on lab values entered manually or extracted from PDF reports.

---

## 🚀 Features

* 🔬 Predicts 4 diseases using ML models
* 📄 Upload lab reports (PDF) for auto data extraction
* ✏️ Manual form input (optional fields supported)
* 📊 Risk visualization with percentages
* ⚡ FastAPI backend + React frontend

---

## 🧠 Tech Stack

**Backend:**

* FastAPI
* Scikit-learn
* Pandas / NumPy

**Frontend:**

* React (Vite)
* Tailwind CSS

---

## ⚙️ How to Run the Project

### 1️⃣ Clone the repository

```bash
git clone https://github.com/KavyaSharma112/AI-Based-Medical-Test-Triage
cd AI-Based-Medical-Test-Triage
```

---

## 🔧 Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --reload
```

👉 Backend runs on:
`http://127.0.0.1:8000`

---

## 💻 Frontend Setup

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Run frontend
npm run dev
```

👉 Frontend runs on:
`http://localhost:5173`

---

## 🔗 Connecting Frontend to Backend

Make sure in `frontend/src/api.js`:

```js
const BASE_URL = "http://127.0.0.1:8000";
```

---

## 🧪 How to Use

### Option 1: Manual Input

* Fill any lab values (not all required)
* Click **Run All Predictions**

### Option 2: Upload PDF

* Upload a lab report
* Values auto-fill
* Click **Run All Predictions**

---

## 📊 Sample Output

* Risk Level: Low / Moderate / High
* Probability Score (%)
* Medical Recommendation
* Features used for prediction

---

## ⚠️ Disclaimer

This is **not a medical diagnosis system**.
It is for educational and research purposes only.

---

## ⭐ Future Improvements

* Better PDF parsing (OCR)
* Model explainability (SHAP)
* Deployment (Render / AWS)
