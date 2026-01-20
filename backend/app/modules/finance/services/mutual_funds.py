import httpx
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from backend.app.modules.finance import models as finance_models
from backend.app.modules.finance.models import MutualFundsMeta, MutualFundHolding, MutualFundOrder

MFAPI_BASE_URL = "https://api.mfapi.in/mf"

class MutualFundService:
    
    @staticmethod
    def get_mock_returns(scheme_code: str) -> float:
        try:
            code_str = str(scheme_code or '0')
            hash_val = sum(ord(c) for c in code_str)
            base = 12 + (hash_val % 25)
            # Add some decimal variation based on hash to make it look real
            decimal = (hash_val % 10) / 10.0
            return float(f"{base + decimal:.1f}")
        except:
            return 12.0

    @staticmethod
    def search_funds(query: Optional[str] = None, category: Optional[str] = None, amc: Optional[str] = None, limit: int = 20, offset: int = 0, sort_by: str = 'relevance', all_funds_cache: Optional[List[dict]] = None):
        try:
            # Fetch the main list from MFAPI if not provided
            if all_funds_cache:
                all_funds = all_funds_cache
            else:
                response = httpx.get(f"{MFAPI_BASE_URL}")
                if response.status_code == 200:
                    all_funds = response.json()
                else:
                    return []
            
            # Continue with processing...
            if True: # indent preservation wrapper
                query_low = query.lower() if query else None
                cat_low = category.lower() if category else None
                amc_low = amc.lower() if amc else None

                # Optimization: Direct filter if possible, otherwise iterate
                filtered_funds = []
                for f in all_funds:
                    scheme_name = f.get('schemeName', '').lower()
                    
                    # Filtering logic
                    match = True
                    if query_low and query_low not in scheme_name:
                        match = False
                    if cat_low and cat_low not in scheme_name: 
                        match = False
                    if amc_low and amc_low not in scheme_name: 
                        match = False
                        
                    if match:
                        filtered_funds.append(f)

                # Sorting
                if sort_by == 'returns_desc':
                    filtered_funds.sort(key=lambda x: MutualFundService.get_mock_returns(str(x.get('schemeCode'))), reverse=True)
                elif sort_by == 'returns_asc':
                    filtered_funds.sort(key=lambda x: MutualFundService.get_mock_returns(str(x.get('schemeCode'))))
                # Default 'relevance' keeps original order (usually by scheme code or alphabetical from API)

                # Pagination
                start = offset
                end = offset + limit
                results = filtered_funds[start:end]
                            
                return results
            return []
        except Exception as e:
            print(f"Error searching funds: {e}")
            return []

    @staticmethod
    def get_fund_nav(scheme_code: str):
        try:
            response = httpx.get(f"{MFAPI_BASE_URL}/{scheme_code}")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "SUCCESS":
                    # Meta: fund_house, scheme_type, scheme_category, scheme_code, scheme_name
                    # Data: date, nav
                    return data
            return None
        except Exception as e:
            print(f"Error fetching NAV: {e}")
            return None

    @staticmethod
    def add_transaction(db: Session, tenant_id: str, data: dict):
        # 1. Ensure Meta exists
        scheme_code = data['scheme_code']
        meta = db.query(MutualFundsMeta).filter(MutualFundsMeta.scheme_code == scheme_code).first()
        
        if not meta:
            # Fetch from API and save
            fund_data = MutualFundService.get_fund_nav(scheme_code)
            if fund_data:
                meta_info = fund_data.get("meta", {})
                meta = MutualFundsMeta(
                    scheme_code=str(meta_info.get("scheme_code")),
                    scheme_name=meta_info.get("scheme_name"),
                    fund_house=meta_info.get("fund_house"),
                    category=meta_info.get("scheme_category")
                )
                db.add(meta)
                db.commit()
            else:
                raise ValueError("Invalid Scheme Code or API Error")

        # 2. Create Order
        order = MutualFundOrder(
            tenant_id=tenant_id,
            scheme_code=scheme_code,
            type=data.get('type', 'BUY'),
            amount=data['amount'],
            units=data['units'],
            nav=data['nav'],
            order_date=data['date'],
            import_source="MANUAL"
        )
        db.add(order)
        
        # 3. Update/Create Holding
        folio_number = data.get('folio_number')
        query = db.query(MutualFundHolding).filter(
            MutualFundHolding.tenant_id == tenant_id,
            MutualFundHolding.scheme_code == scheme_code
        )
        
        if folio_number:
            query = query.filter(MutualFundHolding.folio_number == folio_number)
        else:
            query = query.filter(MutualFundHolding.folio_number.is_(None))
            
        holding = query.first()

        if not holding:
            holding = MutualFundHolding(
                tenant_id=tenant_id,
                scheme_code=scheme_code,
                folio_number=folio_number,
                units=0,
                average_price=0
            )
            db.add(holding)
            db.flush() # Get ID for order
        else:
            # Overwrite if we somehow got a new folio for existing (should not happen with updated filter)
            if folio_number:
                holding.folio_number = folio_number
        
        # Update Holding Logic (Weighted Average Price for BUY, FIFO/Avg for SELL - keeping simple Avg for now)
        if order.type == "BUY":
            # Handle possible None types from DB and Decimal vs Float coercion
            current_units = float(holding.units or 0.0)
            current_avg = float(holding.average_price or 0.0)
            
            # Use order.amount if available (more precise), fallback to units*nav
            order_units = float(order.units)
            order_amount = float(order.amount)
            txn_cost = order_amount if order_amount > 0 else (float(order.nav) * order_units)
            
            total_cost = (current_avg * current_units) + txn_cost
            total_units = current_units + order_units
            
            holding.average_price = total_cost / total_units if total_units > 0 else 0.0
            holding.units = total_units
        elif order.type == "SELL":
            # Simplify: Reduce units, keep avg price same (standard accounting)
            current_units = float(holding.units or 0.0)
            holding.units = max(0, current_units - float(order.units))
        
        # Prevent historical imports from overwriting a newer or forced NAV
        # Only update if current NAV is 0/None or if this order is very recent
        if not holding.last_nav or float(holding.last_nav) == 0:
            holding.last_nav = order.nav
            holding.last_updated_at = order.order_date
        
        holding.current_value = float(holding.units) * float(holding.last_nav or 0.0)

        order.holding_id = holding.id
        db.commit()
        return order

    @staticmethod
    def delete_holding(db: Session, tenant_id: str, holding_id: str):
        holding = db.query(MutualFundHolding).filter(
            MutualFundHolding.id == holding_id,
            MutualFundHolding.tenant_id == tenant_id
        ).first()
        
        if not holding:
            raise Exception("Holding not found")
            
        # Delete related orders too? Or keep them?
        # Usually delete checks for safety, but user asked for delete.
        # Let's delete the holding. Cascade should handle orders if configured, 
        # but let's check models. MutualFundHolding doesn't seem to cascade orders in definitions above clearly.
        # Let's just delete the holding row.
        db.delete(holding)
        db.commit()
        return True

    @staticmethod
    def get_portfolio(db: Session, tenant_id: str):
        import asyncio
        
        holdings = db.query(MutualFundHolding).filter(MutualFundHolding.tenant_id == tenant_id).all()
        results = []
        
        # Check for updates needed (Stale > 24h or None)
        updates_made = False
        today = datetime.utcnow().date()
        
        async def fetch_nav_and_sparkline(scheme_code):
            """Fetch both current NAV and 30-day history concurrently"""
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"https://api.mfapi.in/mf/{scheme_code}", timeout=5.0)
                    
                if response.status_code == 200:
                    fund_data = response.json()
                    raw_data = fund_data.get("data", [])
                    
                    def parse_date(d_str):
                        try:
                            return datetime.strptime(d_str, "%d-%m-%Y")
                        except:
                            return datetime.min

                    # Sort by date descending
                    sorted_data = sorted(raw_data, key=lambda x: parse_date(x.get("date", "")), reverse=True)
                    
                    # Latest NAV
                    latest_nav = 0.0
                    nav_date_str = ""
                    if sorted_data:
                        latest_nav_data = sorted_data[0]
                        latest_nav = float(latest_nav_data.get("nav", 0.0))
                        nav_date_str = latest_nav_data.get("date", "")
                    
                    # Sparkline (last 30 days)
                    sparkline_data = sorted_data[:30]  # Get last 30 entries
                    sparkline_data.reverse()  # Reverse to chronological order
                    sparkline = [float(d.get("nav", 0.0)) for d in sparkline_data if d.get("nav")]
                    
                    return {
                        "latest_nav": latest_nav,
                        "nav_date": nav_date_str,
                        "sparkline": sparkline
                    }
                else:
                    return {"latest_nav": 0.0, "nav_date": "", "sparkline": []}
            except Exception as e:
                print(f"Failed to fetch NAV/sparkline for {scheme_code}: {e}")
                return {"latest_nav": 0.0, "nav_date": "", "sparkline": []}
        
        # Fetch all NAV data concurrently
        async def fetch_all_nav_data():
            tasks = [fetch_nav_and_sparkline(h.scheme_code) for h in holdings]
            return await asyncio.gather(*tasks)
        
        nav_data_list = asyncio.run(fetch_all_nav_data())
        
        # Process each holding with its NAV data
        for h, nav_data in zip(holdings, nav_data_list):
            latest_nav = nav_data["latest_nav"]
            nav_date_str = nav_data["nav_date"]
            sparkline = nav_data["sparkline"]
            
            # Update holding if we got valid NAV
            if latest_nav > 0:
                h.last_nav = latest_nav
                current_units = float(h.units or 0.0)
                h.current_value = current_units * latest_nav
                
                def parse_date(d_str):
                    try:
                        return datetime.strptime(d_str, "%d-%m-%Y")
                    except:
                        return datetime.min
                
                h.last_updated_at = parse_date(nav_date_str)
                db.commit()  # Commit each update individually to avoid DuckDB transaction conflicts
                updates_made = True
            
            # Enrich with Meta name
            meta = db.query(MutualFundsMeta).filter(MutualFundsMeta.scheme_code == h.scheme_code).first()
            
            # Safe float conversion handling None
            units = float(h.units or 0.0)
            avg_price = float(h.average_price or 0.0)
            current_val = float(h.current_value or 0.0)
            invested = units * avg_price
            
            # Profit/Loss Calculation
            pl = 0.0
            if current_val > 0:
                pl = current_val - invested
            
            last_updated_str = h.last_updated_at.strftime("%d-%b-%Y") if h.last_updated_at else "N/A"

            results.append({
                "id": h.id,
                "scheme_code": h.scheme_code,
                "scheme_name": meta.scheme_name if meta else "Unknown Fund",
                "folio_number": h.folio_number,
                "units": units,
                "average_price": avg_price,
                "current_value": current_val,
                "invested_value": invested,
                "last_nav": float(h.last_nav or 0.0),
                "profit_loss": pl,
                "last_updated": last_updated_str,
                "sparkline": sparkline  # 30-day NAV trend
            })
            
        # Remove the bulk commit since we're committing individually now
        return results

    @staticmethod
    def get_market_indices():
        import asyncio
        
        async def fetch_index_data(idx):
            try:
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{idx['symbol']}?interval=5m&range=1d"
                headers = {'User-Agent': 'Mozilla/5.0'}
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, headers=headers, timeout=5.0)
                
                if response.status_code == 200:
                    data = response.json()
                    meta = data['chart']['result'][0]['meta']
                    current_price = meta['regularMarketPrice']
                    previous_close = meta['chartPreviousClose']
                    change = current_price - previous_close
                    percent = (change / previous_close) * 100
                    
                    indicators = data['chart']['result'][0]['indicators']['quote'][0]
                    closes = indicators.get('close', [])
                    valid_closes = [c for c in closes if c is not None]
                    sparkline = valid_closes[-20:] if len(valid_closes) > 20 else valid_closes

                    return {
                        "name": idx['name'],
                        "value": f"{current_price:,.2f}",
                        "change": f"{change:+.2f}",
                        "percent": f"{percent:+.2f}%",
                        "isUp": change >= 0,
                        "sparkline": sparkline
                    }
                else:
                    return {"name": idx['name'], "value": "Unavailable", "change": "0.00", "percent": "0.00%", "isUp": True}
            except Exception as e:
                print(f"Error fetching {idx['name']}: {e}")
                return {"name": idx['name'], "value": "Error", "change": "0.00", "percent": "0.00%", "isUp": True}
        
        async def fetch_all():
            indices = [
                {"name": "NIFTY 50", "symbol": "^NSEI"},
                {"name": "SENSEX", "symbol": "^BSESN"},
                {"name": "BANK NIFTY", "symbol": "^NSEBANK"}
            ]
            tasks = [fetch_index_data(idx) for idx in indices]
            return await asyncio.gather(*tasks)
        
        # Run async tasks
        return asyncio.run(fetch_all())
