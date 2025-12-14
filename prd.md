# Trade Surveillance Support Agent

## Project Overview
This is an agent designed to automate trade surveillance support workflows by:
- Copilot parsing user inquiry emails
- Copilot searching relevant YML config files that constains SQL and Java code that uses the YML to execute the SQL
- YML and Java codes will have metadata annotation for easy searching
- The Java code are in a form of unit tests
- Once it finds the Java code, Copilot will have ability to change the java code arguments provided by the user to accomodate different execution conditions
- Copilot will execute Java processes to generate reports
- Use python to implement the agent

