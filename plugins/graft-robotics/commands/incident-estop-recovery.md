---
description: Post-fault or post-E-stop isolation, Trust Ladder demotion check, and verified re-arm checklist.
---

Run the `incident-estop-recovery` playbook:
1. Confirm the physical ISO 13850 hardware E-stop condition has been physically resolved by an authorized operator.
2. Read `graft://world-model/live` and `graft://trust-ladder/status` to verify fail-closed auto-demotion to `L1`.
3. Call `graft_discover_devices` and `graft_world_model_status` to confirm all LAN/local sensors are fresh.
4. Use `graft_trust_ladder(action="promote")` (with MCP Elicitation sign-off) only after clean verified runs.
