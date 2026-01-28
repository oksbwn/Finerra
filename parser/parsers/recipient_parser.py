import re
from typing import Optional

class RecipientParser:
    """
    Dedicated logic for extracting merchant, recipient, or source names 
    from complex bank transaction descriptions.
    """

    @staticmethod
    def extract(description: str) -> Optional[str]:
        """
        Extract recipient/merchant name from transaction description.
        Informed by Indian bank patterns: UPI, IMPS, NEFT, Salary, Fund Transfers.
        """
        if not description:
            return None
        
        desc = description.strip()
        desc_upper = desc.upper()
        
        # Helper to clean a string from common junk
        def clean_name(name: str) -> str:
            if not name: return ""
            # Remove "VPA", "TO VPA", "VPA-", "VPA/" prefixes
            name = re.sub(r'^(VPA|TO VPA)[-/ ]+', '', name, flags=re.IGNORECASE)
            # Remove trailing numbers/IDs (e.g. -116522, -1341)
            name = re.sub(r'[- ]\d+$', '', name)
            # Remove titles
            name = re.sub(r'^(MR|MS|MRS|DR|PROF)\.?\s+', '', name, flags=re.IGNORECASE)
            # Remove common suffixes like @OKAXIS, @YBL, @ICICI etc
            name = re.sub(r'@[A-Z0-9.\-_]{3,}', '', name, flags=re.IGNORECASE)
            return name.strip()

        # Helper to check if a string looks like a random ID or masked field
        def is_junk_id(s: str) -> bool:
            # Masked with X's (e.g. XXXXXXXXXXXX1341)
            if re.search(r'X{3,}', s, re.IGNORECASE): return True
            # Purely numeric and long (e.g. 116522638546)
            s_clean = re.sub(r'[^0-9]', '', s)
            if s_clean.isdigit() and len(s_clean) > 6: return True
            # Too short to be a name
            if len(s.strip()) < 3: return True
            # Common bank boilerplate words
            if s.upper() in {'DR', 'CR', 'TO', 'BY', 'FROM', 'IB', 'SS', 'UPI', 'IMPS'}: return True
            return False

        # 1. UPI/IMPS/NEFT/RTGS with separators (- or /)
        # Patterns like: UPI-CHEQ DIGITAL PRIVATE-CHEQ1@YESBANK-YE
        # IMPS-600120935098-PALLABINEE PANDA-IBKL-XXX
        for prefix in ['UPI', 'IMPS', 'NEFT', 'RTGS']:
            if desc_upper.startswith(prefix):
                # Split by - or /
                parts = re.split(r'[-/]', desc)
                # Filter out the prefix itself and empty bits
                content_parts = [p.strip() for p in parts if p.upper() != prefix and p.strip()]
                
                # Special handling for IMPS: usually ID-NAME-BANK
                if prefix == 'IMPS' and len(content_parts) >= 2:
                    for p in content_parts:
                        if not is_junk_id(p): return clean_name(p)[:100]
                
                # General check for all parts in order
                for p in content_parts:
                    if not is_junk_id(p):
                        return clean_name(p)[:100]

        # 2. SALARY with numeric prefix (e.g. 5200073603852SALARY FOR THE MONTH DEC)
        salary_match = re.search(r'\d{5,}(SALARY.*)', desc, re.IGNORECASE)
        if salary_match:
            return salary_match.group(1).strip()[:100]

        # 3. INTERNET BANKING / FUND TRANSFER (e.g. IB SS FUNDS TRANSFER DR-55000008469767)
        if 'FUNDS TRANSFER' in desc_upper:
            # Take words before DR/CR or IDs
            words = desc.split()
            meaningful = []
            for w in words:
                w_up = w.upper()
                if w_up in {'IB', 'SS', 'DR', 'CR', 'TO', 'TRANSFER', 'FUNDS'} or re.search(r'\d', w):
                    continue
                meaningful.append(w)
            if meaningful:
                return " ".join(meaningful[:3])[:100]

        # 4. Standard POS/ATM/CARD patterns
        card_match = re.search(r'(?:POS|ATM|WDL|CARD|PURCHASE|SHOPPING|ECOM)(?:\s+|-|/)([^ 0-9/-][^0-9/-]*)', desc, re.IGNORECASE)
        if card_match:
            res = clean_name(card_match.group(1))
            if len(res) > 2: return res[:100]

        # 5. Fallback word-based cleaning
        words = desc.split()
        skip_words = {
            'UPI', 'IMPS', 'NEFT', 'RTGS', 'POS', 'ATM', 'WDL', 'CASH', 'TRANSFER',
            'FUND', 'FUNDS', 'PAY', 'PAYMENT', 'TO', 'BY', 'FROM', 'THE', 'DEBIT',
            'CREDIT', 'PURCHASE', 'SALE', 'ONLINE', 'ECOM', 'CARD', 'NET', 'BANK',
            'IB', 'SS', 'DR', 'CR', 'CHEQ', 'VPA' 
        }
        filtered = [w for w in words if w.upper() not in skip_words and not re.search(r'\d', w)]
        
        if filtered:
            return clean_name(" ".join(filtered[:3]))[:100]
            
        return None
