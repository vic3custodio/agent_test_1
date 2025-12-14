"""
Trade Surveillance MCP Server
Exposes trade surveillance capabilities as MCP tools for Copilot integration.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("trade-surveillance-agent")

# Get project directory from environment or use current
PROJECT_DIR = os.environ.get("TRADE_SURVEILLANCE_PROJECT_DIR", os.getcwd())


def get_project_dir() -> str:
    """Get the project directory."""
    return PROJECT_DIR


@mcp.tool()
def parse_inquiry_email(
    subject: str,
    body: str,
    sender: str = "user@example.com"
) -> dict:
    """
    Parse a user inquiry email to extract trade surveillance parameters.
    
    Use this tool when you receive an email or message asking about:
    - Wash trades investigation
    - Spoofing or layering detection
    - Front running analysis
    - Any trade surveillance query
    
    Args:
        subject: The email subject line
        body: The email body content
        sender: The sender's email address (optional)
    
    Returns:
        Parsed inquiry with extracted parameters like trade_id, account_id, 
        symbol, date range, and report type.
    """
    from src.email_parser import EmailParser
    
    parser = EmailParser()
    email_data = {
        "subject": subject,
        "from": sender,
        "date": "",
        "body": body,
    }
    
    inquiry = parser.parse_email_dict(email_data)
    keywords = parser.extract_keywords(f"{subject}\n{body}")
    
    return {
        "subject": inquiry.subject,
        "sender": inquiry.sender,
        "trade_id": inquiry.trade_id,
        "account_id": inquiry.account_id,
        "symbol": inquiry.symbol,
        "report_type": inquiry.report_type,
        "date_range_start": str(inquiry.date_range_start) if inquiry.date_range_start else None,
        "date_range_end": str(inquiry.date_range_end) if inquiry.date_range_end else None,
        "keywords": keywords,
        "raw_body": inquiry.raw_body,
    }


@mcp.tool()
def search_surveillance_configs(
    keywords: list[str] = None,
    report_type: str = None
) -> dict:
    """
    Search for relevant YML config files and Java test files based on keywords or report type.
    
    Use this tool to find:
    - SQL queries for specific surveillance patterns
    - Java test classes that can generate reports
    - Configuration parameters for detection algorithms
    
    Args:
        keywords: List of keywords to search for (e.g., ["wash_trade", "manipulation"])
        report_type: Type of report to find (wash_trade, spoofing, front_running, layering)
    
    Returns:
        List of matching configuration files with their metadata and SQL queries.
    """
    from src.config_searcher import ConfigSearcher, SearchCriteria
    
    searcher = ConfigSearcher()
    criteria = SearchCriteria(
        keywords=keywords or [],
        report_type=report_type,
        domain="trade_surveillance",
    )
    
    matches = searcher.search(criteria, get_project_dir())
    
    results = []
    for match in matches[:10]:  # Limit to top 10
        result = {
            "file_path": match.file_path,
            "file_type": match.file_type,
            "relevance_score": match.relevance_score,
            "metadata": match.metadata,
        }
        if match.sql_query:
            result["sql_query"] = match.sql_query
        if match.java_class:
            result["java_class"] = match.java_class
        if match.java_method:
            result["java_method"] = match.java_method
        results.append(result)
    
    return {
        "total_matches": len(matches),
        "configs": results,
    }


@mcp.tool()
def get_config_details(file_path: str) -> dict:
    """
    Get detailed contents of a specific YML config or Java test file.
    
    Use this after search_surveillance_configs to get full details of a specific config.
    
    Args:
        file_path: Path to the config file (can be relative or absolute)
    
    Returns:
        Full file contents and parsed metadata.
    """
    from src.config_searcher import ConfigSearcher, SearchCriteria
    
    # Resolve path
    if not os.path.isabs(file_path):
        file_path = os.path.join(get_project_dir(), file_path)
    
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}
    
    searcher = ConfigSearcher()
    criteria = SearchCriteria()
    
    if file_path.endswith(('.yml', '.yaml')):
        match = searcher._parse_yml_file(file_path, criteria)
    elif file_path.endswith('.java'):
        match = searcher._parse_java_file(file_path, criteria)
    else:
        return {"error": "Unsupported file type. Use .yml, .yaml, or .java files."}
    
    if not match:
        return {"error": "Could not parse file"}
    
    return {
        "file_path": match.file_path,
        "file_type": match.file_type,
        "metadata": match.metadata,
        "sql_query": match.sql_query,
        "java_class": match.java_class,
        "java_method": match.java_method,
        "content": match.content,
    }


@mcp.tool()
def list_available_reports() -> dict:
    """
    List all available surveillance report types and their configurations.
    
    Use this tool to discover what reports can be generated.
    
    Returns:
        List of report types with their associated config files and Java tests.
    """
    from src.config_searcher import ConfigSearcher
    
    searcher = ConfigSearcher()
    configs = searcher.get_all_configs(get_project_dir())
    
    reports = []
    for report_type, matches in configs.items():
        yml_files = [m.file_path for m in matches if m.file_type == 'yml']
        java_files = [m.file_path for m in matches if m.file_type == 'java']
        
        reports.append({
            "report_type": report_type,
            "yml_configs": yml_files,
            "java_tests": java_files,
            "total_configs": len(matches),
        })
    
    return {
        "total_report_types": len(reports),
        "reports": reports,
    }


@mcp.tool()
def list_java_tests() -> dict:
    """
    List all available Java test classes that can generate surveillance reports.
    
    Returns:
        List of Java test classes with their file paths and package names.
    """
    from src.java_executor import JavaExecutor
    
    executor = JavaExecutor(project_dir=get_project_dir())
    tests = executor.get_available_tests(get_project_dir())
    
    return {
        "total_tests": len(tests),
        "tests": tests,
    }


@mcp.tool()
def search_java_tests(
    keywords: list[str] = None,
    report_type: str = None,
    class_name: str = None
) -> dict:
    """
    Search for Java test files based on keywords, report type, or class name.
    
    Use this tool to find specific Java tests for surveillance reports.
    Similar to search_surveillance_configs but focused only on Java tests.
    
    Args:
        keywords: List of keywords to search for (e.g., ["wash", "trade", "detection"])
        report_type: Type of report (wash_trade, spoofing, front_running, layering)
        class_name: Partial or full class name to search for
    
    Returns:
        List of matching Java test files with metadata and test methods.
    """
    from src.config_searcher import ConfigSearcher, SearchCriteria
    import re
    
    searcher = ConfigSearcher()
    
    # Build search criteria
    search_keywords = keywords or []
    if report_type:
        search_keywords.append(report_type)
    if class_name:
        search_keywords.append(class_name)
    
    criteria = SearchCriteria(
        keywords=search_keywords,
        report_type=report_type,
        domain="trade_surveillance",
    )
    
    # Search only Java files
    java_matches = searcher._search_java_files(criteria, get_project_dir())
    
    # Additional filtering by class name if provided
    if class_name:
        class_name_lower = class_name.lower()
        java_matches = [
            m for m in java_matches 
            if m.java_class and class_name_lower in m.java_class.lower()
        ]
    
    results = []
    for match in java_matches:
        # Extract all test methods from the file
        test_methods = re.findall(r'@Test.*?(?:public\s+)?void\s+(\w+)\s*\(', match.content, re.DOTALL)
        
        results.append({
            "file_path": match.file_path,
            "java_class": match.java_class,
            "package": match.metadata.get("package", ""),
            "full_class_name": f"{match.metadata.get('package', '')}.{match.java_class}" if match.metadata.get('package') else match.java_class,
            "test_methods": test_methods,
            "report_type": match.metadata.get("report_type", "unknown"),
            "capabilities": match.metadata.get("capability", []),
            "relevance_score": match.relevance_score,
            "metadata": match.metadata,
        })
    
    # Sort by relevance
    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    return {
        "total_matches": len(results),
        "java_tests": results,
    }


@mcp.tool()
def get_test_parameters(java_file_path: str) -> dict:
    """
    Extract configurable parameters from a Java test file.
    
    Use this to understand what parameters can be modified before executing a test.
    
    Args:
        java_file_path: Path to the Java test file
    
    Returns:
        Dictionary of parameter names with their types and current values.
    """
    from src.java_executor import JavaCodeModifier
    
    # Resolve path
    if not os.path.isabs(java_file_path):
        java_file_path = os.path.join(get_project_dir(), java_file_path)
    
    if not os.path.exists(java_file_path):
        return {"error": f"File not found: {java_file_path}"}
    
    with open(java_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    modifier = JavaCodeModifier()
    parameters = modifier.extract_parameters(content)
    
    return {
        "file_path": java_file_path,
        "parameters": parameters,
    }


@mcp.tool()
def modify_test_parameters(
    java_file_path: str,
    modifications: dict
) -> dict:
    """
    Modify parameters in a Java test file for custom execution.
    
    Use this to change test parameters like date ranges, account IDs, or thresholds
    before generating a report.
    
    Args:
        java_file_path: Path to the Java test file
        modifications: Dictionary of parameter names to new values
            Example: {"startDate": "2024-01-01", "symbol": "AAPL", "accountId": "ACC-123"}
    
    Returns:
        Preview of the modified code sections.
    """
    from src.java_executor import JavaCodeModifier
    
    # Resolve path
    if not os.path.isabs(java_file_path):
        java_file_path = os.path.join(get_project_dir(), java_file_path)
    
    if not os.path.exists(java_file_path):
        return {"error": f"File not found: {java_file_path}"}
    
    with open(java_file_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    modifier = JavaCodeModifier()
    modified_content = modifier.modify_parameters(original_content, modifications)
    
    # Find the differences
    original_lines = original_content.split('\n')
    modified_lines = modified_content.split('\n')
    
    changes = []
    for i, (orig, mod) in enumerate(zip(original_lines, modified_lines)):
        if orig != mod:
            changes.append({
                "line": i + 1,
                "original": orig.strip(),
                "modified": mod.strip(),
            })
    
    return {
        "file_path": java_file_path,
        "modifications_applied": modifications,
        "changes": changes,
        "modified_content_preview": modified_content[:2000] + "..." if len(modified_content) > 2000 else modified_content,
    }


@mcp.tool()
def execute_java_test(
    java_class: str,
    method_name: str = None,
    parameters: dict = None,
    java_file_path: str = None
) -> dict:
    """
    Execute a Java test to generate a surveillance report.
    
    Use this to run a specific test after optionally modifying its parameters.
    
    Args:
        java_class: Fully qualified Java class name (e.g., "com.surveillance.tests.WashTradeDetectionTest")
        method_name: Specific test method to run (optional, runs all if not specified)
        parameters: Parameters to modify before execution (optional)
        java_file_path: Path to Java file if parameters need to be modified
    
    Returns:
        Execution result including success status, output, and report path.
    """
    from src.java_executor import JavaExecutor, JavaTestConfig
    
    executor = JavaExecutor(project_dir=get_project_dir())
    
    config = JavaTestConfig(
        class_name=java_class,
        method_name=method_name,
        output_dir=os.path.join(get_project_dir(), "reports"),
        working_dir=get_project_dir(),
    )
    
    # Resolve java_file_path if provided
    if java_file_path and not os.path.isabs(java_file_path):
        java_file_path = os.path.join(get_project_dir(), java_file_path)
    
    if parameters and java_file_path:
        result, modified_code = executor.execute_with_modifications(
            java_file_path,
            parameters,
            config,
        )
    else:
        result = executor.execute_test(config)
    
    return {
        "success": result.success,
        "exit_code": result.exit_code,
        "execution_time_ms": result.execution_time_ms,
        "report_path": result.report_path,
        "stdout": result.stdout[:5000] if result.stdout else None,
        "stderr": result.stderr[:2000] if result.stderr else None,
        "error_message": result.error_message,
    }


@mcp.tool()
def process_surveillance_inquiry(
    subject: str,
    body: str,
    auto_find_config: bool = True
) -> dict:
    """
    Full workflow: Parse an inquiry and find relevant configs/tests to execute.
    
    This is the main entry point for processing trade surveillance requests.
    It combines email parsing and config searching in one step.
    
    Args:
        subject: The inquiry subject/title
        body: The inquiry body/description
        auto_find_config: Whether to automatically search for matching configs
    
    Returns:
        Parsed inquiry details and matching configurations ready for execution.
    """
    from src.email_parser import EmailParser
    from src.config_searcher import ConfigSearcher, SearchCriteria
    
    # Parse the inquiry
    parser = EmailParser()
    email_data = {
        "subject": subject,
        "from": "user@example.com",
        "date": "",
        "body": body,
    }
    
    inquiry = parser.parse_email_dict(email_data)
    keywords = parser.extract_keywords(f"{subject}\n{body}")
    
    result = {
        "inquiry": {
            "subject": inquiry.subject,
            "trade_id": inquiry.trade_id,
            "account_id": inquiry.account_id,
            "symbol": inquiry.symbol,
            "report_type": inquiry.report_type,
            "date_range_start": str(inquiry.date_range_start) if inquiry.date_range_start else None,
            "date_range_end": str(inquiry.date_range_end) if inquiry.date_range_end else None,
            "keywords": keywords,
        },
        "matched_configs": [],
        "recommendations": [],
    }
    
    if auto_find_config:
        # Search for matching configs
        searcher = ConfigSearcher()
        
        # Add report type to keywords if found
        search_keywords = keywords.copy()
        if inquiry.report_type and inquiry.report_type not in search_keywords:
            search_keywords.append(inquiry.report_type)
        
        criteria = SearchCriteria(
            keywords=search_keywords,
            report_type=inquiry.report_type,
            domain="trade_surveillance",
        )
        
        matches = searcher.search(criteria, get_project_dir())
        
        for match in matches[:5]:
            config_info = {
                "file_path": match.file_path,
                "file_type": match.file_type,
                "relevance_score": match.relevance_score,
            }
            if match.java_class:
                config_info["java_class"] = match.java_class
            if match.java_method:
                config_info["java_method"] = match.java_method
            if match.sql_query:
                config_info["has_sql"] = True
            result["matched_configs"].append(config_info)
        
        # Generate recommendations
        java_matches = [m for m in matches if m.file_type == 'java']
        if java_matches:
            best = java_matches[0]
            result["recommendations"].append(
                f"Execute test: {best.java_class} using execute_java_test tool"
            )
            
            # Suggest parameters to modify
            params_to_set = []
            if inquiry.symbol:
                params_to_set.append(f'"symbol": "{inquiry.symbol}"')
            if inquiry.account_id:
                params_to_set.append(f'"accountId": "{inquiry.account_id}"')
            if inquiry.trade_id:
                params_to_set.append(f'"tradeId": "{inquiry.trade_id}"')
            if inquiry.date_range_start:
                params_to_set.append(f'"startDate": "{inquiry.date_range_start.strftime("%Y-%m-%d")}"')
            if inquiry.date_range_end:
                params_to_set.append(f'"endDate": "{inquiry.date_range_end.strftime("%Y-%m-%d")}"')
            
            if params_to_set:
                result["recommendations"].append(
                    f"Suggested parameters: {{{', '.join(params_to_set)}}}"
                )
        else:
            result["recommendations"].append(
                "No matching Java tests found. Check available reports with list_available_reports tool."
            )
    
    return result


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
