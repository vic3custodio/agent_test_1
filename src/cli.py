"""
Command-line interface for the Trade Surveillance Support Agent.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from .agent import TradeSurveillanceAgent, create_agent


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Trade Surveillance Support Agent CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--project-dir",
        type=str,
        default=".",
        help="Project root directory",
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./reports",
        help="Output directory for reports",
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Process command
    process_parser = subparsers.add_parser("process", help="Process an email inquiry")
    process_parser.add_argument(
        "--email",
        type=str,
        help="Path to email file",
    )
    process_parser.add_argument(
        "--subject",
        type=str,
        help="Email subject",
    )
    process_parser.add_argument(
        "--body",
        type=str,
        help="Email body",
    )
    process_parser.add_argument(
        "--auto-execute",
        action="store_true",
        help="Automatically execute the best matching report",
    )
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for configurations")
    search_parser.add_argument(
        "--keywords",
        type=str,
        nargs="+",
        help="Keywords to search for",
    )
    search_parser.add_argument(
        "--report-type",
        type=str,
        help="Report type to filter by",
    )
    search_parser.add_argument(
        "--domain",
        type=str,
        default="trade_surveillance",
        help="Domain to filter by",
    )
    
    # Execute command
    execute_parser = subparsers.add_parser("execute", help="Execute a Java test")
    execute_parser.add_argument(
        "--class",
        dest="java_class",
        type=str,
        required=True,
        help="Java class name",
    )
    execute_parser.add_argument(
        "--method",
        type=str,
        help="Test method name",
    )
    execute_parser.add_argument(
        "--params",
        type=str,
        help="JSON string of parameters",
    )
    execute_parser.add_argument(
        "--file",
        type=str,
        help="Path to Java file for modifications",
    )
    
    # List command
    list_parser = subparsers.add_parser("list-tests", help="List available tests")
    
    # Available reports command
    reports_parser = subparsers.add_parser("list-reports", help="List available report types")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Create agent
    agent = create_agent(
        project_dir=args.project_dir,
        output_dir=args.output_dir,
    )
    
    # Execute command
    if args.command == "process":
        result = handle_process(agent, args)
    elif args.command == "search":
        result = handle_search(agent, args)
    elif args.command == "execute":
        result = handle_execute(agent, args)
    elif args.command == "list-tests":
        result = handle_list_tests(agent, args)
    elif args.command == "list-reports":
        result = handle_list_reports(agent, args)
    else:
        parser.print_help()
        sys.exit(1)
    
    # Output result
    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print_result(result)


def handle_process(agent: TradeSurveillanceAgent, args) -> dict:
    """Handle the process command."""
    email_data = {}
    
    if args.email:
        with open(args.email, 'r') as f:
            email_content = f.read()
        response = agent.process_and_execute(
            email_content=email_content,
            auto_execute=args.auto_execute,
        )
    else:
        email_data = {
            "subject": args.subject or "",
            "body": args.body or "",
            "from": "cli@local",
            "date": "",
        }
        response = agent.process_and_execute(
            email_data=email_data,
            auto_execute=args.auto_execute,
        )
    
    return response.to_dict()


def handle_search(agent: TradeSurveillanceAgent, args) -> dict:
    """Handle the search command."""
    response = agent.search_configs(
        keywords=args.keywords,
        report_type=args.report_type,
        domain=args.domain,
    )
    return response.to_dict()


def handle_execute(agent: TradeSurveillanceAgent, args) -> dict:
    """Handle the execute command."""
    params = None
    if args.params:
        params = json.loads(args.params)
    
    response = agent.execute_report(
        java_class=args.java_class,
        method_name=args.method,
        parameters=params,
        java_file_path=args.file,
    )
    return response.to_dict()


def handle_list_tests(agent: TradeSurveillanceAgent, args) -> dict:
    """Handle the list-tests command."""
    tests = agent.list_tests()
    return {"tests": tests}


def handle_list_reports(agent: TradeSurveillanceAgent, args) -> dict:
    """Handle the list-reports command."""
    reports = agent.get_available_reports()
    return {"reports": reports}


def print_result(result: dict):
    """Print result in human-readable format."""
    print("\n" + "=" * 60)
    print("RESULT")
    print("=" * 60)
    
    if "success" in result:
        status = "✓ SUCCESS" if result["success"] else "✗ FAILED"
        print(f"Status: {status}")
    
    if "message" in result:
        print(f"Message: {result['message']}")
    
    if "parsed_inquiry" in result and result["parsed_inquiry"]:
        print("\n--- Parsed Inquiry ---")
        for key, value in result["parsed_inquiry"].items():
            if value:
                print(f"  {key}: {value}")
    
    if "matched_configs" in result and result["matched_configs"]:
        print(f"\n--- Matched Configs ({len(result['matched_configs'])}) ---")
        for config in result["matched_configs"][:5]:  # Show top 5
            print(f"  [{config['file_type'].upper()}] {config['file_path']}")
            print(f"       Relevance: {config['relevance_score']:.1f}")
    
    if "recommendations" in result and result["recommendations"]:
        print("\n--- Recommendations ---")
        for i, rec in enumerate(result["recommendations"], 1):
            print(f"  {i}. {rec}")
    
    if "execution_result" in result and result["execution_result"]:
        print("\n--- Execution Result ---")
        exec_result = result["execution_result"]
        print(f"  Success: {exec_result['success']}")
        print(f"  Exit Code: {exec_result['exit_code']}")
        print(f"  Time: {exec_result['execution_time_ms']:.0f}ms")
        if exec_result.get("report_path"):
            print(f"  Report: {exec_result['report_path']}")
        if exec_result.get("error_message"):
            print(f"  Error: {exec_result['error_message']}")
    
    if "tests" in result:
        print(f"\n--- Available Tests ({len(result['tests'])}) ---")
        for test in result["tests"]:
            print(f"  {test['full_name']}")
            print(f"    File: {test['file_path']}")
    
    if "reports" in result:
        print(f"\n--- Available Report Types ({len(result['reports'])}) ---")
        for report in result["reports"]:
            print(f"  {report['report_type']}: {report['config_count']} config(s)")
    
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
