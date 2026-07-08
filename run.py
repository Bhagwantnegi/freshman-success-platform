"""
run.py
------
One-click launcher for the Freshman Success Intelligence Platform.
Run this file to start the server: python run.py
Then open your browser at: http://localhost:8000
"""

import subprocess
import sys
import webbrowser
import time


def main():
    print("\n🎓 Freshman Success Intelligence Platform")
    print("─" * 42)
    print("Starting server at http://localhost:8000")
    print("API docs at    http://localhost:8000/api/docs")
    print("Press Ctrl+C to stop.\n")

    # Open browser after a short delay
    def open_browser():
        time.sleep(2)
        webbrowser.open("http://localhost:8000")

    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "backend.main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000",
    ])


if __name__ == "__main__":
    main()
