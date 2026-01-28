from sqlalchemy.orm import Session
from typing import Optional
from parser.schemas.transaction import IngestionResult, ParsedItem, Transaction
from parser.core.classifier import FinancialClassifier
from parser.parsers.registry import ParserRegistry
from parser.db.models import RequestLog
import hashlib
import json
from datetime import datetime, timedelta

class IngestionPipeline:

    def __init__(self, db: Session):
        self.db = db

    def run(self, content: str, source: str, sender: Optional[str] = None) -> IngestionResult:
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
        log = RequestLog(input_hash=input_hash, source=source, input_payload={"content": content, "sender": sender}, status="processing")
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
            if p.can_handle(content, sender):
                try:
                    parsed_txn = p.parse(content)
                    if parsed_txn:
                        logs.append(f"Successfully parsed by {p.name}")
                        break
                except Exception as e:
                    logs.append(f"Parser {p.name} failed: {str(e)}")

        # B. User Patterns
        if not parsed_txn:
             try:
                 from parser.parsers.patterns.regex_engine import PatternParser
                 # Load rules for this source
                 p_parser = PatternParser(self.db, source)
                 parsed_txn = p_parser.parse(content)
             except Exception as e:
                 logs.append(f"Pattern Parser failed: {str(e)}")
                 
        if parsed_txn and not logs: # If parsed by Pattern parser
             logs.append("Parsed via Patterns")

        # C. AI Fallback
        if not parsed_txn:
             try:
                 from parser.parsers.ai.gemini_parser import GeminiParser
                 ai_parser = GeminiParser(self.db)
                 parsed_txn = ai_parser.parse(content, source)
                 if parsed_txn:
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
                metadata={"confidence": 0.5 if "Pattern" in (logs[-1] if logs else "") else 1.0, 
                          "parser_used": "Static/Pattern", 
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
