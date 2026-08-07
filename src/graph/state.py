from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph.message import add_messages

from src.models.guidelines import GuidelineMatch
from src.models.interactions import DrugInteraction
from src.models.patient import PatientProfile
from src.models.report import ClinicalReport

class MediAgentState(TypedDict):
    # -- LangGraph conversation tracking --
    messages: Annotated[list, add_messages]
    # -- Input --
    raw_case: str
    # -- Intake Agent output --
    patient_profile: PatientProfile | None
    # -- DDI Agent output --
    drug_interactions: list[DrugInteraction]
    risk_level: str | None  # "low" | "moderate" | "high" | "critical"
    medications_checked: list[str]
    normalization_failures: list[str]
    # -- Guidelines RAG Agent output --
    guideline_matches: list[GuidelineMatch]
    # -- Synthesis Agent output --
    clinical_report: ClinicalReport | None
    # -- System-wide error tracking --
    agent_errors: list[str]