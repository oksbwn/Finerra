from sqlalchemy.orm import Session
from typing import Optional, Any
from parser.schemas.transaction import IngestionResult, ParsedItem, Transaction
from parser.core.classifier import FinancialClassifier
from parser.parsers.registry import ParserRegistry
from parser.db.models import RequestLog
import hashlib
import json
from datetime import datetime, timedelta
from decimal import Decimal

class IngestionPipeline:

    def __init__(self, db: Session):
        self.db = db

    def _convert_to_schema_txn(self, pt: Any) -> Transaction:
        """Helper to convert backend-style ParsedTransaction or dict to microservice Transaction"""
        from parser.schemas.transaction import Transaction, AccountInfo, MerchantInfo, TransactionType
        
        # If it's already a Transaction object (from AI or Pattern parser)
        if isinstance(pt, Transaction):
            return pt
            
        # If it's a dict (from UniversalParser)
        if isinstance(pt, dict):
            return Transaction(
                amount=Decimal(str(pt.get("amount", 0))),
                type=TransactionType.DEBIT if pt.get("type") == "DEBIT" else TransactionType.CREDIT,
                date=datetime.fromisoformat(pt["date"]) if isinstance(pt["date"], str) else pt["date"],
                account=AccountInfo(mask=pt.get("account_mask") or pt.get("external_id")),
                merchant=MerchantInfo(raw=pt.get("description"), cleaned=pt.get("recipient") or pt.get("description")),
                description=pt.get("description"),
                ref_id=pt.get("external_id") or pt.get("ref_id"),
                balance=Decimal(str(pt["balance"])) if pt.get("balance") else None,
                category=pt.get("category"),
                raw_message=pt.get("original_row", {}).get("description", "Imported")
            )
            
        # If it's a backend ParsedTransaction
        return Transaction(
            amount=pt.amount,
            type=TransactionType.DEBIT if pt.type == "DEBIT" else TransactionType.CREDIT,
            date=pt.date,
            account=AccountInfo(mask=pt.account_mask),
            merchant=MerchantInfo(raw=pt.recipient or pt.description, cleaned=pt.recipient or pt.description),
            description=pt.description,
            ref_id=pt.ref_id,
            balance=pt.balance,
            category=pt.category,
            raw_message=pt.raw_message
        )

    def run(self, content: str, source: str, sender: Optional[str] = None, subject: Optional[str] = None) -> IngestionResult:
        # 1. Idempotency Check
        input_hash = hashlib.sha256(f"{source}:{content}".encode()).hexdigest()
        
        # Check last 5 mins
        cutoff = datetime.utcnow() - timedelta(minutes=5)
        existing = self.db.query(RequestLog).filter(
            RequestLog.input_hash == input_hash,
            RequestLog.created_at >= cutoff
        ).first()

        if existing:
            return IngestionResult(status="duplicate_submission", results=[], logs=["Duplicate submission detected"])

        # Create Log Entry
        log = RequestLog(input_hash=input_hash, source=source, input_payload={"content": content, "sender": sender, "subject": subject}, status="processing")
        self.db.add(log)
        self.db.commit()

        logs = []

        # 2. Classification
        if not FinancialClassifier.is_financial(content, source):
            log.status = "ignored"
            self.db.commit()
            return IngestionResult(status="ignored", results=[], logs=["Classified as non-financial"])

        # 3. Extraction Chain
        parsed_txn = None
        
        # A. Static Parsers
        parsers = ParserRegistry.get_sms_parsers() if source == "SMS" else ParserRegistry.get_email_parsers()
        for p in parsers:
            can_handle = False
            try:
                if source == "SMS":
                    can_handle = p.can_handle(sender or "", content)
                else:
                    can_handle = p.can_handle(subject or "", content)
            except Exception as e:
                logs.append(f"can_handle failed for {type(p).__name__}: {str(e)}")
                
            if can_handle:
                try:
                    pt = p.parse(content)
                    if pt:
                        parsed_txn = self._convert_to_schema_txn(pt)
                        parser_name = getattr(p, 'name', type(p).__name__)
                        logs.append(f"Successfully parsed by {parser_name}")
                        break
                except Exception as e:
                    logs.append(f"Parser {type(p).__name__} failed: {str(e)}")

        # B. User Patterns
        if not parsed_txn:
             try:
                 from parser.parsers.patterns.regex_engine import PatternParser
                 # Load rules for this source
                 p_parser = PatternParser(self.db, source)
                 pt = p_parser.parse(content)
                 if pt:
                     parsed_txn = self._convert_to_schema_txn(pt)
             except Exception as e:
                 logs.append(f"Pattern Parser failed: {str(e)}")
                 
        if parsed_txn and not logs: # If parsed by Pattern parser
             logs.append("Parsed via Patterns")

        # C. AI Fallback
        if not parsed_txn:
             try:
                 from parser.parsers.ai.gemini_parser import GeminiParser
                 ai_parser = GeminiParser(self.db)
                 pt = ai_parser.parse(content, source)
                 if pt:
                     parsed_txn = self._convert_to_schema_txn(pt)
                     logs.append("Extracted via AI")
             except Exception as e:
                 logs.append(f"AI Parser failed: {str(e)}")


        # 4. Normalization & Validation
        if parsed_txn:
             from parser.core.normalizer import MerchantNormalizer
             from parser.core.validator import TransactionValidator
             
             # Normalize Merchant
             if parsed_txn.merchant:
                 parsed_txn.merchant.cleaned = MerchantNormalizer.normalize(parsed_txn.merchant.raw)
                 # Update description if it was raw
                 if not parsed_txn.description or parsed_txn.description == parsed_txn.merchant.raw:
                     parsed_txn.description = parsed_txn.merchant.cleaned
             
             # Enrich Time
             TransactionValidator.enrich_time(parsed_txn)
             
             # Validate
             warnings = TransactionValidator.validate(parsed_txn, content)
             if warnings:
                 logs.extend(warnings)

             # 5. Category Hint
             from parser.core.guesser import CategoryGuesser
             if not parsed_txn.category:
                parsed_txn.category = CategoryGuesser.guess(parsed_txn.merchant.cleaned, parsed_txn.description)

             item = ParsedItem(
                status="extracted",
                transaction=parsed_txn,
                metadata={"confidence": 0.5 if any("Pattern" in l for l in logs) else 1.0, 
                          "parser_used": "Static/Pattern/AI", 
                          "source_original": source}
            )
            
             # Update Log
             log.status = "success"
             log.output_payload = item.model_dump(mode='json')
             self.db.commit()
            
             return IngestionResult(status="success", results=[item], logs=logs)

        # Failed
        log.status = "failed"
        self.db.commit()
        return IngestionResult(status="failed", results=[], logs=logs + ["No parser matched"])
