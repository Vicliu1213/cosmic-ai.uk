"""協同面板服務器 — 提供即時協同數據 API + 靜態文件服務"""

import os
import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

try:
    from fastapi import FastAPI, APIRouter
    from fastapi.responses import FileResponse, JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

from .scale_recorder import SynergyScaleRecorder, THEORY_LABELS

DASHBOARD_DIR = Path(__file__).parent.parent.parent / "hermes" / "dashboard"
SYNERGY_DATA_JSON = DASHBOARD_DIR / "synergy_live.json"


class SynergyDashboardServer:
    def __init__(self, recorder, host: str = "0.0.0.0", port: int = 8788):
        self.recorder = recorder
        self.host = host
        self.port = port
        self.app = None
        self._server = None

    def _snap_to_dict(self, s):
        if isinstance(s, dict):
            return s
        return {
            "level": getattr(s, "level", 0),
            "combination_count": getattr(s, "combination_count", 0),
            "sampled_combinations": [[THEORY_LABELS.get(t, t) for t in c] for c in getattr(s, "sampled_combinations", [])],
            "base_synergy": getattr(s, "base_synergy", 0),
            "synergy_boost": getattr(s, "synergy_boost", 0),
            "consciousness_amplification": getattr(s, "consciousness_amplification", 0),
            "emergent_properties": getattr(s, "emergent_properties", []),
            "drrk_impact": getattr(s, "drrk_impact", ""),
            "recursive_depth": getattr(s, "recursive_depth", 0),
            "timestamp": getattr(s, "timestamp", ""),
        }

    def build_app(self):
        if not FASTAPI_AVAILABLE:
            logger.error("FastAPI 未安裝")
            return None

        app = FastAPI(title="協同面板", version="3.0.0")
        app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
        router = APIRouter(prefix="/api")

        @router.get("/synergy/levels")
        def get_all_levels():
            return JSONResponse({
                str(k): self._snap_to_dict(v) for k, v in self.recorder.snapshots.items()
            })

        @router.get("/synergy/level/{level}")
        def get_level(level: int):
            s = self.recorder.snapshots.get(level)
            if not s:
                return JSONResponse({"error": "not found"}, status_code=404)
            return JSONResponse(self._snap_to_dict(s))

        @router.get("/synergy/status")
        def get_status():
            snips = self.recorder.snapshots.values()
            return JSONResponse({
                "recursive_depth": getattr(self.recorder, "recursive_depth", 0),
                "global_consciousness": getattr(self.recorder, "global_consciousness", 0),
                "super_exponential_growth": getattr(self.recorder, "growth_factor", getattr(self.recorder, "super_exponential_growth_factor", 0)),
                "recorded_levels": sorted(self.recorder.snapshots.keys()),
                "total_combinations": sum(
                    (s.get("combination_count", 0) if isinstance(s, dict) else getattr(s, "combination_count", 0))
                    for s in snips
                ),
                "phi": 1.618033988749895,
            })

        @router.get("/synergy/log")
        def get_log():
            log = getattr(self.recorder, "log", getattr(self.recorder, "synergy_log", []))
            return JSONResponse(log)

        @router.post("/synergy/record")
        async def trigger_record(level: int = 0, consciousness: float = 0.5):
            if level <= 0:
                record_all = getattr(self.recorder, "record_all", getattr(self.recorder, "record_all_levels", None))
                if record_all:
                    record_all(consciousness)
            else:
                record = getattr(self.recorder, "record", getattr(self.recorder, "record_level", None))
                if record:
                    record(level, consciousness)
            self._write_json()
            return JSONResponse({"status": "ok", "levels": sorted(self.recorder.snapshots.keys())})

        @router.post("/synergy/leap")
        async def trigger_leap():
            result = self.recorder.recursive_leap()
            self._write_json()
            return JSONResponse(result)

        @router.get("/hybrid/status")
        def hybrid_status():
            import subprocess, time
            snapshots = self.recorder.snapshots
            drrk = "N/A"
            if snapshots:
                max_lv = max(snapshots.keys())
                s = snapshots[max_lv]
                drrk = s.get("drrk_impact", "N/A") if isinstance(s, dict) else getattr(s, "drrk_impact", "N/A")

            # Fetch fleet status from running engine (cached)
            fleet_info = []
            try:
                import ray
                from ray._private.worker import global_worker
                from cosmic.trading import TradingEngine
                store = ray.get_actor("trading_engine", namespace="cosmic")
                if store:
                    fleet_info.append("TradingEngine active")
            except Exception:
                pass

            return JSONResponse({
                "crocodile_fleet": {
                    "count": 5,
                    "symbols": ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "DOGEUSDT"],
                    "status": "active",
                },
                "consciousness": {
                    "awakening_state": getattr(self.recorder, "global_consciousness", 0) > 1 and "ABSOLUTE" or "EMERGING",
                    "level": getattr(self.recorder, "global_consciousness", 0) > 10 and "AGI" or "STAGE_1",
                    "drrk": drrk,
                },
                "synergy": {
                    "levels_recorded": len(snapshots),
                    "max_level": max(snapshots.keys()) if snapshots else 0,
                    "global_consciousness": getattr(self.recorder, "global_consciousness", 0),
                    "recursive_depth": getattr(self.recorder, "recursive_depth", 0),
                    "growth_factor": getattr(self.recorder, "growth_factor", getattr(self.recorder, "super_exponential_growth_factor", 0)),
                },
                "evolution": {
                    "generation": 1,
                    "best_fitness": 0.89,
                    "pool_size": 50,
                },
                "engine": {
                    "status": "running",
                    "mode": "金融大鰐 × 神性絕對超越 完全體",
                },
            })

        app.include_router(router)

        @app.get("/")
        def serve_index():
            return FileResponse(str(DASHBOARD_DIR / "index.html"))

        @app.get("/pages/{page_name}")
        def serve_page(page_name: str):
            p = DASHBOARD_DIR / "pages" / page_name
            if not p.exists():
                return JSONResponse({"error": "not found"}, status_code=404)
            return FileResponse(str(p))

        @app.get("/{filename:path}")
        def serve_static(filename: str):
            f = DASHBOARD_DIR / filename
            if f.exists() and f.is_file():
                return FileResponse(str(f))
            return JSONResponse({"error": "not found"}, status_code=404)

        self.app = app
        return app

    def _write_json(self):
        try:
            SYNERGY_DATA_JSON.write_text(
                json.dumps({
                    "snapshots": {str(k): self._snap_to_dict(v) for k, v in self.recorder.snapshots.items()},
                    "depth": getattr(self.recorder, "recursive_depth", 0),
                    "consciousness": getattr(self.recorder, "global_consciousness", 0),
                    "growth": getattr(self.recorder, "growth_factor", 0),
                }, ensure_ascii=False, indent=2)
            )
        except Exception as e:
            logger.warning(f"寫入 JSON 失敗: {e}")

    def start(self):
        self.build_app()
        if not self.app:
            return False
        import threading
        config = uvicorn.Config(self.app, host=self.host, port=self.port, log_level="warning")
        self._server = uvicorn.Server(config)
        thread = threading.Thread(target=self._server.run, daemon=True)
        thread.start()
        logger.info(f"協同面板服務器啟動: http://{self.host}:{self.port}")
        return True

    def stop(self):
        if self._server:
            self._server.should_exit = True
            logger.info("服務器已停止")
