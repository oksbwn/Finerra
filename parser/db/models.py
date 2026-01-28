from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from parser.db.database import Base
import uuid
import datetime

def generate_uuid():
    return str(uuid.uuid4())

class RequestLog(Base):
    __tablename__ = "request_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    source = Column(String, nullable=False) # SMS, EMAIL, FILE
    input_hash = Column(String, index=True) # For idempotency
    input_payload = Column(JSON, nullable=True)
    output_payload = Column(JSON, nullable=True)
    status = Column(String) # success, duplicate, failed
    parser_steps = Column(JSON, nullable=True) # Trace of execution

class FileParsingConfig(Base):
    __tablename__ = "file_parsing_configs"

    fingerprint = Column(String, primary_key=True) # e.g. "HDFCBANK-1234"
    format = Column(String, default="EXCEL")
    header_row_index = Column(Integer, default=0)
    columns_json = Column(JSON, nullable=False) # {"date": "Transaction Date", ...}
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class AIConfig(Base):
    __tablename__ = "ai_configs"

    id = Column(String, primary_key=True, default="default")
    provider = Column(String, default="gemini")
    api_key_enc = Column(String, nullable=True) # Encrypted or just stored if internal
    model_name = Column(String, default="gemini-1.5-flash")
    is_enabled = Column(Boolean, default=True)
    prompts_json = Column(JSON, nullable=True)

class PatternRule(Base):
    __tablename__ = "pattern_rules"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    source = Column(String, nullable=False) # SMS, EMAIL
    regex_pattern = Column(String, nullable=False)
    mapping_json = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
