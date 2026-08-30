import asyncio
import os
import sys
from uuid import uuid4
from datetime import datetime, timezone

# Ensure sys.path includes the backend root directory for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import AsyncSession
from services.api.db import async_session
from services.api.models import User, LearnerProfile, Goal, Plan, Module, Lesson, LessonContent
from services.api.models.enums import Pace, RepresentationPref, ScaffoldingPref, DepthPref, Motivation
from sqlalchemy import select

async def seed_demo_user():
    async with async_session() as db:
        async with db.begin():
            
            # Check if demo user already exists
            result = await db.execute(select(User).where(User.email == "demo@sarathi.app"))
            demo_user = result.scalar_one_or_none()
            if not demo_user:
                print("❌ User 'demo@sarathi.app' not found! Please sign up via the frontend first.")
                return
                
            # Check if already seeded
            profile_result = await db.execute(select(LearnerProfile).where(LearnerProfile.user_id == demo_user.id))
            if profile_result.scalar_one_or_none():
                print(f"⚠️ Demo user 'demo@sarathi.app' is already seeded (User ID: {demo_user.id})")
                return
            profile = LearnerProfile(
                user_id=demo_user.id,
                profile_version=1,
                prior_knowledge="Basic programming experience in Python.",
                pace=Pace.standard,
                representation_pref=RepresentationPref.concrete_first,
                scaffolding_pref=ScaffoldingPref.guided_discovery,
                depth_pref=DepthPref.depth_mastery,
                motivation=Motivation.career,
                session_minutes=30,
                language="English"
            )
            db.add(profile)
            
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
                user_id=demo_user.id,
                goal_id=goal.id,
                total_est_minutes=300
            )
            db.add(plan)
            await db.flush()
            
            # Create Module
            module = Module(
                plan_id=plan.id,
                title="Introduction to Arrays and Strings",
                description="Master the fundamentals of array manipulation.",
                order_index=0
            )
            db.add(module)
            await db.flush()
            
            # Create Lesson
            lesson = Lesson(
                module_id=module.id,
                title="Array Reversal Techniques",
                objective="Learn how to reverse an array in-place.",
                concept_ids=["array", "in-place", "two-pointers"],
                est_minutes=20,
                order_index=0,
                status="planned"
            )
            db.add(lesson)
            await db.flush()
            
            # Cache some Lesson Content
            lesson_content = LessonContent(
                lesson_id=lesson.id,
                profile_version=1,
                blocks={
                    "blocks": [
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
                    ]
                },
                token_cost=150
            )
            db.add(lesson_content)
            
            print(f"✅ Demo user 'demo@sarathi.app' seeded successfully. (User ID: {demo_user.id})")

if __name__ == "__main__":
    asyncio.run(seed_demo_user())
