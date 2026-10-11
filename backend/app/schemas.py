"""Pydantic schemas for PromptShield X API contracts."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class SourceTypeEnum:
    USER_PROMPT = "User Prompt"
    UPLOADED_DOCUMENT = "Uploaded Document"
    WEBSITE_CONTENT = "Website Content"
    TOOL_OUTPUT = "Tool Output"

class PolicyDecisionEnum:
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    SANITIZE = "SANITIZE"
    ESCALATE = "ESCALATE"

# --- Request Schemas ---

class InspectRequest(BaseModel):
    task: str = Field(..., description="The legitimate authorized user task", min_length=1)
    content: str = Field(..., description="Incoming content to inspect", min_length=1)
    source_type: str = Field(default="User Prompt", description="Source of content")
    source_metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata e.g. URL or filename")
    inspection_level: Optional[str] = Field(default="adaptive", description="standard, enhanced, deep, or adaptive")
    force_detector_degraded: Optional[bool] = Field(default=False, description="Simulate AI classifier failure for demo")

class ActionCheckRequest(BaseModel):
    inspection_id: Optional[str] = Field(default=None, description="Bound inspection ID")
    tool_name: str = Field(..., description="Name of the tool the AI proposes to execute")
    tool_args: Dict[str, Any] = Field(default_factory=dict, description="Arguments proposed for the tool")
    authorized_task: Optional[str] = Field(default="", description="Original user task context")
    target_destination: Optional[str] = Field(default=None, description="Target URL or domain if external")

class AssistantRunRequest(BaseModel):
    inspection_id: str = Field(..., description="Stored inspection ID to retrieve permitted content")
    task: Optional[str] = Field(default="", description="Task context")

class ReviewActionRequest(BaseModel):
    inspection_id: str = Field(...)
    reviewer: str = Field(default="admin_reviewer")
    action: str = Field(..., description="APPROVE or REJECT")
    notes: Optional[str] = Field(default="")

class PolicyUpdateRequest(BaseModel):
    version: str = Field(default="v2.1")
    settings: Dict[str, Any] = Field(..., description="Key-value security policy toggles and thresholds")

# --- Response Schemas ---

class Finding(BaseModel):
    rule_id: str
    name: str
    category: str
    severity: str  # critical, high, medium, low
    description: str
    offset_start: int
    offset_end: int
    evidence_snippet: str

class RiskIndicator(BaseModel):
    prompt_risk: int = Field(ge=0, le=100)
    source_risk: int = Field(ge=0, le=100)
    intent_drift_risk: int = Field(ge=0, le=100)
    action_impact: int = Field(ge=0, le=100)
    combined_priority: int = Field(ge=0, le=100)
    factors: List[str] = Field(default_factory=list)

class DecisionStep(BaseModel):
    step_number: int
    title: str
    status: str  # pass, alert, blocked, sanitized, held
    explanation: str
    evidence: Optional[str] = None

class NormalizationDetail(BaseModel):
    original_length: int
    normalized_length: int
    transformations_applied: List[str]
    decoded_payloads: List[str] = Field(default_factory=list)

class MLDetectorResult(BaseModel):
    attack_probability: float
    predicted_label: int
    confidence_level: str
    model_version: str
    status: str  # ready, degraded, fallback

class IntentAnalysisResult(BaseModel):
    task_intent: str
    content_intent: str
    mismatch_detected: bool
    drift_score: int
    explanation: str

class InspectResponse(BaseModel):
    inspection_id: str
    decision: str  # ALLOW, BLOCK, SANITIZE, ESCALATE
    summary_explanation: str
    task: str
    source_type: str
    original_content: str
    sanitized_content: Optional[str] = None
    permitted_content: Optional[str] = None
    forwarding_permitted: bool
    triggered_policy: str
    triggered_rules: List[str]
    findings: List[Finding]
    risk_scores: RiskIndicator
    normalization: NormalizationDetail
    ml_result: MLDetectorResult
    intent_analysis: IntentAnalysisResult
    decision_steps: List[DecisionStep]
    policy_version: str
    created_at: str

class ActionCheckResponse(BaseModel):
    action_allowed: bool
    decision: str  # ALLOW or BLOCK
    reason: str
    violating_rule: Optional[str] = None
    firewall_checks: Dict[str, Any]
    target_destination: Optional[str] = None
    timestamp: str

class AssistantRunResponse(BaseModel):
    inspection_id: str
    success: bool
    status: str  # executed, blocked, rejected
    message: str
    executed_content: Optional[str] = None
    assistant_output: Optional[str] = None
    proposed_action: Optional[Dict[str, Any]] = None
    action_firewall_verdict: Optional[ActionCheckResponse] = None

class PolicyItem(BaseModel):
    id: str
    name: str
    category: str
    rule_id: str
    action: str
    priority: int
    is_hard_rule: bool
    enabled: bool
    description: str

class PolicyConfigResponse(BaseModel):
    version: str
    last_updated: str
    policies: List[PolicyItem]
    settings: Dict[str, Any]

class EvaluationMetrics(BaseModel):
    total_cases: int
    attacks_detected: int
    missed_attacks: int
    false_positives: int
    correct_benign: int
    reviews_held: int
    precision: float
    recall: float
    false_positive_rate: float
    f1_score: float
    average_latency_ms: float
    rule_only_metrics: Dict[str, float]
    hybrid_metrics: Dict[str, float]
    test_cases: List[Dict[str, Any]]
    evaluated_at: str
