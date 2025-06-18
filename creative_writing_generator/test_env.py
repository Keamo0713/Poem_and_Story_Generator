from dotenv import load_dotenv
import os
from pathlib import Path

print("Trying to load .env...")

# Explicit path load
dotenv_path = Path("C:/Users/Capaciti/Downloads/creative_writing_generator/.env")
if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path)
else:
    print("❌ .env file not found at specified path.")

# Check variables
api_key = os.getenv("AZURE_OPENAI_API_KEY")
if api_key:
    print("✅ API key loaded.")
    print("Endpoint:", os.getenv("AZURE_OPENAI_ENDPOINT"))
    print("Deployment:", os.getenv("AZURE_OPENAI_DEPLOYMENT"))
else:
    print("❌ API key not loaded.")
