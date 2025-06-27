from dotenv import load_dotenv
import os

load_dotenv()  # load variables from .env file

api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    print("API key loaded successfully!")
else:
    print("Failed to load API key.")
