"""
NeuroSpeak – Model Training Pipeline
Trains Random Forest, SVM, and CNN-LSTM on PhysioNet EEG Motor Imagery Dataset.

Usage:
    python ml/train.py --data_dir ./dataset --runs R03 R04 R07 R08 R11 R12
"""

import os
import argparse
import numpy as np
import joblib
from datetime import datetime

# ─── CONFIG ─────────────────────────────────────────────────────────────────

RUNS = ['R03', 'R04', 'R07', 'R08', 'R11', 'R12']
EVENT_ID = {'T0': 1, 'T1': 2, 'T2': 3}
LABEL_NAMES = ['Rest', 'Left Hand', 'Right Hand']
MODEL_DIR = os.path.join(os.path.dirname(__file__))
RANDOM_STATE = 42


# ─── DATA LOADING ────────────────────────────────────────────────────────────

def load_dataset(data_dir, runs=RUNS, subjects=None, max_subjects=20):
    """
    Load PhysioNet EEG Motor Imagery dataset.

    Args:
        data_dir: Root directory of the dataset (contains S001, S002, ...)
        runs: List of run IDs to include (e.g. ['R03', 'R04'])
        subjects: Explicit list of subject IDs; None = auto-discover
        max_subjects: Max subjects to load (for speed)

    Returns:
        X: np.ndarray (n_samples, n_features)
        y: np.ndarray (n_samples,)
    """
    from preprocessing.eeg_loader import load_eeg, get_event_annotations, epoch_data
    from preprocessing.signal_filter import preprocess_signal
    from preprocessing.feature_extractor import extract_features

    X_all, y_all = [], []

    if subjects is None:
        subjects = sorted([d for d in os.listdir(data_dir)
                           if d.startswith('S') and os.path.isdir(os.path.join(data_dir, d))])[:max_subjects]

    print(f"[Train] Loading {len(subjects)} subjects, runs: {runs}")

    for subj in subjects:
        subj_dir = os.path.join(data_dir, subj)
        for run in runs:
            edf_path = os.path.join(subj_dir, f"{subj}{run}.edf")
            if not os.path.exists(edf_path):
                continue
            try:
                raw = load_eeg(edf_path)
                raw = preprocess_signal(raw)
                events, eid = get_event_annotations(raw)
                if events.shape[0] == 0:
                    continue
                epochs = epoch_data(raw, events, eid)
                X, y = extract_features(epochs)
                X_all.append(X)
                y_all.append(y)
                print(f"  ✓ {subj}/{run}: {X.shape[0]} epochs")
            except Exception as e:
                print(f"  ✗ {subj}/{run}: {e}")
                continue

    if not X_all:
        raise RuntimeError("No data loaded. Check dataset path and structure.")

    return np.vstack(X_all), np.concatenate(y_all)


def generate_synthetic_data(n_samples=2000, n_features=1024, n_classes=3):
    """Generate synthetic EEG features for demonstration / CI testing."""
    np.random.seed(RANDOM_STATE)
    X = np.random.randn(n_samples, n_features).astype(np.float32)
    y = np.random.randint(1, n_classes + 1, n_samples)
    # Add class-specific signal
    for cls in range(1, n_classes + 1):
        mask = y == cls
        X[mask, (cls - 1) * 50: cls * 50] += cls * 0.5
    return X, y


# ─── TRAINING ────────────────────────────────────────────────────────────────

def train_random_forest(X_train, y_train):
    from sklearn.ensemble import RandomForestClassifier
    clf = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        min_samples_split=5,
        random_state=RANDOM_STATE,
        n_jobs=-1
    )
    clf.fit(X_train, y_train)
    return clf


def train_svm(X_train, y_train):
    from sklearn.svm import SVC
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import Pipeline

    pipe = Pipeline([
        ('scaler', StandardScaler()),
        ('svm', SVC(kernel='rbf', C=10, gamma='scale',
                    probability=True, random_state=RANDOM_STATE))
    ])
    pipe.fit(X_train, y_train)
    return pipe


def train_cnn_lstm(X_train, y_train, n_classes=3, epochs=30, batch_size=32):
    """
    Build and train a 1D CNN + LSTM model for EEG classification.
    Input shape: (n_samples, n_features) → reshaped to (n_samples, n_features, 1)
    """
    try:
        import tensorflow as tf
        from tensorflow.keras import layers, models
        from sklearn.preprocessing import LabelEncoder
        from tensorflow.keras.utils import to_categorical

        # Encode labels to 0-indexed
        le = LabelEncoder()
        y_enc = le.fit_transform(y_train)
        y_cat = to_categorical(y_enc, num_classes=n_classes)

        X_in = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)

        model = models.Sequential([
            layers.Conv1D(64, kernel_size=5, activation='relu', padding='same',
                         input_shape=(X_train.shape[1], 1)),
            layers.BatchNormalization(),
            layers.MaxPooling1D(pool_size=2),
            layers.Conv1D(128, kernel_size=3, activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling1D(pool_size=2),
            layers.LSTM(64, return_sequences=True),
            layers.LSTM(32),
            layers.Dropout(0.4),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(n_classes, activation='softmax')
        ])

        model.compile(optimizer=tf.keras.optimizers.Adam(1e-3),
                      loss='categorical_crossentropy',
                      metrics=['accuracy'])

        model.fit(X_in, y_cat,
                  epochs=epochs,
                  batch_size=batch_size,
                  validation_split=0.15,
                  verbose=1)

        return model, le
    except ImportError:
        print("[Train] TensorFlow not available. Skipping CNN-LSTM.")
        return None, None


# ─── EVALUATION ──────────────────────────────────────────────────────────────

def evaluate_model(clf, X_test, y_test, model_name='Model'):
    from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    report = classification_report(y_test, y_pred,
                                   target_names=LABEL_NAMES,
                                   output_dict=True)

    print(f"\n{'─'*50}")
    print(f"  {model_name} Results")
    print(f"{'─'*50}")
    print(f"  Accuracy : {acc * 100:.2f}%")
    print(classification_report(y_test, y_pred, target_names=LABEL_NAMES))
    print(f"  Confusion Matrix:\n{cm}")

    return {
        'model_name': model_name,
        'accuracy': acc,
        'confusion_matrix': cm.tolist(),
        'report': report
    }


# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='NeuroSpeak Model Trainer')
    parser.add_argument('--data_dir', default='./dataset',
                        help='Root directory of PhysioNet dataset')
    parser.add_argument('--runs', nargs='+', default=RUNS)
    parser.add_argument('--synthetic', action='store_true',
                        help='Use synthetic data (no dataset needed)')
    parser.add_argument('--models', nargs='+', default=['rf', 'svm'],
                        choices=['rf', 'svm', 'cnn'],
                        help='Models to train')
    args = parser.parse_args()

    from sklearn.model_selection import train_test_split

    print("\n" + "="*60)
    print("  NeuroSpeak – Training Pipeline")
    print("="*60)
    print(f"  Start time : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Models     : {args.models}")

    # Load or generate data
    if args.synthetic or not os.path.exists(args.data_dir):
        print("\n[Train] Using synthetic data...")
        X, y = generate_synthetic_data()
    else:
        print(f"\n[Train] Loading from: {args.data_dir}")
        X, y = load_dataset(args.data_dir, runs=args.runs)

    print(f"\n[Train] Dataset: {X.shape[0]} samples, {X.shape[1]} features, {len(set(y))} classes")

    # Handle NaN/Inf
    X = np.nan_to_num(X, nan=0.0, posinf=1e6, neginf=-1e6)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y)

    results = []

    # Random Forest
    if 'rf' in args.models:
        print("\n[Train] Training Random Forest...")
        rf = train_random_forest(X_train, y_train)
        res = evaluate_model(rf, X_test, y_test, 'Random Forest')
        results.append(res)
        rf_path = os.path.join(MODEL_DIR, 'model_rf.pkl')
        joblib.dump(rf, rf_path)
        print(f"[Train] Saved: {rf_path}")

    # SVM
    if 'svm' in args.models:
        print("\n[Train] Training SVM...")
        svm = train_svm(X_train, y_train)
        res = evaluate_model(svm, X_test, y_test, 'SVM')
        results.append(res)
        svm_path = os.path.join(MODEL_DIR, 'model_svm.pkl')
        joblib.dump(svm, svm_path)
        print(f"[Train] Saved: {svm_path}")

    # CNN-LSTM
    if 'cnn' in args.models:
        print("\n[Train] Training CNN-LSTM...")
        cnn, le = train_cnn_lstm(X_train, y_train)
        if cnn is not None:
            cnn.save(os.path.join(MODEL_DIR, 'model_cnn.h5'))
            joblib.dump(le, os.path.join(MODEL_DIR, 'label_encoder.pkl'))

    # Save best model as model.pkl (for predict.py)
    if results:
        best = max(results, key=lambda r: r['accuracy'])
        best_model_name = best['model_name']
        src = os.path.join(MODEL_DIR, f"model_{'rf' if 'Forest' in best_model_name else 'svm'}.pkl")
        dst = os.path.join(MODEL_DIR, 'model.pkl')
        if os.path.exists(src):
            import shutil
            shutil.copy(src, dst)
            print(f"\n[Train] Best model: {best_model_name} ({best['accuracy']*100:.2f}%) → saved as model.pkl")

    print(f"\n[Train] Done. {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


if __name__ == '__main__':
    main()
