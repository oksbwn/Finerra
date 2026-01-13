import re
from typing import Optional
from datetime import datetime
from decimal import Decimal
from backend.app.modules.ingestion.base import BaseSmsParser, ParsedTransaction

class GenericSmsParser(BaseSmsParser):
    # Regex patterns for common Indian bank SMS formats
    # Example: "Rs 1234.00 debited from a/c XX1234 on 01-01-25 to USER via UPI. Ref: 123"
    # Example: "Credited Rs 5000.00 to a/c XX9999..."
    
    DEBIT_PATTERN = re.compile(r"(?i)(?:Rs\.?|INR)\s*([\d,]+\.?\d*)\s*debited\s*from.*a/c\s*([xX]*\d+)(?:.*to\s+([^.]+))?", re.IGNORECASE)
    CREDIT_PATTERN = re.compile(r"(?i)(?:credited|deposited).*?(?:Rs\.?|INR)\s*([\d,]+\.?\d*).*?a/c\s*([xX]*\d+)(?:.*from\s+([^.]+))?", re.IGNORECASE)
    
    # Generic "Spent" pattern
    SPENT_PATTERN = re.compile(r"(?i)Spent\s*(?:Rs\.?|INR)\s*([\d,]+\.?\d*)\s*on\s*statcard\s*([xX]*\d+)(?:.*at\s+([^.]+))?", re.IGNORECASE)

    def can_handle(self, sender: str, message: str) -> bool:
        # Very broad check for now, can be refined to specific Sender IDs (e.g. AD-HDFC)
        return "debited" in message.lower() or "credited" in message.lower() or "spent" in message.lower()

    def parse(self, content: str) -> Optional[ParsedTransaction]:
        content = content.replace(",", "") # Remove commas from currency
        
        # Try Debit
        match = self.DEBIT_PATTERN.search(content)
        if match:
            amount = Decimal(match.group(1))
            account_mask = match.group(2)
            merchant = match.group(3).strip() if match.group(3) else "Unknown"
            return ParsedTransaction(
                amount=amount,
                date=datetime.now(), # In real parser, extract date from SMS or use received_at
                description=f"Debit at {merchant}",
                type="DEBIT",
                account_mask=account_mask,
                recipient=merchant,
                raw_message=content
            )

        # Try Spent (Credit Card usually)
        match = self.SPENT_PATTERN.search(content)
        if match:
            amount = Decimal(match.group(1))
            account_mask = match.group(2)
            merchant = match.group(3).strip() if match.group(3) else "Unknown"
            return ParsedTransaction(
                amount=amount,
                date=datetime.now(),
                description=f"Spent at {merchant}",
                type="DEBIT",
                account_mask=account_mask,
                recipient=merchant,
                raw_message=content
            )

        # Try Credit
        match = self.CREDIT_PATTERN.search(content)
        if match:
            amount = Decimal(match.group(1))
            account_mask = match.group(2)
            source = match.group(3).strip() if match.group(3) else "Unknown"
            return ParsedTransaction(
                amount=amount,
                date=datetime.now(),
                description=f"Credit from {source}",
                type="CREDIT",
                account_mask=account_mask,
                recipient=source,
                raw_message=content
            )
            
        return None
