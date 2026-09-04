import json
from services.agents.base import run
from services.agents.schemas import DiagnosticResponse, NextQuestion, ProfileDraft, AccessibilityOptions

def _diagnostician_fallback(transcript_len: int) -> DiagnosticResponse:
    """
    Fixed bank of 8 questions to fallback on if the agent fails or times out.
    Includes 3 micro-problems to satisfy requirements.
    """
    if transcript_len == 0:
        return DiagnosticResponse(
            complete=False,
            questions=[NextQuestion(
                question_text="Welcome! What brings you to learn with us today? (e.g. preparing for an exam, career switch, general curiosity)",
                question_type="single_choice",
                options=["exam", "career", "curiosity", "project"]
            )]
        )
    elif transcript_len == 1:
        return DiagnosticResponse(
            complete=False,
            questions=[NextQuestion(
                question_text="How much time can you dedicate per session?",
                question_type="single_choice",
                options=["15 minutes", "30 minutes", "60 minutes"]
            )]
        )
    elif transcript_len == 2:
        return DiagnosticResponse(
            complete=False,
            questions=[NextQuestion(
                question_text="When learning a new topic, do you prefer to start with a concrete example or the abstract rule?",
                question_type="single_choice",
                options=["Example first", "Rule first"]
            )]
        )
    elif transcript_len == 3:
        return DiagnosticResponse(
            complete=False,
            questions=[NextQuestion(
                question_text="Do you prefer seeing fully worked examples before trying yourself, or guided discovery?",
                question_type="single_choice",
                options=["Worked examples", "Guided discovery"]
            )]
        )
    elif transcript_len == 4:
        return DiagnosticResponse(
            complete=False,
            questions=[NextQuestion(
                question_text="Do you prefer a broad survey of the material or in-depth mastery?",
                question_type="single_choice",
                options=["Broad survey", "In-depth mastery"]
            )]
        )
    elif transcript_len == 5:
        return DiagnosticResponse(
            complete=False,
            questions=[NextQuestion(
                question_text="Micro-problem 1: What does `print(type([]))` output in Python?",
                question_type="micro_problem"
            )]
        )
    elif transcript_len == 6:
        return DiagnosticResponse(
            complete=False,
            questions=[NextQuestion(
                question_text="Micro-problem 2: If x = 5 and y = 2, what is the value of `x // y` in Python?",
                question_type="micro_problem"
            )]
        )
    elif transcript_len == 7:
        return DiagnosticResponse(
            complete=False,
            questions=[NextQuestion(
                question_text="Micro-problem 3: Write a short snippet to add 'apple' to the list `fruits = []`.",
                question_type="micro_problem"
            )]
        )
    
    # Derivation for the default fallback profile
    return DiagnosticResponse(
        complete=True,
        profile_draft=ProfileDraft(
            prior_knowledge="shaky",
            pace="standard",
            representation_pref="concrete_first",
            scaffolding_pref="worked_examples",
            depth_pref="breadth_survey",
            motivation="curiosity",
            session_minutes=30,
            language="en",
            accessibility=AccessibilityOptions()
        )
    )

async def get_next_action(transcript: list[dict]) -> DiagnosticResponse:
    """
    Executes the Diagnostician agent.
    """
    transcript_str = json.dumps(transcript, indent=2)
    
        # Fallback factory closure capturing transcript length
    def fallback_factory():
        # transcript is a list of interactions (e.g. dicts containing agent and learner keys)
        transcript_len = len(transcript)
        return _diagnostician_fallback(transcript_len)

    from services.api.config import get_settings
    settings = get_settings()

    response = await run(
        agent_name="diagnostician",
        prompt_template_path="diagnostician.md",
        context={"transcript": transcript_str},
        output_model=DiagnosticResponse,
        model_tier=settings.get_agent_tier("diagnostician"),
        fallback_factory=fallback_factory
    )

    return response
