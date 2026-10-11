"""Unit tests verifying detection and policy enforcement for diverse malicious documents.
Covers poisoned resumes, financial reports, SOC-2 audits, customer support tickets,
invoices, CSV sheets, Kubernetes logs, JSON configs, Python PR reviews, and benign controls.
"""

import json
import os
import pytest
from backend.app.schemas import InspectRequest
from backend.app.pipeline import run_inspection_pipeline
from backend.app.action_firewall import check_action

def load_test_documents():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(base_dir, "data", "test_documents.json")
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

TEST_DOCUMENTS = load_test_documents()

@pytest.mark.parametrize("doc", TEST_DOCUMENTS, ids=[d["id"] for d in TEST_DOCUMENTS])
def test_malicious_document_inspection(doc):
    if doc.get("tool_demo"):
        res = check_action(
            tool_name=doc["tool_name"],
            tool_args=doc["tool_args"],
            authorized_task=doc["task"],
            target_destination=doc["tool_args"]["url"]
        )
        assert res.get("action_allowed") is False
        assert res.get("decision") == "BLOCK"
    else:
        req = InspectRequest(
            task=doc["task"],
            content=doc["content"],
            source_type=doc["source_type"]
        )
        res = run_inspection_pipeline(req)
        assert res.decision == doc["expected_decision"], (
            f"Failed on {doc['id']} ({doc['name']}): "
            f"Expected {doc['expected_decision']}, got {res.decision}. "
            f"Triggered rules: {res.triggered_rules}, policy: {res.triggered_policy}"
        )
