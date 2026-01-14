import re
import json

class PatternGenerator:
    @staticmethod
    def generate_regex_and_config(raw_content: str, labels: dict):
        """
        Attempts to find labels in raw_content and generate a regex.
        Labels: {amount, date_str, account_mask, recipient, ref_id}
        """
        clean_content = " ".join(raw_content.split())
        escaped_content = re.escape(clean_content)
        
        mapping = {}
        group_idx = 1
        
        # We process fields from largest string to smallest or in logical order
        # to avoid partial matches (though re.escape handles some of it)
        
        fields = [
            ("amount", str(labels.get("amount"))),
            ("recipient", labels.get("recipient")),
            ("account_mask", labels.get("account_mask")),
            ("ref_id", labels.get("ref_id")),
            # Date is tricky because format might vary, we'll try to find the literal string 
            # if user provided it matching the message
        ]
        
        current_regex = escaped_content
        
        for key, val in fields:
            if not val: continue
            
            # Escape the value to find it in the already-escaped content
            escaped_val = re.escape(val)
            
            if escaped_val in current_regex:
                # Replace the FIRST occurrence of the value with a non-greedy group
                # We use a placeholder to avoid replacing parts of already replaced groups
                placeholder = f"__GROUP_{group_idx}__"
                current_regex = current_regex.replace(escaped_val, placeholder, 1)
                mapping[key] = group_idx
                group_idx += 1

        # Final pass: replace placeholders with actual regex groups
        for i in range(1, group_idx):
            current_regex = current_regex.replace(f"__GROUP_{i}__", "(.*?)")
            
        return current_regex, json.dumps(mapping)
