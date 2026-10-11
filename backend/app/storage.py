"""Local SQLite storage module for PromptShield X using standard sqlite3."""

import os
import json
import sqlite3
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "runtime")
DB_PATH = os.path.join(DB_DIR, "promptshield.db")

def get_connection() -> sqlite3.Connection:
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inspections (
        id TEXT PRIMARY KEY,
        task TEXT NOT NULL,
        content TEXT NOT NULL,
        raw_content TEXT NOT NULL,
        source_type TEXT NOT NULL,
        decision TEXT NOT NULL,
        summary_explanation TEXT NOT NULL,
        permitted_content TEXT,
        sanitized_content TEXT,
        forwarding_permitted INTEGER NOT NULL,
        triggered_policy TEXT,
        triggered_rules TEXT,
        findings TEXT,
        risk_scores TEXT,
        normalization TEXT,
        ml_result TEXT,
        intent_analysis TEXT,
        decision_steps TEXT,
        policy_version TEXT,
        created_at TEXT NOT NULL,
        review_status TEXT DEFAULT 'none'
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS policies (
        id TEXT PRIMARY KEY,
        version TEXT NOT NULL,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        rule_id TEXT NOT NULL,
        action TEXT NOT NULL,
        priority INTEGER NOT NULL,
        is_hard_rule INTEGER NOT NULL,
        enabled INTEGER NOT NULL,
        description TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS policy_settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id TEXT PRIMARY KEY,
        inspection_id TEXT NOT NULL,
        reviewer TEXT NOT NULL,
        action TEXT NOT NULL,
        notes TEXT,
        timestamp TEXT NOT NULL,
        FOREIGN KEY(inspection_id) REFERENCES inspections(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS evaluations (
        id TEXT PRIMARY KEY,
        metrics_json TEXT NOT NULL,
        timestamp TEXT NOT NULL
    );
    """)

    conn.commit()
    conn.close()

def save_inspection(inspection_data: Dict[str, Any]) -> str:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR REPLACE INTO inspections (
        id, task, content, raw_content, source_type, decision,
        summary_explanation, permitted_content, sanitized_content,
        forwarding_permitted, triggered_policy, triggered_rules,
        findings, risk_scores, normalization, ml_result,
        intent_analysis, decision_steps, policy_version, created_at, review_status
    ) VALUES (
        ?, ?, ?, ?, ?, ?,
        ?, ?, ?,
        ?, ?, ?,
        ?, ?, ?, ?,
        ?, ?, ?, ?, ?
    )
    """, (
        inspection_data["inspection_id"],
        inspection_data["task"],
        inspection_data.get("masked_content", inspection_data["original_content"]),
        inspection_data["original_content"],
        inspection_data["source_type"],
        inspection_data["decision"],
        inspection_data["summary_explanation"],
        inspection_data.get("permitted_content"),
        inspection_data.get("sanitized_content"),
        1 if inspection_data["forwarding_permitted"] else 0,
        inspection_data["triggered_policy"],
        json.dumps(inspection_data.get("triggered_rules", [])),
        json.dumps([f.model_dump() if hasattr(f, 'model_dump') else f for f in inspection_data.get("findings", [])]),
        json.dumps(inspection_data["risk_scores"].model_dump() if hasattr(inspection_data["risk_scores"], 'model_dump') else inspection_data["risk_scores"]),
        json.dumps(inspection_data["normalization"].model_dump() if hasattr(inspection_data["normalization"], 'model_dump') else inspection_data["normalization"]),
        json.dumps(inspection_data["ml_result"].model_dump() if hasattr(inspection_data["ml_result"], 'model_dump') else inspection_data["ml_result"]),
        json.dumps(inspection_data["intent_analysis"].model_dump() if hasattr(inspection_data["intent_analysis"], 'model_dump') else inspection_data["intent_analysis"]),
        json.dumps([s.model_dump() if hasattr(s, 'model_dump') else s for s in inspection_data.get("decision_steps", [])]),
        inspection_data.get("policy_version", "v2.1"),
        inspection_data.get("created_at", datetime.now(timezone.utc).isoformat()),
        inspection_data.get("review_status", "none")
    ))

    conn.commit()
    conn.close()
    return inspection_data["inspection_id"]

def get_inspection(inspection_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inspections WHERE id = ?", (inspection_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "inspection_id": row["id"],
        "task": row["task"],
        "content": row["content"],
        "raw_content": row["raw_content"],
        "source_type": row["source_type"],
        "decision": row["decision"],
        "summary_explanation": row["summary_explanation"],
        "permitted_content": row["permitted_content"],
        "sanitized_content": row["sanitized_content"],
        "forwarding_permitted": bool(row["forwarding_permitted"]),
        "triggered_policy": row["triggered_policy"],
        "triggered_rules": json.loads(row["triggered_rules"] or "[]"),
        "findings": json.loads(row["findings"] or "[]"),
        "risk_scores": json.loads(row["risk_scores"] or "{}"),
        "normalization": json.loads(row["normalization"] or "{}"),
        "ml_result": json.loads(row["ml_result"] or "{}"),
        "intent_analysis": json.loads(row["intent_analysis"] or "{}"),
        "decision_steps": json.loads(row["decision_steps"] or "[]"),
        "policy_version": row["policy_version"],
        "created_at": row["created_at"],
        "review_status": row["review_status"]
    }

def list_inspections(limit: int = 50, search: Optional[str] = None, decision_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT id, task, source_type, decision, summary_explanation, forwarding_permitted, triggered_rules, risk_scores, created_at, review_status FROM inspections WHERE 1=1"
    params = []

    if decision_filter and decision_filter.upper() != "ALL":
        query += " AND decision = ?"
        params.append(decision_filter.upper())

    if search:
        query += " AND (task LIKE ? OR summary_explanation LIKE ? OR id LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term])

    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    results = []
    for r in rows:
        risk = json.loads(r["risk_scores"] or "{}")
        rules = json.loads(r["triggered_rules"] or "[]")
        results.append({
            "inspection_id": r["id"],
            "task": r["task"],
            "source_type": r["source_type"],
            "decision": r["decision"],
            "summary_explanation": r["summary_explanation"],
            "forwarding_permitted": bool(r["forwarding_permitted"]),
            "triggered_rules": rules,
            "risk_scores": risk,
            "created_at": r["created_at"],
            "review_status": r["review_status"]
        })
    return results

def get_policies() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM policies ORDER BY priority ASC")
    rows = cursor.fetchall()
    conn.close()

    return [{
        "id": r["id"],
        "version": r["version"],
        "name": r["name"],
        "category": r["category"],
        "rule_id": r["rule_id"],
        "action": r["action"],
        "priority": r["priority"],
        "is_hard_rule": bool(r["is_hard_rule"]),
        "enabled": bool(r["enabled"]),
        "description": r["description"]
    } for r in rows]

def get_policy_settings() -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM policy_settings")
    rows = cursor.fetchall()
    conn.close()
    settings = {}
    for r in rows:
        try:
            settings[r["key"]] = json.loads(r["value"])
        except Exception:
            settings[r["key"]] = r["value"]
    return settings

def update_policy_settings(settings: Dict[str, Any]):
    conn = get_connection()
    cursor = conn.cursor()
    for k, v in settings.items():
        val_str = json.dumps(v)
        cursor.execute("INSERT OR REPLACE INTO policy_settings (key, value) VALUES (?, ?)", (k, val_str))
    conn.commit()
    conn.close()

def save_review(review_data: Dict[str, Any]):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO reviews (id, inspection_id, reviewer, action, notes, timestamp)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        review_data["id"],
        review_data["inspection_id"],
        review_data["reviewer"],
        review_data["action"],
        review_data.get("notes", ""),
        review_data["timestamp"]
    ))

    new_status = "approved" if review_data["action"] == "APPROVE" else "rejected"
    new_decision = "ALLOW" if review_data["action"] == "APPROVE" else "BLOCK"
    forwarding = 1 if review_data["action"] == "APPROVE" else 0

    cursor.execute("""
    UPDATE inspections
    SET review_status = ?, decision = ?, forwarding_permitted = ?
    WHERE id = ?
    """, (new_status, new_decision, forwarding, review_data["inspection_id"]))

    conn.commit()
    conn.close()

def get_latest_evaluation() -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT metrics_json, timestamp FROM evaluations ORDER BY timestamp DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        return json.loads(row["metrics_json"])
    return None

def save_evaluation(metrics: Dict[str, Any]):
    conn = get_connection()
    cursor = conn.cursor()
    eval_id = f"eval_{int(datetime.now(timezone.utc).timestamp())}"
    cursor.execute("INSERT INTO evaluations (id, metrics_json, timestamp) VALUES (?, ?, ?)", (
        eval_id,
        json.dumps(metrics),
        datetime.now(timezone.utc).isoformat()
    ))
    conn.commit()
    conn.close()
