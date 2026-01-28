import re
from typing import Optional, Dict, Any
from parser.parsers.base import BaseParser
from parser.schemas.transaction import Transaction, TransactionType, AccountInfo, MerchantInfo
from datetime import datetime
from decimal import Decimal

class SbiSmsParser(BaseParser):
    def __init__(self):
        super().__init__("SbiSmsParser", "SMS")
        # Example: "Txn of Rs.100.00 on SBI A/c XX1234 at MERCHANT on 13Jan26. Ref: 123"
        self.txn_pattern = re.compile(
            r"(?i)(?:Txn\s*of|INR|Rs\.?)\s*([\d,.]+).*?A/c\s*([^\s]*?\d+)\s+at\s+(.*?)\s+on\s+(\d{1,2}[A-Z]{3}\d{2,4}|\d{1,2}-\d{1,2}-\d{2,4})(?:.*?[Rr]ef[:\.\s-]+([^\s\.]+))?",
            re.IGNORECASE
        )

    def can_handle(self, content: str, sender: Optional[str] = None) -> bool:
        if sender and "SBI" in sender.upper(): return True
        return "sbi" in content.lower()

    def parse(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[Transaction]:
        clean_content = " ".join(content.split())
        match = self.txn_pattern.search(clean_content)
        if match:
            amount = self._clean_amount(match.group(1))
            account_mask = match.group(2)
            merchant_raw = match.group(3).strip()
            date_str = match.group(4)
            ref_id = match.group(5)
            
            return self._create_txn(amount, merchant_raw, account_mask, date_str, "DEBIT", clean_content, ref_id)
        return None

    def _create_txn(self, amount, recipient, account_mask, date_str, type_str, raw, ref_id):
        txn_date = datetime.now()
        formats = ["%d%b%y", "%d%b%Y", "%d-%m-%y", "%d-%m-%Y"]
        for fmt in formats:
            try:
                txn_date = datetime.strptime(date_str, fmt)
                break
            except: continue
        
        return Transaction(
            amount=amount,
            type=TransactionType(type_str),
            date=txn_date,
            account=AccountInfo(mask=account_mask, provider="SBI"),
            merchant=MerchantInfo(raw=recipient, cleaned=recipient),
            description=recipient,
            ref_id=ref_id,
            raw_message=raw
        )
