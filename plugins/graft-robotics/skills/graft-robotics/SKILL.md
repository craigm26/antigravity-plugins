---
name: graft-robotics
description: Pair Claude, Antigravity, Codex, Gemini, or an offline local LLM safely with physical robots using Graft Robotics (graftrobotics.ai). Supports MCP App Workbench, MCP Form Elicitations for L0-L3 & Semantic Ratchet sign-off, 5 operational Playbooks (MCP Prompts + slash commands), live MCP Resources, Rust graft-core LAN LiDAR meshing, material mechanics, and RoboCurve SET-Sim rehearsal.
---

# Graft Robotics Plugin (`v0.4.0`)

Graft puts a deterministic, default-deny software pre-flight boundary, live multi-sensor MuJoCo 4.0 World Model, Semantic-to-Deterministic Ratchet, and progressive `L0 -> L3` Trust Ladder between any frontier or local LLM and physical robots.

> **Mandatory Safety Boundary:** `robot-gate`, `graft-core`, `graft-watchdog`, `bounded-embodiment`, and `robot-md-gateway` are deterministic software enforcement and RFC 8785 / SHA-256 audit layers — **never** replacements for certified hardwired ISO 13850 shop E-stops or ISO 13849-1 safety relays.

## Capabilities Included
- **MCP App (`ui://graft-robotics/workbench.html`):** Interactive Workbench side-pane / inline UI (`open_graft_workbench`).
- **MCP Form Elicitations (`ctx.elicit`):** Native operator confirmation forms before:
  - Promoting a robot on the Trust Ladder (`graft_trust_ladder(action="promote")`)
  - Resolving an `L1` Semantic Ratchet escalation on unlabeled objects (`graft_check_semantic_action`)
  - Interactive Skill Pack scaffolding (`graft_install_skill_pack(pack_id="interactive")`)
- **5 Operational Playbooks (MCP Prompts + Claude Code `/graft-robotics:*` commands):**
  - `shift-start-preflight`
  - `cnc-cell-onboarding`
  - `shadow-trial-audit`
  - `semantic-hazard-ratchet`
  - `incident-estop-recovery`
- **5 Live MCP Resources:** `ui://graft-robotics/workbench.html`, `graft://world-model/live`, `graft://trust-ladder/status`, `graft://benchmarks/latest`, `graft://safety/boundary-policy`.
- **PreToolUse Guardrail Hook (`hooks/hooks.json`):** Reinforces ISO 13850 hardware E-stop & signed `ROBOT.md` checks before physical-robot MCP calls.
- **14 MCP Tools:** World Model, LAN LiDAR `.obj` meshing (Rust `graft-core`), Material Crush/Slip Mechanics, Semantic Ratchet, Trust Ladder, Ambient Wi-Fi/Audio/Video Discovery, Envelope 0.2 Verifier, Job Skill Packs, `uv`-first Client Bundles, and RoboCurve SET-Sim Rehearsal (`graft_run_set_benchmark`).
