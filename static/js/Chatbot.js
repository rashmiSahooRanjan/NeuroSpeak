/**
 * NeuroSpeak – Chatbot Module  (chatbot.js)
 * Self-contained: knowledge base + UI functions + smart matcher
 * Include this file AFTER script.js in index.html:
 *   <script src="{{ url_for('static', filename='js/chatbot.js') }}"></script>
 */

// ══════════════════════════════════════════════════════════════════
//  KNOWLEDGE BASE  — 26 topic entries
// ══════════════════════════════════════════════════════════════════
const NS_KB = [

  {
    keys: ['what is neurospeak','about neurospeak','about project','project overview',
           'what does this','explain project','tell me about','introduction'],
    answer: `🧠 NeuroSpeak – Project Overview

NeuroSpeak is a Brain-Computer Interface (BCI) system that converts EEG (brainwave) signals into readable text using Artificial Intelligence and Machine Learning.

What it does:
  → User uploads an EEG recording (.edf or .csv file)
  → AI preprocesses and cleans the raw brain signal
  → Machine learning model classifies brain activity patterns
  → Classified patterns are mapped to communication phrases
  → Output is shown as text, spoken aloud & saved as PDF report

Real-world purpose:
  Helps patients with ALS, locked-in syndrome, and paralysis
  communicate purely through thought — no physical movement needed.

This project is built as a B.Tech Major Project and is suitable
for hackathons, research demos, and placement portfolios.`
  },

  {
    keys: ['how does it work','how it works','how project works','working',
           'how neurospeak works','explain how','working principle','mechanism'],
    answer: `⚙️ How NeuroSpeak Works — 6 Step Pipeline:

Step 1 — Signal Acquisition
  EDF/CSV EEG file uploaded → MNE-Python loads it.
  Extracts: 64 channels, 160Hz sampling rate, duration, annotations.

Step 2 — Preprocessing
  Bandpass filter (1–40 Hz) → removes DC drift & muscle noise.
  Notch filter (60 Hz) → removes power line interference.

Step 3 — Noise Removal
  ICA (Independent Component Analysis) detects and removes
  eye blink and heartbeat artifacts automatically.

Step 4 — Feature Extraction
  1024 features per 2-second EEG epoch extracted:
  PSD band powers + Hjorth parameters + time-domain stats.

Step 5 — ML Classification
  CNN-LSTM model classifies each epoch as:
  T0 (Rest) / T1 (Left Hand) / T2 (Right Hand)

Step 6 — Text Generation
  Prediction sequences mapped to BCI communication phrases:
  e.g. "HELP ME", "CALL DOCTOR", "I NEED WATER"`
  },

  {
    keys: ['technology','tech stack','technologies used','which technology',
           'tools used','framework','language','programming','built with'],
    answer: `💻 NeuroSpeak Technology Stack:

Frontend:
  • HTML5 + CSS3 (Glassmorphism dark theme)
  • JavaScript ES6
  • Chart.js 4.4 — 5 chart types (line, bar, radar, doughnut)
  • GSAP 3.12 + ScrollTrigger — scroll animations

Backend:
  • Python 3.14 + Flask 3.1 (REST API server)
  • Flask-CORS (cross-origin requests)
  • Werkzeug (file handling)

Machine Learning:
  • TensorFlow 2.21 — CNN-LSTM deep learning model
  • Scikit-learn — Random Forest & SVM classifiers
  • NumPy 2.4.6 — numerical computing
  • Pandas 3.0 — data manipulation
  • Joblib — model serialization (.pkl files)

Signal Processing:
  • MNE-Python 1.12 — EEG loading, filtering, ICA
  • SciPy 1.17 — Welch PSD, signal mathematics

Database:
  • MongoDB Atlas (cloud) / Local MongoDB
  • PyMongo 4.17 driver

Reports:
  • ReportLab 4.5 — PDF generation

Authentication:
  • PyJWT 2.13 — JWT tokens
  • bcrypt 5.0 — password hashing`
  },

  {
    keys: ['machine learning','ml model','which model','deep learning',
           'neural network','classifier','classification','ai model'],
    answer: `🤖 Machine Learning Models in NeuroSpeak:

3 models are implemented:

① CNN-LSTM (Primary Model — 93.8% accuracy) ★
   Architecture:
   Conv1D(64, kernel=5, ReLU) → BatchNorm → MaxPool
   Conv1D(128, kernel=3, ReLU) → BatchNorm → MaxPool
   LSTM(64, return_sequences=True)
   LSTM(32) → Dropout(0.4)
   Dense(64, ReLU) → Dropout(0.3)
   Dense(3, Softmax)
   Why: CNN extracts local patterns, LSTM captures time sequences.

② Random Forest (88.4% accuracy)
   200 decision trees, max_depth=15
   Fast training, good interpretability

③ SVM — Support Vector Machine (89.7% accuracy)
   RBF kernel, C=10, gamma='scale'
   StandardScaler pipeline

Input to all models: 1024 feature vector per EEG epoch
Output: T0 (Rest) | T1 (Left Hand) | T2 (Right Hand)

Best performing model → auto-saved as model.pkl`
  },

  {
    keys: ['how ml trained','how model trained','training','how is the model trained',
           'train','training process','how to train','model training'],
    answer: `🏋️ How the ML Model is Trained:

Dataset: PhysioNet EEG Motor Movement/Imagery Dataset
  • 109 subjects (S001–S109)
  • Runs used: R03, R04, R07, R08, R11, R12
  • Labels: T0=Rest, T1=Left Hand, T2=Right Hand

Complete Training Process:
  1. Load EDF files using MNE-Python
  2. Bandpass filter (1–40Hz) + Notch (60Hz)
  3. ICA artifact removal
  4. Epoch into 2-second windows (160 samples each)
  5. Extract 1024 features per epoch
  6. Split: 80% train / 20% test (stratified)
  7. Train all 3 models (RF, SVM, CNN-LSTM)
  8. Evaluate accuracy, confusion matrix, F1-score
  9. Save best model as model.pkl

Training Commands:
  # No dataset needed (synthetic data):
  python ml/train.py --synthetic

  # With real PhysioNet data:
  python ml/train.py --data_dir ./dataset

CNN-LSTM: Adam optimizer, lr=0.001, 30 epochs, batch=32
Training time: ~20 min GPU / ~90 min CPU`
  },

  {
    keys: ['signal processing','preprocessing','filter','filtering',
           'how signal','noise removal','ica','bandpass','notch','mne'],
    answer: `📡 EEG Signal Processing Pipeline:

① Bandpass Filter (1–40 Hz)
   Tool: MNE raw.filter(l_freq=1, h_freq=40)
   Removes: DC drift (below 1Hz), muscle EMG noise (above 40Hz)
   Type: FIR (Finite Impulse Response) filter

② Notch Filter (60 Hz)
   Tool: MNE raw.notch_filter(freqs=60)
   Removes: Electrical power line interference
   (50Hz in India/Europe, 60Hz in USA)

③ Average Re-reference
   Tool: raw.set_eeg_reference('average')
   Effect: Subtracts mean of all 64 channels from each channel
   Reduces: Common-mode noise across electrodes

④ ICA — Independent Component Analysis
   Tool: mne.preprocessing.ICA
   Components: 15 ICA components extracted
   Auto-detects: Eye blink (EOG) components via frontal correlation
   Removes: Up to 2 artifact components automatically

⑤ Epoching
   Window: 2 seconds per epoch
   Overlap: 1 second sliding window
   Baseline: -200ms to 0ms (pre-stimulus normalization)

Library: MNE-Python — the gold standard for EEG processing`
  },

  {
    keys: ['feature','feature extraction','features used','what features',
           'psd','hjorth','band power','extraction','1024'],
    answer: `🔬 Feature Extraction — 1024 Features Per Epoch:

Per channel (64 channels × 16 features = 1024 total):

Time-Domain Features (7 per channel):
  • Mean            — average amplitude
  • Std Dev         — signal variability
  • Peak-to-Peak    — amplitude range (max - min)
  • Skewness        — distribution asymmetry
  • Kurtosis        — outlier sensitivity / peakedness
  • RMS             — root mean square (signal power)
  • IQR             — interquartile range (75th - 25th percentile)

Frequency-Domain / PSD (5 per channel):
  Using Welch's method (scipy.signal.welch):
  • Delta  (0.5–4 Hz)  — deep sleep patterns
  • Theta  (4–8 Hz)    — drowsiness / memory
  • Alpha  (8–13 Hz)   — relaxed alertness ← KEY for BCI
  • Beta   (13–30 Hz)  — active thinking ← KEY for BCI
  • Gamma  (30–45 Hz)  — cognitive processing

Hjorth Parameters (3 per channel):
  • Activity    = var(signal) — signal power
  • Mobility    = sqrt(var(dx)/var(x)) — mean frequency
  • Complexity  = mobility(dx)/mobility(x) — frequency changes

Zero-Crossing Rate (1 per channel):
  How often signal crosses zero → frequency content indicator`
  },

  {
    keys: ['eeg','what is eeg','electroencephalography','brain signal',
           'brain wave','what are brain waves','electrode'],
    answer: `🧠 EEG — Electroencephalography:

EEG measures tiny electrical voltages (microvolts) produced by
millions of neurons firing in the brain, detected by electrodes
placed on the scalp using conductive gel.

NeuroSpeak EEG Specifications:
  • Channels: 64 electrodes (10-20 international system)
  • Sampling Rate: 160 Hz (160 measurements per second)
  • Amplitude: 10–100 μV (millionths of a volt)
  • Format: EDF (European Data Format) files

EEG Frequency Bands:
  🔵 Delta (0.5–4 Hz)  — deep sleep, unconscious
  🟣 Theta (4–8 Hz)    — drowsy, meditative
  🟢 Alpha (8–13 Hz)   — relaxed, eyes closed
  🟡 Beta  (13–30 Hz)  — alert, focused, active
  🔴 Gamma (30+ Hz)    — complex cognitive tasks

Motor Imagery EEG:
  When you IMAGINE moving your hand (without actually moving),
  the brain generates Event-Related Desynchronization (ERD) —
  a decrease in alpha/beta power over the motor cortex.
  This ERD pattern is what NeuroSpeak detects and classifies.`
  },

  {
    keys: ['dataset','data','physionet','which dataset','training data',
           'edf file','subjects','data used','109 subjects'],
    answer: `📊 Dataset — PhysioNet EEG Motor Imagery:

Name: EEG Motor Movement/Imagery Dataset
URL: https://physionet.org/content/eegmmidb/1.0.0/
License: Free for research use

Specifications:
  • 109 subjects (S001 to S109)
  • 14 runs per subject (R01 to R14)
  • File format: .edf (European Data Format)
  • Sampling rate: 160 Hz
  • Channels: 64 EEG electrodes
  • Duration: ~2 minutes per run

Runs Used by NeuroSpeak:
  R03, R04 — Left/Right hand imagery task
  R07, R08 — Left/Right hand imagery task (repeat)
  R11, R12 — Left/Right hand + feet imagery

EDF Annotation Labels:
  T0 = Rest (baseline, no task)
  T1 = Left hand motor imagery
  T2 = Right hand motor imagery

Each subject contributes ~300–400 labeled 2-second epochs.
Total dataset: ~40,000 epochs across all 109 subjects.`
  },

  {
    keys: ['t0','t1','t2','label','labels','classes','rest',
           'left hand','right hand','motor imagery','what is t0',
           'what is t1','what is t2','classification label'],
    answer: `🏷️ EEG Classification Labels — T0, T1, T2:

T0 — Rest State
  Subject sits quietly. No task given.
  Brain shows: High alpha power, synchronized oscillations.
  EEG pattern: Regular, calm waves over entire scalp.

T1 — Left Hand Motor Imagery
  Subject IMAGINES moving their left hand (no real movement).
  Brain shows: ERD (alpha/beta decrease) over RIGHT motor cortex.
  Key electrodes: C4, CP4 (contralateral to left hand).

T2 — Right Hand Motor Imagery
  Subject IMAGINES moving their right hand.
  Brain shows: ERD over LEFT motor cortex.
  Key electrodes: C3, CP3 (contralateral to right hand).

Why motor imagery works:
  The brain activates the same motor planning areas for both
  real and imagined movement. The difference is that imagined
  movement doesn't send signals to muscles.
  EEG picks up this motor planning activity.

Text Generation Mapping:
  Sequences of T0/T1/T2 → BCI communication phrases:
  e.g. T1,T1,T0,T2,T2,T1 → "HELP ME"
  e.g. T2,T0,T2,T1,T2    → "CALL DOCTOR"`
  },

  {
    keys: ['accuracy','performance','how accurate','model performance','result',
           'how good','precision','recall','f1','benchmark'],
    answer: `📈 NeuroSpeak Model Performance Results:

Model Comparison Table:
  ┌──────────────────┬──────────┬───────────┬────────┐
  │ Model            │ Accuracy │ Precision │  F1    │
  ├──────────────────┼──────────┼───────────┼────────┤
  │ Random Forest    │  88.4%   │  87.9%    │ 87.9%  │
  │ SVM (RBF)        │  89.7%   │  89.4%    │ 89.4%  │
  │ CNN-LSTM ★ Best  │  93.8%   │  93.5%    │ 93.5%  │
  └──────────────────┴──────────┴───────────┴────────┘

Inference Speed: ~220ms per analysis window
Confidence Range: 78–99% (depends on signal quality)

Per-Class Accuracy (CNN-LSTM):
  Rest (T0):       94–96%  ← easiest to detect
  Left Hand (T1):  89–93%
  Right Hand (T2): 85–92%

Factors affecting accuracy:
  ✅ Good electrode contact (gel impedance < 5kΩ)
  ✅ Subject rested and focused
  ✅ Low electromagnetic interference environment
  ❌ Poor gel → high noise → lower accuracy
  ❌ Subject fatigue → alpha increases → harder to classify`
  },

  {
    keys: ['frequency','band','alpha','beta','theta','delta','gamma',
           'brain wave','frequency band','wave type','eeg band'],
    answer: `🌊 EEG Frequency Bands Explained:

🔵 Delta (0.5–4 Hz)
   State: Deep sleep, anesthesia, brain injury
   BCI note: High delta during EEG = subject drowsy/disconnected electrode

🟣 Theta (4–8 Hz)
   State: Drowsiness, meditation, memory formation, creativity
   BCI note: Increases during mental fatigue — monitor for session quality

🟢 Alpha (8–13 Hz)  ← MOST IMPORTANT FOR BCI
   State: Relaxed alertness, eyes closed
   Motor Imagery: DECREASES (ERD) when motor imagery is performed
   This decrease is the primary signal NeuroSpeak detects for T1/T2

🟡 Beta (13–30 Hz)  ← IMPORTANT FOR BCI
   State: Active thinking, alert, focused, motor control
   Motor Imagery: Also shows ERD during motor imagery
   Beta Rebound: Increases AFTER movement (ERS — Event-Related Synchronization)

🔴 Gamma (30–45 Hz)
   State: High cognitive load, attention, neural binding
   BCI note: Often contaminated by muscle (EMG) artifact — least reliable

NeuroSpeak monitors all 5 bands and visualizes them
in the EEG Band Power radar chart after each analysis.`
  },

  {
    keys: ['api','flask','backend','endpoint','rest api','routes','server',
           'flask routes','http','url endpoint'],
    answer: `🌐 Flask REST API — All Endpoints:

GET  /                    → Main dashboard (index.html)
GET  /admin               → Admin control panel
GET  /login               → Login / Register page

GET  /api/health          → Server status + model info + DB check
POST /api/upload          → Upload EDF/CSV file (multipart/form-data)
POST /api/analyze         → Run full 6-step pipeline on uploaded file
POST /api/predict         → Quick inference on signal data
POST /api/report          → Generate & download PDF clinical report
GET  /api/history         → Get analysis history (MongoDB)
GET  /api/dashboard/stats → Aggregate stats for dashboard
POST /api/auth/register   → Create new user account
POST /api/auth/login      → Login → returns JWT token

Example cURL calls:
  curl http://localhost:5000/api/health
  curl -X POST -F "file=@S001R03.edf" http://localhost:5000/api/upload
  curl http://localhost:5000/api/history?limit=5

All API responses: JSON format
Authentication: Bearer JWT token in Authorization header`
  },

  {
    keys: ['mongodb','database','db','atlas','storage','data stored',
           'mongo','collection','schema'],
    answer: `🗄️ MongoDB Database Structure:

NeuroSpeak uses MongoDB to persist all analysis data.

Collections:
  ① analyses — Every EEG analysis result
    Fields: analysis_id, subject_id, generated_text,
            confidence, accuracy, signal_quality, channels,
            duration, predictions[], freq_bands{},
            confusion_matrix[][], alpha/beta/theta/delta power,
            attention_level, focus_score, timestamp, created_at

  ② reports — PDF report metadata
    Fields: analysis_id, subject_id, report_path, generated_at

  ③ users — User accounts
    Fields: email, password (bcrypt hash), role, created_at

MongoDB Atlas Setup (Free):
  1. cloud.mongodb.com → Create free M0 cluster
  2. Network Access → Add IP: 0.0.0.0/0
  3. Database Access → Create user with readWrite role
  4. Connect → copy URI → paste in .env as MONGO_URI

Local MongoDB (offline):
  Download: mongodb.com/try/download/community
  .env: MONGO_URI=mongodb://localhost:27017/neurospeak

Auto fallback: if MongoDB unavailable → in-memory storage`
  },

  {
    keys: ['report','pdf','download report','generate report',
           'clinical report','what is in report','reportlab'],
    answer: `📄 PDF Report Generation:

Click "Download Report" after running analysis.
Generated using ReportLab Python library — A4 format.

Report Contents:
  ① Header — NeuroSpeak logo, report ID, date/time
  ② Meta Table — Subject ID, model version, status
  ③ Signal Metrics
     • Signal Quality (μV) — electrode contact quality
     • Number of channels — 64 EEG channels used
     • Recording duration — length of EEG session
     • Attention Level (%) — beta/alpha power ratio
     • Focus Score (%) — alpha band stability
  ④ Frequency Band Analysis table
     • Delta, Theta, Alpha, Beta, Gamma power values
     • Band function explanations
  ⑤ AI Prediction Results
     • Generated text phrase (e.g. "HELP ME")
     • Confidence score (%)
     • Model accuracy (%)
     • Inference latency (ms)
  ⑥ Clinical Recommendations (6 evidence-based points)
  ⑦ Doctor Notes — placeholder for physician signature

File: NeuroSpeak_Report_[8-char-ID].pdf
Disclaimer: Research purposes only — not a medical diagnosis`
  },

  {
    keys: ['how to use','how use','steps','use the app','use neurospeak',
           'get started','start using','upload eeg','upload file'],
    answer: `🚀 How to Use NeuroSpeak — Step by Step:

① Upload EEG File
   Go to "Upload EEG" section (sidebar or "Start Analysis" button)
   Drag & drop or click "Browse File"
   Accepts: .edf (PhysioNet format) or .csv EEG recordings
   Max size: 50MB
   File info shown: name, subject ID, size, estimated duration

② Run Analysis
   Click the green "Run Analysis" button
   Watch the 6-step AI pipeline animate in real time
   Takes 2–10 seconds depending on file size

③ View Results (Prediction section)
   Generated Text → decoded brain signal phrase
   Confidence Score → how certain the model is (0–100%)
   Model Accuracy → classification performance (%)
   Latency → inference time in milliseconds
   Prediction Chips → T0/T1/T2 sequence

④ Actions Available
   📋 Copy Text → copies output to clipboard
   🔊 Speak → browser speech synthesis reads text aloud
   📄 Download Report → generates clinical PDF

⑤ Analytics Section
   Confusion matrix, band power radar, accuracy chart

⑥ History
   All analyses saved in MongoDB, searchable by Subject ID`
  },

  {
    keys: ['bci','brain computer interface','brain-computer','interface',
           'application','use case','who uses','patients','als','paralysis'],
    answer: `🧠 Brain-Computer Interface (BCI):

Definition:
  A BCI is a direct communication pathway between the brain
  and a computer — bypassing the body's motor output system.

Why BCIs matter:
  • ~1.5 million ALS patients worldwide lose speech & movement
  • Locked-in syndrome = complete paralysis, intact mind
  • Spinal cord injuries may preserve full brain function
  → BCI lets them communicate purely through thought

NeuroSpeak BCI Type: Motor Imagery BCI
  ✅ Non-invasive (scalp electrodes — no surgery)
  ✅ Passive (user imagines movement, no external stimulation)
  ✅ 3-class output: Rest, Left Hand, Right Hand

Real-World Applications:
  🏥 Medical: ALS/stroke/paralysis communication devices
  🦾 Prosthetics: Thought-controlled artificial limbs
  🎮 Gaming: Hands-free game controllers
  🚗 Automotive: Driver drowsiness & attention monitoring
  🎓 Education: Student attention & engagement tracking
  🧘 Wellness: Neurofeedback, meditation apps

NeuroSpeak focuses on assistive communication —
mapping brain patterns to medical phrases for patients
who cannot speak or move any part of their body.`
  },

  {
    keys: ['deploy','deployment','render','railway','docker','host',
           'cloud','production','how to deploy','publish','go live'],
    answer: `☁️ Deployment Options:

① Render (Recommended — Free tier available)
   1. Push code to GitHub
   2. render.com → New Web Service → Connect repo
   3. Build: pip install -r requirements.txt
   4. Start: gunicorn app:app
   5. Add env vars: MONGO_URI, SECRET_KEY
   6. Live at: https://yourapp.onrender.com

② Railway
   npm install -g @railway/cli
   railway login
   railway new
   railway up
   Add env vars in Railway dashboard

③ Docker (any server)
   docker build -t neurospeak .
   docker run -p 5000:5000 \
     -e MONGO_URI="mongodb+srv://..." \
     -e SECRET_KEY="your-key" \
     neurospeak

④ Local Development
   python app.py → http://localhost:5000

⑤ Docker Compose (app + MongoDB together)
   docker-compose up -d

Required files:
  Procfile  → web: gunicorn app:app
  Dockerfile → included in project

Important: Use MongoDB Atlas (not localhost) for cloud deploys!`
  },

  {
    keys: ['confusion matrix','confusion','what is confusion matrix',
           'how to read confusion matrix','matrix result'],
    answer: `📊 Confusion Matrix — How to Read It:

A confusion matrix shows how well the model classifies each class.

NeuroSpeak Matrix (3×3 for T0, T1, T2):

              Predicted→  Rest   L-Hand  R-Hand
  Actual Rest    →        [96]    [2]     [5]
  Actual L-Hand  →        [8]    [93]     [2]
  Actual R-Hand  →        [4]     [1]    [85]

Diagonal cells (green) = CORRECT predictions
Off-diagonal cells (red tint) = ERRORS/misclassifications

How to interpret:
  96 → model correctly classified Rest 96 times
   8 → 8 Rest epochs were wrongly called Left Hand
  93 → Left Hand correctly identified 93 times

Overall accuracy = sum of diagonal / total
  = (96 + 93 + 85) / (96+2+5+8+93+2+4+1+85)
  = 274 / 296 = 92.6%

Common confusions in EEG-BCI:
  Left Hand vs Right Hand → can look similar in some subjects
  Rest vs Left Hand → if subject accidentally imagines movement`
  },

  {
    keys: ['confidence','confidence score','what is confidence',
           'confidence meaning','score interpretation'],
    answer: `🎯 Confidence Score Explained:

The confidence score (0–100%) = how certain the model is
about its prediction for each EEG epoch.

How it's calculated:
  CNN-LSTM Softmax output gives probabilities for each class.
  Example: [0.04, 0.92, 0.04] → T1 predicted, 92% confidence.
  Final score = average confidence across ALL epochs in the file.

Interpretation Guide:
  90–100% → Very high — excellent signal quality, reliable result
  80–90%  → Good — normal for EEG BCI systems
  70–80%  → Moderate — signal may be slightly noisy
  < 70%   → Low — check electrode placement and gel contact

What affects confidence:
  ✅ Low electrode impedance (< 5kΩ) → higher confidence
  ✅ Subject relaxed and focused → cleaner signal
  ✅ Quiet room, no electrical devices nearby
  ❌ Dry electrodes → high noise → low confidence
  ❌ Subject moving → muscle artifact → confused model`
  },

  {
    keys: ['attention','focus','attention level','focus score',
           'what is attention level','cognitive state'],
    answer: `🎯 Attention Level & Focus Score:

These are real-time cognitive state indicators computed
from the EEG frequency band powers.

Attention Level (0–100%):
  Formula: normalized (Beta power / Alpha power) ratio
  High beta + low alpha = high attention/alertness
  Example: Beta=0.45, Alpha=0.20 → Attention ~85%
  Use: Driver alertness, student engagement monitoring

Focus Score (0–100%):
  Derived from alpha band temporal stability
  Stable alpha rhythm = good focused state
  Drops when: distracted, drowsy, or task-switching
  Use: Neurofeedback training, meditation quality

Brain States by these metrics:
  High Attention + High Focus → Deep concentration
  High Attention + Low Focus → Stressed / scattered
  Low Attention + High Focus → Relaxed mindfulness
  Low Attention + Low Focus → Drowsy / disengaged

Displayed in: EEG Visualization section as metric cards
Updated after each analysis run.`
  },

  {
    keys: ['cnn lstm','cnn-lstm','deep learning model','neural architecture',
           'conv1d','lstm layer','model architecture'],
    answer: `🧬 CNN-LSTM Architecture Details:

Input Shape: (batch_size, 1024_features, 1)

Layer Stack:
┌─────────────────────────────────────────────┐
│ Conv1D(64 filters, kernel=5, ReLU)          │ ← extract local patterns
│ BatchNormalization                           │ ← stabilize training
│ MaxPooling1D(pool_size=2)                   │ ← reduce dimensions
├─────────────────────────────────────────────┤
│ Conv1D(128 filters, kernel=3, ReLU)         │ ← higher-level features
│ BatchNormalization                           │
│ MaxPooling1D(pool_size=2)                   │
├─────────────────────────────────────────────┤
│ LSTM(64 units, return_sequences=True)       │ ← temporal patterns
│ LSTM(32 units)                              │ ← sequence summary
│ Dropout(0.4)                                │ ← prevent overfitting
├─────────────────────────────────────────────┤
│ Dense(64, ReLU)                             │ ← learned features
│ Dropout(0.3)                                │
│ Dense(3, Softmax)                           │ ← [T0, T1, T2] probs
└─────────────────────────────────────────────┘

Training Config:
  Optimizer: Adam (learning_rate=0.001)
  Loss: Categorical Crossentropy
  Epochs: 30 | Batch size: 32
  Validation split: 15%

Why CNN + LSTM?
  CNN: Extracts spatial feature patterns (like image recognition)
  LSTM: Models temporal dependencies between EEG time windows
  Result: Best of both → 93.8% classification accuracy`
  },

  {
    keys: ['random forest','svm','support vector','rf model',
           'random forest model','svm model','ensemble'],
    answer: `🌲 Random Forest & SVM Details:

Random Forest:
  Type: Ensemble of decision trees (bagging method)
  Config: 200 trees, max_depth=15, min_samples_split=5
  Training: ~3 minutes on full dataset
  Accuracy: 88.4%

  How it works:
  → Each tree trained on random subset of data + features
  → Final prediction = majority vote of all 200 trees
  → Feature importance scores available for interpretability

  Strengths:
  ✅ Handles high-dimensional data (1024 features) well
  ✅ No feature scaling needed
  ✅ Fast inference (<10ms)
  ✅ Interpretable feature importances

SVM (Support Vector Machine):
  Type: Kernel-based classifier
  Config: RBF kernel, C=10, gamma='scale', probability=True
  Preprocessing: StandardScaler (zero mean, unit variance)
  Training: ~8 minutes
  Accuracy: 89.7%

  How it works:
  → Finds optimal hyperplane maximizing class margin
  → RBF kernel maps to infinite-dimensional space
  → Probability via Platt scaling

  Strengths:
  ✅ Strong with high-dimensional feature spaces
  ✅ Robust to overfitting in medium datasets
  ✅ Good generalization`
  },

  {
    keys: ['ica','independent component analysis','artifact',
           'eye blink','artifact removal','noise','eog'],
    answer: `🧹 ICA — Independent Component Analysis:

ICA is the method NeuroSpeak uses to remove biological artifacts
(eye blinks, heartbeat) from EEG signals.

How ICA works:
  1. Assumes EEG = mix of independent sources (brain + artifacts)
  2. Mathematically separates the signal into N independent components
  3. Each component = one "source" (brain region or artifact)
  4. Artifacts have characteristic topographies:
     • Eye blinks → large signal at frontal electrodes (Fp1, Fp2)
     • Heartbeat → rhythmic pattern across all channels
  5. Identified artifact components are set to zero
  6. Signal is reconstructed without the artifacts

NeuroSpeak ICA config:
  Components: 15 (or n_channels - 1 if fewer channels)
  Method: FastICA (default in MNE-Python)
  Max iterations: 200
  Auto-detects: EOG (eye) components via correlation
  Removes: Up to 2 worst artifact components

Before ICA: Signal contaminated with large eye blink spikes
After ICA:  Clean neural signal — 10–50x better quality

Library: mne.preprocessing.ICA`
  },

  {
    keys: ['hjorth','hjorth parameters','activity','mobility','complexity'],
    answer: `📐 Hjorth Parameters Explained:

Hjorth (1970) proposed 3 time-domain features that efficiently
describe the statistical properties of EEG signals.

① Activity = var(x)
   Signal variance = raw power of the signal
   High activity → more signal amplitude variability
   Low activity → flat, quiet signal

② Mobility = sqrt( var(dx) / var(x) )
   dx = first derivative of signal (rate of change)
   Represents the mean frequency of the signal
   High mobility → signal changes rapidly (high frequency)
   Low mobility → slow, gradual signal changes

③ Complexity = mobility(dx) / mobility(x)
   dx = first derivative, ddx = second derivative
   Represents how much the signal deviates from a pure sine wave
   High complexity → irregular, complex waveform
   Low complexity → regular oscillation (like pure alpha wave)

Why use Hjorth?
  ✅ Very computationally efficient (no FFT needed)
  ✅ Discriminative for motor imagery EEG states
  ✅ Complement to PSD features
  ✅ Proven in BCI literature since 1970

Used in: Each of 64 channels = 3 × 64 = 192 Hjorth features total`
  },

  {
    keys: ['hello','hi','hey','good morning','good evening',
           'namaste','hii','helo','hai','greet'],
    answer: `👋 Hello! Welcome to NeuroSpeak Assistant!

I have complete knowledge about this project. Ask me anything!

📌 Popular questions:
  • "How does NeuroSpeak work?"
  • "What technology is used?"
  • "How is the ML model trained?"
  • "What is EEG?"
  • "Explain signal processing steps"
  • "What is T0, T1, T2?"
  • "How accurate is the model?"
  • "What is ICA?"
  • "Explain CNN-LSTM architecture"
  • "What is the PhysioNet dataset?"
  • "How to use this application?"
  • "What is a BCI?"

Or click any suggestion chip below to get started! 💡`
  },

  {
    keys: ['help','what can you','what do you know','topics',
           'questions','what can i ask','menu','options'],
    answer: `🤖 NeuroSpeak Assistant — Full Topic List:

I can answer detailed questions about all of these:

🧠 Project
  "What is NeuroSpeak?" | "Project overview"

⚙️ Working
  "How does NeuroSpeak work?" | "6-step pipeline"

💻 Technology
  "What technology is used?" | "Tech stack"

🤖 ML Models
  "Which ML model?" | "CNN-LSTM" | "Random Forest" | "SVM"

🏋️ Training
  "How is the model trained?" | "Training process"

📡 Signal Processing
  "Preprocessing steps" | "ICA" | "Bandpass filter"

🔬 Features
  "What features are extracted?" | "PSD" | "Hjorth"

🧠 EEG
  "What is EEG?" | "Brain waves" | "Electrodes"

📊 Dataset
  "PhysioNet dataset" | "How many subjects?"

🏷️ Labels
  "What is T0, T1, T2?" | "Motor imagery"

📈 Accuracy
  "Model performance" | "Confusion matrix"

🌊 Frequency Bands
  "Alpha beta theta delta gamma explained"

🌐 API
  "Flask endpoints" | "REST API routes"

🗄️ Database
  "MongoDB setup" | "What data is stored?"

📄 Reports
  "PDF report contents" | "Download report"

☁️ Deployment
  "How to deploy?" | "Render/Railway/Docker"

🎯 Scores
  "Confidence score" | "Attention level" | "Focus score"`
  },

];

// ══════════════════════════════════════════════════════════════════
//  SMART KEYWORD MATCHER
// ══════════════════════════════════════════════════════════════════
function ns_getChatReply(question) {
  const q = question.toLowerCase().trim();
  let bestScore  = 0;
  let bestAnswer = null;

  for (const entry of NS_KB) {
    let score = 0;
    for (const kw of entry.keys) {
      if (q === kw) {
        score += 20;                        // exact match
      } else if (q.includes(kw)) {
        score += kw.split(' ').length * 3;  // phrase match — longer = better
      } else {
        // individual word match
        for (const word of kw.split(' ')) {
          if (word.length > 3 && q.includes(word)) score += 1;
        }
      }
    }
    if (score > bestScore) {
      bestScore  = score;
      bestAnswer = entry.answer;
    }
  }

  if (bestScore > 0 && bestAnswer) return bestAnswer;

  return `🤔 I couldn't find a specific answer for that.

Try asking:
  • "How does NeuroSpeak work?"
  • "What technology is used?"
  • "How is the ML model trained?"
  • "What is T0 T1 T2?"
  • "Explain signal processing"
  • "What is EEG?"
  • "How accurate is the model?"

Or type "help" to see all topics I can answer.`;
}


// ══════════════════════════════════════════════════════════════════
//  CHAT UI FUNCTIONS
// ══════════════════════════════════════════════════════════════════

function toggleChat() {
  const panel = document.getElementById('chatPanel');
  if (!panel) return;
  panel.classList.toggle('open');
  if (panel.classList.contains('open')) {
    setTimeout(() => {
      const inp = document.getElementById('chatInput');
      if (inp) inp.focus();
    }, 300);
  }
}

function sendChat() {
  const input = document.getElementById('chatInput');
  if (!input) return;
  const msg = input.value.trim();
  if (!msg) return;

  ns_addMsg(msg, 'user');
  input.value = '';
  input.focus();

  const typing = ns_showTyping();
  setTimeout(() => {
    typing.remove();
    ns_addMsg(ns_getChatReply(msg), 'bot');
  }, 700);
}

function askSuggestion(text) {
  const input = document.getElementById('chatInput');
  if (!input) return;
  input.value = text;
  sendChat();
}

function ns_addMsg(text, role) {
  const box = document.getElementById('chatMessages');
  if (!box) return null;
  const div = document.createElement('div');
  div.className = 'chat-msg ' + role;
  div.style.whiteSpace = 'pre-wrap';
  div.style.wordBreak  = 'break-word';
  div.textContent = text;
  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
  return div;
}

function ns_showTyping() {
  const box = document.getElementById('chatMessages');
  const div = document.createElement('div');
  div.className = 'chat-msg bot';
  div.innerHTML  = '<span style="opacity:.55;letter-spacing:4px;font-size:1rem">● ● ●</span>';
  if (box) { box.appendChild(div); box.scrollTop = box.scrollHeight; }
  return div;
}

// ── Wire up Enter key on chatInput on DOM ready ────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const inp = document.getElementById('chatInput');
  if (inp) {
    inp.addEventListener('keydown', e => {
      if (e.key === 'Enter') { e.preventDefault(); sendChat(); }
    });
  }
  // Also wire the FAB button in case onclick attr was missed
  const fab = document.getElementById('chatFab');
  if (fab) fab.onclick = toggleChat;
});