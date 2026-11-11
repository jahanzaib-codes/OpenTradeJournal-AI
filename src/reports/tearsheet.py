"""
OpenTradeJournal-AI: Performance Tearsheet Generator
Outputs institutional ASCII tearsheets and performance summaries.
"""

from typing import List
from tabulate import tabulate
from src.models.trade import PerformanceSummary, TradeRecord


class TearsheetGenerator:
    """Generates ASCII and markdown performance tearsheets."""

    @staticmethod
    def generate_ascii_tearsheet(summary: PerformanceSummary) -> str:
        """Renders institutional CLI tearsheet."""
        overview_table = [
            ["Total Executed Trades", f"{summary.total_trades}"],
            ["Winning Trades", f"{summary.winning_trades} ({summary.win_rate_pct}%)"],
            ["Losing Trades", f"{summary.losing_trades}"],
            ["Total Net PnL", f"${summary.total_net_pnl:,.2f}"],
            ["Profit Factor", f"{summary.profit_factor:.2f}"],
            ["Payoff Ratio (Avg Win / Loss)", f"{summary.payoff_ratio:.2f}"],
            ["Average Win", f"${summary.average_win:,.2f}"],
            ["Average Loss", f"${summary.average_loss:,.2f}"],
            ["Expectancy per Trade", f"${summary.expectancy_per_trade:,.2f}"],
            ["Maximum Peak Drawdown", f"${summary.max_drawdown:,.2f} ({summary.max_drawdown_pct:.1f}%)"],
            ["Annualized Sharpe Ratio", f"{summary.sharpe_ratio:.2f}"],
            ["Sortino Ratio (Downside)", f"{summary.sortino_ratio:.2f}"],
            ["Brokerage Commissions", f"${summary.total_commissions:,.2f}"]
        ]

        header = """
================================================================================
           🏛️ OPENTRADEJOURNAL-AI: QUANTITATIVE PERFORMANCE TEARSHEET           
================================================================================
"""
        table_rendered = tabulate(overview_table, headers=["Performance Metric", "Quantitative Value"], tablefmt="fancy_grid")
        footer = "\n" + "="*80 + "\n"
        return header + table_rendered + footer
