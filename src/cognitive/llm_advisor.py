"""
OpenTradeJournal-AI: Cognitive Coaching & Executive Summary Advisor
Synthesizes algorithmic bias detections into an institutional psych audit report.
"""

from typing import List, Dict, Any
from src.models.trade import PerformanceSummary, CognitiveDiagnosis, CognitiveBiasType


class CognitiveCoachingAdvisor:
    """Generates structured trader psychology audit and debiasing recommendations."""

    @staticmethod
    def generate_executive_psych_report(
        metrics: PerformanceSummary,
        diagnoses: List[CognitiveDiagnosis]
    ) -> str:
        """Constructs an institutional Markdown psychological audit review."""
        bias_counts: Dict[str, int] = {}
        for d in diagnoses:
            b_name = d.bias_detected.value
            bias_counts[b_name] = bias_counts.get(b_name, 0) + 1

        disciplined_count = bias_counts.get(CognitiveBiasType.DISCIPLINED.value, 0)
        total = len(diagnoses) if len(diagnoses) > 0 else 1
        discipline_score = round((disciplined_count / total) * 100.0, 1)

        report = [
            "# 🧠 Quantitative Trader Psychology & Discipline Audit",
            "",
            f"**Discipline Score:** `{discipline_score}%`  ",
            f"**Total Executions Analyzed:** `{metrics.total_trades}`  ",
            f"**Realized Net PnL:** `${metrics.total_net_pnl:,.2f}`  ",
            f"**Profit Factor:** `{metrics.profit_factor}`  ",
            "",
            "---",
            "",
            "## 📊 Behavioral Bias Breakdown",
            "",
            "| Cognitive Pattern | Occurrences | Percentage | Risk Profile |",
            "| :--- | :---: | :---: | :--- |"
        ]

        for bias, count in sorted(bias_counts.items(), key=lambda x: x[1], reverse=True):
            pct = round((count / total) * 100.0, 1)
            risk = "CRITICAL" if bias in ["REVENGE_TRADING", "STOP_LOSS_TAMPERING"] else ("HIGH" if bias == "OVERLEVERAGING" else "OPTIMAL")
            report.append(f"| **{bias}** | `{count}` | `{pct}%` | `{risk}` |")

        report.extend([
            "",
            "---",
            "",
            "## 💡 Actionable Mental Model Coaching",
            ""
        ])

        if bias_counts.get(CognitiveBiasType.REVENGE_TRADING.value, 0) > 0:
            report.append(
                "> [!CAUTION] **Revenge Trading Detected:**\n"
                "> You entered positions immediately following losing trades with amplified sizing. "
                "This indicates tilt. **Mandatory Action:** Implement a hard cooldown timer of 15 minutes after any consecutive loss."
            )

        if bias_counts.get(CognitiveBiasType.STOP_LOSS_TAMPERING.value, 0) > 0:
            report.append(
                "> [!WARNING] **Uncontrolled Downside / Missing Invalidation:**\n"
                "> Multiple trades were executed without structural stop-loss orders. "
                "**Mandatory Action:** Configure broker bracket orders where entry is rejected unless an OCO stop loss is defined."
            )

        if discipline_score >= 80.0:
            report.append(
                "> [!TIP] **High Execution Discipline:**\n"
                "> Over 80% of trades followed structured sizing and orderly risk parameters. "
                "Focus on letting winning trades reach 2R-3R profit targets to expand your expectancy."
            )

        return "\n".join(report)
