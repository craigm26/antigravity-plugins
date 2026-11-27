---
description: End-to-end ROS 2 Pre-Flight Gate & ISO 10218:2025 / EU (2023/1230) Compliance Audit — ros2-bridge, 4-stage gate check, verified compliance-pack ZIP (0 private keys), opt-in Fleet Vault status/push, and Cloudflare-only CI/CD gate hook.
---

# ROS 2 Pre-Flight & Compliance Audit Playbook (`/ros2-compliance-audit`)

Guide the robotics team through a complete, offline-verifiable **ROS 2 pre-flight & compliance audit** for their ROS 2 / MoveIt 2 / industrial robot cell — **Zero GitHub Actions (Cloudflare-only CI/CD)**.

> **Mandatory ISO 13850 & ISO 13849-1 Hardware Safety Boundary:** `robot-gate`, `graft-core`, `graft-watchdog`, `bounded-embodiment`, and `robot-md-gateway` are strictly deterministic **software** pre-flight gates and RFC 8785 / SHA-256 audit layers claiming **ZERO** Performance Level (PL) or Safety Integrity Level (SIL) credit. Certified hardwired ISO 13850 red mushroom E-stops, ISO 13849-1:2023 safety relays/door interlocks, and an application-specific ANSI/A3 R15.06-2025 & ISO 12100 risk assessment remain mandatory.
>
> **ITAR / EAR Export-Control Boundary (`22 CFR Parts 120–130` & `15 CFR Parts 730–774`):** Keep `GRAFT_VAULT_API_KEY` unset (100% zero phone-home) and use local Apple Silicon MLX or Gemma 4 / Ollama for any ITAR/EAR or air-gapped workcell.

---

## Step 1 — Generate Drop-In ROS 2 Pre-Flight Boundary Bundle (`ros2-bridge`)

1. Call `graft_ros2_generate_bundle(workspace_dir=".", output_dir="./ros2_bundle", stack="moveit2", embodiment="ur5e", frame_id="base_link")` (or run CLI `robot-gate ros2-bridge --dir . --generate-bundle ./ros2_bundle --stack moveit2 --embodiment ur5e --frame-id base_link`).
2. Inspect the generated `graft_ros2_params.yaml`, `graft_ros2_gate.launch.py`, and `README_ROS2.md`:
   - Confirm `require_hard_latch: true`, `L0_OBSERVE: 0.0` (0% shadow start), workspace bounds, and keep-out exclusion boxes mirror signed `ROBOT.md`.
   - Confirm topic remappings for MoveIt 2, UR RTDE, Fairino FR5, or xArm6.

## Step 2 — Run 4-Stage Deterministic Pre-Flight Check (`check`)

1. Run `robot-gate check --dir . --sim-only` (or `robot_run_gate_check(sim_only=True)` via `robot-gate mcp`).
2. Verify all 4 stages pass and emit a fresh Ed25519-signed `.robot-gate/gate_receipt.json` matching the live workspace SHA-256 fingerprint.
3. Verify the offline SHA-256 audit chain (`robot-gate verify-audit --dir .`).

## Step 3 — Generate & Offline-Verify Compliance Dossier ZIP (`compliance-pack --verify`)

1. Call `graft_generate_compliance_pack(workspace_dir=".", zip_filename="graft-compliance-pack.zip")` (or run CLI `robot-gate compliance-pack --dir . --out ./graft-compliance-pack.zip && robot-gate compliance-pack --verify ./graft-compliance-pack.zip`, or click **Download Compliance Pack ZIP** in the Graft Workbench hitting `GET http://127.0.0.1:8785/v1/compliance-pack`).
2. Confirm:
   - Offline verification passes (`valid: true`, canonical RFC 8785 `manifest_sha256` matches).
   - **0 private keys / 0 `.pem` files** included in `graft-compliance-pack.zip`.
   - Clause coverage for **ISO 10218-1:2025 Clause 5.1.16**, **ISO 10218-2:2025 Clause 5.2.16**, and **EU Machinery Regulation (EU) 2023/1230** (effective Jan 20, 2027) is recorded clearly alongside the ISO 13850 hardware boundary attestation.

## Step 4 — Opt-In Hosted Fleet Vault Sync (`vault status` / `vault push`)

1. Call `graft_vault_status(limit=20)` (or check the **Vault Drift Status** badge in the Graft Workbench hitting `GET http://127.0.0.1:8785/v1/vault/status`).
2. If `GRAFT_VAULT_API_KEY` is **unset**, confirm the offline zero-phone-home status (`offline: true`, zero network calls).
3. Only for non-ITAR/EAR teams who explicitly opt in to 5-year active Cloudflare D1 Fleet Vault retention (+ 10-year offline-verifiable compliance archive export for EU 2023/1230 Annex IV):
   ```bash
   export GRAFT_VAULT_API_KEY="<your-vault-key>"
   robot-gate vault push --dir .
   ```
   Review any voltage, thermal, or TCP drift alerts returned by the vault.

## Step 5 — Cloudflare-Only CI/CD Gate Hook (Zero GitHub Actions)

Wire the deterministic compliance & test gate directly into your Cloudflare Pages/Workers build pipeline (zero GitHub Actions required):
```bash
bash ./robot-gate/ci/cloudflare-build.sh
```
Confirm every change to `ROBOT.md`, `skills/`, or `policies/` re-runs `robot-gate check --sim-only` and `robot-gate compliance-pack --verify` before release.
