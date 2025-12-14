"""
Tests for the Trade Surveillance Support Agent.
"""

import pytest
from datetime import datetime
from src.email_parser import EmailParser, ParsedInquiry
from src.config_searcher import ConfigSearcher, SearchCriteria
from src.java_executor import JavaCodeModifier
from src.agent import TradeSurveillanceAgent


class TestEmailParser:
    """Tests for the EmailParser class."""
    
    def setup_method(self):
        self.parser = EmailParser()
    
    def test_parse_email_dict_basic(self):
        """Test parsing a basic email dictionary."""
        email_data = {
            "subject": "Wash Trade Investigation",
            "from": "analyst@company.com",
            "date": "2024-12-13",
            "body": "Please investigate wash trades for symbol AAPL",
        }
        
        result = self.parser.parse_email_dict(email_data)
        
        assert result.subject == "Wash Trade Investigation"
        assert result.sender == "analyst@company.com"
        assert result.symbol == "AAPL"
        assert result.report_type == "wash_trade"
    
    def test_parse_email_with_trade_id(self):
        """Test extracting trade ID from email."""
        email_data = {
            "subject": "Query about trade",
            "from": "user@company.com",
            "date": "",
            "body": "Please check trade ID: TRD-123456",
        }
        
        result = self.parser.parse_email_dict(email_data)
        
        assert result.trade_id == "TRD-123456"
    
    def test_parse_email_with_account_id(self):
        """Test extracting account ID from email."""
        email_data = {
            "subject": "Account investigation",
            "from": "user@company.com",
            "date": "",
            "body": "Review activity for account number: ACC-789",
        }
        
        result = self.parser.parse_email_dict(email_data)
        
        assert result.account_id == "ACC-789"
    
    def test_parse_email_with_date_range(self):
        """Test extracting date range from email."""
        email_data = {
            "subject": "Historical analysis",
            "from": "user@company.com",
            "date": "",
            "body": "Analyze trades from 2024-01-01 to 2024-06-30",
        }
        
        result = self.parser.parse_email_dict(email_data)
        
        assert result.date_range_start == datetime(2024, 1, 1)
        assert result.date_range_end == datetime(2024, 6, 30)
    
    def test_extract_keywords(self):
        """Test keyword extraction."""
        text = "We found suspicious wash trade and spoofing patterns"
        
        keywords = self.parser.extract_keywords(text)
        
        assert "wash_trade" in keywords
        assert "spoofing" in keywords
        assert "suspicious" in keywords


class TestConfigSearcher:
    """Tests for the ConfigSearcher class."""
    
    def setup_method(self):
        self.searcher = ConfigSearcher()
    
    def test_create_search_criteria(self):
        """Test creating search criteria."""
        criteria = SearchCriteria(
            keywords=["wash_trade", "manipulation"],
            report_type="wash_trade",
            domain="trade_surveillance",
        )
        
        assert len(criteria.keywords) == 2
        assert criteria.report_type == "wash_trade"
        assert criteria.domain == "trade_surveillance"


class TestJavaCodeModifier:
    """Tests for the JavaCodeModifier class."""
    
    def setup_method(self):
        self.modifier = JavaCodeModifier()
    
    def test_format_string_value(self):
        """Test formatting string values for Java."""
        result = self.modifier._format_value("test", "String")
        assert result == '"test"'
    
    def test_format_int_value(self):
        """Test formatting integer values for Java."""
        result = self.modifier._format_value(42, "int")
        assert result == "42"
    
    def test_format_boolean_value(self):
        """Test formatting boolean values for Java."""
        assert self.modifier._format_value(True, "boolean") == "true"
        assert self.modifier._format_value(False, "boolean") == "false"
    
    def test_format_double_value(self):
        """Test formatting double values for Java."""
        result = self.modifier._format_value(3.14, "double")
        assert result == "3.14d"
    
    def test_modify_parameters(self):
        """Test modifying parameters in Java code."""
        java_code = '''
        @Parameter("startDate")
        private String startDate = "2024-01-01";
        '''
        
        modified = self.modifier.modify_parameters(
            java_code, 
            {"startDate": "2025-01-01"}
        )
        
        assert '"2025-01-01"' in modified


class TestTradeSurveillanceAgent:
    """Tests for the TradeSurveillanceAgent class."""
    
    def setup_method(self):
        self.agent = TradeSurveillanceAgent(project_dir=".")
    
    def test_agent_initialization(self):
        """Test agent initializes correctly."""
        assert self.agent.email_parser is not None
        assert self.agent.config_searcher is not None
        assert self.agent.java_executor is not None
    
    def test_process_inquiry_no_content(self):
        """Test processing inquiry with no content."""
        response = self.agent.process_inquiry()
        
        assert not response.success
        assert "No email content provided" in response.message
    
    def test_search_configs(self):
        """Test searching for configs."""
        response = self.agent.search_configs(
            keywords=["wash_trade"],
            report_type="wash_trade",
        )
        
        assert response.success
        assert "Found" in response.message


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
