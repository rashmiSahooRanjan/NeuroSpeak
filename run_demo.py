"""
NeuroSpeak – Demo Runner
Generates a synthetic EEG CSV, uploads it, runs analysis, and prints results.
Run: python run_demo.py
"""

import os
import sys
import json
import time
import numpy as np
import requests

BASE_URL = "http://localhost:5000"


def generate_demo_csv(path="demo_eeg.csv", n_channels=8, duration_s=10, sfreq=160):
    """Create a synthetic EEG CSV file."""
    n_samples = int(duration_s * sfreq)
    t = np.linspace(0, duration_s, n_samples)
    ch_names = ["Fp1", "Fp2", "F3", "F4", "C3", "C4", "P3", "P4"][:n_channels]
    data = {}
    for i, ch in enumerate(ch_names):
        # Mix of alpha (10Hz), beta (20Hz), and noise
        data[ch] = (
            np.sin(2 * np.pi * 10 * t) * (0.3 + 0.1 * i)
            + np.sin(2 * np.pi * 20 * t) * 0.15
            + np.random.randn(n_samples) * 0.05
        )

    import csv
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(ch_names)
        for i in range(n_samples):
            writer.writerow([round(data[ch][i], 6) for ch in ch_names])
    print(f"✅ Generated demo EEG: {path} ({n_channels}ch, {duration_s}s, {sfreq}Hz)")
    return path


def wait_for_server(max_tries=10):
    for i in range(max_tries):
        try:
            r = requests.get(f"{BASE_URL}/api/health", timeout=2)
            if r.status_code == 200:
                print(f"✅ Server online: {r.json().get('version')}")
                return True
        except Exception:
            pass
        print(f"   Waiting for server... ({i+1}/{max_tries})")
        time.sleep(1)
    return False


def run_demo():
    print("\n" + "="*60)
    print("  🧠 NeuroSpeak Demo Runner")
    print("="*60)

    # 1. Check server
    print("\n[1/4] Checking server...")
    if not wait_for_server():
        print("❌ Server not running. Start with: python app.py")
        sys.exit(1)

    # 2. Generate demo file
    print("\n[2/4] Generating synthetic EEG data...")
    csv_path = generate_demo_csv()

    # 3. Upload
    print("\n[3/4] Uploading EEG file...")
    with open(csv_path, 'rb') as f:
        r = requests.post(f"{BASE_URL}/api/upload", files={'file': ('S999R03.csv', f, 'text/csv')})
    if r.status_code != 200:
        print(f"❌ Upload failed: {r.text}")
        sys.exit(1)
    upload_data = r.json()
    file_id = upload_data['file_id']
    print(f"   File ID    : {file_id}")
    print(f"   Subject    : {upload_data['subject_id']}")
    print(f"   Size       : {upload_data['file_size_mb']} MB")

    # 4. Analyze
    print("\n[4/4] Running AI analysis pipeline...")
    r = requests.post(f"{BASE_URL}/api/analyze", json={
        'file_id': file_id,
        'subject_id': upload_data['subject_id']
    })
    if r.status_code != 200:
        print(f"❌ Analysis failed: {r.text}")
        sys.exit(1)

    result = r.json()['result']

    # Print results
    print("\n" + "="*60)
    print("  📊 ANALYSIS RESULTS")
    print("="*60)
    print(f"  Analysis ID    : {result['analysis_id'][:16]}...")
    print(f"  Subject ID     : {result['subject_id']}")
    print(f"  Signal Quality : {result['signal_quality']} μV")
    print(f"  Attention Level: {result['attention_level']}%")
    print(f"  Focus Score    : {result['focus_score']}%")
    print(f"  Alpha Power    : {result['alpha_power']}")
    print(f"  Beta Power     : {result['beta_power']}")
    print()
    print(f"  Generated Text : 🗣  {result['generated_text']}")
    print(f"  Confidence     : {result['confidence']}%")
    print(f"  Model Accuracy : {result['accuracy']}%")
    print(f"  Latency        : {result['latency_ms']} ms")
    print(f"  Predictions    : {' → '.join(result['predictions'][:8])}...")
    print()
    print(f"  ✅ Open http://localhost:5000 to view the dashboard")
    print("="*60 + "\n")

    # Cleanup
    try:
        os.remove(csv_path)
    except Exception:
        pass


if __name__ == '__main__':
    run_demo()
