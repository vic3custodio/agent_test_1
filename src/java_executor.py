"""
Java Executor Module
Executes Java test processes and manages report generation.
"""

import os
import re
import subprocess
import tempfile
import shutil
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime


@dataclass
class ExecutionResult:
    """Result of a Java execution."""
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    execution_time_ms: float
    report_path: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class JavaTestConfig:
    """Configuration for running a Java test."""
    class_name: str
    method_name: Optional[str] = None
    arguments: Dict[str, Any] = field(default_factory=dict)
    system_properties: Dict[str, str] = field(default_factory=dict)
    classpath: List[str] = field(default_factory=list)
    java_home: Optional[str] = None
    working_dir: Optional[str] = None
    timeout_seconds: int = 300
    output_dir: Optional[str] = None


class JavaCodeModifier:
    """
    Modifies Java test code to accommodate different execution conditions.
    
    Metadata:
        - component: java_modifier
        - capability: modify_arguments, update_parameters
        - domain: trade_surveillance
    """
    
    # Patterns for finding and modifying Java code
    PARAMETER_PATTERN = re.compile(
        r'(@Parameter\s*\(\s*"([^"]+)"\s*\))\s*\n\s*(?:private\s+)?(\w+)\s+(\w+)\s*=\s*([^;]+);',
        re.MULTILINE
    )
    VARIABLE_ASSIGNMENT_PATTERN = re.compile(
        r'((?:private|public|protected)?\s*(?:static\s+)?(?:final\s+)?(\w+)\s+(\w+))\s*=\s*([^;]+);'
    )
    STRING_LITERAL_PATTERN = re.compile(r'"([^"]*)"')
    
    def modify_parameters(self, java_content: str, modifications: Dict[str, Any]) -> str:
        """
        Modify parameters in Java code based on the provided modifications.
        
        Args:
            java_content: Original Java source code
            modifications: Dictionary of parameter names to new values
            
        Returns:
            Modified Java source code
        """
        modified = java_content
        
        for param_name, new_value in modifications.items():
            # Try to find and replace parameter annotations
            modified = self._replace_parameter(modified, param_name, new_value)
            
            # Try to find and replace variable assignments
            modified = self._replace_variable(modified, param_name, new_value)
        
        return modified
    
    def _replace_parameter(self, content: str, param_name: str, new_value: Any) -> str:
        """Replace a @Parameter annotated field."""
        pattern = re.compile(
            rf'(@Parameter\s*\(\s*"{re.escape(param_name)}"\s*\))\s*\n\s*(?:private\s+)?(\w+)\s+(\w+)\s*=\s*[^;]+;',
            re.MULTILINE
        )
        
        match = pattern.search(content)
        if match:
            annotation = match.group(1)
            var_type = match.group(2)
            var_name = match.group(3)
            formatted_value = self._format_value(new_value, var_type)
            replacement = f'{annotation}\n    private {var_type} {var_name} = {formatted_value};'
            content = pattern.sub(replacement, content, count=1)
        
        return content
    
    def _replace_variable(self, content: str, var_name: str, new_value: Any) -> str:
        """Replace a variable assignment."""
        # Pattern to match variable declarations/assignments
        pattern = re.compile(
            rf'((?:private|public|protected)?\s*(?:static\s+)?(?:final\s+)?(\w+)\s+{re.escape(var_name)})\s*=\s*[^;]+;'
        )
        
        match = pattern.search(content)
        if match:
            declaration = match.group(1)
            var_type = match.group(2)
            formatted_value = self._format_value(new_value, var_type)
            replacement = f'{declaration} = {formatted_value};'
            content = pattern.sub(replacement, content, count=1)
        
        return content
    
    def _format_value(self, value: Any, java_type: str) -> str:
        """Format a Python value for Java source code."""
        if value is None:
            return 'null'
        
        java_type_lower = java_type.lower()
        
        if java_type_lower == 'string':
            return f'"{value}"'
        elif java_type_lower in ('int', 'integer'):
            return str(int(value))
        elif java_type_lower in ('long'):
            return f'{int(value)}L'
        elif java_type_lower in ('double'):
            return f'{float(value)}d'
        elif java_type_lower in ('float'):
            return f'{float(value)}f'
        elif java_type_lower in ('boolean'):
            return 'true' if value else 'false'
        elif java_type_lower == 'date':
            if isinstance(value, datetime):
                return f'Date.parse("{value.strftime("%Y-%m-%d")}")'
            return f'Date.parse("{value}")'
        elif java_type_lower.startswith('list'):
            if isinstance(value, list):
                items = ', '.join(self._format_value(v, 'String') for v in value)
                return f'Arrays.asList({items})'
        
        # Default to string representation
        return f'"{value}"'
    
    def extract_parameters(self, java_content: str) -> Dict[str, Dict[str, Any]]:
        """
        Extract all parameters from Java code.
        
        Returns:
            Dictionary of parameter names to their info (type, current value, etc.)
        """
        parameters = {}
        
        # Find @Parameter annotations
        for match in self.PARAMETER_PATTERN.finditer(java_content):
            param_name = match.group(2)
            var_type = match.group(3)
            var_name = match.group(4)
            current_value = match.group(5).strip()
            
            parameters[param_name] = {
                'variable_name': var_name,
                'type': var_type,
                'current_value': current_value,
            }
        
        return parameters


class JavaExecutor:
    """
    Executes Java test processes to generate reports.
    
    Metadata:
        - component: java_executor
        - capability: execute_tests, generate_reports
        - domain: trade_surveillance
    """
    
    DEFAULT_MAVEN_CMD = 'mvn'
    DEFAULT_GRADLE_CMD = 'gradle'
    
    def __init__(self, 
                 java_home: Optional[str] = None,
                 maven_home: Optional[str] = None,
                 gradle_home: Optional[str] = None,
                 project_dir: Optional[str] = None):
        """
        Initialize the Java executor.
        
        Args:
            java_home: Path to Java installation
            maven_home: Path to Maven installation
            gradle_home: Path to Gradle installation
            project_dir: Path to the Java project directory
        """
        self.java_home = java_home or os.environ.get('JAVA_HOME')
        self.maven_home = maven_home or os.environ.get('MAVEN_HOME')
        self.gradle_home = gradle_home or os.environ.get('GRADLE_HOME')
        self.project_dir = project_dir or os.getcwd()
        self.modifier = JavaCodeModifier()
    
    def execute_test(self, config: JavaTestConfig) -> ExecutionResult:
        """
        Execute a Java test with the given configuration.
        
        Args:
            config: JavaTestConfig with test details
            
        Returns:
            ExecutionResult with execution details
        """
        start_time = datetime.now()
        
        try:
            # Determine build tool
            build_tool = self._detect_build_tool(config.working_dir or self.project_dir)
            
            if build_tool == 'maven':
                result = self._execute_maven_test(config)
            elif build_tool == 'gradle':
                result = self._execute_gradle_test(config)
            else:
                result = self._execute_direct_java(config)
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            result.execution_time_ms = execution_time
            
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            return ExecutionResult(
                success=False,
                exit_code=-1,
                stdout='',
                stderr=str(e),
                execution_time_ms=execution_time,
                error_message=str(e),
            )
    
    def execute_with_modifications(self, 
                                   java_file_path: str,
                                   modifications: Dict[str, Any],
                                   config: JavaTestConfig) -> Tuple[ExecutionResult, str]:
        """
        Modify Java code and execute the test.
        
        Args:
            java_file_path: Path to the Java test file
            modifications: Dictionary of parameter modifications
            config: JavaTestConfig with test details
            
        Returns:
            Tuple of (ExecutionResult, modified_code)
        """
        # Read original file
        with open(java_file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Modify the code
        modified_content = self.modifier.modify_parameters(original_content, modifications)
        
        # Create a temporary modified file
        temp_dir = tempfile.mkdtemp()
        try:
            # Preserve package structure
            rel_path = self._get_relative_path(java_file_path, config.working_dir or self.project_dir)
            temp_file = Path(temp_dir) / rel_path
            temp_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            # Update config to use temp directory
            modified_config = JavaTestConfig(
                class_name=config.class_name,
                method_name=config.method_name,
                arguments=config.arguments,
                system_properties=config.system_properties,
                classpath=config.classpath + [str(temp_dir)],
                java_home=config.java_home,
                working_dir=config.working_dir,
                timeout_seconds=config.timeout_seconds,
                output_dir=config.output_dir,
            )
            
            result = self.execute_test(modified_config)
            return result, modified_content
            
        finally:
            # Cleanup temp directory
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def _detect_build_tool(self, project_dir: str) -> str:
        """Detect which build tool is used in the project."""
        project_path = Path(project_dir)
        
        if (project_path / 'pom.xml').exists():
            return 'maven'
        elif (project_path / 'build.gradle').exists() or (project_path / 'build.gradle.kts').exists():
            return 'gradle'
        else:
            return 'direct'
    
    def _execute_maven_test(self, config: JavaTestConfig) -> ExecutionResult:
        """Execute test using Maven."""
        mvn_cmd = self._get_maven_command()
        
        cmd = [mvn_cmd, 'test', '-Dtest=' + config.class_name]
        
        if config.method_name:
            cmd[-1] += '#' + config.method_name
        
        # Add system properties
        for key, value in config.system_properties.items():
            cmd.append(f'-D{key}={value}')
        
        return self._run_command(cmd, config)
    
    def _execute_gradle_test(self, config: JavaTestConfig) -> ExecutionResult:
        """Execute test using Gradle."""
        gradle_cmd = self._get_gradle_command()
        
        cmd = [gradle_cmd, 'test', '--tests', config.class_name]
        
        if config.method_name:
            cmd[-1] += '.' + config.method_name
        
        # Add system properties
        for key, value in config.system_properties.items():
            cmd.append(f'-D{key}={value}')
        
        return self._run_command(cmd, config)
    
    def _execute_direct_java(self, config: JavaTestConfig) -> ExecutionResult:
        """Execute test directly using java command."""
        java_cmd = self._get_java_command()
        
        cmd = [java_cmd]
        
        # Add system properties
        for key, value in config.system_properties.items():
            cmd.append(f'-D{key}={value}')
        
        # Add classpath
        if config.classpath:
            cmd.extend(['-cp', os.pathsep.join(config.classpath)])
        
        # Add JUnit runner and test class
        cmd.extend(['org.junit.runner.JUnitCore', config.class_name])
        
        return self._run_command(cmd, config)
    
    def _run_command(self, cmd: List[str], config: JavaTestConfig) -> ExecutionResult:
        """Run a command and capture output."""
        working_dir = config.working_dir or self.project_dir
        
        env = os.environ.copy()
        if config.java_home:
            env['JAVA_HOME'] = config.java_home
            env['PATH'] = os.path.join(config.java_home, 'bin') + os.pathsep + env.get('PATH', '')
        
        try:
            result = subprocess.run(
                cmd,
                cwd=working_dir,
                env=env,
                capture_output=True,
                text=True,
                timeout=config.timeout_seconds,
            )
            
            # Check for report output
            report_path = self._find_report(config.output_dir or working_dir)
            
            return ExecutionResult(
                success=result.returncode == 0,
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                execution_time_ms=0,  # Will be set by caller
                report_path=report_path,
            )
            
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                success=False,
                exit_code=-1,
                stdout='',
                stderr='Execution timed out',
                execution_time_ms=config.timeout_seconds * 1000,
                error_message='Execution timed out',
            )
    
    def _get_java_command(self) -> str:
        """Get the java command path."""
        if self.java_home:
            return os.path.join(self.java_home, 'bin', 'java')
        return 'java'
    
    def _get_maven_command(self) -> str:
        """Get the maven command path."""
        if self.maven_home:
            return os.path.join(self.maven_home, 'bin', 'mvn')
        return self.DEFAULT_MAVEN_CMD
    
    def _get_gradle_command(self) -> str:
        """Get the gradle command path."""
        if self.gradle_home:
            return os.path.join(self.gradle_home, 'bin', 'gradle')
        return self.DEFAULT_GRADLE_CMD
    
    def _get_relative_path(self, file_path: str, base_dir: str) -> str:
        """Get relative path of file from base directory."""
        try:
            return str(Path(file_path).relative_to(Path(base_dir)))
        except ValueError:
            return Path(file_path).name
    
    def _find_report(self, output_dir: str) -> Optional[str]:
        """Find generated report in output directory."""
        output_path = Path(output_dir)
        
        # Common report patterns
        report_patterns = ['*.html', '*.pdf', '*.csv', '*.xlsx', '*report*']
        
        for pattern in report_patterns:
            reports = list(output_path.glob(f'**/{pattern}'))
            if reports:
                # Return most recently modified
                reports.sort(key=lambda p: p.stat().st_mtime, reverse=True)
                return str(reports[0])
        
        return None
    
    def get_available_tests(self, project_dir: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Get list of available test classes in the project.
        
        Returns:
            List of dictionaries with test class info
        """
        search_dir = Path(project_dir or self.project_dir)
        tests = []
        
        # Search common test directories
        for test_dir in ['src/test/java', 'test', 'tests']:
            dir_path = search_dir / test_dir
            if dir_path.exists():
                for java_file in dir_path.rglob('*Test*.java'):
                    with open(java_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract class name
                    class_match = re.search(r'class\s+(\w+)', content)
                    if class_match:
                        class_name = class_match.group(1)
                        
                        # Extract package
                        package_match = re.search(r'package\s+([\w.]+);', content)
                        package = package_match.group(1) if package_match else ''
                        
                        full_name = f'{package}.{class_name}' if package else class_name
                        
                        tests.append({
                            'class_name': class_name,
                            'full_name': full_name,
                            'file_path': str(java_file),
                            'package': package,
                        })
        
        return tests
