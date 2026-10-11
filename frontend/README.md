# PromptShield X — Frontend Security Console

Enterprise SecOps management console and real-time inspection interface for the **PromptShield X** Dual-Boundary AI Security Gateway.

---

## 1. Overview

The PromptShield X frontend is a high-performance Single Page Application (SPA) built for security analysts, incident responders, and compliance auditors. It interfaces directly with the FastAPI gateway to provide real-time prompt telemetry, forensic policy inspection, and incident escalation workflows.

---

## 2. Core Functional Modules

### 1. Security Inspector (`/inspector`)
- **Real-Time Input Analysis**: Accepts user prompts, uploaded documents, web snippets, and simulated tool outputs.
- **Forensic Decision Banner**: Immediately reflects gateway enforcement (`ALLOW`, `BLOCK`, `SANITIZE`, `ESCALATE`).
- **6-Step Decision Audit Trail**: Explains how every verdict was reached (Input received → Suspicious behavior found → Risk analyzed → Policy applied → Safe result → Action checked).
- **Surgical Sanitization Diff View**: Displays excised malicious spans side-by-side with sanitized content safe for assistant forwarding.
- **On-Demand Cloud AI Verification**: Optional verification modal with Google Gemini for borderline or ambiguous cases.
- **Higher Authority Escalation Card**: One-click dispatch of flagged payloads, user identities, and employee workstations to the SecOps incident queue.

### 2. Authority Portal (`/authority`)
- **Incident Dossier Repository**: Dedicated SecOps queue for escalated prompts with complete chain-of-custody.
- **Identity Telemetry**: Captures submitting user name, employee ID, corporate email, department, client IP, and workstation identifier.
- **Disposition Lifecycle**: Supports triage workflows (`TRANSFERRED_FOR_INVESTIGATION`, `UNDER_INVESTIGATION`, `ACTION_TAKEN`, `EVIDENCE_SEALED`, `RESOLVED`, `FALSE_POSITIVE_CLEARED`).
- **One-Click Dossier Export**: Formats complete forensic reports for legal or HR compliance reviews.

### 3. Threat Verification Lab (`/attack-lab`)
- **Baseline Threat Matrix**: 9 pre-configured attack categories demonstrating prompt injection, secret exfiltration, role impersonation, base64 obfuscation, and jailbreaks.
- **Comprehensive Document Corpus**: Dropdown selector integrating 30 real-world malicious documents, invoices, logs, and benign security queries.
- **End-to-End Pipeline Visualization**: Shows raw input → Gateway inspection → Sanitized forwarding → Downstream assistant operation.

### 4. Security Policies (`/policies`)
- **Hard Security Invariants**: Displays inviolable rules (token disclosure prevention, exfiltration blocks, policy tampering barriers).
- **Configurable Operational Controls**: Real-time toggles for surgical sanitization, deep payload decoding, and intent drift escalation thresholds.

### 5. Empirical Evaluation (`/evaluation`)
- **Performance Benchmarks**: Displays empirical accuracy metrics evaluated against held-out datasets.
- **Comparative Analysis**: Bar charts contrasting deterministic Rule-Only detection against the Hybrid Detection pipeline.
- **Live Benchmark Execution**: On-demand button triggering automated re-evaluation directly against backend test corpora.

### 6. Audit Trail & History (`/history`)
- **Persistent Inspection Log**: Searchable and filterable record of all processed inputs.
- **Credential Masking**: Automatically redacts sensitive system tokens (`DEMO_INTERNAL_****_4821`).
- **Human-in-the-Loop Review**: Interface for security administrators to approve or reject escalated requests.

---

## 3. Technology Stack

- **Framework**: React 19
- **Build Tool**: Vite 8
- **Styling**: Tailwind CSS 4
- **Icons**: Lucide React
- **Data Visualization**: Recharts
- **Linter**: Oxlint

---

## 4. Getting Started

### Prerequisites
- Node.js 18.x or higher
- npm 9.x or higher

### Installation & Run

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will start at `http://localhost:5173`.

### Production Build

```bash
# Type check and build optimized bundle
npm run build

# Preview production build locally
npm run preview
```

### Linting

```bash
npm run lint
```
