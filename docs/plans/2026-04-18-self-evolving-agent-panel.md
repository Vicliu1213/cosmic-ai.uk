# Self-Evolving Agent Panel Implementation Plan

> **For Hermes:** Build a practical self-evolving agent control panel that combines profile/personality/workspace controls with finance-grade observability and verification.

**Goal:** Turn the dashboard into a useful agent operations center with custom profiles, personalities, workspaces, skills, live status, and self-improvement controls.

**Architecture:** Use a mixed layout: finance-style visual hierarchy for readability, and an agent-control core for power users. The panel should expose high-value actions first (switch profile, switch personality, pick model, open workspace, run verification), then surface telemetry and self-improvement signals on the right.

**Tech Stack:** HTML, CSS, minimal JS, existing Hermes dashboard pages, existing vendor/hermes-webui patterns, pytest.

---

### Task 1: Define the agent control model

**Objective:** Decide the canonical control objects the panel will expose.

**Files:**
- Modify: `hermes/dashboard/pages/control_center.html`
- Modify: `hermes/dashboard/pages/algorithms.html`
- Modify: `hermes/dashboard/index.html`

**Controls to expose:**
- Profile: `macro`, `quant`, `risk`, `ops`
- Personality: `oracle`, `architect`, `executor`, `sentinel`
- Workspace: active repo / project context
- Model: default and live override
- Verification: Hest status, test coverage, recent failures

---

### Task 2: Add a custom agent block to the dashboard

**Objective:** Make the dashboard show a dedicated agent customization area instead of hiding it in settings.

**Files:**
- Modify: `hermes/dashboard/index.html`
- Modify: `hermes/dashboard/styles.css`
- Test: `tests/test_agent_panel.py`

**UI blocks:**
- Profile switcher
- Personality switcher
- Workspace switcher
- Model picker
- Skills chip list
- Save/apply button

---

### Task 3: Add live self-evolution controls

**Objective:** Expose the tools that let the agent adapt itself safely.

**Files:**
- Modify: `hermes/dashboard/pages/control_center.html`
- Modify: `hermes/dashboard/app.js`
- Modify: `hermes/dashboard/styles.css`

**Controls:**
- Enable/disable self-improvement mode
- Choose optimization target: speed / accuracy / cost / stability
- Show recent regressions
- Show suggested next skill / profile / workspace
- Require verification before applying changes

---

### Task 4: Wire vendor-style profile/personality concepts into the local UI

**Objective:** Reuse the proven vendor patterns instead of inventing a new custom mechanism.

**Files:**
- Reference: `vendor/hermes-webui/static/commands.js`
- Reference: `vendor/hermes-webui/static/panels.js`
- Reference: `vendor/hermes-webui/static/index.html`
- Modify: local dashboard pages and app wiring

**Behavior:**
- Profile changes should update model/workspace defaults
- Personality changes should alter the agent behavior mode
- Workspace changes should preserve conversation safety

---

### Task 5: Verify the panel is useful, not just beautiful

**Objective:** Add tests that check the actual control affordances exist.

**Files:**
- Create: `tests/test_agent_panel.py`
- Create: `tests/test_self_evolution_controls.py`

**Assertions:**
- profile controls exist
- personality controls exist
- workspace controls exist
- Hest verification entry exists
- self-improvement controls exist
- finance-style telemetry blocks exist

---

### Task 6: Polish the design language

**Objective:** Merge the finance dashboard look with the higher-order agent control language.

**Files:**
- Modify: `hermes/dashboard/styles.css`

**Design rules:**
- Left = control/navigation
- Center = action/workbench
- Right = telemetry/verification
- Top = global state bar
- Use premium gradients, not excessive animation
- Keep it fast and readable on mobile

---

### Task 7: Final verification

**Objective:** Confirm the new panel is stable.

**Run:**
`pytest tests/test_dashboard_overview.py tests/test_control_center.py tests/test_dashboard_sidebar.py tests/test_agent_panel.py tests/test_self_evolution_controls.py -q`

**Expected:** all pass
