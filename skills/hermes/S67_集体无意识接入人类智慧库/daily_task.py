#!/usr/bin/env python3
"""
每日異動報告 — S67 集体无意识接入人类智慧库
讀取 evolution.jsonl + skill.json 產生真實異動報表
cron: 0 0 * * * python .hermes/skills/S67_集体无意识接入人类智慧库/daily_task.py
"""
import json, math
from pathlib import Path
from datetime import datetime, timedelta, timezone

SKILL_ID   = "S67"
SKILL_NAME = "集体无意识接入人类智慧库"
CATEGORY   = "意识精神"
SYNERGY_IDS = ["S21", "S34"]

HERMES_ROOT = Path(".hermes")
SKILL_VAULT = HERMES_ROOT / "skill_vault"
EVOLUTION_LOG = HERMES_ROOT / "evolution.jsonl"
REPORT_DIR = Path(__file__).parent / "report"
REPORT_DIR.mkdir(exist_ok=True)

MUTATION_THRESHOLDS = {
    "BETA": 1.0, "GAMMA": 5.0, "DELTA": 20.0, "OMEGA": 100.0,
}


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


def load_skill_state() -> dict:
    sf = SKILL_VAULT / SKILL_ID / "skill.json"
    if sf.exists():
        return json.loads(sf.read_text(encoding="utf-8"))
    return {}


def load_hero_profile() -> dict:
    pf = HERMES_ROOT / "hero_profile.json"
    if pf.exists():
        return json.loads(pf.read_text(encoding="utf-8"))
    return {}


def build_report() -> str:
    logs = load_evolution_log()
    state = load_skill_state()
    hero = load_hero_profile()

    mastery = state.get("mastery_level", 0.0)
    stage = state.get("mutation_stage", "ALPHA")
    last_evolved = state.get("last_evolved", "N/A")

    my_mutations = []
    my_activations = 0
    for log in logs:
        for _sid, m in log.get("mutations", []):
            if _sid == SKILL_ID:
                my_mutations.append({"iteration": log["iteration"], "mutation": m})
        if SKILL_ID in str(log.get("evolved_skills", [])):
            my_activations += 1

    stages = ["ALPHA", "BETA", "GAMMA", "DELTA", "OMEGA"]
    current_idx = stages.index(stage) if stage in stages else 0
    next_stage = stages[current_idx + 1] if current_idx < len(stages) - 1 else None
    next_threshold = MUTATION_THRESHOLDS.get(next_stage) if next_stage else None
    stage_progress = (mastery / next_threshold * 100) if next_threshold else 100.0

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    report = []
    report.append(f"# {SKILL_ID} {SKILL_NAME} — 每日異動報告 {today}")
    report.append("")
    report.append(f"**類別**: {CATEGORY} | **當前異變**: {stage} | **掌握度**: {mastery:.4f}")
    report.append("")
    report.append("## 系統層級")
    report.append("")
    report.append("| 指標 | 值 |")
    report.append("|------|-----|")
    report.append(f"| 英雄 | {hero.get('callsign', 'N/A')} |")
    report.append(f"| 等級 | {hero.get('tier', 'N/A')} |")
    report.append(f"| 總迭代 | {hero.get('total_iterations', 0)} |")
    report.append(f"| 奇點 | {'✅' if hero.get('singularity_reached') else '⏳'} |")
    report.append("")
    report.append("## 技能狀態")
    report.append("")
    report.append("| 指標 | 值 |")
    report.append("|------|-----|")
    report.append(f"| 掌握度 | {mastery:.4f} |")
    report.append(f"| 異變階段 | {stage} |")
    report.append(f"| 進化次數 | {state.get('evolution_count', 0)} |")
    report.append(f"| 最後進化 | {last_evolved[:16] if last_evolved and last_evolved != 'N/A' else 'N/A'} |")
    report.append(f"| 本日激活 | {my_activations} 次 |")
    report.append(f"| 階段進度 | {stage_progress:.1f}% |")
    if next_threshold:
        report.append(f"| 下一異變 | {next_stage} (掌握度 {next_threshold}) |")
    else:
        report.append("| 下一異變 | Ω已達 — 全技能融合待命中 |")
    report.append("")
    report.append("## 異變記錄")
    report.append("")
    if my_mutations:
        report.append("| 迭代 | 異變 |")
        report.append("|------|------|")
        for m in my_mutations:
            report.append(f"| #{m['iteration']} | {m['mutation']} |")
    else:
        report.append("_無異變觸發_")
    report.append("")
    report.append("## 協同技能")
    report.append("")
    if SYNERGY_IDS:
        for syn in SYNERGY_IDS:
            syn_state = SKILL_VAULT / syn / "skill.json"
            if syn_state.exists():
                sd = json.loads(syn_state.read_text(encoding="utf-8"))
                report.append(f"- **{syn}** {sd.get('name_cn', '?')} (掌握度 {sd.get('mastery_level', 0):.2f}, {sd.get('mutation_stage', 'ALPHA')})")
            else:
                report.append(f"- **{syn}** (無資料)")
    else:
        report.append("_無協同技能_")
    report.append("")
    report.append("## 建議")
    report.append("")
    if next_threshold:
        remaining = next_threshold - mastery
        if remaining > 0:
            report.append(f"- 距離下一異變還需 **{remaining:.2f}** 掌握度")
        else:
            report.append("- 掌握度已達異變閾值，等待引擎觸發異變")
    else:
        report.append("- 已達 Ω 級，準備觸發 S96 終極融合")
    report.append("")
    report.append("---")
    report.append(f"*產生時間: {datetime.now(timezone.utc).isoformat()}*")
    report.append("")

    return "\n".join(report)


def main():
    report = build_report()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = REPORT_DIR / f"{{today}}.md"
    path.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
