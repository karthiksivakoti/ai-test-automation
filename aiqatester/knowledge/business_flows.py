# ai-test-automation/aiqatester/knowledge/business_flows.py
"""
Business Flows module for AIQATester.

This module defines the data structure for storing business flow information.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

@dataclass
class Step:
    """A single step in a business flow."""
    description: str
    page_url: str
    action_type: str  # click, input, select, etc.
    selector: Optional[str] = None
    input_value: Optional[str] = None
    expected_result: Optional[str] = None

@dataclass
class BusinessFlow:
    """Model for a business flow in a website."""
    name: str
    description: str
    priority: int = 1  # 1-5, with 5 being highest priority
    steps: List[Step] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    
    def add_step(self, step: Step) -> None:
        """Add a step to the business flow."""
        self.steps.append(step)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the business flow to a dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "priority": self.priority,
            "steps": [
                {
                    "description": step.description,
                    "page_url": step.page_url,
                    "action_type": step.action_type,
                    "selector": step.selector,
                    "input_value": step.input_value,
                    "expected_result": step.expected_result
                }
                for step in self.steps
            ],
            "prerequisites": self.prerequisites,
            "success_criteria": self.success_criteria
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BusinessFlow':
        """Create a business flow from a dictionary."""
        flow = cls(
            name=data["name"],
            description=data["description"],
            priority=data.get("priority", 1),
            prerequisites=data.get("prerequisites", []),
            success_criteria=data.get("success_criteria", [])
        )
        
        # Add steps
        for step_data in data.get("steps", []):
            step = Step(
                description=step_data["description"],
                page_url=step_data["page_url"],
                action_type=step_data["action_type"],
                selector=step_data.get("selector"),
                input_value=step_data.get("input_value"),
                expected_result=step_data.get("expected_result")
            )
            flow.add_step(step)
        
        return flow