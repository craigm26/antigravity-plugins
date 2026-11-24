# Robot-MD Guardrails

- Never market or describe `robot-md-gateway` or software `estop()` as a safety-rated emergency stop (ISO 13850). Frame it accurately as a deterministic, default-deny enforcement gateway and offline-verifiable audit layer.
- Always run `robot_doctor` or `status.report` to verify bus voltage and hardware reachability before commanding physical robot motion.
- Never bypass `ROBOT.md` declared workspace bounds or tier checks.
