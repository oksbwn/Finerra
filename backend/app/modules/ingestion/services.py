from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from backend.app.modules.finance import models as finance_models
from backend.app.modules.ingestion.base import ParsedTransaction

class IngestionService:
    @staticmethod
    def match_account(db: Session, tenant_id: str, mask: str) -> Optional[finance_models.Account]:
        """
        Find an account belonging to the tenant that ends with the given mask.
        Mask usually is 4 digits like "1234".
        """
        if not mask or len(mask) < 2:
            return None
            
        # Basic suffix match
        # DuckDB/SQLAlchemy 'like' or 'endswith'
        # We assume the mask in DB (e.g. "XX1234") ends with the SMS mask (e.g. "1234")
        # or simplified: just check if DB account_mask ends with the provided digits
        
        accounts = db.query(finance_models.Account).filter(
            finance_models.Account.tenant_id == tenant_id,
            finance_models.Account.account_mask != None
        ).all()
        
        for acc in accounts:
            if acc.account_mask and acc.account_mask.endswith(mask[-4:]):
                return acc
        return None

    @staticmethod
    def process_transaction(db: Session, tenant_id: str, parsed: ParsedTransaction):
        """
        Process a parsed transaction: match account, save transaction.
        """
        account = None
        if parsed.account_mask:
            account = IngestionService.match_account(db, tenant_id, parsed.account_mask)
            
        if not account and parsed.account_mask:
            # Auto-Discovery: Create new untrusted account
            print(f"Auto-creating account for mask {parsed.account_mask}")
            account = finance_models.Account(
                tenant_id=tenant_id,
                name=f"Auto-Detected (XX{parsed.account_mask[-4:]})",
                type=finance_models.AccountType.BANK, # Default to Bank
                account_mask=parsed.account_mask[-4:], # Store last 4 digits
                is_verified=False,
                balance=0.0
            )
            db.add(account)
            db.commit()
            db.refresh(account)
            
        if not account:
             # Fallback if no mask was present in SMS at all
             # For V1, we log/skip
             return {"status": "skipped", "reason": f"No account found and no mask in SMS"}
            
        # Create Transaction via Finance Service (Handles Deduplication & Balance Updates)
        from backend.app.modules.finance.services import FinanceService
        from backend.app.modules.finance import schemas as finance_schemas
        
        # Determine amount sign
        final_amount = parsed.amount
        if parsed.type == "DEBIT":
            final_amount = -abs(parsed.amount)
        else:
            final_amount = abs(parsed.amount)
            
        txn_create = finance_schemas.TransactionCreate(
            account_id=str(account.id),
            amount=final_amount,
            date=parsed.date,
            description=parsed.description,
            category="Uncategorized",
            external_id=parsed.ref_id,
            tags=[]
        )
        
        try:
            db_txn = FinanceService.create_transaction(db, txn_create, tenant_id)
            return {"status": "success", "transaction_id": db_txn.id, "account": account.name, "deduplicated": db_txn.created_at < parsed.date}
        except Exception as e:
            print(f"Error creating transaction: {e}")
            raise e
