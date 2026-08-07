from enum import Enum

from pydantic import BaseModel, Field


class Severity(str, Enum):
    """Drug interaction severity levels, matching DDInter 2.0 classification."""

    MAJOR = "major"
    MODERATE = "moderate"
    MINOR = "minor"
    UNKNOWN = "unknown"


class DrugInteraction(BaseModel):
    """A single drug-drug interaction identified by the DDI Agent.

    Each interaction is backed by data from DDInter 2.0 or the local
    fallback database — never from the LLM's parametric memory.
    """

    drug_a: str = Field(description="First drug in the interaction pair")
    drug_b: str = Field(description="Second drug in the interaction pair")
    severity: Severity = Field(description="Interaction severity: major, moderate, minor, or unknown")
    mechanism: str | None = Field(
        default=None,
        description="Pharmacological mechanism of the interaction (e.g., 'CYP2C9 inhibition')",
    )
    clinical_effect: str | None = Field(
        default=None,
        description="What happens clinically (e.g., 'Increased risk of bleeding')",
    )
    management: str | None = Field(
        default=None,
        description="Recommended management (e.g., 'Monitor INR more frequently')",
    )
    source: str = Field(
        description="Data source for this interaction (e.g., 'DDInter 2.0', 'local_fallback')"
    )


class DDIResult(BaseModel):
    """Complete output of the DDI Agent — all interactions found + overall risk."""

    interactions: list[DrugInteraction] = Field(
        default_factory=list,
        description="All drug-drug interactions detected",
    )
    risk_level: str = Field(
        default="low",
        description="Overall risk level: 'low', 'moderate', 'high', or 'critical'",
    )
    medications_checked: list[str] = Field(
        default_factory=list,
        description="List of all medication names that were checked (for audit trail)",
    )
    normalization_failures: list[str] = Field(
        default_factory=list,
        description="Drug names that could not be normalized via RxNorm (transparency)",
    )
