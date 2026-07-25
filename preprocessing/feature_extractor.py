"""
NeuroSpeak – Feature Extractor
Extracts time-domain, frequency-domain, and statistical features from EEG epochs.
"""

import numpy as np
from scipy.stats import skew, kurtosis
from scipy.signal import welch


def extract_features(raw_or_epochs):
    """
    Main feature extraction dispatcher.
    Accepts either MNE Raw or MNE Epochs.

    Returns:
        X: np.ndarray of shape (n_samples, n_features)
        y: np.ndarray of labels (if epochs with events, else None)
    """
    try:
        # Try as Epochs first
        data = raw_or_epochs.get_data()  # (n_epochs, n_channels, n_times)
        labels = raw_or_epochs.events[:, 2]
        X = np.vstack([_extract_epoch_features(epoch) for epoch in data])
        y = labels
        return X, y
    except (AttributeError, IndexError):
        # Fall back to Raw: create sliding windows
        data = raw_or_epochs.get_data()  # (n_channels, n_times)
        sfreq = raw_or_epochs.info['sfreq']
        windows = _sliding_windows(data, sfreq, window_sec=2.0, step_sec=1.0)
        X = np.vstack([_extract_epoch_features(w) for w in windows])
        return X, None


def _sliding_windows(data, sfreq, window_sec=2.0, step_sec=1.0):
    """Create sliding windows from continuous raw data."""
    window_samples = int(window_sec * sfreq)
    step_samples = int(step_sec * sfreq)
    n_times = data.shape[1]
    windows = []
    for start in range(0, n_times - window_samples, step_samples):
        windows.append(data[:, start:start + window_samples])
    return windows


def _extract_epoch_features(epoch):
    """
    Extract a comprehensive feature vector from a single epoch.
    epoch: np.ndarray of shape (n_channels, n_times)

    Feature groups:
    1. Time-domain stats (mean, std, skew, kurtosis, peak-to-peak)
    2. Frequency-domain band powers (delta, theta, alpha, beta, gamma)
    3. Hjorth parameters (activity, mobility, complexity)
    4. Zero-crossing rate
    """
    features = []

    for ch_data in epoch:
        features.extend(_time_features(ch_data))
        features.extend(_freq_features(ch_data))
        features.extend(_hjorth_features(ch_data))
        features.append(_zero_crossing_rate(ch_data))

    return np.array(features, dtype=np.float32)


def _time_features(signal):
    """Statistical time-domain features."""
    return [
        float(np.mean(signal)),
        float(np.std(signal)),
        float(np.max(signal) - np.min(signal)),  # Peak-to-peak amplitude
        float(skew(signal)),
        float(kurtosis(signal)),
        float(np.sqrt(np.mean(signal ** 2))),     # RMS
        float(np.percentile(signal, 75) - np.percentile(signal, 25)),  # IQR
    ]


def _freq_features(signal, sfreq=160.0, nperseg=128):
    """Frequency band power features."""
    bands = {
        'delta': (0.5, 4),
        'theta': (4, 8),
        'alpha': (8, 13),
        'beta': (13, 30),
        'gamma': (30, 45),
    }
    try:
        freqs, psd = welch(signal, fs=sfreq, nperseg=min(nperseg, len(signal) // 2))
    except Exception:
        return [0.0] * len(bands)

    powers = []
    for fmin, fmax in bands.values():
        idx = np.logical_and(freqs >= fmin, freqs <= fmax)
        powers.append(float(np.mean(psd[idx])) if idx.any() else 0.0)
    return powers


def _hjorth_features(signal):
    """
    Hjorth Parameters:
    - Activity: variance of signal
    - Mobility: sqrt(var(diff(x)) / var(x))
    - Complexity: mobility(diff(x)) / mobility(x)
    """
    diff1 = np.diff(signal)
    diff2 = np.diff(diff1)

    var_x = np.var(signal) + 1e-10
    var_d1 = np.var(diff1) + 1e-10
    var_d2 = np.var(diff2) + 1e-10

    activity = var_x
    mobility = np.sqrt(var_d1 / var_x)
    complexity = np.sqrt(var_d2 / var_d1) / mobility if mobility > 0 else 0.0

    return [float(activity), float(mobility), float(complexity)]


def _zero_crossing_rate(signal):
    """Number of times the signal crosses zero per sample."""
    crossings = np.where(np.diff(np.sign(signal)))[0]
    return float(len(crossings) / len(signal))


def get_feature_names(n_channels=64):
    """Return feature names for interpretability."""
    time_names = ['mean', 'std', 'ptp', 'skew', 'kurtosis', 'rms', 'iqr']
    freq_names = ['delta', 'theta', 'alpha', 'beta', 'gamma']
    hjorth_names = ['hjorth_act', 'hjorth_mob', 'hjorth_comp']
    zcr_names = ['zcr']

    per_channel = time_names + freq_names + hjorth_names + zcr_names
    return [f"ch{i}_{f}" for i in range(n_channels) for f in per_channel]
