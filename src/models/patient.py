from pydantic import BaseModel, Field

class Medication(BaseModel):
    """A single medication the patient is currently taking."""
    name: str = Field(description="Generic drug name (e.g., 'Metformin', not brand names)")
    dosage: str | None = Field(default=None, description="Dosage amount (e.g., '1000mg')")
    frequency: str | None = Field(default=None, description="How often taken (e.g., 'BID', 'once daily')")
    route: str | None = Field(default=None, description="Administration route (e.g., 'oral', 'IV')")

class LabResult(BaseModel):
    """A single lab test result."""
    test_name: str = Field(description="Name of the lab test (e.g., 'HbA1c', 'Creatinine')")
    value: str = Field(description="Result value with units (e.g., '7.2%', '1.8 mg/dL')")
    is_abnormal: bool | None = Field(default=None, description="Whether this result is outside normal range")
    
    
class PatientProfile(BaseModel):
    """Structured patient profile — the Intake Agent's output contract.
    Every field the downstream agents need is defined here.
    The Intake Agent must populate this from unstructured clinical text.
    """
    name: str | None = Field(default=None, description="Patient name if mentioned")
    age: int | None = Field(default=None, description="Patient age in years")
    sex: str | None = Field(default=None, description="Patient sex (e.g., 'Male', 'Female')")
    conditions: list[str] = Field(
        default_factory=list,
        description="Active medical conditions/diagnoses (e.g., ['Type 2 Diabetes', 'Hypertension'])",
    )
    symptoms: list[str] = Field(
        default_factory=list,
        description="Current symptoms the patient reports (e.g., ['dizziness', 'fatigue'])",
    )
    medications: list[Medication] = Field(
        default_factory=list,
        description="Current medication list with dosage details",
    )
    allergies: list[str] = Field(
        default_factory=list,
        description="Known drug or other allergies",
    )
    lab_results: list[LabResult] = Field(
        default_factory=list,
        description="Recent laboratory test results",
    )
    medical_history: list[str] = Field(
        default_factory=list,
        description="Relevant past medical history items",
    )