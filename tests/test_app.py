"""
NeuroSpeak – Unit Tests
Run: pytest tests/ -v
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import numpy as np
import pytest
import json


# ─── APP FIXTURE ──────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    from app import app
    app.config['TESTING'] = True
    app.config['UPLOAD_FOLDER'] = '/tmp/ns_test_uploads'
    os.makedirs('/tmp/ns_test_uploads', exist_ok=True)
    with app.test_client() as c:
        yield c


# ─── HEALTH ──────────────────────────────────────────────────────────────────

def test_health(client):
    r = client.get('/api/health')
    assert r.status_code == 200
    d = json.loads(r.data)
    assert d['status'] == 'online'
    assert 'version' in d


def test_index(client):
    r = client.get('/')
    assert r.status_code == 200


# ─── UPLOAD ──────────────────────────────────────────────────────────────────

def test_upload_no_file(client):
    r = client.post('/api/upload')
    assert r.status_code == 400

def test_upload_invalid_type(client):
    data = {'file': (b'fake content', 'test.exe')}
    r = client.post('/api/upload', data=data, content_type='multipart/form-data')
    assert r.status_code == 400

def test_upload_csv(client):
    # Create a minimal CSV
    csv_content = b"Fp1,Fp2,F3,F4\n0.1,0.2,0.3,0.4\n0.2,0.1,0.4,0.3\n"
    data = {'file': (csv_content, 'S001R03.csv')}
    r = client.post('/api/upload', data=data, content_type='multipart/form-data')
    assert r.status_code == 200
    d = json.loads(r.data)
    assert d['success'] == True
    assert 'file_id' in d
    assert 'subject_id' in d


# ─── PREDICT ─────────────────────────────────────────────────────────────────

def test_predict(client):
    payload = {'signal': [0.1] * 100}
    r = client.post('/api/predict',
                    data=json.dumps(payload),
                    content_type='application/json')
    assert r.status_code == 200
    d = json.loads(r.data)
    assert 'text' in d
    assert 'confidence' in d


# ─── HISTORY ─────────────────────────────────────────────────────────────────

def test_history(client):
    r = client.get('/api/history')
    assert r.status_code == 200
    d = json.loads(r.data)
    assert 'history' in d


def test_dashboard_stats(client):
    r = client.get('/api/dashboard/stats')
    assert r.status_code == 200
    d = json.loads(r.data)
    assert 'total_analyses' in d
    assert 'avg_accuracy' in d


# ─── FEATURE EXTRACTOR ───────────────────────────────────────────────────────

def test_time_features():
    from preprocessing.feature_extractor import _time_features
    sig = np.random.randn(320)
    feats = _time_features(sig)
    assert len(feats) == 7
    assert not any(np.isnan(feats))

def test_freq_features():
    from preprocessing.feature_extractor import _freq_features
    sig = np.random.randn(320)
    feats = _freq_features(sig)
    assert len(feats) == 5
    assert all(f >= 0 for f in feats)

def test_hjorth_features():
    from preprocessing.feature_extractor import _hjorth_features
    sig = np.random.randn(320)
    feats = _hjorth_features(sig)
    assert len(feats) == 3

def test_epoch_features():
    from preprocessing.feature_extractor import _extract_epoch_features
    epoch = np.random.randn(64, 320)  # 64 channels, 320 samples
    feats = _extract_epoch_features(epoch)
    assert feats.ndim == 1
    assert len(feats) > 0
    assert not np.any(np.isnan(feats))


# ─── SIMULATE PREDICTIONS ────────────────────────────────────────────────────

def test_simulate_predictions():
    from app import _simulate_predictions
    preds, conf = _simulate_predictions()
    assert len(preds) > 0
    assert all(p in ['T0', 'T1', 'T2'] for p in preds)
    assert all(0 <= c <= 1 for c in conf)

def test_predictions_to_text():
    from app import _predictions_to_text
    text = _predictions_to_text(['T1', 'T2', 'T0', 'T1'])
    assert isinstance(text, str)
    assert len(text) > 0


# ─── CONFUSION MATRIX ────────────────────────────────────────────────────────

def test_confusion_matrix():
    from app import _generate_confusion_matrix
    cm = _generate_confusion_matrix()
    assert len(cm) == 3
    assert all(len(row) == 3 for row in cm)
