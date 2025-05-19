from openai import OpenAI
import os
from dotenv import load_dotenv

# Load your API key from .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

models = client.models.list()

print("\n✅ Models your API key has access to:\n")
for m in models.data:
    print("-", m.id)
