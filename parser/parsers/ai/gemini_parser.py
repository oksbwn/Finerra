from google import genai
from google.genai import types
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import json
from parser.db.models import AIConfig
from parser.schemas.transaction import Transaction, TransactionType, AccountInfo, MerchantInfo
from datetime import datetime
from decimal import Decimal

class GeminiParser:
    def __init__(self, db: Session):
        self.db = db
        self.config = self._get_config()

    def _get_config(self) -> Optional[AIConfig]:
        return self.db.query(AIConfig).filter(AIConfig.is_enabled == True).first()

    def parse(self, content: str, source: str) -> Optional[Transaction]:
        if not self.config or not self.config.api_key_enc:
            return None

        # New google-genai client
        client = genai.Client(api_key=self.config.api_key_enc)
        
        config = types.GenerateContentConfig(
            temperature=0.1,
            top_p=1,
            top_k=32,
            max_output_tokens=1024,
            response_mime_type="application/json",
        )

        model_id = self.config.model_name or "gemini-1.5-flash"

        # Standard Prompt
        prompt = f"""
        You are a precise financial parser. Extract transaction details from the following {source} message.
        Return ONLY valid JSON.
        
        Input: "{content}"
        
        Required JSON Structure:
        {{
            "amount": float,
            "type": "DEBIT" or "CREDIT",
            "date": "YYYY-MM-DD",
            "currency": "INR" (default),
            "account_mask": "1234" (last 4 digits or null),
            "bank_name": "HDFC" (or null),
            "merchant": "Amazon" (clean name),
            "description": "raw description"
        }}
        
        Rules:
        1. If date is missing/relative (e.g. 'today', 'yesterday'), calculate it based on today's reference: {datetime.now().strftime('%Y-%m-%d')}.
        2. ALWAYS return date in ISO format (YYYY-MM-DD). Convert '28-03-24' to '2024-03-28'.
        3. For 'merchant', extract the actual entity name (e.g. 'Uber', 'Zomato').
        4. If unable to extract strictly, return null.
        """

        try:
            response = client.models.generate_content(
                model=model_id,
                contents=prompt,
                config=config
            )
            text = response.text.strip()
            # Clean potential markdown code blocks
            if text.startswith("```json"):
                text = text[7:-3]
            elif text.startswith("```"):
                text = text[3:-3]
            
            data = json.loads(text)
            if not data: return None
            
            # Robust Date Parsing
            extracted_date = data.get("date")
            final_date = datetime.now()
            if extracted_date:
                try:
                    if "-" in extracted_date and len(extracted_date) == 10:
                        final_date = datetime.strptime(extracted_date, "%Y-%m-%d")
                    else:
                        from dateutil import parser as date_parser
                        final_date = date_parser.parse(extracted_date)
                except:
                    final_date = datetime.now()

            # Map to Schema
            return Transaction(
                amount=Decimal(str(data.get("amount", 0))),
                type=TransactionType(data.get("type", "DEBIT").upper()),
                date=final_date,
                currency=data.get("currency", "INR"),
                account=AccountInfo(
                    mask=data.get("account_mask"), 
                    provider=data.get("bank_name")
                ),
                merchant=MerchantInfo(
                    raw=data.get("description") or data.get("merchant") or "Unknown", 
                    cleaned=data.get("merchant") or "Unknown"
                ),
                description=data.get("description") or content,
                recipient=data.get("merchant") or "Unknown",
                raw_message=content
            )

        except Exception as e:
            print(f"AI Parse Error: {e}")
            return None
