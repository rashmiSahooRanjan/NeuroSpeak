# NeuroSpeak – Deployment Guide

## Local Development

```bash
# 1. Create virtualenv
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy env file
cp .env.example .env
# Edit .env: set your MONGO_URI and SECRET_KEY

# 4. Train model (choose one)
python ml/train.py --synthetic          # No dataset needed
python ml/train.py --data_dir ./dataset # With PhysioNet data

# 5. Run server
python app.py
# Open: http://localhost:5000
```

---

## MongoDB Setup

### Option A – Local MongoDB
```bash
# Install MongoDB Community: https://www.mongodb.com/try/download/community
mongod --dbpath /data/db
# MONGO_URI=mongodb://localhost:27017/neurospeak
```

### Option B – MongoDB Atlas (Free Tier)
1. Go to https://cloud.mongodb.com → Create Free Cluster
2. Database Access → Add User (username/password)
3. Network Access → Add IP: 0.0.0.0/0
4. Connect → Drivers → Copy connection string
5. Set in .env:
```
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/neurospeak
```

---

## Deploy to Render (Free)

1. Push code to GitHub:
```bash
git init
git add .
git commit -m "Initial NeuroSpeak commit"
git remote add origin https://github.com/yourusername/neurospeak.git
git push -u origin main
```

2. Go to https://render.com → New → Web Service
3. Connect GitHub repository
4. Settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Environment: Python 3
5. Add Environment Variables:
   - `MONGO_URI` = your Atlas URI
   - `SECRET_KEY` = random-secret-key
   - `FLASK_ENV` = production
6. Click Deploy

---

## Deploy to Railway

```bash
npm install -g @railway/cli
railway login
railway new
railway up

# Set env vars in Railway dashboard:
# MONGO_URI, SECRET_KEY, FLASK_ENV=production
```

---

## Docker

```bash
# Build
docker build -t neurospeak:latest .

# Run
docker run -d \
  -p 5000:5000 \
  -e MONGO_URI="mongodb://host.docker.internal:27017/neurospeak" \
  -e SECRET_KEY="your-secret" \
  --name neurospeak \
  neurospeak:latest

# With MongoDB via Docker Compose
docker-compose up -d
```

### docker-compose.yml
```yaml
version: '3.8'
services:
  web:
    build: .
    ports: ["5000:5000"]
    environment:
      - MONGO_URI=mongodb://mongo:27017/neurospeak
      - SECRET_KEY=neurospeak-docker-secret
      - FLASK_ENV=production
    depends_on: [mongo]
  mongo:
    image: mongo:6.0
    volumes: [mongo_data:/data/db]
    ports: ["27017:27017"]
volumes:
  mongo_data:
```

---

## GitHub Setup

```bash
git init
git add .
git commit -m "🧠 NeuroSpeak v1.0.0 – Initial Release"
git branch -M main
git remote add origin https://github.com/USERNAME/NeuroSpeak.git
git push -u origin main

# Create release
git tag -a v1.0.0 -m "NeuroSpeak v1.0.0"
git push origin v1.0.0
```

---

## PhysioNet Dataset Download

```bash
# Install wget
pip install wfdb

# Download first 5 subjects (demo)
python - <<'EOF'
import wfdb
for i in range(1, 6):
    subj = f"S{i:03d}"
    for run in ['R03','R04','R07','R08','R11','R12']:
        try:
            wfdb.dl_database(
                'eegmmidb',
                dl_dir=f'./dataset/{subj}',
                records=[f"{subj}/{subj}{run}"]
            )
        except: pass
EOF
```

Full dataset: https://physionet.org/content/eegmmidb/1.0.0/

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Yes | neurospeak-secret-2024 | Flask/JWT secret |
| `MONGO_URI` | No | localhost:27017 | MongoDB connection |
| `FLASK_ENV` | No | development | Set to production on deploy |
| `PORT` | No | 5000 | Server port |

---

## API Quick Reference

```bash
# Health check
curl http://localhost:5000/api/health

# Upload EDF
curl -X POST -F "file=@S001R03.edf" http://localhost:5000/api/upload

# Analyze
curl -X POST -H "Content-Type: application/json" \
  -d '{"file_id":"uuid_S001R03.edf","subject_id":"S001"}' \
  http://localhost:5000/api/analyze

# History
curl http://localhost:5000/api/history?limit=5

# Dashboard stats
curl http://localhost:5000/api/dashboard/stats
```
