"""
Streamlit App Runner
Simple script to start the Streamlit application
"""
import subprocess
import sys
from pathlib import Path

def main():
    """Run the Streamlit app"""
    app_path = Path(__file__).parent / "app.py"

    print("🚀 Starting EB-1A Agent System Streamlit UI...")
    print(f"📁 App path: {app_path}")
    print("\n" + "="*60)
    print("The app will open in your browser automatically")
    print("Press Ctrl+C to stop the server")
    print("="*60 + "\n")

    # Run streamlit
    subprocess.run([
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_path),
        "--server.port=8501",
        "--server.address=localhost"
    ])

if __name__ == "__main__":
    main()
