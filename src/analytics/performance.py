"""
OpenTradeJournal-AI: Quantitative Performance Engine
Computes institutional risk-adjusted return metrics, drawdowns, and distribution statistics.
"""

from typing import List, Dict, Any
import numpy as np
import pandas as pd
from src.models.trade import TradeRecord, PerformanceSummary


class PerformanceEngine:
    """Calculates portfolio and strategy performance analytics from trade records."""

    @staticmethod
    def calculate_summary(trades: List[TradeRecord]) -> PerformanceSummary:
        """Computes comprehensive quantitative performance tear sheet metrics."""
        if not trades:
            return PerformanceSummary(
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                breakeven_trades=0,
                win_rate_pct=0.0,
                profit_factor=0.0,
                total_net_pnl=0.0,
                gross_profit=0.0,
                gross_loss=0.0,
                average_trade_pnl=0.0,
                average_win=0.0,
                average_loss=0.0,
                payoff_ratio=0.0,
                max_drawdown=0.0,
                max_drawdown_pct=0.0,
                sharpe_ratio=0.0,
                sortino_ratio=0.0,
                expectancy_per_trade=0.0,
                total_commissions=0.0
            )

        pnls = [t.pnl for t in trades]
        commissions = [t.commission for t in trades]

        wins = [p for p in pnls if p > 0.0]
        losses = [p for p in pnls if p < 0.0]
        bes = [p for p in pnls if p == 0.0]

        total_trades = len(trades)
        winning_trades = len(wins)
        losing_trades = len(losses)
        breakeven_trades = len(bes)

        win_rate = (winning_trades / total_trades * 100.0) if total_trades > 0 else 0.0

        gross_profit = sum(wins)
        gross_loss = abs(sum(losses))
        net_pnl = sum(pnls)

        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else (999.0 if gross_profit > 0 else 0.0)
        avg_trade = net_pnl / total_trades if total_trades > 0 else 0.0
        avg_win = (gross_profit / winning_trades) if winning_trades > 0 else 0.0
        avg_loss = (gross_loss / losing_trades) if losing_trades > 0 else 0.0
        payoff_ratio = (avg_win / avg_loss) if avg_loss > 0 else (avg_win if avg_win > 0 else 0.0)

        # Drawdown computation
        equity_curve = np.cumsum(pnls)
        peaks = np.maximum.accumulate(equity_curve)
        drawdowns = peaks - equity_curve
        max_drawdown = float(np.max(drawdowns)) if len(drawdowns) > 0 else 0.0
        max_peak = float(np.max(peaks)) if len(peaks) > 0 else 1.0
        max_drawdown_pct = (max_drawdown / max_peak * 100.0) if max_peak > 0 else 0.0

        # Sharpe & Sortino (Annualized based on trade frequency approximation)
        pnl_array = np.array(pnls)
        std_dev = float(np.std(pnl_array)) if len(pnl_array) > 1 else 0.0
        sharpe = (float(np.mean(pnl_array)) / std_dev * np.sqrt(252)) if std_dev > 0 else 0.0

        downside = pnl_array[pnl_array < 0]
        downside_std = float(np.std(downside)) if len(downside) > 1 else (std_dev if std_dev > 0 else 1.0)
        sortino = (float(np.mean(pnl_array)) / downside_std * np.sqrt(252)) if downside_std > 0 else 0.0

        # Expectancy = (Win% * AvgWin) - (Loss% * AvgLoss)
        win_prob = winning_trades / total_trades
        loss_prob = losing_trades / total_trades
        expectancy = (win_prob * avg_win) - (loss_prob * avg_loss)

        return PerformanceSummary(
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            breakeven_trades=breakeven_trades,
            win_rate_pct=round(win_rate, 2),
            profit_factor=round(profit_factor, 2),
            total_net_pnl=round(net_pnl, 2),
            gross_profit=round(gross_profit, 2),
            gross_loss=round(gross_loss, 2),
            average_trade_pnl=round(avg_trade, 2),
            average_win=round(avg_win, 2),
            average_loss=round(avg_loss, 2),
            payoff_ratio=round(payoff_ratio, 2),
            max_drawdown=round(max_drawdown, 2),
            max_drawdown_pct=round(max_drawdown_pct, 2),
            sharpe_ratio=round(sharpe, 2),
            sortino_ratio=round(sortino, 2),
            expectancy_per_trade=round(expectancy, 2),
            total_commissions=round(sum(commissions), 2)
        )
