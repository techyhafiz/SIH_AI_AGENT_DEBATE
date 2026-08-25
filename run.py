import sys
import os
import uvicorn
import webbrowser
import threading
import time

backend_dir = os.path.join(os.path.dirname(__file__), "multi-ai-debate", "backend")
if not os.path.exists(backend_dir):
    backend_dir = os.path.join(os.path.dirname(__file__), "backend")

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

def open_browser():
    time.sleep(1.5)
    print("\n[+] Opening browser at http://localhost:8000 ...")
    try:
        webbrowser.open("http://localhost:8000")
    except Exception:
        pass

if __name__ == "__main__":
    print("=" * 60)
    print(" STARTING AI CONSENSUS ARENA (UNIFIED SERVER)")
    print(" - Web Application: http://localhost:8000")
    print(" - Backend API: http://localhost:8000/docs")
    print("=" * 60)

    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, app_dir=backend_dir)
