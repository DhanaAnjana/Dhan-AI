import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("WARNING: GROQ_API_KEY is not set in environment variables.")

# Initialize the Groq client
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
