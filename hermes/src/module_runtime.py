from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class ModuleState:
    name: str
    is_active: bool = False
    execution_count: int = 0
    error_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    last_input: Optional[Any] = None
    last_output: Optional[Any] = None


class ModuleRuntime:
    def __init__(self, name: str, components: List[str], capabilities: List[str], config: Optional[Dict[str, Any]] = None):
        self.state = ModuleState(name=name)
        self.components = components
        self.capabilities = capabilities
        self.config = config or {}

    def activate(self) -> Dict[str, Any]:
        self.state.is_active = True
        return self.status()

    def deactivate(self) -> Dict[str, Any]:
        self.state.is_active = False
        return self.status()

    def status(self) -> Dict[str, Any]:
        return {
            "name": self.state.name,
            "is_active": self.state.is_active,
            "execution_count": self.state.execution_count,
            "error_count": self.state.error_count,
            "created_at": self.state.created_at.isoformat(),
            "components": self.components,
            "capabilities": self.capabilities,
            "config_keys": list(self.config.keys()),
        }

    def manifest(self) -> Dict[str, Any]:
        return {
            "module": self.state.name,
            "components": self.components,
            "capabilities": self.capabilities,
            "state": self.status(),
        }

    def record_io(self, input_data: Any, output_data: Any) -> None:
        self.state.last_input = input_data
        self.state.last_output = output_data
        self.state.execution_count += 1

    def error(self, reason: str) -> Dict[str, Any]:
        self.state.error_count += 1
        return {"status": "error", "module": self.state.name, "error": reason, "state": self.status()}
