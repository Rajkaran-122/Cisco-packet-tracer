# 04 — AI Prompt Design

## 1. Overview

File: prompts/diagnose_prompt.md (142 lines)
Role: System prompt passed to Anthropic Claude on every LLM fallback call
Loaded by: engine.py:load_prompt_template()
Used in: engine.py:diagnose_with_llm() as the "system" parameter

The prompt is the contract between NetSage AI and the LLM. It defines:
- The LLM's role and scope
- What evidence it may and may not use
- The exact JSON output format
- 3 worked examples that demonstrate the expected reasoning style

---

## 2. Prompt Structure

### Section 1: Role Definition
The LLM is told it is the diagnostic reasoning module inside NetSage AI, invoked ONLY when
the deterministic checker (checker.py) has already failed to find a pattern match. This is
critical: it prevents the LLM from competing with or overriding the deterministic tier.

  "You are invoked only when the deterministic rule checker (checker.py) does not recognize
   the fault pattern in the captured show command output. Your job is to reason about cases
   the static regex rules don't cover — you are the fallback path, not the primary one."

### Section 2: Five Reasoning Rules
1. Base conclusions strictly on supplied show output and topology note
   — Never invent interface names, IP addresses, or error messages
2. Identify the OSI layer most likely responsible
3. Propose the minimum safe remediation
   — If ambiguous, prefer a non-destructive show command over guessing at a config change
4. You are advisory only — never imply the fix has been applied
5. If evidence is insufficient, say so with a low confidence score rather than fabricating

### Section 3: Output Format Specification
The LLM is instructed to return ONLY a JSON object with exactly these 6 fields:

  {
    "root_cause":    "<one sentence, plain language>",
    "osi_layer":     "<e.g. 'Layer 3' or 'Layer 2 / Layer 3'>",
    "confidence":    0.0,
    "evidence":      "<the specific line(s) from show output that support this>",
    "next_command":  "<single most useful next CLI command to run or apply>",
    "fix_steps":     ["<step 1>", "<step 2>", "..."]
  }

### Section 4: Three Few-Shot Examples

---

## 3. JSON Schema Verification

The prompt schema is enforced at TWO levels:

Level 1 — LLM_OUTPUT_SCHEMA in engine.py (Anthropic Structured Outputs)
This schema is sent to the API via output_config and forces the model to produce
JSON that matches the declared structure before the response is even returned.

  Required fields: root_cause, osi_layer, confidence, evidence, next_command, fix_steps
  Types enforced: root_cause=string, osi_layer=string, confidence=number,
                  evidence=string, next_command=string, fix_steps=array[string]
  additionalProperties: false (no extra fields permitted)

Level 2 — _validate_llm_result() in engine.py
Application-level validation runs after JSON parsing:
  - All 6 fields must be present
  - root_cause must be non-empty string
  - osi_layer must be non-empty string
  - confidence must be float between 0.0 and 1.0
  - fix_steps must be list of strings

If validation fails at either level, a RuntimeError is raised with a descriptive message.
The error propagates to the Streamlit UI where it is displayed as st.error().

---

## 4. Few-Shot Example Analysis

### Example 1: Missing Static Route
Input: show ip route with no route to 10.30.0.0/24
Output demonstrates:
  - Quoting specific routing table entry as evidence
  - Low-impact next_command: show running-config | section router
  - Three progressive fix_steps (add route, verify, test)
  - Confidence: 0.9 (high — routing table is conclusive)

### Example 2: Native VLAN Mismatch
Input: show interfaces trunk with mismatched native VLANs
Output demonstrates:
  - Quoting exact trunk port output lines as evidence
  - next_command: show running-config interface Fa0/2
  - Three fix_steps including post-fix verification
  - Confidence: 0.85

### Example 3: ACL Not Applied to Interface
Input: show ip interface showing "Inbound access list is not set"
       show access-lists showing GUEST-RESTRICT defined but unused
Output demonstrates:
  - Correlating two separate show outputs
  - Quoting both as evidence
  - Precise fix_steps including end and verification command
  - Confidence: 0.95 (very high — the ACL exists but binding is absent)
  - NOTE: This matches the show output design of NET-031 exactly

---

## 5. Hallucination Controls

| Control | Mechanism | Enforcement |
|---|---|---|
| Evidence grounding | Rule 1: never invent identifiers not in input | Prompt instruction |
| Minimum remediation | Rule 3: prefer show command over config change when ambiguous | Prompt instruction |
| Advisory-only framing | Rule 4: never imply fix is applied | Prompt instruction |
| Low confidence preference | Rule 5: explicit low score over fabricated root cause | Prompt instruction |
| Schema enforcement | Structured Outputs API | engine.py LLM_OUTPUT_SCHEMA |
| Field validation | _validate_llm_result() | engine.py application-level |
| Confidence gate | approval_allowed = confidence >= 0.75 AND safe | engine.py + app.py |

---

## 6. Recommended Improvements

1. Add concept_tag to the output schema — allows the dashboard to show LLM-inferred tags
2. Add a low-confidence example — show the model what a 0.4-confidence ambiguous response looks like
3. Add multi-symptom guidance — what to do when show output contains multiple fault indicators
4. Add severity guidance — allow the LLM to infer severity from the symptom description
