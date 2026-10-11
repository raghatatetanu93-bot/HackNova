"""FastAPI router and endpoints for PromptShield X."""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any

from backend.app.schemas import (
    InspectRequest, InspectResponse,
    ActionCheckRequest, ActionCheckResponse,
    AssistantRunRequest, AssistantRunResponse,
    ReviewActionRequest, PolicyUpdateRequest,
    PolicyConfigResponse, PolicyItem
)
from backend.app.pipeline import run_inspection_pipeline
from backend.app.action_firewall import check_action
from backend.app.forwarding import run_assistant_for_inspection
from backend.app.review import process_review, get_pending_reviews
from backend.app.policy_engine import get_active_policies_list, get_active_settings
from backend.app.storage import (
    list_inspections, get_inspection,
    update_policy_settings, get_latest_evaluation
)

router = APIRouter()

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "PromptShield X Security Gateway",
        "engine": "offline-hybrid",
        "version": "2.1.0"
    }

@router.post("/inspect", response_model=InspectResponse)
def inspect_content(req: InspectRequest):
    try:
        return run_inspection_pipeline(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inspection pipeline failure: {str(e)}")

@router.get("/policies", response_model=PolicyConfigResponse)
def get_policies_endpoint():
    policies = get_active_policies_list()
    settings = get_active_settings()
    return PolicyConfigResponse(
        version=settings.get("policy_version", "v2.1"),
        last_updated="2026-10-11T00:00:00Z",
        policies=[PolicyItem(**p) for p in policies],
        settings=settings
    )

@router.put("/policies")
def update_policies_endpoint(req: PolicyUpdateRequest):
    # Untrusted content must never be able to modify policies
    try:
        update_policy_settings(req.settings)
        return {
            "status": "success",
            "message": "Security policy settings successfully updated.",
            "version": req.version
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update policies: {str(e)}")

@router.get("/history")
def get_history_endpoint(
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = None,
    decision: Optional[str] = None
):
    return list_inspections(limit=limit, search=search, decision_filter=decision)

@router.get("/inspections/{inspection_id}")
def get_inspection_endpoint(inspection_id: str):
    record = get_inspection(inspection_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Inspection ID '{inspection_id}' not found.")
    return record

@router.get("/reviews")
def get_reviews_endpoint():
    return get_pending_reviews()

@router.post("/review")
def review_action_endpoint(req: ReviewActionRequest):
    try:
        result = process_review(
            inspection_id=req.inspection_id,
            reviewer=req.reviewer,
            action=req.action,
            notes=req.notes or ""
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/assistant/run", response_model=AssistantRunResponse)
def assistant_run_endpoint(req: AssistantRunRequest):
    result = run_assistant_for_inspection(req.inspection_id, req.task)
    return AssistantRunResponse(**result)

@router.post("/actions/check", response_model=ActionCheckResponse)
def actions_check_endpoint(req: ActionCheckRequest):
    result = check_action(
        tool_name=req.tool_name,
        tool_args=req.tool_args,
        inspection_id=req.inspection_id,
        authorized_task=req.authorized_task,
        target_destination=req.target_destination
    )
    return ActionCheckResponse(**result)

@router.get("/evaluation/latest")
def get_evaluation_endpoint():
    res = get_latest_evaluation()
    if not res:
        return {"status": "none", "message": "No evaluation results available."}
    return res
