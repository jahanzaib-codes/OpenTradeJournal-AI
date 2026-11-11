"""
OpenTradeJournal-AI: MetaTrader 5 Statement Parser
Ingests MT5 Deal / Order History exports into normalized TradeRecord models.
"""

import io
import csv
from typing import List
from datetime import datetime
from src.models.trade import TradeRecord, AssetClass, TradeDirection


class MT5Parser:
    """Parser for MetaTrader 5 (MT5) trade history reports."""

    @staticmethod
    def parse_csv(csv_content: str) -> List[TradeRecord]:
        """Parses MT5 History Deals / Orders CSV."""
        records: List[TradeRecord] = []
        reader = csv.DictReader(io.StringIO(csv_content))
        
        for idx, row in enumerate(reader):
            try:
                # MT5 typical columns: Time, Position, Order, Symbol, Type, Volume, Price, S/L, T/P, Time, Price, Commission, Swap, Profit
                symbol = row.get("Symbol") or row.get("symbol") or "EURUSD"
                time_str = row.get("Time") or row.get("Open Time") or row.get("time") or ""
                
                try:
                    dt = datetime.strptime(time_str, "%Y.%m.%d %H:%M:%S")
                except:
                    try:
                        dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                    except:
                        dt = datetime.now()

                order_type = (row.get("Type") or row.get("type") or "buy").lower()
                direction = TradeDirection.LONG if "buy" in order_type else TradeDirection.SHORT
                
                volume = abs(float(row.get("Volume") or row.get("volume") or "0.1"))
                entry_price = float(row.get("Price") or row.get("Open Price") or "1.0")
                exit_price = float(row.get("Close Price") or row.get("Price") or entry_price)
                
                profit = float(row.get("Profit") or row.get("profit") or "0.0")
                commission = abs(float(row.get("Commission") or row.get("commission") or "0.0"))
                swap = float(row.get("Swap") or row.get("swap") or "0.0")
                net_pnl = profit + swap - commission

                sl_str = row.get("S/L") or row.get("sl")
                sl = float(sl_str) if sl_str and float(sl_str) > 0 else None
                
                tp_str = row.get("T/P") or row.get("tp")
                tp = float(tp_str) if tp_str and float(tp_str) > 0 else None

                ticket = row.get("Position") or row.get("Order") or str(idx + 1000)

                # Classify asset
                if any(curr in symbol.upper() for curr in ["USD", "EUR", "GBP", "JPY", "CHF", "AUD", "NZD", "CAD"]):
                    if "BTC" in symbol or "ETH" in symbol:
                        ac = AssetClass.CRYPTO
                    elif "XAU" in symbol or "XAG" in symbol:
                        ac = AssetClass.FUTURES
                    else:
                        ac = AssetClass.FOREX
                else:
                    ac = AssetClass.EQUITY

                pnl_pct = (net_pnl / (entry_price * volume * 100000 if ac == AssetClass.FOREX else entry_price * volume)) * 100.0 if entry_price > 0 else 0.0

                records.append(TradeRecord(
                    trade_id=f"MT5-{ticket}",
                    broker="MT5",
                    symbol=symbol,
                    asset_class=ac,
                    direction=direction,
                    entry_time=dt,
                    exit_time=dt,
                    entry_price=entry_price,
                    exit_price=exit_price,
                    quantity=volume,
                    pnl=net_pnl,
                    pnl_percent=round(pnl_pct, 2),
                    commission=commission,
                    stop_loss=sl,
                    take_profit=tp,
                    notes=row.get("Comment", "")
                ))
            except Exception:
                continue

        return records
