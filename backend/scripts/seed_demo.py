import asyncio
import os
import sys
from uuid import uuid4
from datetime import datetime, timezone

# Ensure sys.path includes the backend root directory for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.ext.asyncio import AsyncSession
from services.api.db import async_session
from services.api.models import User, LearnerProfile, Goal, Plan, Module, Lesson, LessonContent
from services.api.models.enums import Pace, RepresentationPref, ScaffoldingPref, DepthPref, Motivation
from sqlalchemy import select, delete
from services.api.routers.dev_auth import dev_user_id

async def seed_demo_user():
    email = "demo@sarathi.app"
    expected_user_id = dev_user_id(email)

    async with async_session() as db:
        async with db.begin():
            # Check if demo user already exists
            result = await db.execute(select(User).where(User.email == email))
            demo_user = result.scalars().first()
            if not demo_user:
                print(f"Creating missing demo user: {email} with ID {expected_user_id}")
                demo_user = User(id=expected_user_id, email=email)
                db.add(demo_user)
                await db.flush()
            elif demo_user.id != expected_user_id:
                print(f"⚠️ Warning: Existing demo user has ID {demo_user.id}, but dev_auth expects {expected_user_id}")
            
            # Delete old profiles for this user
            await db.execute(delete(LearnerProfile).where(LearnerProfile.user_id == demo_user.id))
            
            profile = LearnerProfile(
                user_id=demo_user.id,
                profile_version=1,
                prior_knowledge={},
                pace=Pace.deliberate,
                representation_pref=RepresentationPref.concrete_first,
                scaffolding_pref=ScaffoldingPref.worked_examples,
                depth_pref=DepthPref.depth_mastery,
                motivation=Motivation.exam,
                session_minutes=25,
                language="en",
                accessibility={
                    "font_scale": 1.0,
                    "reduced_motion": False,
                    "screen_reader": False,
                    "dyslexia_font": False
                }
            )
            db.add(profile)
            print("Created LearnerProfile for demo user.")
            
            # Check if Goal exists to avoid duplicates when running twice
            goal_result = await db.execute(select(Goal).where(Goal.user_id == demo_user.id))
            goal = goal_result.scalars().first()
            if not goal:
                # Create Goal
                goal = Goal(
                    user_id=demo_user.id,
                    raw_input="I want to learn data structures and algorithms to pass technical interviews.",
                    normalized_topic="Data Structures and Algorithms",
                    target_level="Intermediate",
                    deadline=None,
                    status="planned"
                )
                db.add(goal)
                await db.flush()
                
                # Create Plan
                plan = Plan(
                    goal_id=goal.id,
                    version=1,
                    title="DSA Mastery",
                    rationale="To pass technical interviews.",
                    profile_version=1,
                    status="draft"
                )
                db.add(plan)
                await db.flush()
                
                # Create Module
                module = Module(
                    plan_id=plan.id,
                    title="Introduction to Arrays and Strings",
                    objective="Master the fundamentals of array manipulation.",
                    rationale="Arrays and strings are the building blocks of most technical interviews.",
                    est_minutes=20,
                    order_index=0,
                    status="draft"
                )
                db.add(module)
                await db.flush()
                
                # Create Lesson
                lesson = Lesson(
                    module_id=module.id,
                    title="Array Reversal Techniques",
                    objective="Learn how to reverse an array in-place.",
                    concept_ids=[],
                    est_minutes=20,
                    order_index=0,
                    status="draft"
                )
                db.add(lesson)
                await db.flush()
                
                # Cache some Lesson Content
                lesson_content = LessonContent(
                    lesson_id=lesson.id,
                    profile_version=1,
                    blocks=[
                        {
                            "id": "block-1",
                            "type": "explanation",
                            "content": "# Reversing an Array In-Place\n\nTo reverse an array efficiently without using extra memory, we can use the **two-pointer technique**.",
                            "metadata": {}
                        },
                        {
                            "id": "block-2",
                            "type": "code",
                            "content": "def reverse_array(arr):\n    left, right = 0, len(arr) - 1\n    while left < right:\n        arr[left], arr[right] = arr[right], arr[left]\n        left += 1\n        right -= 1\n    return arr",
                            "metadata": {"language": "python"}
                        },
                        {
                            "id": "block-3",
                            "type": "question",
                            "content": "What is the time complexity of the in-place array reversal?",
                            "metadata": {
                                "question_type": "multiple_choice",
                                "options": ["O(1)", "O(log n)", "O(n)", "O(n^2)"],
                                "correct_answer": "O(n)",
                                "explanation": "We iterate through half of the array, which takes O(n/2) time. This simplifies to O(n)."
                            }
                        }
                    ],
                    token_cost=150
                )
                db.add(lesson_content)
                print("Created goal, plan, module, and lesson data.")
            else:
                print("Goal already exists, skipping creation of plan data.")
            
            print(f"[OK] Demo user 'demo@sarathi.app' seeded successfully. (User ID: {demo_user.id})")

if __name__ == "__main__":
    asyncio.run(seed_demo_user())
