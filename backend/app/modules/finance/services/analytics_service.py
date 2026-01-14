from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.modules.finance import models
from backend.app.modules.finance.services.transaction_service import TransactionService

class AnalyticsService:
    @staticmethod
    def get_summary_metrics(db: Session, tenant_id: str, user_role: str = "ADULT", account_id: str = None, start_date: datetime = None, end_date: datetime = None):
        
        # 1. Accounts & Net Worth
        accounts_query = db.query(models.Account).filter(models.Account.tenant_id == tenant_id)
        if account_id:
            accounts_query = accounts_query.filter(models.Account.id == account_id)
        if user_role == "CHILD":
            accounts_query = accounts_query.filter(models.Account.type.notin_(["INVESTMENT", "CREDIT"]))
        
        accounts = accounts_query.all()
        
        # Categorize Balances
        breakdown = {
            "net_worth": 0,
            "bank_balance": 0,
            "cash_balance": 0,
            "credit_debt": 0,
            "investment_value": 0,
            "total_credit_limit": 0,
            "available_credit": 0
        }
        
        for acc in accounts:
            bal = float(acc.balance or 0)
            if acc.type == 'CREDIT_CARD':
                breakdown["credit_debt"] += bal
                breakdown["net_worth"] -= bal
                
                limit = float(acc.credit_limit or 0)
                breakdown["total_credit_limit"] += limit
                breakdown["available_credit"] += (limit - bal)
            
            elif acc.type == 'INVESTMENT':
                breakdown["investment_value"] += bal
                breakdown["net_worth"] += bal
            
            elif acc.type == 'LOAN':
                breakdown["net_worth"] -= bal
                
            else:
                # Bank, Wallet, etc.
                breakdown["net_worth"] += bal
                if acc.type == 'BANK': breakdown["bank_balance"] += bal
                elif acc.type == 'WALLET': breakdown["cash_balance"] += bal

        # 2. Monthly Spending (or Filtered Spending)
        if not start_date:
            now = datetime.utcnow()
            start_date = datetime(now.year, now.month, 1)
        
        txns_query = db.query(models.Transaction).filter(
            models.Transaction.tenant_id == tenant_id,
            models.Transaction.date >= start_date,
            models.Transaction.amount < 0,
            models.Transaction.is_transfer == False
        )
        if end_date:
            txns_query = txns_query.filter(models.Transaction.date <= end_date)
        if account_id:
            txns_query = txns_query.filter(models.Transaction.account_id == account_id)
        if user_role == "CHILD":
             txns_query = txns_query.join(models.Account, models.Transaction.account_id == models.Account.id)\
                                    .filter(models.Account.type.notin_(["INVESTMENT", "CREDIT"]))
        
        monthly_spending = abs(sum(txn.amount for txn in txns_query.all()))
        
        # 3. Overall Budget Health
        all_budgets = db.query(models.Budget).filter(models.Budget.tenant_id == tenant_id).all()
        overall = next((b for b in all_budgets if b.category == 'OVERALL'), None)
        total_budget_limit = float(overall.amount_limit) if overall else 0
        if not overall and all_budgets:
            total_budget_limit = sum(float(b.amount_limit) for b in all_budgets)
            
        budget_health = {
            "limit": total_budget_limit,
            "spent": float(monthly_spending),
            "percentage": (float(monthly_spending) / total_budget_limit * 100) if total_budget_limit > 0 else 0
        }
        
        # 4. Recent Transactions
        # Avoid circular import at top level if possible, or Import inside method
        recent_txns = TransactionService.get_transactions(db, tenant_id, limit=5, user_role=user_role)
        
        return {
            "breakdown": breakdown,
            "monthly_spending": monthly_spending,
            "budget_health": budget_health,
            "recent_transactions": recent_txns,
            "currency": accounts[0].currency if accounts else "INR"
        }

    @staticmethod
    def get_balance_forecast(db: Session, tenant_id: str, days: int = 30, account_id: str = None):
        from datetime import timedelta
        
        # 1. Starting Balance (Liquid assets only)
        liquid_accounts_query = db.query(models.Account).filter(
            models.Account.tenant_id == tenant_id,
            models.Account.type.in_(['BANK', 'WALLET'])
        )
        if account_id:
            liquid_accounts_query = liquid_accounts_query.filter(models.Account.id == account_id)
        
        liquid_accounts = liquid_accounts_query.all()
        
        current_balance = float(sum(acc.balance or 0 for acc in liquid_accounts))
        
        # 2. Get Recurring Transactions
        recs_query = db.query(models.RecurringTransaction).filter(
            models.RecurringTransaction.tenant_id == tenant_id,
            models.RecurringTransaction.is_active == True
        )
        if account_id:
            recs_query = recs_query.filter(models.RecurringTransaction.account_id == account_id)
        recs = recs_query.all()
        
        # 3. Discretionary Spending Heuristic
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_txns_query = db.query(models.Transaction).filter(
            models.Transaction.tenant_id == tenant_id,
            models.Transaction.date >= thirty_days_ago,
            models.Transaction.amount < 0,
            models.Transaction.is_transfer == False
        )
        if account_id:
            recent_txns_query = recent_txns_query.filter(models.Transaction.account_id == account_id)
        recent_txns = recent_txns_query.all()
        
        total_recent = abs(sum(float(t.amount) for t in recent_txns))
        # Daily burn rate based on history
        daily_burn = total_recent / 30.0 if total_recent > 0 else 0
        
        forecast = []
        today = datetime.utcnow().date()
        running_bal = current_balance
        
        for i in range(days):
            target_date = today + timedelta(days=i)
            
            # Apply burn (except for day 0)
            if i > 0:
                running_bal -= daily_burn
            
            # Apply recurring if due
            for r in recs:
                # Simplistic check: matches next_run_date or follows frequency logic
                # For this forecast, we look ahead at next_run and if it lands on this date, we apply.
                # In a more advanced version, we'd Project all occurrences in the window.
                if r.next_run_date.date() == target_date:
                    amt = float(r.amount)
                    if r.type == 'DEBIT':
                        running_bal -= amt
                    else:
                        running_bal += amt
            
            forecast.append({
                "date": target_date.isoformat(),
                "balance": round(running_bal, 2)
            })
            
        return forecast
    @staticmethod
    def get_budget_history(db: Session, tenant_id: str, months: int = 6):
        from datetime import timedelta
        
        # Get all budgets to know which categories to track
        budgets = db.query(models.Budget).filter(models.Budget.tenant_id == tenant_id).all()
        categories = [b.category for b in budgets]
        
        if not categories:
            return []

        now = datetime.utcnow()
        history = []
        
        for i in range(months):
            # Calculate target month and year
            target_month = now.month - i
            target_year = now.year
            while target_month <= 0:
                target_month += 12
                target_year -= 1
            
            m_start = datetime(target_year, target_month, 1)
            if target_month == 12:
                m_end = datetime(target_year + 1, 1, 1)
            else:
                m_end = datetime(target_year, target_month + 1, 1)
            
            # Query spending for these categories in this month
            spendings = db.query(
                models.Transaction.category,
                func.sum(models.Transaction.amount).label('total')
            ).filter(
                models.Transaction.tenant_id == tenant_id,
                models.Transaction.date >= m_start,
                models.Transaction.date < m_end,
                models.Transaction.amount < 0,
                models.Transaction.is_transfer == False,
                models.Transaction.category.in_(categories)
            ).group_by(models.Transaction.category).all()
            
            spend_map = {s.category: abs(float(s.total)) for s in spendings}
            
            # Special case for OVERALL: ignore category and sum all
            if 'OVERALL' in categories:
                overall_spend = db.query(func.sum(models.Transaction.amount)).filter(
                    models.Transaction.tenant_id == tenant_id,
                    models.Transaction.date >= m_start,
                    models.Transaction.date < m_end,
                    models.Transaction.amount < 0,
                    models.Transaction.is_transfer == False
                ).scalar() or 0
                spend_map['OVERALL'] = abs(float(overall_spend))
            
            month_label = m_start.strftime("%b %Y")
            
            entry = {
                "month": month_label,
                "data": []
            }
            
            for b in budgets:
                entry["data"].append({
                    "category": b.category,
                    "limit": float(b.amount_limit),
                    "spent": spend_map.get(b.category, 0.0)
                })
            
            history.append(entry)
            
        return history[::-1] # Chronological order
