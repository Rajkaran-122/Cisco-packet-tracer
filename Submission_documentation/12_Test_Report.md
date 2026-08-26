# 12 — Automated Test Report

## 1. Overview

The NetSage AI repository includes an automated Python test suite to guarantee the integrity of diagnostic routing, safety policy enforcement, and LLM constraints.

Framework: `unittest` (compatible with `pytest`)
Directory: `tests/`
Total Tests: 7
Run command: `python -m pytest tests/ -v`

All 7 tests passed successfully during the pre-submission audit.

---

## 2. Test Execution Results

```text
============================= test session starts =============================
platform win32 -- Python 3.12.6, pytest-8.3.4
collected 7 items

tests/test_app_policy.py::TestAppPolicy::test_manual_edit_cannot_contain_destructive_commands PASSED [14%]
tests/test_llm_request.py::TestLLMRequestContract::test_llm_request_contract    PASSED [28%]
tests/test_netsage.py::TestNetSageEngine::test_all_cases_route_as_designed      PASSED [42%]
tests/test_netsage.py::TestNetSageEngine::test_llm_high_confidence_can_reach_hitl_gate PASSED [57%]
tests/test_netsage.py::TestNetSageEngine::test_llm_schema_and_confidence_gate   PASSED [71%]
tests/test_safety.py::TestSafetyPolicy::test_destructive_commands_are_blocked   PASSED [85%]
tests/test_safety.py::TestSafetyPolicy::test_safe_commands_pass                 PASSED [100%]

============================== 7 passed in 0.32s ==============================
```

---

## 3. Test Coverage Breakdown

### `test_netsage.py` (Core Engine Logic)
**`test_all_cases_route_as_designed`**
- Verifies that all 33 cases load from the CSV correctly.
- Confirms that NET-001 through NET-013 return `ERRORS_DETECTED` from the deterministic checker.
- Confirms that NET-014 through NET-033 return `NO_ERRORS_DETECTED` from the checker, correctly triggering the LLM fallback path.

**`test_llm_schema_and_confidence_gate`**
- Verifies that the `LLM_OUTPUT_SCHEMA` does not allow additional properties.
- Injects a mock LLM response with confidence 0.5.
- Asserts that `approval_allowed` becomes `False` because 0.5 is below the 0.75 threshold.

**`test_llm_high_confidence_can_reach_hitl_gate`**
- Injects a mock LLM response with confidence 0.9.
- Asserts that `approval_allowed` becomes `True`, enabling the Approve button in the dashboard.

### `test_safety.py` (Command Safety Guardrails)
**`test_safe_commands_pass`**
- Input: `["configure terminal", "interface Gi0/0.30", "no shutdown"]`
- Asserts: `safe` is True and `blocked_commands` is empty.

**`test_destructive_commands_are_blocked`**
- Input: `["reload", "write erase", "show ip route"]`
- Asserts: `safe` is False and `blocked_commands` correctly contains "reload" and "write erase".

### `test_app_policy.py` (Manual Override Safety)
**`test_manual_edit_cannot_contain_destructive_commands`**
- Verifies that if an engineer attempts to inject a destructive command via the Edit dialog, the safety policy will flag it just like an AI-generated command.
- Input: `["configure terminal", "reload"]`
- Asserts: `safe` is False.

### `test_llm_request.py` (Anthropic API Contract)
**`test_llm_request_contract`**
- Mocks the Anthropic API call to inspect the arguments passed by `engine.py`.
- Asserts that `temperature` is NOT in the request (required for Claude Sonnet 5).
- Asserts that `output_config.format.type` is set to `json_schema`.

---

## 4. Missing Test Coverage Assessment

While the existing tests ensure core functionality, a production deployment should add:
1. **Per-Rule Checker Tests**: Individual tests for each of the 14 regex rules in `checker.py` to prevent regressions.
2. **Dataset Integrity Tests**: Automated validation that all 33 rows in `cases.csv` contain valid strings for all 8 required columns.
3. **Audit Log String Formatting**: Tests to ensure that pipe characters (`|`) in root cause or engineer notes are correctly escaped before being written to the Markdown table.
