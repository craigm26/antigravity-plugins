---
name: graft-robotics
description: Pair Claude Code, Antigravity, Codex CLI, Gemini CLI, Apple Silicon MLX, or local Gemma 4 safely with physical robots using Graft Robotics v0.5.0 (graftrobotics.ai). Supports 19 MCP tools (ROS 2 launch bundle generator graft_ros2_generate_bundle, opt-in Cloudflare D1 Fleet Vault status graft_vault_status, universal 6-client Agent Connect graft_connect_agent, 1-click ISO 10218:2025 & EU 2023/1230 Compliance Dossier ZIP graft_generate_compliance_pack, self-serve Remote Shop Onboarding), live Wedge A-Upmarket MCP App Workbench, 4 fail-closed MCP Form Elicitations, 7 operational Playbooks (incl. /ros2-compliance-audit), 5 live MCP Resources, Rust graft-core continuous swept-path & LAN LiDAR meshing, and 6-family Hand HAL mechanics.
---

# Graft Robotics Plugin (`v0.5.0`)

Graft puts a deterministic, default-deny software pre-flight boundary (`graft-core` Rust continuous slab kernel + `graft-watchdog`), ROS 2 Pre-Flight Interceptor, ISO 10218:2025 & EU (2023/1230) Compliance Dossier engine, Semantic-to-Deterministic Ratchet, 6-family Hand HAL mechanics engine, and fail-closed progressive `L0 -> L3` Trust Ladder between any frontier or local LLM and physical robots.

> **Mandatory Safety Boundary:** `robot-gate`, `graft-core`, `graft-watchdog`, `bounded-embodiment`, and `robot-md-gateway` are deterministic software enforcement and RFC 8785 / SHA-256 audit layers claiming **ZERO** PL/SIL credit — **never** replacements for certified hardwired ISO 13850 shop E-stops or ISO 13849-1 safety relays.
>
> **ITAR / EAR Export-Control Boundary:** For ITAR (`22 CFR Parts 120-130`) or EAR (`15 CFR Parts 730-774`) workcells, use local air-gapped Apple Silicon MLX or Google Gemma 4 / Ollama and leave `GRAFT_VAULT_API_KEY` unset (100% zero phone-home).

## Connect Any LLM to Any Robot (`v0.5.0`)
- **`graft_connect_agent(client, robot, environment, include_vault)`:** Generates exact copy-paste client configs for **Claude Code** (`.mcp.json`), **Google Antigravity** (`mcp_config.json`), **OpenAI Codex CLI** (`~/.codex/config.toml`), **Gemini CLI** (`gemini-extension.json`), **Apple Silicon MLX** (air-gapped LAN), and **Google Gemma 4 / Ollama** (air-gapped edge), plus an `L0 OBSERVE` starter prompt and mandatory ISO 13850 & ITAR/EAR boundaries. Companion studio: [https://graftrobotics.ai/connect/](https://graftrobotics.ai/connect/).
- **`graft_ros2_generate_bundle(workspace_dir, output_dir, stack, embodiment, frame_id)`:** Generates a drop-in ROS 2 pre-flight boundary launch bundle (`graft_ros2_gate.launch.py`, `graft_ros2_params.yaml`, `README_ROS2.md`) for MoveIt 2, UR RTDE, Fairino FR5, and xArm6.
- **`graft_vault_status(robot_id, limit)`:** Queries the opt-in Cloudflare D1 Hosted Fleet Vault for compliance receipts and drift alerts — strictly zero phone-home (`offline: true`, 0 network calls) when `GRAFT_VAULT_API_KEY` is unset.

## Self-Serve Remote Shop Onboarding & ROS 2 Compliance Audit
- **Slash Command & MCP Prompt (`/ros2-compliance-audit` · `ros2-compliance-audit`):** Guides teams end-to-end through `ros2-bridge` -> `check` -> `compliance-pack --verify` -> opt-in `vault push` -> Cloudflare-only `robot-gate/ci/cloudflare-build.sh` (**Zero GitHub Actions**).
- **Slash Command & MCP Prompt (`/remote-shop-onboarding` · `remote-shop-onboarding`):** Plain-English Remote Shop Onboarding Specialist across 5 tracks (`cnc`, `lab`, `oem`, `benchtop`, `ehs`) with 6-family Hand HAL selection and a 48-hour zero-motion `L0 OBSERVE` shadow trial.
- **Companion Surfaces:** [https://graftrobotics.ai/connect/](https://graftrobotics.ai/connect/), [https://graftrobotics.ai/compliance/](https://graftrobotics.ai/compliance/), [https://graftrobotics.ai/vault/](https://graftrobotics.ai/vault/), and [https://graftrobotics.ai/onboard/](https://graftrobotics.ai/onboard/).

## Capabilities Included (`v0.5.0`)
- **Live Wedge A-Upmarket MCP App (`ui://graft-robotics/workbench.html`):** Interactive Workbench side-pane / inline UI (`open_graft_workbench`) connecting to `http://127.0.0.1:8785` with 2-second live polling, 1-click **Download Compliance Pack ZIP** (`GET /v1/compliance-pack`), **Vault Drift Status** badge (`GET /v1/vault/status`), sandboxed iframe `postMessage` JSON-RPC bridge fallback, and explicit offline-demo indicator when the local server is stopped.
- **4 Fail-Closed MCP Form Elicitations (`ctx.elicit`):** Native operator confirmation forms before:
  - Promoting a robot on the Trust Ladder (`graft_trust_ladder(action="promote")`) — **fails closed** if the MCP client does not support elicitation
  - Resolving an `L1` Semantic Ratchet escalation on unlabeled objects (`graft_check_semantic_action`)
  - Interactive Skill Pack scaffolding (`graft_install_skill_pack(pack_id="interactive")`)
  - Interactive Remote Shop Onboarding kit generation (`graft_generate_onboarding_kit(interactive=True)`)
- **7 Operational Playbooks (MCP Prompts + Claude Code `/graft-robotics:*` commands):**
  - `ros2-compliance-audit`
  - `remote-shop-onboarding`
  - `shift-start-preflight`
  - `cnc-cell-onboarding`
  - `shadow-trial-audit`
  - `semantic-hazard-ratchet`
  - `incident-estop-recovery`
- **5 Live MCP Resources:** `ui://graft-robotics/workbench.html`, `graft://world-model/live`, `graft://trust-ladder/status`, `graft://benchmarks/latest`, `graft://safety/boundary-policy`.
- **PreToolUse Guardrail Hook (`hooks/hooks.json`):** Reinforces ISO 13850 hardware E-stop, ITAR/EAR air-gap, and signed `ROBOT.md` checks before physical-robot, ROS 2, compliance-pack, and agent-connect MCP calls across both `graft-robotics` (`.mcp.json`) and `workbench` (`mcp_config.json`) server names.
- **19 MCP Tools:** `open_graft_workbench`, `graft_world_model_status`, `graft_check_part_mechanics`, `graft_ingest_lan_lidar`, `graft_trust_ladder`, `graft_check_semantic_action`, `graft_ratchet_semantic_tag`, `graft_verify_envelope`, `graft_recommend_bundle`, `graft_list_skill_packs`, `graft_install_skill_pack`, `graft_discover_devices`, `graft_ingest_ambient_signal`, `graft_generate_onboarding_kit`, `graft_run_set_benchmark` (quarantine honesty disclosure), `graft_generate_compliance_pack`, `graft_ros2_generate_bundle`, `graft_vault_status`, and `graft_connect_agent`.
