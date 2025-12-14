# Trade Surveillance Support Agent

An **AI-powered Copilot agent** for automating trade surveillance support workflows. Interact with it directly in VS Code Copilot Chat using natural language!

## Overview

This agent uses **MCP (Model Context Protocol)** to expose trade surveillance capabilities as tools that GitHub Copilot can call. Simply chat with Copilot to:

- Parse inquiry emails and extract surveillance parameters
- Search for relevant YML configs and Java tests
- View and modify test parameters
- Execute Java tests to generate reports

## Quick Start - Using with Copilot Chat

Once the MCP server is running, interact with the agent in Copilot Chat:

```
"Parse this email: Subject: Wash Trade Alert, Body: Please investigate account ACC-123 for wash trades on AAPL between 2024-01-01 and 2024-06-30"

"Search for spoofing detection configs"

"Find Java tests for wash trade detection"

"What parameters can I configure for the WashTradeDetectionTest?"

"Execute the wash trade detection test for symbol AAPL"
```

## Installation

```bash
# Create virtual environment with Python 3.10+
python3.12 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package and MCP dependencies
pip install -e ".[dev]" "mcp[cli]"
```

## MCP Server Setup

The MCP server is configured in `.vscode/mcp.json`:

```json
{
  "servers": {
    "trade-surveil": {
      "type": "stdio",
      "command": "/path/to/project/.venv/bin/python",
      "args": ["-m", "src.mcp_server"],
      "env": {
        "TRADE_SURVEILLANCE_PROJECT_DIR": "/path/to/project"
      }
    }
  }
}
```

To start using the agent:
1. Open VS Code in this project
2. The MCP server starts automatically
3. Open Copilot Chat and start asking questions!

## MCP Tools Available

| Tool | Description |
|------|-------------|
| `parse_inquiry_email` | Parse an email to extract trade/account IDs, symbols, dates, report type |
| `search_surveillance_configs` | Find YML and Java configs by keywords or report type |
| `search_java_tests` | Search specifically for Java test files by keywords, report type, or class name |
| `get_config_details` | Get full contents of a specific config file |
| `list_available_reports` | List all report types with their associated configs |
| `list_java_tests` | List all available Java test classes |
| `get_test_parameters` | Extract configurable parameters from a Java test |
| `modify_test_parameters` | Modify test parameters and preview changes |
| `execute_java_test` | Run a Java test to generate a surveillance report |
| `process_surveillance_inquiry` | Full workflow: parse inquiry + find matching configs |

## Project Structure

```
trade-surveillance-agent/
├── src/
│   ├── __init__.py
│   ├── mcp_server.py      # MCP server exposing tools to Copilot
│   ├── agent.py           # Main agent orchestrator
│   ├── email_parser.py    # Email parsing module
│   ├── config_searcher.py # YML/Java config search
│   ├── java_executor.py   # Java test execution
│   └── cli.py             # Command-line interface
├── configs/
│   ├── wash_trade_detection.yml
│   ├── spoofing_detection.yml
│   └── front_running_detection.yml
├── src/test/java/com/surveillance/tests/
│   ├── WashTradeDetectionTest.java
│   ├── SpoofingDetectionTest.java
│   └── FrontRunningDetectionTest.java
├── tests/
│   └── test_agent.py
├── .vscode/
│   └── mcp.json           # MCP server configuration
├── pyproject.toml
└── README.md
```

## Supported Report Types

| Report Type | Description | Config File | Java Test |
|-------------|-------------|-------------|-----------|
| `wash_trade` | Detect wash trade patterns | `wash_trade_detection.yml` | `WashTradeDetectionTest.java` |
| `spoofing` | Detect spoofing/layering | `spoofing_detection.yml` | `SpoofingDetectionTest.java` |
| `front_running` | Detect front running | `front_running_detection.yml` | `FrontRunningDetectionTest.java` |

## Example Workflows

### 1. Investigate a User Inquiry

```
User: "I received this email - Subject: Urgent wash trade check, Body: Please investigate wash trades for account ACC-789 symbol TSLA from March 2024"

Copilot: [Uses parse_inquiry_email] Found:
- Account: ACC-789
- Symbol: TSLA  
- Report Type: wash_trade
- Date: March 2024

[Uses search_surveillance_configs] Found matching config: wash_trade_detection.yml
Recommended test: WashTradeDetectionTest.testDetectWashTrades
```

### 2. Search and Execute a Report

```
User: "Find spoofing detection tests and show me the parameters"

Copilot: [Uses search_java_tests] Found SpoofingDetectionTest with methods:
- testDetectSpoofing
- testDetectLayering
- testDetectSpoofingForAccount

[Uses get_test_parameters] Configurable parameters:
- startDate: "2024-01-01"
- endDate: "2024-12-31"
- cancelRateThreshold: 0.75
- maxOrderLifetimeMs: 500
```

### 3. Modify and Execute

```
User: "Run the spoofing test for symbol AAPL with cancel rate threshold 0.80"

Copilot: [Uses modify_test_parameters then execute_java_test]
Modified parameters and executed test...
Report generated at: reports/spoofing_report_20241213.csv
```

## Metadata Annotations

### YML Config Files

Use comment annotations for searchability:

```yaml
# @name: wash_trade_detection
# @report_type: wash_trade
# @domain: trade_surveillance
# @capability: detect_wash_trades
# @tags: wash_trade, manipulation
```

### Java Test Files

Use @Meta annotations in Java classes:

```java
/**
 * @Meta(component = "wash_trade_test")
 * @Meta(capability = "detect_wash_trades")
 * @Meta(domain = "trade_surveillance")
 * @Meta(report_type = "wash_trade")
 */
public class WashTradeDetectionTest {
    @Parameter("startDate")
    private String startDate = "2024-01-01";
    
    @Parameter("symbol")
    private String symbol = null;
    // ...
}
```

## Configuration

Environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `TRADE_SURVEILLANCE_PROJECT_DIR` | Project root directory | Current directory |
| `JAVA_HOME` | Path to Java installation | System default |
| `MAVEN_HOME` | Path to Maven installation | System default |

## Development

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html

# Run MCP server manually (for debugging)
python -m src.mcp_server
```

## License

MIT License
