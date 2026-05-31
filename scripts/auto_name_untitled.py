#!/usr/bin/env python3
"""
自動偵測 Untitled-N.json 技能檔案 → 取合適名稱 → 儲存正確路徑 → 驗證

掃描 docs/ 與 skills/hermes/，根據 content.name 或 content.script 自動重新命名。
支援 dry-run 模式。可排程 cron 定期執行。
"""
import json, os, re, sys, glob, logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
log = logging.getLogger('auto_name')

# 掃描範圍 — 專案目錄 + 全局 Hermes 技能目錄
HERMES_GLOBAL = Path.home() / ".hermes" / "skills"
SCAN_DIRS = [
    Path(__file__).parent.parent / "docs",
    Path(__file__).parent.parent / "skills" / "hermes",
    HERMES_GLOBAL,
]

# 保留原有 `name` 欄位作為檔名基底，若無則用 script 檔名
def propose_name(data: dict) -> str:
    raw = data.get("name") or data.get("script", "")
    raw = raw.replace(".py", "").replace(".json", "")
    # kebab → snake
    name = re.sub(r'[- ]', '_', raw).strip('_').lower()
    if not name:
        name = f"unnamed_skill"
    return name + ".json"


def validate_json(path: Path) -> bool:
    try:
        with open(path) as f:
            data = json.load(f)
        required = ["name", "prompt"]
        missing = [k for k in required if k not in data]
        if missing:
            log.warning(f"  ⚠ 缺少欄位: {missing}")
        return True
    except json.JSONDecodeError as e:
        log.error(f"  ❌ JSON 解析失敗: {e}")
        return False


def process_one(path: Path, dry_run: bool = False) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"path": str(path), "status": "error", "detail": str(e)}

    new_name = propose_name(data)
    target = path.with_name(new_name)

    if target == path:
        return {"path": str(path), "status": "skip", "detail": "名稱已是正確格式"}

    if target.exists():
        # 同名衝突 → 加時間戳
        ts = datetime.now().strftime("%H%M%S")
        stem = target.stem
        target = target.with_name(f"{stem}_{ts}.json")

    if dry_run:
        log.info(f"  [dry-run] {path.name} → {target.name}")
        return {"path": str(path), "new_name": target.name, "status": "dry-run"}

    # 執行重新命名
    path.rename(target)
    ok = validate_json(target)
    skill_name = data.get("name", "?")
    script = data.get("script", "")

    # 同步至全局 Hermes skills 目錄
    global_target = HERMES_GLOBAL / target.name
    if HERMES_GLOBAL.is_dir():
        if not global_target.exists():
            # 用 symlink 指向實際檔案
            try:
                global_target.symlink_to(target.resolve())
                log.info(f"  🔗 全局共用: ~/.hermes/skills/{target.name}")
            except Exception:
                # fallback: 複製
                import shutil
                shutil.copy2(target, global_target)
                log.info(f"  📋 全局共用 (copy): ~/.hermes/skills/{target.name}")
        else:
            log.info(f"  ⏭ 全局已存在: ~/.hermes/skills/{target.name}")

    log.info(f"  ✅ {path.name} → {target.name}  |  技能: {skill_name}  |  腳本: {script}")
    return {
        "path": str(path),
        "new_name": target.name,
        "new_path": str(target),
        "skill": skill_name,
        "script": script,
        "status": "renamed",
        "valid": ok,
    }


def scan_and_process(dry_run: bool = False) -> list[dict]:
    results = []
    for base_dir in SCAN_DIRS:
        if not base_dir.is_dir():
            continue
        for fpath in sorted(base_dir.glob("Untitled-*.json")):
            log.info(f"發現: {fpath}")
            r = process_one(fpath, dry_run=dry_run)
            results.append(r)
    return results


def print_summary(results: list[dict]):
    renamed = [r for r in results if r["status"] == "renamed"]
    skipped = [r for r in results if r["status"] == "skip"]
    errors = [r for r in results if r.get("status", "").startswith("error")]
    dry = [r for r in results if r["status"] == "dry-run"]

    total = len(results)
    print(f"\n{'='*55}")
    print(f"  📦 總計: {total}   ✅ 已重新命名: {len(renamed)}  ⏭ 跳過: {len(skipped)}  ❌ 錯誤: {len(errors)}")
    if dry:
        print(f"  🌀 dry-run 預覽: {len(dry)} 個（未實際執行）")
    if renamed:
        print(f"\n  已重新命名:")
        for r in renamed:
            print(f"    {Path(r['path']).name}  →  {r['new_name']}  [{r['skill']}]")
    if errors:
        print(f"\n  錯誤:")
        for r in errors:
            print(f"    {r['path']}: {r.get('detail','')}")
    print(f"{'='*55}")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv
    watch = "--watch" in sys.argv or "-w" in sys.argv

    if dry_run:
        log.info("🌀 dry-run 模式 — 只預覽不執行\n")
    else:
        log.info("🔍 開始掃描 Untitled 技能檔案...\n")

    results = scan_and_process(dry_run=dry_run)
    print_summary(results)

    if watch:
        import time
        log.info("👀 watch 模式啟動 (每 30 秒掃描一次, Ctrl+C 結束)")
        seen = {r["path"] for r in results}
        try:
            while True:
                time.sleep(30)
                new_results = scan_and_process(dry_run=False)
                for r in new_results:
                    if r["path"] not in seen:
                        print_summary([r])
                        seen.add(r["path"])
        except KeyboardInterrupt:
            log.info("watch 模式結束")
