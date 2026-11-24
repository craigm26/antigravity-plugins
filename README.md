# Antigravity Plugin Marketplace (`craigm26/antigravity-plugins`)

Public plugin marketplace of **Antigravity** plugins (skills, rules, MCP servers, and interactive Side-Pane MCP Apps) built by [Craig Merry](https://craigmerry.com).

- **Browse the Marketplace Catalog:** https://craigm26.github.io/antigravity-plugins/
- **Machine-Readable Registry:** [`marketplace.json`](./marketplace.json) & [`.claude-plugin/marketplace.json`](./.claude-plugin/marketplace.json)

## One-Line Install

Install all plugins:
```bash
curl -fsSL https://raw.githubusercontent.com/craigm26/antigravity-plugins/main/install.sh | bash
```

Install a single plugin:
```bash
# Robot-MD & OpenCastor
curl -fsSL https://raw.githubusercontent.com/craigm26/antigravity-plugins/main/install.sh | bash -s -- --plugin robot-md

# GraftFork
curl -fsSL https://raw.githubusercontent.com/craigm26/antigravity-plugins/main/install.sh | bash -s -- --plugin graftfork
```

## Available Plugins

| Plugin | Category | Interactive MCP App | Highlights |
| :--- | :--- | :--- | :--- |
| **[`robot-md`](./plugins/robot-md)** | Robotics & Physical AI | **Robot-MD Console** (`aux_pane`, `global`) | Live SO-ARM101 Feetech STS3215 telemetry, `ROBOT.md` 403 bounds verification, `robot_doctor` fault isolation, latching `fleet_estop` |
| **[`graftfork`](./plugins/graftfork)** | Developer Tools | **GraftFork Inspector** (`aux_pane`, `global`) | Local git fork divergence inspector, `0 wrong moves` test-gate rules, quick links to `graftfork.com` & Claude Connector Directory |

## Requirements
- Python 3.10+ with `mcp` (`pip install mcp`)
- Optional for live SO-ARM101 hardware telemetry: `pip install castor-hal so-arm101-actuator`
