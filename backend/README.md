# PromptShield X — Backend Security Engine

Adaptive, Trust-Aware Dual-Boundary AI Security Gateway built with Python, FastAPI, scikit-learn, and SQLite.

---

## 1. System Architecture

PromptShield X implements an enterprise dual-boundary defense model:
1. **Ingestion Boundary**: Intercepts, normalizes, detects, and sanitizes untrusted prompt content before it can reach downstream AI models.
2. **Egress Boundary (Action Firewall)**: Intercepts and validates proposed tool execution parameters before external network actions or database queries can execute.

```
                      ┌────────────────────────────────────────┐
                      │            Incoming Request            │
                      └──────────────────┬─────────────────────┘
                                         ▼
                      ┌────────────────────────────────────────┐
                      │    Module B: Text Normalization        │
                      │    (NFKC, Whitespace, Base64/Hex)      │
                      └──────────────────┬─────────────────────┘
                                         ▼
                      ┌────────────────────────────────────────┐
                      │      Module C: Hybrid Detection        │
                      │  ┌─────────────────┬─────────────────┐ │
                      │  │ Deterministic   │ Local Scikit-   │ │
                      │  │ Rule Engine     │ Learn Classifier│ │
                      │  └─────────────────┴─────────────────┘ │
                      └──────────────────┬─────────────────────┘
                                         ▼
                      ┌────────────────────────────────────────┐
                      │  Module D: Protected Values Detection  │
                      │  (Credentials, System Tokens, Whitelist│
                      └──────────────────┬─────────────────────┘
                                         ▼
                      ┌────────────────────────────────────────┐
                      │    Module E: Intent Drift Analysis     │
                      │   (Task Intent vs. Content Intent)     │
                      └──────────────────┬─────────────────────┘
                                         ▼
                      ┌────────────────────────────────────────┐
                      │   Module F: Explainable Risk Engine    │
                      │   (Prompt, Source, Drift, Action)      │
                      └──────────────────┬─────────────────────┘
                                         ▼
                      ┌────────────────────────────────────────┐
                      │    Module H: Policy Engine Precedence  │
                      │    ALLOW / BLOCK / SANITIZE / ESCALATE │
                      └──────────────────┬─────────────────────┘
                                         ▼
          ┌──────────────────────────────┼──────────────────────────────┐
          ▼                              ▼                              ▼
    [Decision: ALLOW]           [Decision: SANITIZE]           [Decision: BLOCK]
          │                              │                              │
          │                     Module I: Surgical              Prohibit Forwarding
          │                     Span Excision & Pass 2          Log SecOps Incident
          │                     Reinspection Pass                       │
          │                              │                              ▼
          └──────────────────────────────┼─────────────────────► [Authority Portal]
                                         ▼
                      ┌────────────────────────────────────────┐
                      │     Permitted Content Stored in DB     │
                      └──────────────────┬─────────────────────┘
                                         ▼
                      ┌────────────────────────────────────────┐
                      │   Module J: Independent Action Firewall│
                      │   - Tool registration validation       │
                      │   - Parameter credential scanning      │
                      │   - Destination whitelist checking     │
                      └──────────────────┬─────────────────────┘
                                         ▼
                               [Authorized Action]
```

---

## 2. Directory Structure

```
backend/
├── app/
│   ├── action_firewall.py     # Module J: Independent outbound tool firewall
│   ├── api.py                 # FastAPI routing and request endpoints
│   ├── detector.py            # Module C: Scikit-learn offline ML classifier
│   ├── evidence.py            # Structured telemetry and finding models
│   ├── forwarding.py          # Module K: Controlled assistant execution
│   ├── gemini_verifier.py     # Module G: On-demand Cloud AI verifier
│   ├── intent_engine.py       # Module E: Objective divergence detection
│   ├── main.py                # Application entry point and CORS configuration
│   ├── normalization.py       # Module B: Unicode & multi-format decoding
│   ├── pipeline.py            # Central security orchestration pipeline
│   ├── policy_engine.py       # Module H: Deterministic policy precedence
│   ├── protected_values.py    # Module D: Token disclosure & exfiltration defense
│   ├── review.py              # Module L: Human review authorization
│   ├── risk_engine.py         # Module F: Multi-dimensional risk scoring
│   ├── rules.py               # Module C: Deterministic lexical patterns
│   ├── sanitizer.py           # Module I: Surgical span excision
│   ├── schemas.py             # Pydantic data contracts and models
│   └── storage.py             # SQLite persistence and audit log management
├── config/
│   └── protected_values.json  # Configured credentials, authorized & unauthorized domains
├── data/
│   ├── evaluation_data.json   # Held-out evaluation corpus (20 cases)
│   ├── test_documents.json    # Standardized test document corpus (30 documents)
│   └── training_data.json     # Balanced classifier training dataset (120 samples)
├── models/
│   ├── classifier.joblib      # Serialized scikit-learn TF-IDF + LogisticRegression pipeline
│   └── metadata.json          # Model version, sample counts, and training metrics
├── runtime/
│   └── promptshield.db        # SQLite persistent database
├── scripts/
│   ├── evaluate.py            # Empirical benchmark runner
│   ├── prepare_dataset.py     # Training and evaluation data generator
│   ├── seed_demo.py           # Database seeder for baseline policies
│   ├── train_model.py         # Offline classifier training pipeline
│   └── verify_demos.py        # Scenario verification integration script
└── tests/
    ├── test_action_firewall.py     # Egress action firewall tests
    ├── test_api.py                 # FastAPI endpoint integration tests
    ├── test_authority.py           # Authority Portal and incident tests
    ├── test_detection.py           # Rule and regex detection tests
    ├── test_gemini.py              # Cloud AI verification tests
    ├── test_malicious_documents.py # 30-document corpus verification suite
    ├── test_pipeline.py            # Full pipeline orchestration tests
    ├── test_policy.py              # Policy engine precedence tests
    └── test_sanitizer.py           # Surgical sanitization and reinspection tests
```

---

## 3. Core Modules

| Module | Responsibility | Key Invariant |
| :--- | :--- | :--- |
| **Module B: Normalization** | Unicode NFKC folding, whitespace compression, Base64/Hex decoding | Decodes concealed payloads up to bounded byte limits |
| **Module C: Hybrid Detection** | Deterministic regex patterns + TF-IDF Logistic Regression | Contextual exemption for academic quotation; ML never permits alone |
| **Module D: Data Protection** | Protected token detection (`DEMO_INTERNAL_TOKEN_4821`), outbound exfiltration | Hard invariant: Protected token matches cannot be bypassed by human review |
| **Module E: Intent Drift** | Semantic divergence between user task and content objective | Detects unauthorized pivots from benign tasks to extraction |
| **Module F: Risk Scoring** | Computes Prompt (0-100), Source (0-100), Drift (0-100), Action Impact (0-100) | Orthogonal scoring providing human-explainable contributing factors |
| **Module H: Policy Engine** | Evaluates rule precedence (`BLOCK` > `SANITIZE` > `ESCALATE` > `ALLOW`) | Hard rules strictly override soft rules and human approvals |
| **Module I: Sanitization** | Surgically excises offending instruction spans from documents | Mandatory reinspection pass required before forwarding is authorized |
| **Module J: Action Firewall** | Validates proposed tool actions (`tool_name`, destination, arguments) | Intercepts leaks even if an injection bypassed prior layers |
| **Module L: SecOps Escalation**| Tracks employee identity, workstation, and complete raw prompt dossier | Automatically seals malicious prompts into SecOps incident queue |

---

## 4. API Endpoints

### Inspection & Enforcement
- `POST /inspect`: Runs the complete dual-boundary inspection pipeline.
- `POST /actions/check`: Intercepts and validates proposed AI tool execution.
- `POST /assistant/run`: Executes simulated AI assistant strictly using database-stored permitted content.

### Documents & Policies
- `GET /test-documents`: Returns the 30-file test corpus of real-world security vectors.
- `GET /policies`: Retrieves active policy rules and operational thresholds.
- `PUT /policies`: Updates configurable security thresholds.

### Authority Portal & Incidents
- `GET /incidents`: Lists security incidents transferred for higher authority investigation.
- `POST /incidents/escalate`: Dispatches a sealed incident dossier with employee identity metadata.
- `PATCH /incidents/{incident_id}`: Updates incident triage status and adds investigator notes.
- `GET /authority/prompts`: Returns comprehensive prompt oversight feed with employee provenance.
- `GET /authority/stats`: Computes monitored department count and threat volume statistics.

### Evaluation & Auditing
- `GET /evaluation/latest`: Returns the most recent empirical benchmark evaluation.
- `POST /evaluation/run`: Triggers immediate re-evaluation across held-out datasets.
- `GET /history`: Lists past inspections with filtering by decision and search query.
- `POST /review`: Submits human approval or rejection for escalated inspections.

### Cloud AI Verification
- `POST /gemini/verify`: Consults Google Gemini API for verification on borderline prompts.
- `GET /gemini/config`: Returns masked API key configuration status.
- `POST /gemini/config`: Updates Gemini API key in local configuration.

---

## 5. Local Setup & Execution

### Prerequisites
- Python 3.11+
- Virtual environment recommended (`venv`)

### Installation

```bash
# From repository root
pip install -r requirements.txt
# Or install core dependencies directly:
pip install fastapi uvicorn pydantic scikit-learn joblib pytest
```

### Running the API Server

```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

Interactive API documentation (Swagger UI) is available at `http://127.0.0.1:8000/docs`.

### Running Tests

```bash
# Execute entire test suite (all 67 tests)
$env:PYTHONPATH="."
python -m pytest backend/tests/ -v
```

### Running Model Training & Evaluation

```bash
# Re-train offline classifier
python backend/scripts/train_model.py

# Run benchmark evaluation
python backend/scripts/evaluate.py
```
