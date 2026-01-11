import json
from decimal import Decimal
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from backend.app.modules.finance import models, schemas

class FinanceService:
    # --- Accounts ---
    def create_account(db: Session, account: schemas.AccountCreate, tenant_id: str) -> models.Account:
        db_account = models.Account(
            **account.model_dump(),
            tenant_id=tenant_id
        )
        if hasattr(db_account, 'owner_id') and db_account.owner_id:
             db_account.owner_id = str(db_account.owner_id) # Ensure string

        db.add(db_account)
        db.commit()
        db.refresh(db_account)
        return db_account

    def get_accounts(db: Session, tenant_id: str, owner_id: Optional[str] = None) -> List[models.Account]:
        query = db.query(models.Account).filter(models.Account.tenant_id == tenant_id)
        if owner_id:
            query = query.filter((models.Account.owner_id == owner_id) | (models.Account.owner_id == None))
        return query.all()

    def update_account(db: Session, account_id: str, account_update: schemas.AccountUpdate, tenant_id: str) -> Optional[models.Account]:
        db_account = db.query(models.Account).filter(
            models.Account.id == account_id,
            models.Account.tenant_id == tenant_id
        ).first()
        
        if not db_account:
            return None
            
        update_data = account_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_account, key, value)
            
        db.add(db_account)
        db.commit()
        db.refresh(db_account)
        return db_account

    # --- Transactions ---
    def create_transaction(db: Session, transaction: schemas.TransactionCreate, tenant_id: str) -> models.Transaction:
        # Deduplication Check: external_id
        if transaction.external_id:
            existing = db.query(models.Transaction).filter(
                models.Transaction.account_id == str(transaction.account_id),
                models.Transaction.external_id == transaction.external_id,
                models.Transaction.tenant_id == tenant_id
            ).first()
            if existing:
                # Idempotency: Return existing transaction instead of creating duplicate
                return existing

        # Serialize tags if present
        tags_str = json.dumps(transaction.tags) if transaction.tags else None
        
        # Infer Type from Amount
        # Negative amount = DEBIT (Expense)
        # Positive amount = CREDIT (Income)
        txn_type = models.TransactionType.DEBIT if transaction.amount < 0 else models.TransactionType.CREDIT

        db_transaction = models.Transaction(
            account_id=str(transaction.account_id),
            tenant_id=tenant_id,
            amount=transaction.amount,
            date=transaction.date,
            description=transaction.description,
            category=transaction.category,
            tags=tags_str,
            external_id=transaction.external_id,
            type=txn_type
        )
        
        # Update Account Balance
        # We should ideally fetch and update account balance here
        db_account = db.query(models.Account).filter(models.Account.id == str(transaction.account_id)).first()
        if db_account:
            # Assuming db_account.balance is set
            current_bal = db_account.balance or 0
            db_account.balance = current_bal + transaction.amount
            db.add(db_account)

        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
        return db_transaction

    def get_transactions(
        db: Session, 
        tenant_id: str, 
        account_id: Optional[str] = None, 
        limit: int = 100
    ) -> List[models.Transaction]:
        query = db.query(models.Transaction).filter(models.Transaction.tenant_id == tenant_id)
        if account_id:
            query = query.filter(models.Transaction.account_id == account_id)
        return query.order_by(models.Transaction.date.desc()).limit(limit).all()

    def update_transaction(db: Session, txn_id: str, txn_update: schemas.TransactionUpdate, tenant_id: str) -> Optional[models.Transaction]:
        db_txn = db.query(models.Transaction).filter(
            models.Transaction.id == txn_id,
            models.Transaction.tenant_id == tenant_id
        ).first()
        
        if not db_txn:
            return None
            
        update_data = txn_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if key == 'tags' and value is not None:
                setattr(db_txn, key, json.dumps(value))
            else:
                setattr(db_txn, key, value)
                
        db.commit()
        db.refresh(db_txn)
        return db_txn

    # --- Metrics ---
    def get_summary_metrics(db: Session, tenant_id: str):
        from datetime import datetime
        
        # Net Worth: Sum of all account balances
        accounts = db.query(models.Account).filter(models.Account.tenant_id == tenant_id).all()
        net_worth = sum(acc.balance or 0 for acc in accounts)
        
        # Monthly Spending: Sum of negative transactions in current month
        # We calculate the magnitude (absolute value) of spending
        now = datetime.utcnow()
        start_of_month = datetime(now.year, now.month, 1)
        
        txns = db.query(models.Transaction).filter(
            models.Transaction.tenant_id == tenant_id,
            models.Transaction.date >= start_of_month,
            models.Transaction.amount < 0 
        ).all()
        
        # Sum is negative (e.g. -500), so we negate it to get positive spending (500)
        monthly_spending = -sum(txn.amount for txn in txns)
        
        return {
            "net_worth": net_worth,
            "monthly_spending": monthly_spending,
            "currency": accounts[0].currency if accounts else "INR"
        }
