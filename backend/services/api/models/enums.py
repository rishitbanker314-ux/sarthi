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
