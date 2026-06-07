#!/usr/bin/env python3
"""
每日異動報告 — 讀取 evolution.jsonl + skill.json 產生 HTML/Markdown 報表
用法:  python scripts/hermes_daily_report.py [--days 1] [--format md]
"""
import json, sys, os
from pathlib import Path
from datetime import datetime, timedelta, timezone
from collections import defaultdict

HERMES_ROOT = Path(".hermes")
SKILL_VAULT = HERMES_ROOT / "skill_vault"
EVOLUTION_LOG = HERMES_ROOT / "evolution.jsonl"
HERO_PROFILE = HERMES_ROOT / "hero_profile.json"
REPORT_DIR = HERMES_ROOT / "reports"
REPORT_DIR.mkdir(exist_ok=True)


def load_evolution_log(hours: int = 24) -> list:
    if not EVOLUTION_LOG.exists():
        return []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    records = []
    for line in EVOLUTION_LOG.read_text(encoding="utf-8").strip().splitlines():
        if not line:
            continue
        try:
            rec = json.loads(line)
            ts = datetime.fromisoformat(rec.get("timestamp", ""))
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            if ts >= cutoff:
                records.append(rec)
        except Exception:
            continue
    return records


def load_all_skill_states() -> dict:
    states = {}
    if not SKILL_VAULT.exists():
        return states
    for skill_dir in sorted(SKILL_VAULT.iterdir()):
        sf = skill_dir / "skill.json"
        if sf.exists():
            states[skill_dir.name] = json.loads(sf.read_text(encoding="utf-8"))
    return states


def load_hero_profile() -> dict:
    if HERO_PROFILE.exists():
        return json.loads(HERO_PROFILE.read_text(encoding="utf-8"))
    return {}


def compute_changes(logs: list, skill_states: dict) -> dict:
    changes = {
        "total_iterations": len(logs),
        "tier_changes": [],
        "mutations": [],
        "skills_evolved": defaultdict(int),
        "omega_skills": 0,
        "singularity_reached": False,
    }

    for log in logs:
        if log.get("tier_change"):
            changes["tier_changes"].append({
                "iteration": log["iteration"],
                "change": log["tier_change"],
            })
        for sid, mutation in log.get("mutations", []):
            changes["mutations"].append({
                "iteration": log["iteration"],
                "skill_id": sid,
                "mutation": mutation,
            })
            changes["skills_evolved"][sid] += 1

    for sid, state in skill_states.items():
        if state.get("mutation_stage") == "OMEGA":
            changes["omega_skills"] += 1

    hero = load_hero_profile()
    changes["singularity_reached"] = hero.get("singularity_reached", False)
    changes["hero_tier"] = hero.get("tier", "STREET")
    changes["hero_callsign"] = hero.get("callsign", "UNKNOWN")
    changes["total_iterations_all"] = hero.get("total_iterations", 0)

    return changes


def generate_markdown_report(changes: dict, skill_states: dict) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = []
    lines.append(f"# 赫爾墨斯每日異動報告 — {now}")
    lines.append("")
    lines.append(f"**英雄**: {changes['hero_callsign']} | "
                 f"**等級**: {changes['hero_tier']} | "
                 f"**總迭代**: {changes['total_iterations_all']}")
    lines.append("")

    # Summary
    lines.append("## 摘要")
    lines.append("")
    lines.append(f"| 指標 | 值 |")
    lines.append(f"|------|-----|")
    lines.append(f"| 本日迭代次數 | {changes['total_iterations']} |")
    lines.append(f"| Ω級技能 | {changes['omega_skills']}/96 |")
    lines.append(f"| 奇點狀態 | {'✅ 已達成' if changes['singularity_reached'] else '⏳ 進行中'} |")
    lines.append(f"| 等級變更 | {len(changes['tier_changes'])} 次 |")
    lines.append(f"| 異變觸發 | {len(changes['mutations'])} 次 |")
    lines.append(f"| 活躍技能 | {len(changes['skills_evolved'])} 項 |")
    lines.append("")

    # Tier changes
    if changes["tier_changes"]:
        lines.append("## 等級變更")
        lines.append("")
        for tc in changes["tier_changes"]:
            lines.append(f"- 迭代 #{tc['iteration']}: **{tc['change']}**")
        lines.append("")

    # Mutations
    if changes["mutations"]:
        lines.append("## 異變記錄")
        lines.append("")
        lines.append("| 迭代 | 技能 | 異變階段 |")
        lines.append("|------|------|----------|")
        for m in changes["mutations"][-20:]:  # last 20
            sid = m["skill_id"]
            name = skill_states.get(sid, {}).get("name_cn", sid)
            lines.append(f"| #{m['iteration']} | {name} ({sid}) | {m['mutation']} |")
        lines.append("")

    # Top evolved
    if changes["skills_evolved"]:
        top = sorted(changes["skills_evolved"].items(), key=lambda x: -x[1])[:10]
        lines.append("## 最高活躍技能 (Top 10)")
        lines.append("")
        lines.append("| 技能 | 激活次數 | 當前掌握度 | 異變階段 |")
        lines.append("|------|----------|------------|----------|")
        for sid, count in top:
            st = skill_states.get(sid, {})
            name = st.get("name_cn", sid)
            mastery = st.get("mastery_level", 0)
            stage = st.get("mutation_stage", "ALPHA")
            lines.append(f"| {name} ({sid}) | {count} | {mastery:.2f} | {stage} |")
        lines.append("")

    # All skills summary
    lines.append("## 全部技能狀態")
    lines.append("")
    lines.append("| 編號 | 名稱 | 掌握度 | 異變 | 最後進化 |")
    lines.append("|------|------|--------|------|----------|")
    for sid in sorted(skill_states.keys()):
        st = skill_states[sid]
        last = st.get("last_evolved", "")
        if last:
            try:
                last = datetime.fromisoformat(last).strftime("%m-%d %H:%M")
            except Exception:
                last = last[:16]
        lines.append(f"| {sid} | {st.get('name_cn', '?')} | "
                     f"{st.get('mastery_level', 0):.2f} | "
                     f"{st.get('mutation_stage', 'ALPHA')} | {last or '-'} |")

    return "\n".join(lines)


def generate_html_report(changes: dict, skill_states: dict) -> str:
    md = generate_markdown_report(changes, skill_states)
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>赫爾墨斯每日異動報告</title>
<style>
body {{ font-family: sans-serif; max-width: 960px; margin: auto; padding: 20px; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ccc; padding: 6px 10px; text-align: left; }}
th {{ background: #f0f0f0; }}
h1 {{ color: #333; }}
h2 {{ color: #555; border-bottom: 2px solid #ddd; padding-bottom: 4px; }}
</style></head><body>
<pre>{md}</pre>
</body></html>"""
    return html


def main():
    days = 1
    fmt = "md"
    for i, arg in enumerate(sys.argv[1:]):
        if arg == "--days" and i + 2 < len(sys.argv):
            days = int(sys.argv[i + 2])
        elif arg == "--format" and i + 2 < len(sys.argv):
            fmt = sys.argv[i + 2]

    logs = load_evolution_log(hours=days * 24)
    skill_states = load_all_skill_states()
    changes = compute_changes(logs, skill_states)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if fmt == "html":
        report = generate_html_report(changes, skill_states)
        path = REPORT_DIR / f"{today}.html"
    else:
        report = generate_markdown_report(changes, skill_states)
        path = REPORT_DIR / f"{today}.md"

    path.write_text(report, encoding="utf-8")
    print(report)
    print(f"\n--- 報告已寫入: {path} ---")


if __name__ == "__main__":
    main()
