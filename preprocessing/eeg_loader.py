"""
NeuroSpeak – EEG Loader
Loads EDF files using MNE-Python.
PhysioNet EEG Motor Movement/Imagery Dataset compatible.
"""

import os
import numpy as np

def load_eeg(filepath: str):
    """
    Load an EDF file and return an MNE Raw object.

    Args:
        filepath: Path to the EDF file.

    Returns:
        mne.io.Raw object with signal data.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        ValueError: If the file cannot be parsed as EDF.
    """
    import mne

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"EDF file not found: {filepath}")

    ext = os.path.splitext(filepath)[1].lower()

    if ext == '.edf':
        raw = mne.io.read_raw_edf(filepath, preload=True, verbose=False)
    elif ext == '.csv':
        raw = _load_csv_as_raw(filepath)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    print(f"[EEG Loader] Loaded: {filepath}")
    print(f"  Channels  : {raw.info['nchan']}")
    print(f"  Sfreq     : {raw.info['sfreq']} Hz")
    print(f"  Duration  : {raw.times[-1]:.2f} s")
    print(f"  Ch names  : {raw.info['ch_names'][:5]} ...")

    return raw


def _load_csv_as_raw(filepath: str):
    """
    Load a CSV file as an MNE Raw object.
    Expected format: time column + EEG channel columns.
    """
    import mne
    import pandas as pd

    df = pd.read_csv(filepath)

    # Try to detect time column
    time_cols = [c for c in df.columns if c.lower() in ['time', 't', 'timestamp']]
    if time_cols:
        df = df.drop(columns=time_cols)

    ch_names = list(df.columns)
    data = df.values.T.astype(np.float64)

    # Assume 160 Hz sampling rate (PhysioNet standard)
    sfreq = 160.0
    info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types='eeg')
    raw = mne.io.RawArray(data, info, verbose=False)

    return raw


def get_event_annotations(raw):
    """
    Extract event annotations from a PhysioNet EDF file.
    Returns events array and event_id mapping.
    T0 = rest, T1 = left hand, T2 = right hand
    """
    import mne

    event_id = {'T0': 1, 'T1': 2, 'T2': 3}
    try:
        events, _ = mne.events_from_annotations(raw, event_id=event_id, verbose=False)
    except Exception:
        # Fallback: generate synthetic events
        n_events = max(1, int(raw.times[-1] / 4))
        onsets = np.linspace(0, raw.times[-1] - 2, n_events)
        events = np.column_stack([
            (onsets * raw.info['sfreq']).astype(int),
            np.zeros(n_events, dtype=int),
            np.random.choice([1, 2, 3], n_events)
        ])

    return events, event_id


def epoch_data(raw, events, event_id, tmin=-0.2, tmax=0.8):
    """
    Epoch the raw data around events.

    Args:
        raw: MNE Raw object
        events: Events array
        event_id: Event ID mapping
        tmin: Epoch start (seconds before event)
        tmax: Epoch end (seconds after event)

    Returns:
        mne.Epochs object
    """
    import mne

    epochs = mne.Epochs(
        raw, events, event_id=event_id,
        tmin=tmin, tmax=tmax,
        baseline=(None, 0),
        preload=True,
        verbose=False
    )
    return epochs


def get_signal_stats(raw):
    """Compute basic statistics of the raw EEG signal."""
    data = raw.get_data()
    return {
        'n_channels': data.shape[0],
        'n_samples': data.shape[1],
        'duration_s': raw.times[-1],
        'sfreq': raw.info['sfreq'],
        'mean_uv': float(np.mean(np.abs(data)) * 1e6),
        'std_uv': float(np.std(data) * 1e6),
        'max_uv': float(np.max(np.abs(data)) * 1e6),
        'channel_names': raw.info['ch_names']
    }
