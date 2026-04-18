# Finance Dashboard Visual Effects Plan

> **For Hermes:** Implement the financial-whale style dashboard visuals using TDD.

**Goal:** Upgrade the dashboard and control center with premium finance-style visual panels, chart effects, KPI ribbons, and liquidity/risk aesthetics.

**Architecture:** Use pure HTML/CSS with lightweight inline SVG/semantic blocks so the UI stays static, fast, and easy to verify. Add finance-themed sections to the main dashboard and control center, then keep the existing navigation intact.

**Tech Stack:** HTML, CSS, Python pytest, existing Hermes dashboard pages.

---

### Task 1: Add finance-style visual blocks to dashboard home

**Objective:** Add a market ribbon, KPI strip, sparkline cards, and liquidity heatmap language to `hermes/dashboard/index.html`.

**Files:**
- Modify: `hermes/dashboard/index.html`
- Test: `tests/test_dashboard_finance_visuals.py`

**Step 1: Write failing test**

```python
from pathlib import Path

def test_dashboard_finance_visuals_exist():
    text = Path('hermes/dashboard/index.html').read_text(encoding='utf-8')
    assert 'market-ribbon' in text
    assert 'kpi-grid' in text
    assert 'sparkline-chart' in text
    assert 'liquidity heatmap' in text
```

**Step 2: Run test to verify failure**

Run: `pytest tests/test_dashboard_finance_visuals.py -v`
Expected: FAIL — strings are missing from the dashboard HTML.

**Step 3: Write minimal implementation**

Add the following blocks to the dashboard:
- `market-ribbon`
- `kpi-grid`
- `sparkline-chart`
- `liquidity heatmap`

**Step 4: Run test to verify pass**

Run: `pytest tests/test_dashboard_finance_visuals.py -v`
Expected: PASS

### Task 2: Add premium finance visuals to control center

**Objective:** Add matching finance-style panels to `hermes/dashboard/pages/control_center.html`.

**Files:**
- Modify: `hermes/dashboard/pages/control_center.html`
- Test: `tests/test_control_center_finance_visuals.py`

**Step 1: Write failing test**

```python
from pathlib import Path


def test_control_center_finance_visuals_exist():
    text = Path('hermes/dashboard/pages/control_center.html').read_text(encoding='utf-8')
    assert 'performance ribbon' in text
    assert 'strategy pulse' in text
    assert 'risk contour' in text
```

**Step 2: Run test to verify failure**

Run: `pytest tests/test_control_center_finance_visuals.py -v`
Expected: FAIL — strings are missing from the control center HTML.

**Step 3: Write minimal implementation**

Add matching premium panels and labels to the control center page.

**Step 4: Run test to verify pass**

Run: `pytest tests/test_control_center_finance_visuals.py -v`
Expected: PASS

### Task 3: Polish styles for finance visuals

**Objective:** Add CSS for glassmorphism, animated gradients, KPI chips, and chart bars.

**Files:**
- Modify: `hermes/dashboard/styles.css`

**Step 1: Implement CSS classes**

Add styles for:
- `.market-ribbon`
- `.kpi-grid`
- `.sparkline-chart`
- `.liquidity-heatmap`
- `.performance-ribbon`
- `.strategy-pulse`
- `.risk-contour`

**Step 2: Verify visually and run all dashboard tests**

Run: `pytest tests/test_dashboard_overview.py tests/test_control_center.py tests/test_dashboard_sidebar.py tests/test_dashboard_finance_visuals.py tests/test_control_center_finance_visuals.py -q`
Expected: all pass

