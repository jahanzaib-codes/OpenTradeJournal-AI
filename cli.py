"""
OpenTradeJournal-AI: Interactive Command Line Interface (CLI)
Enables standalone terminal trade analysis, psychology auditing, and tearsheet generation.
"""

import sys
import argparse
from datetime import datetime, timedelta
from src.models.trade import TradeRecord, AssetClass, TradeDirection
from src.parsers.ibkr_parser import IBKRParser
from src.parsers.mt5_parser import MT5Parser
from src.parsers.crypto_parser import CryptoParser
from src.analytics.performance import PerformanceEngine
from src.cognitive.mistake_detector import CognitiveMistakeDetector
from src.cognitive.llm_advisor import CognitiveCoachingAdvisor
from src.reports.tearsheet import TearsheetGenerator


def get_demo_trades():
    base_time = datetime.now() - timedelta(days=7)
    return [
        TradeRecord(
            trade_id="DEMO-101", broker="IBKR", symbol="SPY", asset_class=AssetClass.OPTIONS,
            direction=TradeDirection.LONG, entry_time=base_time, exit_time=base_time + timedelta(minutes=40),
            entry_price=4.50, exit_price=6.10, quantity=10.0, pnl=1600.0, pnl_percent=35.5, commission=12.0
        ),
        TradeRecord(
            trade_id="DEMO-102", broker="IBKR", symbol="TSLA", asset_class=AssetClass.EQUITY,
            direction=TradeDirection.SHORT, entry_time=base_time + timedelta(hours=2), exit_time=base_time + timedelta(hours=3),
            entry_price=240.0, exit_price=244.0, quantity=50.0, pnl=-200.0, pnl_percent=-1.67, commission=2.0
        ),
        # Revenge trade: entered within 120s of loss with doubled size
        TradeRecord(
            trade_id="DEMO-103", broker="IBKR", symbol="TSLA", asset_class=AssetClass.EQUITY,
            direction=TradeDirection.LONG, entry_time=base_time + timedelta(hours=3, minutes=2), exit_time=base_time + timedelta(hours=3, minutes=30),
            entry_price=244.2, exit_price=241.0, quantity=100.0, pnl=-320.0, pnl_percent=-1.31, commission=4.0
        ),
        TradeRecord(
            trade_id="DEMO-104", broker="MT5", symbol="XAUUSD", asset_class=AssetClass.FUTURES,
            direction=TradeDirection.LONG, entry_time=base_time + timedelta(days=2), exit_time=base_time + timedelta(days=2, hours=3),
            entry_price=2680.0, exit_price=2710.0, quantity=1.5, pnl=4500.0, pnl_percent=1.12, commission=10.0
        ),
        # Overleveraged crypto trade without stop loss
        TradeRecord(
            trade_id="DEMO-105", broker="BINANCE", symbol="SOLUSDT", asset_class=AssetClass.CRYPTO,
            direction=TradeDirection.LONG, entry_time=base_time + timedelta(days=3), exit_time=base_time + timedelta(days=3, hours=4),
            entry_price=210.0, exit_price=185.0, quantity=30.0, pnl=-750.0, pnl_percent=-11.9, commission=6.0
        )
    ]


def main():
    parser = argparse.ArgumentParser(description="OpenTradeJournal-AI CLI Terminal")
    subparsers = parser.add_subparsers(dest="command")

    demo_p = subparsers.add_parser("demo", help="Run full diagnostic demo on synthetic trade portfolio")
    
    analyze_p = subparsers.add_parser("analyze", help="Analyze trade statement file")
    analyze_p.add_argument("--file", "-f", required=True, help="Path to statement file (CSV or JSON)")
    analyze_p.add_argument("--broker", "-b", required=True, choices=["ibkr", "mt5", "binance", "bybit"], help="Broker format")

    args = parser.parse_args()

    if args.command == "demo" or not args.command:
        trades = get_demo_trades()
        print("\n📈 Loaded 5 Multi-Broker Demo Trades across IBKR, MT5, and Binance.\n")
    elif args.command == "analyze":
        with open(args.file, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        if args.broker == "ibkr":
            trades = IBKRParser.parse_csv(content)
        elif args.broker == "mt5":
            trades = MT5Parser.parse_csv(content)
        else:
            trades = CryptoParser.parse_json(content, exchange=args.broker.upper())
        print(f"\n📂 Ingested {len(trades)} trade records from {args.file} [{args.broker.upper()}].\n")

    summary = PerformanceEngine.calculate_summary(trades)
    detector = CognitiveMistakeDetector()
    diagnoses = detector.analyze_trades(trades)
    
    # 1. Output ASCII Tearsheet
    print(TearsheetGenerator.generate_ascii_tearsheet(summary))
    
    # 2. Output Cognitive Psych Report
    print(CognitiveCoachingAdvisor.generate_executive_psych_report(summary, diagnoses))


if __name__ == "__main__":
    main()
