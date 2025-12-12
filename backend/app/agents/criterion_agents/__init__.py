"""
Criterion-Specific Agents
Specialized agents for each EB-1A criterion
"""
from .critical_role_agent import CriticalRoleAgent
from .original_contribution_agent import OriginalContributionAgent

__all__ = [
    "CriticalRoleAgent",
    "OriginalContributionAgent"
]
