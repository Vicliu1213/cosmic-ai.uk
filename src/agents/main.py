"""
代理模組 - 主入點

負責初始化和協調所有交易代理，包括：
- 數據同步代理 (DataSyncAgent)
- 定量分析代理 (QuantAnalystAgent)  
- 風險審計代理 (RiskAuditAgent)
- 技術分析代理 (TechnicianAgent)
- 市場情報代理 (MarketIntelligenceAgent)
"""

import sys
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class AgentStatus:
    """代理狀態數據類"""
    name: str
    status: str  # 'running', 'idle', 'error'
    last_update: str
    metrics: Dict[str, Any] = field(default_factory=dict)


class AgentsModuleManager:
    """代理模組管理器 - 協調所有交易代理"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化代理模組管理器
        
        Args:
            config: 模組配置字典
        """
        self.config = config or {}
        self.agents = {}
        self.agent_status = {}
        self.is_initialized = False
        logger.info("✅ 代理模組管理器初始化完成")
    
    def initialize_agents(self) -> Dict[str, bool]:
        """
        初始化所有可用的交易代理
        
        Returns:
            各代理初始化狀態字典
        """
        try:
            from .base_agent import BaseAgent, AgentRegistry
            
            # 使用 AgentRegistry 註冊所有代理
            registry = AgentRegistry()
            self.agents = registry.list_available_agents()
            
            self.is_initialized = True
            logger.info(f"✅ 已初始化 {len(self.agents)} 個交易代理")
            
            # 初始化每個代理的狀態
            for agent_name in self.agents:
                self.agent_status[agent_name] = AgentStatus(
                    name=agent_name,
                    status='idle',
                    last_update='',
                    metrics={}
                )
            
            return {name: True for name in self.agents}
            
        except Exception as e:
            logger.error(f"❌ 代理初始化失敗: {str(e)}")
            return {}
    
    def get_agent(self, name: str):
        """
        獲取指定的交易代理
        
        Args:
            name: 代理名稱
            
        Returns:
            代理實例
        """
        if name not in self.agents:
            raise ValueError(f"未知的代理: {name}")
        return self.agents[name]
    
    def list_available_agents(self) -> List[str]:
        """列出所有可用的交易代理"""
        return list(self.agents.keys())
    
    def start_agent(self, agent_name: str) -> bool:
        """
        啟動指定代理
        
        Args:
            agent_name: 代理名稱
            
        Returns:
            啟動是否成功
        """
        try:
            if agent_name not in self.agent_status:
                logger.error(f"❌ 代理不存在: {agent_name}")
                return False
            
            self.agent_status[agent_name].status = 'running'
            logger.info(f"✅ 代理已啟動: {agent_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 啟動代理失敗 ({agent_name}): {str(e)}")
            self.agent_status[agent_name].status = 'error'
            return False
    
    def stop_agent(self, agent_name: str) -> bool:
        """
        停止指定代理
        
        Args:
            agent_name: 代理名稱
            
        Returns:
            停止是否成功
        """
        try:
            if agent_name not in self.agent_status:
                logger.error(f"❌ 代理不存在: {agent_name}")
                return False
            
            self.agent_status[agent_name].status = 'idle'
            logger.info(f"✅ 代理已停止: {agent_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 停止代理失敗 ({agent_name}): {str(e)}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """獲取模組狀態"""
        return {
            'initialized': self.is_initialized,
            'agents_count': len(self.agents),
            'available_agents': self.list_available_agents(),
            'agent_statuses': {
                name: {
                    'status': status.status,
                    'last_update': status.last_update
                }
                for name, status in self.agent_status.items()
            }
        }


async def main(config: Optional[Dict[str, Any]] = None):
    """
    代理模組主入點
    
    Args:
        config: 模組配置
    """
    manager = AgentsModuleManager(config)
    status = manager.initialize_agents()
    
    print("\n" + "="*60)
    print("🤖 代理模組 (Agents Module)")
    print("="*60)
    print(f"初始化狀態: {status}")
    print(f"可用代理: {manager.list_available_agents()}")
    print("="*60 + "\n")
    
    return manager


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
