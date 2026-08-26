# 01 — NetSage AI: Project Overview

## 1. What Is NetSage AI?

NetSage AI is an enterprise-grade, AI-assisted network fault-diagnosis platform built for Cisco IOS
and Cisco Packet Tracer lab environments. It acts as an intelligent troubleshooting co-pilot for
network engineers — it never replaces the engineer, and it never executes commands autonomously.

The system combines two diagnostic tiers working in sequence:

**Tier 1 — Deterministic Rule Engine** (checker.py)
Scans captured Cisco IOS show-command output using 14 hand-crafted regular expressions. When a
known fault signature is found, it returns a 100%-confidence diagnosis instantly — no API call,
no cost, no latency.

**Tier 2 — LLM Reasoning Fallback** (engine.py + diagnose_prompt.md)
For complex misconfigurations that static signatures cannot recognize, the system calls Anthropic
Claude with a structured JSON schema. The LLM must return a root cause, OSI layer, confidence
score, evidence quote, next diagnostic command, and fix steps.

Both tiers are gated behind a mandatory Human-in-the-Loop (HITL) review. NetSage AI never
directly executes Cisco commands on any network device.

---

## 2. Problem Statement

**Official challenge**: "NetSage AI – Build an AI troubleshooting helper with human review"

Enterprise networking teams face this challenge daily:
- Network faults occur at multiple OSI layers simultaneously
- Reproducing a fault requires exact show-command evidence
- AI tools can hallucinate interface names, IP addresses, and commands
- Destructive AI-generated commands (reload, write erase) can cause outages if auto-executed
- There is no audit trail of what the AI suggested and what the engineer actually deployed

NetSage AI solves all five problems.

---

## 3. Goals

| Goal | How Achieved |
|---|---|
| Structured fault diagnosis library | 33-case dataset with 8 fields per case |
| Fast deterministic diagnosis for known faults | 14 regex rules in checker.py |
| Intelligent fallback for complex cases | Claude via Anthropic Structured Outputs |
| Zero hallucination risk on known patterns | Deterministic path has no LLM involvement |
| Prevent destructive command execution | safety.py blocks reload, write erase, format, delete, etc. |
| Enforce human oversight | HITL gate in Streamlit — Approve button disabled until confidence >= 0.75 |
| Full audit trail | Append-only model_audit_log.md with every decision |
| Documented AI failures | 5 case studies in responsible_ai_log.md |

---

## 4. Key Features

- **Hybrid diagnosis**: Deterministic-first, LLM-fallback architecture
- **33-case dataset**: Covers VLAN, DHCP, DNS, OSPF, RIP, ACL, NAT, Wireless, SSH, STP, EtherChannel, HSRP, and more
- **Structured Outputs**: JSON schema enforced at the API level — no malformed responses
- **Confidence gate**: LLM proposals below 0.75 confidence cannot be approved in one click
- **Safety policy**: 6 destructive command patterns blocked in both AI output and human edits
- **HITL workflow**: Approve & Deploy / Edit Commands / Reject — all logged
- **5-tab Streamlit dashboard**: Diagnostic lab, analytics, dataset explorer, audit trail, demo walkthrough
- **Responsible AI documentation**: 5 real case studies where human review prevented AI mistakes
- **Automated tests**: 7 tests covering routing logic, schema, confidence gate, safety policy
- **Cisco Packet Tracer lab**: Complete NET-001 topology with fault, fix, and verification

---

## 5. Technology Stack

| Component | Technology | Version Requirement |
|---|---|---|
| Web framework | Streamlit | >= 1.38 |
| Data processing | pandas | >= 2.2 |
| LLM provider | Anthropic Claude | anthropic >= 0.84 |
| LLM model | claude-sonnet-5 | Anthropic API |
| Language | Python | >= 3.9 (verified 3.12.6) |
| Network simulator | Cisco Packet Tracer | Any recent version |

---

## 6. What Makes This Responsible AI?

NetSage AI was designed from the ground up to prevent three classes of AI harm in networking:

**1. Destructive Command Execution**
Commands like `reload` and `write erase` would cause network-wide outages if auto-deployed.
safety.py blocks them before they ever reach a human for approval.

**2. Hallucinated Configuration**
The LLM prompt explicitly forbids inventing interface names, IP addresses, or error messages
not present in the captured show output. The Anthropic Structured Outputs API enforces the
schema so no free-text hallucination can pollute the diagnosis.

**3. Security Degradation**
Without human review, an AI might remove an entire ACL to restore connectivity rather than
fixing the specific wildcard mask error. The HITL Edit path allows engineers to correct the
precise misconfiguration without dropping security controls.
