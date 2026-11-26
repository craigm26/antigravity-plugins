---
name: graft-robotics
description: Pair Claude, Antigravity, Codex, Gemini, Apple MLX, or local Gemma 4 safely with physical robots using Graft Robotics (graftrobotics.ai). Supports self-serve Remote Shop Onboarding (/remote-shop-onboarding & graft_generate_onboarding_kit), MCP App Workbench, MCP Form Elicitations for L0-L3, Semantic Ratchet & Onboarding sign-off, 6 operational Playbooks (MCP Prompts + slash commands), live MCP Resources, Rust graft-core LAN LiDAR meshing, 6-family Hand HAL mechanics, and RoboCurve SET-Sim rehearsal.
---

# Graft Robotics Plugin (`v0.4.0`)

Graft puts a deterministic, default-deny software pre-flight boundary, live multi-sensor MuJoCo 4.0 World Model, Semantic-to-Deterministic Ratchet, 6-family Hand HAL mechanics engine, and progressive `L0 -> L3` Trust Ladder between any frontier or local LLM and physical robots.

> **Mandatory Safety Boundary:** `robot-gate`, `graft-core`, `graft-watchdog`, `bounded-embodiment`, and `robot-md-gateway` are deterministic software enforcement and RFC 8785 / SHA-256 audit layers — **never** replacements for certified hardwired ISO 13850 shop E-stops or ISO 13849-1 safety relays.

## Self-Serve Remote Shop Onboarding (Zero FDE / Zero Machinist Required)
- **Slash Command & MCP Prompt (`/remote-shop-onboarding` · `remote_shop_onboarding`):** Turns Claude, Antigravity, Codex, Apple MLX, or local Gemma 4 into a plain-English Remote Shop Onboarding Specialist across all 5 user tracks (`cnc`, `lab`, `oem`, `benchtop`, `ehs`) in `quick` or `advanced` depth — guiding phone-photo hazard & keep-out identification, hardwired ISO 13850 / ISO 13849-1 verification, 6-family Hand HAL selection, and a 48-hour zero-motion `L0 OBSERVE` shadow trial.
- **MCP Tool (`graft_generate_onboarding_kit`):** Generates a complete ready-to-use onboarding kit (`ROBOT.md` v1.1 starting in `L0_OBSERVE`, `uv`-first install commands, tailored LLM coach prompt, 48-hour `L0` shadow trial plan, ISO 13850 safety boundary note, and link to `https://graftrobotics.ai/onboard/`), with native MCP Form Elicitation (`RemoteOnboardingElicitation`).
- **Companion Surfaces:** Web studio at [https://graftrobotics.ai/onboard/](https://graftrobotics.ai/onboard/) and offline CLI wizard `robot-gate onboard`.

## Capabilities Included
- **MCP App (`ui://graft-robotics/workbench.html`):** Interactive Workbench side-pane / inline UI (`open_graft_workbench`).
- **MCP Form Elicitations (`ctx.elicit`):** Native operator confirmation forms before:
  - Promoting a robot on the Trust Ladder (`graft_trust_ladder(action="promote")`)
  - Resolving an `L1` Semantic Ratchet escalation on unlabeled objects (`graft_check_semantic_action`)
  - Interactive Skill Pack scaffolding (`graft_install_skill_pack(pack_id="interactive")`)
  - Interactive Remote Shop Onboarding kit generation (`graft_generate_onboarding_kit(interactive=True)`)
- **6 Operational Playbooks (MCP Prompts + Claude Code `/graft-robotics:*` commands):**
  - `remote-shop-onboarding` (MCP Prompt: `remote_shop_onboarding`)
  - `shift-start-preflight`
  - `cnc-cell-onboarding`
  - `shadow-trial-audit`
  - `semantic-hazard-ratchet`
  - `incident-estop-recovery`
- **5 Live MCP Resources:** `ui://graft-robotics/workbench.html`, `graft://world-model/live`, `graft://trust-ladder/status`, `graft://benchmarks/latest`, `graft://safety/boundary-policy`.
- **PreToolUse Guardrail Hook (`hooks/hooks.json`):** Reinforces ISO 13850 hardware E-stop & signed `ROBOT.md` checks before physical-robot MCP calls.
- **15 MCP Tools:** Remote Shop Onboarding Kit Generator (`graft_generate_onboarding_kit`), World Model, LAN LiDAR `.obj` meshing (Rust `graft-core`), Material Crush/Slip Mechanics, Semantic Ratchet, Trust Ladder, Ambient Wi-Fi/Audio/Video Discovery, Envelope 0.2 Verifier, Job Skill Packs, `uv`-first Client Bundles, and RoboCurve SET-Sim Rehearsal (`graft_run_set_benchmark`).
