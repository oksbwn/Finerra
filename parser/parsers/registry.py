from typing import List, Optional
from parser.parsers.base import BaseParser

class ParserRegistry:
    _sms_parsers: List[BaseParser] = []
    _email_parsers: List[BaseParser] = []

    @classmethod
    def register_sms(cls, parser: BaseParser):
        cls._sms_parsers.append(parser)

    @classmethod
    def register_email(cls, parser: BaseParser):
        cls._email_parsers.append(parser)
    
    @classmethod
    def get_sms_parsers(cls) -> List[BaseParser]:
        return cls._sms_parsers

    @classmethod
    def get_email_parsers(cls) -> List[BaseParser]:
        return cls._email_parsers
