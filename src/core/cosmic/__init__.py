"""
異變全知宇宙智能體系統 - 核心類集合
Cosmic Core - UltraBrain Omniscient Universe Intelligence Core Classes

このモジュールは、異變全知宇宙智能體系統の最重要な核心類を集約しています。
This module aggregates the most critical core classes of the cosmic system.

主要構成:
1. Agents (智能體系統) - cosmic.agents
2. Quantum (量子系統) - cosmic.quantum
3. Fault Tolerance (容錯系統) - cosmic.fault_tolerance
4. Learning (自進化學習) - cosmic.learning
5. Utilities (工具和輔助) - cosmic.utilities
"""

__version__ = "1.0.0"
__name__ = "cosmic-core"

# 導入所有核心模塊
from . import agents
from . import quantum
from . import fault_tolerance
from . import learning
from . import utilities

# 直接導出主要類
from .agents import Agent
from .quantum import QiskitQuantumSimulator
from .fault_tolerance import FaultDetectionEngine, FaultIsolationManager, FailoverManager
from .learning import SelfEvolutionEngine
from .utilities import KnowledgeBase, EncodingProtection, DataInterface

# 元數據
METADATA = {
    "name": "異變全知宇宙智能體系統 - 核心層",
    "english_name": "Cosmic Core - UltraBrain Omniscient Universe Intelligence",
    "version": __version__,
    "modules": {
        "agents": "智能體系統 (Agent System)",
        "quantum": "量子系統 (Quantum Systems)",
        "fault_tolerance": "容錯系統 (Fault Tolerance)",
        "learning": "自進化學習 (Self-Evolution Learning)",
        "utilities": "工具和輔助 (Utilities & Helpers)"
    },
    "core_classes": [
        "Agent",
        "QiskitQuantumSimulator",
        "FaultDetectionEngine",
        "FaultIsolationManager",
        "FailoverManager",
        "SelfEvolutionEngine",
        "KnowledgeBase",
        "EncodingProtection",
        "DataInterface"
    ],
    "status": "✅ 已激活",
    "location": "src/core/cosmic/"
}

__all__ = [
    "agents",
    "quantum",
    "fault_tolerance",
    "learning",
    "utilities",
    "Agent",
    "QiskitQuantumSimulator",
    "FaultDetectionEngine",
    "FaultIsolationManager",
    "FailoverManager",
    "SelfEvolutionEngine",
    "KnowledgeBase",
    "EncodingProtection",
    "DataInterface",
    "METADATA"
]
