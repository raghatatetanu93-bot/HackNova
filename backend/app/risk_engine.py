"""Module F: Explainable Risk Scoring Engine.
Computes four orthogonal indicators (Prompt, Source, Intent Drift, Action Impact)
along with clear contributing factors. Never overrides hard security policy.
"""

from typing import List, Dict, Any
from backend.app.schemas import RiskIndicator
from backend.app.evidence import RuleFinding
from backend.app.protected_values import ProtectedValueFinding

SOURCE_BASE_RISK = {
    "User Prompt": 20,
    "Uploaded Document": 60,
    "Website Content": 75,
    "Tool Output": 70
}

def calculate_risk_scores(
    source_type: str,
    rule_findings: List[RuleFinding],
    protected_findings: List[ProtectedValueFinding],
    ml_result: Dict[str, Any],
    intent_result: Dict[str, Any],
    transformations: List[str]
) -> RiskIndicator:
    factors: List[str] = []

    # 1. Source Risk (0-100)
    source_risk = SOURCE_BASE_RISK.get(source_type, 50)
    if source_type in ["Uploaded Document", "Website Content", "Tool Output"]:
        factors.append(f"Source provenance '{source_type}' lacks instruction authority (baseline risk {source_risk}/100)")
    else:
        factors.append(f"Source '{source_type}' has direct user provenance (baseline risk {source_risk}/100)")

    # 2. Prompt Risk (0-100)
    prompt_risk = 5
    ml_prob = ml_result.get("attack_probability", 0.0)
    ml_status = ml_result.get("status", "ready")

    if ml_status == "degraded":
        prompt_risk += 30
        factors.append("ML detector in degraded mode (increased baseline caution +30)")
    else:
        prompt_risk += int(ml_prob * 40)
        if ml_prob > 0.65:
            factors.append(f"ML classifier flagged high attack probability ({ml_prob*100:.1f}%)")

    # Add for deterministic rule severity
    for rf in rule_findings:
        if rf.severity == "critical":
            prompt_risk += 45
            factors.append(f"Critical rule violation: {rf.name} ({rf.rule_id})")
        elif rf.severity == "high":
            prompt_risk += 30
            factors.append(f"High-severity rule match: {rf.name} ({rf.rule_id})")
        elif rf.severity == "medium":
            prompt_risk += 15

    # Add for obfuscation transformations
    if any("decoded" in t for t in transformations):
        prompt_risk += 25
        factors.append("Detected and decoded obfuscated payloads (Base64/Hex)")

    prompt_risk = min(100, max(0, prompt_risk))

    # 3. Intent Drift Risk (0-100)
    intent_drift_risk = intent_result.get("drift_score", 0)
    if intent_result.get("mismatch_detected"):
        factors.append(f"Intent drift detected: Content aims for '{intent_result.get('content_intent')}' vs task '{intent_result.get('task_intent')}'")

    # 4. Action Impact (0-100)
    action_impact = 10
    has_exfil = any(pf.is_exfiltration_request for pf in protected_findings) or any(rf.rule_id in ["RULE-EXF-004", "RULE-SEC-003"] for rf in rule_findings)
    has_pol_tamper = any(rf.rule_id == "RULE-POL-005" for rf in rule_findings)
    has_token_leak = len(protected_findings) > 0

    if has_token_leak:
        action_impact += 40
        factors.append("Contains literal/encoded protected system token values")
    if has_exfil:
        action_impact += 40
        factors.append("Includes instructions to transmit data to external destination")
    if has_pol_tamper:
        action_impact += 45
        factors.append("Attempts to tamper with security firewall policy")

    action_impact = min(100, max(0, action_impact))

    # Combined priority score (weighted heuristic)
    combined = int((prompt_risk * 0.35) + (source_risk * 0.20) + (intent_drift_risk * 0.20) + (action_impact * 0.25))
    combined = min(100, max(0, combined))

    return RiskIndicator(
        prompt_risk=prompt_risk,
        source_risk=source_risk,
        intent_drift_risk=intent_drift_risk,
        action_impact=action_impact,
        combined_priority=combined,
        factors=factors
    )
