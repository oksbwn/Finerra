from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.exceptions import http_exception_handler, generic_exception_handler
from starlette.exceptions import HTTPException as StarletteHTTPException

def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
    )

    # Middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # TODO: Restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception Handlers
    application.add_exception_handler(StarletteHTTPException, http_exception_handler)
    application.add_exception_handler(Exception, generic_exception_handler)

    # Routers
    from backend.app.modules.auth.router import router as auth_router
    from backend.app.modules.finance.router import router as finance_router
    from backend.app.modules.ingestion.router import router as ingestion_router
    
    application.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
    application.include_router(finance_router, prefix=f"{settings.API_V1_STR}/finance", tags=["finance"])
    application.include_router(ingestion_router, prefix=f"{settings.API_V1_STR}/ingestion", tags=["ingestion"])
    
    # DB Creation (Dev only)
    # DB Creation (Dev only)
    from backend.app.core.database import engine, Base
    from sqlalchemy import text, inspect
    
    # Simple Auto-Migration: Add missing columns
    # We use a direct execution approach to avoid introspection issues
    # 1. Accounts Migration
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE accounts ADD COLUMN account_mask VARCHAR"))
            print("Detailed Migration Log: 'account_mask' column ADDED successfully.")
    except Exception as e:
        print(f"Detailed Migration Log: 'account_mask' likely exists. {e}")

    # 2. Transactions Migration
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE transactions ADD COLUMN type VARCHAR DEFAULT 'DEBIT'"))
            print("Detailed Migration Log: 'type' column ADDED successfully.")
    except Exception as e:
         print(f"Detailed Migration Log: 'type' likely exists. {e}")

    # 3. Accounts Owner Name Migration
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE accounts ADD COLUMN owner_name VARCHAR"))
            print("Detailed Migration Log: 'owner_name' column ADDED successfully.")
    except Exception as e:
         print(f"Detailed Migration Log: 'owner_name' likely exists. {e}")

    # 4. Accounts Balance Migration
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE accounts ADD COLUMN balance DECIMAL(15,2) DEFAULT 0"))
            print("Detailed Migration Log: 'balance' column ADDED successfully.")
    except Exception as e:
         print(f"Detailed Migration Log: 'balance' likely exists. {e}")

    # 5. Accounts Verified Migration
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE accounts ADD COLUMN is_verified BOOLEAN DEFAULT TRUE"))
            print("Detailed Migration Log: 'is_verified' column ADDED successfully.")
    except Exception as e:
         print(f"Detailed Migration Log: 'is_verified' likely exists. {e}")

    # 6. Transactions CreatedAt Migration
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE transactions ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"))
            print("Detailed Migration Log: 'created_at' column in transactions ADDED successfully.")
    except Exception as e:
         print(f"Detailed Migration Log: 'created_at' in transactions likely exists. {e}")

    # 11. Transactions Source Migration
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE transactions ADD COLUMN source VARCHAR DEFAULT 'MANUAL'"))
            print("Detailed Migration Log: 'source' column in transactions ADDED successfully.")
    except Exception as e:
         print(f"Detailed Migration Log: 'source' in transactions likely exists. {e}")

    # 12. Transactions Recipient Migration
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE transactions ADD COLUMN recipient VARCHAR"))
            print("Detailed Migration Log: 'recipient' column in transactions ADDED successfully.")
    except Exception as e:
         print(f"Detailed Migration Log: 'recipient' in transactions likely exists. {e}")

    # 13. Backfill Recipient Data (One-time)
    try:
        from backend.app.modules.ingestion.parsers.recipient_parser import RecipientParser
        from sqlalchemy.orm import Session
        with Session(engine) as session:
            # Find all transactions with missing recipient
            from backend.app.modules.finance.models import Transaction
            txns = session.query(Transaction).filter((Transaction.recipient == None) | (Transaction.recipient == "")).all()
            if txns:
                print(f"Detailed Migration Log: Backfilling {len(txns)} recipients using modular RecipientParser...")
                for txn in txns:
                    txn.recipient = RecipientParser.extract(txn.description)
                session.commit()
                print("Detailed Migration Log: Backfill completed successfully.")
    except Exception as e:
        print(f"Detailed Migration Log: Recipient backfill failed. {e}")

    # 7. Category Rules Migration
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS category_rules (
                    id VARCHAR PRIMARY KEY,
                    tenant_id VARCHAR NOT NULL,
                    name VARCHAR NOT NULL,
                    category VARCHAR NOT NULL,
                    keywords VARCHAR NOT NULL,
                    priority INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (tenant_id) REFERENCES tenants(id)
                )
            """))
            print("Detailed Migration Log: 'category_rules' table CREATED successfully.")
    except Exception as e:
         print(f"Detailed Migration Log: 'category_rules' table creation failed. {e}")

    # 8. Categories Migration (Ensure icon exists)
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE categories ADD COLUMN icon VARCHAR DEFAULT '🏷️'"))
            print("Detailed Migration Log: 'icon' column in categories ADDED successfully.")
    except Exception as e:
         print(f"Detailed Migration Log: 'icon' in categories likely exists. {e}")

    # 9. Budgets Migration
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS budgets (
                    id VARCHAR PRIMARY KEY,
                    tenant_id VARCHAR NOT NULL,
                    category VARCHAR NOT NULL,
                    amount_limit DECIMAL(15, 2) NOT NULL,
                    period VARCHAR DEFAULT 'MONTHLY',
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (tenant_id) REFERENCES tenants(id)
                )
            """))
            print("Detailed Migration Log: 'budgets' table CREATED successfully.")
    except Exception as e:
        print(f"Detailed Migration Log: 'budgets' table creation failed. {e}")

    # 10. Accounts Import Config Migration
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE accounts ADD COLUMN import_config VARCHAR"))
            print("Detailed Migration Log: 'import_config' column ADDED successfully.")
    except Exception as e:
         print(f"Detailed Migration Log: 'import_config' likely exists. {e}")

    # 14. Email Configurations Table Migration
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS email_configurations (
                    id VARCHAR PRIMARY KEY,
                    tenant_id VARCHAR NOT NULL,
                    email VARCHAR NOT NULL,
                    password VARCHAR NOT NULL,
                    imap_server VARCHAR DEFAULT 'imap.gmail.com',
                    folder VARCHAR DEFAULT 'INBOX',
                    is_active BOOLEAN DEFAULT TRUE,
                    last_sync_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (tenant_id) REFERENCES tenants(id)
                )
            """))
            print("Detailed Migration Log: 'email_configurations' table CREATED successfully.")
    except Exception as e:
        print(f"Detailed Migration Log: 'email_configurations' table creation failed. {e}")

    # 15. Pending Transactions Table Migration
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS pending_transactions (
                    id VARCHAR PRIMARY KEY,
                    tenant_id VARCHAR NOT NULL,
                    account_id VARCHAR NOT NULL,
                    amount DECIMAL(15,2) NOT NULL,
                    date TIMESTAMP NOT NULL,
                    description VARCHAR,
                    recipient VARCHAR,
                    category VARCHAR,
                    source VARCHAR NOT NULL,
                    raw_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (tenant_id) REFERENCES tenants(id),
                    FOREIGN KEY (account_id) REFERENCES accounts(id)
                )
            """))
            print("Detailed Migration Log: 'pending_transactions' table CREATED successfully.")
            
            # Add full_name and avatar to users
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN full_name VARCHAR"))
                print("Detailed Migration Log: 'full_name' column ADDED to users.")
            except: pass
            
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN avatar VARCHAR"))
                print("Detailed Migration Log: 'avatar' column ADDED to users.")
            except: pass

            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR DEFAULT 'ADULT'"))
                print("Detailed Migration Log: 'role' column ADDED to users.")
            except: pass

            try:
                conn.execute(text("ALTER TABLE accounts ADD COLUMN owner_id VARCHAR"))
                print("Detailed Migration Log: 'owner_id' column ADDED to accounts.")
            except: pass

            try:
                conn.execute(text("ALTER TABLE email_configurations ADD COLUMN auto_sync_enabled BOOLEAN DEFAULT FALSE"))
                print("Detailed Migration Log: 'auto_sync_enabled' column ADDED to email_configurations.")
            except: pass

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS email_sync_logs (
                    id VARCHAR PRIMARY KEY,
                    config_id VARCHAR NOT NULL,
                    tenant_id VARCHAR NOT NULL,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    status VARCHAR,
                    items_processed NUMERIC(10,0) DEFAULT 0,
                    message TEXT,
                    FOREIGN KEY (config_id) REFERENCES email_configurations(id),
                    FOREIGN KEY (tenant_id) REFERENCES tenants(id)
                )
            """))
            print("Detailed Migration Log: 'email_sync_logs' table CREATED successfully.")

            try:
                conn.execute(text("ALTER TABLE email_sync_logs ADD COLUMN tenant_id VARCHAR"))
                print("Detailed Migration Log: 'tenant_id' column ADDED to email_sync_logs.")
            except: pass

            try:
                conn.execute(text("ALTER TABLE pending_transactions ADD COLUMN external_id VARCHAR"))
                print("Detailed Migration Log: 'external_id' column ADDED to pending_transactions.")
            except: pass

    except Exception as e:
        print(f"Detailed Migration Log: Migration error (handled): {e}")

    Base.metadata.create_all(bind=engine)

    # --- Background Tasks ---
    import asyncio
    from backend.app.modules.ingestion.email_sync import EmailSyncService
    from backend.app.modules.ingestion import models as ingestion_models
    from backend.app.modules.ingestion.services import IngestionService # Indirectly needed
    from backend.app.core.database import SessionLocal
    
    @application.on_event("startup")
    async def schedule_auto_sync():
        async def run_auto_sync():
            while True:
                print("[AutoSync] Checking for scheduled syncs...")
                try:
                    # Create a new session for this thread
                    with SessionLocal() as db:
                        configs = db.query(ingestion_models.EmailConfiguration).filter(
                            ingestion_models.EmailConfiguration.is_active == True,
                            ingestion_models.EmailConfiguration.auto_sync_enabled == True
                        ).all()
                        
                        print(f"[AutoSync] Found {len(configs)} active configs.")
                        for config in configs:
                            print(f"[AutoSync] Syncing {config.email}...")
                            try:
                                EmailSyncService.sync_emails(
                                    db=db,
                                    tenant_id=config.tenant_id,
                                    config_id=config.id,
                                    imap_server=config.imap_server,
                                    email_user=config.email,
                                    email_pass=config.password,
                                    folder=config.folder,
                                    search_criterion='ALL'
                                )
                            except Exception as e:
                                print(f"[AutoSync] Error syncing {config.email}: {e}")
                except Exception as e:
                    print(f"[AutoSync] General Loop Error: {e}")
                
                # Sleep for 15 minutes (900 seconds)
                await asyncio.sleep(900)

        asyncio.create_task(run_auto_sync())

    return application

app = create_application()

@app.get("/")
def root():
    return {"message": "Welcome to Family Finance Platform API"}
