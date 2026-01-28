import re
from typing import Optional, Dict, Any
from parser.parsers.base import BaseParser
from parser.schemas.transaction import Transaction, TransactionType, AccountInfo, MerchantInfo
from datetime import datetime
from decimal import Decimal

class HdfcSmsParser(BaseParser):
    def __init__(self):
        super().__init__("HdfcSmsParser", "SMS")
        # Example: Rs.1200 debited from a/c 1234 on 28-01-26 to AMZN Pay. Ref 123
        self.patterns = [
            r"Rs\.?\s*([\d,.]+)\s*(?:debited|spent).*?a/c\s*([^\s]+)\s*on\s*([\d-]+)\s*to\s*([^.]+)",
            r"Rs\.?\s*([\d,.]+)\s*spent\s*on\s*([\d-]+)\s*at\s*([^.]+)"
        ]

    def can_handle(self, content: str, sender: Optional[str] = None) -> bool:
        if sender and "HDFC" in sender.upper(): return True
        return "hdfc" in content.lower()

    def parse(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[Transaction]:
        for pattern in self.patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                groups = match.groups()
                # Naive mapping based on regex group count
                amount = self._clean_amount(groups[0])
                
                # Try to parse date
                date_str = groups[2] if len(groups) > 2 else groups[1]
                txn_date = datetime.now()
                try:
                    txn_date = datetime.strptime(date_str, "%d-%m-%y")
                except:
                    pass

                merchant = groups[3].strip() if len(groups) > 3 else groups[2].strip()
                
                # Logic to determine account if present
                acc_mask = groups[1] if len(groups) > 3 else "XXXX"
                
                return Transaction(
                    amount=amount,
                    type=TransactionType.DEBIT,
                    date=txn_date,
                    account=AccountInfo(mask=acc_mask, provider="HDFC Bank"),
                    merchant=MerchantInfo(raw=merchant, cleaned=merchant),
                    description=merchant,
                    raw_message=content
                )
        return None
