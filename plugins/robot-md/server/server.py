#!/usr/bin/env python3
"""Robot-MD & OpenCastor Antigravity MCP App Server.

Provides live SO-ARM101 bus telemetry, ROBOT.md workspace bounds verification,
robot_doctor fault isolation, latching software e-stop, and an interactive
Antigravity side-pane / inline MCP App (`ui://robot-md/console.html`).
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any

from mcp import types
from mcp.server.fastmcp import FastMCP

APP_URI = "ui://robot-md/console.html"
HTML_PATH = Path(os.environ.get("ROBOT_MD_APP_HTML", Path(__file__).with_name("console.html")))
MANIFEST_PATH = Path(os.environ.get("ROBOT_MD_MANIFEST", "/home/craigm26/bob/ROBOT.md"))
ARM_PORT = os.environ.get(
    "ROBOT_MD_ARM_PORT",
    "/dev/serial/by-id/usb-1a86_USB_Single_Serial_5AAF219301-if00",
)
TRAVELER_PATH = Path("/home/craigm26/bob/demo-audit-traveler.json")

PANE_META = {
    "ui": {"resourceUri": APP_URI},
    "com.google.antigravity/ui": {
        "entrypoints": [
            {"type": "aux_pane", "title": "Robot-MD Console"},
            {"type": "global", "title": "Robot-MD Console"},
        ]
    },
}
INLINE_META = {"ui": {"resourceUri": APP_URI}}

mcp = FastMCP("robot-md-console")

_STATE: dict[str, Any] = {
    "estopped": False,
    "last_check": None,
}


def _read_live_arm() -> dict[str, Any]:
    """Read live SO-ARM101 Feetech STS3215 telemetry without moving any servo."""
    try:
        from so_arm101_actuator.actuator import SOArm101Actuator

        arm = SOArm101Actuator()
        out = arm.execute(
            envelope={"tool_name": "status.report", "tool_args": {}},
            manifest_path=MANIFEST_PATH,
            tier="read",
            config={"port": ARM_PORT, "baud": 1_000_000},
        )
        tele = out.telemetry or {}
        return {
            "reachable": bool(out.success),
            "port": ARM_PORT,
            "estopped": bool(tele.get("estopped", _STATE["estopped"])),
            "voltages_v": tele.get("motor_voltages_v") or {},
            "temps_c": tele.get("motor_temps_c") or {},
            "loads": tele.get("motor_loads") or {},
            "error": out.error_message,
        }
    except Exception as exc:
        return {
            "reachable": False,
            "port": ARM_PORT,
            "estopped": _STATE["estopped"],
            "voltages_v": {},
            "temps_c": {},
            "loads": {},
            "error": str(exc),
        }


def _recent_audit_steps(limit: int = 5) -> list[dict[str, Any]]:
    if not TRAVELER_PATH.exists():
        return []
    try:
        data = json.loads(TRAVELER_PATH.read_text())
        steps = data.get("steps") or []
        return [
            {
                "act": s.get("act"),
                "tool": s.get("tool"),
                "outcome": s.get("outcome_kind"),
                "sha256": (s.get("sha256") or "")[:16],
            }
            for s in steps[-limit:]
        ]
    except Exception:
        return []


def _snapshot() -> dict[str, Any]:
    bus = _read_live_arm()
    return {
        "ts": round(time.time(), 2),
        "manifest": str(MANIFEST_PATH),
        "manifest_exists": MANIFEST_PATH.exists(),
        "estopped": _STATE["estopped"] or bus["estopped"],
        "bus": bus,
        "last_check": _STATE["last_check"],
        "recent_audit": _recent_audit_steps(5),
    }


def _result(summary: str, data: dict[str, Any]) -> types.CallToolResult:
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=summary)],
        structuredContent=data,
    )


@mcp.resource(
    APP_URI,
    name="Robot-MD Console",
    mime_type="text/html;profile=mcp-app",
    meta={"ui": {"prefersBorder": False}},
)
def console_html() -> str:
    return HTML_PATH.read_text(encoding="utf-8")


@mcp.tool(name="open_robot_console", title="Robot-MD Console", meta=PANE_META)
def open_robot_console() -> types.CallToolResult:
    """Open the interactive Robot-MD & OpenCastor live telemetry and E-stop console."""
    snap = _snapshot()
    bus = snap["bus"]
    summary = (
        f"Robot-MD Console ready. Bus reachable={bus['reachable']}, "
        f"estopped={snap['estopped']}, joints={len(bus['voltages_v'])}."
    )
    return _result(summary, snap)


@mcp.tool(name="robot_doctor", title="Run robot_doctor", meta=INLINE_META)
def robot_doctor() -> types.CallToolResult:
    """Inspect live SO-ARM101 bus voltage, temperature, load, and hardware reachability."""
    snap = _snapshot()
    bus = snap["bus"]
    fault_domain = "healthy" if bus["reachable"] else "hardware_bus_unreachable"
    snap["fault_domain"] = fault_domain
    summary = (
        f"robot_doctor: fault_domain={fault_domain}, reachable={bus['reachable']}, "
        f"voltages={bus['voltages_v']}, temps_c={bus['temps_c']}"
    )
    return _result(summary, snap)


@mcp.tool(name="verify_workspace_bounds", title="Verify Workspace Bounds", meta=INLINE_META)
def verify_workspace_bounds(x_mm: float = 650.0, y_mm: float = 0.0, z_mm: float = 120.0) -> types.CallToolResult:
    """Dry-check a target coordinate (mm) against ROBOT.md workspace bounds without moving servos."""
    try:
        from so_arm101_actuator import kinematics as kin

        box = kin.workspace_box(str(MANIFEST_PATH))
        pt = (float(x_mm), float(y_mm), float(z_mm))
        if box is None:
            allowed, reason = False, "no_workspace_declared"
        else:
            clr = box.clearance(pt)
            allowed = clr >= 10.0
            reason = (
                f"in_workspace (clearance {clr:.1f} mm >= 10.0 mm margin)"
                if allowed
                else f"out_of_workspace: clearance {clr:.1f} mm from face {box.nearest_face(pt)} (< 10.0 mm margin)"
            )
    except Exception as exc:
        allowed, reason = False, f"check_error: {exc}"

    check = {
        "target_mm": [x_mm, y_mm, z_mm],
        "allowed": allowed,
        "outcome": "allowed" if allowed else "403_denied",
        "reason": reason,
        "ts": round(time.time(), 3),
    }
    check["sha256"] = hashlib.sha256(json.dumps(check, sort_keys=True).encode()).hexdigest()[:24]
    _STATE["last_check"] = check
    snap = _snapshot()
    return _result(f"Bounds check ({x_mm}, {y_mm}, {z_mm}) mm -> {check['outcome']}: {reason}", snap)


@mcp.tool(name="fleet_estop", title="Latch Fleet ESTOP")
def fleet_estop() -> types.CallToolResult:
    """Latch best-effort software e-stop in the console (not an ISO 13850 hardware e-stop)."""
    _STATE["estopped"] = True
    snap = _snapshot()
    return _result("Software fleet_estop LATCHED. Call clear_estop to recover.", snap)


@mcp.tool(name="clear_estop", title="Clear Fleet ESTOP")
def clear_estop() -> types.CallToolResult:
    """Clear the software e-stop latch (operator recovery)."""
    _STATE["estopped"] = False
    snap = _snapshot()
    return _result("Software fleet_estop CLEARED.", snap)


if __name__ == "__main__":
    mcp.run()
