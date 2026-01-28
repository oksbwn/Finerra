import re
from typing import Optional, Dict, Any
from parser.parsers.base import BaseParser
from parser.schemas.transaction import Transaction, TransactionType, AccountInfo, MerchantInfo
from datetime import datetime
from decimal import Decimal

class IciciSmsParser(BaseParser):
    def __init__(self):
        super().__init__("IciciSmsParser", "SMS")
        # Example: "INR 869.00 spent using ICICI Bank Card XX0004 on 23-Sep-24 on IND*Amazon. Avl Limit: INR 2,39,131.00"
        self.spent_pattern = re.compile(
            r"(?i)(?:INR|Rs\.?)\s*([\d,]+\.?\d*)\s*spent\s*using\s*ICICI\s*Bank\s*.*?(?:Card|A/c)\s*([xX]*\d+)\s*on\s*(\d{2}-[a-z]{3}-\d{2,4})\s*on\s*(.*?)\.\s*(?:Ref[:\.\s-]+(\w+))?",
            re.IGNORECASE
        )
        # Example: "Your A/c XX123 is debited for INR 500.00 on 23-Sep-24. Info: UPI-Zomato-123. Avl Bal: INR 1,000.00"
        self.debit_pattern = re.compile(
            r"(?i)A/c\s*([xX]*\d+)\s*is\s*debited\s*for\s*(?:INR|Rs\.?)\s*([\d,]+\.?\d*)\s*on\s*(\d{2}-[a-z]{3}-\d{2,4})\.\s*Info:\s*(.*?)(?:\.\s*Ref[:\.\s-]+(\w+))?",
            re.IGNORECASE
        )

    def can_handle(self, content: str, sender: Optional[str] = None) -> bool:
        if sender and ("ICICI" in sender.upper() or "IPAY" in sender.upper()): return True
        return "icici" in content.lower()

    def parse(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[Transaction]:
        clean_content = " ".join(content.split())
        
        # 1. Try Spent
        match = self.spent_pattern.search(clean_content)
        if match:
            amount = self._clean_amount(match.group(1))
            account_mask = match.group(2)
            date_str = match.group(3)
            recipient = match.group(4).strip()
            ref_id = match.group(5)
            return self._create_txn(amount, recipient, account_mask, date_str, "DEBIT", clean_content, ref_id)

        # 2. Try Debit
        match = self.debit_pattern.search(clean_content)
        if match:
            account_mask = match.group(1)
            amount = self._clean_amount(match.group(2))
            date_str = match.group(3)
            recipient = match.group(4).strip()
            ref_id = match.group(5)
            return self._create_txn(amount, recipient, account_mask, date_str, "DEBIT", clean_content, ref_id)

        return None

    def _create_txn(self, amount, recipient, account_mask, date_str, type_str, raw, ref_id):
        try:
             # ICICI often uses 23-Sep-24
             txn_date = datetime.strptime(date_str, "%d-%b-%y")
        except:
             try:
                 txn_date = datetime.strptime(date_str, "%d-%b-%Y")
             except:
                 txn_date = datetime.now()
        
        return Transaction(
            amount=amount,
            type=TransactionType(type_str),
            date=txn_date,
            account=AccountInfo(mask=account_mask, provider="ICICI Bank"),
            merchant=MerchantInfo(raw=recipient, cleaned=recipient), # We skip RecipientParser for now, can implement later
            description=recipient,
            ref_id=ref_id,
            raw_message=raw
        )
