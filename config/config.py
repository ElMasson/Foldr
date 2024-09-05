#config/config.py

import os
from dotenv import load_dotenv

load_dotenv()

MISTRALAI_API_KEY = os.getenv('MISTRALAI_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GOOGLE_CSE_ID = os.getenv('GOOGLE_CSE_ID')
COHERE_API_KEY = os.getenv('COHERE_API_KEY')
LLAMA_CLOUD_API_KEY = os.getenv('LLAMA_CLOUD_API_KEY')

if not all([MISTRALAI_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY, GOOGLE_CSE_ID, COHERE_API_KEY, LLAMA_CLOUD_API_KEY]):
    raise ValueError("Toutes les clés API nécessaires ne sont pas définies dans le fichier .env")

