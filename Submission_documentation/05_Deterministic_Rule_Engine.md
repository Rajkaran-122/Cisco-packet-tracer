# 05 — Deterministic Rule Engine

## 1. Overview

File: src/checker.py (221 lines)
Entry point: run_checks(show_output: str) -> Dict[str, Any]
Design: Conservative — only flags faults when a known, high-confidence pattern matches.
        Never guesses. Falls through to LLM for anything it does not recognize.

---

## 2. How the Engine Works

run_checks() receives the raw show_output string from a dataset case.

For each of the 14 rules (in order):
  1. The rule's compiled regex pattern is searched across the entire string
  2. If a match is found, named capture groups are extracted
  3. The issue and remediation strings are formatted with the capture group values
  4. A flagged_issue dict is appended to the list

After all rules are checked, the function returns:
  {
    "status": "ERRORS_DETECTED" or "NO_ERRORS_DETECTED",
    "flagged_issues": [ {check_id, module, issue, osi_layer, remediation}, ... ]
  }

Key design decision: ALL matching rules are collected. engine.py uses only the FIRST
flagged_issue as the primary diagnosis when routing deterministic cases. Every match
is still recorded in the flagged_issues list for full inspection.

---

## 3. All 14 Active Rules

### Rule 1: CHK_INT_ADMIN_DOWN
Module: Physical / Link Layer
OSI Layer: Layer 1 / Layer 2
Pattern: \S+ is administratively down, line protocol is down
Triggered by: show interfaces output
Capture groups: {intf} — the interface name
Issue: "Interface {intf} is administratively shut down."
Remediation:
  configure terminal
  interface {intf}
  no shutdown
Dataset case: NET-001 (primary demo case)

### Rule 2: CHK_LINE_PROTOCOL_DOWN
Module: Physical / Link Layer
OSI Layer: Layer 1 / Layer 2
Pattern: \S+ is up, line protocol is down
Triggered by: show interfaces output
Capture groups: {intf}
Issue: "Interface {intf} is enabled but line protocol is down."
Remediation: show controllers {intf} + verify encapsulation and duplex
Dataset case: NET-012

### Rule 3: CHK_DUPLICATE_IP
Module: Network Layer (IP Addressing)
OSI Layer: Layer 3
Pattern: %IP-4-DUPADDR: Duplicate address \d+\.\d+\.\d+\.\d+ on \S+, sourced by MAC
Triggered by: show logging output
Capture groups: {ip}, {intf}, {mac}
Issue: "Duplicate IP address {ip} detected on {intf} conflicting with MAC {mac}."
Remediation: shutdown interface, reassign unique IP, no shutdown
Dataset case: NET-013

### Rule 4: CHK_NATIVE_VLAN_MISMATCH
Module: Data Link Layer (Trunking)
OSI Layer: Layer 2
Pattern: native vlan mismatch
Triggered by: CDP syslog message
Issue: "Native VLAN mismatch detected on a trunk link."
Remediation: switchport trunk native vlan <id> on both ends
Dataset case: NET-002

### Rule 5: CHK_VLAN_NOT_IN_DATABASE
Module: Data Link Layer (VLAN)
OSI Layer: Layer 2
Pattern: vlan \d+ not found in current vlan database
Triggered by: IOS config-mode error
Capture groups: {vlan}
Issue: "VLAN {vlan} is referenced but does not exist in the VLAN database."
Remediation: configure terminal + vlan {vlan} + name
Dataset case: NET-003

### Rule 6: CHK_TRUNK_VLAN_NOT_ALLOWED
Module: Data Link Layer (Trunking)
OSI Layer: Layer 2
Pattern: vlan \d+ (?:is )?not allowed on (?:this )?trunk
Triggered by: show interfaces switchport
Capture groups: {vlan}
Issue: "VLAN {vlan} is pruned from the trunk's allowed list."
Remediation: switchport trunk allowed vlan add {vlan}
Dataset case: NET-004

### Rule 7: CHK_OSPF_NO_NEIGHBORS
Module: Network Layer (Routing)
OSI Layer: Layer 3
Pattern: show ip ospf neighbor\s*\n\s*(?:\n|$)
Triggered by: empty show ip ospf neighbor output (with command echo)
Issue: "No OSPF neighbors are listed on the expected interface."
Remediation: verify area IDs and network statements
Dataset case: NET-005
NOTE: Requires command echo in the captured output

### Rule 8: CHK_NETWORK_UNREACHABLE
Module: Network Layer (Routing)
OSI Layer: Layer 3
Pattern: % network is unreachable|destination host unreachable
Triggered by: ping failure output
Issue: "Destination network is unreachable; routing table likely missing a route."
Remediation: show ip route + add missing static or dynamic route
Dataset case: NET-006

### Rule 9: CHK_NAT_NO_TRANSLATIONS
Module: Network Layer (NAT)
OSI Layer: Layer 3
Pattern: show ip nat translations\s*\n\s*Pro\s+Inside global[^\n]*\n(?![^\n]*\d+\.\d+\.\d+\.\d+)
Triggered by: empty show ip nat translations output
Issue: "No active NAT translations exist; inside/outside roles or NAT ACL may be misconfigured."
Remediation: show ip nat statistics + confirm interface roles
Dataset case: NET-007
NOTE: Complex multi-line pattern — requires exact formatting

### Rule 10: CHK_DHCP_POOL_EXHAUSTED
Module: Application / Service Layer (DHCP)
OSI Layer: Layer 7 (Service)
Pattern: 0 leases? available|pool.*exhausted
Triggered by: show ip dhcp pool
Issue: "The DHCP pool has no available leases remaining."
Remediation: Expand pool or remove stale excluded-address entries
Dataset case: NET-008

### Rule 11: CHK_PORT_ERR_DISABLED
Module: Data Link Layer (Port Security)
OSI Layer: Layer 2
Pattern: err-disabled|%PM-4-ERR_DISABLE
Triggered by: show interfaces status or syslog
Issue: "Port has been placed into err-disabled state from a port-security violation."
Remediation: shutdown + no shutdown after confirming and removing offending device
Dataset case: NET-009

### Rule 12: CHK_DUPLEX_MISMATCH
Module: Physical Layer
OSI Layer: Layer 1
Pattern: %CDP-4-DUPLEX_MISMATCH|duplex mismatch
Triggered by: CDP syslog
Issue: "A duplex mismatch was detected between two connected interfaces."
Remediation: Set matching duplex/speed or auto on both ends
Dataset case: NET-010

### Rule 13: CHK_IP_ROUTING_DISABLED
Module: Network Layer (Multilayer Switching)
OSI Layer: Layer 3
Pattern: ip routing:?\s+is\s+disabled|ip routing\s*:\s*disabled
Triggered by: show ip protocols
Issue: "IP routing is globally disabled on this multilayer switch."
Remediation: configure terminal + ip routing
Dataset case: NET-011

### Rule 14: CHK_BAD_MASK_OR_OVERLAP
Module: Network Layer (IP Addressing)
OSI Layer: Layer 3
Pattern: % (?:Bad mask|Inconsistent address and mask|Overlapping subnet)
Triggered by: IOS config-mode error when entering wrong subnet mask
Issue: "Subnet mask mismatch or invalid address-mask combination configured."
Remediation: Verify correct prefix and reconfigure interface
NOTE: This rule is NOT mentioned in the README (README incorrectly states 13 rules).
      The rule is fully functional and active in checker.py.

---

## 4. Rule Engine Output Format

{
  "status": "ERRORS_DETECTED",         <- or "NO_ERRORS_DETECTED"
  "flagged_issues": [
    {
      "check_id":    "CHK_INT_ADMIN_DOWN",
      "module":      "Physical / Link Layer",
      "issue":       "Interface GigabitEthernet0/0.30 is administratively shut down.",
      "osi_layer":   "Layer 1 / Layer 2",
      "remediation": "configure terminal\ninterface GigabitEthernet0/0.30\nno shutdown"
    }
  ]
}

---

## 5. False Positive / False Negative Assessment

| Rule | False Positive Risk | False Negative Risk | Notes |
|---|---|---|---|
| CHK_INT_ADMIN_DOWN | Very Low | Low | Very specific pattern |
| CHK_LINE_PROTOCOL_DOWN | Low | Medium | Encapsulation mismatch may not trigger |
| CHK_DUPLICATE_IP | Very Low | Medium | Requires syslog message to be present |
| CHK_NATIVE_VLAN_MISMATCH | Low | Medium | Requires CDP to be enabled |
| CHK_VLAN_NOT_IN_DATABASE | Very Low | Low | IOS always prints this exact error |
| CHK_TRUNK_VLAN_NOT_ALLOWED | Low | Low | Multiple trigger patterns covered |
| CHK_OSPF_NO_NEIGHBORS | Medium | Medium | Requires command echo in captured text |
| CHK_NETWORK_UNREACHABLE | Low | Medium | Percentage sign required |
| CHK_NAT_NO_TRANSLATIONS | High | Medium | Complex multi-line regex fragile |
| CHK_DHCP_POOL_EXHAUSTED | Low | Low | Clear numeric pattern |
| CHK_PORT_ERR_DISABLED | Very Low | Low | Both syslog and status formats covered |
| CHK_DUPLEX_MISMATCH | Very Low | Medium | CDP required |
| CHK_IP_ROUTING_DISABLED | Very Low | Low | Clear IOS output |
| CHK_BAD_MASK_OR_OVERLAP | Very Low | High | Only IOS error messages, not manual review |
