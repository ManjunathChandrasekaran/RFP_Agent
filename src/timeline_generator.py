"""
Timeline Generator Module
Creates project timelines and Gantt charts
"""

import logging
from typing import Dict, List
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class TimelineGenerator:
    """Generate project timelines and schedules"""

    # Typical phases in software projects
    DEFAULT_PHASES = [
        {'name': 'Planning & Kickoff', 'percentage': 5},
        {'name': 'Requirements Analysis', 'percentage': 10},
        {'name': 'Design & Architecture', 'percentage': 15},
        {'name': 'Development', 'percentage': 40},
        {'name': 'Testing & QA', 'percentage': 15},
        {'name': 'Deployment & Go-Live', 'percentage': 10},
        {'name': 'Post-Launch Support', 'percentage': 5},
    ]

    def __init__(self):
        """Initialize timeline generator"""
        self.phases = []
        self.tasks = []

    def generate_timeline(self, total_days: float, team_size: int = 3) -> List[Dict]:
        """
        Generate project phases with dates

        Args:
            total_days: Total estimated project days
            team_size: Number of team members

        Returns:
            List of timeline phases
        """
        start_date = datetime.now()
        phases = []
        current_date = start_date
        
        for phase in self.DEFAULT_PHASES:
            phase_days = (total_days * phase['percentage']) / 100
            end_date = current_date + timedelta(days=phase_days)
            
            phases.append({
                'name': phase['name'],
                'start_date': current_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'duration_days': round(phase_days, 1),
                'percentage': phase['percentage'],
                'team_members': team_size,
                'status': 'planned',
            })
            
            current_date = end_date
        
        self.phases = phases
        logger.info(f"Generated timeline with {len(phases)} phases")
        return phases

    def generate_gantt_data(self, timeline: List[Dict]) -> Dict:
        """
        Generate Gantt chart data

        Args:
            timeline: Timeline phases

        Returns:
            Dictionary with Gantt chart data
        """
        gantt_data = {
            'title': 'Project Timeline',
            'tasks': [],
            'startDate': timeline[0]['start_date'] if timeline else '',
            'endDate': timeline[-1]['end_date'] if timeline else '',
        }
        
        for i, phase in enumerate(timeline, 1):
            task = {
                'id': str(i),
                'name': phase['name'],
                'startDate': phase['start_date'],
                'endDate': phase['end_date'],
                'duration': phase['duration_days'],
                'progress': 0,
                'dependencies': [str(i-1)] if i > 1 else [],
                'resourceAssigned': [f"Team Member {j}" for j in range(1, phase['team_members'] + 1)],
            }
            gantt_data['tasks'].append(task)
        
        return gantt_data

    def create_milestones(self, timeline: List[Dict]) -> List[Dict]:
        """
        Create key milestones from timeline

        Args:
            timeline: Timeline phases

        Returns:
            List of milestones
        """
        milestones = []
        
        key_phases = [0, 3, 5, 6]  # Key milestone positions
        
        for idx in key_phases:
            if idx < len(timeline):
                phase = timeline[idx]
                milestone = {
                    'name': f"{phase['name']} Complete",
                    'date': phase['end_date'],
                    'status': 'planned',
                    'deliverables': self._get_phase_deliverables(phase['name']),
                }
                milestones.append(milestone)
        
        return milestones

    def _get_phase_deliverables(self, phase_name: str) -> List[str]:
        """Get typical deliverables for a phase"""
        deliverables = {
            'Planning & Kickoff': ['Project Plan', 'Team Assignments', 'Communication Plan'],
            'Requirements Analysis': ['Requirements Document', 'Use Cases', 'Acceptance Criteria'],
            'Design & Architecture': ['System Architecture', 'Database Design', 'API Specifications'],
            'Development': ['Source Code', 'Build Documentation', 'API Implementation'],
            'Testing & QA': ['Test Reports', 'Bug Fixes', 'Quality Assurance Sign-off'],
            'Deployment & Go-Live': ['Deployment Plan', 'Release Notes', 'Production Setup'],
            'Post-Launch Support': ['Support Documentation', 'User Guides', 'Training Materials'],
        }
        
        return deliverables.get(phase_name, [])

    def generate_html_gantt(self, timeline: List[Dict], output_file: str = None) -> str:
        """
        Generate HTML Gantt chart

        Args:
            timeline: Timeline phases
            output_file: Optional output file path

        Returns:
            HTML string
        """
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Project Timeline - Gantt Chart</title>
            <script src="https://cdn.jsdelivr.net/npm/frappe-gantt@0.6.0/dist/frappe-gantt.min.js"></script>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/frappe-gantt@0.6.0/dist/frappe-gantt.css">
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .container { max-width: 1200px; margin: 0 auto; }
                h1 { color: #333; }
                .summary { background: #f5f5f5; padding: 15px; margin: 20px 0; border-radius: 5px; }
                table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background: #4CAF50; color: white; }
                tr:hover { background: #f5f5f5; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Project Timeline - Gantt Chart</h1>
                <div class="summary">
                    <strong>Project Duration:</strong> {start_date} to {end_date}<br>
                    <strong>Total Duration:</strong> {total_days} days<br>
                    <strong>Number of Phases:</strong> {num_phases}
                </div>
                
                <h2>Phase Details</h2>
                <table>
                    <tr>
                        <th>Phase</th>
                        <th>Start Date</th>
                        <th>End Date</th>
                        <th>Duration (days)</th>
                        <th>% of Project</th>
                    </tr>
        """
        
        if timeline:
            start_date = timeline[0]['start_date']
            end_date = timeline[-1]['end_date']
            total_days = sum(p['duration_days'] for p in timeline)
            
            html = html.format(
                start_date=start_date,
                end_date=end_date,
                total_days=round(total_days, 1),
                num_phases=len(timeline)
            )
            
            for phase in timeline:
                html += f"""
                    <tr>
                        <td>{phase['name']}</td>
                        <td>{phase['start_date']}</td>
                        <td>{phase['end_date']}</td>
                        <td>{phase['duration_days']}</td>
                        <td>{phase['percentage']}%</td>
                    </tr>
                """
        
        html += """
                </table>
                
                <h2>Gantt Chart</h2>
                <svg id="gantt"></svg>
                
                <script>
                    var tasks = [
        """
        
        for i, phase in enumerate(timeline, 1):
            deps = f"['{i-1}']" if i > 1 else "[]"
            html += f"""
                        {{
                            id: '{i}',
                            name: '{phase['name']}',
                            start: '{phase['start_date']}',
                            end: '{phase['end_date']}',
                            progress: 0,
                            dependencies: {deps}
                        }},
            """
        
        html += """
                    ];
                    
                    var gantt_chart = new Gantt("#gantt", tasks, {
                        on_click: function (task) {
                            console.log(task);
                        },
                        on_date_change: function(task, start, end) {
                            console.log(task, start, end);
                        },
                        on_progress_change: function(task, progress) {
                            console.log(task, progress);
                        },
                        on_assign: function(task, resources) {
                            console.log(task, resources);
                        },
                        view_modes: ['Quarter Day', 'Half Day', 'Day', 'Week', 'Month'],
                        column_width: 30,
                        step: 24,
                        bar_height: 30,
                        bar_corner_radius: 3,
                        arrow_curve: 5,
                        padding: 18,
                        view_mode: 'Week',
                        date_format: 'YYYY-MM-DD',
                        custom_popup_html: null
                    });
                </script>
            </div>
        </body>
        </html>
        """
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(html)
            logger.info(f"Generated Gantt chart HTML to {output_file}")
        
        return html

    def generate_resource_schedule(self, timeline: List[Dict], team_structure: Dict = None) -> List[Dict]:
        """
        Generate resource allocation schedule

        Args:
            timeline: Timeline phases
            team_structure: Team structure and roles

        Returns:
            Resource schedule
        """
        if team_structure is None:
            team_structure = {
                'technical_lead': 1,
                'senior_developers': 2,
                'junior_developers': 1,
                'qa_engineers': 1,
                'devops_engineer': 1,
            }
        
        schedule = []
        
        for phase in timeline:
            # Allocate resources based on phase
            allocation = {
                'phase': phase['name'],
                'start_date': phase['start_date'],
                'end_date': phase['end_date'],
                'team_members': self._allocate_team_members(phase['name'], team_structure),
                'total_allocation': sum(team_structure.values()),
            }
            schedule.append(allocation)
        
        return schedule

    def _allocate_team_members(self, phase: str, team: Dict) -> Dict:
        """Allocate team members based on phase needs"""
        # Default: minimal allocation
        allocation = {role: 0 for role in team.keys()}
        
        if 'Planning' in phase:
            allocation['technical_lead'] = 1
        elif 'Requirements' in phase:
            allocation['technical_lead'] = 1
            allocation['senior_developers'] = 1
        elif 'Design' in phase:
            allocation['technical_lead'] = 1
            allocation['senior_developers'] = 2
        elif 'Development' in phase:
            allocation['senior_developers'] = 1
            allocation['junior_developers'] = 1
            allocation['devops_engineer'] = 1
        elif 'Testing' in phase:
            allocation['qa_engineers'] = 1
            allocation['senior_developers'] = 1
        elif 'Deployment' in phase:
            allocation['technical_lead'] = 1
            allocation['devops_engineer'] = 1
        
        return allocation


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    generator = TimelineGenerator()
    
    # Generate 100-day project timeline
    timeline = generator.generate_timeline(total_days=100, team_size=5)
    
    print("Project Timeline:")
    for phase in timeline:
        print(f"  {phase['name']}: {phase['start_date']} to {phase['end_date']} ({phase['duration_days']} days)")
    
    # Generate Gantt chart
    generator.generate_html_gantt(timeline, './timeline.html')
    print("\nGenerated Gantt chart: ./timeline.html")
