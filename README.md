# Antigravity Plugins (`robot-md` & `graftfork`)

Open-source **Antigravity** plugins (skills, rules, MCP servers, and interactive Side-Pane MCP Apps) built by [Craig Merry](https://craigmerry.com).

## Included Plugins

### 1. `robot-md` — Robot-MD & OpenCastor
Bounded physical-AI robotics plugin with a live **Robot-MD Console** side pane (`aux_pane` + `global` MCP App):
- Live Feetech STS3215 servo telemetry (voltage, temperature, torque load) on SO-ARM101 (`/dev/ttyACM0`)
- One-click `ROBOT.md` pre-execution workspace bounds verification (`403 DENY` + SHA-256 receipt) without moving servos
- `robot_doctor` hardware-vs-software fault isolation and latching software `fleet_estop`
- Bundled `robot-md` skill + safety-honest guardrails (`rules/AGENTS.md`)

### 2. `graftfork` — GraftFork Carry Inspector
Test-gated upstream OSS fork carry plugin with an interactive **GraftFork Inspector** side pane (`aux_pane` + `global` MCP App):
- Inspects any local git fork (branch, latest tag, commits ahead of tag, recent carry stack)
- Enforces GraftFork's `0 wrong moves` test-gate rules (`rules/AGENTS.md`)
- Direct links to [graftfork.com](https://graftfork.com), [graftfork.com/results](https://graftfork.com/results), and the [Claude Connector Directory](https://claude.ai/directory/graftfork)

## Quick Install

```bash
git clone https://github.com/craigm26/antigravity-plugins.git
cd antigravity-plugins
./install.sh
```

Antigravity automatically discovers plugins in `~/.gemini/config/plugins/` without a restart. Open **Robot-MD Console** or **GraftFork Inspector** from the side pane **`+`** menu or left sidebar.

### Requirements
- Python 3.10+ with `mcp` installed (`pip install mcp`)
- Optional for live SO-ARM101 bus telemetry: `pip install castor-hal so-arm101-actuator`
