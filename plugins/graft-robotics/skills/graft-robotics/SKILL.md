---
name: graft-robotics
description: Pair Claude, Antigravity, Codex, Gemini, or an offline local LLM safely with physical robots using Graft Robotics (graftrobotics.ai). Use when opening the Graft Robotics Workbench MCP App, inspecting multi-sensor world models and live LAN LiDAR obstacle meshes, checking material crush/slip/payload mechanics, advancing the L0-L3 Trust Ladder, or generating a client deployment bundle for any LLM tool and budget.
---

# Graft Robotics Skill (`graftrobotics.ai`)

Use the bundled `graft-robotics` MCP App tools whenever pairing an LLM with physical arms, industrial cobots, CNC tending cells, or humanoids:

- **`open_graft_workbench()`**: Opens the interactive **Graft Robotics Workbench** MCP App (`aux_pane` / `global` / Claude MCP App) showing live World Model state, networked LAN sensors & reconstructed MuJoCo 4.0 meshes, progressive `L0 -> L3` Trust Ladder, and a client LLM + budget bundle generator.
- **`graft_world_model_status()`**: Reads live KNOWN/UNKNOWN entities, active LAN sensors, reconstructed `.obj` obstacle meshes, and Trust Ladder status (connects to a running local CNC cell runner on `:8791` when available).
- **`graft_check_part_mechanics(actor, part_id, grip_force_n, bimanual, coolant_wet)`**: Runs deterministic payload, wrist torque, jaw width, material crush-limit, and dry vs. coolant-wet Coulomb friction slip checks BEFORE grasping.
- **`graft_ingest_lan_lidar(sensor_id, x, y, z, half_size_m, mesh_id)`**: Ingests a point cloud from any networked shop PC LiDAR into a live `.obj` collision mesh and verifies swept paths in MuJoCo 4.0.
- **`graft_trust_ladder(action, robot_id, operator)`**: Inspects, promotes (evidence-gated), or demotes a robot across `L0 OBSERVE -> L1 ATOMIC ASSIST -> L2 SUPERVISED CHAIN -> L3 AUTONOMOUS FROZEN`.
- **`graft_verify_envelope(envelope_path)`**: Validates a physical Envelope 0.2 JSON file against the public RRF `bounded-embodiment` schema and computes its RFC 8785 JCS SHA-256 digest.
- **`graft_recommend_bundle(llm_provider, budget_tier, hardware_target)`**: Outputs the exact install script and client config for Claude Desktop/Code, Antigravity, OpenAI Codex, Gemini CLI, or 100% offline air-gapped Ollama on Raspberry Pi 5 / Jetson.

## Operating Principles
1. **Use every sensor on the shop LAN:** Fuse local RGB-D, wrist F/T, PLC I/O, and any networked LiDAR into live collision meshes.
2. **Respect physical mechanics:** Enforce known yield strength, crush limits (e.g. cardboard `45 N`), payload caps, and wet-coolant friction.
3. **Earn trust incrementally:** Start Day 1 at `L0/L1` (small-object picks at 30% speed with HiTL approval) before graduating to autonomous frozen YAML skills.
4. **Honest safety boundary:** Always pair software enforcement with hardwired ISO 13850 shop emergency stops.
