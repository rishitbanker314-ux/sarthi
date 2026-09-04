import asyncio
from services.agents.tutor import TutorAgent
from services.api.config import get_settings

async def main():
    agent = TutorAgent()
    lesson_draft = {
        "title": "Introduction to Python",
        "objective": "Understand basic variables and print statements.",
        "concept_ids": [],
        "est_minutes": 5
    }
    profile = {
        "prior_knowledge": {"python": "none"},
        "pace": "standard",
        "representation_pref": "concrete_first",
        "scaffolding_pref": "guided_discovery",
        "depth_pref": "breadth_survey",
        "motivation": "curiosity",
        "session_minutes": 5,
        "language": "en",
        "accessibility": {}
    }
    
    settings = get_settings()
    settings.demo_mode = False
    
    draft = await agent.generate_lesson(lesson_draft, profile)
    print(draft.model_dump_json(indent=2))

if __name__ == "__main__":
    asyncio.run(main())
