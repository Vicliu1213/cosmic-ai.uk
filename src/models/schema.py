from pydantic import BaseModel, Field
from typing import Literal, Optional

class TradeSignal(BaseModel):
    symbol: str
    action: Literal["ENTRY", "HOLD", "CLOSE", "WAIT"]
    side: Literal["LONG", "SHORT"]
    price_entry: float
    price_tp: float
    price_sl: float
    leverage: int = Field(ge=1, le=50)
    risk_usd: float
    confidence: float = Field(ge=0, le=1) # 0 to 1
    justification: str # AI 必須給出理由，用於存入 RAG 記憶庫
n
