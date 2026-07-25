"""
NeuroSpeak – MongoDB Integration
Supports: Atlas (cloud) | Local MongoDB | Auto in-memory fallback
"""

import os
from datetime import datetime
from pymongo import MongoClient, DESCENDING
from pymongo.server_api import ServerApi

# ── Read URI from .env or environment ─────────────────────────────────────────
MONGO_URI = os.environ.get('MONGO_URI', '')

# ── Connection helper ─────────────────────────────────────────────────────────

def _make_client(uri: str) -> MongoClient:
    """
    Build a MongoClient with correct parameters for both
    Atlas (+srv) and local (localhost) connections.
    """
    is_atlas = '+srv' in uri or 'mongodb.net' in uri

    if is_atlas:
        return MongoClient(
            uri,
            server_api=ServerApi('1'),
            serverSelectionTimeoutMS=15000,
            connectTimeoutMS=15000,
            socketTimeoutMS=20000,
            tls=True,
            tlsAllowInvalidCertificates=True,  # fixes Windows SSL store issues
            retryWrites=True,
            w='majority',
        )
    else:
        # Local MongoDB – no TLS needed
        return MongoClient(
            uri,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
        )


# ── Connect ───────────────────────────────────────────────────────────────────

if not MONGO_URI:
    # No URI set at all → try local MongoDB first, then raise
    MONGO_URI = 'mongodb+srv://rashmiranjansahoo730_db_user:3lQfYGjU3F23ztXk@cluster0.ty6zj2e.mongodb.net/neurospeak'
    print("[MongoDB] No MONGO_URI set. Trying local MongoDB...")

try:
    client = _make_client(MONGO_URI)
    client.admin.command('ping')          # real connectivity test
    db = client['neurospeak']
    print(f"[MongoDB] ✅ Connected: {'Atlas' if 'mongodb.net' in MONGO_URI else 'Local'}")

except Exception as e:
    raise ConnectionError(f"MongoDB connection failed: {e}")


# ── Collections ───────────────────────────────────────────────────────────────
analyses = db['analyses']
reports  = db['reports']
users    = db['users']

# ── Indexes (safe – ignore if already exist) ──────────────────────────────────
try:
    analyses.create_index([('timestamp', DESCENDING)])
    analyses.create_index([('subject_id', 1)])
    reports.create_index([('analysis_id', 1)])
    users.create_index([('email', 1)], unique=True)
except Exception:
    pass


# ── CRUD ──────────────────────────────────────────────────────────────────────

def save_analysis(data: dict) -> str:
    doc = {
        'analysis_id':      data.get('analysis_id', ''),
        'subject_id':       data.get('subject_id', 'UNKNOWN'),
        'file_id':          data.get('file_id', ''),
        'timestamp':        data.get('timestamp', datetime.utcnow().isoformat()),
        'signal_quality':   data.get('signal_quality', 0),
        'channels':         data.get('channels', 64),
        'duration':         data.get('duration', 0),
        'predictions':      data.get('predictions', []),
        'generated_text':   data.get('generated_text', ''),
        'confidence':       data.get('confidence', 0),
        'accuracy':         data.get('accuracy', 0),
        'latency_ms':       data.get('latency_ms', 0),
        'attention_level':  data.get('attention_level', 0),
        'focus_score':      data.get('focus_score', 0),
        'alpha_power':      data.get('alpha_power', 0),
        'beta_power':       data.get('beta_power', 0),
        'theta_power':      data.get('theta_power', 0),
        'delta_power':      data.get('delta_power', 0),
        'freq_bands':       data.get('freq_bands', {}),
        'confusion_matrix': data.get('confusion_matrix', []),
        'created_at':       datetime.utcnow(),
    }
    result = analyses.insert_one(doc)
    return str(result.inserted_id)


def get_analysis(analysis_id: str):
    doc = analyses.find_one({'analysis_id': analysis_id})
    if doc:
        doc['_id'] = str(doc['_id'])
    return doc


def get_history(limit: int = 20, subject_id: str = None) -> list:
    query = {}
    if subject_id:
        query['subject_id'] = subject_id
    cursor = analyses.find(query, {'_id': 0}).sort('created_at', DESCENDING).limit(limit)
    return list(cursor)


def delete_analysis(analysis_id: str) -> bool:
    return analyses.delete_one({'analysis_id': analysis_id}).deleted_count > 0


def save_report(data: dict) -> str:
    result = reports.insert_one({
        'analysis_id':  data.get('analysis_id', ''),
        'subject_id':   data.get('subject_id', 'UNKNOWN'),
        'report_path':  data.get('report_path', ''),
        'generated_at': datetime.utcnow().isoformat(),
        'created_at':   datetime.utcnow(),
    })
    return str(result.inserted_id)


def get_report(analysis_id: str):
    doc = reports.find_one({'analysis_id': analysis_id})
    if doc:
        doc['_id'] = str(doc['_id'])
    return doc


def get_stats() -> dict:
    total    = analyses.count_documents({})
    pipeline = [{'$group': {
        '_id': None,
        'avg_confidence': {'$avg': '$confidence'},
        'avg_accuracy':   {'$avg': '$accuracy'},
    }}]
    agg = list(analyses.aggregate(pipeline))
    return {
        'total_analyses': total,
        'avg_confidence': round(agg[0].get('avg_confidence', 0), 2) if agg else 0,
        'avg_accuracy':   round(agg[0].get('avg_accuracy',   0), 2) if agg else 0,
        'total_subjects': len(analyses.distinct('subject_id')),
    }


def create_user(email: str, hashed_pw: str, role: str = 'user') -> str:
    result = users.insert_one({
        'email':      email,
        'password':   hashed_pw,
        'role':       role,
        'created_at': datetime.utcnow(),
    })
    return str(result.inserted_id)


def get_user(email: str):
    doc = users.find_one({'email': email})
    if doc:
        doc['_id'] = str(doc['_id'])
    return doc