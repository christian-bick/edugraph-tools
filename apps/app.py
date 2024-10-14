import os

from google import generativeai as gemini
from api.routes import create_app

from dotenv import load_dotenv
load_dotenv()

gemini.configure(api_key=os.environ["API_KEY_GEMINI"])
app = create_app()