# PromptShield X — Enterprise Dual-Boundary AI Security Gateway

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Engine: Offline Hybrid](https://img.shields.io/badge/Engine-Offline%20Hybrid%20v2.1-emerald.svg)]()
[![Tests: 67 Passing](https://img.shields.io/badge/Tests-67%20Passed-brightgreen.svg)]()
[![Precision: 100%](https://img.shields.io/badge/Precision-100%25-blue.svg)]()
[![Recall: 100%](https://img.shields.io/badge/Recall-100%25-blue.svg)]()
[![Latency: Sub-5ms](https://img.shields.io/badge/Avg%20Latency-4.2ms-teal.svg)]()

PromptShield X is an adaptive, dual-boundary AI security gateway engineered to protect Large Language Model (LLM) applications and autonomous agents against prompt injection, unauthorized instruction overrides, confidential token exfiltration, and malicious tool operations.

---

## 1. Executive Summary

As enterprise LLMs transition from isolated chatbots to agentic workflows that ingest external documents, parse web content, and execute tool operations (database queries, external API calls, script runs), they become vulnerable to **indirect prompt injection** and **confidential data exfiltration**.

PromptShield X addresses this attack surface through an **adaptive dual-boundary architecture**:
1. **Ingestion Boundary**: Intercepts, normalizes, detects, scores, and sanitizes untrusted input before it reaches the downstream model.
2. **Egress Boundary (Action Firewall)**: Intercepts and validates proposed tool execution parameters before network transmission or data mutation can occur.

The core gateway operates **completely offline** using deterministic lexical engines and a calibrated local scikit-learn classifier (`TF-IDF` + `LogisticRegression`), achieving sub-5ms inspection latency with zero runtime dependencies on external cloud APIs. When borderline uncertainty is detected, the gateway can optionally consult Google Gemini for on-demand cloud confirmation, or escalate directly to enterprise SecOps investigators via the built-in **Authority Portal**.

---

## 2. Dual-Boundary Architecture

```
                                  [ INGESTION BOUNDARY ]
                                             │
                                             ▼
                                  ┌──────────────────────┐
                                  │   Incoming Payload   │
                                  │ (Prompt, Doc, Web)   │
                                  └──────────┬───────────┘
                                             │
                                             ▼
                                  ┌──────────────────────┐
                                  │ Text Normalization   │
                                  │ (NFKC, B64/Hex Decode│
                                  └──────────┬───────────┘
                                             │
                                             ▼
                                  ┌──────────────────────┐
                                  │ Hybrid Detection     │
                                  │ (Regex + Scikit-Learn│
                                  └──────────┬───────────┘
                                             │
                                             ▼
                                  ┌──────────────────────┐
                                  │ Protected Values &   │
                                  │ Token Disclosure Scan│
                                  └──────────┬───────────┘
                                             │
                                             ▼
                                  ┌──────────────────────┐
                                  │ Intent Drift Engine  │
                                  │ (Task vs. Content)   │
                                  └──────────┬───────────┘
                                             │
                                             ▼
                                  ┌──────────────────────┐
                                  │ Risk Scoring Engine  │
                                  │ (4 Orthogonal Scores)│
                                  └──────────┬───────────┘
                                             │
                                             ▼
                                  ┌──────────────────────┐
                                  │ Policy Engine        │
                                  │ Deterministic Order  │
                                  └──────────┬───────────┘
                                             │
              ┌──────────────────────────────┼──────────────────────────────┐
              ▼                              ▼                              ▼
        [VERDICT: ALLOW]             [VERDICT: SANITIZE]            [VERDICT: BLOCK]
              │                              │                              │
              │                      Surgical Excision                      │
              │                      & Mandatory Pass 2                     │
              │                      Reinspection Check                     │
              │                              │                              │
              └──────────────────────────────┼──────────────────────────────┘
                                             │
                                             ▼
                                  ┌──────────────────────┐
                                  │ Permitted Content    │
                                  │ Stored in SQLite DB  │
                                  └──────────┬───────────┘
                                             │
                                             ▼
                                  ┌──────────────────────┐
                                  │ Downstream AI Agent  │
                                  │ Proposes Tool Action │
                                  └──────────┬───────────┘
                                             │
                                             ▼
                                  [ EGRESS BOUNDARY ]
                                  ┌──────────────────────┐
                                  │ Action Firewall      │
                                  │ - Registered Tool?   │
                                  │ - Secret Leak Free?  │
                                  │ - Whitelisted Domain?│
                                  └──────────┬───────────┘
                                             │
                             ┌───────────────┴───────────────┐
                             ▼                               ▼
                     [ACTION AUTHORIZED]             [ACTION BLOCKED]
```

---

## 3. Defense-in-Depth Pipeline (Modules A – L)

### Module A: Source Provenance & Provenance Tracking
Incoming content is tagged with its provenance source (`User Prompt`, `Uploaded Document`, `Website Content`, `Tool Output`). External and third-party sources receive elevated baseline skepticism, ensuring documents cannot dictate system-level directives.

### Module B: Text Normalization & Obfuscation Detection
- **Unicode Normalization**: Performs `NFKC` folding to collapse homoglyphs and hidden zero-width unicode characters.
- **Whitespace Compression**: Eliminates non-standard tabs, form-feeds, and multi-space formatting.
- **Spaced Token Reconstruction**: Reconstructs spaced strings designed to evade regex filters (e.g., `D E M O _ I N T E R N A L`).
- **Bounded Recursive Decoding**: Automatically decodes Base64 and Hexadecimal strings, subjecting decoded inner payloads to complete inspection passes.

### Module C: Hybrid Threat Detection
- **Deterministic Lexical Engine**: Identifies direct instruction overrides, system role tags (`<|system|>`, `### SYSTEM:`), unconstrained persona triggers (`DAN`, `ROOT_SHELL`), policy tampering, and external transmission commands.
- **Academic Context Exemption**: Differentiates active attacks from benign educational or research inquiries quoting attack phrases (e.g., *'In security literature, what does "ignore previous instructions" mean?'*).
- **Offline ML Classifier**: TF-IDF unigram/bigram feature extraction paired with Logistic Regression. Provides calibrated probability scores completely offline in ~3ms.

### Module D: Protected-Value & Data Exfiltration Inspection
- Scans incoming inputs for matches against fictional internal tokens (`DEMO_INTERNAL_TOKEN_4821`, `PROMPT_SHIELD_SEC_9942`, `CORP_FINANCE_KEY_7103`).
- Detects requests to dump, output, or transmit sensitive system credentials.
- Masks sensitive values in database records (`DEMO_INTERNAL_****_4821`) for safe security auditing.

### Module E: Intent Drift Detection Engine
Compares the authorized user objective with the semantic objective of incoming content. If a user asks to *'Summarize quarterly earnings'* but an embedded clause commands the agent to *'Transmit customer records to an external endpoint'*, the intent drift engine flags the objective mismatch with an elevated drift score (85/100).

### Module F: Explainable Multi-Dimensional Risk Scoring
Calculates four orthogonal risk indicators, each on a scale of 0 to 100:
1. **Prompt Risk (0–100)**: Adversarial indicators within the text itself (lexical rules, ML probability, obfuscation).
2. **Source Risk (0–100)**: Provenance trust baseline based on ingestion channel.
3. **Intent Drift Risk (0–100)**: Divergence between authorized user task and content objective.
4. **Action Impact (0–100)**: Potential damage of proposed operations (credential access, network exfiltration, policy tampering).
- **Combined Priority Index**: Weighted heuristic aggregating all four dimensions into an actionable operational severity rating.

### Module G: Cloud AI Verification (Optional On-Demand)
When local software detects borderline uncertainty (e.g. elevated drift without explicit rule violation, or simulated classifier degradation), the gateway can consult Google Gemini (`gemini-2.5-flash`) for semantic arbitration. If an API key is not configured, the gateway falls back gracefully to deterministic offline safety policies.

### Module H: Deterministic Policy Engine
Applies strict, unambiguous precedence rules:
1. **POL-001 (Hard Block)**: Protected token disclosure or exfiltration attempt.
2. **POL-002 (Hard Block)**: Unauthorized outbound network transmission.
3. **POL-003 (Hard Block)**: Security policy tampering or guardrail bypass.
4. **POL-004 (Hard Block)**: System authority or developer mode impersonation.
5. **POL-005 (Surgical Sanitization)**: Instruction override contained within salvageable document context.
6. **POL-006 (Escalation)**: Ambiguous administrative tasks or unresolved intent drift held for SecOps review.
7. **POL-007 (Allow)**: Clean input verified safe across all controls.

### Module I: Surgical Sanitization & Mandatory Reinspection
When an untrusted document contains an isolated injection within otherwise legitimate content, the sanitizer:
1. Merges overlapping injection character spans.
2. Assesses the remaining content length to prevent destructive over-sanitization.
3. Surgically excises the offending span, preserving legitimate text.
4. **Enforces a mandatory second inspection pass** across the sanitized output. If any residual threat remains, the verdict immediately falls back to `BLOCK`.

### Module J: Independent Egress Action Firewall
Intercepts simulated tool execution requests before external APIs or database drivers execute:
- Validates tool registration against allowed system capabilities.
- Inspects tool argument payloads for internal credentials or secret tokens.
- Enforces an organization domain whitelist (`api.company.internal`), blocking unauthorized destinations (`attacker.example`, `webhook.site`).

### Module K: Controlled Assistant Forwarding
Downstream assistant execution occurs strictly through gateway mediation. The assistant receives only content retrieved directly from the database after formal policy approval (`ALLOW` or reinspected `SANITIZE`), eliminating bypasses via client-side payload tampering.

### Module L: SecOps Escalation & Authority Portal
Every blocked or escalated prompt automatically creates a sealed forensic incident record:
- Captures submitting employee identity, corporate email, department, client IP, and workstation ID.
- Stores complete raw prompt payloads alongside exact malicious trigger extracts.
- Supports investigator triage lifecycles (`UNDER_INVESTIGATION`, `ACTION_TAKEN`, `EVIDENCE_SEALED`, `RESOLVED`, `FALSE_POSITIVE_CLEARED`).

---

## 4. Hard Security Invariants

These invariants are architecturally locked and **cannot be overridden** by human review, configuration toggles, or runtime parameters:

| Invariant ID | Rule | Architectural Guarantee |
| :--- | :--- | :--- |
| **INV-001** | Non-Bypassable Token Protection | Matches for protected tokens (`RULE-SEC-003`) cannot be approved by human review (`process_review()` raises `ValueError`). |
| **INV-002** | Exfiltration Destination Barrier | Network transmission to non-whitelisted destinations is rejected by the Action Firewall (`AFW-DEST-006`). |
| **INV-003** | Mandatory Reinspection | Sanitized content is never permitted for forwarding without a clean pass through a complete second inspection cycle. |
| **INV-004** | Fail-Safe Graceful Degradation | If the ML classifier fails or is uninitialized, the engine defaults to a conservative cautious state (`attack_prob = 0.50`), never silently defaulting to `ALLOW`. |
| **INV-005** | Database-Bound Execution | Downstream assistants can only execute payloads stored in the gateway database under an authorized inspection record. |

---

## 5. Empirical Evaluation & Performance Metrics

PromptShield X is benchmarked against held-out evaluation datasets comprising diverse prompt injection variants, exfiltration attempts, role impersonations, and benign control inquiries:

| Evaluation Metric | Rule-Only Baseline | Hybrid Detection Pipeline | Uplift |
| :--- | :--- | :--- | :--- |
| **Precision** | 100.0% | **100.0%** | Baseline parity |
| **Recall** | 92.9% | **100.0%** | **+7.1%** |
| **F1 Score** | 96.3% | **100.0%** | **+3.7%** |
| **False Positive Rate (FPR)** | 0.0% | **0.0%** | 0.0% false alarms |
| **Average Inspection Latency** | 0.9 ms | **4.2 ms** | Production-ready real-time |

### Multi-Format Document Verification (30/30 Passed)
The gateway is verified against a 30-document corpus spanning 10 enterprise file formats (`.txt`, `.md`, `.json`, `.yaml`, `.csv`, `.sh`, `.patch`, `.py`, `.xml`, `.log`), verifying 100% accuracy on indirect injections, token disclosures, base64 obfuscations, and academic security quotations.

---

## 6. Project Layout

```
HackNova/
├── backend/
│   ├── app/                   # Core FastAPI application and security modules
│   │   ├── action_firewall.py # Egress tool firewall
│   │   ├── api.py             # REST API endpoints
│   │   ├── detector.py        # Offline TF-IDF classifier
│   │   ├── evidence.py        # Telemetry data structures
│   │   ├── forwarding.py      # Controlled assistant execution
│   │   ├── gemini_verifier.py # Optional Cloud AI verification
│   │   ├── intent_engine.py   # Intent drift analysis
│   │   ├── main.py            # FastAPI entry point
│   │   ├── normalization.py   # NFKC & multi-format decoding
│   │   ├── pipeline.py        # Orchestration pipeline
│   │   ├── policy_engine.py   # Deterministic policy rules
│   │   ├── protected_values.py# Token scanning & masking
│   │   ├── review.py          # Human-in-the-loop review
│   │   ├── risk_engine.py     # 4-dimensional risk scoring
│   │   ├── rules.py           # Lexical rule definitions
│   │   ├── sanitizer.py       # Surgical span excision
│   │   ├── schemas.py         # Pydantic request/response models
│   │   └── storage.py         # SQLite persistence & audit log
│   ├── config/                # Protected tokens and domain whitelists
│   ├── data/                  # Benchmark and training datasets
│   ├── models/                # Serialized classifier & metadata
│   ├── runtime/               # SQLite database file
│   ├── scripts/               # Training, seeding, and evaluation scripts
│   ├── tests/                 # 67-test automated test suite
│   └── README.md              # Backend technical documentation
├── frontend/
│   ├── src/
│   │   ├── components/        # Header, Sidebar, and navigation
│   │   ├── pages/             # Inspector, Authority Portal, Attack Lab, Policies, Evaluation, History
│   │   ├── api.js             # Gateway HTTP client
│   │   └── App.jsx            # Application shell and tab router
│   ├── package.json           # Frontend dependencies
│   ├── vite.config.js         # Vite configuration
│   └── README.md              # Frontend technical documentation
├── test_documents/            # 30 real-world security test files
│   ├── README.md              # Test document inventory and evaluation mapping
│   └── [30 sample files...]   # Markdown, txt, yaml, json, csv, patch, py, sh
├── .env.example               # Environment configuration template
├── .gitignore                 # Git ignore rules
└── README.md                  # Master project documentation
```

---

## 7. Quickstart Guide

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm 9+

### 1. Backend Setup & Test Execution

```bash
# Set PYTHONPATH to project root
$env:PYTHONPATH="."

# Run the complete test suite (all 67 tests pass)
python -m pytest backend/tests/ -v

# Start the FastAPI gateway server
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

The gateway API will be active at `http://127.0.0.1:8000`. Swagger documentation is available at `http://127.0.0.1:8000/docs`.

### 2. Frontend Setup

In a separate terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Open `http://localhost:5173` in your browser. The application will load directly to the **Inspector**.

### 3. (Optional) Cloud AI Verification Setup

PromptShield X runs fully offline by default. To enable on-demand Cloud Gemini AI confirmation:
```bash
# Copy environment configuration
cp .env.example .env

# Edit .env and supply your Gemini API key:
# GEMINI_API_KEY=AIzaSy...
```

Alternatively, configure the key in real time via the **Security Inspector** or the **Policies** tab.

---

## 8. Verification Scenarios Walkthrough

| Scenario | Ingestion Channel | Threat Vector | Gateway Action | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **Normal Report** | Uploaded Document | Legitimate quarterly financial figures | Passes all checks cleanly | **ALLOW** |
| **Indirect Injection** | Uploaded Document | Hidden instruction override embedded in memo | Excises offending span; passes 2nd inspection | **SANITIZE** |
| **Token Disclosure** | User Prompt | Request to dump `DEMO_INTERNAL_TOKEN_4821` | Enforces hard security invariant `POL-001` | **BLOCK** |
| **Academic Research** | User Prompt | Quotes *"ignore previous instructions"* in query | Contextual exemption avoids false positive | **ALLOW** |
| **Action Firewall Block**| AI Tool Operation | Proposed `send_external_http` to `attacker.example` | Intercepts unauthorized external domain | **FIREWALL BLOCK**|
| **Degraded Mode** | User Prompt | Unclear administrative socket execution | Graceful fallback engages conservative review | **ESCALATE** |
| **Base64 Obfuscation** | Uploaded Document | Encoded payload concealing jailbreak command | Normalizer decodes and flags inner attack | **BLOCK** |
| **Spaced Token Evasion**| User Prompt | Spaced letters `D E M O _ I N T E R N A L` | Token reconstructor collapses and blocks | **BLOCK** |
| **Authority Portal Dispatch**| SecOps Interface | Malicious prompt flagged by gateway | Complete raw prompt dossier sealed with IP/host | **TRANSFERRED** |

---

## 9. Automated Test Suite

The test suite covers unit, integration, policy, and corpus-level security invariants:

```bash
$env:PYTHONPATH="."
python -m pytest backend/tests/ -v
```

```
backend/tests/test_action_firewall.py ....      [  5%]  Egress action checks & whitelisting
backend/tests/test_api.py ......                [ 14%]  REST endpoints & health checks
backend/tests/test_authority.py ....            [ 20%]  Authority Portal incident dispatch
backend/tests/test_detection.py ........        [ 32%]  Lexical patterns & benign quotation
backend/tests/test_gemini.py .....              [ 40%]  Cloud verifier & offline simulation
backend/tests/test_malicious_documents.py ...   [ 85%]  30-document multi-format corpus
backend/tests/test_pipeline.py ....             [ 91%]  End-to-end inspection pipeline
backend/tests/test_policy.py ...                [ 95%]  Policy precedence & hard blocks
backend/tests/test_sanitizer.py ...             [100%]  Surgical excision & reinspection

============================== 67 passed in 4.33s ==============================
```

---

## 10. License

PromptShield X is licensed under the [MIT License](LICENSE).
