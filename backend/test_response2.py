from google.genai import types

print(types.GenerateContentResponse.model_fields.keys())
try:
    print(types.GenerateContentResponseUsageMetadata.model_fields.keys())
except Exception as e:
    print(f"Error GenerateContentResponseUsageMetadata: {e}")

try:
    print(types.GenerateContentResponse.__annotations__)
except:
    pass

