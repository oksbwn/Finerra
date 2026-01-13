import re
from typing import Optional
from datetime import datetime
from decimal import Decimal
from backend.app.modules.ingestion.base import BaseSmsParser, BaseEmailParser, ParsedTransaction
from backend.app.modules.ingestion.parsers.recipient_parser import RecipientParser

class KotakSmsParser(BaseSmsParser):
    """
    Parser for Kotak Bank SMS Alerts.
    """
    # Example: "Rs. 100.00 debited from A/c XX1234 on 13-01-26 to VPA MERCHANT. Ref: 123"
    DEBIT_PATTERN = re.compile(
        r"(?i)(?:Rs\.?|INR)\s*([\d,]+\.?\d*)\s*debited\s*from\s*A/c\s*(?:.*?|x*|X*)(\d+)\s*on\s*(\d{2}-\d{2}-\d{2,4})\s*to\s*(.*?)(?:\.\s*Ref[:\.\s-]+(\w+))?",
        re.IGNORECASE
    )
    
    # Example: "Spent Rs. 100.00 on Kotak Card XX1234 at MERCHANT on 13-01-26. Ref: 123"
    SPENT_PATTERN = re.compile(
        r"(?i)Spent\s*(?:Rs\.?|INR)\s*([\d,]+\.?\d*)\s*on\s*Kotak\s*.*?(?:Card|A/c)\s*([xX]*\d+)\s*at\s*(.*?)\s*on\s*(\d{2}-\d{2}-\d{2,4})(?:.*?[Rr]ef[:\.\s-]+(\w+))?",
        re.IGNORECASE
    )

    def can_handle(self, sender: str, message: str) -> bool:
        return "kotak" in sender.lower() or "kotak" in message.lower()

    def parse(self, content: str) -> Optional[ParsedTransaction]:
        clean_content = " ".join(content.split())
        
        # 1. Try Debit
        match = self.DEBIT_PATTERN.search(clean_content)
        if match:
            ref = match.group(5).strip() if match.group(5) else None
            return self._create_txn(Decimal(match.group(1).replace(",", "")), match.group(4), match.group(2), match.group(3), "DEBIT", content, ref, "SMS")

        # 2. Try Spent
        match = self.SPENT_PATTERN.search(clean_content)
        if match:
            ref = match.group(5).strip() if match.group(5) else None
            return self._create_txn(Decimal(match.group(1).replace(",", "")), match.group(3), match.group(2), match.group(4), "DEBIT", content, ref, "SMS")

        return None

    def _create_txn(self, amount, recipient, account_mask, date_str, type_str, raw, ref_id, source):
        try:
            formats = ["%d-%m-%y", "%d-%m-%Y", "%d/%m/%y", "%d/%m/%Y"]
            txn_date = None
            for fmt in formats:
                try:
                    txn_date = datetime.strptime(date_str, fmt)
                    break
                except: continue
            if not txn_date: txn_date = datetime.now()
        except:
            txn_date = datetime.now()
            
        clean_recipient = RecipientParser.extract(recipient)
        return ParsedTransaction(
            amount=amount,
            date=txn_date,
            description=f"Kotak: {clean_recipient or recipient}",
            type=type_str,
            account_mask=account_mask,
            recipient=clean_recipient,
            ref_id=ref_id,
            raw_message=raw,
            source=source
        )

class KotakEmailParser(BaseEmailParser):
    """
    Parser for Kotak Bank Email Alerts.
    """
    REF_PATTERN = re.compile(r"(?i)(?:Ref|UTR|TXN#|Ref No)[:\.\s-]+(\w{3,})")

    def can_handle(self, subject: str, body: str) -> bool:
        combined = (subject + " " + body).lower()
        return "kotak" in combined and any(k in combined for k in ["transaction", "spent", "debited", "alert", "upi"])

    def parse(self, content: str) -> Optional[ParsedTransaction]:
        clean_content = " ".join(content.split())
        
        if "kotak" in clean_content.lower():
            amt_match = re.search(r"(?i)(?:INR|Rs\.?)\s*([\d\.]+(?:,\d{3})*)", clean_content)
            if amt_match:
                amt_str = amt_match.group(1).replace(",", "")
                date_match = re.search(r"(\d{2}-\d{2}-\d{2,4})", clean_content)
                if date_match:
                    merchant_match = re.search(r"(?i)(?:at|to|towards|for|on)\s+([A-Z0-9\s*]{3,30}?)(?:\s+on|\s+at|\.|\s+from|\s+using)", clean_content)
                    merchant = merchant_match.group(1).strip() if merchant_match else "Unknown Merchant"
                    mask_match = re.search(r"(?i)(?:A/c|card|XX)\s*(\d{4,})", clean_content)
                    mask = mask_match.group(1) if mask_match else "XXXX"
                    
                    ref_match = self.REF_PATTERN.search(clean_content)
                    ref_id = ref_match.group(1).strip() if ref_match else None
                    
                    return self._create_txn(Decimal(amt_str), merchant, mask, date_match.group(1), "DEBIT", content, ref_id)

        return None

    def _create_txn(self, amount, recipient, account_mask, date_str, type_str, raw, ref_id):
        try:
            formats = ["%d-%m-%y", "%d-%m-%Y", "%d/%m/%y", "%d/%m/%Y"]
            txn_date = None
            for fmt in formats:
                try:
                    txn_date = datetime.strptime(date_str, fmt)
                    break
                except: continue
            if not txn_date: txn_date = datetime.now()
        except:
            txn_date = datetime.now()
            
        clean_recipient = RecipientParser.extract(recipient)
        return ParsedTransaction(
            amount=amount,
            date=txn_date,
            description=f"Kotak: {clean_recipient or recipient}",
            type=type_str,
            account_mask=account_mask,
            recipient=clean_recipient,
            ref_id=ref_id,
            raw_message=raw,
            source="EMAIL"
        )
