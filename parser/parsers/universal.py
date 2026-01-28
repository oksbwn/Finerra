import pandas as pd
import io
from typing import List, Dict, Optional, Any
from datetime import datetime
from decimal import Decimal
from parser.schemas.transaction import Transaction, TransactionType, AccountInfo, MerchantInfo

class UniversalParser:
    @staticmethod
    def analyze(file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Analyze file to detect header row and return preview.
        """
        try:
            # Read first 30 rows raw (no header) to scan
            if filename.lower().endswith('.csv'):
                # Read with 'header=None' to get raw rows
                df_raw = pd.read_csv(io.BytesIO(file_content), header=None, nrows=30)
            elif filename.lower().endswith(('.xls', '.xlsx')):
                df_raw = pd.read_excel(io.BytesIO(file_content), header=None, nrows=30)
            else:
                raise ValueError("Unsupported file format")
            
            # Heuristic: Count intersections with keywords
            keywords = {'date', 'txn', 'transaction', 'valuedate', 'description', 
                        'desc', 'particulars', 'narration', 'remark', 'amount', 
                        'debit', 'credit', 'dr', 'cr', 'balance', 'bal', 'limit', 'ref'}
            
            best_idx = 0
            max_score = 0
            detected_headers = []
            
            for idx, row in df_raw.iterrows():
                # Convert row values to string and lower
                row_str = [str(val).lower().strip() for val in row.values if pd.notna(val)]
                score = len(set(row_str).intersection(keywords))
                
                # Bonus for 'date' and 'amount' as they are critical
                if any('date' in s for s in row_str): score += 1
                if any('amount' in s or 'debit' in s for s in row_str): score += 1
                
                if score > max_score:
                    max_score = score
                    best_idx = idx
                    # Original values as headers
                    detected_headers = [str(val).strip() for val in row.values if pd.notna(val)]

            # Fallback: if score is too low, might be index 0
            if max_score < 1:
                best_idx = 0
                detected_headers = [str(val).strip() for val in df_raw.iloc[0].values if pd.notna(val)]

            # Get Preview Data
            if filename.lower().endswith('.csv'):
                df_preview = pd.read_csv(io.BytesIO(file_content), header=best_idx, nrows=5)
            else:
                df_preview = pd.read_excel(io.BytesIO(file_content), header=best_idx, nrows=5)
            
            # Sanitize preview for JSON
            preview_rows = []
            for _, split_row in df_preview.iterrows():
                clean_row = {}
                for col in df_preview.columns:
                    val = split_row[col]
                    if pd.isna(val): val = ""
                    elif isinstance(val, (datetime, pd.Timestamp)): val = str(val)
                    clean_row[str(col)] = val
                preview_rows.append(clean_row)

            return {
                "header_row_index": int(best_idx),
                "headers": detected_headers,
                "preview": preview_rows
            }

        except Exception as e:
            raise ValueError(f"Analysis failed: {str(e)}")

    @staticmethod
    def parse(file_content: bytes, filename: str, mapping: Dict[str, str], header_row_index: int = 0, password: Optional[str] = None) -> List[Transaction]:
        """
        Parse CSV/Excel content using pandas and return unified Transaction objects.
        """
        try:
            # Detect format
            if filename.lower().endswith('.csv'):
                try:
                    df = pd.read_csv(io.BytesIO(file_content), header=header_row_index, on_bad_lines='skip')
                except:
                    df = pd.read_csv(io.BytesIO(file_content), encoding='utf-8-sig', header=header_row_index, on_bad_lines='skip')
            elif filename.lower().endswith(('.xls', '.xlsx')):
                # For password protected excel files, pandas does not support it directly.
                # Usually requires msoffcrypto-dot-py or similar.
                # For now, we pass it but standard pandas will fail if it's encrypted.
                df = pd.read_excel(io.BytesIO(file_content), header=header_row_index)
            else:
                raise ValueError("Unsupported file format")

            # Remove rows where ALL columns are NaN
            df.dropna(how='all', inplace=True)
            
            # Normalize Headers (strip whitespace)
            df.columns = df.columns.astype(str).str.strip()
            
            parsed_txns = []
            
            # Helper to safely get value
            def get_val(row, col):
                if col not in row: return None 
                if pd.isna(row.get(col)): return None
                return row.get(col)
            
            for idx, row in df.iterrows():
                try:
                    # 1. Date
                    date_col = mapping.get('date')
                    raw_date = get_val(row, date_col)
                    date_obj = UniversalParser._parse_date(raw_date)
                    if not date_obj: continue

                    # 2. Description
                    desc_col = mapping.get('description')
                    desc = str(get_val(row, desc_col) or "No Description")

                    # 3. Amount
                    amount = Decimal(0)
                    txn_type = TransactionType.DEBIT

                    if 'amount' in mapping:
                        amt_col = mapping['amount']
                        raw_amt = get_val(row, amt_col)
                        amount = UniversalParser._clean_amount(raw_amt)
                        if amount < 0:
                             txn_type = TransactionType.DEBIT
                             amount = abs(amount) # Store absolute
                        else:
                             # Default assumption if positive? Usually Credit, but depends on signed column
                             # If "Amount" column has -ve for debit, +ve for credit:
                             # But here we need to be careful. Let's assume Credit unless negative?
                             # Or use is_debit flag logic. 
                             # For now: -ve is DEBIT, +ve is CREDIT.
                             # If user provides separate Dr/Cr columns that's handled below.
                             txn_type = TransactionType.CREDIT

                    elif 'debit' in mapping and 'credit' in mapping:
                        raw_debit = get_val(row, mapping['debit'])
                        raw_credit = get_val(row, mapping['credit'])
                        
                        debit = UniversalParser._clean_amount(raw_debit)
                        credit = UniversalParser._clean_amount(raw_credit)
                        
                        if debit > 0:
                            amount = debit
                            txn_type = TransactionType.DEBIT
                        elif credit > 0:
                            amount = credit
                            txn_type = TransactionType.CREDIT
                        else:
                            continue
                    
                    if amount == 0: continue

                    # 4. Ref ID
                    ref_id = None
                    ref_col = mapping.get('reference') or mapping.get('ref')
                    if ref_col:
                        raw_ref = get_val(row, ref_col)
                        if raw_ref: ref_id = str(raw_ref).strip()
                    
                    # 5. Balance
                    balance_val = None
                    bal_col = mapping.get('balance')
                    if bal_col:
                         balance_val = UniversalParser._clean_amount(get_val(row, bal_col))

                    # Construct Transaction
                    txn = Transaction(
                        amount=amount,
                        type=txn_type,
                        date=date_obj,
                        account=AccountInfo(mask="XXXX", provider="Imported"),
                        merchant=MerchantInfo(raw=desc, cleaned=desc),
                        description=desc,
                        ref_id=ref_id,
                        balance=balance_val
                    )
                    parsed_txns.append(txn)

                except Exception:
                    continue
            
            return parsed_txns

        except Exception as e:
            raise ValueError(f"Failed to parse file: {str(e)}")

    @staticmethod
    def _parse_date(val: Any) -> Optional[datetime]:
        if pd.isna(val): return None
        if isinstance(val, (datetime, pd.Timestamp)): return val
        date_str = str(val).strip()
        formats = ["%d-%m-%Y", "%d/%m/%Y", "%d-%b-%Y", "%Y-%m-%d", "%Y/%m/%d"]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except: pass
        
        try:
             return pd.to_datetime(date_str, dayfirst=True).to_pydatetime()
        except: return None

    @staticmethod
    def _clean_amount(val) -> Decimal:
        if val is None: return Decimal(0)
        s = str(val).replace(",", "").replace(" ", "")
        # Handle 100 Cr / 100 Dr
        mult = 1
        if 'dr' in s.lower(): 
            s = s.lower().replace('dr', '')
            mult = -1 # Treat as negative for logic
        elif 'cr' in s.lower():
            s = s.lower().replace('cr', '')
        
        # Handle trailing/leading negative
        if s.endswith('-'): s = '-' + s[:-1]
        
        clean = ''.join(c for c in s if c.isdigit() or c == '.' or c == '-')
        try:
            return Decimal(clean) * mult
        except: return Decimal(0)
