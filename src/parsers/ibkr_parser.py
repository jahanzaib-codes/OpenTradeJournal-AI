"""
OpenTradeJournal-AI: Interactive Brokers Statement Parser
Ingests IBKR Activity Statement CSV exports and Flex Queries into normalized TradeRecord models.
"""

import io
import csv
from typing import List
from datetime import datetime
from src.models.trade import TradeRecord, AssetClass, TradeDirection


class IBKRParser:
    """Parser for Interactive Brokers (IBKR) activity exports."""

    @staticmethod
    def parse_csv(csv_content: str) -> List[TradeRecord]:
        """
        Parses IBKR Activity / Trades CSV file.
        Matches Buy/Sell executions into round-trip trades.
        """
        records: List[TradeRecord] = []
        reader = csv.reader(io.StringIO(csv_content))
        
        # IBKR format often contains section headers like "Trades,Header,DataDiscriminator..."
        # We search for Trade execution rows
        headers = []
        trade_rows = []
        
        for row in reader:
            if not row:
                continue
            if len(row) > 2 and row[0] == "Trades" and row[1] == "Header":
                headers = [h.strip() for h in row]
            elif len(row) > 2 and row[0] == "Trades" and row[1] == "Data":
                if headers:
                    row_dict = dict(zip(headers, row))
                    trade_rows.append(row_dict)

        # Fallback to standard generic CSV if not IBKR sectioned format
        if not trade_rows:
            reader = csv.DictReader(io.StringIO(csv_content))
            for row in reader:
                trade_rows.append(row)

        for idx, item in enumerate(trade_rows):
            try:
                symbol = item.get("Symbol") or item.get("symbol") or "UNKNOWN"
                dt_str = item.get("Date/Time") or item.get("Date") or item.get("datetime") or ""
                
                # Parse date
                try:
                    dt = datetime.strptime(dt_str, "%Y-%m-%d, %H:%M:%S")
                except:
                    try:
                        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                    except:
                        dt = datetime.now()

                qty_str = item.get("Quantity") or item.get("qty") or "1"
                qty = abs(float(qty_str))
                
                price_str = item.get("T. Price") or item.get("Price") or item.get("price") or "0.0"
                price = float(price_str)
                
                pnl_str = item.get("Realized P/L") or item.get("pnl") or "0.0"
                pnl = float(pnl_str)
                
                comm_str = item.get("Comm/Fee") or item.get("commission") or "0.0"
                commission = abs(float(comm_str))

                # Identify direction
                raw_side = item.get("Buy/Sell") or item.get("side") or ("LONG" if float(qty_str) > 0 else "SHORT")
                direction = TradeDirection.LONG if "BUY" in raw_side.upper() or "LONG" in raw_side.upper() else TradeDirection.SHORT

                # Determine asset class
                asset_category = item.get("Asset Category", "").upper()
                if "OPT" in asset_category:
                    ac = AssetClass.OPTIONS
                elif "FUT" in asset_category:
                    ac = AssetClass.FUTURES
                elif "FOREX" in asset_category or "CASH" in asset_category:
                    ac = AssetClass.FOREX
                else:
                    ac = AssetClass.EQUITY

                # Synthesize round-trip trade record
                pnl_pct = (pnl / (price * qty)) * 100.0 if (price * qty) > 0 else 0.0

                records.append(TradeRecord(
                    trade_id=f"IBKR-{item.get('TradeID', idx+1)}",
                    broker="IBKR",
                    symbol=symbol,
                    asset_class=ac,
                    direction=direction,
                    entry_time=dt,
                    exit_time=dt,
                    entry_price=price,
                    exit_price=price,
                    quantity=qty,
                    pnl=pnl,
                    pnl_percent=round(pnl_pct, 2),
                    commission=commission,
                    notes=item.get("Notes/Codes", "")
                ))
            except Exception:
                continue

        return records
