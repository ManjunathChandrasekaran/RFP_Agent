"""
Compliance Matcher Module
Maps requirements to team capabilities and identifies gaps
"""

import logging
import json
from typing import Dict, List, Tuple
from datetime import datetime

try:
    import pandas as pd
except ImportError:
    print("Pandas not found. Install with: pip install pandas")

from config import TEAM_CAPABILITIES


class ComplianceMatcher:
    """Match requirements to team capabilities"""
    
    def __init__(self):
        """Initialize compliance matcher"""
        self.logger = logging.getLogger(__name__)
        self.team_capabilities = TEAM_CAPABILITIES
    
    def extract_technical_requirements(self, requirements: List[Dict]) -> List[str]:
        """
        Extract technical keywords from requirements
        
        Args:
            requirements: List of requirements
            
        Returns:
            List of technical terms mentioned in requirements
        """
        technical_terms = set()
        
        for req in requirements:
            text = req.get("text", "").lower()
            tags = req.get("tags", [])
            
            # Add tags
            technical_terms.update(tags)
            
            # Extract from text
            keywords = [
                "python", "java", "node.js", "go", "c#", "rust", "typescript",
                "react", "vue", "angular", "aws", "azure", "gcp", "kubernetes",
                "docker", "postgresql", "mongodb", "redis", "elasticsearch",
                "rest api", "graphql", "grpc", "websocket",
                "oauth", "jwt", "saml", "ldap",
                "ci/cd", "jenkins", "gitlab", "github actions",
                "terraform", "cloudformation", "ansible",
                "microservices", "serverless", "lambda", "ecs", "aks"
            ]
            
            for keyword in keywords:
                if keyword in text:
                    technical_terms.add(keyword)
        
        return list(technical_terms)
    
    def match_capabilities(self, technical_requirements: List[str]) -> Dict[str, Dict]:
        """
        Match technical requirements to team capabilities
        
        Args:
            technical_requirements: List of technical terms
            
        Returns:
            Matching results with capability coverage
        """
        matches = {}
        unmatched = []
        
        for tech in technical_requirements:
            matched = False
            tech_lower = tech.lower()
            
            for capability_name, capability_info in self.team_capabilities.items():
                technologies = capability_info.get("technologies", [])
                for tech_in_cap in technologies:
                    if tech_lower in tech_in_cap.lower() or tech_in_cap.lower() in tech_lower:
                        if capability_name not in matches:
                            matches[capability_name] = {
                                "technologies": set(),
                                "capability_info": capability_info,
                                "match_count": 0
                            }
                        matches[capability_name]["technologies"].add(tech)
                        matches[capability_name]["match_count"] += 1
                        matched = True
                        break
                if matched:
                    break
            
            if not matched:
                unmatched.append(tech)
        
        # Convert sets to lists for JSON serialization
        for capability in matches:
            matches[capability]["technologies"] = list(matches[capability]["technologies"])
        
        return {
            "matched": matches,
            "unmatched": unmatched,
            "coverage_percentage": (len(technical_requirements) - len(unmatched)) / len(technical_requirements) * 100 if technical_requirements else 0
        }
    
    def generate_compliance_matrix(self, requirements: List[Dict], 
                                   matches: Dict) -> Dict[str, Dict]:
        """
        Generate compliance matrix showing requirement coverage
        
        Args:
            requirements: List of requirements
            matches: Capability matches
            
        Returns:
            Compliance matrix
        """
        matrix = {}
        
        for req in requirements:
            req_id = req.get("id", "UNKNOWN")
            category = req.get("category", "Unknown")
            text = req.get("text", "")
            
            # Check if requirement is covered
            is_covered = True
            covered_by = []
            
            # Extract technical terms from this requirement
            req_tech_terms = []
            for keyword in req.get("tags", []):
                req_tech_terms.append(keyword)
            
            # Check against matched capabilities
            for capability_name, cap_match in matches.get("matched", {}).items():
                for matched_tech in cap_match.get("technologies", []):
                    if any(t in text.lower() for t in req.get("tags", [])):
                        covered_by.append(capability_name)
                        break
            
            # If no matched capabilities and requirement has technical terms, mark as gap
            if not covered_by and req.get("tags"):
                is_covered = False
            
            matrix[req_id] = {
                "category": category,
                "priority": req.get("priority", "Medium"),
                "complexity": req.get("complexity", "Medium"),
                "covered": is_covered,
                "covered_by": list(set(covered_by)),  # Remove duplicates
                "effort_hours": req.get("estimated_effort_hours", 0),
                "tags": req.get("tags", [])
            }
        
        return matrix
    
    def identify_capability_gaps(self, requirements: List[Dict], 
                                 matches: Dict) -> Dict:
        """
        Identify gaps in team capabilities
        
        Args:
            requirements: List of requirements
            matches: Capability matches
            
        Returns:
            Gap analysis
        """
        gaps = {
            "technology_gaps": matches.get("unmatched", []),
            "skill_gaps": [],
            "resource_gaps": [],
            "compliance_gaps": [],
            "total_gap_risk": "Low"
        }
        
        # Analyze requirements for potential skill gaps
        for req in requirements:
            category = req.get("category", "")
            priority = req.get("priority", "")
            
            # Check if we have the required capability area
            if category and priority in ["Critical", "High"]:
                capability_found = False
                for cap_name in self.team_capabilities.keys():
                    if category.lower() in cap_name.lower() or cap_name.lower() in category.lower():
                        capability_found = True
                        break
                
                if not capability_found:
                    gaps["skill_gaps"].append({
                        "requirement": req.get("text", "")[:100],
                        "category": category,
                        "priority": priority
                    })
            
            # Check for compliance-related requirements without dedicated coverage
            if "compliance" in category.lower() or "security" in category.lower():
                if "Security & Compliance" not in self.team_capabilities:
                    gaps["compliance_gaps"].append(req.get("text", "")[:100])
        
        # Assess overall gap risk
        gap_count = len(gaps["technology_gaps"]) + len(gaps["skill_gaps"]) + len(gaps["compliance_gaps"])
        critical_gaps = len(gaps["compliance_gaps"]) + len([g for g in gaps["skill_gaps"] if g.get("priority") == "Critical"])
        
        if critical_gaps > 0:
            gaps["total_gap_risk"] = "High"
        elif gap_count > 3:
            gaps["total_gap_risk"] = "Medium"
        else:
            gaps["total_gap_risk"] = "Low"
        
        return gaps
    
    def generate_recommendations(self, gaps: Dict) -> List[str]:
        """
        Generate recommendations for addressing gaps
        
        Args:
            gaps: Gap analysis results
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if gaps["technology_gaps"]:
            recs = ", ".join(gaps["technology_gaps"][:3])
            recommendations.append(
                f"Consider upskilling team on: {recs}"
            )
        
        if gaps["skill_gaps"]:
            critical_gaps = [g for g in gaps["skill_gaps"] if g.get("priority") == "Critical"]
            if critical_gaps:
                recommendations.append(
                    "For critical requirements, consider hiring specialists or contractors"
                )
            else:
                recommendations.append(
                    "Some skill gaps identified; plan training or partnerships"
                )
        
        if gaps["compliance_gaps"]:
            recommendations.append(
                "Establish compliance and security practices; consider hiring security expert"
            )
        
        if gaps["total_gap_risk"] == "High":
            recommendations.append(
                "High risk detected; strongly recommend external expertise or partnerships"
            )
        
        if not recommendations:
            recommendations.append(
                "Team capabilities well-aligned with requirements. Proceed with confidence."
            )
        
        return recommendations
    
    def create_compliance_report(self, requirements: List[Dict]) -> Dict:
        """
        Create comprehensive compliance and capability report
        
        Args:
            requirements: List of requirements
            
        Returns:
            Complete compliance report
        """
        # Extract technical requirements
        tech_requirements = self.extract_technical_requirements(requirements)
        
        # Match to capabilities
        matches = self.match_capabilities(tech_requirements)
        
        # Generate compliance matrix
        compliance_matrix = self.generate_compliance_matrix(requirements, matches)
        
        # Identify gaps
        gaps = self.identify_capability_gaps(requirements, matches)
        
        # Generate recommendations
        recommendations = self.generate_recommendations(gaps)
        
        # Calculate coverage metrics
        covered_requirements = sum(1 for r in compliance_matrix.values() if r["covered"])
        total_requirements = len(compliance_matrix)
        
        report = {
            "generated_date": datetime.now().isoformat(),
            "technical_requirements": tech_requirements,
            "capability_matches": matches,
            "compliance_matrix": compliance_matrix,
            "gap_analysis": gaps,
            "recommendations": recommendations,
            "coverage_metrics": {
                "total_requirements": total_requirements,
                "covered_requirements": covered_requirements,
                "uncovered_requirements": total_requirements - covered_requirements,
                "coverage_percentage": (covered_requirements / total_requirements * 100) if total_requirements > 0 else 0
            },
            "team_summary": {
                "total_capabilities": len(self.team_capabilities),
                "team_members": sum(
                    cap.get("team_size", 0) for cap in self.team_capabilities.values()
                ),
                "avg_experience_years": sum(
                    cap.get("experience_years", 0) for cap in self.team_capabilities.values()
                ) / len(self.team_capabilities) if self.team_capabilities else 0
            }
        }
        
        return report
    
    def save_report(self, report: Dict, output_path: str):
        """Save compliance report to file"""
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        self.logger.info(f"Compliance report saved to: {output_path}")
    
    def export_to_csv(self, compliance_matrix: Dict, output_path: str):
        """Export compliance matrix to CSV"""
        try:
            df = pd.DataFrame(compliance_matrix).T
            df.to_csv(output_path)
            self.logger.info(f"Compliance matrix exported to: {output_path}")
        except Exception as e:
            self.logger.error(f"Error exporting to CSV: {e}")


def analyze_compliance(requirements: List[Dict], output_dir: str = "./output") -> Dict:
    """
    Convenience function to analyze compliance and capabilities
    
    Args:
        requirements: List of requirements
        output_dir: Directory to save reports
        
    Returns:
        Compliance report
    """
    matcher = ComplianceMatcher()
    report = matcher.create_compliance_report(requirements)
    
    # Save reports
    import os
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save JSON report
    json_file = os.path.join(output_dir, f"compliance_report_{timestamp}.json")
    matcher.save_report(report, json_file)
    
    # Save CSV matrix
    csv_file = os.path.join(output_dir, f"compliance_matrix_{timestamp}.csv")
    matcher.export_to_csv(report["compliance_matrix"], csv_file)
    
    return report
