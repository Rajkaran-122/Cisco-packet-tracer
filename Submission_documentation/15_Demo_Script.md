# 15 — Live Demo Script

This script provides a step-by-step guide for presenting NetSage AI during a technical viva or evaluation demo.

## Pre-Demo Setup

1. **Launch Streamlit**: Open a terminal, run `streamlit run src/app.py`, and have the dashboard open in a browser.
2. **Open Packet Tracer**: Open `packet_tracer/NetSage_AI_NET001.pkt` in Cisco Packet Tracer.
3. **Open Notepad**: Have `packet_tracer/net_sage_demo_input.txt` ready to copy from.

---

## Step 1: Context Setting (1 min)
*Goal: Explain what the project is and the safety boundary.*

**Script:**
> "Welcome to the NetSage AI demo. NetSage AI is a troubleshooting co-pilot for network engineers. It uses a hybrid architecture: a deterministic regex engine for fast, zero-cost known faults, and an LLM fallback for complex reasoning. Most importantly, it operates behind a mandatory Human-in-the-Loop safety gate. It NEVER executes commands autonomously."

---

## Step 2: The Fault (2 mins)
*Goal: Prove the network is broken in Packet Tracer.*

**Action**: Switch to Cisco Packet Tracer.
**Script:**
> "Here is our lab topology. PC1 in VLAN 10 needs to reach Server1 in VLAN 30. R1 is our router-on-a-stick gateway."
**Action**: Open PC1 Command Prompt and type `ping 192.168.30.10`.
**Script:**
> "As you can see, the ping fails with 100% packet loss. There is a fault."
**Action**: Open R1 CLI and type `show ip interface brief`.
**Script:**
> "As an engineer, I pull the basic logs. The router shows that `GigabitEthernet0/0.30` is administratively down."

---

## Step 3: AI Diagnosis (2 mins)
*Goal: Show NetSage diagnosing the fault.*

**Action**: Switch to the NetSage Streamlit dashboard (Tab 1).
**Action**: Select "NET-001" from the dropdown. (The evidence box is pre-populated, but you can explain this is where the engineer pastes the output).
**Action**: Click the "Run Diagnostic" button.
**Script:**
> "I feed this evidence into NetSage. Because this is a known fault signature, the deterministic checker catches it instantly. No API call was made. We have a 100% confidence diagnosis: the interface is shut down. The AI proposes the fix: `configure terminal`, `interface Gi0/0.30`, `no shutdown`."

---

## Step 4: The HITL Gate & Safety (2 mins)
*Goal: Demonstrate the approval workflow and audit logging.*

**Script:**
> "Notice the three buttons at the bottom. The 'Approve' button is only enabled because the confidence is above 0.75 and the proposed commands passed the `safety.py` guardrail check. If the AI had proposed `reload` or `write erase`, this button would be physically disabled."
**Action**: Click "Approve & Deploy (Manual)".
**Script:**
> "I agree with the fix, so I approve it. The UI notifies us that the decision was logged to the audit trail."
**Action**: Switch to Tab 4 (Responsible AI & Audit Trail).
**Script:**
> "Here in the audit log, we have a permanent, timestamped record that I approved this specific fix for NET-001. The dashboard metrics update in real-time."

---

## Step 5: Resolution (2 mins)
*Goal: Prove the fix works.*

**Action**: Switch back to Cisco Packet Tracer.
**Script:**
> "Because NetSage enforces a human safety boundary, it did not execute the command. I will apply the approved fix manually."
**Action**: Type the fix on R1:
```text
configure terminal
interface GigabitEthernet0/0.30
no shutdown
```
**Script:**
> "The line protocol comes up. Let's verify."
**Action**: Open PC1 and re-run `ping 192.168.30.10`.
**Script:**
> "The ping succeeds. The fault is resolved. The workflow is complete."

---

## Step 6: Explore the Dashboard (1 min)
*Goal: Show the remaining evaluation requirements.*

**Action**: Click through Tabs 2 and 3 quickly.
**Script:**
> "Beyond the diagnostic lab, the platform includes a full analytics dashboard showing our dataset distribution by domain and OSI layer, the full 33-case dataset explorer, and 5 documented responsible AI case studies detailing where human review prevented AI mistakes."
