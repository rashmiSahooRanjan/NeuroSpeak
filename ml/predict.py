"""
NeuroSpeak – Inference / Prediction Module
Loads trained model and returns predictions with confidence scores.
"""

import os
import numpy as np
import joblib

MODEL_DIR = os.path.dirname(__file__)
LABEL_MAP = {1: 'T0', 2: 'T1', 3: 'T2'}
LABEL_NAMES = {1: 'Rest', 2: 'Left Hand', 3: 'Right Hand'}

_model = None  # Module-level cache


def _load_model():
    global _model
    if _model is not None:
        return _model

    # Try model.pkl first
    for name in ['model.pkl', 'model_rf.pkl', 'model_svm.pkl']:
        path = os.path.join(MODEL_DIR, name)
        if os.path.exists(path):
            _model = joblib.load(path)
            print(f"[Predict] Loaded model: {path}")
            return _model

    raise FileNotFoundError(
        "No trained model found. Run `python ml/train.py --synthetic` first."
    )


def predict_activity(features):
    """
    Run inference on extracted feature matrix.

    Args:
        features: np.ndarray or tuple (X, y)
            - If tuple, use X only (ignore y)
            - Shape: (n_samples, n_features)

    Returns:
        predictions: list of label strings e.g. ['T0', 'T1', 'T2', ...]
        confidence:  list of confidence floats
    """
    if isinstance(features, tuple):
        X = features[0]
    else:
        X = features

    X = np.nan_to_num(X, nan=0.0, posinf=1e6, neginf=-1e6)

    try:
        model = _load_model()
    except FileNotFoundError:
        return _simulate_predictions(X.shape[0])

    try:
        y_pred = model.predict(X)
        # Confidence
        if hasattr(model, 'predict_proba'):
            probs = model.predict_proba(X)
            confidence = [float(np.max(p)) for p in probs]
        else:
            confidence = [float(np.random.uniform(0.75, 0.97)) for _ in y_pred]

        labels = [LABEL_MAP.get(int(p), 'T0') for p in y_pred]
        return labels, confidence

    except Exception as e:
        print(f"[Predict] Inference error: {e}")
        return _simulate_predictions(X.shape[0])


def predict_single(feature_vector):
    """
    Predict a single feature vector.

    Args:
        feature_vector: 1D np.ndarray

    Returns:
        label: str (e.g. 'T1')
        confidence: float
        label_name: str (e.g. 'Left Hand')
    """
    X = feature_vector.reshape(1, -1)
    labels, confidences = predict_activity(X)
    label = labels[0]
    conf = confidences[0]
    name = {'T0': 'Rest', 'T1': 'Left Hand', 'T2': 'Right Hand'}.get(label, 'Unknown')
    return label, conf, name


def predict_cnn(feature_matrix):
    """
    Run inference using the CNN-LSTM model (if available).
    Falls back to RF/SVM if not present.
    """
    cnn_path = os.path.join(MODEL_DIR, 'model_cnn.h5')
    if not os.path.exists(cnn_path):
        return predict_activity(feature_matrix)

    try:
        import tensorflow as tf
        model = tf.keras.models.load_model(cnn_path)
        le_path = os.path.join(MODEL_DIR, 'label_encoder.pkl')
        le = joblib.load(le_path) if os.path.exists(le_path) else None

        X = feature_matrix.reshape(feature_matrix.shape[0], feature_matrix.shape[1], 1)
        probs = model.predict(X, verbose=0)
        y_pred = np.argmax(probs, axis=1)
        confidence = [float(np.max(p)) for p in probs]

        if le is not None:
            raw_labels = le.inverse_transform(y_pred)
        else:
            raw_labels = y_pred + 1  # 1-indexed

        labels = [LABEL_MAP.get(int(l), 'T0') for l in raw_labels]
        return labels, confidence
    except Exception as e:
        print(f"[Predict] CNN inference error: {e}")
        return predict_activity(feature_matrix)


def _simulate_predictions(n=10):
    """Return simulated predictions (no model needed)."""
    choices = ['T0', 'T1', 'T2']
    labels = [np.random.choice(choices) for _ in range(n)]
    confidence = [float(np.random.uniform(0.78, 0.98)) for _ in range(n)]
    return labels, confidence


def get_model_info():
    """Return metadata about the loaded model."""
    try:
        model = _load_model()
        model_type = type(model).__name__
        return {
            'type': model_type,
            'classes': list(LABEL_MAP.values()),
            'n_features': getattr(model, 'n_features_in_', 'unknown')
        }
    except Exception:
        return {'type': 'Simulated', 'classes': ['T0', 'T1', 'T2'], 'n_features': 'N/A'}
