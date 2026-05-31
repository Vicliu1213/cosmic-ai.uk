#!/usr/bin/env python3
"""
演示：技能系統（Hermes cron） + 異能系統（CoreMatrix × GateBridge）
"""
import sys, os, json, time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "hermes", "src"))

def separator(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

# ════════════════════════════════════════════════════
# PART 1: 技能系統 — Hermes Cron Task
# ════════════════════════════════════════════════════
separator("PART 1: 技能系統 — Hermes 排程任務")

skills_dir = Path("skills/hermes")
docs_dir = Path("docs")
renamed = list(skills_dir.glob("bitget*.json")) + list(docs_dir.glob("bitget*.json"))
print(f"\n已重新命名的技能檔案 ({len(renamed)}):")
for f in renamed:
    data = json.loads(f.read_text())
    print(f"  📄 {f}")
    print(f"     技能名稱: {data['name']}")
    print(f"     執行腳本: {data['script']}")
    print(f"     排程:     {data['schedule']['display']}")
    print(f"     狀態:     {data['state']}")
    print(f"     提示詞:   {data['prompt'][:80]}...")

print(f"\n   ✅ 技能系統正常 — Hermes 會依排程自動執行")

# ════════════════════════════════════════════════════
# PART 2: 異能系統 — CoreMatrix × GateBridge
# ════════════════════════════════════════════════════
separator("PART 2: 異能系統 — CoreMatrix × GateBridge")

from src.synergy.gate_bridge import GateAbilityBridge
from src.layers.distributed.synergy import SynergyEngine

bridge = GateAbilityBridge(energy_capacity=1000.0)
synergy = SynergyEngine(gate_bridge=bridge)

print("\n啟動 SynergyEngine 記錄所有協同層級...")
synergy.record_all(consciousness=0.618)

status = bridge.get_full_status()
print(f"\n門檻激活: {status['unlocked_count']}/15")
print(f"最高 DRRK: {status.get('drrk_max', '—')}")

print(f"\n已解鎖異能:")
for a in status['abilities']:
    print(f"  🔓 {a['name']:12s}  |  {a['type']:10s}  |  能耗 {a['cost']:3d}  |  冷卻 {a['cooldown']}s  |  DRRK {a['drrk']}")

mx = status['matrix']
es = mx.get('energy_status', {})
print(f"\nCoreMatrix 狀態:")
print(f"  能量池:   {es.get('current',0):.0f}/{es.get('capacity',0):.0f} ({es.get('percentage',0):.1f}%)")
print(f"  健康度:   {mx.get('system_health','—')}")

# Attempt a test ability activation
separator("PART 3: 異能激活測試")

from 异能矩阵 import AbilityConfig, AbilityType

# 手動激活一個異能
test_ability = AbilityConfig(
    ability_id="demo_fireball",
    name="演示火球術",
    ability_type=AbilityType.OFFENSIVE,
    base_energy_cost=50.0,
    base_cooldown=5.0,
    synergy_tags=["fire", "demo"],
)

cm = bridge.ensure_core_matrix()
import asyncio
async def test_activate():
    result = await cm.activate_ability(test_ability, intensity=0.8)
    print(f"  異能: {test_ability.name}")
    print(f"  結果: {'✅ 成功' if result['success'] else '❌ 失敗'}")
    if result.get('energy_cost'):
        print(f"  能耗: {result['energy_cost']:.1f} 能量")
    if result.get('remaining_energy'):
        print(f"  剩餘: {result['remaining_energy']:.1f} 能量")
    return result

r = asyncio.run(test_activate())

# Summary
separator("SUMMARY")
print(f"""
  🔧 技能系統     ✅  {len(renamed)} 個技能已命名就緒
  ⚡ 異能系統     ✅  {status['unlocked_count']} 道門檻 → {len(status['abilities'])} 個異能解鎖
  🧠 CoreMatrix   ✅  能量池 {es.get('percentage',0):.0f}% · 健康 {mx.get('system_health','—')}
  🎯 激活測試     {'✅ 成功' if r.get('success') else '⚠️ 狀態: '+str(r.get('status','unknown'))}
""")
