import re
from typing import Optional
from datetime import datetime
from decimal import Decimal
from backend.app.modules.ingestion.base import BaseSmsParser, ParsedTransaction

class HdfcParser(BaseSmsParser):
    # Sample: Sent Rs.70.00 From HDFC Bank A/C *5244 To Mr SIDHARTHA SWAIN On 09/01/26 Ref 116929657356 Not You? Call ...
    
    # Regex Breakdown:
    # Sent Rs\.([\d\.]+)        -> Amount
    # From HDFC Bank A/C \*(\d+) -> Mask
    # To (.*?)                  -> Payee (Non-greedy match until 'On')
    # On (\d{2}/\d{2}/\d{2})    -> Date
    # Ref (\d+)                 -> Ref ID

    PATTERN = re.compile(
        r"Sent Rs\.([\d\.]+) From HDFC Bank A/C \*(\d+) To (.*?) On (\d{2}/\d{2}/\d{2}) Ref (\d+)", 
        re.IGNORECASE
    )

    def can_handle(self, sender: str, message: str) -> bool:
        return "HDFC Bank" in message and "Ref" in message

    def parse(self, content: str) -> Optional[ParsedTransaction]:
        match = self.PATTERN.search(content)
        if match:
            amount_str = match.group(1)
            mask = match.group(2)
            payee = match.group(3).strip()
            date_str = match.group(4)
            ref_id = match.group(5)
            
            # Parse Date (09/01/26 -> DD/MM/YY)
            try:
                txn_date = datetime.strptime(date_str, "%d/%m/%y")
            except ValueError:
                txn_date = datetime.now()

            return ParsedTransaction(
                amount=Decimal(amount_str),
                date=txn_date,
                description=f"Sent to {payee}",
                type="DEBIT",
                account_mask=mask,
                merchant=payee,
                ref_id=ref_id,
                raw_message=content,
                # Map 'ref_id' to external_id logic inside service/router if needed
                # Base ParsedTransaction has ref_id, we should ensure it maps to external_id
            )
        return None
