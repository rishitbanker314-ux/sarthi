import asyncio
import os
from pydantic import BaseModel
from google import genai
from google.genai import types

class Answer(BaseModel):
    answer: str
    confidence: float

async def main():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY environment variable is missing or empty.")
        return

    client = genai.Client(api_key=api_key)
    
    prompt = "What is the capital of France? Return your confidence out of 1.0."
    print(f"Sending prompt: {prompt}\n")

    response = client.models.generate_content(
        model="gemini-3.7-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Answer,
            temperature=0.0
        )
    )

    print("--- Parsed Output ---")
    print(response.parsed)

    print("\n--- Token Usage ---")
    if hasattr(response, 'usage_metadata') and response.usage_metadata:
        print(f"Prompt Tokens:     {response.usage_metadata.prompt_token_count}")
        print(f"Candidates Tokens: {response.usage_metadata.candidates_token_count}")
        print(f"Total Tokens:      {response.usage_metadata.total_token_count}")
    else:
        print("No usage metadata returned.")

if __name__ == "__main__":
    asyncio.run(main())
