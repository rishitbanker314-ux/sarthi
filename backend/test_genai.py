from google import genai
from google.genai import types
import inspect

print("--- Client initialization ---")
print(inspect.signature(genai.Client.__init__))

client = genai.Client(api_key="DUMMY")

print("\n--- Generate Content ---")
print(inspect.signature(client.models.generate_content))
print(inspect.signature(client.aio.models.generate_content))

print("\n--- Generate Content Config ---")
print(inspect.signature(types.GenerateContentConfig.__init__))
