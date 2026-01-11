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
