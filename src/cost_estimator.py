"""
Cost Estimator Module
Estimates project costs based on requirements and team capabilities
"""

import logging
from typing import Dict, List, Tuple
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CostEstimator:
    """Estimate project costs based on requirements"""

    # Default effort estimates (in hours) for common tasks
    DEFAULT_EFFORT_MAP = {
        'simple_feature': 16,
        'moderate_feature': 40,
        'complex_feature': 80,
        'critical_feature': 120,
        'api_endpoint': 12,
        'database_design': 20,
        'database_optimization': 30,
        'testing': 30,
        'integration': 24,
        'documentation': 15,
        'deployment': 10,
        'infrastructure_setup': 40,
        'security_audit': 25,
        'training': 20,
        'support_setup': 15,
    }

    # Complexity multipliers based on requirement priority
    PRIORITY_MULTIPLIERS = {
        'critical': 1.5,
        'high': 1.25,
        'medium': 1.0,
        'low': 0.8,
    }

    # Hourly rates by experience level
    DEFAULT_RATES = {
        'junior': 50,
        'mid': 100,
        'senior': 150,
        'architect': 200,
    }

    def __init__(self, hourly_rates: Dict = None, markup_percentage: float = 30):
        """
        Initialize cost estimator

        Args:
            hourly_rates: Custom hourly rates by level
            markup_percentage: Markup percentage for profit margin
        """
        self.hourly_rates = hourly_rates or self.DEFAULT_RATES
        self.markup_percentage = markup_percentage
        self.cost_lines = []

    def estimate_requirement_effort(self, requirement: Dict) -> float:
        """
        Estimate effort hours for a single requirement

        Args:
            requirement: Requirement dictionary

        Returns:
            Estimated effort in hours
        """
        # Base effort from requirement type
        req_type = requirement.get('type', 'other')
        
        # Map requirement type to effort category
        effort_map = {
            'functional': 40,  # Default for functional
            'non_functional': 30,
            'performance': 35,
            'security': 40,
            'compliance': 50,
            'infrastructure': 45,
            'integration': 24,
            'support': 15,
            'training': 20,
        }
        
        base_effort = effort_map.get(req_type, 30)
        
        # Apply priority multiplier
        priority = requirement.get('priority', 'medium')
        multiplier = self.PRIORITY_MULTIPLIERS.get(priority, 1.0)
        
        estimated_effort = base_effort * multiplier
        
        logger.debug(f"Estimated effort for requirement {requirement.get('id')}: {estimated_effort} hours")
        
        return estimated_effort

    def estimate_total_project_effort(self, requirements: List[Dict]) -> Dict:
        """
        Estimate total project effort

        Args:
            requirements: List of requirements

        Returns:
            Dictionary with effort breakdown
        """
        efforts = {
            'total_hours': 0,
            'by_type': {},
            'by_priority': {},
            'requirements_details': [],
        }
        
        for req in requirements:
            effort = self.estimate_requirement_effort(req)
            req_type = req.get('type', 'other')
            priority = req.get('priority', 'medium')
            
            efforts['total_hours'] += effort
            
            # By type
            if req_type not in efforts['by_type']:
                efforts['by_type'][req_type] = {'count': 0, 'hours': 0}
            efforts['by_type'][req_type]['count'] += 1
            efforts['by_type'][req_type]['hours'] += effort
            
            # By priority
            if priority not in efforts['by_priority']:
                efforts['by_priority'][priority] = {'count': 0, 'hours': 0}
            efforts['by_priority'][priority]['count'] += 1
            efforts['by_priority'][priority]['hours'] += effort
            
            # Details
            efforts['requirements_details'].append({
                'req_id': req.get('id'),
                'description': req.get('text', '')[:100],
                'type': req_type,
                'priority': priority,
                'estimated_hours': effort,
            })
        
        logger.info(f"Total project effort: {efforts['total_hours']} hours")
        return efforts

    def calculate_cost(self, total_hours: float, hourly_rate: float = None, 
                      include_markup: bool = True) -> Dict:
        """
        Calculate project cost

        Args:
            total_hours: Total estimated hours
            hourly_rate: Hourly rate (uses senior rate if not specified)
            include_markup: Whether to include markup percentage

        Returns:
            Dictionary with cost breakdown
        """
        if hourly_rate is None:
            hourly_rate = self.hourly_rates['senior']
        
        base_cost = total_hours * hourly_rate
        
        if include_markup:
            markup_amount = base_cost * (self.markup_percentage / 100)
            total_cost = base_cost + markup_amount
        else:
            markup_amount = 0
            total_cost = base_cost
        
        return {
            'total_hours': total_hours,
            'hourly_rate': hourly_rate,
            'base_cost': round(base_cost, 2),
            'markup_percentage': self.markup_percentage if include_markup else 0,
            'markup_amount': round(markup_amount, 2),
            'total_cost': round(total_cost, 2),
        }

    def generate_pricing_proposal(self, requirements: List[Dict], 
                                 company_name: str = "Your Company",
                                 project_name: str = "RFP Response") -> Dict:
        """
        Generate comprehensive pricing proposal

        Args:
            requirements: List of requirements
            company_name: Your company name
            project_name: Project name

        Returns:
            Complete pricing proposal
        """
        # Estimate effort
        effort_breakdown = self.estimate_total_project_effort(requirements)
        total_hours = effort_breakdown['total_hours']
        
        # Calculate different cost scenarios
        scenarios = {}
        for level, rate in self.hourly_rates.items():
            scenarios[level] = self.calculate_cost(total_hours, rate, include_markup=True)
        
        # Create detailed line items
        line_items = self._create_line_items(requirements, effort_breakdown)
        
        proposal = {
            'timestamp': datetime.now().isoformat(),
            'company_name': company_name,
            'project_name': project_name,
            'summary': {
                'total_requirements': len(requirements),
                'total_estimated_hours': round(total_hours, 2),
            },
            'effort_breakdown': effort_breakdown,
            'cost_scenarios': scenarios,
            'recommended_rate': 'senior',
            'recommended_cost': scenarios['senior']['total_cost'],
            'line_items': line_items,
            'assumptions': self._get_assumptions(),
            'payment_terms': self._get_payment_terms(),
        }
        
        logger.info("Generated pricing proposal")
        return proposal

    def _create_line_items(self, requirements: List[Dict], 
                          effort_breakdown: Dict) -> List[Dict]:
        """Create detailed line items for proposal"""
        line_items = []
        item_number = 1
        
        # Group by type
        for req_type, type_data in effort_breakdown['by_type'].items():
            if type_data['hours'] > 0:
                rate = self.hourly_rates['senior']
                cost = type_data['hours'] * rate
                markup = cost * (self.markup_percentage / 100)
                
                line_items.append({
                    'item_number': item_number,
                    'description': f"{req_type.replace('_', ' ').title()} Development",
                    'quantity': type_data['count'],
                    'hours': round(type_data['hours'], 2),
                    'unit_rate': rate,
                    'base_cost': round(cost, 2),
                    'markup': round(markup, 2),
                    'total_cost': round(cost + markup, 2),
                })
                item_number += 1
        
        # Add contingency
        total_before_contingency = sum(li['total_cost'] for li in line_items)
        contingency = total_before_contingency * 0.15  # 15% contingency
        
        line_items.append({
            'item_number': item_number,
            'description': 'Contingency (15%)',
            'quantity': 1,
            'hours': 0,
            'unit_rate': 0,
            'base_cost': 0,
            'markup': 0,
            'total_cost': round(contingency, 2),
        })
        
        return line_items

    def _get_assumptions(self) -> List[str]:
        """Get standard assumptions for proposal"""
        return [
            "Estimates are based on the requirements extracted from the RFP document",
            "Team availability is assumed to be 8 hours per business day",
            "Includes development, testing, and documentation",
            "Does not include dedicated project management (can be added if required)",
            "Assumes standard scope and no major requirement changes",
            "Excludes third-party licensing costs",
            "Assumes access to necessary tools and infrastructure",
        ]

    def _get_payment_terms(self) -> Dict:
        """Get standard payment terms"""
        return {
            'structure': 'Milestone-based',
            'milestones': [
                {'name': 'Project Kickoff', 'percentage': 20},
                {'name': 'Initial Development', 'percentage': 30},
                {'name': 'Integration & Testing', 'percentage': 30},
                {'name': 'Deployment & Handover', 'percentage': 20},
            ],
            'invoice_terms': 'Net 30',
            'acceptance_criteria': 'Requirements met and tested',
        }

    def estimate_timeline(self, total_hours: float, team_size: int = 3, 
                         hours_per_day: float = 8.0) -> Dict:
        """
        Estimate project timeline

        Args:
            total_hours: Total estimated hours
            team_size: Number of team members
            hours_per_day: Billable hours per day per person

        Returns:
            Timeline dictionary
        """
        daily_capacity = team_size * hours_per_day
        calendar_days = (total_hours / daily_capacity) * 1.3  # Add 30% buffer
        business_days = calendar_days * 0.7  # Approximate business day ratio
        
        # Add holidays/vacation (10 days)
        business_days += 10
        
        weeks = business_days / 5
        months = weeks / 4.33
        
        start_date = datetime.now()
        end_date = start_date + timedelta(days=calendar_days)
        
        return {
            'total_hours': total_hours,
            'team_size': team_size,
            'hours_per_day_per_person': hours_per_day,
            'daily_capacity_hours': daily_capacity,
            'estimated_calendar_days': round(calendar_days, 1),
            'estimated_business_days': round(business_days, 1),
            'estimated_weeks': round(weeks, 1),
            'estimated_months': round(months, 2),
            'start_date': start_date.strftime('%Y-%m-%d'),
            'estimated_end_date': end_date.strftime('%Y-%m-%d'),
        }


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    estimator = CostEstimator()
    
    # Sample requirements
    sample_reqs = [
        {'id': 1, 'type': 'functional', 'priority': 'critical', 'text': 'User auth'},
        {'id': 2, 'type': 'performance', 'priority': 'high', 'text': 'Low latency'},
        {'id': 3, 'type': 'security', 'priority': 'critical', 'text': 'Encryption'},
    ]
    
    proposal = estimator.generate_pricing_proposal(sample_reqs)
    print(json.dumps(proposal, indent=2))
