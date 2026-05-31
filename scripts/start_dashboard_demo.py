#!/usr/bin/env python3
"""Standalone dashboard for demo - no Ray needed"""
import sys, os, json, time
from pathlib import Path

sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.join(os.getcwd(), 'hermes', 'src'))

from src.layers.distributed.synergy import SynergyEngine
from src.synergy.gate_bridge import GateAbilityBridge
from src.synergy.dashboard_server import SynergyDashboardServer

bridge = GateAbilityBridge(energy_capacity=1000.0)
synergy = SynergyEngine(gate_bridge=bridge)
synergy.record_all(consciousness=0.618)
synergy.recursive_leap()

dashboard = SynergyDashboardServer(synergy, port=8788)
dashboard.start()
time.sleep(2)

status = bridge.get_full_status()
Path("hermes/dashboard/synergy_gates.json").write_text(json.dumps(status, ensure_ascii=False))
print("DASHBOARD_READY", flush=True)

while True:
    time.sleep(10)
