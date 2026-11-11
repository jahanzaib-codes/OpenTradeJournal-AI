"""
OpenTradeJournal-AI: Core Data Models
Provides strict Pydantic data schemas for multi-broker trade ingestion,
cognitive mistake classification, and quantitative portfolio metrics.
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class AssetClass(str, Enum):
    EQUITY = "EQUITY"
    FOREX = "FOREX"
    CRYPTO = "CRYPTO"
    FUTURES = "FUTURES"
    OPTIONS = "OPTIONS"


class TradeDirection(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"


class CognitiveBiasType(str, Enum):
    DISCIPLINED = "DISCIPLINED"
    FOMO = "FOMO"
    REVENGE_TRADING = "REVENGE_TRADING"
    OVERLEVERAGING = "OVERLEVERAGING"
    STOP_LOSS_TAMPERING = "STOP_LOSS_TAMPERING"
    PREMATURE_EXIT = "PREMATURE_EXIT"
    OVERTRADING = "OVERTRADING"


class BiasSeverity(str, Enum):
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TradeRecord(BaseModel):
    trade_id: str = Field(..., description="Unique trade execution identifier")
    broker: str = Field(..., description="Source broker (IBKR, MT5, BINANCE, BYBIT)")
    symbol: str = Field(..., description="Traded instrument ticker (e.g., AAPL, EURUSD, BTCUSDT)")
    asset_class: AssetClass = Field(default=AssetClass.EQUITY)
    direction: TradeDirection = Field(..., description="Trade direction (LONG or SHORT)")
    entry_time: datetime = Field(..., description="Timestamp of position entry")
    exit_time: datetime = Field(..., description="Timestamp of position exit")
    entry_price: float = Field(..., gt=0.0, description="Average entry execution price")
    exit_price: float = Field(..., gt=0.0, description="Average exit execution price")
    quantity: float = Field(..., gt=0.0, description="Executed trade quantity/lot size")
    pnl: float = Field(..., description="Realized net profit or loss in quote currency")
    pnl_percent: float = Field(default=0.0, description="Percentage return on invested capital")
    commission: float = Field(default=0.0, ge=0.0, description="Total broker commissions and exchange fees")
    stop_loss: Optional[float] = Field(default=None, description="Initial placed stop loss price")
    take_profit: Optional[float] = Field(default=None, description="Initial placed take profit target price")
    initial_risk_amount: Optional[float] = Field(default=None, description="Dollar risk assigned at entry")
    notes: Optional[str] = Field(default="", description="Trader discretionary commentary")


class CognitiveDiagnosis(BaseModel):
    trade_id: str
    symbol: str
    bias_detected: CognitiveBiasType
    severity: BiasSeverity
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    trigger_rule: str
    explanation: str
    actionable_remedy: str


class PerformanceSummary(BaseModel):
    total_trades: int
    winning_trades: int
    losing_trades: int
    breakeven_trades: int
    win_rate_pct: float
    profit_factor: float
    total_net_pnl: float
    gross_profit: float
    gross_loss: float
    average_trade_pnl: float
    average_win: float
    average_loss: float
    payoff_ratio: float
    max_drawdown: float
    max_drawdown_pct: float
    sharpe_ratio: float
    sortino_ratio: float
    expectancy_per_trade: float
    total_commissions: float
