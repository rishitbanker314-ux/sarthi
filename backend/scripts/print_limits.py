import httpx
import os

key = os.environ["GEMINI_API_KEY"]
r = httpx.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={key}")
models = r.json().get("models", [])
for m in models:
    if "flash" in m["name"] or "pro" in m["name"]:
        print(f"{m['name']} - RPM: {m.get('rateLimit', 'Unknown')}")
