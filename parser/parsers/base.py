from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from parser.schemas.transaction import Transaction, TransactionType, AccountInfo, MerchantInfo
import re
from datetime import datetime
from decimal import Decimal

class BaseParser(ABC):
    def __init__(self, name: str, source: str):
        self.name = name
        self.source = source # SMS, EMAIL, etc.

    @abstractmethod
    def can_handle(self, content: str, sender: Optional[str] = None) -> bool:
        """
        Fast check to see if this parser should run.
        """
        pass

    @abstractmethod
    def parse(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[Transaction]:
        """
        Attempt to extract a transaction from the content.
        """
        pass

    def _clean_amount(self, amount_str: str) -> Decimal:
        """Helper to clean currency strings like 'Rs. 1,200.00'"""
        if not amount_str: return Decimal(0)
        clean = re.sub(r'[^\d.]', '', amount_str.replace(",", ""))
        try:
            return Decimal(clean)
        except:
            return Decimal(0)
