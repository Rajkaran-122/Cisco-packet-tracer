# 07 — Safety Guardrails

## 1. Overview

File: src/safety.py (38 lines)
Entry function: validate_commands(commands: Iterable[str]) -> Dict[str, Any]
Purpose: Prevent destructive Cisco IOS commands from reaching the human approval gate
         or being logged as accepted engineer commands.

IMPORTANT: NetSage AI never executes any commands on network hardware.
Safety.py is an advisory safety check — it cannot prevent an engineer from
typing these commands directly into Cisco Packet Tracer or a real device.
Its role is to prevent the AI from PROPOSING them and to prevent the dashboard
from APPROVING them automatically.

---

## 2. Blocked Command Patterns (6 Active)

All patterns are compiled with re.IGNORECASE and matched from the start of each line.

| # | Pattern | Blocks | Why Blocked |
|---|---|---|---|
| 1 | ^\s*reload\b | reload | Reboots entire device — network-wide outage risk |
| 2 | ^\s*write\s+erase\b | write erase | Erases startup configuration permanently |
| 3 | ^\s*erase\s+startup-config\b | erase startup-config | Same effect as write erase |
| 4 | ^\s*format\b | format flash: etc. | Destroys device file system |
| 5 | ^\s*delete\b | delete flash:vlan.dat etc. | Permanent file deletion |
| 6 | ^\s*crypto\s+key\s+zeroize\b | crypto key zeroize | Destroys RSA key pairs (disables SSH) |

---

## 3. Function Behaviour

validate_commands(commands) processes each line individually:

  for command in commands:
    line = str(command).strip()
    if not line: continue                    <- skip blank lines
    checked.append(line)
    if any(re.search(pattern, line, IGNORECASE) for pattern in BLOCKED_PATTERNS):
      blocked.append(line)

Returns:
  {
    "safe": True if blocked is empty else False,
    "blocked_commands": ["reload", ...],
    "checked_commands": ["configure terminal", "interface Gi0/0.30", ...]
  }

---

## 4. Where Safety Is Enforced

Safety checks run at THREE points in the pipeline:

### Point 1: Deterministic path — _checker_result_to_schema() in engine.py
When a checker rule fires, its remediation string is split into lines and
validate_commands() is called BEFORE the result is returned to the dashboard.
approval_allowed is set based on the safety result.

### Point 2: LLM path — _validate_llm_result() in engine.py
After LLM JSON is validated, validate_commands() is called on fix_steps.
Same approval_allowed logic applies.

### Point 3: Human edit path — app.py:L311
When an engineer clicks "Edit Commands" and submits modified commands,
validate_commands() is called on the edited text BEFORE the audit entry
is written. If blocked commands are found:
  - st.error() is displayed
  - The audit log is NOT updated
  - The engineer must remove the destructive command before proceeding

---

## 5. UI Enforcement

The Approve & Deploy button in the dashboard uses Streamlit's native disabled= parameter:

  approve = st.button(
    "Approve & Deploy (Manual)",
    disabled=not approval_allowed,
    ...
  )

This means the button is PHYSICALLY DISABLED in the browser if:
  - safety["safe"] is False (blocked commands in fix_steps), OR
  - confidence < 0.75 (LLM path only)

A warning message is displayed explaining which condition is blocking approval.

---

## 6. What Safety.py Does NOT Cover

1. Commands that are partially destructive (e.g. "no ip routing" — disables routing globally)
2. Commands that are safe in isolation but dangerous in sequence
3. Commands the engineer types directly into Packet Tracer without using NetSage
4. Logical errors in remediation commands that would create new misconfigurations

These are addressed by the HITL review requirement — the human engineer provides
the final judgment on whether proposed commands are appropriate.

---

## 7. Test Verification

Two unit tests verify safety policy:

test_safe_commands_pass (test_safety.py):
  Input: ["configure terminal", "interface Gi0/0.30", "no shutdown"]
  Expected: safe=True, blocked_commands=[]
  Result: PASS

test_destructive_commands_are_blocked (test_safety.py):
  Input: ["reload", "write erase", "show ip route"]
  Expected: safe=False, blocked=["reload", "write erase"]
  Result: PASS

test_manual_edit_cannot_contain_destructive_commands (test_app_policy.py):
  Input: ["configure terminal", "reload"]
  Expected: safe=False, blocked=["reload"]
  Result: PASS
