import re
from typing import Optional
from datetime import datetime
from decimal import Decimal
from backend.app.modules.ingestion.base import BaseSmsParser, BaseEmailParser, ParsedTransaction
from backend.app.modules.ingestion.parsers.recipient_parser import RecipientParser

class IciciSmsParser(BaseSmsParser):
    """
    Parser for ICICI Bank SMS Alerts.
    """
    # Example: "INR 869.00 spent using ICICI Bank Card XX0004 on 23-Sep-24 on IND*Amazon. Avl Limit: INR 2,39,131.00"
    SPENT_PATTERN = re.compile(
        r"(?i)(?:INR|Rs\.?)\s*([\d,]+\.?\d*)\s*spent\s*using\s*ICICI\s*Bank\s*.*?(?:Card|A/c)\s*([xX]*\d+)\s*on\s*(\d{2}-[a-z]{3}-\d{2,4})\s*on\s*(.*?)\.\s*(?:Ref[:\.\s-]+(\w+))?",
        re.IGNORECASE
    )
    
    # Example: "Your A/c XX123 is debited for INR 500.00 on 23-Sep-24. Info: UPI-Zomato-123. Avl Bal: INR 1,000.00"
    DEBIT_PATTERN = re.compile(
        r"(?i)A/c\s*([xX]*\d+)\s*is\s*debited\s*for\s*(?:INR|Rs\.?)\s*([\d,]+\.?\d*)\s*on\s*(\d{2}-[a-z]{3}-\d{2,4})\.\s*Info:\s*(.*?)(?:\.\s*Ref[:\.\s-]+(\w+))?",
        re.IGNORECASE
    )

    def can_handle(self, sender: str, message: str) -> bool:
        return "icici" in sender.lower() or "icici" in message.lower()

    def parse(self, content: str, date_hint: Optional[datetime] = None) -> Optional[ParsedTransaction]:
        clean_content = " ".join(content.split())
        
        # 1. Try Spent
        match = self.SPENT_PATTERN.search(clean_content)
        if match:
            amount = Decimal(match.group(1).replace(",", ""))
            account_mask = match.group(2)
            date_str = match.group(3)
            recipient = match.group(4).strip()
            ref_id = match.group(5)
            return self._create_txn(amount, recipient, account_mask, date_str, "DEBIT", content, ref_id, "SMS", date_hint)

        # 2. Try Debit
        match = self.DEBIT_PATTERN.search(clean_content)
        if match:
            account_mask = match.group(1)
            amount = Decimal(match.group(2).replace(",", ""))
            date_str = match.group(3)
            recipient = match.group(4).strip()
            ref_id = match.group(5)
            return self._create_txn(amount, recipient, account_mask, date_str, "DEBIT", content, ref_id, "SMS", date_hint)

        return None

    def _create_txn(self, amount, recipient, account_mask, date_str, type_str, raw, ref_id, source, date_hint=None):
        try:
            # ICICI often uses 23-Sep-24
            txn_date = datetime.strptime(date_str, "%d-%b-%y")
        except:
            try:
                txn_date = datetime.strptime(date_str, "%d-%b-%Y")
            except:
                txn_date = date_hint or datetime.now()
            
        clean_recipient = RecipientParser.extract(recipient)
        return ParsedTransaction(
            amount=amount,
            date=txn_date,
            description=f"ICICI: {clean_recipient or recipient}",
            type=type_str,
            account_mask=account_mask,
            recipient=clean_recipient,
            ref_id=ref_id,
            raw_message=raw,
            source=source
        )

class IciciEmailParser(BaseEmailParser):
    """
    Parser for ICICI Bank Email Alerts.
    """
    REF_PATTERN = re.compile(r"(?i)(?:Ref|UTR|TXN#|Ref No)[:\.\s-]+(\w{3,})")

    def can_handle(self, subject: str, body: str) -> bool:
        combined = (subject + " " + body).lower()
        return "icici" in combined and any(k in combined for k in ["transaction", "spent", "debited", "alert", "upi"])

    def parse(self, content: str, date_hint: Optional[datetime] = None) -> Optional[ParsedTransaction]:
        clean_content = " ".join(content.split())
        
        # Use common patterns or loose fallback
        # ICICI emails are quite varied, so we leverage the loose matcher with ICICI specific keywords
        if "icici" in clean_content.lower():
            amt_match = re.search(r"(?i)(?:INR|Rs\.?)\s*([\d\.]+(?:,\d{3})*)", clean_content)
            if amt_match:
                amt_str = amt_match.group(1).replace(",", "")
                # Flexible Date Support: 13-Jan-24, 13/01/2024, 13-01-2024
                date_match = re.search(r"(\d{2}[-/ ](?:[a-zA-Z]{3,9}|\d{2})[-/ ]\d{2,4})", clean_content)
                if date_match:
                    date_val = date_match.group(1)
                    merchant_match = re.search(r"(?i)(?:at|to|towards|for|on)\s+([A-Z0-9\s*]{3,30}?)(?:\s+on|\s+at|\.|\s+from|\s+using)", clean_content)
                    merchant = merchant_match.group(1).strip() if merchant_match else "Unknown Merchant"
                    # Improved Mask: A/c, card, Card, XX, xxxx ending in 1234
                    mask_match = re.search(r"(?i)(?:A/c|Account|card|Card|XX|xx|ending in)\s*.*?(?:x*|X*|\*)*(\d{4,})", clean_content)
                    mask = mask_match.group(1) if mask_match else "XXXX"
                    
                    ref_match = self.REF_PATTERN.search(clean_content)
                    ref_id = ref_match.group(1).strip() if ref_match else None
                    
                    return self._create_txn(Decimal(amt_str), merchant, mask, date_val, "DEBIT", content, ref_id, date_hint)

        return None

    def _create_txn(self, amount, recipient, account_mask, date_str, type_str, raw, ref_id, date_hint=None):
        try:
            formats = ["%d-%b-%y", "%d-%b-%Y", "%d-%m-%y", "%d-%m-%Y", "%d/%m/%y", "%d/%m/%Y", "%d %b %y", "%d %B %Y"]
            txn_date = None
            for fmt in formats:
                try:
                    txn_date = datetime.strptime(date_str, fmt)
                    break
                except: continue
            if not txn_date: txn_date = date_hint or datetime.now()
        except:
            txn_date = datetime.now()
                
        clean_recipient = RecipientParser.extract(recipient)
        return ParsedTransaction(
            amount=amount,
            date=txn_date,
            description=f"ICICI: {clean_recipient or recipient}",
            type=type_str,
            account_mask=account_mask,
            recipient=clean_recipient,
            ref_id=ref_id,
            raw_message=raw,
            source="EMAIL"
        )
