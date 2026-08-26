# NetSage AI — Submission Documentation Index

> **Industry Problem Statement**: *NetSage AI – Build an AI troubleshooting helper with human review*
> **Date**: August 2026 | **Version**: 1.0.1

---

## Document Navigation

| # | Document | Purpose |
|---|---|---|
| 01 | 01_Project_Overview.md | What is NetSage AI, goals, features |
| 02 | 02_System_Architecture.md | Full technical architecture with data-flow diagrams |
| 03 | 03_Dataset_Design.md | All 33 cases, columns, coverage, quality analysis |
| 04 | 04_AI_Prompt_Design.md | Prompt structure, JSON schema, few-shot examples |
| 05 | 05_Deterministic_Rule_Engine.md | All 14 checker rules, logic, inputs, outputs |
| 06 | 06_LLM_Reasoning_Layer.md | Claude integration, confidence gate, schema validation |
| 07 | 07_Safety_Guardrails.md | Blocked commands, policy design, enforcement points |
| 08 | 08_Human_in_the_Loop_Review.md | HITL gate implementation, Approve/Edit/Reject workflow |
| 09 | 09_Responsible_AI.md | 5 case studies of AI corrections by humans |
| 10 | 10_Dashboard_Guide.md | All 5 dashboard tabs, metrics, data sources |
| 11 | 11_Packet_Tracer_Lab.md | NET-001 topology, fault, fix, verification |
| 12 | 12_Test_Report.md | All 7 tests with results and coverage analysis |
| 13 | 13_Setup_and_Running.md | Installation, configuration, launch instructions |
| 14 | 14_Requirement_Compliance_Matrix.md | Official requirements vs. evidence |
| 15 | 15_Demo_Script.md | Step-by-step demonstration guide for live viva |

---

## Official Requirements Quick Checklist

| Requirement | Status | Evidence |
|---|---|---|
| 30+ troubleshooting cases | COMPLETE — 33 cases | data/cases.csv |
| Evidence per case (6 fields) | COMPLETE — 8 columns | data/cases.csv header |
| Structured AI prompt library | COMPLETE — JSON schema + 3 examples | prompts/diagnose_prompt.md |
| Python deterministic rule checker | COMPLETE — 14 regex rules | src/checker.py |
| Dashboard (issue types/severity/agreement) | COMPLETE — 5-tab Streamlit app | src/app.py |
| Responsible AI log (5+ AI-correction cases) | COMPLETE — 5 case studies | docs/responsible_ai_log.md |
| Demo: broken to fix to verify | COMPLETE — NET-001 end-to-end | packet_tracer/ + Tab 5 |
| Mandatory human review | COMPLETE — HITL gate enforced | src/app.py L279-335 |
