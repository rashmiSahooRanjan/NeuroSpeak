# 🧠 NeuroSpeak – Brain Signal to Text Communication System

> AI-Powered EEG Analysis Platform | B.Tech Major Project

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15-orange.svg)](https://tensorflow.org)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green.svg)](https://mongodb.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📌 Abstract

NeuroSpeak is a Brain-Computer Interface (BCI) system that converts EEG (Electroencephalography) brain signals into readable text using Artificial Intelligence and Machine Learning. It processes raw EEG data from EDF files, applies signal preprocessing, extracts meaningful features, classifies brain activity patterns using a CNN-LSTM deep learning model, and maps predictions to text output — all through a modern web dashboard.

---

## 🎯 Objectives

- Read and parse EEG data from PhysioNet EDF files
- Preprocess EEG signals (bandpass filter, notch filter, ICA)
- Extract time-domain, frequency-domain, and Hjorth features
- Classify brain motor imagery states (Rest / Left Hand / Right Hand)
- Convert classified sequences into meaningful text/phrases
- Display results on a futuristic glassmorphism web dashboard
- Generate downloadable PDF clinical reports
- Store analysis history in MongoDB

---

## 🏗️ Project Structure

```
NeuroSpeak/
├── app.py                        # Main Flask application & API routes
├── requirements.txt              # Python dependencies
├── README.md                     # Project documentation
├── .env.example                  # Environment variables template
├── Procfile                      # Render/Railway deployment
│
├── preprocessing/
│   ├── __init__.py
│   ├── eeg_loader.py             # EDF/CSV file loading using MNE
│   ├── signal_filter.py          # Bandpass, notch, ICA preprocessing
│   └── feature_extractor.py      # PSD, Hjorth, time-domain features
│
├── ml/
│   ├── __init__.py
│   ├── train.py                  # Training pipeline (RF, SVM, CNN-LSTM)
│   ├── predict.py                # Inference module
│   └── model.pkl                 # Trained model (generated after training)
│
├── database/
│   ├── __init__.py
│   └── mongodb.py                # MongoDB schemas & CRUD operations
│
├── reports/
│   ├── __init__.py
│   └── report_generator.py       # PDF report generation (ReportLab)
│
├── static/
│   ├── css/style.css             # Glassmorphism dark theme
│   └── js/script.js              # Charts, upload, analysis, chat UI
│
├── templates/
│   └── index.html                # Main dashboard (Jinja2)
│
├── uploads/                      # Uploaded EEG files (auto-created)
├── dataset/                      # Place PhysioNet dataset here
└── docs/
    └── project_report.md         # Full academic project report
```

---

## 🔧 Technology Stack

| Layer             | Technology                                                  |
| ----------------- | ----------------------------------------------------------- |
| Frontend          | HTML5, CSS3 (Glassmorphism), JavaScript ES6, Chart.js, GSAP |
| Backend           | Python 3.10+, Flask 3.0, Flask-CORS                         |
| ML/AI             | Scikit-learn, TensorFlow 2.15 (CNN-LSTM), NumPy, Pandas     |
| Signal Processing | MNE-Python, SciPy                                           |
| Database          | MongoDB (PyMongo)                                           |
| Reports           | ReportLab                                                   |
| Deployment        | Render / Railway / Docker                                   |

---

## 📊 Dataset

**PhysioNet EEG Motor Movement/Imagery Dataset**

- 109 subjects (S001–S109)
- 14 runs per subject
- Runs used: R03, R04, R07, R08, R11, R12
- Sampling rate: 160 Hz | Channels: 64

**Labels:**

| Code | Meaning                  |
| ---- | ------------------------ |
| T0   | Rest state               |
| T1   | Left hand motor imagery  |
| T2   | Right hand motor imagery |

Download: https://physionet.org/content/eegmmidb/1.0.0/

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/NeuroSpeak.git
cd NeuroSpeak
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate       # Linux/Mac
venv\Scripts\activate          # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your MongoDB URI and secret key
```

### 5. Train the Model (Optional – uses synthetic data if no dataset)

```bash
# With synthetic data (no dataset needed):
python ml/train.py --synthetic

# With real PhysioNet dataset:
python ml/train.py --data_dir ./dataset --runs R03 R04 R07 R08
```

### 6. Run the Application

```bash
python app.py
```

Open: **http://localhost:5000**

---

## 🌐 API Endpoints

| Method | Endpoint                 | Description                      |
| ------ | ------------------------ | -------------------------------- |
| GET    | `/api/health`          | Server health check              |
| POST   | `/api/upload`          | Upload EDF/CSV file              |
| POST   | `/api/analyze`         | Run full EEG analysis pipeline   |
| POST   | `/api/predict`         | Quick inference on signal data   |
| POST   | `/api/report`          | Generate and download PDF report |
| GET    | `/api/history`         | Retrieve analysis history        |
| GET    | `/api/dashboard/stats` | Aggregate dashboard statistics   |

---

## 🧠 ML Pipeline

```
EDF File → MNE Load → Bandpass Filter (1-40Hz) → Notch (60Hz)
→ ICA Artifact Removal → Epoch Segmentation
→ Feature Extraction (PSD + Hjorth + Time-domain)
→ CNN-LSTM Classification → T0/T1/T2 Labels
→ Character/Phrase Mapping → Text Output
```

**Models Implemented:**

- ✅ Random Forest (200 estimators)
- ✅ SVM (RBF kernel, probability=True)
- ✅ CNN-LSTM (Conv1D → BatchNorm → MaxPool → LSTM → Dense)

---

## ☁️ Deployment

### Render

```bash
# Add to Render dashboard:
# Build Command: pip install -r requirements.txt
# Start Command: gunicorn app:app
# Set env vars: MONGO_URI, SECRET_KEY
```

### Railway

```bash
railway login
railway new
railway up
```

### Docker

```bash
docker build -t neurospeak .
docker run -p 5000:5000 -e MONGO_URI=your_uri neurospeak
```

---

## 📸 Features

- 🎨 Futuristic glassmorphism dark UI with cyberpunk aesthetics
- 📡 Drag & drop EDF/CSV upload
- 🌊 Real-time animated EEG waveform visualization
- ⚙️ Animated 6-step AI processing pipeline
- 💬 Text output with speech synthesis
- 📊 Analytics dashboard (confusion matrix, band power, accuracy charts)
- 📄 Downloadable PDF clinical reports
- 🕐 MongoDB analysis history with search
- 🤖 Built-in AI chat assistant
- 🌙 Dark/Light mode toggle

---

## 👥 Team

| Role              | Responsibility                        |
| ----------------- | ------------------------------------- |
| ML Engineer       | CNN-LSTM model, feature extraction    |
| Backend Dev       | Flask API, MongoDB integration        |
| Frontend Dev      | Dashboard UI, Chart.js visualizations |
| Signal Processing | MNE pipeline, ICA, filtering          |

---

## 📜 License

MIT License — Free for academic and research use.

---

## 🙏 Acknowledgments

- [PhysioNet](https://physionet.org) for the EEG dataset
- [MNE-Python](https://mne.tools) for EEG signal processing
- [TensorFlow](https://tensorflow.org) for deep learning
- [Anthropic Claude](https://anthropic.com) for AI assistance
