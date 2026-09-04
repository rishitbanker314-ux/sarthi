import asyncio
import httpx
import time
import os
import json

import argparse

BASE_URL = os.environ.get("API_URL", "http://127.0.0.1:8000")

async def main(args):
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=600.0) as client:
        print("1. Creating Demo User...")
        response = await client.post("/dev/auth/token", json={"email": "demo@example.com"})
        if response.status_code != 200:
            print("Failed to create demo user.", response.text)
            return
            
        data = response.json()
        token = data.get("access_token") or data.get("token")
        headers = {"Authorization": f"Bearer {token}"}
        
        print("2. Fetching Learner Profile (and upserting user)...")
        res = await client.get("/api/v1/me", headers=headers)
        learner = res.json()
        
        print("3. Submit Diagnostic (via chat)...")
        res = await client.post("/api/v1/diagnostic/sessions", headers=headers)
        session_id = res.json()["id"]
        
        answers = [
            "I have about 2 years of experience with JavaScript.",
            "I can dedicate about 10 hours per week.",
            "I want to learn Python and system design."
        ]
        
        idx = 0
        while True:
            if args.slow: await asyncio.sleep(4)
            ans = answers[idx % len(answers)]
            res = await client.post(f"/api/v1/diagnostic/sessions/{session_id}/answer", headers=headers, json={"answer": ans})
            if res.status_code == 429:
                await asyncio.sleep(2)
                continue
            idx += 1
            data = res.json()
            if data.get("complete"):
                break
        
        res = await client.post(f"/api/v1/diagnostic/sessions/{session_id}/complete", headers=headers)
        learner = res.json()
        learner_id = learner.get("learner_id") or learner.get("id")
        
        print("4. Parse Goal...")
        goal_payload = {"raw_input": "Learn Python for Data Science"}
        res = await client.post("/api/v1/goals", headers=headers, json=goal_payload)
        goal = res.json()
        goal_id = goal["id"]
        
        print("5. Generate Plan...")
        if args.slow: await asyncio.sleep(15)  # Wait for Pro quota to definitely refresh
        res = await client.post(f"/api/v1/goals/{goal_id}/plan", headers=headers)
        job = res.json()
        job_id = job["job_id"]
        
        print(f"Polling job {job_id} for plan generation...")
        plan_id = None
        while True:
            res = await client.get(f"/api/v1/jobs/{job_id}", headers=headers)
            j = res.json()
            if j["status"] == "succeeded":
                plan_id = j["result"]["plan_id"]
                break
            elif j["status"] == "failed":
                print("Plan generation failed:", j)
                return
            await asyncio.sleep(2)
            
        print("6. Fetching Plan...")
        res = await client.get(f"/api/v1/plans/{plan_id}", headers=headers)
        plan = res.json()
        
        print("\n--- PLAN RATIONALE EXCERPT ---")
        print(plan.get("rationale", "")[:200] + "...")
        print("------------------------------\n")
        
        # Get first module and FIRST lesson only
        module = plan["modules"][0]
        lesson = module["lessons"][0]
        
        lesson_id = lesson["id"]
        print(f"7. Generating 1 Lesson {lesson_id}...")
        if args.slow: await asyncio.sleep(4)
        res = await client.post(f"/api/v1/lessons/{lesson_id}/start", headers=headers)
        
        content = ""
        async with client.stream("GET", f"/api/v1/lessons/{lesson_id}/content", headers=headers) as stream_res:
            async for chunk in stream_res.aiter_text():
                content += chunk
                
        print("\n--- LESSON CONTENT EXCERPT ---")
        print(content[:200] + "...")
        print("------------------------------\n")
                
        print("8. Generating Checkpoint (1 quiz)...")
        if args.slow: await asyncio.sleep(4)
        res = await client.post(f"/api/v1/lessons/{lesson_id}/checkpoint", headers=headers)
        checkpoint = res.json()
        if res.status_code != 200: print(f"ERROR: {res.status_code} {res.text}"); exit(1)
        checkpoint_id = checkpoint["id"]
            
        print("9. Submitting Checkpoint...")
        responses = {
            item["id"]: item["options"][0] if item.get("options") else "answer"
            for item in checkpoint["items"]
        }
        res = await client.post(f"/api/v1/checkpoints/{checkpoint_id}/submit", headers=headers, json={"responses": responses})
        print("Evaluation result:", res.status_code)
                
        print("10. Triggering Adaptation...")
        if args.slow: await asyncio.sleep(15)  # Wait for Pro quota
        res = await client.post(f"/api/v1/plans/{plan_id}/replan", headers=headers)
        job = res.json()
        a_job_id = job["job_id"]
        
        print(f"Polling job {a_job_id} for adaptation...")
        while True:
            res = await client.get(f"/api/v1/jobs/{a_job_id}", headers=headers)
            j = res.json()
            if j["status"] == "succeeded":
                break
            elif j["status"] == "failed":
                print("Adaptation failed:", j)
                return
            await asyncio.sleep(2)

        print("Measurement flow complete!")
        print("\n--- PREWARM COMPLETE ---")
        print(f"Learner ID: {learner_id}")
        print(f"Access Token: {token}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--slow", action="store_true", help="Sleep between calls to respect rate limits")
    args = parser.parse_args()
    asyncio.run(main(args))
