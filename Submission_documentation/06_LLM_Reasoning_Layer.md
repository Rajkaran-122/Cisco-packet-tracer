# 06 — LLM Reasoning Layer

## 1. Overview

File: src/engine.py (205 lines)
LLM Provider: Anthropic
Model: claude-sonnet-5 (configured in data/system_config.json)
API Feature Used: Structured Outputs (output_config with json_schema)
Entry function: diagnose_with_llm(case, config)

The LLM path is only activated when checker.run_checks() returns NO_ERRORS_DETECTED.
This covers cases NET-014 through NET-033 — complex faults that require semantic
reasoning about configuration context rather than exact string pattern matching.

---

## 2. When the LLM Path Activates

  diagnose_case(case)
    |
    +-> run_checks(show_outputs)
    |
    +-- status == ERRORS_DETECTED?
    |     YES: return _checker_result_to_schema()     <- LLM NOT called
    |     NO:  return diagnose_with_llm(case, config) <- LLM called here

The LLM is never called for cases NET-001 through NET-013 under any circumstances.
This is verified by the automated test test_all_cases_route_as_designed.

---

## 3. Request Construction

The API call is constructed in engine.py:diagnose_with_llm():

  client = anthropic.Anthropic(api_key=api_key)

  system_prompt = load_prompt_template()  <- prompts/diagnose_prompt.md

  user_content = (
    f"Symptom: {case['symptom']}\n"
    f"Topology Note: {case['topology_note']}\n"
    f"Captured show output:\n{case['show_outputs']}\n\n"
    "Diagnose this case using only the supplied evidence."
  )

  response = client.messages.create(
    model=config["llm"]["model"],         <- "claude-sonnet-5"
    max_tokens=config["llm"]["max_tokens"], <- 1024
    system=system_prompt,
    messages=[{"role": "user", "content": user_content}],
    output_config={
      "format": {
        "type": "json_schema",
        "schema": LLM_OUTPUT_SCHEMA
      }
    }
  )

IMPORTANT: temperature is intentionally NOT included in this call.
Claude Sonnet 5 rejects non-default sampling parameters. The CHANGELOG
documents this: "Removed the unsupported temperature parameter."

---

## 4. Structured Outputs Schema (enforced at API level)

  LLM_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
      "root_cause":   {"type": "string"},
      "osi_layer":    {"type": "string"},
      "confidence":   {"type": "number"},
      "evidence":     {"type": "string"},
      "next_command": {"type": "string"},
      "fix_steps":    {"type": "array", "items": {"type": "string"}}
    },
    "required": [
      "root_cause", "osi_layer", "confidence",
      "evidence", "next_command", "fix_steps"
    ],
    "additionalProperties": False
  }

This schema is sent to the Anthropic API. The model is constrained to produce
only JSON that matches this structure. Any missing field or wrong type causes
the API to reject the response before it is returned.

---

## 5. Application-Level Validation

After the API returns, _validate_llm_result() applies a second layer of checks:

  - All 6 required fields must be present
  - root_cause must be non-empty string
  - osi_layer must be non-empty string
  - evidence must be a string (empty is allowed for low-confidence responses)
  - next_command must be a string
  - fix_steps must be a list where every item is a string
  - confidence must parse as float AND be between 0.0 and 1.0 inclusive

If any check fails, a RuntimeError is raised. This propagates to app.py
where it is caught and displayed as st.error().

---

## 6. Confidence Gate

After validation, the confidence gate is applied:

  threshold = config["thresholds"]["min_confidence_for_auto_flag"]  <- 0.75

  safety = validate_commands(parsed["fix_steps"])

  parsed["approval_allowed"] = (confidence >= threshold) AND safety["safe"]

If approval_allowed is False:
  - The Approve button in the dashboard is DISABLED (Streamlit disabled= parameter)
  - A warning banner is shown explaining the low confidence or unsafe commands
  - The engineer can still Edit or Reject — they cannot Approve until the threshold is met

---

## 7. Unified Output Schema

Both the deterministic and LLM paths return the same dict structure,
enabling the dashboard to display results identically regardless of path:

  {
    "source":           "deterministic_checker" | "llm_reasoning",
    "status":           "ERRORS_DETECTED" | "LLM_INFERRED",
    "root_cause":       string,
    "osi_layer":        string,
    "confidence":       float,
    "evidence":         string,
    "next_command":     string,
    "fix_steps":        [string, ...],
    "flagged_issues":   [dict, ...],  <- empty for LLM path
    "approval_allowed": bool,
    "safety":           {safe, blocked_commands, checked_commands},
    "confidence_threshold": float     <- LLM path only
  }

---

## 8. Error Handling

| Condition | What Happens |
|---|---|
| anthropic package not installed | RuntimeError: "anthropic package is not installed" |
| ANTHROPIC_API_KEY not set | RuntimeError: "ANTHROPIC_API_KEY is not set" |
| API call fails (network error) | anthropic.APIError propagates to app.py |
| Empty response from API | RuntimeError: "LLM returned an empty response" |
| Invalid JSON (should not happen with Structured Outputs) | RuntimeError with JSONDecodeError |
| Missing field in response | RuntimeError listing missing fields |
| Confidence out of range | RuntimeError: "must be between 0.0 and 1.0" |
