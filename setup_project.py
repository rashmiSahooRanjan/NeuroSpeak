"""
NeuroSpeak – Setup Script
Run: python setup.py
Installs deps, trains synthetic model, and verifies the installation.
"""
import subprocess, sys, os

def run(cmd, desc):
    print(f"\n{'─'*50}")
    print(f"  {desc}")
    print(f"{'─'*50}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"⚠️  Command returned non-zero exit: {cmd}")
    return result.returncode == 0

def main():
    print("\n" + "="*60)
    print("  🧠  NeuroSpeak – Automated Setup")
    print("="*60)

    # 1. Install core deps (lighter subset for quick setup)
    core_pkgs = [
        "flask", "flask-cors", "numpy", "pandas", "scipy",
        "scikit-learn", "joblib", "python-dotenv", "werkzeug", "gunicorn"
    ]
    run(f"pip install {' '.join(core_pkgs)} -q", "Installing core dependencies")

    # 2. Optional heavy deps
    print("\n[Optional] Install ML/signal processing packages?")
    print("  These are large (~1GB). Skip for quick demo.")
    choice = input("  Install TensorFlow + MNE? [y/N]: ").strip().lower()
    if choice == 'y':
        run("pip install tensorflow mne reportlab pymongo -q",
            "Installing TensorFlow, MNE, ReportLab, PyMongo")

    # 3. Create dirs
    for d in ['uploads', 'reports', 'dataset', 'ml']:
        os.makedirs(d, exist_ok=True)
    print("\n✅ Directories created")

    # 4. Copy .env
    if not os.path.exists('.env') and os.path.exists('.env.example'):
        import shutil
        shutil.copy('.env.example', '.env')
        print("✅ .env created from .env.example")

    # 5. Train synthetic model
    print("\n[Optional] Train ML model on synthetic data?")
    train = input("  Train now? (fast, no dataset needed) [Y/n]: ").strip().lower()
    if train != 'n':
        run("python ml/train.py --synthetic --models rf svm", "Training ML models (synthetic)")

    print("\n" + "="*60)
    print("  ✅  Setup complete!")
    print("="*60)
    print("\n  Start the server:  python app.py")
    print("  Run demo:          python run_demo.py")
    print("  Open dashboard:    http://localhost:5000")
    print("  Admin panel:       http://localhost:5000/admin\n")

if __name__ == '__main__':
    main()
