import subprocess
import sys
import os
import time

def main():
    print("🚀 Starting Enterprise Cloud Engine...")
    
    root_dir = os.path.abspath(os.path.dirname(__file__))
    web_dir = os.path.join(root_dir, "web")
    
    # Using conda explicitly to ensure we are in the adv-rag-eval environment
    print("-> Starting FastAPI Backend on http://127.0.0.1:8000")
    backend_process = subprocess.Popen(
        "conda run -n adv-rag-eval uvicorn api.main:app --reload --host 127.0.0.1 --port 8000",
        shell=True,
        cwd=root_dir
    )
    
    # Start Vite Frontend
    print("-> Starting Vite Frontend on http://localhost:5173")
    frontend_process = subprocess.Popen(
        "npm run dev",
        shell=True,
        cwd=web_dir
    )
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Enterprise Cloud Engine...")
        backend_process.terminate()
        frontend_process.terminate()
        backend_process.wait()
        frontend_process.wait()
        print("✅ Shutdown complete.")

if __name__ == "__main__":
    main()
