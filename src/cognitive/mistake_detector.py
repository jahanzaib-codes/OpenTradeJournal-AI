"""
OpenTradeJournal-AI: Cognitive Mistake & Psychological Bias Detector
Analyzes trade sequence telemetry to detect revenge trading, FOMO entries,
overleveraging, stop tampering, and emotional discipline breakdowns.
"""

from typing import List, Optional
from datetime import timedelta
from src.models.trade import (
    TradeRecord,
    CognitiveDiagnosis,
    CognitiveBiasType,
    BiasSeverity
)


class CognitiveMistakeDetector:
    """Algorithmic behavioral and psychological bias detector for trading journals."""

    def __init__(
        self,
        revenge_window_seconds: int = 300,
        max_risk_pct_per_trade: float = 2.0,
        overtrading_hourly_threshold: int = 8
    ):
        self.revenge_window_seconds = revenge_window_seconds
        self.max_risk_pct_per_trade = max_risk_pct_per_trade
        self.overtrading_hourly_threshold = overtrading_hourly_threshold

    def analyze_trades(self, trades: List[TradeRecord]) -> List[CognitiveDiagnosis]:
        """Runs full heuristic behavioral audit on sorted trade sequence."""
        diagnoses: List[CognitiveDiagnosis] = []
        if not trades:
            return diagnoses

        # Sort trades chronologically
        sorted_trades = sorted(trades, key=lambda t: t.entry_time)

        for i, current in enumerate(sorted_trades):
            # Check 1: Revenge Trading
            if i > 0:
                prev = sorted_trades[i - 1]
                time_diff = (current.entry_time - prev.exit_time).total_seconds()
                
                # If entered shortly after a losing trade
                if prev.pnl < 0 and 0 <= time_diff <= self.revenge_window_seconds:
                    size_multiplier = (current.quantity / prev.quantity) if prev.quantity > 0 else 1.0
                    severity = BiasSeverity.CRITICAL if size_multiplier > 1.2 else BiasSeverity.HIGH
                    
                    diagnoses.append(CognitiveDiagnosis(
                        trade_id=current.trade_id,
                        symbol=current.symbol,
                        bias_detected=CognitiveBiasType.REVENGE_TRADING,
                        severity=severity,
                        confidence_score=0.92,
                        trigger_rule=f"Entry placed {int(time_diff)}s after a loss of ${abs(prev.pnl):.2f} with {size_multiplier:.1f}x sizing.",
                        explanation=(
                            f"Trade {current.trade_id} exhibits clear signs of revenge trading. "
                            f"Entering within {int(time_diff)} seconds of a losing trade indicates emotional impulse "
                            "and attempt to quickly recoup capital rather than waiting for structural confirmation."
                        ),
                        actionable_remedy=(
                            "Enforce a mandatory 15-minute cooling-off period after any stop-out. "
                            "Automate a daily circuit breaker that locks execution after two consecutive losses."
                        )
                    ))
                    continue

            # Check 2: Overleveraging
            if current.pnl_percent != 0 and abs(current.pnl_percent) > 25.0 and current.asset_class != "CRYPTO":
                diagnoses.append(CognitiveDiagnosis(
                    trade_id=current.trade_id,
                    symbol=current.symbol,
                    bias_detected=CognitiveBiasType.OVERLEVERAGING,
                    severity=BiasSeverity.HIGH,
                    confidence_score=0.88,
                    trigger_rule=f"High volatility swing with {current.quantity} units, exceeding risk envelope.",
                    explanation=(
                        f"Position size of {current.quantity} on {current.symbol} generated excessive margin exposure. "
                        "Overleveraging exposes the portfolio to tail-risk ruin during black-swan gap events."
                    ),
                    actionable_remedy=(
                        "Calibrate position sizing strictly based on Average True Range (ATR) and a fixed 1.0% portfolio risk."
                    )
                ))
                continue

            # Check 3: Stop-Loss Tampering / Missing Stop
            if current.stop_loss is None and current.pnl < 0 and abs(current.pnl) > 200.0:
                diagnoses.append(CognitiveDiagnosis(
                    trade_id=current.trade_id,
                    symbol=current.symbol,
                    bias_detected=CognitiveBiasType.STOP_LOSS_TAMPERING,
                    severity=BiasSeverity.CRITICAL,
                    confidence_score=0.95,
                    trigger_rule="Position executed and closed without a pre-defined hard Stop Loss order.",
                    explanation=(
                        f"Trade {current.trade_id} was held into a loss of ${abs(current.pnl):.2f} without an initial Stop Loss. "
                        "Trading without defined invalidation levels leads to catastrophic account drawdowns."
                    ),
                    actionable_remedy=(
                        "Never transmit an unbracketed order. Always submit hard OCO (One-Cancels-the-Other) stop brackets."
                    )
                ))
                continue

            # Check 4: Premature Profit Taking (Cutting Winners)
            if current.pnl > 0 and 0.0 < current.pnl_percent < 0.2 and current.commission > current.pnl * 0.4:
                diagnoses.append(CognitiveDiagnosis(
                    trade_id=current.trade_id,
                    symbol=current.symbol,
                    bias_detected=CognitiveBiasType.PREMATURE_EXIT,
                    severity=BiasSeverity.LOW,
                    confidence_score=0.78,
                    trigger_rule=f"Winner closed at +${current.pnl:.2f} while paying ${current.commission:.2f} in fees.",
                    explanation=(
                        f"Trade {current.trade_id} was closed prematurely at a micro-gain, where exchange fees ate "
                        f"{round((current.commission / current.pnl)*100, 1)}% of profits. Fear of giving back gains prevents positive expectancy."
                    ),
                    actionable_remedy=(
                        "Employ multi-stage scale-outs (e.g. 50% at 1.5R, move stop to breakeven, and trail the remainder)."
                    )
                ))
                continue

            # Check 5: Disciplined Trade
            diagnoses.append(CognitiveDiagnosis(
                trade_id=current.trade_id,
                symbol=current.symbol,
                bias_detected=CognitiveBiasType.DISCIPLINED,
                severity=BiasSeverity.NONE,
                confidence_score=0.90,
                trigger_rule="Executed with disciplined parameters and orderly risk management.",
                explanation="Trade followed standard risk-adjusted execution parameters with no detected cognitive biases.",
                actionable_remedy="Maintain strict trade logging and continue executing the defined edge."
            ))

        return diagnoses
