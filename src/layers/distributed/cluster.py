"""Ray 分布式集群管理 — 自動初始化、資源調度、健康檢查"""

import os
import sys
import ray
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)

HERMES_SRC = os.path.join(os.path.dirname(__file__), "..", "..", "..", "hermes", "src")


class DistributedCluster:
    def __init__(self, namespace: str = "cosmic", object_store_mb: int = 60):
        self.namespace = namespace
        self.object_store_mb = object_store_mb
        self.initialized = False
        self.resources = {}

    def init(self, runtime_env: Optional[dict] = None) -> bool:
        if ray.is_initialized():
            logger.info("Ray already initialized")
            self.initialized = True
            return True

        env = runtime_env or {
            "env_vars": {"PYTHONPATH": HERMES_SRC},
        }
        try:
            ray.init(
                namespace=self.namespace,
                ignore_reinit_error=True,
                object_store_memory=self.object_store_mb * 1024 * 1024,
                runtime_env=env,
            )
            self.initialized = True
            self._collect_resources()
            logger.info(f"Ray cluster ready: {self.resources}")
            return True
        except Exception as e:
            logger.error(f"Ray init failed: {e}")
            return False

    def _collect_resources(self):
        cluster = ray.cluster_resources()
        self.resources = {
            "cpus": int(cluster.get("CPU", 0)),
            "gpus": int(cluster.get("GPU", 0)),
            "memory": cluster.get("memory", 0),
            "object_store": cluster.get("object_store_memory", 0),
        }

    def resolve_resources(self, default_cpus: int = 1, default_gpus: int = 0) -> tuple:
        cluster = ray.cluster_resources()
        cpus = min(default_cpus, max(1, int(cluster.get("CPU", 1))))
        gpus = default_gpus if cluster.get("GPU", 0) >= default_gpus else 0
        return cpus, gpus

    def get_status(self) -> dict:
        if not self.initialized:
            return {"status": "uninitialized"}
        try:
            self._collect_resources()
            return {
                "status": "running",
                "namespace": self.namespace,
                **self.resources,
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def shutdown(self):
        if ray.is_initialized():
            ray.shutdown()
            self.initialized = False
            logger.info("Ray cluster shut down")
