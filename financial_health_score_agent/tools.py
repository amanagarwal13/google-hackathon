"""Financial Health Score Tools - Wrapper functions for ADK"""

from typing import Dict, Any, Optional
from .scoring_engine import FinancialHealthCalculator
from .visualization_engine import FinancialHealthVisualizer
from .mcp_direct_calculator import calculate_fhs_direct

# Initialize utility classes
_calculator = FinancialHealthCalculator()
_visualizer = FinancialHealthVisualizer()


def calculate_financial_health_score(financial_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate Financial Health Score using direct MCP parsing (no LLM processing).
    
    This function uses hardcoded business rules to parse MCP data structure 
    and calculate scores deterministically.
    """
    # Use direct MCP calculator instead of LLM processing
    return calculate_fhs_direct(financial_data)


def generate_weekly_trend_chart(score_data: Dict[str, Any], title: Optional[str] = None) -> Dict[str, Any]:
    """Generate a weekly trend chart showing Financial Health Score progression"""
    return _visualizer.generate_chart("weekly_trend", score_data, title)


def generate_factor_breakdown_chart(score_data: Dict[str, Any], title: Optional[str] = None) -> Dict[str, Any]:
    """Generate a factor breakdown chart showing individual factor scores"""
    return _visualizer.generate_chart("factor_breakdown", score_data, title)


def generate_improvement_projection_chart(score_data: Dict[str, Any], title: Optional[str] = None) -> Dict[str, Any]:
    """Generate an improvement projection chart showing potential score improvements"""
    return _visualizer.generate_chart("improvement_projection", score_data, title)


def generate_score_distribution_chart(score_data: Dict[str, Any], title: Optional[str] = None) -> Dict[str, Any]:
    """Generate a score distribution chart showing percentile ranking"""
    return _visualizer.generate_chart("score_distribution", score_data, title) 