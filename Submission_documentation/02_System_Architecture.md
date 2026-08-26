# 02 — System Architecture

## 1. Architecture Overview

NetSage AI uses a four-tier pipeline. Each tier has a clear entry condition, a defined output
format, and explicit failure behaviour.

```
Cisco Packet Tracer / show command capture
               |
               | (copy-paste show output into cases.csv or dashboard)
               v
+-----------------------------------------------+
|  Tier 1: Deterministic Rule Checker           |
|  src/checker.py — 14 regex rules              |
|  Input:  show_outputs (string)                |
|  Output: {status, flagged_issues[]}           |
|  Speed:  < 1 ms, zero cost, zero API call     |
+----------------------+------------------------+
                       |
          Match found? |
               YES <---+---> NO
               |                |
               v                v
  _checker_result_to_schema()  Tier 2: LLM Reasoning
  engine.py L70-87             engine.py diagnose_with_llm()
  confidence = 1.0             prompts/diagnose_prompt.md
               |               Claude Structured Outputs API
               |               _validate_llm_result()
               |               confidence gate: >= 0.75
               +-------+-------+
                       |
                       v
+-----------------------------------------------+
|  Tier 3: Safety Guardrails                    |
|  src/safety.py — validate_commands()          |
|  Blocks: reload, write erase, erase           |
|           startup-config, format, delete,     |
|           crypto key zeroize                  |
|  Sets approval_allowed = True/False           |
+----------------------+------------------------+
                       |
                       v
+-----------------------------------------------+
|  Tier 4: Human-in-the-Loop Gate               |
|  src/app.py — Streamlit dashboard             |
|  [Approve & Deploy] [Edit Commands] [Reject]  |
|  Approve button DISABLED if not safe or       |
|  confidence < 0.75                            |
+----------------------+------------------------+
                       |
                       v
+-----------------------------------------------+
|  Tier 5: Audit & Responsible AI               |
|  docs/model_audit_log.md                      |
|  Append-only, one row per decision            |
|  Dashboard reads this for live metrics        |
+-----------------------------------------------+
```

---

## 2. Complete Data Flow

### Step 1: Data Enters the System
- **Source**: Pre-captured Cisco IOS `show` command output in `data/cases.csv`
- **Format**: 8-column CSV — case_id, symptom, topology_note, osi_layer, concept_tag,
  severity, show_outputs, expected_fault
- **Who creates it**: `scripts/generate_cases.py` generated the initial 33 cases;
  future cases can be added manually

### Step 2: User Selects a Case in the Dashboard
- `app.py:load_cases()` reads `cases.csv` into a pandas DataFrame (cached)
- A dropdown selector in Tab 1 lets the engineer choose by case_id and symptom preview
- Optional filter by concept_tag narrows the dropdown list
- Selecting a different case clears any previous diagnosis result from session state

### Step 3: Diagnostic Engine Runs
- `app.py` calls `engine.diagnose_case(case.to_dict())`
- `engine.py:diagnose_case()` calls `checker.run_checks(case["show_outputs"])`
- If status is ERRORS_DETECTED: `_checker_result_to_schema()` formats the result
- If status is NO_ERRORS_DETECTED: `diagnose_with_llm()` is called

### Step 4: LLM Path (if applicable)
- `load_prompt_template()` reads `prompts/diagnose_prompt.md`
- API call is made to Anthropic with:
  - system: the prompt template
  - user: formatted symptom + topology note + show output
  - output_config: Structured Outputs with LLM_OUTPUT_SCHEMA
  - NOTE: temperature is intentionally omitted (Claude Sonnet 5 requirement)
- Response JSON is parsed and validated by `_validate_llm_result()`

### Step 5: Safety Check
- `safety.py:validate_commands()` is called on fix_steps
- Each command line is tested against 6 blocked patterns
- `approval_allowed` is set: True only if confidence >= 0.75 AND all commands safe

### Step 6: HITL Display
- Dashboard shows root_cause, osi_layer, confidence, evidence, fix_steps
- Approve button: enabled only if approval_allowed == True
- Edit button: always available; edits re-validated through safety before logging
- Reject button: always available; requires a reason text input

### Step 7: Decision Logging
- `append_audit_entry()` writes one row to `docs/model_audit_log.md`
- Format: `| Timestamp | Case ID | Action | Root Cause | Engineer Note |`
- The dashboard sidebar reloads metrics from this file after each write

---

## 3. File Responsibility Matrix

| File | Role | Input | Output | Key Functions |
|---|---|---|---|---|
| src/checker.py | Deterministic fault detector | show_outputs string | {status, flagged_issues[]} | run_checks() |
| src/engine.py | Orchestrator | case dict | unified result dict | diagnose_case(), diagnose_with_llm(), _validate_llm_result() |
| src/safety.py | Command policy enforcer | list of CLI strings | {safe, blocked, checked} | validate_commands() |
| src/app.py | UI, HITL gate, audit writer | cases.csv, model_audit_log.md | Dashboard, appended log | load_cases(), parse_audit_log(), append_audit_entry() |
| prompts/diagnose_prompt.md | LLM system prompt | (loaded by engine.py) | Shapes LLM JSON output | load_prompt_template() |
| data/cases.csv | Ground-truth dataset | (written by generate_cases.py) | Source for all diagnostics | — |
| data/system_config.json | Runtime config | (read by engine.py) | LLM model, threshold, paths | load_config() |
| docs/model_audit_log.md | Append-only audit trail | Written by app.py | Dashboard metrics source | — |
| docs/responsible_ai_log.md | AI correction documentation | Static document | Evaluator reference | — |

---

## 4. Failure Modes and Recovery

| Failure | Location | What Happens |
|---|---|---|
| cases.csv missing | app.py:load_cases() | st.error() shown; empty DataFrame returned |
| ANTHROPIC_API_KEY not set | engine.py:diagnose_with_llm() | RuntimeError with clear message |
| LLM returns bad JSON | engine.py:L172-174 | RuntimeError: "LLM returned invalid JSON" |
| LLM missing required field | engine.py:_validate_llm_result() | RuntimeError listing missing fields |
| Confidence out of range | engine.py:L113-114 | RuntimeError: "must be between 0.0 and 1.0" |
| Destructive command in fix_steps | safety.py | approval_allowed=False; Approve disabled |
| Engineer types destructive command in Edit | app.py:L312 | st.error(); audit entry NOT written |
| Diagnosis exception | app.py:L226-228 | st.error(str(e)); no partial result shown |
