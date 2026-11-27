#!/usr/bin/env python3
"""Graft Robotics — Universal MCP Plugin Server v0.5.0 (Claude Code, Antigravity, Codex CLI & Gemini CLI).

Utilizes the FULL Anthropic MCP & Multi-Client Plugin capability surface:
  1. MCP App (`ui://graft-robotics/workbench.html` · `text/html;profile=mcp-app`) — live Wedge A-Upmarket
     Workbench with 2s polling, 1-click Compliance Pack ZIP download, Vault Drift Status badge, and
     sandboxed iframe `postMessage` JSON-RPC fallback
  2. MCP Elicitations (`ctx.elicit(...)` Form Mode with Pydantic schemas for fail-closed human-in-the-loop
     Trust Ladder promotion, L1 Semantic Ratchet confirmation, Skill Pack setup, and Remote Shop Onboarding)
  3. MCP Prompts / Playbooks (`@mcp.prompt()` — 7 operational robotics playbooks matching `commands/*.md`,
     including `/ros2-compliance-audit`)
  4. MCP Resources (`@mcp.resource()` — 5 live resources: Workbench HTML, World Model JSON, Trust Ladder JSON,
     Pi 5 Benchmarks JSON, and ISO 13850 Safety Boundary Markdown)
  5. 19 MCP Tools covering ROS 2 Pre-Flight Launch Bundle generation (`graft_ros2_generate_bundle`),
     opt-in Cloudflare D1 Hosted Fleet Vault status (`graft_vault_status`, zero phone-home when unset),
     universal 6-client Agent Connect (`graft_connect_agent`), 1-Click ISO 10218:2025 & EU 2023/1230
     Compliance Dossier export & offline verification, Remote Shop Onboarding Kit generation, Multi-Sensor
     World Model, LAN LiDAR `.obj` meshing (Rust `graft-core`), Material Mechanics/Slip, Semantic-to-Deterministic
     Ratchet, fail-closed L0-L3 Trust Ladder, Ambient Wi-Fi/Audio/Video Device Discovery, Job Skill Packs,
     Turn-Key Client Bundles (`uv` first), and quarantined SET-Sim honesty disclosure / hardware redirect.

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

PLUGIN_VERSION = "0.5.0"


def _resolve_workspace_dir() -> Path | None:
    """Resolve the Graft Robotics workspace portably via env var, relative parents, or ~/projects."""
    env_ws = os.environ.get("GRAFT_WORKSPACE_DIR")
    if env_ws:
        p = Path(env_ws).expanduser()
        if p.is_dir():
            return p
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "robot-gate" / "src").is_dir():
            return parent
    home_ws = Path.home() / "projects" / "physical-ai-venture"
    if (home_ws / "robot-gate" / "src").is_dir():
        return home_ws
    return None


_WORKSPACE_DIR = _resolve_workspace_dir()
if _WORKSPACE_DIR is not None:
    _path_candidates: list[Path] = [
        _WORKSPACE_DIR / "robot-gate" / "src",
        _WORKSPACE_DIR / "graft-eval",
    ]
    _venv_lib = _WORKSPACE_DIR / "robot-gate" / ".venv" / "lib"
    if _venv_lib.is_dir():
        _path_candidates.extend(sorted(_venv_lib.glob("python*/site-packages")))
    for _candidate in _path_candidates:
        _cstr = str(_candidate)
        if _candidate.is_dir() and _cstr not in sys.path:
            sys.path.append(_cstr)

APP_URI = "ui://graft-robotics/workbench.html"
HTML_PATH = Path(os.environ.get("GRAFT_ROBOTICS_APP_HTML", Path(__file__).with_name("workbench.html")))
CELL_CONSOLE_URL = (
    os.environ.get("GRAFT_CELL_URL")
    or os.environ.get("GRAFT_API_URL")
    or "http://127.0.0.1:8785"
).rstrip("/")
LIVE_RUNNER_URL = (
    os.environ.get("GRAFT_LIVE_RUNNER_URL")
    or os.environ.get("GRAFT_API_URL")
    or CELL_CONSOLE_URL
).rstrip("/")
BENCHMARKS_DIR = Path(
    os.environ.get(
        "GRAFT_BENCHMARKS_DIR",
        str((_WORKSPACE_DIR / "site" / "public" / "benchmarks") if _WORKSPACE_DIR else Path(__file__).resolve().parent / "benchmarks"),
    )
)

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


class RemoteOnboardingElicitation(BaseModel):
    user_type: str = Field(
        default="cnc",
        description="User track: cnc | lab | oem | benchtop | ehs",
    )
    setup_depth: str = Field(
        default="quick",
        description="Setup depth: quick (5-10 min safe defaults) | advanced (custom envelope, keep-outs & fleet signing)",
    )
    hand_family: str = Field(
        default="parallel_2f",
        description="Hand HAL family: parallel_2f | concentric_3f | dexterous_5f | vacuum_suction | magnetic_atc | bimanual_coordinated",
    )
    ai_tier: str = Field(
        default="claude",
        description="AI coach & runtime tier: claude | antigravity | codex | apple_mlx | google_gemma4 | ollama",
    )
    hardwired_estop_confirmed: bool = Field(
        default=False,
        description="Confirm a physical hardwired ISO 13850 red E-stop (and ISO 13849-1 door interlocks where applicable) is installed and tested. Graft software NEVER replaces hardware E-stops.",
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

    if llm in ("apple_mlx", "mlx", "apple", "mac", "mac_mini", "apple-mlx"):
        profile = "apple-mlx-shop-server"
        monthly_llm_cost = "$0/mo recurring (~$599 Mac mini M4/M5 Apple Silicon LAN server)"
        mlx_model = (
            "mlx-community/gemma-4-26b-a4b-it-4bit"
            if budget in ("production", "airgapped")
            else "mlx-community/gemma-4-e4b-it-4bit"
        )
        llm_setup = [
            "# On Mac mini M4/M5 (Apple Silicon Unified Memory, 100% air-gapped LAN server):",
            "uv tool install mlx-lm",
            f"mlx_lm.server --model {mlx_model} --host 0.0.0.0 --port 11434",
            "# Optional Xcode / macOS agent bridge: xcrun mcpbridge",
        ]
        client_config = {
            "mode": "offline_apple_mlx_lan",
            "openai_compatible_url": "http://<mac-mini-lan-ip>:11434/v1",
            "model": mlx_model,
            "vlm_semantic_critic": "local_apple_mlx_veto_only",
            "gateway_url": "http://<robot-pi5-ip>:8785",
            "lan_sensors_ingest": "POST http://<robot-pi5-ip>:8785/sensors/ingest",
        }
    elif llm in ("google_gemma4", "gemma4", "gemma", "litert", "litert-lm", "google-local"):
        profile = "google-gemma4-edge"
        monthly_llm_cost = "$0/mo recurring (100% local Google Gemma 4 via Ollama / LiteRT-LM)"
        gemma_model = "gemma4:26b-a4b-it-q4_K_M" if budget == "production" else "gemma4:e4b-it-qat"
        llm_setup = [
            f"ollama pull {gemma_model}   # native multimodal vision + tool-calling + VLM semantic critic",
            "# Optional Google LiteRT-LM NPU/GPU edge acceleration: uv pip install ai-edge-litert",
        ]
        client_config = {
            "mode": "offline_google_gemma4",
            "ollama_url": "http://127.0.0.1:11434",
            "model": gemma_model,
            "vlm_semantic_critic": "local_gemma4_multimodal_veto_only",
            "gateway_url": "http://127.0.0.1:8785",
            "lan_sensors_ingest": "POST http://<robot-ip>:8785/sensors/ingest",
        }
    elif llm in ("onprem", "on-prem", "ollama", "airgapped", "local") or budget in ("airgapped", "zero", "$0", "0"):
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
            "gateway_url": "http://127.0.0.1:8785",
            "lan_sensors_ingest": "POST http://<robot-ip>:8785/sensors/ingest",
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
            "robot-md-gateway serve --robot-md ./ROBOT.md --bearers ./bearers.yaml --port 8785",
            *llm_setup,
        ],
        "client_config": client_config,
        "safety_note": (
            "Deterministic default-deny software pre-flight gate & SHA-256 audit log — "
            "always pair with hardwired ISO 13850 shop emergency stops."
        ),
    }


_ONBOARD_PERSONAS: dict[str, dict[str, Any]] = {
    "cnc": {
        "label": "CNC / Machine Shop Owner",
        "default_robot": "cnc-cobot-01",
        "hardware_target": "ur5e_cnc",
        "budget_tier": "starter",
        "hal_driver": "castor_hal.drivers.ur_rtde",
        "dof": 6,
        "workspace_box_m": {"x": [-0.75, 0.75], "y": [0.05, 0.85], "z": [0.02, 0.90]},
        "exclusions": [
            {"name": "cnc_door_and_spindle_sweep", "min": [0.42, 0.45, 0.10], "max": [0.80, 0.90, 0.95]},
            {"name": "operator_pendant_walkway", "min": [-0.80, -0.35, 0.00], "max": [0.80, 0.04, 1.80]},
        ],
        "max_tcp_velocity_mps": 0.25,
        "max_contact_force_n": 45.0,
        "coolant_wet_default": True,
        "datums": ["handoff_nest", "cnc_door_clearance", "vise_jaw_datum"],
        "plain_english_focus": "Plain-English Haas/Fanuc/Mazak tending with wet-coolant slip guard and automatic spindle/door keep-outs — zero robotics jargon.",
    },
    "lab": {
        "label": "Robotics Research Lab / Eval Team",
        "default_robot": "lab-eval-arm-01",
        "hardware_target": "ur5e_mujoco",
        "budget_tier": "starter",
        "hal_driver": "castor_hal.drivers.mujoco_sim",
        "dof": 6,
        "workspace_box_m": {"x": [-0.65, 0.65], "y": [-0.55, 0.65], "z": [0.02, 0.85]},
        "exclusions": [
            {"name": "bench_operator_edge", "min": [-0.70, -0.65, 0.00], "max": [0.70, -0.45, 1.40]},
            {"name": "camera_rig_overhead", "min": [-0.40, -0.20, 0.78], "max": [0.40, 0.40, 1.20]},
        ],
        "max_tcp_velocity_mps": 0.30,
        "max_contact_force_n": 35.0,
        "coolant_wet_default": False,
        "datums": ["bench_origin", "eval_tray_datum", "drop_zone_datum"],
        "plain_english_focus": "Reproducible uvx + EV-03 verification workflow, portable 3-datum L0 OBSERVE hardware onboarding, Semantic-to-Deterministic Ratchet, and Python SDK integration.",
    },
    "oem": {
        "label": "Integrator / OEM / ITAR Cell",
        "default_robot": "oem-cell-01",
        "hardware_target": "ur5e_cnc",
        "budget_tier": "airgapped",
        "hal_driver": "castor_hal.drivers.industrial_cell",
        "dof": 6,
        "workspace_box_m": {"x": [-0.85, 0.85], "y": [0.00, 0.95], "z": [0.02, 1.05]},
        "exclusions": [
            {"name": "plc_safety_curtain_plane", "min": [-0.90, -0.30, 0.00], "max": [0.90, 0.02, 2.00]},
            {"name": "control_cabinet_keepout", "min": [-0.90, 0.45, 0.00], "max": [-0.55, 0.98, 1.40]},
        ],
        "max_tcp_velocity_mps": 0.25,
        "max_contact_force_n": 50.0,
        "coolant_wet_default": True,
        "datums": ["fixture_zero", "interlock_clearance", "outbound_pallet"],
        "plain_english_focus": "Air-gapped LAN inference (Apple MLX or local Gemma 4), Ed25519 key custody, fleet-reusable ROBOT.md v1.1 templates, and RFC 8785 audit chains.",
    },
    "benchtop": {
        "label": "Maker / Benchtop / SO-ARM101 Builder",
        "default_robot": "bob-soarm101",
        "hardware_target": "so-arm101",
        "budget_tier": "airgapped",
        "hal_driver": "castor_hal.drivers.feetech_sts3215",
        "dof": 6,
        "workspace_box_m": {"x": [-0.28, 0.28], "y": [0.04, 0.34], "z": [0.01, 0.36]},
        "exclusions": [
            {"name": "laptop_and_keyboard_zone", "min": [-0.35, -0.35, 0.00], "max": [0.35, 0.03, 0.50]},
            {"name": "table_surface_guard", "min": [-0.35, -0.35, -0.10], "max": [0.35, 0.40, 0.008]},
        ],
        "max_tcp_velocity_mps": 0.15,
        "max_contact_force_n": 15.0,
        "coolant_wet_default": False,
        "datums": ["home_pad", "pickup_tray", "dropoff_tray"],
        "plain_english_focus": "5-minute safe desktop sandbox with read-only Feetech servo probe, $0/mo local LLM option, and table-crash prevention.",
    },
    "ehs": {
        "label": "EHS / Plant Safety & Insurance Auditor",
        "default_robot": "ehs-audit-cell-01",
        "hardware_target": "ur5e_cnc",
        "budget_tier": "starter",
        "hal_driver": "castor_hal.drivers.audit_shadow",
        "dof": 6,
        "workspace_box_m": {"x": [-0.70, 0.70], "y": [0.05, 0.80], "z": [0.02, 0.90]},
        "exclusions": [
            {"name": "human_egress_corridor", "min": [-0.80, -0.40, 0.00], "max": [0.80, 0.05, 2.00]},
            {"name": "estop_access_clearance", "min": [0.45, -0.10, 0.00], "max": [0.80, 0.35, 1.60]},
        ],
        "max_tcp_velocity_mps": 0.20,
        "max_contact_force_n": 30.0,
        "coolant_wet_default": False,
        "datums": ["audit_origin", "egress_boundary", "estop_station"],
        "plain_english_focus": "Strict ISO 13850 & ISO 13849-1 hardware/software boundary clarity, fail-closed Envelope 0.2 verification, and offline-verifiable RFC 8785 SHA-256 receipts.",
    },
}

_HAND_FAMILY_SPECS: dict[str, dict[str, Any]] = {
    "parallel_2f": {
        "label": "2-Finger Parallel Jaws (Robotiq 2F-85/140, Feetech SO-ARM101, SMC)",
        "yaml_lines": [
            "      name: primary_parallel_2f",
            "      family: parallel_2f",
            "      driver: castor_hal.end_effectors.parallel_2f",
            "      max_payload_kg: {payload_kg}",
            "      max_accel_mps2: 1.5",
            "      slip_safety_factor: 2.0",
            "      fragile_mode_cap_n: {fragile_n}",
            "      fail_safe_on_software_hold: maintain_grasp",
            "      tcp_offset_m: [0.0, 0.0, 0.14]",
            "      stroke_mm: [0.0, 85.0]",
            "      force_range_n: [5.0, {max_force_n}]",
        ],
    },
    "concentric_3f": {
        "label": "3-Jaw Concentric Chuck / Gripper (Schunk PZN-plus, Kitagawa/Haas)",
        "yaml_lines": [
            "      name: primary_concentric_3f",
            "      family: concentric_3f",
            "      driver: castor_hal.end_effectors.concentric_3f",
            "      max_payload_kg: {payload_kg}",
            "      max_accel_mps2: 1.2",
            "      slip_safety_factor: 2.0",
            "      fail_safe_on_software_hold: maintain_grasp",
            "      tcp_offset_m: [0.0, 0.0, 0.16]",
            "      bore_diameter_mm: [12.0, 110.0]",
            "      jaw_force_range_n: [25.0, 1200.0]",
            "      max_chuck_rpm: 0.0",
            "      min_chuck_pressure_bar: 5.5",
            "      require_drawbar_locked: true",
            "      require_part_seated: true",
            "      jaw_mass_kg: 0.25",
            "      torque_safety_factor: 2.0",
        ],
    },
    "dexterous_5f": {
        "label": "5-Finger Dexterous Hand (Asimov 1, Shadow, Tesollo, Inspire, Ability)",
        "yaml_lines": [
            "      name: primary_dexterous_5f",
            "      family: dexterous_5f",
            "      driver: castor_hal.end_effectors.dexterous_5f",
            "      max_payload_kg: {payload_kg}",
            "      max_accel_mps2: 1.2",
            "      slip_safety_factor: 2.0",
            "      fragile_mode_cap_n: 15.0",
            "      fail_safe_on_software_hold: maintain_grasp",
            "      tcp_offset_m: [0.0, 0.0, 0.18]",
            "      allowed_primitives: [pinch, tripod, power, hook, precision_cylindrical]",
            "      max_total_crush_force_n: 35.0",
            "      max_tendon_tension_n: 28.0",
            "      max_tactile_normal_n: 12.0",
            "      max_finger_temp_c: 55.0",
            "      tactile_feedback_required: true",
        ],
    },
    "vacuum_suction": {
        "label": "Vacuum / Bernoulli Suction Cups (Piab, Schmalz, Festo)",
        "yaml_lines": [
            "      name: primary_vacuum_suction",
            "      family: vacuum_suction",
            "      driver: castor_hal.end_effectors.vacuum_suction",
            "      max_payload_kg: {payload_kg}",
            "      max_accel_mps2: 1.5",
            "      slip_safety_factor: 2.0",
            "      fail_safe_on_software_hold: maintain_grasp",
            "      tcp_offset_m: [0.0, 0.0, 0.12]",
            "      cup_count: 4",
            "      effective_area_cm2: 19.6",
            "      min_vacuum_kpa: -62.0",
            "      slip_guard_drop_pct: 15.0",
            "      pad_friction_coeff: 0.50",
        ],
    },
    "magnetic_atc": {
        "label": "Electromagnetic Gripper / Automatic Tool Changer (Schunk EGM, ATI QC)",
        "yaml_lines": [
            "      name: primary_magnetic_atc",
            "      family: magnetic_atc",
            "      driver: castor_hal.end_effectors.magnetic_atc",
            "      max_payload_kg: {payload_kg}",
            "      max_accel_mps2: 1.2",
            "      slip_safety_factor: 2.0",
            "      fail_safe_on_software_hold: maintain_grasp",
            "      tcp_offset_m: [0.0, 0.0, 0.15]",
            "      ferromagnetic_only: true",
            "      max_holding_force_n: 480.0",
            "      min_airgap_derating_mm: 0.5",
            "      max_airgap_mm: 2.0",
            "      require_lock_pin_verified: true",
            "      require_spindle_zero_rpm: true",
            "      require_flux_verified: true",
            "      max_spindle_rpm_for_entry: 0.0",
        ],
    },
    "bimanual_coordinated": {
        "label": "Dual-Arm Coordinated Manipulation (Asimov 1, dual UR5e/FR5/YAM)",
        "yaml_lines": [
            "      name: primary_bimanual_coordinated",
            "      family: bimanual_coordinated",
            "      driver: castor_hal.end_effectors.bimanual_coordinated",
            "      max_payload_kg: {payload_kg}",
            "      max_accel_mps2: 1.0",
            "      slip_safety_factor: 2.0",
            "      fail_safe_on_software_hold: maintain_grasp",
            "      tcp_offset_m: [0.0, 0.0, 0.15]",
            "      max_combined_payload_kg: {payload_kg}",
            "      max_single_arm_payload_kg: {single_arm_kg}",
            "      allowed_load_split_ratio: [0.35, 0.65]",
            "      min_inter_arm_clearance_m: 0.08",
            "      max_opposing_squeeze_n: 40.0",
            "      max_sync_skew_ms: 20.0",
            "      allowed_coordinated_primitives: [bimanual_crate_lift, bimanual_carry, bimanual_handoff]",
        ],
    },
}

_AI_TIER_ALIASES: dict[str, str] = {
    "claude": "claude",
    "anthropic": "claude",
    "antigravity": "antigravity",
    "agy": "antigravity",
    "gemini": "antigravity",
    "codex": "codex",
    "openai": "codex",
    "apple_mlx": "apple_mlx",
    "mlx": "apple_mlx",
    "apple": "apple_mlx",
    "mac": "apple_mlx",
    "google_gemma4": "google_gemma4",
    "gemma4": "google_gemma4",
    "gemma": "google_gemma4",
    "ollama": "ollama",
    "local": "ollama",
    "onprem": "ollama",
    "airgapped": "apple_mlx",
}


def _build_onboarding_kit(
    *,
    user_type: str,
    setup_depth: str,
    hand_family: str,
    ai_tier: str,
    organization: str,
    robot_name: str,
    hardwired_estop_confirmed: bool,
) -> dict[str, Any]:
    ut = (user_type or "cnc").strip().lower()
    depth = (setup_depth or "quick").strip().lower()
    hf = (hand_family or "parallel_2f").strip().lower()
    ai_norm = _AI_TIER_ALIASES.get((ai_tier or "claude").strip().lower(), "claude")

    if ut not in _ONBOARD_PERSONAS:
        raise ValueError(f"Unsupported user_type '{user_type}'. Expected one of: {sorted(_ONBOARD_PERSONAS)}")
    if depth not in ("quick", "advanced"):
        raise ValueError(f"Unsupported setup_depth '{setup_depth}'. Expected 'quick' or 'advanced'.")
    if hf not in _HAND_FAMILY_SPECS:
        raise ValueError(f"Unsupported hand_family '{hand_family}'. Expected one of: {sorted(_HAND_FAMILY_SPECS)}")

    persona = _ONBOARD_PERSONAS[ut]
    hand = _HAND_FAMILY_SPECS[hf]
    rname = (robot_name or persona["default_robot"]).strip()
    org = (organization or "My Shop Cell").strip()

    # Scale payload & force conservatively for benchtop vs industrial
    payload_kg = 0.5 if ut == "benchtop" else (10.0 if hf == "bimanual_coordinated" else 5.0)
    single_arm_kg = round(payload_kg * 0.6, 2)
    fragile_n = 10.0 if ut == "benchtop" else 25.0
    max_force_n = 25.0 if ut == "benchtop" else 120.0
    max_vel = persona["max_tcp_velocity_mps"] if depth == "advanced" else round(persona["max_tcp_velocity_mps"] * 0.85, 2)
    max_contact = persona["max_contact_force_n"] if depth == "advanced" else round(persona["max_contact_force_n"] * 0.85, 1)

    ws = persona["workspace_box_m"]
    ex_lines: list[str] = []
    for ex in persona["exclusions"]:
        ex_lines.extend(
            [
                f"      - name: {ex['name']}",
                f"        min: {json.dumps(ex['min'])}",
                f"        max: {json.dumps(ex['max'])}",
            ]
        )

    ee_lines = [
        line.format(
            payload_kg=payload_kg,
            single_arm_kg=single_arm_kg,
            fragile_n=fragile_n,
            max_force_n=max_force_n,
        )
        for line in hand["yaml_lines"]
    ]

    estop_yaml = "true" if hardwired_estop_confirmed else "false"
    coolant_yaml = "true" if persona["coolant_wet_default"] else "false"
    airgap_yaml = "true" if (ut == "oem" or ai_norm in ("apple_mlx", "google_gemma4", "ollama")) else "false"
    datums_yaml = ", ".join(persona["datums"])

    robot_md_v1_1 = "\n".join(
        [
            "---",
            'schema_version: "1.1"',
            f"organization: {json.dumps(org)}",
            f"onboarding_track: {ut}",
            f"setup_depth: {depth}",
            f"ai_tier: {ai_norm}",
            f"airgapped_local_only: {airgap_yaml}",
            "trust_ladder:",
            "  starting_level: L0_OBSERVE",
            "  speed_cap_pct_l0: 0",
            "  speed_cap_pct_l1: 30",
            "  require_operator_elicitation_to_promote: true",
            "safety_boundary:",
            "  software_enforcement_only: true",
            f"  hardwired_iso_13850_estop_confirmed: {estop_yaml}",
            "  iso_13849_1_door_interlocks_unmodified: true",
            '  disclaimer: "Deterministic default-deny software pre-flight gate & RFC 8785 SHA-256 audit log — NEVER a replacement for certified hardwired ISO 13850 E-stops or ISO 13849-1 safety relays."',
            "embodiments:",
            f"  {rname}:",
            f"    hal_driver: {persona['hal_driver']}",
            f"    dof: {persona['dof']}",
            "    workspace_box_m:",
            f"      x: {json.dumps(ws['x'])}",
            f"      y: {json.dumps(ws['y'])}",
            f"      z: {json.dumps(ws['z'])}",
            "    exclusion_boxes_m:",
            *ex_lines,
            f"    max_tcp_velocity_mps: {max_vel}",
            f"    max_contact_force_n: {max_contact}",
            f"    coolant_wet_guard: {coolant_yaml}",
            "    allowed_tools:",
            "      - status.report",
            "      - arm.state",
            "      - arm.move_bounded",
            "      - arm.estop",
            "      - arm.estop.clear",
            "      - tool.grip",
            "      - tool.release",
            "    end_effector:",
            *ee_lines,
            "---",
            "",
            f"# {org} — `{rname}` (`ROBOT.md` v1.1)",
            "",
            f"- **Track:** `{ut}` ({persona['label']}) · **Depth:** `{depth}`",
            f"- **Hand HAL Family:** `{hf}` ({hand['label']})",
            f"- **Starting Autonomy Tier:** `L0_OBSERVE` (0% speed/force cap — zero physical motion)",
            f"- **Datums to Teach After 48h L0 Shadow Trial:** `{datums_yaml}`",
            "- **Hardware Safety Rule:** Pair with a tested, hardwired **ISO 13850** red mushroom E-stop and intact **ISO 13849-1** door interlocks before ever promoting past `L0_OBSERVE`.",
            "",
        ]
    )

    bundle = _build_bundle_recommendation(
        llm_provider=ai_norm,
        budget_tier=persona["budget_tier"],
        hardware_target=persona["hardware_target"],
    )
    cell_dir = f"./{rname}" if rname.endswith("-cell") else f"./{rname}-cell"
    cli_onboard_cmd = (
        f"robot-gate onboard --persona {ut} --mode {depth} "
        f"--hand-family {hf} --ai-tier {ai_norm} --robot-name {rname} --out {cell_dir} --non-interactive"
    )
    serve_cmd = f"robot-gate serve --dir {cell_dir} --port 8785"
    install_commands = [
        "# 1. Install published Apache-2.0 RRF core packages (PyPI):",
        bundle["install_commands"][0],
        "# 2. Install Graft Robotics local on-robot gate & Cell Console from your checkout:",
        "uv pip install -e ./robot-gate[server]",
        "# 3. Scaffold your signed ROBOT.md v1.1 cell in zero-motion L0 OBSERVE:",
        cli_onboard_cmd,
        "# 4. Start local Graft Cell Console in zero-motion L0 OBSERVE on :8785:",
        serve_cmd,
        *bundle["install_commands"][1:],
    ]

    llm_coach_instructions = (
        f"You are the Graft Robotics Remote Shop Onboarding Specialist coaching {org} "
        f"(track=`{ut}`: {persona['label']}, depth=`{depth}`, robot=`{rname}`, hand=`{hf}`, AI=`{ai_norm}`).\n"
        f"Focus: {persona['plain_english_focus']}\n"
        "Coaching rules:\n"
        "1. Speak in plain shop English — zero robotics or CNC jargon unless the operator asks for advanced math.\n"
        "2. Ask the operator for 1–2 wide phone photos of the workspace (or a plain-English layout if ITAR/camera-restricted). "
        "Conservatively identify walkways, machine door sweeps, spinning spindles, overhead fixtures, electrical cabinets, and unlabeled chemical jugs.\n"
        "3. Never claim Graft software replaces a physical E-stop. Confirm hardwired ISO 13850 red E-stop + ISO 13849-1 door interlocks before any motion.\n"
        f"4. Verify Hand HAL (`{hf}`) limits and walk through teaching datums ({datums_yaml}) ONLY after a clean 48-hour zero-motion L0 OBSERVE shadow trial.\n"
        "5. If any object is unlabeled or unfamiliar, use Graft's Semantic-to-Deterministic Ratchet (`graft_check_semantic_action`) — never guess."
    )

    first_48h_l0_plan = {
        "starting_level": "L0_OBSERVE",
        "physical_motion_allowed": False,
        "duration_hours": 48,
        "console_url_local": f"{CELL_CONSOLE_URL}/",
        "phases": [
            {
                "window": "Hours 0–2: Boot & Deterministic Dry-Run",
                "steps": [
                    f"Save and Ed25519-sign `{cell_dir}/ROBOT.md` v1.1 (or run `{cli_onboard_cmd}`).",
                    f"Boot the local Graft Cell Console (`{serve_cmd}`) in `L0_OBSERVE` (0% speed/force cap) and open `{CELL_CONSOLE_URL}/`.",
                    "Run 1 in-bounds test proposal (`ALLOW` shadow receipt) and 1 keep-out / slip violation (`DENY` receipt) and verify RFC 8785 SHA-256 hashes.",
                ],
            },
            {
                "window": "Hours 2–24: Zero-Motion Shift Shadowing",
                "steps": [
                    "Run normal shop/lab operations while the AI planner logs proposed intents against live read-only sensors (`graft_discover_devices`).",
                    "Verify zero stale sensor warnings and confirm walkways, doors, and exclusion boxes trigger deterministic `DENY` whenever crossed.",
                ],
            },
            {
                "window": "Hours 24–48: Audit Review & L1 Graduation Gate",
                "steps": [
                    "Inspect the 48-hour SHA-256 shadow receipt log (`/shadow-trial-audit`) for 0 unexpected allows and 0 envelope violations.",
                    "Confirm physical ISO 13850 red E-stop button test and ISO 13849-1 door interlock integrity.",
                    f"Only when every check is green, promote `{rname}` to `L1_ATOMIC` (30% speed cap, human approval every action) via `graft_trust_ladder(action='promote', robot_id='{rname}')` and teach datums: {', '.join(persona['datums'])}.",
                ],
            },
        ],
    }

    estop_status = (
        "CONFIRMED by operator (still verify physically before every shift)."
        if hardwired_estop_confirmed
        else "NOT YET CONFIRMED — cell is strictly locked to zero-motion L0_OBSERVE simulation/shadow mode until an operator verifies a hardwired ISO 13850 E-stop."
    )
    safety_boundary_note = (
        "MANDATORY SAFETY BOUNDARY: `robot-gate`, `graft-core`, `graft-watchdog`, `bounded-embodiment`, and "
        "`robot-md-gateway` provide a deterministic, default-deny SOFTWARE pre-flight gate and offline-verifiable "
        "RFC 8785 / SHA-256 audit chain. They are NEVER a certified ISO 13850 hardware emergency stop or ISO 13849-1 "
        f"safety relay / door interlock. Hardwired ISO 13850 E-stop status: {estop_status}"
    )

    studio_url = f"https://graftrobotics.ai/onboard/?persona={ut}&depth={depth}&hand={hf}&ai={ai_norm}"

    return {
        "ok": True,
        "user_type": ut,
        "persona_label": persona["label"],
        "setup_depth": depth,
        "hand_family": hf,
        "hand_label": hand["label"],
        "ai_tier": ai_norm,
        "organization": org,
        "robot_name": rname,
        "starting_trust_level": "L0_OBSERVE",
        "motion_authorized": False,
        "hardwired_estop_confirmed": bool(hardwired_estop_confirmed),
        "estimated_llm_cost": bundle["estimated_llm_cost"],
        "onboard_studio_url": "https://graftrobotics.ai/onboard/",
        "onboard_studio_deeplink": studio_url,
        "cli_equivalent": cli_onboard_cmd,
        "robot_md_v1_1": robot_md_v1_1,
        "install_commands": install_commands,
        "client_config": bundle["client_config"],
        "llm_coach_instructions": llm_coach_instructions,
        "first_48h_l0_plan": first_48h_l0_plan,
        "safety_boundary_note": safety_boundary_note,
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
    name="Latest Verified Pi 5 Benchmarks & EV-03 Rehearsal Report",
    description="Reproducible 4-layer graft-eval scorecard (Rust graft-core, graft-watchdog, 254/0 hostile fuzzing, EV-03 rehearsal). Note: legacy kinematic SET-Sim is quarantined pending real-contact hardware evaluation.",
    mime_type="application/json",
)
def resource_benchmarks() -> str:
    out: dict[str, Any] = {
        "benchmarks_url": "https://graftrobotics.ai/benchmarks/",
        "set_sim_status": "QUARANTINED — legacy kinematic SET-Sim disabled contact physics (contype='0') and analytically contracted jitter (cx_est *= 0.35); do not cite 36/36. Use graft_generate_onboarding_kit / remote-shop-onboarding for real hardware onboarding.",
    }
    p = BENCHMARKS_DIR / "graft-eval-report.json"
    if p.exists():
        try:
            out["graft_eval"] = json.loads(p.read_text(encoding="utf-8"))
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
        f"2. Read `graft://benchmarks/latest` to show the customer our signed Pi 5 EV-03 rehearsal bundle and Rust kernel stress results.\n"
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
    name="remote-shop-onboarding",
    description="Act as a plain-English Remote Shop Onboarding Specialist (zero FDE / zero machinist needed): phone-photo hazard review, ISO 13850 E-stop check, 6 Hand HAL families, onboarding kit & 48h L0 shadow trial.",
)
def prompt_remote_shop_onboarding(
    user_type: str = "cnc",
    setup_depth: str = "quick",
    organization: str = "My Shop Cell",
) -> str:
    return (
        f"Act as the Graft Robotics Remote Shop Onboarding Specialist for `{organization}` "
        f"(track=`{user_type}`, depth=`{setup_depth}` — zero FDE and zero machining specialist required):\n"
        f"1. Adapt your language to `{user_type}` (`cnc`, `lab`, `oem`, `benchtop`, or `ehs`) and `{setup_depth}` (`quick` vs `advanced`). Keep questions plain-English and one step at a time.\n"
        f"2. Ask the operator for 1–2 wide phone photos of their machine/workspace (or a plain-English layout if camera-restricted). "
        f"Conservatively flag walkways, door/spindle sweeps, electrical cabinets, overhead fixtures, and any unlabeled containers for keep-out zones.\n"
        f"3. Read `graft://safety/boundary-policy` and confirm a hardwired **ISO 13850** red mushroom E-stop and intact **ISO 13849-1** door interlocks/safety relays. "
        f"State clearly that Graft software NEVER replaces hardware E-stops.\n"
        f"4. Help the operator select one of the 6 Hand HAL families (`parallel_2f`, `concentric_3f`, `dexterous_5f`, `vacuum_suction`, `magnetic_atc`, `bimanual_coordinated`) "
        f"and their AI tier (`claude`, `antigravity`, `codex`, `apple_mlx`, `google_gemma4`, `ollama`).\n"
        f"5. Call `graft_generate_onboarding_kit(user_type='{user_type}', setup_depth='{setup_depth}', organization='{organization}', interactive=True)` "
        f"(or pass the collected fields explicitly) to generate their `ROBOT.md` v1.1, working install & `robot-gate serve --dir ... --port 8785` commands, LLM coach prompt, and link to https://graftrobotics.ai/onboard/.\n"
        f"6. Launch their first **48-hour zero-motion `L0 OBSERVE` shadow trial** on `{CELL_CONSOLE_URL}/` before ever teaching datums or promoting to `L1 ATOMIC`."
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


@mcp.prompt(
    name="ros2-compliance-audit",
    description="End-to-end ROS 2 Pre-Flight Gate & ISO 10218:2025 / EU (2023/1230) Compliance Audit (ros2-bridge -> check -> compliance-pack --verify -> opt-in vault push -> Cloudflare cloudflare-build.sh).",
)
def prompt_ros2_compliance_audit(
    workspace_dir: str = ".",
    stack: str = "moveit2",
    embodiment: str = "ur5e",
) -> str:
    return (
        f"Execute the Graft Robotics ROS 2 Pre-Flight & Compliance Audit Playbook for `{embodiment}` "
        f"(`stack={stack}`, `workspace_dir={workspace_dir}` — Zero GitHub Actions, Cloudflare-only):\n"
        f"1. Read `graft://safety/boundary-policy` and confirm hardwired ISO 13850 E-stops, ISO 13849-1 safety relays/interlocks, and ITAR/EAR air-gap posture.\n"
        f"2. Call `graft_ros2_generate_bundle(workspace_dir='{workspace_dir}', output_dir='{workspace_dir}/ros2_bundle', stack='{stack}', embodiment='{embodiment}', frame_id='base_link')` (or run `robot-gate ros2-bridge`).\n"
        f"3. Run the 4-stage deterministic pre-flight gate (`robot-gate check --dir '{workspace_dir}' --sim-only`) to emit a signed `gate_receipt.json` matching the live workspace fingerprint.\n"
        f"4. Call `graft_generate_compliance_pack(workspace_dir='{workspace_dir}')` (or `robot-gate compliance-pack --dir '{workspace_dir}' --verify`) and confirm `valid=True` with 0 private keys / 0 `.pem` files.\n"
        f"5. Call `graft_vault_status(robot_id='{embodiment}', limit=20)` — verify zero phone-home when `GRAFT_VAULT_API_KEY` is unset, or review drift alerts after an opt-in `robot-gate vault push` (non-ITAR/EAR cells only).\n"
        f"6. Wire `robot-gate/ci/cloudflare-build.sh` into Cloudflare Pages/Workers CI/CD (Zero GitHub Actions)."
    )


# ==============================================================================
# MCP TOOLS (19 TOOLS INCLUDING ROS 2 BUNDLE, FLEET VAULT, AGENT CONNECT & COMPLIANCE PACK)
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
        # Fail-closed human-in-the-loop promotion gate: requires interactive MCP Form Elicitation
        # confirming both promotion AND physical ISO 13850 E-stop readiness.
        e_action, e_data = await _try_elicit(
            ctx,
            f"Operator sign-off required to promote '{robot_id}' one level on the Graft Trust Ladder (L0->L3). Confirm physical ISO 13850 E-stop is verified.",
            TrustPromotionElicitation,
        )
        if e_action == "accept" and e_data is not None:
            if not (e_data.confirm_promotion and e_data.hardware_estop_verified):
                return _result(
                    f"Trust promotion HELD for '{robot_id}': operator must confirm both promotion and physical ISO 13850 E-stop readiness.",
                    {"promoted": False, "fail_closed": True, "elicitation": "rejected_safety_checkbox"},
                )
            operator = e_data.operator_name or operator
        elif e_action in ("decline", "cancel"):
            return _result(
                f"Trust promotion cancelled by operator for '{robot_id}'.",
                {"promoted": False, "fail_closed": True, "elicitation": e_action},
            )
        else:
            # FAIL CLOSED when MCP client does not support elicitation (e_action == "unsupported")
            # or returned no structured confirmation data — NEVER silently promote!
            return _result(
                f"Trust promotion REFUSED (fail-closed) for '{robot_id}': this MCP client does not support interactive "
                f"Form Elicitation (ctx.elicit), so operator + physical ISO 13850 E-stop confirmation could not be verified. "
                f"Confirm promotion in a client supporting MCP elicitation or via the authenticated local Graft Cell Console ({CELL_CONSOLE_URL}).",
                {
                    "promoted": False,
                    "fail_closed": True,
                    "elicitation": e_action,
                    "robot_id": robot_id,
                    "cell_console_url": CELL_CONSOLE_URL,
                },
            )

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
        d = evaluate_audio_signal(sensor_id=sensor_id, db_spl=72.0, chatter_score=chatter_score, transcript=transcript)
    elif modality == "video_webcam":
        hc = max(0, int(human_count))
        d = evaluate_video_signal(
            sensor_id=sensor_id,
            human_count=hc,
            nearest_human_m=estimated_distance_m if hc > 0 else None,
        )
    else:
        d = evaluate_wifi_motion_signal(sensor_id=sensor_id, rssi_dbm_samples=[-40.0, -49.0, -37.0, -48.0], estimated_distance_m=estimated_distance_m)
    return _result(f"Ambient [{d.action}] ({modality}): {d.reason}", d.__dict__)


@mcp.tool(name="graft_generate_onboarding_kit", title="Generate Remote Shop Onboarding Kit", meta=INLINE_META)
async def graft_generate_onboarding_kit(
    user_type: str = "cnc",
    setup_depth: str = "quick",
    hand_family: str = "parallel_2f",
    ai_tier: str = "claude",
    organization: str = "My Shop Cell",
    robot_name: str = "",
    hardwired_estop_confirmed: bool = False,
    interactive: bool = False,
    ctx: Context | None = None,
) -> types.CallToolResult:
    """Generate a complete self-serve Remote Shop Onboarding Kit (ROBOT.md v1.1 starting in L0 OBSERVE, uv-first install commands, LLM coach instructions, 48h L0 shadow trial plan, ISO 13850 safety boundary note, and https://graftrobotics.ai/onboard/ link). Supports native MCP Form Elicitation via RemoteOnboardingElicitation."""
    elicitation_status = "skipped"
    if interactive or (user_type or "").strip().lower() == "interactive":
        e_action, e_data = await _try_elicit(
            ctx,
            "Configure your Graft Robotics Remote Shop Onboarding Kit (starts strictly in zero-motion L0 OBSERVE shadow mode). Confirm whether a physical hardwired ISO 13850 E-stop is installed and tested.",
            RemoteOnboardingElicitation,
        )
        elicitation_status = e_action
        if e_action == "accept" and e_data is not None:
            user_type = e_data.user_type
            setup_depth = e_data.setup_depth
            hand_family = e_data.hand_family
            ai_tier = e_data.ai_tier
            hardwired_estop_confirmed = bool(e_data.hardwired_estop_confirmed)
        elif e_action in ("decline", "cancel"):
            return _result(
                "Remote shop onboarding kit generation cancelled by operator.",
                {"ok": False, "generated": False, "elicitation": e_action},
            )
        elif (user_type or "").strip().lower() == "interactive":
            user_type = "cnc"

    try:
        kit = _build_onboarding_kit(
            user_type=user_type,
            setup_depth=setup_depth,
            hand_family=hand_family,
            ai_tier=ai_tier,
            organization=organization,
            robot_name=robot_name,
            hardwired_estop_confirmed=hardwired_estop_confirmed,
        )
    except ValueError as exc:
        return _result(f"Invalid onboarding kit parameter: {exc}", {"ok": False, "error": str(exc)})

    kit["elicitation"] = elicitation_status
    estop_tag = "ISO 13850 E-stop confirmed" if kit["hardwired_estop_confirmed"] else "ISO 13850 E-stop NOT confirmed (L0 shadow only)"
    summary = (
        f"Onboarding Kit ready for {kit['organization']} (`{kit['robot_name']}` · track={kit['user_type']} · "
        f"depth={kit['setup_depth']} · hand={kit['hand_family']} · ai={kit['ai_tier']} · {estop_tag}). "
        f"Starts strictly in zero-motion L0_OBSERVE for 48h shadow trial. Web studio: {kit['onboard_studio_url']}"
    )
    return _result(summary, kit)


@mcp.tool(name="graft_run_set_benchmark", title="SET-Sim Quarantine Notice & Real Hardware Onboarding", meta=INLINE_META)
def graft_run_set_benchmark() -> types.CallToolResult:
    """Disclose the quarantine status of legacy kinematic SET-Sim (36/36) and direct operators to real hardware onboarding."""
    payload = {
        "ok": False,
        "status": "QUARANTINED",
        "quarantined_artifact": "graft-eval/set_benchmark_sim.py",
        "reasons": [
            "All 6 legacy SET-Sim MuJoCo XMLs disabled contact physics globally (`<geom contype='0' conaffinity='0'/>`) and had zero robot arms or F/T sensors.",
            "The closed-loop search loop analytically contracted ground-truth jitter (`cx_est *= 0.35`), mathematically guaranteeing 36/36.",
            "Legacy kinematic SET-Sim is quarantined pending real-contact simulation rewrite or uncut physical Bob (`SO-ARM101`) hardware evaluation.",
        ],
        "recommended_next_steps": [
            "Use `graft_generate_onboarding_kit` or the `/remote-shop-onboarding` playbook to generate a real `L0 OBSERVE` hardware onboarding kit.",
            "Download the printable 3-datum calibration mat at https://graftrobotics.ai/set/ for repeatable physical benchtop trials.",
            "Inspect genuinely verified ARM64 Pi 5 Rust kernel, 254/0 hostile fuzzing, and signed EV-03 rehearsal benchmarks via `graft://benchmarks/latest`.",
        ],
        "onboard_studio_url": "https://graftrobotics.ai/onboard/",
        "set_hardware_hub_url": "https://graftrobotics.ai/set/",
    }
    return _result(
        "SET-Sim QUARANTINED: Legacy kinematic SET-Sim (36/36) is deprecated and must NOT be cited as contact physics or RoboCurve benchmark parity "
        "(collisions were disabled via contype='0' and jitter was analytically contracted via cx_est *= 0.35). "
        "For real hardware onboarding and physical proof, run `graft_generate_onboarding_kit` or `/remote-shop-onboarding`, and see https://graftrobotics.ai/set/.",
        payload,
    )


@mcp.tool(
    name="graft_generate_compliance_pack",
    title="Generate ISO 10218:2025 & EU 2023/1230 Compliance Pack",
    meta=INLINE_META,
)
def graft_generate_compliance_pack(
    workspace_dir: str = ".",
    output_dir: str = "",
    zip_filename: str = "graft-compliance-pack.zip",
    organization: str = "",
    embodiment: str = "",
) -> types.CallToolResult:
    """Generate and offline-verify a tamper-evident ISO 10218:2025 & EU (2023/1230) compliance dossier ZIP for a robot-gate workspace (fail-closed; strictly excludes all private keys)."""
    ws = Path(workspace_dir).expanduser().resolve()
    if not ws.is_dir():
        return _result(
            f"Compliance pack FAILED (fail-closed): workspace directory does not exist: {ws}",
            {
                "ok": False,
                "valid": False,
                "fail_closed": True,
                "error": f"workspace_dir not found: {ws}",
            },
        )

    out_path = Path(output_dir).expanduser().resolve() if output_dir.strip() else None
    safe_zip_name = Path(zip_filename.strip()).name if zip_filename.strip() else "graft-compliance-pack.zip"
    if not safe_zip_name.lower().endswith(".zip"):
        safe_zip_name += ".zip"

    try:
        from robot_gate.compliance_pack import (
            ISO_13850_HARDWARE_BOUNDARY_ATTESTATION,
            generate_compliance_pack,
            verify_compliance_pack,
        )

        pack = generate_compliance_pack(
            ws,
            output_dir=out_path,
            zip_filename=safe_zip_name,
            organization=organization.strip() or None,
            embodiment=embodiment.strip() or None,
        )
        verification = verify_compliance_pack(pack.zip_path)
    except Exception as exc:
        return _result(
            f"Compliance pack generation FAILED (fail-closed): {exc}",
            {
                "ok": False,
                "valid": False,
                "fail_closed": True,
                "workspace_dir": str(ws),
                "error": str(exc),
            },
        )

    if not verification.valid:
        return _result(
            f"Compliance pack FAILED offline verification (fail-closed): {'; '.join(verification.errors)}",
            {
                "ok": False,
                "valid": False,
                "fail_closed": True,
                "zip_path": str(pack.zip_path),
                "manifest_sha256": pack.manifest_sha256,
                "verification": verification.to_dict(),
            },
        )

    payload: dict[str, Any] = {
        "ok": True,
        "valid": True,
        "plugin_version": PLUGIN_VERSION,
        "compliance_pack": pack.to_dict(),
        "verification": verification.to_dict(),
        "security_exclusions": dict(pack.manifest.get("security_exclusions", {})),
        "private_keys_exposed": False,
        "safety_boundary": ISO_13850_HARDWARE_BOUNDARY_ATTESTATION,
        "compliance_studio_url": "https://graftrobotics.ai/compliance/",
    }
    return _result(
        f"Compliance pack VERIFIED [{pack.overall_status} · {pack.readiness_score_pct}%]: "
        f"{pack.zip_path} ({verification.files_verified} files verified, 0 private keys, "
        f"manifest_sha256={pack.manifest_sha256}).",
        payload,
    )


@mcp.tool(
    name="graft_ros2_generate_bundle",
    title="Generate ROS 2 Pre-Flight Launch Bundle",
    meta=INLINE_META,
)
def graft_ros2_generate_bundle(
    workspace_dir: str = ".",
    output_dir: str = "./ros2_bundle",
    stack: str = "moveit2",
    embodiment: str = "ur5e",
    frame_id: str = "base_link",
) -> types.CallToolResult:
    """Generate a drop-in ROS 2 pre-flight boundary launch bundle (`graft_ros2_gate.launch.py`, `graft_ros2_params.yaml`, `README_ROS2.md`) via `robot_gate.ros2_adapter.generate_ros2_launch_bundle()`."""
    ws = Path(workspace_dir).expanduser().resolve()
    if not ws.is_dir():
        return _result(
            f"ROS 2 bundle generation FAILED (fail-closed): workspace directory does not exist: {ws}",
            {
                "ok": False,
                "fail_closed": True,
                "plugin_version": PLUGIN_VERSION,
                "error": f"workspace_dir not found: {ws}",
            },
        )
    out = Path(output_dir).expanduser()
    if not out.is_absolute():
        out = (ws / out).resolve()
    else:
        out = out.resolve()

    try:
        from robot_gate.ros2_adapter import generate_ros2_launch_bundle

        bundle = generate_ros2_launch_bundle(
            ws,
            out,
            embodiment=embodiment.strip() or None,
            stack=stack.strip() or "moveit2",
            frame_id=frame_id.strip() or "base_link",
        )
    except Exception as exc:
        return _result(
            f"ROS 2 bundle generation FAILED (fail-closed): {exc}",
            {
                "ok": False,
                "fail_closed": True,
                "plugin_version": PLUGIN_VERSION,
                "workspace_dir": str(ws),
                "error": str(exc),
            },
        )

    payload: dict[str, Any] = {
        "ok": True,
        "plugin_version": PLUGIN_VERSION,
        "frame_id": frame_id.strip() or "base_link",
        **bundle,
    }
    return _result(
        f"ROS 2 launch bundle ready for '{bundle['embodiment']}' (stack={bundle['stack']}, frame={payload['frame_id']}) "
        f"at {bundle['output_dir']} -> graft_ros2_gate.launch.py, graft_ros2_params.yaml, README_ROS2.md.",
        payload,
    )


@mcp.tool(
    name="graft_vault_status",
    title="Check Opt-In Hosted Fleet Vault Status",
    meta=INLINE_META,
)
def graft_vault_status(
    robot_id: str | None = None,
    limit: int = 20,
) -> types.CallToolResult:
    """Query the opt-in Cloudflare D1 Hosted Fleet Vault for compliance receipts and drift alerts (100% opt-in / zero phone-home when GRAFT_VAULT_API_KEY is unset)."""
    from robot_gate.vault_client import fetch_vault_status

    res = fetch_vault_status(robot_id=robot_id, limit=limit)
    data: dict[str, Any] = {
        "plugin_version": PLUGIN_VERSION,
        **res.to_dict(),
    }
    if res.offline:
        summary = (
            "Hosted Fleet Vault OFFLINE (zero phone-home): GRAFT_VAULT_API_KEY is unset, "
            "so ZERO network calls were made. Set GRAFT_VAULT_API_KEY only for opt-in non-ITAR/EAR sync."
        )
    elif res.ok:
        summary = (
            f"Hosted Fleet Vault ONLINE: {len(res.receipts)} receipt(s), "
            f"{len(res.alerts)} active drift alert(s)."
        )
    else:
        summary = f"Hosted Fleet Vault error (http={res.http_status}): {res.error}"
    return _result(summary, data)


@mcp.tool(
    name="graft_connect_agent",
    title="Connect Any LLM Client to Any Robot (L0 OBSERVE)",
    meta=INLINE_META,
)
def graft_connect_agent(
    client: str = "claude",
    robot: str = "ur5e",
    environment: str = "industrial",
    include_vault: bool = False,
) -> types.CallToolResult:
    """Generate exact copy-paste MCP client config (Claude .mcp.json, Antigravity mcp_config.json, Codex ~/.codex/config.toml, Gemini gemini-extension.json, Apple MLX, Google Gemma 4 / Ollama), an L0 OBSERVE starter prompt, and mandatory ISO 13850 & ITAR/EAR boundary disclosures."""
    try:
        from robot_gate.mcp_server import build_connect_agent_bundle

        bundle = build_connect_agent_bundle(
            client=client,
            robot=robot,
            environment=environment,
            include_vault=include_vault,
            plugin_version=PLUGIN_VERSION,
        )
    except ValueError as exc:
        return _result(
            f"Connect agent configuration FAILED: {exc}",
            {
                "ok": False,
                "fail_closed": True,
                "plugin_version": PLUGIN_VERSION,
                "error": str(exc),
            },
        )

    vault_tag = "vault=OPT-IN" if bundle["include_vault_effective"] else "vault=OFFLINE(0 phone-home)"
    summary = (
        f"Agent Connect v{PLUGIN_VERSION} ready for {bundle['client_label']} -> "
        f"{bundle['robot_label']} ({bundle['environment']}, {vault_tag}, starting in L0_OBSERVE). "
        f"Config file: {bundle['config_filename']}. Studio: {bundle['connect_studio_url']}"
    )
    return _result(summary, bundle)


if __name__ == "__main__":
    mcp.run()
