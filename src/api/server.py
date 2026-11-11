"""
OpenTradeJournal-AI: FastAPI Application Server
Provides REST endpoints for trade statement ingestion, performance analytics,
and automated psychological mistake audits.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.models.trade import (
    TradeRecord,
    PerformanceSummary,
    CognitiveDiagnosis,
    AssetClass,
    TradeDirection
)
from src.parsers.ibkr_parser import IBKRParser
from src.parsers.mt5_parser import MT5Parser
from src.parsers.crypto_parser import CryptoParser
from src.analytics.performance import PerformanceEngine
from src.cognitive.mistake_detector import CognitiveMistakeDetector
from src.cognitive.llm_advisor import CognitiveCoachingAdvisor
from src.reports.tearsheet import TearsheetGenerator

app = FastAPI(
    title="OpenTradeJournal-AI API",
    description="Institutional trade journal, performance analytics, and cognitive psychology detector.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for active journal session
trade_database: List[TradeRecord] = []
detector = CognitiveMistakeDetector()


def load_demo_trades() -> List[TradeRecord]:
    """Generates a realistic multi-broker quant trade dataset."""
    base_time = datetime.now() - timedelta(days=5)
    records = [
        TradeRecord(
            trade_id="DEMO-101",
            broker="IBKR",
            symbol="SPY",
            asset_class=AssetClass.OPTIONS,
            direction=TradeDirection.LONG,
            entry_time=base_time,
            exit_time=base_time + timedelta(minutes=45),
            entry_price=4.50,
            exit_price=6.20,
            quantity=10.0,
            pnl=1700.0,
            pnl_percent=37.78,
            commission=13.0,
            stop_loss=3.50,
            take_profit=6.50
        ),
        TradeRecord(
            trade_id="DEMO-102",
            broker="IBKR",
            symbol="NVDA",
            asset_class=AssetClass.EQUITY,
            direction=TradeDirection.SHORT,
            entry_time=base_time + timedelta(hours=3),
            exit_time=base_time + timedelta(hours=4),
            entry_price=135.0,
            exit_price=138.5,
            quantity=100.0,
            pnl=-350.0,
            pnl_percent=-2.59,
            commission=2.5,
            stop_loss=139.0
        ),
        # Revenge trade immediately following loss with 2x size
        TradeRecord(
            trade_id="DEMO-103",
            broker="IBKR",
            symbol="NVDA",
            asset_class=AssetClass.EQUITY,
            direction=TradeDirection.LONG,
            entry_time=base_time + timedelta(hours=4, minutes=1),
            exit_time=base_time + timedelta(hours=4, minutes=25),
            entry_price=138.6,
            exit_price=136.0,
            quantity=200.0,
            pnl=-520.0,
            pnl_percent=-1.88,
            commission=5.0
        ),
        TradeRecord(
            trade_id="DEMO-104",
            broker="MT5",
            symbol="XAUUSD",
            asset_class=AssetClass.FUTURES,
            direction=TradeDirection.LONG,
            entry_time=base_time + timedelta(days=1),
            exit_time=base_time + timedelta(days=1, hours=2),
            entry_price=2650.0,
            exit_price=2675.0,
            quantity=2.0,
            pnl=5000.0,
            pnl_percent=0.94,
            commission=12.0,
            stop_loss=2640.0,
            take_profit=2680.0
        ),
        TradeRecord(
            trade_id="DEMO-105",
            broker="BINANCE",
            symbol="BTCUSDT",
            asset_class=AssetClass.CRYPTO,
            direction=TradeDirection.LONG,
            entry_time=base_time + timedelta(days=2),
            exit_time=base_time + timedelta(days=2, hours=1),
            entry_price=88000.0,
            exit_price=90500.0,
            quantity=0.5,
            pnl=1250.0,
            pnl_percent=2.84,
            commission=8.8
        )
    ]
    return records


@app.get("/")
def root():
    return {
        "engine": "OpenTradeJournal-AI",
        "status": "online",
        "version": "1.0.0",
        "active_trades_loaded": len(trade_database),
        "docs": "/docs"
    }


@app.get("/health")
def health():
    return {"status": "HEALTHY", "timestamp": datetime.now().isoformat()}


@app.post("/api/v1/demo/load")
def load_demo():
    """Populates journal with realistic multi-broker trades for demonstration."""
    global trade_database
    trade_database = load_demo_trades()
    return {
        "message": "Demo trade history loaded successfully.",
        "trades_count": len(trade_database)
    }


@app.post("/api/v1/import")
async def import_statement(
    broker: str = Query("ibkr", regex="^(ibkr|mt5|binance|bybit)$"),
    file: UploadFile = File(...)
):
    """Uploads and parses broker statement into journal database."""
    global trade_database
    content = await file.read()
    text = content.decode("utf-8", errors="ignore")

    if broker == "ibkr":
        parsed = IBKRParser.parse_csv(text)
    elif broker == "mt5":
        parsed = MT5Parser.parse_csv(text)
    else:
        parsed = CryptoParser.parse_json(text, exchange=broker.upper())

    if not parsed:
        raise HTTPException(status_code=400, detail="Failed to parse valid trade records from file.")

    trade_database.extend(parsed)
    return {
        "broker": broker,
        "imported_records": len(parsed),
        "total_database_records": len(trade_database)
    }


@app.get("/api/v1/analytics/performance", response_model=PerformanceSummary)
def get_performance():
    """Calculates full quantitative portfolio tearsheet metrics."""
    global trade_database
    active_trades = trade_database if trade_database else load_demo_trades()
    return PerformanceEngine.calculate_summary(active_trades)


@app.get("/api/v1/analytics/psychology")
def get_psychology_report():
    """Runs cognitive mistake detector and generates trader psychology audit."""
    global trade_database
    active_trades = trade_database if trade_database else load_demo_trades()
    summary = PerformanceEngine.calculate_summary(active_trades)
    diagnoses = detector.analyze_trades(active_trades)
    markdown_report = CognitiveCoachingAdvisor.generate_executive_psych_report(summary, diagnoses)

    return {
        "diagnoses": diagnoses,
        "executive_report_markdown": markdown_report
    }


@app.get("/api/v1/reports/tearsheet")
def get_ascii_tearsheet():
    """Returns ASCII terminal tearsheet."""
    global trade_database
    active_trades = trade_database if trade_database else load_demo_trades()
    summary = PerformanceEngine.calculate_summary(active_trades)
    ascii_table = TearsheetGenerator.generate_ascii_tearsheet(summary)
    return {"tearsheet": ascii_table}
