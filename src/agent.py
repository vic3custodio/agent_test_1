"""
Trade Surveillance Support Agent
Main agent orchestrator that coordinates email parsing, config searching, and Java execution.
"""

import os
import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from .email_parser import EmailParser, ParsedInquiry
from .config_searcher import ConfigSearcher, SearchCriteria, ConfigMatch
from .java_executor import JavaExecutor, JavaTestConfig, ExecutionResult, JavaCodeModifier


@dataclass
class AgentResponse:
    """Response from the agent."""
    success: bool
    message: str
    parsed_inquiry: Optional[ParsedInquiry] = None
    matched_configs: List[ConfigMatch] = None
    execution_result: Optional[ExecutionResult] = None
    recommendations: List[str] = None
    raw_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.matched_configs is None:
            self.matched_configs = []
        if self.recommendations is None:
            self.recommendations = []
        if self.raw_data is None:
            self.raw_data = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        result = {
            'success': self.success,
            'message': self.message,
            'recommendations': self.recommendations,
        }
        
        if self.parsed_inquiry:
            result['parsed_inquiry'] = {
                'subject': self.parsed_inquiry.subject,
                'sender': self.parsed_inquiry.sender,
                'trade_id': self.parsed_inquiry.trade_id,
                'account_id': self.parsed_inquiry.account_id,
                'symbol': self.parsed_inquiry.symbol,
                'report_type': self.parsed_inquiry.report_type,
                'date_range_start': str(self.parsed_inquiry.date_range_start) if self.parsed_inquiry.date_range_start else None,
                'date_range_end': str(self.parsed_inquiry.date_range_end) if self.parsed_inquiry.date_range_end else None,
            }
        
        if self.matched_configs:
            result['matched_configs'] = [
                {
                    'file_path': c.file_path,
                    'file_type': c.file_type,
                    'relevance_score': c.relevance_score,
                    'metadata': c.metadata,
                }
                for c in self.matched_configs
            ]
        
        if self.execution_result:
            result['execution_result'] = {
                'success': self.execution_result.success,
                'exit_code': self.execution_result.exit_code,
                'execution_time_ms': self.execution_result.execution_time_ms,
                'report_path': self.execution_result.report_path,
                'error_message': self.execution_result.error_message,
            }
        
        result['raw_data'] = self.raw_data
        
        return result


class TradeSurveillanceAgent:
    """
    Main agent for automating trade surveillance support workflows.
    
    This agent:
    1. Parses user inquiry emails to extract relevant parameters
    2. Searches YML config files and Java test files based on metadata
    3. Modifies Java code arguments as needed
    4. Executes Java processes to generate reports
    
    Metadata:
        - component: trade_surveillance_agent
        - capability: parse_emails, search_configs, execute_reports
        - domain: trade_surveillance
        - version: 1.0.0
    """
    
    def __init__(self, 
                 project_dir: Optional[str] = None,
                 config_dirs: Optional[List[str]] = None,
                 java_dirs: Optional[List[str]] = None,
                 java_home: Optional[str] = None,
                 output_dir: Optional[str] = None):
        """
        Initialize the Trade Surveillance Support Agent.
        
        Args:
            project_dir: Root directory of the project
            config_dirs: Directories to search for YML configs
            java_dirs: Directories to search for Java test files
            java_home: Path to Java installation
            output_dir: Directory for report outputs
        """
        self.project_dir = project_dir or os.getcwd()
        self.output_dir = output_dir or os.path.join(self.project_dir, 'reports')
        
        # Initialize components
        self.email_parser = EmailParser()
        self.config_searcher = ConfigSearcher(config_dirs, java_dirs)
        self.java_executor = JavaExecutor(
            java_home=java_home,
            project_dir=self.project_dir,
        )
        self.code_modifier = JavaCodeModifier()
        
        # Ensure output directory exists
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    def process_inquiry(self, email_content: str = None, email_data: Dict[str, str] = None) -> AgentResponse:
        """
        Process a user inquiry email and generate appropriate response/action.
        
        Args:
            email_content: Raw email content (RFC 2822 format)
            email_data: Dictionary with email fields (subject, from, date, body)
            
        Returns:
            AgentResponse with processing results
        """
        try:
            # Step 1: Parse the email
            if email_content:
                inquiry = self.email_parser.parse_email_content(email_content)
            elif email_data:
                inquiry = self.email_parser.parse_email_dict(email_data)
            else:
                return AgentResponse(
                    success=False,
                    message="No email content provided",
                )
            
            # Step 2: Build search criteria from parsed inquiry
            keywords = self.email_parser.extract_keywords(inquiry.raw_body)
            if inquiry.report_type:
                keywords.append(inquiry.report_type)
            
            criteria = SearchCriteria(
                keywords=keywords,
                report_type=inquiry.report_type,
                domain='trade_surveillance',
            )
            
            # Step 3: Search for relevant configs
            matches = self.config_searcher.search(criteria, self.project_dir)
            
            # Step 4: Generate recommendations
            recommendations = self._generate_recommendations(inquiry, matches)
            
            return AgentResponse(
                success=True,
                message=f"Processed inquiry: {inquiry.subject}",
                parsed_inquiry=inquiry,
                matched_configs=matches,
                recommendations=recommendations,
            )
            
        except Exception as e:
            return AgentResponse(
                success=False,
                message=f"Error processing inquiry: {str(e)}",
            )
    
    def search_configs(self, 
                       keywords: List[str] = None,
                       report_type: str = None,
                       domain: str = None) -> AgentResponse:
        """
        Search for relevant YML and Java configurations.
        
        Args:
            keywords: Keywords to search for
            report_type: Type of report (e.g., 'wash_trade', 'spoofing')
            domain: Domain to filter by
            
        Returns:
            AgentResponse with matched configurations
        """
        criteria = SearchCriteria(
            keywords=keywords or [],
            report_type=report_type,
            domain=domain or 'trade_surveillance',
        )
        
        matches = self.config_searcher.search(criteria, self.project_dir)
        
        return AgentResponse(
            success=True,
            message=f"Found {len(matches)} matching configurations",
            matched_configs=matches,
        )
    
    def execute_report(self,
                       java_class: str,
                       method_name: str = None,
                       parameters: Dict[str, Any] = None,
                       java_file_path: str = None) -> AgentResponse:
        """
        Execute a Java test to generate a report.
        
        Args:
            java_class: Fully qualified Java class name
            method_name: Specific test method to run (optional)
            parameters: Parameters to modify in the Java code
            java_file_path: Path to Java file if modifications needed
            
        Returns:
            AgentResponse with execution results
        """
        try:
            config = JavaTestConfig(
                class_name=java_class,
                method_name=method_name,
                output_dir=self.output_dir,
                working_dir=self.project_dir,
            )
            
            if parameters and java_file_path:
                # Execute with modifications
                result, modified_code = self.java_executor.execute_with_modifications(
                    java_file_path,
                    parameters,
                    config,
                )
                raw_data = {'modified_code_preview': modified_code[:500] + '...' if len(modified_code) > 500 else modified_code}
            else:
                # Execute without modifications
                result = self.java_executor.execute_test(config)
                raw_data = {}
            
            message = f"Execution {'succeeded' if result.success else 'failed'}"
            if result.report_path:
                message += f". Report generated at: {result.report_path}"
            
            return AgentResponse(
                success=result.success,
                message=message,
                execution_result=result,
                raw_data=raw_data,
            )
            
        except Exception as e:
            return AgentResponse(
                success=False,
                message=f"Error executing report: {str(e)}",
            )
    
    def process_and_execute(self,
                            email_content: str = None,
                            email_data: Dict[str, str] = None,
                            auto_execute: bool = False) -> AgentResponse:
        """
        Full workflow: parse email, find configs, and optionally execute report.
        
        Args:
            email_content: Raw email content
            email_data: Dictionary with email fields
            auto_execute: Whether to automatically execute the best matching report
            
        Returns:
            AgentResponse with full workflow results
        """
        # Process the inquiry
        inquiry_response = self.process_inquiry(email_content, email_data)
        
        if not inquiry_response.success:
            return inquiry_response
        
        if not inquiry_response.matched_configs:
            inquiry_response.recommendations.append(
                "No matching configurations found. Consider adding relevant YML/Java files with proper metadata."
            )
            return inquiry_response
        
        if auto_execute:
            # Find best Java test to execute
            java_matches = [m for m in inquiry_response.matched_configs if m.file_type == 'java']
            
            if java_matches:
                best_match = java_matches[0]  # Already sorted by relevance
                
                # Build parameters from inquiry
                params = {}
                if inquiry_response.parsed_inquiry.trade_id:
                    params['tradeId'] = inquiry_response.parsed_inquiry.trade_id
                if inquiry_response.parsed_inquiry.account_id:
                    params['accountId'] = inquiry_response.parsed_inquiry.account_id
                if inquiry_response.parsed_inquiry.symbol:
                    params['symbol'] = inquiry_response.parsed_inquiry.symbol
                if inquiry_response.parsed_inquiry.date_range_start:
                    params['startDate'] = inquiry_response.parsed_inquiry.date_range_start.strftime('%Y-%m-%d')
                if inquiry_response.parsed_inquiry.date_range_end:
                    params['endDate'] = inquiry_response.parsed_inquiry.date_range_end.strftime('%Y-%m-%d')
                
                # Execute
                exec_response = self.execute_report(
                    java_class=best_match.java_class,
                    method_name=best_match.java_method,
                    parameters=params if params else None,
                    java_file_path=best_match.file_path if params else None,
                )
                
                # Merge responses
                inquiry_response.execution_result = exec_response.execution_result
                inquiry_response.raw_data.update(exec_response.raw_data)
                
                if exec_response.success:
                    inquiry_response.message += f" | Report execution succeeded"
                else:
                    inquiry_response.message += f" | Report execution failed: {exec_response.message}"
        
        return inquiry_response
    
    def _generate_recommendations(self, inquiry: ParsedInquiry, matches: List[ConfigMatch]) -> List[str]:
        """Generate recommendations based on inquiry and matches."""
        recommendations = []
        
        if not matches:
            recommendations.append("No matching configurations found. Try adding more specific keywords to your inquiry.")
            return recommendations
        
        # Recommend based on match types
        yml_matches = [m for m in matches if m.file_type == 'yml']
        java_matches = [m for m in matches if m.file_type == 'java']
        
        if yml_matches and not java_matches:
            recommendations.append(
                f"Found {len(yml_matches)} YML config(s) but no corresponding Java tests. "
                "Consider creating Java test files that reference these configs."
            )
        
        if java_matches:
            best = java_matches[0]
            recommendations.append(
                f"Recommended action: Execute test '{best.java_class}' "
                f"(relevance score: {best.relevance_score:.1f})"
            )
        
        # Add parameter recommendations
        if inquiry.report_type:
            recommendations.append(f"Report type identified: {inquiry.report_type}")
        else:
            recommendations.append("No specific report type identified. Consider specifying the report type in your inquiry.")
        
        return recommendations
    
    def get_available_reports(self) -> List[Dict[str, Any]]:
        """
        Get list of all available report types and their configurations.
        
        Returns:
            List of available report configurations
        """
        configs = self.config_searcher.get_all_configs(self.project_dir)
        
        reports = []
        for report_type, matches in configs.items():
            reports.append({
                'report_type': report_type,
                'config_count': len(matches),
                'configs': [
                    {
                        'file_path': m.file_path,
                        'file_type': m.file_type,
                        'metadata': m.metadata,
                    }
                    for m in matches
                ]
            })
        
        return reports
    
    def list_tests(self) -> List[Dict[str, str]]:
        """Get list of available Java tests."""
        return self.java_executor.get_available_tests(self.project_dir)


def create_agent(project_dir: str = None, **kwargs) -> TradeSurveillanceAgent:
    """
    Factory function to create a Trade Surveillance Agent.
    
    Args:
        project_dir: Root directory of the project
        **kwargs: Additional arguments passed to TradeSurveillanceAgent
        
    Returns:
        Configured TradeSurveillanceAgent instance
    """
    return TradeSurveillanceAgent(project_dir=project_dir, **kwargs)
