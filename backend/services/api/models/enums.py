import enum

class Pace(str, enum.Enum):
    deliberate = "deliberate"
    standard = "standard"
    fast = "fast"

class RepresentationPref(str, enum.Enum):
    concrete_first = "concrete_first"
    abstract_first = "abstract_first"

class ScaffoldingPref(str, enum.Enum):
    worked_examples = "worked_examples"
    guided_discovery = "guided_discovery"

class DepthPref(str, enum.Enum):
    breadth_survey = "breadth_survey"
    depth_mastery = "depth_mastery"

class Motivation(str, enum.Enum):
    exam = "exam"
    career = "career"
    curiosity = "curiosity"
    project = "project"

class DiagnosticStatus(str, enum.Enum):
    started = "started"
    completed = "completed"
    abandoned = "abandoned"

class JobStatus(str, enum.Enum):
    queued = "queued"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"

class JobKind(str, enum.Enum):
    plan_generation = "plan_generation"
    replan = "replan"

class SignalType(str, enum.Enum):
    checkpoint_score = "checkpoint_score"
    confusion_flag = "confusion_flag"
    time_on_block = "time_on_block"
    hint_requested = "hint_requested"
    retry = "retry"
    inline_check_failed = "inline_check_failed"
    skip = "skip"
    session_abandon = "session_abandon"
    revisit = "revisit"

class MessageRole(str, enum.Enum):
    user = "user"
    assistant = "assistant"

class AdaptationTrigger(str, enum.Enum):
    struggling = "struggling"
    stuck = "stuck"
    racing = "racing"
    stalled = "stalled"
    decaying = "decaying"

class AdaptationAction(str, enum.Enum):
    insert_prerequisite = "insert_prerequisite"
    slow_pace = "slow_pace"
    reexplain_concept = "reexplain_concept"
    compress_forward = "compress_forward"
    reorder = "reorder"
    extend_timeline = "extend_timeline"
    no_op = "no_op"
