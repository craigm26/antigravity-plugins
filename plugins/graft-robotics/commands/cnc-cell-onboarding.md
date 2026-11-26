---
description: Onboard a new CNC tending cell in ~20 minutes using a verified Job Skill Pack and 3 datums.
---

Run the `cnc-cell-onboarding` playbook:
1. Call `graft_list_skill_packs(job="cnc")` and review `cnc-tending-haas-vf2`.
2. Call `graft_install_skill_pack(pack_id="interactive")` to trigger the native MCP Elicitation setup form (starting safely in `L0_OBSERVE` zero-motion shadow mode).
3. Run `graft_check_part_mechanics(actor="ur5e", part_id="finished_bracket", grip_force_n=35.0, coolant_wet=True)` to show wet-coolant slip compensation.
4. Walk the operator through teaching the 3 cell datums (`handoff_nest`, `haas_door_clearance`, `kurt_vise_jaw`).
