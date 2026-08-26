# 11 — Packet Tracer Lab

## 1. Overview

The NetSage AI submission includes a fully documented Cisco Packet Tracer lab to demonstrate the end-to-end diagnostic workflow on a simulated network.

Demo Case: **NET-001**
Symptom: PC1 cannot reach Server1 in VLAN 30
Root Cause: The VLAN 30 router sub-interface (`GigabitEthernet0/0.30`) is administratively down.

---

## 2. Lab Artifacts

All necessary lab components are in the `packet_tracer/` directory:

- `NetSage_AI_NET001.pkt`: The binary Cisco Packet Tracer file.
- `README.md`: The complete build specification to recreate the lab.
- `router_config.txt`: The initial IOS configuration for the router (R1).
- `switch_config.txt`: The initial IOS configuration for the switch (SW1).
- `verification_commands.txt`: The commands to verify the fault and the fix.
- `net_sage_demo_input.txt`: Pre-formatted text to copy-paste into NetSage for the demo.
- `submission_checklist.md`: The 16-item checklist for the demo.

---

## 3. Topology Design

```text
PC1 (192.168.10.10/24, GW: 192.168.10.1)
  |
  +-- SW1 Fa0/1 (access, VLAN 10)
  
Server1 (192.168.30.10/24, GW: 192.168.30.1)
  |
  +-- SW1 Fa0/2 (access, VLAN 30)

SW1 Fa0/24 -----[trunk, VLANs 10,30]----- R1 Gi0/0
                                                |
                                          R1 Gi0/0.10 (192.168.10.1/24) — VLAN 10 GW
                                          R1 Gi0/0.30 (192.168.30.1/24) — SHUTDOWN (Fault)
```

---

## 4. IP Addressing Scheme

| Device | Interface | VLAN | IP Address | Subnet Mask | Default Gateway |
|---|---|---|---|---|---|
| PC1 | FastEthernet0 | 10 | 192.168.10.10 | 255.255.255.0 | 192.168.10.1 |
| Server1 | FastEthernet0 | 30 | 192.168.30.10 | 255.255.255.0 | 192.168.30.1 |
| R1 | Gi0/0.10 | 10 | 192.168.10.1 | 255.255.255.0 | - |
| R1 | Gi0/0.30 | 30 | 192.168.30.1 | 255.255.255.0 | - |

---

## 5. The Fault Injection

The fault is intentionally placed in the R1 configuration provided in `router_config.txt`:

```text
interface GigabitEthernet0/0.30
 encapsulation dot1Q 30
 ip address 192.168.30.1 255.255.255.0
 description VLAN30_GATEWAY
 ! INTENTIONAL FAULT FOR NET-001:
 shutdown
```

This ensures that any traffic destined for VLAN 30 is dropped by the router because the sub-interface is administratively down.

---

## 6. Verification & Resolution Steps

**Pre-Fix Verification (in Packet Tracer)**
From PC1 command prompt: `ping 192.168.30.10`
Result: 100% packet loss (Request timed out).

From R1 CLI: `show ip interface brief`
Result shows: `GigabitEthernet0/0.30 is administratively down, line protocol is down`

**NetSage AI Diagnosis**
The show output is fed into NetSage AI. The deterministic checker matches the rule `CHK_INT_ADMIN_DOWN`.
The AI proposes the fix:
```text
configure terminal
interface GigabitEthernet0/0.30
no shutdown
```

**Human Review & Application**
The engineer clicks "Approve & Deploy (Manual)" in the NetSage dashboard (recording the decision).
The engineer then types the commands manually into R1 in Packet Tracer.

**Post-Fix Verification (in Packet Tracer)**
From PC1 command prompt: `ping 192.168.30.10`
Result: 0% packet loss (Replies received).
