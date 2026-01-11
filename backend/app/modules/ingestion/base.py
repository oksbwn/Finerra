from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

class ParsedTransaction(BaseModel):
    amount: Decimal
    date: datetime
    description: str
    type: str # DEBIT or CREDIT
    account_mask: Optional[str] = None # Last 4 digits if available
    merchant: Optional[str] = None
    category: Optional[str] = None
    ref_id: Optional[str] = None
    raw_message: str

class BaseParser(ABC):
    @abstractmethod
    def parse(self, content: str) -> Optional[ParsedTransaction]:
        """
        Parse raw content (SMS body or CSV row) into a structured transaction.
        Returns None if parsing fails or content is irrelevant.
        """
        pass

class BaseSmsParser(BaseParser):
    @abstractmethod
    def can_handle(self, sender: str, message: str) -> bool:
        """
        Determine if this parser can handle the given SMS.
        """
        pass
