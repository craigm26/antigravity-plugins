---
description: Run the mandatory Graft Robotics shift-start pre-flight checklist (zero motion until verified).
---

Run the `shift-start-preflight` playbook using the Graft Robotics MCP tools:
1. Read MCP resource `graft://safety/boundary-policy` and remind the operator that software checks never replace hardwired ISO 13850 E-stops.
2. Call `graft_discover_devices` and `graft_world_model_status` to check local/LAN LiDAR, Wi-Fi CSI, microphone, and camera freshness.
3. Validate `./envelope.json` (if present) via `graft_verify_envelope`.
4. Inspect `graft_trust_ladder(action="status")` and summarize readiness clearly before authorizing any motion.
