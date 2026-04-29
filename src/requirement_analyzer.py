"""
Requirement Analyzer Module
Analyzes and categorizes requirements from RFP documents
"""

import logging
import re
from typing import Dict, List, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class RequirementType(Enum):
    """Enumeration of requirement types"""
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non_functional"
    PERFORMANCE = "performance"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    INFRASTRUCTURE = "infrastructure"
    INTEGRATION = "integration"
    SUPPORT = "support"
    TRAINING = "training"
    OTHER = "other"


class RequirementAnalyzer:
    """Analyze and categorize RFP requirements"""

    # Keywords for requirement categorization
    KEYWORDS = {
        RequirementType.FUNCTIONAL: [
            'feature', 'function', 'capability', 'allow', 'enable', 'support',
            'provide', 'deliver', 'implement', 'build', 'create', 'develop',
            'user shall', 'system shall', 'must', 'should'
        ],
        RequirementType.PERFORMANCE: [
            'performance', 'speed', 'latency', 'throughput', 'response time',
            'capacity', 'load', 'scale', 'scalable', 'concurrent', 'users',
            'requests per second', 'transactions per second'
        ],
        RequirementType.SECURITY: [
            'security', 'encryption', 'authentication', 'authorization',
            'access control', 'secure', 'protection', 'vulnerability',
            'penetration test', 'ssl', 'tls', 'firewall', 'audit', 'compliance'
        ],
        RequirementType.COMPLIANCE: [
            'compliance', 'gdpr', 'hipaa', 'pci-dss', 'sox', 'iso',
            'regulatory', 'legal', 'standard', 'certification', 'audit',
            'governance', 'policy'
        ],
        RequirementType.INFRASTRUCTURE: [
            'infrastructure', 'hosting', 'cloud', 'server', 'database',
            'storage', 'network', 'deployment', 'environment', 'kubernetes',
            'docker', 'aws', 'azure', 'gcp', 'on-premise'
        ],
        RequirementType.INTEGRATION: [
            'integration', 'api', 'interface', 'connect', 'sync', 'exchange',
            'interoperability', 'third-party', 'external', 'webhook'
        ],
        RequirementType.SUPPORT: [
            'support', 'maintenance', 'sla', 'uptime', 'monitoring',
            'alerting', 'incident', 'response time', 'availability'
        ],
        RequirementType.TRAINING: [
            'training', 'documentation', 'knowledge transfer', 'onboarding',
            'instruction', 'education', 'certification'
        ]
    }

    def __init__(self):
        """Initialize requirement analyzer"""
        self.requirements = []
        self.extracted_count = 0

    def extract_requirements(self, text: str) -> List[Dict]:
        """
        Extract individual requirements from text

        Args:
            text: Raw text from RFP document

        Returns:
            List of extracted requirements
        """
        try:
            requirements = []
            
            # Split by common requirement delimiters
            lines = text.split('\n')
            
            for line_num, line in enumerate(lines):
                line = line.strip()
                
                # Skip empty lines and short lines
                if not line or len(line) < 10:
                    continue
                
                # Check if line contains requirement indicators
                if self._is_requirement_line(line):
                    requirement = {
                        'id': len(requirements) + 1,
                        'text': line,
                        'line_number': line_num,
                        'type': self._categorize_requirement(line),
                        'priority': self._estimate_priority(line),
                        'effort_estimate': None,
                    }
                    requirements.append(requirement)
            
            self.requirements = requirements
            self.extracted_count = len(requirements)
            logger.info(f"Extracted {len(requirements)} requirements")
            
            return requirements

        except Exception as e:
            logger.error(f"Error extracting requirements: {str(e)}")
            raise

    def _is_requirement_line(self, line: str) -> bool:
        """
        Determine if a line contains a requirement

        Args:
            line: Text line to check

        Returns:
            True if line appears to be a requirement
        """
        requirement_patterns = [
            r'(req\d+|requirement|spec|specification|shall|must|should|may)',
            r'(feature|function|capability|implement|develop|build)',
            r'(the system|the application|the platform)',
            r'^[A-Z]{2,}[\d\-\.]*\s*:',  # REQ-001: format
        ]
        
        line_lower = line.lower()
        return any(re.search(pattern, line_lower) for pattern in requirement_patterns)

    def _categorize_requirement(self, text: str) -> str:
        """
        Categorize a requirement based on keywords

        Args:
            text: Requirement text

        Returns:
            Requirement type
        """
        text_lower = text.lower()
        
        # Count keyword matches for each type
        scores = {}
        for req_type, keywords in self.KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[req_type] = score
        
        # Return type with highest score
        if max(scores.values()) > 0:
            return max(scores, key=scores.get).value
        
        return RequirementType.OTHER.value

    def _estimate_priority(self, text: str) -> str:
        """
        Estimate priority level of requirement

        Args:
            text: Requirement text

        Returns:
            Priority level (critical, high, medium, low)
        """
        text_lower = text.lower()
        
        critical_keywords = ['critical', 'must', 'required', 'mandatory', 'essential']
        high_keywords = ['should', 'important', 'necessary']
        medium_keywords = ['nice to have', 'recommended']
        low_keywords = ['optional', 'may', 'could']
        
        if any(kw in text_lower for kw in critical_keywords):
            return 'critical'
        elif any(kw in text_lower for kw in high_keywords):
            return 'high'
        elif any(kw in text_lower for kw in medium_keywords):
            return 'medium'
        elif any(kw in text_lower for kw in low_keywords):
            return 'low'
        
        return 'medium'  # Default

    def group_requirements(self, requirements: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Group requirements by type

        Args:
            requirements: List of requirements

        Returns:
            Dictionary with requirements grouped by type
        """
        grouped = {}
        
        for req_type in RequirementType:
            grouped[req_type.value] = [
                r for r in requirements if r['type'] == req_type.value
            ]
        
        logger.info(f"Grouped {len(requirements)} requirements into {len(grouped)} categories")
        return grouped

    def identify_dependencies(self, requirements: List[Dict]) -> List[Tuple[int, int]]:
        """
        Identify dependencies between requirements

        Args:
            requirements: List of requirements

        Returns:
            List of (requirement_id, dependent_requirement_id) tuples
        """
        dependencies = []
        
        for i, req1 in enumerate(requirements):
            for j, req2 in enumerate(requirements):
                if i != j:
                    # Simple heuristic: if requirements share keywords, they might be related
                    text1_words = set(req1['text'].lower().split())
                    text2_words = set(req2['text'].lower().split())
                    
                    # Check for common content words (length > 4)
                    common_words = {w for w in text1_words & text2_words if len(w) > 4}
                    
                    if len(common_words) > 2:
                        dependencies.append((req1['id'], req2['id']))
        
        logger.info(f"Identified {len(dependencies)} potential dependencies")
        return dependencies

    def generate_summary(self, requirements: List[Dict]) -> Dict:
        """
        Generate summary statistics of requirements

        Args:
            requirements: List of requirements

        Returns:
            Summary dictionary
        """
        grouped = self.group_requirements(requirements)
        
        summary = {
            'total_requirements': len(requirements),
            'by_type': {k: len(v) for k, v in grouped.items()},
            'by_priority': {
                'critical': len([r for r in requirements if r['priority'] == 'critical']),
                'high': len([r for r in requirements if r['priority'] == 'high']),
                'medium': len([r for r in requirements if r['priority'] == 'medium']),
                'low': len([r for r in requirements if r['priority'] == 'low']),
            }
        }
        
        return summary


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    analyzer = RequirementAnalyzer()
    
    # Example requirements text
    sample_text = """
    REQ-001: The system must support user authentication with multi-factor authentication.
    REQ-002: The application should provide real-time data sync capabilities.
    REQ-003: Performance requirement: response time under 500ms for 95th percentile.
    REQ-004: Security: All data must be encrypted using AES-256.
    REQ-005: The platform must be deployable on Kubernetes.
    """
    
    reqs = analyzer.extract_requirements(sample_text)
    print("\nExtracted Requirements:")
    for req in reqs:
        print(f"  ID {req['id']}: {req['type']} (Priority: {req['priority']})")
        print(f"    {req['text'][:80]}...")
