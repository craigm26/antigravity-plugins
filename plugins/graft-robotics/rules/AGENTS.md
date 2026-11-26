# Graft Robotics Safety & Trust Rules

- Never market or describe `robot-gate`, `robot-md-gateway`, or software `estop()` as a safety-rated ISO 13850 hardware emergency stop. Always frame them accurately as a deterministic, default-deny software pre-flight boundary gate and offline-verifiable RFC 8785 / SHA-256 audit layer paired with hardwired ISO 13850 shop E-stops.
- Always check live multi-sensor world-model freshness (local RGB-D + any networked LAN LiDAR meshes) and known material/payload/slip limits before commanding physical motion.
- Never bypass signed `ROBOT.md` bounds, Envelope 0.2 keep-out zones, or the progressive `L0 OBSERVE -> L3 AUTONOMOUS` Trust Ladder.
- Start new robots and environments small (L1 atomic single-object picks at 30% speed with human approval) and graduate to autonomous frozen YAML skills only after clean sensor-verified runs.
