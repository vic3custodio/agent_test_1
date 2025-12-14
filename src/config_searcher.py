"""
Config Searcher Module
Searches YML config files and Java test files based on metadata annotations.
"""

import os
import re
import yaml
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path


@dataclass
class ConfigMatch:
    """Represents a matched configuration file."""
    file_path: str
    file_type: str  # 'yml' or 'java'
    metadata: Dict[str, Any]
    sql_query: Optional[str] = None
    java_class: Optional[str] = None
    java_method: Optional[str] = None
    relevance_score: float = 0.0
    content: str = ""


@dataclass
class SearchCriteria:
    """Search criteria for finding relevant configs."""
    keywords: List[str] = field(default_factory=list)
    report_type: Optional[str] = None
    domain: Optional[str] = None
    capability: Optional[str] = None
    tags: List[str] = field(default_factory=list)


class ConfigSearcher:
    """
    Searches YML config files and Java test files based on metadata annotations.
    
    Metadata:
        - component: config_searcher
        - capability: search_yml, search_java, find_sql
        - domain: trade_surveillance
    """
    
    # Regex patterns for extracting metadata from files
    YML_METADATA_PATTERN = re.compile(r'#\s*@(\w+):\s*(.+?)(?:\n|$)')
    JAVA_METADATA_PATTERN = re.compile(r'@Meta(?:data)?\s*\(\s*(\w+)\s*=\s*"([^"]+)"\s*\)')
    JAVA_CLASS_PATTERN = re.compile(r'(?:public\s+)?class\s+(\w+)')
    JAVA_METHOD_PATTERN = re.compile(r'@Test.*?(?:public\s+)?void\s+(\w+)\s*\(', re.DOTALL)
    SQL_BLOCK_PATTERN = re.compile(r'sql:\s*[|>]?\s*\n((?:\s{2,}.+\n?)+)', re.MULTILINE)
    
    def __init__(self, config_dirs: List[str] = None, java_dirs: List[str] = None):
        """
        Initialize the config searcher.
        
        Args:
            config_dirs: List of directories to search for YML configs
            java_dirs: List of directories to search for Java test files
        """
        self.config_dirs = config_dirs or ['configs', 'config', 'yml']
        self.java_dirs = java_dirs or ['src/test', 'test', 'tests']
        self._yml_cache: Dict[str, ConfigMatch] = {}
        self._java_cache: Dict[str, ConfigMatch] = {}
    
    def search(self, criteria: SearchCriteria, base_path: str = ".") -> List[ConfigMatch]:
        """
        Search for YML and Java files matching the given criteria.
        
        Args:
            criteria: Search criteria
            base_path: Base path to search from
            
        Returns:
            List of matching ConfigMatch objects, sorted by relevance
        """
        matches = []
        
        # Search YML files
        yml_matches = self._search_yml_files(criteria, base_path)
        matches.extend(yml_matches)
        
        # Search Java files
        java_matches = self._search_java_files(criteria, base_path)
        matches.extend(java_matches)
        
        # Sort by relevance score
        matches.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return matches
    
    def _search_yml_files(self, criteria: SearchCriteria, base_path: str) -> List[ConfigMatch]:
        """Search YML configuration files."""
        matches = []
        
        for config_dir in self.config_dirs:
            dir_path = Path(base_path) / config_dir
            if not dir_path.exists():
                continue
            
            for yml_file in dir_path.rglob('*.yml'):
                match = self._parse_yml_file(str(yml_file), criteria)
                if match and match.relevance_score > 0:
                    matches.append(match)
            
            for yaml_file in dir_path.rglob('*.yaml'):
                match = self._parse_yml_file(str(yaml_file), criteria)
                if match and match.relevance_score > 0:
                    matches.append(match)
        
        return matches
    
    def _search_java_files(self, criteria: SearchCriteria, base_path: str) -> List[ConfigMatch]:
        """Search Java test files."""
        matches = []
        
        for java_dir in self.java_dirs:
            dir_path = Path(base_path) / java_dir
            if not dir_path.exists():
                continue
            
            for java_file in dir_path.rglob('*Test*.java'):
                match = self._parse_java_file(str(java_file), criteria)
                if match and match.relevance_score > 0:
                    matches.append(match)
        
        return matches
    
    def _parse_yml_file(self, file_path: str, criteria: SearchCriteria) -> Optional[ConfigMatch]:
        """Parse a YML file and extract metadata."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract metadata from comments
            metadata = {}
            for match in self.YML_METADATA_PATTERN.finditer(content):
                key = match.group(1).lower()
                value = match.group(2).strip()
                if key in metadata:
                    if isinstance(metadata[key], list):
                        metadata[key].append(value)
                    else:
                        metadata[key] = [metadata[key], value]
                else:
                    metadata[key] = value
            
            # Parse YAML content
            try:
                yaml_content = yaml.safe_load(content)
                if yaml_content and isinstance(yaml_content, dict):
                    # Extract metadata from YAML structure
                    if 'metadata' in yaml_content:
                        for k, v in yaml_content['metadata'].items():
                            metadata[k.lower()] = v
            except yaml.YAMLError:
                pass
            
            # Extract SQL query
            sql_query = None
            sql_match = self.SQL_BLOCK_PATTERN.search(content)
            if sql_match:
                sql_query = sql_match.group(1).strip()
            
            # Calculate relevance score
            score = self._calculate_relevance(metadata, content, criteria)
            
            return ConfigMatch(
                file_path=file_path,
                file_type='yml',
                metadata=metadata,
                sql_query=sql_query,
                relevance_score=score,
                content=content,
            )
            
        except Exception as e:
            print(f"Error parsing YML file {file_path}: {e}")
            return None
    
    def _parse_java_file(self, file_path: str, criteria: SearchCriteria) -> Optional[ConfigMatch]:
        """Parse a Java test file and extract metadata."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract metadata from annotations
            metadata = {}
            for match in self.JAVA_METADATA_PATTERN.finditer(content):
                key = match.group(1).lower()
                value = match.group(2).strip()
                if key in metadata:
                    if isinstance(metadata[key], list):
                        metadata[key].append(value)
                    else:
                        metadata[key] = [metadata[key], value]
                else:
                    metadata[key] = value
            
            # Extract package name
            package_match = re.search(r'package\s+([\w.]+);', content)
            if package_match:
                metadata['package'] = package_match.group(1)
            
            # Extract class name
            java_class = None
            class_match = self.JAVA_CLASS_PATTERN.search(content)
            if class_match:
                java_class = class_match.group(1)
            
            # Extract test method names
            java_methods = self.JAVA_METHOD_PATTERN.findall(content)
            java_method = java_methods[0] if java_methods else None
            
            # Store all test methods in metadata for reference
            if java_methods:
                metadata['test_methods'] = java_methods
            
            # Calculate relevance score
            score = self._calculate_relevance(metadata, content, criteria)
            
            return ConfigMatch(
                file_path=file_path,
                file_type='java',
                metadata=metadata,
                java_class=java_class,
                java_method=java_method,
                relevance_score=score,
                content=content,
            )
            
        except Exception as e:
            print(f"Error parsing Java file {file_path}: {e}")
            return None
    
    def _calculate_relevance(self, metadata: Dict, content: str, criteria: SearchCriteria) -> float:
        """Calculate relevance score based on criteria matching."""
        score = 0.0
        content_lower = content.lower()
        
        # Match keywords in content
        for keyword in criteria.keywords:
            keyword_lower = keyword.lower().replace('_', ' ')
            if keyword_lower in content_lower or keyword.lower() in content_lower:
                score += 1.0
        
        # Match report type
        if criteria.report_type:
            report_type_lower = criteria.report_type.lower()
            if report_type_lower in content_lower:
                score += 2.0
            if metadata.get('report_type', '').lower() == report_type_lower:
                score += 3.0
        
        # Match domain
        if criteria.domain:
            if metadata.get('domain', '').lower() == criteria.domain.lower():
                score += 2.0
        
        # Match capability
        if criteria.capability:
            capability = metadata.get('capability', '')
            if isinstance(capability, list):
                if criteria.capability.lower() in [c.lower() for c in capability]:
                    score += 2.0
            elif capability.lower() == criteria.capability.lower():
                score += 2.0
        
        # Match tags
        for tag in criteria.tags:
            tag_lower = tag.lower()
            file_tags = metadata.get('tags', [])
            if isinstance(file_tags, str):
                file_tags = [file_tags]
            if tag_lower in [t.lower() for t in file_tags]:
                score += 1.0
        
        return score
    
    def find_related_java_for_yml(self, yml_match: ConfigMatch, base_path: str = ".") -> List[ConfigMatch]:
        """
        Find Java test files that reference or use a specific YML config.
        
        Args:
            yml_match: The YML ConfigMatch to find related Java files for
            base_path: Base path to search from
            
        Returns:
            List of related Java ConfigMatch objects
        """
        related = []
        yml_name = Path(yml_match.file_path).stem
        
        for java_dir in self.java_dirs:
            dir_path = Path(base_path) / java_dir
            if not dir_path.exists():
                continue
            
            for java_file in dir_path.rglob('*.java'):
                try:
                    with open(java_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check if Java file references the YML config
                    if yml_name in content:
                        criteria = SearchCriteria(keywords=[yml_name])
                        match = self._parse_java_file(str(java_file), criteria)
                        if match:
                            match.relevance_score = 5.0  # High relevance for direct reference
                            related.append(match)
                            
                except Exception:
                    pass
        
        return related
    
    def get_all_configs(self, base_path: str = ".") -> Dict[str, List[ConfigMatch]]:
        """
        Get all available configs organized by report type.
        
        Args:
            base_path: Base path to search from
            
        Returns:
            Dictionary mapping report types to list of configs
        """
        all_matches = self.search(SearchCriteria(), base_path)
        
        organized = {}
        for match in all_matches:
            report_type = match.metadata.get('report_type', 'unknown')
            if report_type not in organized:
                organized[report_type] = []
            organized[report_type].append(match)
        
        return organized
