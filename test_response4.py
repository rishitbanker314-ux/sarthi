from google.genai import types

try:
    print(types.ThinkingConfig.__annotations__)
except Exception as e:
    print(f"Error ThinkingConfig: {e}")
