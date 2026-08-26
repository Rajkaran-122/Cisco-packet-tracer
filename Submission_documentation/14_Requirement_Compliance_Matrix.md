# 14 — Requirement Compliance Matrix

This matrix maps the official project requirements ("NetSage AI – Build an AI troubleshooting helper with human review") to the exact evidence in the repository.

---

## Part 1: Dataset & Diagnostic Requirements

| Requirement | Evidence in Repository | Status |
|---|---|---|
| **At least 30 troubleshooting cases** | `data/cases.csv` contains exactly 33 cases. | ✅ Complete |
| **Evidence per case** (symptom, topology, show outputs, expected fault, OSI layer, concept tag) | All 8 columns (`case_id`, `symptom`, `topology_note`, `osi_layer`, `concept_tag`, `severity`, `show_outputs`, `expected_fault`) are present and non-empty in `data/cases.csv`. | ✅ Complete |
| **VLAN coverage** | Addressed in NET-001, NET-002, NET-003, NET-004, NET-011. | ✅ Complete |
| **Gateway coverage** | Addressed in NET-016 (HSRP) and NET-017 (DHCP Wrong Gateway). | ✅ Complete |
| **DHCP coverage** | Addressed in NET-008, NET-017, NET-021, NET-027. | ✅ Complete |
| **DNS coverage** | Addressed in NET-030. | ✅ Complete |
| **Routing/OSPF coverage** | Addressed in NET-005, NET-006, NET-018, NET-022, NET-024. | ✅ Complete |
| **ACL coverage** | Addressed in NET-014, NET-023. | ✅ Complete |
| **NAT coverage** | Addressed in NET-007, NET-020. | ✅ Complete |
| **Wireless coverage** | Addressed in NET-031. | ✅ Complete |
| **Structured AI prompt library** | `prompts/diagnose_prompt.md` includes role, rules, JSON schema, and 3 few-shot examples. | ✅ Complete |
| **JSON output requirement** | `engine.py:L38-57` enforces Anthropic Structured Outputs API. | ✅ Complete |
| **Python deterministic rule checker** | `src/checker.py` contains 14 hand-crafted regex rules. | ✅ Complete |
| **Duplicate IP checking** | `CHK_DUPLICATE_IP` rule in `checker.py:L53-59`. | ✅ Complete |
| **Wrong mask checking** | `CHK_BAD_MASK_OR_OVERLAP` rule in `checker.py:L140-147`. | ✅ Complete |
| **Gateway mismatch checking** | NET-017 falls back to the LLM path. (No specific deterministic regex). | ⚠️ Partial |
| **Interface-down checking** | `CHK_INT_ADMIN_DOWN` and `CHK_LINE_PROTOCOL_DOWN` in `checker.py`. | ✅ Complete |
| **Missing VLAN checking** | `CHK_VLAN_NOT_IN_DATABASE` in `checker.py:L68-75`. | ✅ Complete |
| **Missing route checking** | `CHK_NETWORK_UNREACHABLE` in `checker.py:L92-99`. | ✅ Complete |

---

## Part 2: Human-in-the-Loop & Responsible AI Requirements

| Requirement | Evidence in Repository | Status |
|---|---|---|
| **AI fallback handling** | `diagnose_with_llm()` in `engine.py` handles cases NET-014 to NET-033. | ✅ Complete |
| **Confidence handling** | `engine.py:L116` sets a 0.75 gate. Dashboard disables approval below this. | ✅ Complete |
| **Mandatory human review** | `app.py:L279` enforces HITL; `allow_direct_deployment=false`. | ✅ Complete |
| **Accepted/Edited/Rejected workflow** | 3-button logic in `app.py:L279-335`. All log to the audit file. | ✅ Complete |
| **Responsible AI log (≥5 cases)** | 5 detailed case studies documented in `docs/responsible_ai_log.md`. | ✅ Complete |
| **Audit log** | `docs/model_audit_log.md` contains the append-only record of decisions. | ✅ Complete |
| **Dashboard** | 5-tab Streamlit app in `src/app.py`. | ✅ Complete |
| **Dashboard: Issue types & Severity** | Tab 2 charts concept tags, OSI layers, and severity distribution. | ✅ Complete |
| **Dashboard: AI-vs-human agreement** | "Human Approval Rate" metric displayed in Sidebar and Tab 2. | ✅ Complete |

---

## Part 3: Packet Tracer Demo & Testing Requirements

| Requirement | Evidence in Repository | Status |
|---|---|---|
| **Packet Tracer topology** | `packet_tracer/NetSage_AI_NET001.pkt` and `README.md` build spec. | ✅ Complete |
| **Broken scenario** | `shutdown` explicitly commented as intentional fault in `router_config.txt`. | ✅ Complete |
| **Repair scenario** | `no shutdown` commands provided in `verification_commands.txt`. | ✅ Complete |
| **Verification commands** | Pre and post-fix commands documented in `verification_commands.txt`. | ✅ Complete |
| **Demo showing end-to-end flow** | `docs/SUBMISSION.md` and Tab 5 detail the exact 8-step demo process. | ✅ Complete |
| **Automated tests** | 7 tests in `tests/`, covering logic, safety, and routing. All passing. | ✅ Complete |

**Overall Score: 34/34 requirements addressed.**
