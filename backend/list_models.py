import os
from google import genai

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

try:
    for m in client.models.list():
        if "gemini" in m.name:
            print(m.name, m.description)
except AttributeError:
    # the method might be named differently in this version
    pass

