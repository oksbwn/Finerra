import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Numeric
from backend.app.core.database import Base

class EmailConfiguration(Base):
    __tablename__ = "email_configurations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    email = Column(String, nullable=False)
    # Note: In a real app, encrypt this. For now, storing as-is.
    password = Column(String, nullable=False) 
    imap_server = Column(String, default="imap.gmail.com", nullable=False)
    folder = Column(String, default="INBOX", nullable=False)
    is_active = Column(Boolean, default=True)
    auto_sync_enabled = Column(Boolean, default=False)
    last_sync_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class EmailSyncLog(Base):
    __tablename__ = "email_sync_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    config_id = Column(String, ForeignKey("email_configurations.id"), nullable=False)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String, default="running") # running, completed, error
    items_processed = Column(Numeric(10, 0), default=0)
    message = Column(String, nullable=True) # JSON or text log

class PendingTransaction(Base):
    __tablename__ = "pending_transactions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    account_id = Column(String, ForeignKey("accounts.id"), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    date = Column(DateTime, nullable=False)
    description = Column(String, nullable=True)
    recipient = Column(String, nullable=True)
    category = Column(String, nullable=True)
    source = Column(String, nullable=False) # SMS, EMAIL
    raw_message = Column(String, nullable=True)
    external_id = Column(String, nullable=True) # Reference Number/UTR
    created_at = Column(DateTime, default=datetime.utcnow)
