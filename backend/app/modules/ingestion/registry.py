from datetime import datetime
from typing import List, Optional
from backend.app.modules.ingestion.base import BaseSmsParser, BaseEmailParser, ParsedTransaction

class SmsParserRegistry:
    _parsers: List[BaseSmsParser] = []

    @classmethod
    def register(cls, parser: BaseSmsParser):
        """Register a new parser instance."""
        cls._parsers.append(parser)

    @classmethod
    def parse(cls, sender: str, message: str) -> Optional[ParsedTransaction]:
        """
        Iterate through registered parsers and return the first successful result.
        """
        for parser in cls._parsers:
            if parser.can_handle(sender, message):
                print(f"Parser {parser.__class__.__name__} handling message from {sender}")
                return parser.parse(message)
        return None

class EmailParserRegistry:
    _parsers: List[BaseEmailParser] = []

    @classmethod
    def register(cls, parser: BaseEmailParser):
        """Register a new parser instance."""
        cls._parsers.append(parser)

    @classmethod
    def parse(cls, subject: str, body: str, date_hint: Optional[datetime] = None) -> Optional[ParsedTransaction]:
        """
        Iterate through registered parsers and return the first successful result.
        """
        for parser in cls._parsers:
            if parser.can_handle(subject, body):
                print(f"Email Parser {parser.__class__.__name__} handling email: {subject}")
                return parser.parse(body, date_hint)
        return None
