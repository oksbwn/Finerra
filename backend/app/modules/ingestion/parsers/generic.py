import re
from typing import Optional
from datetime import datetime
from decimal import Decimal
from backend.app.modules.ingestion.base import BaseSmsParser, BaseEmailParser, ParsedTransaction
from backend.app.modules.ingestion.parsers.recipient_parser import RecipientParser

class GenericSmsParser(BaseSmsParser):
    """
    Parser for common Indian bank SMS formats.
    """
    DEBIT_PATTERN = re.compile(r"(?i)(?:Rs\.?|INR)\s*([\d,]+\.?\d*)\s*debited\s*from.*?a/c\s*([xX]*\d+)(?:.*to\s+([^.]+))?", re.IGNORECASE)
    CREDIT_PATTERN = re.compile(r"(?i)(?:credited|deposited).*?(?:Rs\.?|INR)\s*([\d,]+\.?\d*).*?a/c\s*([xX]*\d+)(?:.*from\s+([^.]+))?", re.IGNORECASE)
    SPENT_PATTERN = re.compile(r"(?i)Spent\s*(?:Rs\.?|INR)\s*([\d,]+\.?\d*)\s*on\s*.*?card\s*([xX]*\d+)(?:.*at\s+([^.]+))?", re.IGNORECASE)
    REF_PATTERN = re.compile(r"(?i)(?:Ref|UTR|TXN#|Ref No)[:\.\s-]+(\w{3,})")

    def can_handle(self, sender: str, message: str) -> bool:
        keywords = ["debited", "credited", "spent", "spent at", "payment", "txn", "upi"]
        return any(k in message.lower() for k in keywords)

    def parse(self, content: str) -> Optional[ParsedTransaction]:
        clean_content = " ".join(content.split())
        clean_content_no_comma = clean_content.replace(",", "")
        
        def get_ref():
            match = self.REF_PATTERN.search(clean_content)
            return match.group(1).strip() if match else None

        # 1. Try Debit
        match = self.DEBIT_PATTERN.search(clean_content_no_comma)
        if match:
            return self._create_txn(Decimal(match.group(1)), match.group(3) or "Unknown", match.group(2), "DEBIT", content, get_ref(), "SMS")

        # 2. Try Spent
        match = self.SPENT_PATTERN.search(clean_content_no_comma)
        if match:
            return self._create_txn(Decimal(match.group(1)), match.group(3) or "Unknown", match.group(2), "DEBIT", content, get_ref(), "SMS")

        # 3. Try Credit
        match = self.CREDIT_PATTERN.search(clean_content_no_comma)
        if match:
            return self._create_txn(Decimal(match.group(1)), match.group(3) or "Unknown", match.group(2), "CREDIT", content, get_ref(), "SMS")

        return None

    def _create_txn(self, amount, recipient, account_mask, type_str, raw, ref_id, source):
        clean_recipient = RecipientParser.extract(recipient)
        return ParsedTransaction(
            amount=amount,
            date=datetime.now(),
            description=f"Ingested: {clean_recipient or recipient}",
            type=type_str,
            account_mask=account_mask,
            recipient=clean_recipient,
            ref_id=ref_id,
            raw_message=raw,
            source=source
        )

class GenericEmailParser(BaseEmailParser):
    """
    Parser for common bank email formats.
    """
    SPEND_PATTERN = re.compile(r"(?i)spend\s*of\s*(?:Rs\.?|INR)\s*([\d,]+\.?\d*)\s*at\s*(.*?)\s*on\s*A/c\s*(?:.*?|x*|X*)(\d+)\s*on\s*(\d{2}-\d{2}-\d{2,4})", re.IGNORECASE)
    DEBIT_PATTERN = re.compile(r"(?i)A/c\s*(?:.*?|x*|X*)(\d+)\s*has\s*been\s*debited\s*for\s*(?:Rs\.?|INR)\s*([\d,]+\.?\d*)\s*on\s*(\d{2}-\d{2}-\d{2,4})\s*towards\s*(.*?)\.", re.IGNORECASE)
    GENERIC_ALERT_PATTERN = re.compile(r"(?i)A/c\s*(?:.*?|x*|X*)(\d+):?\s*(?:Rs\.?|INR)\s*([\d,]+\.?\d*)\s*(?:spent|debited|spent\s*at)\s*(?:at|to)?\s*(.*?)\s*on\s*(\d{2}-\d{2}-\d{2,4})", re.IGNORECASE)
    REF_PATTERN = re.compile(r"(?i)(?:Ref|UTR|TXN#|Ref No)[:\.\s-]+(\w{3,})")

    def can_handle(self, subject: str, body: str) -> bool:
        combined = (subject + " " + body).lower()
        keywords = ["transaction", "spent", "debited", "credited", "payment", "alert", "txn", "upi", "vpa"]
        return any(k in combined for k in keywords)

    def parse(self, content: str) -> Optional[ParsedTransaction]:
        clean_content = " ".join(content.split())
        clean_content_no_comma = clean_content.replace(",", "")
        
        def get_ref():
            match = self.REF_PATTERN.search(clean_content)
            return match.group(1).strip() if match else None

        # 1. Try Spend
        match = self.SPEND_PATTERN.search(clean_content_no_comma)
        if match:
            return self._create_txn(Decimal(match.group(1)), match.group(2), match.group(3), match.group(4), "DEBIT", content, get_ref())

        # 2. Try Debit
        match = self.DEBIT_PATTERN.search(clean_content_no_comma)
        if match:
            return self._create_txn(Decimal(match.group(2)), match.group(4), match.group(1), match.group(3), "DEBIT", content, get_ref())

        # 3. Try Generic Alert
        match = self.GENERIC_ALERT_PATTERN.search(clean_content_no_comma)
        if match:
            return self._create_txn(Decimal(match.group(2)), match.group(3), match.group(1), match.group(4), "DEBIT", content, get_ref())

        # Loose fallback
        if any(k in clean_content.lower() for k in ["transaction", "txn", "upi", "vpa"]):
            amt_match = re.search(r"(?i)(?:Rs\.?|INR)\s*([\d\.]+(?:,\d{3})*)", clean_content)
            if amt_match:
                amt_str = amt_match.group(1).replace(",", "")
                date_match = re.search(r"(\d{2}[-/]\d{2}[-/]\d{2,4})", clean_content)
                if date_match:
                    merchant_match = re.search(r"(?i)(?:at|to|towards|for)\s+([A-Z0-9\s*]{3,30}?)(?:\s+on|\s+at|\.|\s+from|\s+using)", clean_content)
                    merchant = merchant_match.group(1).strip() if merchant_match else "Unknown Merchant"
                    mask_match = re.search(r"(?i)(?:A/c|card|XX)\s*(\d{4,})", clean_content)
                    mask = mask_match.group(1) if mask_match else "XXXX"
                    return self._create_txn(Decimal(amt_str), merchant, mask, date_match.group(1), "DEBIT", content, get_ref())

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
            description=f"Alert: {clean_recipient or recipient}",
            type=type_str,
            account_mask=account_mask,
            recipient=clean_recipient,
            ref_id=ref_id,
            raw_message=raw,
            source="EMAIL"
        )
