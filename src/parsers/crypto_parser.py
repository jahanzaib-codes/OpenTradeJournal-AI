"""
OpenTradeJournal-AI: Crypto Exchange Statement Parser
Ingests Binance, Bybit, and OKX trade history exports into normalized TradeRecord models.
"""

import json
from typing import List
from datetime import datetime
from src.models.trade import TradeRecord, AssetClass, TradeDirection


class CryptoParser:
    """Parser for Cryptocurrency exchange fills (Binance, Bybit)."""

    @staticmethod
    def parse_json(json_str: str, exchange: str = "BINANCE") -> List[TradeRecord]:
        """Parses list of trade fills from JSON."""
        records: List[TradeRecord] = []
        try:
            data = json.loads(json_str)
            if isinstance(data, dict) and "data" in data:
                data = data["data"]
            if not isinstance(data, list):
                return records

            for idx, item in enumerate(data):
                symbol = item.get("symbol") or item.get("market") or "BTCUSDT"
                side = (item.get("side") or item.get("type") or "BUY").upper()
                direction = TradeDirection.LONG if "BUY" in side else TradeDirection.SHORT
                
                price = float(item.get("price") or item.get("avgPrice") or "1.0")
                qty = float(item.get("qty") or item.get("executedQty") or item.get("size") or "1.0")
                pnl = float(item.get("realizedPnl") or item.get("pnl") or "0.0")
                fee = abs(float(item.get("commission") or item.get("fee") or "0.0"))

                time_val = item.get("time") or item.get("timestamp") or 0
                if isinstance(time_val, (int, float)) and time_val > 1000000000000:
                    dt = datetime.fromtimestamp(time_val / 1000.0)
                elif isinstance(time_val, (int, float)) and time_val > 0:
                    dt = datetime.fromtimestamp(time_val)
                else:
                    dt = datetime.now()

                trade_id = str(item.get("id") or item.get("tradeId") or idx + 1)
                notional = price * qty
                pnl_pct = (pnl / notional * 100.0) if notional > 0 else 0.0

                records.append(TradeRecord(
                    trade_id=f"{exchange.upper()}-{trade_id}",
                    broker=exchange.upper(),
                    symbol=symbol,
                    asset_class=AssetClass.CRYPTO,
                    direction=direction,
                    entry_time=dt,
                    exit_time=dt,
                    entry_price=price,
                    exit_price=price,
                    quantity=qty,
                    pnl=pnl - fee,
                    pnl_percent=round(pnl_pct, 2),
                    commission=fee,
                    notes=item.get("orderId", "")
                ))
        except Exception:
            pass

        return records
