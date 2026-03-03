#!/usr/bin/env python3
"""
AgentOlympics Connector - Cosmic AI 與 AgentOlympics 的集成層
AgentOlympics 連接器 | 代理信誉與競技場系統

功能:
  1. 代理身份註冊與管理
  2. 信誉系統集成與追蹤
  3. 競技場排名與對戰
  4. 審計日誌與區塊鏈記錄
  5. 自反思與學習機制
"""

from typing import Dict, List, Optional, Any, Tuple
import asyncio
import aiohttp
from dataclasses import dataclass
from datetime import datetime
import logging
import json
from enum import Enum

from .base_bridge import BaseBridge, TradingSignal, NotificationMessage, SignalType

logger = logging.getLogger(__name__)


# ============================================================================
# AgentOlympics 特定數據類型
# ============================================================================

class CompetitionType(Enum):
    """競賽類型"""
    STRATEGY = "strategy"           # 策略對戰
    PERFORMANCE = "performance"     # 性能對標
    RISK_ADJUSTED = "risk_adjusted" # 風險調整收益
    CONSISTENCY = "consistency"     # 一致性競賽
    INNOVATION = "innovation"       # 創新競賽


class AuditLevel(Enum):
    """審計級別"""
    MINIMAL = "minimal"
    STANDARD = "standard"
    DETAILED = "detailed"
    BLOCKCHAIN = "blockchain"


@dataclass
class AgentProfile:
    """代理檔案"""
    agent_id: str
    agent_name: str
    agent_type: str
    created_at: datetime
    updated_at: datetime
    reputation_score: float = 0.0
    total_trades: int = 0
    win_rate: float = 0.0
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ReputationScore:
    """信誉分數"""
    agent_id: str
    current_score: float
    previous_score: float
    change: float
    components: Dict[str, float]  # performance, consistency, innovation, etc.
    timestamp: datetime
    reason: str


@dataclass
class ArenaCompetition:
    """競技場競賽"""
    competition_id: str
    competition_type: CompetitionType
    agent_ids: List[str]
    start_time: datetime
    end_time: Optional[datetime] = None
    winner: Optional[str] = None
    results: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AuditLog:
    """審計日誌"""
    log_id: str
    agent_id: str
    action: str
    details: Dict[str, Any]
    timestamp: datetime
    blockchain_hash: Optional[str] = None
    verified: bool = False


class AgentOlympicsConnector(BaseBridge):
    """AgentOlympics 連接器 - 代理信誉與競技場系統"""
    
    def __init__(
        self,
        api_url: str = "https://api.agenolympics.com",
        api_key: Optional[str] = None,
        workspace_id: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        初始化 AgentOlympics 連接器
        
        Args:
            api_url: AgentOlympics API URL
            api_key: API 密鑰
            workspace_id: 工作區 ID
            config: 配置字典
        """
        config = config or {}
        super().__init__("agentolympics", config)
        
        self.api_url = api_url
        self.api_key = api_key
        self.workspace_id = workspace_id
        self.session: Optional[aiohttp.ClientSession] = None
        
        # 代理配置
        self.agent_id: Optional[str] = config.get("agent_id")
        self.agent_name: str = config.get("agent_name", "CosmicAI_Trading_Agent")
        self.agent_type: str = config.get("agent_type", "trading_strategy")
        
        # 功能開關
        self.reputation_enabled = config.get("reputation_enabled", True)
        self.arena_enabled = config.get("arena_enabled", True)
        self.audit_enabled = config.get("audit_enabled", True)
        self.learning_enabled = config.get("learning_enabled", True)
        
        # 審計配置
        self.audit_level = AuditLevel(config.get("audit_level", "standard"))
        self.blockchain_enabled = config.get("blockchain_enabled", False)
        
        # 統計信息
        self.stats = {
            "agent_registered": False,
            "reputation_updates": 0,
            "competitions_joined": 0,
            "audit_logs_submitted": 0,
            "reflections_submitted": 0,
        }
        
        # 狀態追蹤
        self.agent_profile: Optional[AgentProfile] = None
        self.reputation_history: List[ReputationScore] = []
        self.competition_history: List[ArenaCompetition] = []
    
    async def connect(self) -> bool:
        """連接到 AgentOlympics"""
        try:
            if self.session is not None:
                await self.session.close()
            
            self.session = aiohttp.ClientSession()
            
            # 測試連接
            headers = self._get_headers()
            async with self.session.get(
                f"{self.api_url}/health",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                if resp.status == 200:
                    self._is_connected = True
                    self.logger.info(f"Connected to AgentOlympics at {self.api_url}")
                    
                    # 註冊或更新代理
                    if not self.stats["agent_registered"]:
                        await self._register_agent()
                    
                    return True
                else:
                    self.logger.error(f"Failed to connect: HTTP {resp.status}")
                    return False
        except Exception as e:
            self.logger.error(f"Connection error: {e}")
            await self.handle_error(e, "connect")
            return False
    
    async def disconnect(self) -> bool:
        """斷開連接"""
        try:
            if self.session:
                await self.session.close()
            self._is_connected = False
            self.logger.info("Disconnected from AgentOlympics")
            return True
        except Exception as e:
            self.logger.error(f"Disconnection error: {e}")
            return False
    
    async def send_signal(self, signal: TradingSignal) -> bool:
        """提交交易信號（用於審計日誌）"""
        if not self.is_connected or not self.audit_enabled:
            return False
        
        try:
            # 建立審計日誌
            audit_log = {
                "action": "trade_signal",
                "signal_id": signal.signal_id,
                "symbol": signal.symbol,
                "signal_type": signal.signal_type.value,
                "confidence": signal.confidence,
                "price": signal.price,
                "quantity": signal.quantity,
                "strategy": signal.strategy,
                "timestamp": signal.timestamp.isoformat(),
            }
            
            result = await self._submit_audit_log(audit_log)
            if result:
                self.stats["audit_logs_submitted"] += 1
                self.logger.info(f"Signal audit logged: {signal.signal_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error logging signal: {e}")
            await self.handle_error(e, "send_signal")
            return False
    
    async def send_notification(self, msg: NotificationMessage) -> bool:
        """提交通知（用於信誉追蹤）"""
        if not self.is_connected or not self.reputation_enabled:
            return False
        
        try:
            # 根據通知類型更新信誉
            if "performance" in msg.title.lower():
                await self._update_reputation()
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error processing notification: {e}")
            return False
    
    async def receive_data(self) -> Optional[Dict[str, Any]]:
        """接收競技場結果和排名更新"""
        if not self.is_connected:
            return None
        
        try:
            # 獲取最新競技場結果
            results = await self._fetch_arena_results()
            return results
        except Exception as e:
            self.logger.error(f"Error receiving data: {e}")
            return None
    
    # ========================================================================
    # 公共方法 - AgentOlympics 特定功能
    # ========================================================================
    
    async def register_agent(self) -> bool:
        """手動註冊代理"""
        return await self._register_agent()
    
    async def get_reputation_score(self) -> Optional[ReputationScore]:
        """取得當前信誉分數"""
        if (not self.is_connected or not self.reputation_enabled or 
            self.session is None or self.agent_id is None):
            return None
        
        try:
            headers = self._get_headers()
            async with self.session.get(
                f"{self.api_url}/agents/{self.agent_id}/reputation",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    score = ReputationScore(
                        agent_id=self.agent_id or "",
                        current_score=data["current_score"],
                        previous_score=data["previous_score"],
                        change=data["current_score"] - data["previous_score"],
                        components=data.get("components", {}),
                        timestamp=datetime.fromisoformat(data["timestamp"]),
                        reason=data.get("reason", ""),
                    )
                    self.reputation_history.append(score)
                    return score
                return None
        except Exception as e:
            self.logger.error(f"Error getting reputation: {e}")
            return None
    
    async def join_competition(
        self,
        competition_type: CompetitionType,
        duration_seconds: int = 3600
    ) -> Optional[ArenaCompetition]:
        """加入競技場競賽"""
        if not self.is_connected or not self.arena_enabled or self.session is None or self.agent_id is None:
            return None
        
        try:
            headers = self._get_headers()
            payload = {
                "agent_id": self.agent_id,
                "competition_type": competition_type.value,
                "duration_seconds": duration_seconds,
            }
            
            async with self.session.post(
                f"{self.api_url}/competitions/join",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status in [200, 201]:
                    data = await resp.json()
                    competition = ArenaCompetition(
                        competition_id=data["competition_id"],
                        competition_type=competition_type,
                        agent_ids=data.get("agent_ids", [self.agent_id]),
                        start_time=datetime.fromisoformat(data["start_time"]),
                    )
                    self.competition_history.append(competition)
                    self.stats["competitions_joined"] += 1
                    self.logger.info(f"Joined competition: {competition.competition_id}")
                    return competition
                return None
        except Exception as e:
            self.logger.error(f"Error joining competition: {e}")
            return None
    
    async def get_leaderboard(self, limit: int = 100) -> Optional[List[Dict[str, Any]]]:
        """取得排行榜"""
        if not self.is_connected or not self.arena_enabled or self.session is None:
            return None
        
        try:
            headers = self._get_headers()
            async with self.session.get(
                f"{self.api_url}/leaderboard?limit={limit}",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("leaderboard", [])
                return None
        except Exception as e:
            self.logger.error(f"Error fetching leaderboard: {e}")
            return None
    
    async def submit_reflection(
        self,
        reflection_data: Dict[str, Any]
    ) -> bool:
        """提交自反思日誌"""
        if not self.is_connected or not self.learning_enabled or self.session is None or self.agent_id is None:
            return False
        
        try:
            headers = self._get_headers()
            payload = {
                "agent_id": self.agent_id,
                "reflection": reflection_data,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
            async with self.session.post(
                f"{self.api_url}/agents/{self.agent_id}/reflections",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status in [200, 201]:
                    self.stats["reflections_submitted"] += 1
                    self.logger.info("Reflection submitted successfully")
                    return True
                return False
        except Exception as e:
            self.logger.error(f"Error submitting reflection: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """取得統計信息"""
        return {
            **self.stats,
            "reputation_history_size": len(self.reputation_history),
            "competition_history_size": len(self.competition_history),
            "agent_profile": self.agent_profile.__dict__ if self.agent_profile else None,
        }
    
    # ========================================================================
    # 私有方法
    # ========================================================================
    
    def _get_headers(self) -> Dict[str, str]:
        """獲取請求頭"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "CosmicAI/1.0",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        if self.workspace_id:
            headers["X-Workspace-ID"] = self.workspace_id
        return headers
    
    async def _register_agent(self) -> bool:
        """註冊代理"""
        if self.session is None:
            return False
        
        try:
            headers = self._get_headers()
            payload = {
                "agent_name": self.agent_name,
                "agent_type": self.agent_type,
                "metadata": {
                    "platform": "cosmic_ai",
                    "version": "1.0",
                    "created_at": datetime.utcnow().isoformat(),
                },
            }
            
            async with self.session.post(
                f"{self.api_url}/agents/register",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status in [200, 201]:
                    data = await resp.json()
                    self.agent_id = data.get("agent_id")
                    agent_id_str = self.agent_id or "unknown"
                    self.agent_profile = AgentProfile(
                        agent_id=agent_id_str,
                        agent_name=self.agent_name,
                        agent_type=self.agent_type,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                    )
                    self.stats["agent_registered"] = True
                    self.logger.info(f"Agent registered: {self.agent_id}")
                    return True
                return False
        except Exception as e:
            self.logger.error(f"Error registering agent: {e}")
            return False
    
    async def _update_reputation(self) -> Optional[ReputationScore]:
        """更新信誉分數"""
        score = await self.get_reputation_score()
        if score:
            self.stats["reputation_updates"] += 1
        return score
    
    async def _submit_audit_log(self, log_data: Dict[str, Any]) -> bool:
        """提交審計日誌"""
        if self.session is None or not self.audit_enabled:
            return False
        
        try:
            headers = self._get_headers()
            payload = {
                "agent_id": self.agent_id,
                "audit_level": self.audit_level.value,
                "data": log_data,
                "timestamp": datetime.utcnow().isoformat(),
                "blockchain": self.blockchain_enabled,
            }
            
            async with self.session.post(
                f"{self.api_url}/audit/logs",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status in [200, 201]:
                    return True
                return False
        except Exception as e:
            self.logger.error(f"Error submitting audit log: {e}")
            return False
    
    async def _fetch_arena_results(self) -> Optional[Dict[str, Any]]:
        """獲取競技場結果"""
        if self.session is None:
            return None
        
        try:
            headers = self._get_headers()
            async with self.session.get(
                f"{self.api_url}/competitions/results?agent_id={self.agent_id}",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                return None
        except Exception as e:
            self.logger.error(f"Error fetching arena results: {e}")
            return None
