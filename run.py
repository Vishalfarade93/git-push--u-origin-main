import uvicorn
import sys
import os

if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 8000))
    print("=" * 65)
    print("  THE PERSONAL SIGNAL - Modern Broadsheet Newspaper")
    print(f"  Running at: http://{host}:{port}")
    print("  Press Ctrl+C to stop.")
    print("=" * 65)
    uvicorn.run("backend.server:app", host=host, port=port, reload=False)
