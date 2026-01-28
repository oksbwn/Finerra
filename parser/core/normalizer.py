from typing import Optional, Dict
import re

class MerchantNormalizer:
    
    # Simple regex based aliases
    # In future, this can be loaded from DB
    ALIASES = {
        "Amazon": [r"AMZN", r"Amazon", r"AMAZON PAY"],
        "Swiggy": [r"SWIGGY", r"BUNDL TECHNOLOGIES"],
        "Zomato": [r"ZOMATO"],
        "Uber": [r"UBER"],
        "Ola": [r"ANI TECHNOLOGIES", r"OLA"],
        "Starbucks": [r"TATA STARBUCKS"],
        "Netflix": [r"NETFLIX"],
        "Apple": [r"APPLE\.COM", r"ITUNES"],
        "Google": [r"GOOGLE", r"GOOGLE PLAY"],
        "UPI": [r"UPI", r"IMPS", r"NEFT"] 
    }

    @staticmethod
    def normalize(raw_merchant: str) -> str:
        if not raw_merchant: return "Unknown"
        
        raw_upper = raw_merchant.upper()
        
        # 1. Alias Lookup
        for clean_name, patterns in MerchantNormalizer.ALIASES.items():
            for pattern in patterns:
                if re.search(pattern, raw_merchant, re.IGNORECASE):
                    return clean_name
        
        # 2. Cleanup (remove common noise)
        # Remove "UPI-", "POS-", "VPS-" prefixes
        clean = re.sub(r"^(UPI|POS|VPS|ATW|ATM)-?", "", raw_upper)
        # Remove trailing locatons/IDs like "MUMBAI", "12345"
        # Heuristic: if it looks like a merchant + ID, keep merchant
        
        return clean.strip().title()
