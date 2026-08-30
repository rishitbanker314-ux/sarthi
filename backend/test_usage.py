import asyncio
import httpx
import time
import json
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from services.api.db import get_session, async_session
from services.api.models.user import User
from services.api.models.learner_profile import LearnerProfile

async def create_user_if_not_exists(email: str, uid: str):
    async with async_session() as db:
        user = (await db.execute(select(User).filter_by(id=uid))).scalar_one_or_none()
        if not user:
            user = User(id=uid, email=email)
            db.add(user)
            try:
                await db.commit()
            except IntegrityError:
                await db.rollback()

        # Add profile
        profile = (await db.execute(select(LearnerProfile).filter_by(user_id=uid))).scalar_one_or_none()
        if not profile:
            profile = LearnerProfile(
                user_id=uid,
                profile_version=1,
                prior_knowledge={},
                pace="standard",
                representation_pref="concrete_first",
                scaffolding_pref="guided_discovery",
                depth_pref="breadth_survey",
                motivation="curiosity",
                session_minutes=30,
                language="English",
                accessibility={}
            )
            db.add(profile)
            try:
                await db.commit()
            except IntegrityError:
                await db.rollback()

async def run():
    async with httpx.AsyncClient(timeout=120.0) as client:
        # Create a mock auth token
        print("Creating auth token...")
        email = f"test_{str(uuid.uuid4())}@example.com"
        NAMESPACE_DEV_AUTH = uuid.UUID("12345678-1234-5678-1234-567812345678")
        uid = str(uuid.uuid5(NAMESPACE_DEV_AUTH, email.lower()))
        await create_user_if_not_exists(email, uid)

        resp = await client.post("http://127.0.0.1:8001/dev/auth/token", json={"email": email})
        resp.raise_for_status()
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Start a goal
        print("Starting goal...")
        resp = await client.post(
            "http://127.0.0.1:8001/api/v1/goals",
            json={"raw_input": "I want to learn async programming."},
            headers=headers
        )
        if resp.status_code != 200:
            print("Failed to start goal:", resp.text)
            return
            
        data = resp.json()
        goal_id = data["id"]
        
        # 3. Create a plan
        print("Triggering plan generation...")
        resp = await client.post(f"http://127.0.0.1:8001/api/v1/goals/{goal_id}/plan", headers=headers)
        if resp.status_code != 202:
            print("Failed to trigger plan:", resp.text)
            return

        print("Polling plan status...")
        while True:
            resp = await client.get(f"http://127.0.0.1:8001/api/v1/plans/{goal_id}", headers=headers)
            if resp.status_code == 200:
                print("Plan generation complete!")
                break
            time.sleep(1)
            
        # Get Usage
        resp = await client.get("http://127.0.0.1:8001/health/usage")
        print(resp.json())

if __name__ == "__main__":
    asyncio.run(run())
