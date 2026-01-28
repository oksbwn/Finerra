from fastapi import APIRouter, Depends, HTTPException, Header, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from pydantic import BaseModel

from parser.db.database import get_db
from parser.core.pipeline import IngestionPipeline
from parser.schemas.transaction import IngestionResult, ParsedItem, TransactionMeta
from parser.parsers.bank.hdfc import HdfcSmsParser
from parser.parsers.bank.icici import IciciSmsParser
from parser.parsers.bank.sbi import SbiSmsParser
from parser.parsers.registry import ParserRegistry

# Register Parsers (Should be done on startup, but here is fine for now)
ParserRegistry.register_sms(HdfcSmsParser())
ParserRegistry.register_sms(IciciSmsParser())
ParserRegistry.register_sms(SbiSmsParser())

router = APIRouter()

class AIConfigUpdate(BaseModel):
    provider: str = "gemini"
    api_key: Optional[str] = None
    model_name: str = "gemini-1.5-flash"
    is_enabled: bool = True

@router.get("/v1/config/ai")
def get_ai_config(db: Session = Depends(get_db)):
    from parser.db.models import AIConfig
    config = db.query(AIConfig).first()
    if not config:
        return {"status": "not_configured"}
    
    # Mask Key
    masked_key = "****" + config.api_key_enc[-4:] if config.api_key_enc and len(config.api_key_enc) > 4 else "****"
    
    return {
        "provider": config.provider,
        "model_name": config.model_name,
        "is_enabled": config.is_enabled,
        "api_key_masked": masked_key
    }

@router.post("/v1/config/ai")
def update_ai_config(payload: AIConfigUpdate, db: Session = Depends(get_db)):
    from parser.db.models import AIConfig
    config = db.query(AIConfig).first()
    if not config:
        config = AIConfig(id="default")
        db.add(config)
    
    config.provider = payload.provider
    config.model_name = payload.model_name
    config.is_enabled = payload.is_enabled
    
    # Only update key if provided
    if payload.api_key:
        config.api_key_enc = payload.api_key # Storing plain for now as per plan
    
    db.commit()
    return {"status": "success", "message": "AI Config Updated"}

class SmsIngestRequest(BaseModel):
    sender: str
    body: str
    received_at: Optional[str] = None

class EmailIngestRequest(BaseModel):
    subject: str
    body_text: str
    sender: str
    received_at: Optional[str] = None

@router.post("/v1/ingest/sms", response_model=IngestionResult)
def ingest_sms(
    payload: SmsIngestRequest,
    x_api_key: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    # Security Check (Simple placeholder)
    # in prod: verify x_api_key against DB/Env
    
    pipeline = IngestionPipeline(db)
    result = pipeline.run(payload.body, "SMS", payload.sender)
    
    return result

@router.post("/v1/ingest/email", response_model=IngestionResult)
def ingest_email(
    payload: EmailIngestRequest,
    x_api_key: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    pipeline = IngestionPipeline(db)
    # Combine subject and body for classification/parsing context
    full_content = f"{payload.subject}\n{payload.body_text}"
    result = pipeline.run(full_content, "EMAIL", payload.sender)
    return result

@router.post("/v1/config/mapping")
def save_file_mapping(
    payload: dict, # {fingerprint, format, header_row_index, mapping}
    db: Session = Depends(get_db)
):
    from parser.db.models import FileParsingConfig
    import json
    
    fingerprint = payload.get("fingerprint")
    if not fingerprint:
        raise HTTPException(status_code=400, detail="Fingerprint required")

    config = db.query(FileParsingConfig).filter(FileParsingConfig.fingerprint == fingerprint).first()
    if not config:
        config = FileParsingConfig(fingerprint=fingerprint)
        db.add(config)
    
    config.format = payload.get("format", "EXCEL")
    config.header_row_index = payload.get("header_row_index", 0)
    config.columns_json = payload.get("mapping", {})
    
    db.commit()
    return {"status": "success", "message": "Mapping saved"}

class PatternRuleCreate(BaseModel):
    source: str # SMS, EMAIL
    regex_pattern: str
    mapping: Dict[str, Any]
    # Example: {"amount": 1, "merchant": "Uber"}

@router.post("/v1/config/patterns")
def create_pattern_rule(payload: PatternRuleCreate, db: Session = Depends(get_db)):
    from parser.db.models import PatternRule
    
    # Validation: Check if regex is valid
    try:
        import re
        re.compile(payload.regex_pattern)
    except re.error:
        raise HTTPException(status_code=400, detail="Invalid Regex Pattern")

    rule = PatternRule(
        source=payload.source,
        regex_pattern=payload.regex_pattern,
        mapping_json=payload.mapping
    )
    db.add(rule)
    db.commit()
    return {"status": "success", "id": rule.id}

@router.post("/v1/ingest/file", response_model=IngestionResult)
async def ingest_file(
    file: UploadFile = File(...),
    account_fingerprint: Optional[str] = Form(None),
    mapping_override: Optional[str] = Form(None), # JSON string
    password: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Ingest Excel/CSV. 
    If account_fingerprint provided, tries to load saved mapping.
    """
    from parser.parsers.universal import UniversalParser
    from parser.db.models import FileParsingConfig, RequestLog
    import json
    
    content = await file.read()
    filename = file.filename
    
    # 1. Determine Mapping
    mapping = {}
    header_idx = 0
    
    # Defaults logic
    if account_fingerprint:
        saved = db.query(FileParsingConfig).filter(FileParsingConfig.fingerprint == account_fingerprint).first()
        if saved:
            mapping = saved.columns_json
            header_idx = saved.header_row_index
            
    if mapping_override:
        try:
             # Merge or overwrite
             mapping = json.loads(mapping_override)
        except: pass

    # 2. Parse
    # If no mapping, we should ideally analyze first, but here we assume user sends mapping or we fail/return raw analysis?
    # The requirement was "ingest". If mapping missing, we can't ingest transaction objects properly.
    # For now, if no mapping, we try to Analyze and return failure/suggestion?
    # Or just try UniversalParser.parse with empty mapping (will fail).
    
    if not mapping:
        # Fallback: Analyzer mode
        try:
            analysis = UniversalParser.analyze(content, filename)
            # We can't return IngestionResult easily here since it expects Transactions.
            # But we can log it.
            return IngestionResult(status="analysis_required", results=[], logs=["No mapping found. Analysis: " + json.dumps(analysis, default=str)])
        except Exception as e:
            return IngestionResult(status="failed", results=[], logs=[str(e)])

    try:
        txns = UniversalParser.parse(content, filename, mapping, header_idx, password=password)
        
        # Convert to ParsedItems
        results = []
        for t in txns:
            # We map UniversalParser.Transaction (same schema) to ParsedItem
            results.append(ParsedItem(
                status="extracted",
                transaction=t,
                metadata=TransactionMeta(confidence=1.0, parser_used="UniversalParser", source_original="FILE")
            ))
            
        return IngestionResult(status="success", results=results)
        
    except Exception as e:
        return IngestionResult(status="failed", results=[], logs=[str(e)])

@router.post("/v1/ingest/cas")
async def ingest_cas(
    file: UploadFile = File(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    from parser.parsers.cas import CasParser
    
    content = await file.read()
    try:
        data = CasParser.parse(content, password)
        return {"status": "success", "count": len(data), "transactions": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"CAS Parse Failed: {str(e)}")
