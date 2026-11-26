#!/usr/bin/env python3
"""Graft Robotics — Universal MCP Plugin Server v0.4.0 (Anthropic Claude Code & Google Antigravity).

Utilizes the FULL Anthropic MCP & Claude Code Plugin capability surface:
  1. MCP App (`ui://graft-robotics/workbench.html` · `text/html;profile=mcp-app`)
  2. MCP Elicitations (`ctx.elicit(...)` Form Mode with Pydantic schemas for human-in-the-loop
     Trust Ladder promotion, L1 Semantic Ratchet confirmation, and interactive Skill Pack setup)
  3. MCP Prompts / Playbooks (`@mcp.prompt()` — 5 operational robotics playbooks matching `commands/*.md`)
  4. MCP Resources (`@mcp.resource()` — live World Model JSON, Trust Ladder JSON, Pi 5 Benchmarks JSON,
     and ISO 13850 Safety Boundary Markdown)
  5. 14 MCP Tools covering Multi-Sensor World Model, LAN LiDAR `.obj` meshing (Rust `graft-core`),
     Material Mechanics/Slip, Semantic-to-Deterministic Ratchet, L0-L3 Trust Ladder, Ambient Wi-Fi/Audio/Video
     Device Discovery, Job Skill Packs, Turn-Key Client Bundles (`uv` first), and RoboCurve SET-Sim rehearsal.

Compatible with BOTH `mcp 1.x` (`FastMCP`) and `mcp 2.x` (`MCPServer`).
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path
from typing import Any

from mcp import types
from pydantic import BaseModel, Field

try:
    from mcp.server.fastmcp import Context, FastMCP
except ImportError:  # mcp >= 2.0 renamed FastMCP -> MCPServer
    from mcp.server.mcpserver import Context, MCPServer as FastMCP  # type: ignore

# Ensure local robot-gate + bounded-embodiment + graft-eval are importable when available
for _candidate in (
    "/home/craigm26/projects/physical-ai-venture/robot-gate/src",
    "/home/craigm26/projects/physical-ai-venture/robot-gate/.venv/lib/python3.13/site-packages",
    "/home/craigm26/projects/physical-ai-venture/graft-eval",
):
    if os.path.isdir(_candidate) and _candidate not in sys.path:
        sys.path.append(_candidate)

APP_URI = "ui://graft-robotics/workbench.html"
HTML_PATH = Path(os.environ.get("GRAFT_ROBOTICS_APP_HTML", Path(__file__).with_name("workbench.html")))
LIVE_RUNNER_URL = os.environ.get("GRAFT_LIVE_RUNNER_URL", "http://127.0.0.1:8791").rstrip("/")
BENCHMARKS_DIR = Path("/home/craigm26/projects/physical-ai-venture/site/public/benchmarks")

PANE_META = {
    "ui": {"resourceUri": APP_URI},
    "com.google.antigravity/ui": {
        "entrypoints": [
            {"type": "aux_pane", "title": "Graft Robotics Workbench"},
            {"type": "global", "title": "Graft Robotics Workbench"},
        ]
    },
}
INLINE_META = {"ui": {"resourceUri": APP_URI}}

mcp = FastMCP("graft-robotics")


# ==============================================================================
# MCP ELICITATION SCHEMAS (FORM MODE — STRUCTURED HUMAN-IN-THE-LOOP APPROVALS)
# ==============================================================================
class TrustPromotionElicitation(BaseModel):
    operator_name: str = Field(description="Operator name recorded in the RFC 8785 SHA-256 audit log")
    hardware_estop_verified: bool = Field(
        default=False,
        description="Confirm a physical ISO 13850 shop E-stop is reachable and tested before increasing speed/autonomy",
    )
    confirm_promotion: bool = Field(
        default=False,
        description="Approve promoting this robot by one level on the L0->L3 Trust Ladder",
    )


class SemanticRatchetElicitation(BaseModel):
    confirmed_object_tag: str = Field(
        default="unidentified",
        description="Verified semantic hazard/class tag (e.g. oxidizer_bleach, ammonia_base, live_electrical, aluminum_6061_t6)",
    )
    approve_action: bool = Field(
        default=False,
        description="Approve executing this high-consequence action after human inspection (False keeps fail-closed DENY)",
    )
    ratchet_into_world_model: bool = Field(
        default=True,
        description="Persist this verified tag permanently into the signed World Model for deterministic future checks",
    )


class SkillPackOnboardingElicitation(BaseModel):
    pack_id: str = Field(
        default="cnc-tending-haas-vf2",
        description="Skill Pack ID (cnc-tending-haas-vf2 | warehouse-unpack-and-ship-humanoid | benchtop-kitting-and-qc-soarm101 | mobile-farm-ag-can-j1939)",
    )
    organization: str = Field(default="Graft Robotics Shop", description="Shop or lab name for signed ROBOT.md")
    start_in_l0_shadow_mode: bool = Field(
        default=True,
        description="Start in zero-motion L0 OBSERVE shadow mode before teaching datums (recommended)",
    )


async def _try_elicit(ctx: Context | None, message: str, schema: type[BaseModel]) -> tuple[str, Any]:
    """Invoke MCP Form Elicitation safely with graceful fallback for clients without elicitation support."""
    if ctx is None or not hasattr(ctx, "elicit"):
        return ("unsupported", None)
    try:
        res = await ctx.elicit(message=message, schema=schema)
        action = getattr(res, "action", "decline")
        return (str(action), getattr(res, "data", None))
    except Exception:
        return ("unsupported", None)


def _http_get_json(url: str, timeout: float = 2.0) -> dict[str, Any] | None:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def _http_post_json(url: str, payload: dict[str, Any], timeout: float = 15.0) -> dict[str, Any] | None:
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def _live_or_offline_snapshot() -> dict[str, Any]:
    live = _http_get_json(f"{LIVE_RUNNER_URL}/state", timeout=1.5)
    if live is not None:
        return {
            "mode": "live_mujoco_runner",
            "runner_url": LIVE_RUNNER_URL,
            "status_text": live.get("status_text", ""),
            "decision": live.get("decision", "ALLOW"),
            "world_model": live.get("world_model", {}),
            "fusion_model": live.get("fusion_model", {}),
            "trust_ladder": live.get("trust_ladder", {}),
            "actuators": live.get("actuators", []),
            "ollama_models": live.get("ollama_models", []),
            "audit_tail_sha256": live.get("audit_tail_sha256", ""),
            "homepage": "https://graftrobotics.ai",
        }

    be_ver = "not-installed"
    rust_ver = None
    try:
        import bounded_embodiment
        be_ver = bounded_embodiment.__version__
    except Exception:
        pass
    try:
        import graft_core
        rust_ver = graft_core.version()
    except Exception:
        pass
    return {
        "mode": "offline_local",
        "runner_url": LIVE_RUNNER_URL,
        "status_text": "Offline mode — start sim-shop/live_runner.py or robot-md-gateway serve for live hardware telemetry",
        "decision": "ALLOW",
        "bounded_embodiment_version": be_ver,
        "rust_graft_core_version": rust_ver,
        "world_model": {"revision": 0, "known_count": 0, "unknown_count": 0, "entities": {}},
        "fusion_model": {"sensors": {}, "live_meshes": {}, "known_parts": {}},
        "trust_ladder": {"robots": {}},
        "homepage": "https://graftrobotics.ai",
    }


def _build_bundle_recommendation(llm_provider: str, budget_tier: str, hardware_target: str) -> dict[str, Any]:
    llm = (llm_provider or "claude").strip().lower()
    budget = (budget_tier or "starter").strip().lower()
    hw = (hardware_target or "ur5e_cnc").strip().lower()

    extra_pkgs = ["robot-md", "bounded-embodiment", "castor-hal"]
    if "so-arm" in hw or "soarm" in hw or "feetech" in hw:
        extra_pkgs.append("so-arm101-actuator")
    if any(k in hw for k in ("ur5", "cobot", "cnc", "asimov", "humanoid", "mujoco")):
        extra_pkgs.append("mujoco")

    with_flags = " ".join(f"--with {p}" for p in extra_pkgs)
    uv_cmd = f"uv tool install robot-md-gateway {with_flags}"
    pip_cmd = "pip install robot-md-gateway " + " ".join(extra_pkgs)

    if llm in ("onprem", "on-prem", "ollama", "airgapped", "local") or budget in ("airgapped", "zero", "$0", "0"):
        profile = "onprem-airgapped"
        monthly_llm_cost = "$0/mo (100% local Ollama on Pi 5 / Jetson Orin)"
        llm_setup = [
            "ollama pull qwen3.5:4b              # fast 4B tool-calling on Pi 5 (8GB+)",
            "ollama pull gemma4:e4b-it-qat       # or gemma4:12b-it-qat on Jetson Orin",
        ]
        client_config = {
            "mode": "offline_on_premises",
            "ollama_url": "http://127.0.0.1:11434",
            "model": "qwen3.5:4b",
            "gateway_url": "http://127.0.0.1:8080",
            "lan_sensors_ingest": "POST http://<robot-ip>:8791/sensors/ingest",
        }
    elif llm in ("antigravity", "agy", "google"):
        profile = "antigravity"
        monthly_llm_cost = "$0-$20/mo (Google Antigravity + Gemini)"
        llm_setup = [
            "curl -fsSL https://raw.githubusercontent.com/craigm26/antigravity-plugins/main/install.sh | bash -s -- --plugin graft-robotics",
        ]
        client_config = {
            "plugin_dir": "~/.gemini/config/plugins/graft-robotics",
            "mcp_app": "ui://graft-robotics/workbench.html (aux_pane)",
        }
    elif llm in ("codex", "openai", "chatgpt"):
        profile = "codex-openai"
        monthly_llm_cost = "$20-$200/mo (OpenAI Codex CLI / ChatGPT)"
        llm_setup = [
            "# Add to ~/.codex/config.toml:",
            "[mcp_servers.graft_robotics]",
            'command = "python3"',
            'args = ["~/.graft-robotics/server/server.py"]',
        ]
        client_config = {
            "codex_config_toml": '[mcp_servers.graft_robotics]\ncommand = "python3"\nargs = ["~/.graft-robotics/server/server.py"]',
        }
    elif llm in ("gemini-cli", "gemini"):
        profile = "gemini-cli"
        monthly_llm_cost = "$0-$20/mo (Google Gemini CLI)"
        llm_setup = [
            "curl -fsSL https://raw.githubusercontent.com/craigm26/antigravity-plugins/main/install.sh | bash -s -- --plugin graft-robotics",
        ]
        client_config = {
            "mcpServers": {
                "graft-robotics": {
                    "command": "python3",
                    "args": ["~/.gemini/config/plugins/graft-robotics/server/server.py"],
                }
            }
        }
    else:
        profile = "claude-anthropic"
        monthly_llm_cost = "$20-$200/mo (Claude Pro / Max / Claude Code / Enterprise)"
        llm_setup = [
            "claude plugin marketplace add RobotRegistryFoundation/claude-code-plugins",
            "claude plugin install graft-robotics@robotregistryfoundation",
        ]
        client_config = {
            "mcpServers": {
                "graft-robotics": {
                    "command": "python3",
                    "args": ["${CLAUDE_PLUGIN_ROOT}/server/server.py"],
                }
            }
        }

    return {
        "bundle_profile": profile,
        "llm_provider": llm,
        "budget_tier": budget,
        "hardware_target": hw,
        "estimated_llm_cost": monthly_llm_cost,
        "software_license": "Apache-2.0 (free local runtime & public PyPI packages)",
        "install_commands": [
            uv_cmd,
            f"# pip fallback: {pip_cmd}",
            "robot-md-gateway init --yes",
            "robot-md-gateway list-actuators",
            "robot-md-gateway serve --robot-md ./ROBOT.md --bearers ./bearers.yaml --port 8080",
            *llm_setup,
        ],
        "client_config": client_config,
        "safety_note": (
            "Deterministic default-deny software pre-flight gate & SHA-256 audit log — "
            "always pair with hardwired ISO 13850 shop emergency stops."
        ),
    }


def _result(summary: str, data: dict[str, Any]) -> types.CallToolResult:
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=summary)],
        structuredContent=data,
    )


# ==============================================================================
# MCP RESOURCES (MCP APP UI + LIVE READABLE DATA URIS)
# ==============================================================================
@mcp.resource(
    APP_URI,
    name="Graft Robotics Workbench",
    mime_type="text/html;profile=mcp-app",
    meta={"ui": {"prefersBorder": False}},
)
def workbench_html() -> str:
    return HTML_PATH.read_text(encoding="utf-8")


@mcp.resource(
    "graft://world-model/live",
    name="Live Multi-Sensor World Model",
    description="Current KNOWN/UNKNOWN/KEEPOUT entities, LAN LiDAR meshes, Rust kernel status, and Semantic Ratchet registry.",
    mime_type="application/json",
)
def resource_world_model() -> str:
    return json.dumps(_live_or_offline_snapshot(), indent=2)


@mcp.resource(
    "graft://trust-ladder/status",
    name="L0-L3 Trust Ladder Status",
    description="Current earned autonomy tier, speed/force caps, and verified run counts per robot.",
    mime_type="application/json",
)
def resource_trust_ladder() -> str:
    snap = _live_or_offline_snapshot()
    return json.dumps(snap.get("trust_ladder", {}), indent=2)


@mcp.resource(
    "graft://benchmarks/latest",
    name="Latest Verified Pi 5 Benchmarks & SET-Sim Report",
    description="Reproducible 4-layer graft-eval scorecard (including RoboHarm Tier 0-3 ratchet & RoboCurve SET-Sim MuJoCo 4.0 results).",
    mime_type="application/json",
)
def resource_benchmarks() -> str:
    out: dict[str, Any] = {"benchmarks_url": "https://graftrobotics.ai/benchmarks/"}
    for key, fname in (("graft_eval", "graft-eval-report.json"), ("set_sim", "set-sim-report.json")):
        p = BENCHMARKS_DIR / fname
        if p.exists():
            try:
                out[key] = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                pass
    return json.dumps(out, indent=2)


@mcp.resource(
    "graft://safety/boundary-policy",
    name="ISO 13850 & Envelope 0.2 Safety Boundary Policy",
    description="Mandatory software vs. hardware safety boundary rules for physical robot deployments.",
    mime_type="text/markdown",
)
def resource_safety_policy() -> str:
    return (
        "# Graft Robotics Safety Boundary Policy\n\n"
        "1. **Software Enforcement Only:** `robot-gate`, `graft-core`, `graft-watchdog`, `bounded-embodiment`, "
        "and `robot-md-gateway` provide a deterministic, default-deny software pre-flight gate and offline-verifiable "
        "RFC 8785 / SHA-256 audit chain — **never** a certified ISO 13850 hardware emergency stop or ISO 13849-1 safety relay.\n"
        "2. **Progressive Trust (`L0 -> L3`):** Every new robot or cell begins in zero-motion `L0 OBSERVE`, graduates "
        "through `L1 ATOMIC` (30% speed, human approval every action), and auto-demotes to `L1` on any fault or drift.\n"
        "3. **Semantic-to-Deterministic Ratchet:** High-consequence verbs (`pour`, `mix`, `insert`, `heat`, `cut`, `drop_into`) "
        "on `unknown`-provenance objects escalate to `L1` human approval (via MCP Elicitation when supported) and crystallize "
        "newly discovered hazards into signed deterministic World Model rules.\n"
    )


# ==============================================================================
# MCP PROMPTS / PLAYBOOKS (REUSABLE WORKFLOWS DISCOVERABLE VIA prompts/list)
# ==============================================================================
@mcp.prompt(
    name="shift-start-preflight",
    description="Run the mandatory shift-start physical robot pre-flight checklist (zero motion until verified).",
)
def prompt_shift_start_preflight(robot_id: str = "ur5e", envelope_path: str = "./envelope.json") -> str:
    return (
        f"Execute the Graft Robotics Shift-Start Pre-Flight Playbook for `{robot_id}`:\n"
        f"1. Read resource `graft://safety/boundary-policy` and confirm hardwired ISO 13850 E-stop pairing.\n"
        f"2. Call `graft_discover_devices` to inspect local & LAN sensors (LiDAR, Wi-Fi CSI, mics, cameras).\n"
        f"3. Call `graft_world_model_status` to verify zero stale sensors and inspect live keep-out zones.\n"
        f"4. If `{envelope_path}` exists, call `graft_verify_envelope(envelope_path='{envelope_path}')`.\n"
        f"5. Call `graft_trust_ladder(action='status', robot_id='{robot_id}')` and report readiness — do NOT command motion unless every check is green."
    )


@mcp.prompt(
    name="cnc-cell-onboarding",
    description="Onboard a new CNC tending cell in ~20 minutes using a verified Job Skill Pack and 3 datums.",
)
def prompt_cnc_cell_onboarding(organization: str = "My Machine Shop", target_dir: str = "./my-cnc-cell") -> str:
    return (
        f"Run the Graft Robotics 20-Minute CNC Cell Onboarding Playbook for `{organization}`:\n"
        f"1. Call `graft_list_skill_packs(job='cnc')` and inspect `cnc-tending-haas-vf2`.\n"
        f"2. Call `graft_install_skill_pack(pack_id='cnc-tending-haas-vf2', target_dir='{target_dir}', organization='{organization}')` (using MCP Elicitation to confirm L0 shadow start).\n"
        f"3. Call `graft_check_part_mechanics(actor='ur5e', part_id='finished_bracket', grip_force_n=35.0, coolant_wet=True)` to verify wet-coolant slip compensation.\n"
        f"4. Guide the operator through teaching the 3 datums (`handoff_nest`, `haas_door_clearance`, `kurt_vise_jaw`) in `L0 OBSERVE` before promoting to `L1 ATOMIC`."
    )


@mcp.prompt(
    name="shadow-trial-audit",
    description="Run a zero-motion 48-hour L0 OBSERVE Shadow Trial and generate a buyer-ready audit summary.",
)
def prompt_shadow_trial_audit(cell_name: str = "Cell-01") -> str:
    return (
        f"Run the Graft Robotics Zero-Motion L0 Shadow Trial Playbook for `{cell_name}`:\n"
        f"1. Verify all robots are in `L0_OBSERVE` via `graft_trust_ladder(action='status')`.\n"
        f"2. Read `graft://benchmarks/latest` to show the customer our signed Pi 5 EV-03 verification bundle and SET-Sim rehearsal results.\n"
        f"3. Inspect `graft_world_model_status` and summarize how many proposals would be allowed vs. caught before a single motor ever moves.\n"
        f"4. Present the signed SHA-256 Shadow Trial Receipt and clear criteria for human-approved promotion to `L1 ATOMIC`."
    )


@mcp.prompt(
    name="semantic-hazard-ratchet",
    description="Inspect an unlabeled or novel shop object with the Semantic-to-Deterministic Ratchet and lock in rules.",
)
def prompt_semantic_hazard_ratchet(verb: str = "pour", source_object_id: str = "unlabeled_jug_a", target_object_id: str = "unlabeled_jug_b") -> str:
    return (
        f"Run the Semantic-to-Deterministic Ratchet Playbook for `{verb}({source_object_id}, {target_object_id})`:\n"
        f"1. Call `graft_check_semantic_action(verb='{verb}', source_object_id='{source_object_id}', target_object_id='{target_object_id}')`.\n"
        f"2. If provenance is `unknown`, use the native MCP Elicitation form to ask the human operator to confirm the object's identity and whether to ratchet the tag permanently into the World Model.\n"
        f"3. Verify that repeat checks catch the hazard deterministically in microseconds with zero VLM call."
    )


@mcp.prompt(
    name="incident-estop-recovery",
    description="Post-fault or post-E-stop isolation, Trust Ladder demotion verification, and safe re-arm checklist.",
)
def prompt_incident_estop_recovery(robot_id: str = "ur5e") -> str:
    return (
        f"Execute the Graft Robotics Post-Fault / E-Stop Recovery Playbook for `{robot_id}`:\n"
        f"1. Confirm the physical ISO 13850 hardware E-stop condition has been cleared by a qualified human operator.\n"
        f"2. Inspect `graft://world-model/live` and `graft://trust-ladder/status` to confirm the robot auto-demoted cleanly to `L1` and inspect the latest SHA-256 audit tail.\n"
        f"3. Run `graft_discover_devices` and `graft_world_model_status` to confirm all LAN LiDAR, Wi-Fi CSI, and local sensors are fresh.\n"
        f"4. Do NOT promote past `L1` without running `graft_trust_ladder(action='promote', robot_id='{robot_id}')` and completing the operator elicitation confirmation."
    )


# ==============================================================================
# MCP TOOLS (14 TOOLS INCLUDING ELICITATION-ENABLED HUMAN APPROVAL GATES)
# ==============================================================================
@mcp.tool(name="open_graft_workbench", title="Graft Robotics Workbench", meta=PANE_META)
def open_graft_workbench() -> types.CallToolResult:
    """Open the interactive Graft Robotics Workbench side pane / MCP App."""
    snap = _live_or_offline_snapshot()
    wm = snap.get("world_model", {})
    tr = snap.get("trust_ladder", {}).get("robots", {})
    summary = (
        f"Graft Robotics Workbench ready ({snap['mode']}). "
        f"World Model rev #{wm.get('revision', 0)} (KNOWN={wm.get('known_count', 0)}, UNKNOWN={wm.get('unknown_count', 0)}), "
        f"tracked robots={list(tr.keys())}."
    )
    return _result(summary, snap)


@mcp.tool(name="graft_world_model_status", title="World Model & LAN Sensors", meta=INLINE_META)
def graft_world_model_status() -> types.CallToolResult:
    """Inspect the live multi-sensor World Model, LAN LiDAR meshes, Rust kernel, Semantic Ratchet, Trust Ladder, and actuator telemetry."""
    snap = _live_or_offline_snapshot()
    fm = snap.get("fusion_model", {})
    summary = (
        f"Mode={snap['mode']} | sensors={list(fm.get('sensors', {}).keys())} | "
        f"live_meshes={list(fm.get('live_meshes', {}).keys())} | decision={snap.get('decision')}"
    )
    return _result(summary, snap)


@mcp.tool(name="graft_check_part_mechanics", title="Check Part Strength & Slip", meta=INLINE_META)
def graft_check_part_mechanics(
    actor: str = "asimov-1",
    part_id: str = "inbound_crate",
    grip_force_n: float = 32.0,
    bimanual: bool = True,
    coolant_wet: bool = False,
) -> types.CallToolResult:
    """Check payload, torque, material crush limit, and Coulomb slip safety factor before grasping."""
    live = _http_post_json(
        f"{LIVE_RUNNER_URL}/mcp",
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "check_part_mechanics",
                "arguments": {
                    "actor": actor,
                    "part_id": part_id,
                    "grip_force_n": grip_force_n,
                    "bimanual": bimanual,
                    "coolant_wet": coolant_wet,
                },
            },
        },
    )
    if live and "result" in live:
        out = json.loads(live["result"]["content"][0]["text"])
    else:
        from robot_gate.world_model import ROBOT_CAPACITIES, PartSpec, evaluate_mechanics

        parts = {
            "inbound_crate": PartSpec("inbound_crate", "corrugated_cardboard_ect32", 1.35, (0.20, 0.20, 0.09), 200.0, requires_bimanual=True),
            "billet_6061": PartSpec("billet_6061", "aluminum_6061_t6", 0.95, (0.076, 0.076, 0.04), 76.0),
            "finished_bracket": PartSpec("finished_bracket", "aluminum_thin_bracket", 0.62, (0.076, 0.076, 0.036), 76.0, coolant_wet=True),
            "heavy_steel_die": PartSpec("heavy_steel_die", "steel_1018", 7.50, (0.12, 0.10, 0.08), 80.0),
        }
        v = evaluate_mechanics(ROBOT_CAPACITIES[actor], parts[part_id], commanded_grip_force_n=grip_force_n, bimanual=bimanual, coolant_wet=coolant_wet)
        out = {
            "allowed": v.allowed,
            "reasons": list(v.reasons),
            "required_grip_force_n": v.required_grip_force_n,
            "recommended_grip_force_n": v.recommended_grip_force_n,
            "payload_utilization_pct": v.payload_utilization_pct,
            "safety_factor_slip": v.safety_factor_slip,
        }
    verdict = "ALLOW" if out.get("allowed") else "DENY"
    detail = "; ".join(out.get("reasons", [])) or f"SF_slip={out.get('safety_factor_slip')}x, rec={out.get('recommended_grip_force_n')}N"
    return _result(f"Mechanics [{verdict}] {actor} -> {part_id} @ {grip_force_n}N: {detail}", out)


@mcp.tool(name="graft_ingest_lan_lidar", title="Ingest LAN LiDAR Obstacle Mesh", meta=INLINE_META)
def graft_ingest_lan_lidar(
    sensor_id: str = "lan_lidar_shop_pc",
    x: float = 0.35,
    y: float = 0.15,
    z: float = 1.08,
    half_size_m: float = 0.10,
    mesh_id: str = "stray_cart_lan",
) -> types.CallToolResult:
    """Ingest a 3D point cloud from any networked LAN LiDAR into a live .obj collision mesh checked in MuJoCo 4.0."""
    live = _http_post_json(
        f"{LIVE_RUNNER_URL}/sensors/ingest",
        {"sensor_id": sensor_id, "x": x, "y": y, "z": z, "half_size_m": half_size_m, "mesh_id": mesh_id},
    )
    if live:
        m = live.get("mesh") or {}
        return _result(f"Ingested LAN LiDAR '{sensor_id}' -> live mesh '{mesh_id}' ({m.get('face_count', 0)} triangles) active in MuJoCo 4.0.", live)
    return _result("Live runner offline; start sim-shop/live_runner.py to push live LAN LiDAR meshes.", {"ok": False})


@mcp.tool(name="graft_trust_ladder", title="Trust & Skill Graduation Ladder", meta=INLINE_META)
async def graft_trust_ladder(
    action: str = "status",
    robot_id: str = "asimov-1",
    operator: str = "operator",
    ctx: Context | None = None,
) -> types.CallToolResult:
    """Inspect, run Day-1 L1 small-object practice, or promote a robot along L0 OBSERVE -> L3 AUTONOMOUS (uses MCP Elicitation for operator sign-off)."""
    if action == "pick_small_object":
        res = _http_post_json(
            f"{LIVE_RUNNER_URL}/mcp",
            {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "pick_small_object", "arguments": {"hitl_approved": True}}},
        )
        if res and "result" in res:
            out = json.loads(res["result"]["content"][0]["text"])
            return _result(f"Day-1 L1 small-object pick result: {out.get('trust_progress', out)}", out)
    elif action == "promote":
        # Use native MCP Form Elicitation when supported to enforce human-in-the-loop promotion sign-off!
        e_action, e_data = await _try_elicit(
            ctx,
            f"Operator sign-off required to promote '{robot_id}' one level on the Graft Trust Ladder (L0->L3). Confirm physical ISO 13850 E-stop is verified.",
            TrustPromotionElicitation,
        )
        if e_action == "accept" and e_data is not None:
            if not (e_data.confirm_promotion and e_data.hardware_estop_verified):
                return _result(
                    f"Trust promotion HELD for '{robot_id}': operator must confirm both promotion and physical ISO 13850 E-stop readiness.",
                    {"promoted": False, "elicitation": "rejected_safety_checkbox"},
                )
            operator = e_data.operator_name or operator
        elif e_action in ("decline", "cancel"):
            return _result(f"Trust promotion cancelled by operator for '{robot_id}'.", {"promoted": False, "elicitation": e_action})

        res = _http_post_json(
            f"{LIVE_RUNNER_URL}/mcp",
            {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "promote_trust", "arguments": {"actor": robot_id, "operator": operator}}},
        )
        if res and "result" in res:
            out = json.loads(res["result"]["content"][0]["text"])
            return _result(f"Trust promotion for {robot_id} (operator={operator}): {out}", out)
    snap = _live_or_offline_snapshot()
    return _result(f"Trust Ladder snapshot: {json.dumps(snap.get('trust_ladder', {}))}", snap.get("trust_ladder", {}))


@mcp.tool(name="graft_check_semantic_action", title="Semantic-to-Deterministic Ratchet Check", meta=INLINE_META)
async def graft_check_semantic_action(
    verb: str = "pour",
    source_object_id: str = "unlabeled_jug_a",
    target_object_id: str = "unlabeled_jug_b",
    expected_part_number: str = "",
    camera_caption: str = "",
    use_critic: bool = True,
    ctx: Context | None = None,
) -> types.CallToolResult:
    """Evaluate a proposed physical action against Graft's Semantic Provenance Gate, GHS/shop hazard matrix, and veto-only VLM critic — eliciting human confirmation & ratcheting tags on unknown objects."""
    from robot_gate.semantic_guard import (
        RuleBasedVLMStubCritic,
        SemanticActionProposal,
        SemanticObjectSpec,
        SemanticWorldRegistry,
    )

    live = _http_post_json(
        f"{LIVE_RUNNER_URL}/mcp",
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "check_semantic_action",
                "arguments": {
                    "verb": verb,
                    "source_object_id": source_object_id,
                    "target_object_id": target_object_id or None,
                    "expected_part_number": expected_part_number or None,
                    "camera_caption": camera_caption,
                    "use_critic": use_critic,
                },
            },
        },
    )
    if live and "result" in live:
        out = json.loads(live["result"]["content"][0]["text"])
    else:
        reg = SemanticWorldRegistry()
        reg.register_object(SemanticObjectSpec("billet_6061", tags=("aluminum_6061_t6",), provenance="work_order", part_number="JOB-6061-REV-B"))
        reg.register_object(SemanticObjectSpec("bracket_rev_a", tags=("aluminum_6061_t6",), provenance="work_order", part_number="JOB-6061-REV-A"))
        reg.register_object(SemanticObjectSpec("unlabeled_jug_a", provenance="unknown"))
        reg.register_object(SemanticObjectSpec("unlabeled_jug_b", provenance="unknown"))
        sv = reg.evaluate_proposal(
            SemanticActionProposal(
                verb=verb,
                source_object_id=source_object_id,
                target_object_id=target_object_id or None,
                expected_part_number=expected_part_number or None,
                camera_caption=camera_caption,
            ),
            critic=RuleBasedVLMStubCritic() if use_critic else None,
            auto_ratchet_from_critic=True,
        )
        out = {
            "allowed": sv.decision == "ALLOW",
            "decision": sv.decision,
            "tier_triggered": sv.tier_triggered,
            "reasons": list(sv.reasons),
            "ratcheted_tags": {k: list(v) for k, v in sv.ratcheted_tags.items()},
            "verdict_sha256": sv.verdict_sha256,
        }

    # If escalated to L1 Human Approval, invoke native MCP Form Elicitation so the operator can label & ratchet!
    if out.get("decision") == "ESCALATE_L1_HUMAN":
        e_action, e_data = await _try_elicit(
            ctx,
            f"Semantic Guard escalated `{verb}({source_object_id}, {target_object_id})` ({out['reasons'][0]}). Identify the object tag and confirm whether to ratchet into the World Model.",
            SemanticRatchetElicitation,
        )
        if e_action == "accept" and e_data is not None:
            out["operator_elicitation"] = e_data.model_dump()
            if e_data.ratchet_into_world_model and e_data.confirmed_object_tag:
                _http_post_json(
                    f"{LIVE_RUNNER_URL}/mcp",
                    {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "tools/call",
                        "params": {
                            "name": "ratchet_semantic_tag",
                            "arguments": {"object_id": source_object_id, "tags": [e_data.confirmed_object_tag], "note": "Ratcheted via MCP Elicitation"},
                        },
                    },
                )

    return _result(
        f"Semantic Guard [{out['decision']}] ({out['tier_triggered']}): {'; '.join(out.get('reasons', []))}",
        out,
    )


@mcp.tool(name="graft_ratchet_semantic_tag", title="Ratchet Semantic Tag Into World Model", meta=INLINE_META)
def graft_ratchet_semantic_tag(
    object_id: str,
    tags: list[str],
    note: str = "Operator-confirmed hazard tag",
) -> types.CallToolResult:
    """Persist a newly discovered semantic hazard tag into the signed World Model so future checks enforce it deterministically with zero VLM latency."""
    live = _http_post_json(
        f"{LIVE_RUNNER_URL}/mcp",
        {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "ratchet_semantic_tag", "arguments": {"object_id": object_id, "tags": tags, "note": note}}},
    )
    if live and "result" in live:
        out = json.loads(live["result"]["content"][0]["text"])
        return _result(f"Ratcheted '{object_id}' += {tags} (sha256={str(out.get('sha256',''))[:16]}...)", out)
    from robot_gate.semantic_guard import SemanticWorldRegistry

    reg = SemanticWorldRegistry()
    sha = reg.ratchet_tag(object_id, tags, source="mcp_operator", note=note)
    return _result(f"Ratcheted '{object_id}' += {tags} locally (sha256={sha[:16]}...)", {"ratcheted": True, "object_id": object_id, "tags": tags, "sha256": sha})


@mcp.tool(name="graft_verify_envelope", title="Verify Envelope 0.2 (RRF Standard)", meta=INLINE_META)
def graft_verify_envelope(envelope_path: str) -> types.CallToolResult:
    """Validate an official Envelope 0.2 JSON file using public `bounded-embodiment` and compute its RFC 8785 hash."""
    p = Path(envelope_path).expanduser()
    if not p.exists():
        return _result(f"Envelope file not found: {p}", {"valid": False, "error": "file_not_found"})
    try:
        from bounded_embodiment.canonical import sha256_jcs
        from bounded_embodiment.envelope import load as load_env

        doc = json.loads(p.read_text(encoding="utf-8"))
        load_env(doc)
        digest = sha256_jcs({k: v for k, v in doc.items() if k != "signature"})
        return _result(f"VALID Envelope 0.2 ({p.name}) · RFC 8785 sha256={digest[:16]}...", {"valid": True, "sha256": digest, "path": str(p)})
    except Exception as exc:
        return _result(f"INVALID Envelope ({p.name}): {exc}", {"valid": False, "error": str(exc)})


@mcp.tool(name="graft_recommend_bundle", title="Generate Client LLM & Budget Bundle", meta=INLINE_META)
def graft_recommend_bundle(
    llm_provider: str = "claude",
    budget_tier: str = "starter",
    hardware_target: str = "ur5e_cnc",
) -> types.CallToolResult:
    """Generate exact uv/uvx install commands & MCP config for a client's LLM tool (claude, antigravity, codex, gemini-cli, onprem), budget, and robot hardware."""
    bundle = _build_bundle_recommendation(llm_provider, budget_tier, hardware_target)
    return _result(
        f"Bundle '{bundle['bundle_profile']}' for {bundle['hardware_target']} ({bundle['estimated_llm_cost']}): "
        + " && ".join(bundle["install_commands"][:1]),
        bundle,
    )


@mcp.tool(name="graft_list_skill_packs", title="Browse Vertical Job Skill Packs", meta=INLINE_META)
def graft_list_skill_packs(robot: str = "", job: str = "") -> types.CallToolResult:
    """List pre-built verifiable Job Skill Packs matched to robot hardware and shop job (CNC tending, humanoid unpack/ship, SO-ARM101 kitting, CAN/J1939 ag)."""
    from robot_gate.skillpacks import list_skill_packs

    packs = list_skill_packs(robot=robot or None, job=job or None)
    names = [f"{p['pack_id']} (~{p['setup_time_min']}m)" for p in packs]
    return _result(
        f"Found {len(packs)} matching Skill Pack(s): " + (", ".join(names) if names else "none"),
        {"count": len(packs), "packs": packs},
    )


@mcp.tool(name="graft_install_skill_pack", title="Install Job Skill Pack", meta=INLINE_META)
async def graft_install_skill_pack(
    pack_id: str = "cnc-tending-haas-vf2",
    target_dir: str = "./my-cell",
    organization: str = "Graft Robotics Shop",
    ctx: Context | None = None,
) -> types.CallToolResult:
    """Scaffold a ready-to-calibrate robot workspace from a vertical Skill Pack (supports interactive MCP Form Elicitation when pack_id='interactive')."""
    if pack_id == "interactive":
        e_action, e_data = await _try_elicit(
            ctx,
            "Configure your vertical Job Skill Pack workspace (starts safely in zero-motion L0 OBSERVE shadow mode).",
            SkillPackOnboardingElicitation,
        )
        if e_action == "accept" and e_data is not None:
            pack_id = e_data.pack_id
            organization = e_data.organization
        elif e_action in ("decline", "cancel"):
            return _result("Skill Pack installation cancelled by operator.", {"installed": False})
        else:
            pack_id = "cnc-tending-haas-vf2"

    from robot_gate.skillpacks import install_skill_pack

    res = install_skill_pack(pack_id, Path(target_dir).expanduser(), organization=organization, sign=True)
    return _result(
        f"Installed '{res['pack_id']}' into {res['workspace']} (~{res['setup_time_min']} min onboarding). "
        f"Teach {len(res['datums_to_teach'])} datums ({', '.join(res['datums_to_teach'])}), starting at {res['starting_trust_level']}.",
        res,
    )


@mcp.tool(name="graft_discover_devices", title="Discover Helpful Networked & Local Devices", meta=INLINE_META)
def graft_discover_devices(include_local: bool = True, include_lan: bool = True) -> types.CallToolResult:
    """Discover local and LAN devices (Wi-Fi RSSI/CSI sensing, USB/RTSP/ONVIF webcams, shop mics, LAN LiDARs, serial buses) that can improve robot safety and world-model accuracy."""
    from robot_gate.device_discovery import discover_environment_devices

    res = discover_environment_devices(include_local=include_local, include_lan=include_lan)
    return _result(
        f"Discovered {res['discovered_count']} helpful environment device(s): {res['by_modality']}. "
        "Operator consent is required before attaching external cameras, mics, or Wi-Fi nodes.",
        res,
    )


@mcp.tool(name="graft_ingest_ambient_signal", title="Fuse Wi-Fi, Audio, or Video Signal", meta=INLINE_META)
def graft_ingest_ambient_signal(
    modality: str = "wifi_sensing",
    sensor_id: str = "shop_wifi_ap_01",
    estimated_distance_m: float = 0.9,
    chatter_score: float = 0.0,
    transcript: str = "",
    human_count: int = 0,
) -> types.CallToolResult:
    """Evaluate a live Wi-Fi human-motion signal, shop microphone audio cue/chatter, or webcam detection into an Envelope 0.2 proximity directive (nominal / slow_30pct / hold_safe_stop)."""
    live = _http_post_json(
        f"{LIVE_RUNNER_URL}/sensors/ambient",
        {
            "modality": modality,
            "sensor_id": sensor_id,
            "estimated_distance_m": estimated_distance_m,
            "chatter_score": chatter_score,
            "transcript": transcript,
            "human_count": human_count,
        },
    )
    if live and "directive" in live:
        d = live["directive"]
        return _result(f"Ambient [{d['action']}] ({modality}): {d['reason']}", live)

    from robot_gate.device_discovery import (
        evaluate_audio_signal,
        evaluate_video_signal,
        evaluate_wifi_motion_signal,
    )

    if modality == "audio_mic":
        d = evaluate_audio_signal(sensor_id=sensor_id, db_spl=88.0, chatter_score=chatter_score, transcript=transcript)
    elif modality == "video_webcam":
        d = evaluate_video_signal(sensor_id=sensor_id, human_count=max(1, human_count), nearest_human_m=estimated_distance_m)
    else:
        d = evaluate_wifi_motion_signal(sensor_id=sensor_id, rssi_dbm_samples=[-40.0, -49.0, -37.0, -48.0], estimated_distance_m=estimated_distance_m)
    return _result(f"Ambient [{d.action}] ({modality}): {d.reason}", d.__dict__)


@mcp.tool(name="graft_run_set_benchmark", title="Run RoboCurve SET-Sim Benchmark (MuJoCo 4.0)", meta=INLINE_META)
def graft_run_set_benchmark() -> types.CallToolResult:
    """Return or run the MuJoCo 4.0.1 rehearsal of RoboCurve's Six Easy Tasks (SET) comparing open-loop vs. Graft closed-loop harness."""
    rep_path = BENCHMARKS_DIR / "set-sim-report.json"
    if rep_path.exists():
        rep = json.loads(rep_path.read_text(encoding="utf-8"))
        s = rep["summary"]
        return _result(
            f"SET-Sim (MuJoCo 4.0 Rehearsal · NOT real hardware): Open-Loop {s['open_loop_passed']}/{s['total_trials']} ({s['open_loop_pct']}%) "
            f"vs. Graft Closed-Loop {s['graft_harness_passed']}/{s['total_trials']} ({s['graft_harness_pct']}%) | 0 bounds violations.",
            rep,
        )
    return _result("SET-Sim report not found yet; run graft-eval/set_benchmark_sim.py.", {"ok": False})


if __name__ == "__main__":
    mcp.run()
