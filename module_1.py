from config import GROQ_API_KEY
from groq import Groq
import os

client = Groq(api_key=GROQ_API_KEY)

def speech_to_text(filename):
    with open(filename, "rb") as file:
        transcription = client.audio.transcriptions.create(
          file=(filename, file.read()),
          model="whisper-large-v3",
          response_format="verbose_json",
          language='en'
        )
        return transcription.text
  