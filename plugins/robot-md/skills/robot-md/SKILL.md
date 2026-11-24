---
name: robot-md
description: Operate, diagnose, and verify bounded physical robots using ROBOT.md, robot-md-gateway, castor-hal (Serial, CAN/J1939, ROS 2), and OpenCastor. Use when inspecting live servo telemetry, running robot_doctor fault isolation, verifying workspace bounds, or opening the Robot-MD Console side pane.
---

# Robot-MD & OpenCastor Skill

Use the bundled `robot-md_console` MCP server tools whenever working with physical robots or `ROBOT.md` manifests:

- **`open_robot_console`**: Opens the interactive **Robot-MD Console** side pane (`aux_pane` / `global`) showing live SO-ARM101 Feetech STS3215 voltage/temp/load telemetry, `ROBOT.md` bounds, recent audit traveler steps, and a live `FLEET ESTOP` button.
- **`robot_doctor`**: Reads live bus telemetry from `/dev/ttyACM0` (or reports `hardware_reachable=False` if disconnected) to isolate software/config faults from physical bus/power/servo faults before any motion.
- **`verify_workspace_bounds(x_mm, y_mm, z_mm)`**: Dry-checks a coordinate against the declared `ROBOT.md` workspace box without moving servos and returns a SHA-256 receipt.
- **`fleet_estop` / `clear_estop`**: Latches or clears the software e-stop state.

## Core Engineering Rules
1. Always inspect `ROBOT.md` and run `robot_doctor` before commanding physical actuation.
2. Never claim `robot-md-gateway` or software `estop()` is a safety-rated ISO 13850 hardware e-stop. Software gates refuse commands at the boundary and emit signed receipts; hardware deadmans and physical e-stops cut power.
3. For new hardware integrations, implement `castor_hal.transport.Transport` (`open`, `close`, `set_goal`, `read_state`, `estop`) rather than bypassing `castor-hal`.
