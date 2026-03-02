# 🩺 Medical Image Analysis System

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.x-green.svg)](https://flask.palletsprojects.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://react.dev/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-FF6F00.svg)](https://www.tensorflow.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-7.0-47A248.svg)](https://www.mongodb.com/)
[![JWT](https://img.shields.io/badge/Auth-JWT-black.svg)](https://jwt.io/)

A full-stack AI application for **medical image classification** with two production modules:

- 🧠 **Brain Tumor Analysis** (MRI)
- 🫁 **COVID-19 Analysis** (Chest X-ray)

The platform provides secure authentication, single and batch prediction, report generation, and disease-wise history/output management.

---

## 📌 Table of Contents

- [Project Overview](#-project-overview)
- [Core Features](#-core-features)
- [Disease Modules](#-disease-modules)
- [System Architecture](#-system-architecture)
- [Project Structure](#-project-structure)
- [Tech Stack](#-tech-stack)
- [API Reference](#-api-reference)
- [Report Generation](#-report-generation)
- [Authentication Flow](#-authentication-flow)
- [Installation & Setup](#-installation--setup)
- [Usage Flow](#-usage-flow)
- [Configuration](#-configuration)
- [Troubleshooting](#-troubleshooting)
- [Security Notes](#-security-notes)
- [Roadmap](#-roadmap)
- [Contributors](#-contributors)
- [License](#-license)
- [Medical Disclaimer](#-medical-disclaimer)

---

## 🔍 Project Overview

**Medical Image Analysis System** is a final-year project that combines AI/ML and web engineering to assist in preliminary disease screening from radiology images.

The application includes:

- Modern React frontend with module-based workflow
- Flask backend with blueprint-based route separation
- TensorFlow/Keras inference pipelines for both diseases
- MongoDB persistence for users and prediction data
- JWT-based authentication and protected APIs
- PDF reports for single and batch results

---

## ✨ Core Features

- 🔐 User registration, login, token verification, logout
- 📊 Dashboard with disease module selection
- 🧠 Brain Tumor MRI single + batch prediction
- 🫁 COVID-19 X-ray single + batch prediction
- 🧾 PDF report generation (single and batch)
- 🗂️ Disease-specific upload and output directories
- 🕒 Prediction history and analytics support
- ⚠️ Robust error handling for invalid requests/files

---

## 🧠🫁 Disease Modules

### 1) Brain Tumor Module

- Input: MRI image(s)
- Typical classes: Glioma, Meningioma, Pituitary, No Tumor
- Supports single and batch analysis
- Disease-specific reporting and history

### 2) COVID-19 Module

- Input: Chest X-ray image(s)
- Predicts COVID-related class output from trained model
- Supports single and batch analysis
- Disease-specific reporting and history

---

## 🏗️ System Architecture

### Frontend Layer

- React + Vite SPA
- Auth screens + protected module flow
- Dashboard + dedicated pages for both modules

### Backend Layer

- Flask app with modular blueprints
- Image preprocessing + model inference
- API layer for auth, prediction, reports

### Data Layer

- MongoDB collections for users and analysis data
- Stores prediction metadata, history, and batch summaries

### Output Layer

- Uploaded files by disease
- Generated PDF reports by disease

---

## 📁 Project Structure

```text
Medical_Image_Analysis_System/
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── config/
│   │   └── database.py
│   ├── models/
│   │   ├── brain_tumor_model.h5
│   │   └── covid_19_model.h5
│   ├── routes/
│   │   ├── auth_routes.py
│   │   ├── brain_tumor_routes.py
│   │   ├── covid_19_routes.py
│   │   └── report_routes.py
│   ├── utils/
│   │   ├── auth.py
│   │   └── pdf_generator.py
│   ├── uploads/
│   │   ├── brain_tumor/
│   │   └── covid_19/
│   └── output/
│       ├── brain_tumor/
│       └── covid_19/
├── frontend/
│   └── Medical_Image_Analysis_System/
│       ├── package.json
│       └── src/
│           ├── App.jsx
│           ├── main.jsx
│           └── components/
│               ├── Dashboard.jsx
│               ├── BrainTumorAnalysis.jsx
│               └── CovidAnalysis.jsx
└── notebooks/
```

---

## 🛠️ Tech Stack

### Frontend

- React
- Vite
- Axios
- Bootstrap / custom CSS
- React Router

### Backend

- Flask
- Flask-CORS
- TensorFlow / Keras
- Pillow, NumPy
- PyMongo
- PyJWT
- bcrypt

### Database

- MongoDB / MongoDB Atlas

---

## 🔌 API Reference

Base URL:

```text
http://localhost:5000
```

### Auth APIs

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/verify`
- `POST /api/auth/logout`

### Brain Tumor APIs

- `POST /api/brain_tumor/predict`
- `POST /api/brain_tumor/predict/batch`
- Additional analytics/history routes in `backend/routes/brain_tumor_routes.py`

### COVID-19 APIs

- `POST /api/covid_19/predict`
- `POST /api/covid_19/predict/batch`
- Additional analytics/history routes in `backend/routes/covid_19_routes.py`

### Report APIs

- Routes defined in `backend/routes/report_routes.py`
- Supports both single and batch reports for both modules

---

## 🧾 Report Generation

PDF reports are generated using backend utilities and stored disease-wise:

- `backend/output/brain_tumor`
- `backend/output/covid_19`

Report pipeline highlights:

- Model prediction summary
- Confidence score and metadata
- Disease-aware formatting/content
- Stable file naming and download flow

---

## 🔐 Authentication Flow

1. User registers account
2. User logs in and receives JWT token
3. Frontend stores token and sends it in `Authorization` header
4. Protected APIs validate token using middleware/decorator
5. User can logout and invalidate session flow at client side

Header format:

```text
Authorization: Bearer <token>
```

---

## 🚀 Installation & Setup

### Prerequisites

- Python 3.11+
- Node.js and npm
- MongoDB (local or Atlas)

### 1) Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` in `backend`:

```env
MONGO_URI=your_mongodb_connection_string
JWT_SECRET_KEY=your_secret_key
FLASK_ENV=development
FLASK_DEBUG=True
```

Run backend:

```bash
python app.py
```

### 2) Frontend

```bash
cd frontend/Medical_Image_Analysis_System
npm install
npm run dev
```

Frontend: `http://localhost:5173`
Backend: `http://localhost:5000`

---

## 🧭 Usage Flow

1. Register/Login
2. Open dashboard
3. Choose **Brain Tumor** or **COVID-19** module
4. Upload one or multiple images
5. Run prediction and review result
6. Generate/download report
7. Return to dashboard or logout

---

## ⚙️ Configuration

Typical runtime configuration:

- `MONGO_URI`
- `JWT_SECRET_KEY`
- Upload size/file restrictions in backend
- CORS origin for frontend URL
- Model paths for both disease modules

Ensure these model files exist:

- `backend/models/brain_tumor_model.h5`
- `backend/models/covid_19_model.h5`

---

## 🧯 Troubleshooting

- **Model not loading**: verify model files and paths
- **Mongo connection error**: verify `MONGO_URI`
- **401 Unauthorized**: token missing/expired
- **CORS issue**: allow frontend origin in Flask CORS config
- **Wrong endpoint used**: use module-prefixed routes (`/api/brain_tumor/*`, `/api/covid_19/*`)
- **Report issue**: verify request payload fields and generated output folder permissions

---

## 🔒 Security Notes

- Password hashing with bcrypt
- JWT for route protection
- File validation for upload endpoints
- Input validation and controlled error responses
- Keep secrets in `.env` only; never commit credentials

---

## 🗺️ Roadmap

- Improved analytics dashboards
- Better report templates and export options
- Role-based access (admin/doctor/user)
- Model explainability support
- Cloud deployment and CI/CD hardening

---

## 👥 Contributors

- **Abhay Tyagi** — Backend + Database + Deep Learning(Model Training).
- **Ayush Chauhan** — Frondend + Authentication.

Institution: ABES Engineering College (Final Year Project)

---

## 📜 License

This project is licensed under the MIT License.

---

## ⚠️ Medical Disclaimer

This software is intended for **educational and research purposes** only and is **not a substitute for professional clinical diagnosis**. Always consult qualified medical professionals for healthcare decisions.
