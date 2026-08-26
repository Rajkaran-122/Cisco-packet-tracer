# 10 — Dashboard Guide

## 1. Overview

File: `src/app.py` (538 lines)
Framework: Streamlit (>=1.38)
Run command: `streamlit run src/app.py`

The NetSage AI dashboard provides the operational interface for the Human-in-the-Loop gate,
scenario inspection, analytics, and audit logging. It is built entirely in Python using Streamlit.

---

## 2. Global Elements

**Sidebar**:
Always visible. Displays:
- System Operating Rules (Hybrid architecture, LLM fallback, Confidence >= 0.75, HITL required)
- Live Audit Metrics (Total Decisions, Human Approval Rate, Edits, Rejections)
- Metrics are recalculated automatically every time an action is taken.

**Top Header**:
Always visible above tabs. Displays:
- Total Active Scenarios
- Active Deterministic Rules (14)
- Human Approval Rate
- Safety Guardrails status

---

## 3. Tab Breakdown

### Tab 1: 🔬 Diagnostic Lab & HITL Gate
**Purpose**: The primary operational interface where an engineer reviews and acts on AI diagnoses.
**Features**:
- Domain Filter: Dropdown to filter cases by `concept_tag` (e.g., VLAN, OSPF, NAT).
- Case Selector: Dropdown to pick a specific scenario from the dataset.
- Scenario Context: Expander showing symptom, topology note, OSI layer, severity, and the captured show-command output.
- **Run Diagnostic Button**: Triggers the diagnosis pipeline (`engine.diagnose_case`).
- **Results Display**: Shows the Root Cause, OSI Layer, Confidence, Evidence, Next Command, and Fix Steps.
- **HITL Gate**:
  - `Approve & Deploy (Manual)` button (Disabled if confidence < 0.75 or safety check fails).
  - `Edit Commands` button (Opens an override text area).
  - `Reject (False Positive)` button.

### Tab 2: 📊 Analytics & Agreement Dashboard
**Purpose**: Visualizes dataset distribution and operational metrics.
**Features**:
- **Scenarios by Network Domain**: Bar chart derived from `cases_df["concept_tag"]`.
- **Scenarios by OSI Layer**: Bar chart derived from `cases_df["osi_layer"]`.
- **Scenarios by Severity Level**: Dataframe table of High, Medium, Low distributions.
- **HITL Decision Breakdown**: Dataframe table counting Approvals, Edits, and Rejections from the audit log.

### Tab 3: 📋 Case Dataset Explorer
**Purpose**: Provides full visibility into the troubleshooting dataset.
**Features**:
- Search bar: Filter cases by text in symptom, concept, or fault.
- Dataframe view: Interactive table of all cases.
- Download button: Download the complete `cases.csv` directly from the dashboard.

### Tab 4: 🛡️ Responsible AI & Audit Trail
**Purpose**: Transparency into the model's history and human corrections.
**Features**:
- **Live Audit Log**: Interactive dataframe rendering the contents of `model_audit_log.md`.
- **Action Filter**: Dropdown to filter the audit log by Approval, Edit, or Rejection.
- **Case Studies**: 5 expandable sections detailing the documented Responsible AI correction cases (NET-009, NET-014, NET-020, NET-026, NET-031).

### Tab 5: 🧪 Packet Tracer Demo Walkthrough
**Purpose**: Step-by-step documentation for the NET-001 live demo.
**Features**:
- Static display of the scenario context, topology, pre-fix verification steps, expected NetSage AI output, and post-fix validation for the NET-001 demo case.

---

## 4. Key Metrics and Calculations

**Human Approval Rate**:
Displayed in the sidebar and Tab 2.
Calculation: `(Total Approvals / Total Decisions) * 100`
Note: This represents the rate at which human engineers accepted the AI's proposal without modification. It is an operational metric, not a semantic AI accuracy metric.

**Audit Log Refresh**:
When an engineer clicks a HITL button (Approve, Confirm Edit, Confirm Reject):
1. The entry is appended to `model_audit_log.md`.
2. The Streamlit data cache for `load_audit_metrics` is explicitly cleared.
3. The dashboard calls `st.rerun()`.
4. The sidebar instantly reflects the updated metrics.
