from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
from backend.app.modules.auth import models as auth_models
from backend.app.modules.auth.dependencies import get_current_user
from backend.app.modules.ingestion.registry import SmsParserRegistry
from backend.app.modules.ingestion.parsers.generic_sms import GenericSmsParser
from backend.app.modules.ingestion.parsers.hdfc import HdfcParser

# Register default parsers
SmsParserRegistry.register(HdfcParser())
SmsParserRegistry.register(GenericSmsParser())

router = APIRouter()

class SmsPayload(BaseModel):
    sender: str
    message: str

from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.modules.ingestion.services import IngestionService

@router.post("/sms")
def ingest_sms(
    payload: SmsPayload,
    current_user: auth_models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ingest a raw SMS message, parse it, and SAVE the transaction if account matches.
    """
    parsed = SmsParserRegistry.parse(payload.sender, payload.message)
    
    if not parsed:
        raise HTTPException(status_code=422, detail="Could not parse SMS content")
        
    result = IngestionService.process_transaction(db, str(current_user.tenant_id), parsed)
    
    return {
        "status": "processed",
        "parsed_data": parsed,
        "result": result
    }

# --- Universal Import (CSV/Excel) ---
from fastapi import UploadFile, File, Form
from typing import List, Dict, Optional
import json
from backend.app.modules.ingestion.parsers.universal_parser import UniversalParser
from backend.app.modules.finance import schemas as finance_schemas
from backend.app.modules.finance.services import FinanceService

@router.post("/csv/analyze")
async def analyze_file(
    file: UploadFile = File(...),
    current_user: auth_models.User = Depends(get_current_user)
):
    """
    Auto-detect header row and return preview.
    """
    try:
        content = await file.read()
        analysis = UniversalParser.analyze(content, file.filename)
        return analysis
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/csv/parse") 
async def parse_file(
    file: UploadFile = File(...),
    mapping: str = Form(...), # JSON string
    header_row_index: int = Form(0),
    current_user: auth_models.User = Depends(get_current_user)
):
    """
    Parse CSV/Excel and return rows.
    """
    try:
        mapping_dict = json.loads(mapping)
        content = await file.read()
        # Pass filename to detect extension
        parsed = UniversalParser.parse(content, file.filename, mapping_dict, header_row_index)
        return parsed
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

class ImportItem(BaseModel):
    date: str
    description: str
    recipient: Optional[str] = None
    amount: float
    type: str # DEBIT/CREDIT
    external_id: Optional[str] = None

class ImportPayload(BaseModel):
    account_id: str
    transactions: List[ImportItem]
    source: str = "CSV" # Default to CSV

@router.post("/csv/import")
def import_csv(
    payload: ImportPayload,
    current_user: auth_models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Bulk import verified transactions.
    """
    success_count = 0
    errors = []
    
    from datetime import datetime
    
    for idx, txn in enumerate(payload.transactions):
        try:
             # Convert to Finance Service format
             # Note: Parser already returns negative amounts for DEBIT, positive for CREDIT
             txn_create = finance_schemas.TransactionCreate(
                 account_id=payload.account_id,
                 amount=txn.amount,  # Use parsed amount as-is
                 date=datetime.fromisoformat(txn.date),
                 description=txn.description,
                 recipient=txn.recipient,  # Extracted merchant/payee
                 category="Uncategorized",
                 tags=[],
                 source=payload.source,
                 external_id=txn.external_id
             )
             FinanceService.create_transaction(db, txn_create, str(current_user.tenant_id))
             success_count += 1
        except Exception as e:
            errors.append(f"Row {idx+1}: {str(e)}")
            
    return {
        "status": "completed",
        "imported": success_count,
        "errors": errors
    }
