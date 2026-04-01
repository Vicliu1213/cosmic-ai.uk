"""
Base Engine Module - Unified engine interface and configuration
Provides foundational classes for all engine implementations
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol
from enum import Enum
import time
import logging

logger = logging.getLogger(__name__)


class EngineState(Enum):
    """Engine operational states"""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class EngineConfig:
    """Base configuration for all engines"""
    name: str
    version: str = "1.0.0"
    enabled: bool = True
    timeout_seconds: float = 30.0
    max_retries: int = 3
    retry_backoff: float = 2.0
    logging_level: str = "INFO"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'timeout_seconds': self.timeout_seconds,
            'max_retries': self.max_retries,
            'retry_backoff': self.retry_backoff,
            'logging_level': self.logging_level,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'EngineConfig':
        """Create config from dictionary"""
        return cls(
            name=config_dict.get('name', 'unknown'),
            version=config_dict.get('version', '1.0.0'),
            enabled=config_dict.get('enabled', True),
            timeout_seconds=config_dict.get('timeout_seconds', 30.0),
            max_retries=config_dict.get('max_retries', 3),
            retry_backoff=config_dict.get('retry_backoff', 2.0),
            logging_level=config_dict.get('logging_level', 'INFO'),
            metadata=config_dict.get('metadata', {})
        )


@dataclass
class EngineMetrics:
    """Engine performance metrics"""
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    average_latency_ms: float = 0.0
    peak_latency_ms: float = 0.0
    total_uptime_seconds: float = 0.0
    last_error: Optional[str] = None
    last_error_time: Optional[float] = None
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_operations == 0:
            return 0.0
        return self.successful_operations / self.total_operations


class BaseEngine(ABC):
    """
    Abstract base class for all engine implementations.
    Provides unified interface for initialization, execution, and monitoring.
    """
    
    def __init__(self, config: EngineConfig):
        """
        Initialize the engine with configuration
        
        Args:
            config: EngineConfig instance
        """
        self.config = config
        self.state = EngineState.UNINITIALIZED
        self.metrics = EngineMetrics()
        self._start_time: Optional[float] = None
        self._logger = logging.getLogger(f"{self.__class__.__name__}.{config.name}")
        self._logger.setLevel(config.logging_level)
    
    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the engine
        Must be implemented by subclasses
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def execute(self, *args, **kwargs) -> Any:
        """
        Execute the engine's primary operation
        Must be implemented by subclasses
        
        Returns:
            Any: Result of the operation
        """
        pass
    
    @abstractmethod
    async def shutdown(self) -> bool:
        """
        Shutdown the engine gracefully
        Must be implemented by subclasses
        
        Returns:
            bool: True if shutdown successful, False otherwise
        """
        pass
    
    async def start(self) -> bool:
        """
        Start the engine (public interface)
        
        Returns:
            bool: True if started successfully
        """
        if not self.config.enabled:
            self._logger.warning(f"Engine {self.config.name} is disabled")
            return False
        
        try:
            self.state = EngineState.INITIALIZING
            self._start_time = time.time()
            
            success = await self.initialize()
            
            if success:
                self.state = EngineState.READY
                self._logger.info(f"Engine {self.config.name} started successfully")
                return True
            else:
                self.state = EngineState.ERROR
                self._logger.error(f"Failed to initialize engine {self.config.name}")
                return False
                
        except Exception as e:
            self.state = EngineState.ERROR
            self.metrics.last_error = str(e)
            self.metrics.last_error_time = time.time()
            self._logger.error(f"Error starting engine: {e}", exc_info=True)
            return False
    
    async def stop(self) -> bool:
        """
        Stop the engine (public interface)
        
        Returns:
            bool: True if stopped successfully
        """
        try:
            self.state = EngineState.STOPPING
            success = await self.shutdown()
            
            if success:
                self.state = EngineState.STOPPED
                self._logger.info(f"Engine {self.config.name} stopped successfully")
                return True
            else:
                self.state = EngineState.ERROR
                self._logger.error(f"Failed to shutdown engine {self.config.name}")
                return False
                
        except Exception as e:
            self.state = EngineState.ERROR
            self._logger.error(f"Error stopping engine: {e}", exc_info=True)
            return False
    
    async def run(self, *args, **kwargs) -> Any:
        """
        Run the engine's primary operation
        
        Returns:
            Any: Result of the operation
        """
        if self.state not in [EngineState.READY, EngineState.RUNNING]:
            self._logger.error(f"Engine not ready. Current state: {self.state}")
            return None
        
        try:
            self.state = EngineState.RUNNING
            self.metrics.total_operations += 1
            
            start_time = time.time()
            result = await self.execute(*args, **kwargs)
            elapsed_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Update metrics
            self.metrics.successful_operations += 1
            self.metrics.average_latency_ms = (
                (self.metrics.average_latency_ms * (self.metrics.successful_operations - 1) + elapsed_time) /
                self.metrics.successful_operations
            )
            self.metrics.peak_latency_ms = max(self.metrics.peak_latency_ms, elapsed_time)
            
            self.state = EngineState.READY
            return result
            
        except Exception as e:
            self.metrics.failed_operations += 1
            self.metrics.last_error = str(e)
            self.metrics.last_error_time = time.time()
            self.state = EngineState.ERROR
            self._logger.error(f"Error during execution: {e}", exc_info=True)
            return None
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get engine status information
        
        Returns:
            Dict: Status information including state, metrics, and config
        """
        uptime = 0.0
        if self._start_time:
            uptime = time.time() - self._start_time
        
        return {
            'name': self.config.name,
            'version': self.config.version,
            'state': self.state.value,
            'enabled': self.config.enabled,
            'uptime_seconds': uptime,
            'metrics': {
                'total_operations': self.metrics.total_operations,
                'successful_operations': self.metrics.successful_operations,
                'failed_operations': self.metrics.failed_operations,
                'success_rate': self.metrics.success_rate,
                'average_latency_ms': self.metrics.average_latency_ms,
                'peak_latency_ms': self.metrics.peak_latency_ms,
                'last_error': self.metrics.last_error,
            }
        }
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.config.name}, state={self.state.value})"
