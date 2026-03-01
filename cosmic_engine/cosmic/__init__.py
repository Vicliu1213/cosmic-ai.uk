# 宇宙交易引擎核心包

from .knowledge_base import KnowledgeBase
from .agent import Agent
from .trading import TradingEngine, Order, Position
from .consensus import ConsensusManager
from .data_interface import DataInterface
from .quantum_tasks import (
    quantum_manager, 
    run_grover, 
    run_shor, 
    run_annealing,
    run_vqe,
    run_qaoa
)
from .utils import setup_logging, get_logger, export_json_snapshot, load_json_snapshot

__version__ = "2.0.0"
__all__ = [
    'KnowledgeBase',
    'Agent',
    'TradingEngine',
    'Order',
    'Position',
    'ConsensusManager',
    'DataInterface',
    'quantum_manager',
    'run_grover',
    'run_shor',
    'run_annealing',
    'run_vqe',
    'run_qaoa',
    'setup_logging',
    'get_logger',
    'export_json_snapshot',
    'load_json_snapshot'
]
