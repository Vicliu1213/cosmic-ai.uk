"""
Base Agent Module
==================

Provides abstract base class for all agents with standardized interface.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, TypeVar, Optional, List
from dataclasses import dataclass

# Type variables for generic input/output
InputT = TypeVar('InputT')
OutputT = TypeVar('OutputT')


@dataclass
class AgentResult:
    """Standard result wrapper for agent outputs"""
    success: bool
    data: Any
    error: Optional[str] = None
    agent_name: str = ""
    
    def __bool__(self) -> bool:
        return self.success


class BaseAgent(ABC, Generic[InputT, OutputT]):
    """
    Abstract base class for all agents.
    
    Provides standardized interface for:
    - Naming and identification
    - Execution with typed input/output
    - Optional agent marking
    - Input/output schema documentation
    
    Usage:
        class MyAgent(BaseAgent[MyInput, MyOutput]):
            @property
            def name(self) -> str:
                return "my_agent"
            
            async def execute(self, input_data: MyInput) -> MyOutput:
                # Implementation
                pass
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        Agent name for logging and configuration.
        Should be snake_case, e.g., 'predict_agent', 'regime_detector_agent'
        """
        pass
    
    @property
    def display_name(self) -> str:
        """Human-readable agent name for UI display"""
        # Convert snake_case to Title Case
        return ' '.join(word.capitalize() for word in self.name.split('_'))
    
    @property
    def is_optional(self) -> bool:
        """
        Whether this agent can be disabled.
        Override to return False for core agents.
        """
        return True
    
    @property
    def is_core(self) -> bool:
        """Inverse of is_optional for clarity"""
        return not self.is_optional
    
    @abstractmethod
    async def execute(self, input_data: InputT) -> OutputT:
        """
        Execute agent logic.
        
        Args:
            input_data: Typed input for the agent
            
        Returns:
            Typed output from the agent
        """
        pass
    
    def execute_sync(self, input_data: InputT) -> OutputT:
        """
        Synchronous wrapper for execute.
        Uses asyncio.run() for compatibility with sync code.
        """
        import asyncio
        try:
            loop = asyncio.get_running_loop()
            # If already in async context, create a task
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, self.execute(input_data))
                return future.result()
        except RuntimeError:
            # No running loop, safe to use asyncio.run
            return asyncio.run(self.execute(input_data))
    
    def get_input_schema(self) -> Dict[str, Any]:
        """
        Return expected input schema for documentation.
        Override in subclass to provide schema.
        """
        return {"description": "No schema defined"}
    
    def get_output_schema(self) -> Dict[str, Any]:
        """
        Return expected output schema for documentation.
        Override in subclass to provide schema.
        """
        return {"description": "No schema defined"}
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name}, optional={self.is_optional})>"


class AgentRegistry:
    """
    代理註冊表 - 管理和列出所有可用的交易代理
    Agent Registry - Manages and lists all available trading agents
    """
    
    def __init__(self):
        """初始化代理註冊表"""
        self._agents: Dict[str, Any] = {}
        self._register_default_agents()
    
    def _register_default_agents(self):
        """註冊默認的交易代理"""
        # 定義所有可用的代理類名
        available_agents = [
            'DataSyncAgent',
            'QuantAnalystAgent',
            'RiskAuditAgent',
            'PositionAnalyzerAgent',
            'TrendAgent',
            'RegimeDetectorAgent',
            'SymbolSelectorAgent',
            'PredictAgent',
            'TriggerDetectorAgent',
            'ReflectionAgent'
        ]
        
        # 為每個代理創建虛擬類
        for agent_name in available_agents:
            agent_class_name = agent_name
            snake_case_name = ''.join(['_' + c.lower() if c.isupper() else c 
                                      for c in agent_name]).lstrip('_')
            
            # 動態創建代理信息字典
            self._agents[agent_class_name] = {
                'name': snake_case_name,
                'display_name': agent_name.replace('Agent', '').strip(),
                'is_optional': True,
                'status': 'available'
            }
    
    def register_agent(self, agent_name: str, agent_info: Dict[str, Any]) -> bool:
        """
        註冊新的代理
        
        Args:
            agent_name: 代理名稱
            agent_info: 代理信息字典
            
        Returns:
            註冊是否成功
        """
        try:
            if agent_name in self._agents:
                return False
            
            self._agents[agent_name] = agent_info
            return True
        except Exception as e:
            print(f"❌ 代理註冊失敗: {str(e)}")
            return False
    
    def get_agent_info(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """
        獲取指定名稱的代理信息
        
        Args:
            agent_name: 代理名稱
            
        Returns:
            代理信息字典或 None
        """
        return self._agents.get(agent_name)
    
    def list_available_agents(self) -> Dict[str, Dict[str, Any]]:
        """
        列出所有可用的代理
        
        Returns:
            可用代理字典
        """
        agents_dict = {}
        for name, info in self._agents.items():
            if isinstance(info, dict):
                agents_dict[info.get('name', name.lower())] = info
            else:
                agents_dict[name.lower()] = {
                    'name': name.lower(),
                    'display_name': name,
                    'status': 'available'
                }
        return agents_dict
    
    def get_agent_names(self) -> List[str]:
        """
        獲取所有代理名稱列表
        
        Returns:
            代理名稱列表
        """
        result = []
        for name, info in self._agents.items():
            if isinstance(info, dict):
                result.append(info.get('name', name.lower()))
            else:
                result.append(name.lower())
        return result
    
    def is_agent_available(self, agent_name: str) -> bool:
        """
        檢查代理是否可用
        
        Args:
            agent_name: 代理名稱
            
        Returns:
            代理是否可用
        """
        return agent_name in self._agents or agent_name.lower() in self.get_agent_names()
