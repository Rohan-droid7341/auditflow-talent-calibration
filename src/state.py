from typing import TypedDict, List, Dict, Any, Optional

class CandidateProfile(TypedDict, total=False):
    id: str
    name: str
    university: str
    degree: str
    gpa: float
    grad_year: int
    target_role: str
    skills: List[Dict[str, Any]]
    projects: List[Dict[str, Any]]
    assessments: List[Dict[str, Any]]
    experience: List[Dict[str, Any]]

class RequisitionCriteria(TypedDict, total=False):
    role_title: str
    minimum_qualifications: List[str]
    preferred_qualifications: List[str]
    technical_discovery_focus: List[str]
    scoring_weights: Dict[str, float]

class CritiqueFeedback(TypedDict, total=False):
    status: str  # "PASS" or "REVISE"
    iteration: int
    unsupported_claims: List[str]
    reasoning: str

class CalibrationState(TypedDict, total=False):
    # Inputs
    candidate_id: str
    raw_job_description: str
    
    # Structured & Unstructured Extraction
    parsed_req: RequisitionCriteria
    structured_profile: CandidateProfile
    unstructured_evidence: List[Dict[str, Any]]
    
    # Deliverables
    match_score: float
    qualification_breakdown: Dict[str, Any]
    discovery_rubric: List[Dict[str, Any]]
    synthesis_draft: str
    
    # Self-reflection tracking
    critique: CritiqueFeedback
    revision_count: int
    
    # Telemetry
    telemetry: Dict[str, Any]
    status_log: List[str]
