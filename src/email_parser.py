"""
Email Parser Module
Parses user inquiry emails to extract relevant information for trade surveillance queries.
"""

import re
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
import email
from email.message import Message


@dataclass
class ParsedInquiry:
    """Represents a parsed user inquiry from email."""
    subject: str
    sender: str
    date: datetime
    trade_id: Optional[str] = None
    account_id: Optional[str] = None
    symbol: Optional[str] = None
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
    report_type: Optional[str] = None
    additional_params: Dict[str, Any] = None
    raw_body: str = ""
    
    def __post_init__(self):
        if self.additional_params is None:
            self.additional_params = {}


class EmailParser:
    """
    Parses user inquiry emails and extracts trade surveillance parameters.
    
    Metadata:
        - component: email_parser
        - capability: parse_inquiry, extract_parameters
        - domain: trade_surveillance
    """
    
    # Regex patterns for extracting common trade surveillance parameters
    PATTERNS = {
        'trade_id': [
            r'trade\s*(?:id|#|number)[:\s]*([A-Z0-9\-]+)',
            r'(?:TRD|TRADE)[:\-]?([A-Z0-9]+)',
        ],
        'account_id': [
            r'account\s*(?:id|#|number)[:\s]*([A-Z0-9\-]+)',
            r'(?:ACC|ACCT)[:\-]?([A-Z0-9]+)',
        ],
        'symbol': [
            r'symbol[:\s]*([A-Z]{1,5})',
            r'ticker[:\s]*([A-Z]{1,5})',
            r'stock[:\s]*([A-Z]{1,5})',
        ],
        'date': [
            r'(\d{4}[-/]\d{2}[-/]\d{2})',
            r'(\d{2}[-/]\d{2}[-/]\d{4})',
        ],
        'report_type': [
            r'report\s*(?:type)?[:\s]*(wash\s*trades?|spoofing|layering|front\s*running|insider)',
            r'(wash\s*trades?|spoofing|layering|front\s*running|insider)\s*(?:report|analysis)?',
            r'investigate\s+(wash\s*trades?|spoofing|layering|front\s*running|insider)',
        ],
    }
    
    REPORT_TYPE_MAPPING = {
        'wash trade': 'wash_trade',
        'wash trades': 'wash_trade',
        'wash_trade': 'wash_trade',
        'wash_trades': 'wash_trade',
        'spoofing': 'spoofing',
        'layering': 'layering',
        'front running': 'front_running',
        'front_running': 'front_running',
        'insider': 'insider_trading',
    }

    def __init__(self):
        self._compiled_patterns = self._compile_patterns()
    
    def _compile_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Compile regex patterns for efficiency."""
        compiled = {}
        for key, patterns in self.PATTERNS.items():
            compiled[key] = [re.compile(p, re.IGNORECASE) for p in patterns]
        return compiled
    
    def parse_email_content(self, email_content: str) -> ParsedInquiry:
        """
        Parse raw email content (RFC 2822 format) and extract inquiry parameters.
        
        Args:
            email_content: Raw email content as string
            
        Returns:
            ParsedInquiry object with extracted parameters
        """
        msg = email.message_from_string(email_content)
        return self._parse_message(msg)
    
    def parse_email_dict(self, email_data: Dict[str, str]) -> ParsedInquiry:
        """
        Parse email from dictionary format.
        
        Args:
            email_data: Dictionary with keys 'subject', 'from', 'date', 'body'
            
        Returns:
            ParsedInquiry object with extracted parameters
        """
        subject = email_data.get('subject', '')
        sender = email_data.get('from', '')
        date_str = email_data.get('date', '')
        body = email_data.get('body', '')
        
        # Parse date
        try:
            date = datetime.fromisoformat(date_str) if date_str else datetime.now()
        except ValueError:
            date = datetime.now()
        
        # Extract parameters from subject and body
        full_text = f"{subject}\n{body}"
        params = self._extract_parameters(full_text)
        
        return ParsedInquiry(
            subject=subject,
            sender=sender,
            date=date,
            trade_id=params.get('trade_id'),
            account_id=params.get('account_id'),
            symbol=params.get('symbol'),
            date_range_start=params.get('date_range_start'),
            date_range_end=params.get('date_range_end'),
            report_type=params.get('report_type'),
            additional_params=params.get('additional', {}),
            raw_body=body,
        )
    
    def _parse_message(self, msg: Message) -> ParsedInquiry:
        """Parse an email.message.Message object."""
        subject = msg.get('Subject', '')
        sender = msg.get('From', '')
        date_str = msg.get('Date', '')
        
        # Parse date
        try:
            date = email.utils.parsedate_to_datetime(date_str) if date_str else datetime.now()
        except (ValueError, TypeError):
            date = datetime.now()
        
        # Get body
        body = self._get_email_body(msg)
        
        # Extract parameters
        full_text = f"{subject}\n{body}"
        params = self._extract_parameters(full_text)
        
        return ParsedInquiry(
            subject=subject,
            sender=sender,
            date=date,
            trade_id=params.get('trade_id'),
            account_id=params.get('account_id'),
            symbol=params.get('symbol'),
            date_range_start=params.get('date_range_start'),
            date_range_end=params.get('date_range_end'),
            report_type=params.get('report_type'),
            additional_params=params.get('additional', {}),
            raw_body=body,
        )
    
    def _get_email_body(self, msg: Message) -> str:
        """Extract text body from email message."""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain':
                    payload = part.get_payload(decode=True)
                    if payload:
                        return payload.decode('utf-8', errors='replace')
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                return payload.decode('utf-8', errors='replace')
        return ""
    
    def _extract_parameters(self, text: str) -> Dict[str, Any]:
        """Extract trade surveillance parameters from text."""
        params = {'additional': {}}
        
        # Extract trade_id
        for pattern in self._compiled_patterns['trade_id']:
            match = pattern.search(text)
            if match:
                params['trade_id'] = match.group(1).upper()
                break
        
        # Extract account_id
        for pattern in self._compiled_patterns['account_id']:
            match = pattern.search(text)
            if match:
                params['account_id'] = match.group(1).upper()
                break
        
        # Extract symbol
        for pattern in self._compiled_patterns['symbol']:
            match = pattern.search(text)
            if match:
                params['symbol'] = match.group(1).upper()
                break
        
        # Extract dates
        dates = []
        for pattern in self._compiled_patterns['date']:
            matches = pattern.findall(text)
            for date_str in matches:
                try:
                    # Try different date formats
                    for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%m-%d-%Y', '%m/%d/%Y']:
                        try:
                            dates.append(datetime.strptime(date_str, fmt))
                            break
                        except ValueError:
                            continue
                except Exception:
                    pass
        
        if dates:
            dates.sort()
            params['date_range_start'] = dates[0]
            if len(dates) > 1:
                params['date_range_end'] = dates[-1]
        
        # Extract report type
        for pattern in self._compiled_patterns['report_type']:
            match = pattern.search(text)
            if match:
                report_type = match.group(1).lower().strip()
                params['report_type'] = self.REPORT_TYPE_MAPPING.get(report_type, report_type.replace(' ', '_'))
                break
        
        return params
    
    def extract_keywords(self, text: str) -> List[str]:
        """
        Extract relevant keywords from text for searching YML/Java files.
        
        Args:
            text: Text to extract keywords from
            
        Returns:
            List of relevant keywords
        """
        # Common trade surveillance terms
        surveillance_terms = [
            'wash trade', 'spoofing', 'layering', 'front running', 'insider',
            'manipulation', 'alert', 'violation', 'compliance', 'suspicious',
            'pattern', 'detection', 'threshold', 'volume', 'price',
        ]
        
        keywords = []
        text_lower = text.lower()
        
        for term in surveillance_terms:
            if term in text_lower:
                keywords.append(term.replace(' ', '_'))
        
        return keywords
