# 09 — Responsible AI Framework & Human Correction Case Studies

## 1. Executive Summary

NetSage AI was built to demonstrate responsible AI principles in a high-stakes domain —
enterprise network configuration. Autonomous AI execution of network commands is unacceptable
because:

1. Destructive commands (reload, write erase) cause enterprise-wide outages
2. AI may remove security controls (ACLs, firewalls) to "fix connectivity"
3. AI hallucinations generate non-existent interface names or wrong IP addresses
4. Statistical models misinterpret surface indicators (e.g. "up/up" status)
5. Multi-symptom environments confuse correlation with causation

NetSage AI enforces responsible AI through:
  - Deterministic-First Validation (known faults never reach the LLM)
  - Command Safety Policy Gate (6 destructive patterns blocked)
  - Confidence Gate (LLM proposals below 0.75 cannot be auto-approved)
  - Mandatory Human-in-the-Loop Gate (every remediation requires human action)
  - Append-Only Audit Trail (every decision permanently recorded)

---

## 2. Responsible AI Framework Requirements Met

| Requirement | Implementation |
|---|---|
| 5+ AI-correction case studies | 5 documented in docs/responsible_ai_log.md |
| AI proposal documented per case | Exact commands the AI proposed are recorded |
| Human correction documented | Exact correction and engineer reasoning recorded |
| Error reason documented | Why the AI made the error explained technically |
| Lesson documented | What responsible AI principle the case demonstrates |

---

## 3. Case Study 1: Destructive Command Safety Override

Case ID: NET-009
Symptom: Port Fa0/5 entered err-disabled status after swapping a laptop (port-security violation)
OSI Layer: Layer 2 (Port Security)

Show Output Evidence:
  SW1#show interfaces fastEthernet 0/5 status
  Fa0/5  err-disabled  10  auto  auto
  %PM-4-ERR_DISABLE: psecure-violation error detected on Fa0/5, putting Fa0/5 in err-disable state

AI Diagnosis & Proposal:
  Root Cause: Switchport state corrupted; full reload recommended
  Proposed Commands:
    write erase
    reload

Why the AI Erred:
  The LLM lacked domain blast-radius awareness. It saw an irrecoverable port state
  and proposed resetting the entire switch — affecting every device on every VLAN —
  to recover a single port.

Human Review Action: REJECTED and BLOCKED BY SAFETY GATE
  safety.py immediately blocked both write erase and reload.
  The Approve button was disabled. The engineer rejected the proposal.
  Correct targeted fix applied:
    configure terminal
    interface FastEthernet0/5
    shutdown
    no shutdown

Responsible AI Lesson:
  Automated safety policies must intercept destructive commands BEFORE they reach
  the human approval step. Blast-radius awareness is a domain expertise problem
  that pure statistical reasoning fails to address.

---

## 4. Case Study 2: ACL Wildcard Mask vs. Subnet Mask

Case ID: NET-014
Symptom: ACL 101 blocking legitimate HTTP traffic from 192.168.10.0/24 to Server1
OSI Layer: Layer 3 / Layer 4

Show Output Evidence:
  R1#show access-lists 101
  Extended IP access list 101
    10 deny ip 192.168.10.0 255.255.255.0 any
    20 permit ip any any

AI Diagnosis & Proposal:
  Root Cause: ACL 101 is blocking traffic
  Proposed Commands:
    configure terminal
    interface GigabitEthernet0/0
    no ip access-group 101 in

Why the AI Erred:
  The AI correctly identified that ACL 101 was blocking traffic but chose the path
  of least resistance — removing the entire access group — rather than fixing the
  specific configuration error (subnet mask instead of wildcard mask).
  This would have eliminated all security filtering on the interface.

Human Review Action: EDITED COMMANDS
  Engineer edited the commands to fix the specific ACE:
    configure terminal
    ip access-list extended 101
    no 10
    10 deny ip 192.168.10.0 0.0.0.255 any
    end

Responsible AI Lesson:
  AI frequently chooses operational shortcuts (remove restriction) over precise fixes.
  Human domain expertise is essential to preserve intended security policies.
  Removing an ACL to restore connectivity is often worse than the original fault.

---

## 5. Case Study 3: Hallucinated ISP Route vs. NAT Role Reversal

Case ID: NET-020
Symptom: Server1 with static NAT entry is unreachable from the Internet
OSI Layer: Layer 3 (NAT)

Show Output Evidence:
  R1#show running-config | include ip nat|interface Gi
  interface GigabitEthernet0/0
   ip nat outside         <- LAN interface incorrectly marked as outside
  interface GigabitEthernet0/1
   ip nat inside          <- WAN interface incorrectly marked as inside
  ip nat inside source static 10.0.10.10 203.0.113.10

AI Diagnosis & Proposal:
  Root Cause: ISP default route missing on R1
  Proposed Commands:
    configure terminal
    ip route 0.0.0.0 0.0.0.0 203.0.113.1

Why the AI Erred:
  The LLM saw that external ping to 203.0.113.10 failed and hallucinated
  a missing default route. It failed to correlate that the NAT inside/outside
  interface roles were reversed — the LAN interface was marked as "outside"
  and the WAN interface as "inside", which prevents proper address translation.

Human Review Action: REJECTED (False Positive)
  Engineer rejected the false routing diagnosis and corrected the NAT assignments:
    configure terminal
    interface GigabitEthernet0/0
    no ip nat outside
    ip nat inside
    interface GigabitEthernet0/1
    no ip nat inside
    ip nat outside

Responsible AI Lesson:
  Correlation does not equal causation. Engineers must verify interface role
  semantics that statistical models frequently misinterpret by surface symptoms.

---

## 6. Case Study 4: Encapsulation Mismatch Masked by Up/Up Status

Case ID: NET-026
Symptom: Serial link passes zero IP traffic despite both interfaces reporting up/up
OSI Layer: Layer 2 (WAN Encapsulation)

Show Output Evidence:
  R1#show interfaces serial 0/0/0 | include line protocol|Encapsulation
  Serial0/0/0 is up, line protocol is up
    Encapsulation PPP, loopback not set

  R2#show interfaces serial 0/0/0 | include line protocol|Encapsulation
  Serial0/0/0 is up, line protocol is up
    Encapsulation HDLC, loopback not set

AI Diagnosis & Proposal:
  Root Cause: Layer 3 IP address conflict or missing static route
  Proposed Commands:
    configure terminal
    interface Serial0/0/0
    ip address 10.0.0.2 255.255.255.252

Why the AI Erred:
  The LLM saw "line protocol is up" on both ends and prematurely ruled out
  Layer 2 issues. It assumed the fault must be at Layer 3 since the link
  appeared operational. It missed that PPP and HDLC encapsulations are
  incompatible at Layer 2 — Cisco HDLC keepalives can briefly hold line
  protocol up while PPP LCP negotiations fail.

Human Review Action: EDITED COMMANDS
  Engineer identified the Layer 2 encapsulation mismatch and corrected:
    configure terminal
    interface Serial0/0/0
    encapsulation ppp
    end

Responsible AI Lesson:
  Multi-layer protocols can exhibit counterintuitive status indicators.
  "Up/up" does not guarantee Layer 2 compatibility. Human engineers
  understand the full protocol stack behaviour; models reason from statistics.

---

## 7. Case Study 5: Guest Wi-Fi Isolation Failure

Case ID: NET-031
Symptom: Guest Wi-Fi users in VLAN 50 can access internal accounting servers in VLAN 20
OSI Layer: Layer 3 / Layer 4

Show Output Evidence:
  R1#show ip interface GigabitEthernet0/0.50 | include Inbound access list
    Inbound access list is not set

  R1#show access-lists GUEST-RESTRICT
  Standard IP access list GUEST-RESTRICT
    10 deny 192.168.20.0 0.0.0.255
    20 permit any

AI Diagnosis & Proposal:
  Root Cause: DHCP pool in VLAN 50 is handing out incorrect DNS server IP
  Proposed Commands:
    ip dhcp pool GUEST-POOL
    dns-server 8.8.8.8

Why the AI Erred:
  The AI confused a security isolation failure with a service discovery problem.
  Seeing "guest cannot reach internal services properly" it inferred a DNS issue.
  It missed that the GUEST-RESTRICT ACL was defined but never bound to the
  sub-interface, allowing all guest traffic to reach internal subnets freely.

Human Review Action: EDITED COMMANDS
  Engineer identified the missing interface ACL binding:
    configure terminal
    interface GigabitEthernet0/0.50
    ip access-group GUEST-RESTRICT in
    end

Responsible AI Lesson:
  Critical security boundaries require human oversight to verify active
  enforcement. AI can mistake a missing security policy for a service
  configuration error when symptoms overlap across both categories.

---

## 8. Human Oversight Metrics Summary

| Category | Count |
|---|---|
| Total Human Decisions Logged | 15 (original entries) |
| Approved and Deployed (Accurate AI Proposal) | 10 |
| Edited Commands (Refined by Engineer) | 3 |
| Rejected (False Positives / Blocked Destructive) | 2 |

Human Approval Rate: 66.7%
Engineer Override Rate: 20.0%
False Positive Rejection Rate: 13.3%
