"""
NeuroSpeak – MongoDB Atlas Full Diagnostic
Run: python test_mongo.py
"""
import sys, socket, subprocess

MONGO_URI = "mongodb+srv://rashmiranjansahoo730_db_user:3lQfYGjU3F23ztXk@cluster0.ty6zj2e.mongodb.net/neurospeak"

print("\n" + "="*60)
print("  NeuroSpeak – MongoDB Atlas Full Diagnostic")
print("="*60)

# ── CHECK 1: Python version ───────────────────────────────────────────
print(f"\n[1] Python version : {sys.version}")

# ── CHECK 2: pymongo ─────────────────────────────────────────────────
try:
    import pymongo
    from pymongo import MongoClient
    from pymongo.server_api import ServerApi
    print(f"[2] PyMongo        : {pymongo.version} ✅")
except ImportError:
    print("[2] PyMongo        : ❌ NOT INSTALLED")
    print("    Fix: pip install pymongo")
    sys.exit(1)

# ── CHECK 3: dnspython ───────────────────────────────────────────────
try:
    import dns.resolver
    print(f"[3] dnspython      : installed ✅")
except ImportError:
    print("[3] dnspython      : ❌ NOT INSTALLED")
    print("    Fix: pip install dnspython")
    sys.exit(1)

# ── CHECK 4: DNS resolution of Atlas cluster ─────────────────────────
print("\n[4] Resolving Atlas cluster DNS...")
try:
    import dns.resolver
    answers = dns.resolver.resolve('_mongodb._tcp.cluster0.effhf4z.mongodb.net', 'SRV')
    for r in answers:
        print(f"    ✅ SRV: {r.target} port {r.port}")
except Exception as e:
    print(f"    ❌ DNS FAILED: {e}")
    print("    → Your network/DNS is blocking Atlas SRV lookups")
    print("    → Try: change DNS to 8.8.8.8 (Google) or 1.1.1.1 (Cloudflare)")

# ── CHECK 5: TCP port 27017 reachability ─────────────────────────────
print("\n[5] Testing TCP port 27017 to Atlas hosts...")
hosts = [
    'ac-uxnjdgb-shard-00-00.effhf4z.mongodb.net',
    'ac-uxnjdgb-shard-00-01.effhf4z.mongodb.net',
    'ac-uxnjdgb-shard-00-02.effhf4z.mongodb.net',
]
tcp_ok = False
for host in hosts:
    try:
        sock = socket.create_connection((host, 27017), timeout=5)
        sock.close()
        print(f"    ✅ {host}:27017 reachable")
        tcp_ok = True
    except Exception as e:
        print(f"    ❌ {host}:27017 BLOCKED — {e}")

if not tcp_ok:
    print("\n    ⚠️  ALL Atlas hosts are unreachable on port 27017!")
    print("    This means your FIREWALL or ISP is blocking the connection.")
    print("    Solutions:")
    print("    A) Atlas Dashboard → Network Access → Add 0.0.0.0/0")
    print("    B) Disable Windows Firewall temporarily and test again")
    print("    C) Use a different network (mobile hotspot)")
    print("    D) Use port 27017 alternative — see option E below\n")

# ── CHECK 6: HTTPS port 443 (Atlas srv alternative) ──────────────────
print("\n[6] Testing HTTPS port 443 to Atlas (alternative)...")
try:
    sock = socket.create_connection(('cluster0.effhf4z.mongodb.net', 443), timeout=5)
    sock.close()
    print("    ✅ Port 443 reachable — try connecting via SRV over TLS")
except Exception as e:
    print(f"    ❌ Port 443 also blocked: {e}")

# ── CHECK 7: attempt actual connection ───────────────────────────────
print("\n[7] Attempting MongoDB Atlas connection (15s timeout)...")
try:
    client = MongoClient(
        MONGO_URI,
        server_api=ServerApi('1'),
        serverSelectionTimeoutMS=15000,
        connectTimeoutMS=15000,
        socketTimeoutMS=15000,
        tls=True,
        tlsAllowInvalidCertificates=True,
        retryWrites=True,
    )
    client.admin.command('ping')
    db = client['neurospeak']
    db['connection_test'].insert_one({'ping': True})
    db['connection_test'].delete_many({'ping': True})
    print("    ✅ CONNECTION SUCCESSFUL! MongoDB Atlas is working.")
    print("\n🎉 All checks passed. Run: python app.py\n")

except Exception as e:
    err = str(e)
    print(f"    ❌ Connection FAILED")
    print(f"    Error: {err[:200]}")

    print("\n" + "="*60)
    print("  DIAGNOSIS & SOLUTIONS")
    print("="*60)

    if "No replica set members" in err or "Timeout" in err:
        print("""
  ❌ CAUSE: Atlas Network Access is blocking your IP address
            OR your firewall/ISP is blocking port 27017.

  ── SOLUTION A (Atlas Network Access) ────────────────────
  1. Go to: https://cloud.mongodb.com
  2. Select your project
  3. Left sidebar → SECURITY → Network Access
  4. Click green button: "+ ADD IP ADDRESS"
  5. Click: "ALLOW ACCESS FROM ANYWHERE"
     (This adds 0.0.0.0/0 — allows all IPs)
  6. Click CONFIRM
  7. Wait 2-3 minutes for changes to apply
  8. Run: python test_mongo.py again

  ── SOLUTION B (Windows Firewall) ────────────────────────
  1. Windows Search → "Windows Defender Firewall"
  2. Click "Turn Windows Defender Firewall on or off"
  3. Turn OFF for Private network (temporarily)
  4. Test again, then turn back ON after confirming

  ── SOLUTION C (Mobile Hotspot) ──────────────────────────
  1. Connect your PC to your phone's mobile hotspot
  2. Run: python test_mongo.py
  3. If it works → your office/home router is blocking port 27017
  4. Fix: Add YOUR IP to Atlas Network Access (not 0.0.0.0/0)

  ── SOLUTION D (Use free MongoDB locally) ────────────────
  1. Download: https://www.mongodb.com/try/download/community
  2. Install and start MongoDB locally
  3. Change .env: MONGO_URI=mongodb://localhost:27017/neurospeak
  4. App works fully with local MongoDB
""")
    elif "Authentication" in err or "auth" in err.lower():
        print("""
  ❌ CAUSE: Wrong username or password.

  Fix in Atlas:
  1. SECURITY → Database Access
  2. Edit user: rs5038676_db_user
  3. Reset password and update .env MONGO_URI
""")
    elif "SSL" in err or "certificate" in err.lower():
        print("""
  ❌ CAUSE: SSL/TLS certificate error on Windows.
  Already using tlsAllowInvalidCertificates=True.
  Try: pip install certifi
       pip install pyopenssl
""")
    else:
        print(f"\n  Unknown error. Full message:\n  {err}\n")