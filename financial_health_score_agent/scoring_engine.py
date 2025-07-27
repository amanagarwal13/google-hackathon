"""Financial Health Score Calculation Engine"""

from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
import random
import math


class FinancialHealthCalculator:
    """Calculate comprehensive Financial Health Score (0-1000)"""
    
    def __init__(self):
        # Score weights for different factors
        self.weights = {
            'liquidity_ratio': 0.25,      # Emergency fund coverage
            'savings_rate': 0.20,          # Monthly savings percentage
            'net_worth_growth': 0.15,      # Wealth building trajectory
            'spending_stability': 0.15,    # Spending pattern consistency
            'retirement_readiness': 0.10,  # Long-term planning
            'diversification_score': 0.10, # Investment diversification
            'employment_stability': 0.05   # Income security
        }
        
    def calculate_financial_health_score(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Financial Health Score based on comprehensive financial data"""
        
        # Extract key financial metrics from preprocessed data
        metrics = self._extract_financial_metrics(financial_data)
        
        # Calculate individual factor scores
        factor_scores = {
            'liquidity_ratio': self._calculate_liquidity_score(metrics),
            'savings_rate': self._calculate_savings_score(metrics),
            'net_worth_growth': self._calculate_net_worth_score(metrics),
            'spending_stability': self._calculate_spending_stability_score(metrics),
            'retirement_readiness': self._calculate_retirement_score(metrics),
            'diversification_score': self._calculate_diversification_score(metrics),
            'employment_stability': self._calculate_employment_score(metrics)
        }
        
        # Calculate weighted overall score
        overall_score = sum(
            factor_scores[factor] * self.weights[factor] 
            for factor in factor_scores
        )
        
        # Scale to 0-1000
        overall_score = int(overall_score * 10)
        
        # Determine score grade
        score_grade = self._get_score_grade(overall_score)
        
        # Generate week-wise analysis (simulated for now)
        week_wise_analysis = self._generate_week_wise_analysis(overall_score, factor_scores)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(factor_scores, metrics)
        
        return {
            'overall_score': overall_score,
            'score_grade': score_grade,
            'factor_breakdown': self._format_factor_breakdown(factor_scores),
            'week_wise_analysis': week_wise_analysis,
            'recommendations': recommendations,
            'financial_summary': metrics
        }
    
    def _extract_financial_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key metrics from preprocessed financial data"""
        metrics = {
            'total_assets': 0,
            'total_liabilities': 0,
            'net_worth': 0,
            'monthly_income': 0,
            'monthly_expenses': 0,
            'monthly_savings': 0,
            'savings_rate': 0,
            'liquid_assets': 0,
            'investment_value': 0,
            'epf_balance': 0,
            'asset_types': []
        }
        
        # Extract from net worth summary
        if 'net_worth' in data:
            nw_data = data['net_worth']
            metrics['total_assets'] = nw_data.get('total_assets', 0)
            metrics['total_liabilities'] = nw_data.get('total_liabilities', 0)
            metrics['net_worth'] = nw_data.get('total_net_worth', 0)
            
            # Liquid assets (savings + current accounts)
            account_summary = nw_data.get('account_summary', {})
            metrics['liquid_assets'] = (
                account_summary.get('savings_accounts', {}).get('total_balance', 0) +
                account_summary.get('current_accounts', {}).get('total_balance', 0)
            )
            
            # Investment value
            metrics['investment_value'] = account_summary.get('investment_accounts', {}).get('total_value', 0)
            
            # Add mutual fund value
            if 'mutual_fund_summary' in nw_data:
                metrics['investment_value'] += nw_data['mutual_fund_summary'].get('total_current_value', 0)
            
            # Asset types for diversification
            metrics['asset_types'] = list(nw_data.get('asset_breakdown', {}).keys())
        
        # Extract from transaction summary
        if 'transactions' in data:
            tx_data = data['transactions']
            overall = tx_data.get('overall_summary', {})
            metrics['monthly_income'] = overall.get('average_monthly_income', 0)
            metrics['monthly_expenses'] = overall.get('average_monthly_expenses', 0)
            metrics['monthly_savings'] = overall.get('net_monthly_cashflow', 0)
            
            # Calculate savings rate
            if metrics['monthly_income'] > 0:
                metrics['savings_rate'] = (metrics['monthly_savings'] / metrics['monthly_income']) * 100
        
        # Extract EPF data
        if 'epf' in data:
            epf_data = data['epf']
            metrics['epf_balance'] = epf_data.get('total_epf_balance', 0)
        
        return metrics
    
    def _calculate_liquidity_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate liquidity score based on emergency fund coverage"""
        if metrics['monthly_expenses'] == 0:
            return 50.0  # Default middle score if no expense data
        
        months_covered = metrics['liquid_assets'] / metrics['monthly_expenses']
        
        # Scoring: 6+ months = 100, 3 months = 70, 1 month = 40, 0 = 0
        if months_covered >= 6:
            return 100.0
        elif months_covered >= 3:
            return 70 + (months_covered - 3) * 10
        elif months_covered >= 1:
            return 40 + (months_covered - 1) * 15
        else:
            return months_covered * 40
    
    def _calculate_savings_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate savings score based on savings rate"""
        savings_rate = metrics['savings_rate']
        
        # Scoring: 30%+ = 100, 20% = 80, 10% = 60, 5% = 40, 0% = 20
        if savings_rate >= 30:
            return 100.0
        elif savings_rate >= 20:
            return 80 + (savings_rate - 20) * 2
        elif savings_rate >= 10:
            return 60 + (savings_rate - 10) * 2
        elif savings_rate >= 5:
            return 40 + (savings_rate - 5) * 4
        elif savings_rate >= 0:
            return 20 + savings_rate * 4
        else:
            return max(0, 20 + savings_rate)  # Negative savings rate
    
    def _calculate_net_worth_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate net worth growth score"""
        # For now, base it on debt-to-asset ratio
        if metrics['total_assets'] == 0:
            return 50.0
        
        debt_ratio = metrics['total_liabilities'] / metrics['total_assets']
        
        # Lower debt ratio = higher score
        if debt_ratio == 0:
            return 100.0
        elif debt_ratio <= 0.2:
            return 80 + (0.2 - debt_ratio) * 100
        elif debt_ratio <= 0.5:
            return 50 + (0.5 - debt_ratio) * 100
        else:
            return max(0, 50 - (debt_ratio - 0.5) * 100)
    
    def _calculate_spending_stability_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate spending stability score"""
        # For now, use a simple ratio of savings to income
        if metrics['monthly_income'] == 0:
            return 50.0
        
        # If saving consistently, good stability
        if metrics['monthly_savings'] > 0:
            return min(100, 70 + (metrics['savings_rate'] * 1.5))
        else:
            # Negative savings indicates instability
            return max(20, 50 + (metrics['savings_rate'] * 2))
    
    def _calculate_retirement_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate retirement readiness score"""
        # Simple calculation based on EPF balance relative to annual income
        if metrics['monthly_income'] == 0:
            return 30.0
        
        annual_income = metrics['monthly_income'] * 12
        retirement_ratio = metrics['epf_balance'] / annual_income if annual_income > 0 else 0
        
        # Scoring: 5+ years = 100, 3 years = 70, 1 year = 40
        if retirement_ratio >= 5:
            return 100.0
        elif retirement_ratio >= 3:
            return 70 + (retirement_ratio - 3) * 15
        elif retirement_ratio >= 1:
            return 40 + (retirement_ratio - 1) * 15
        else:
            return retirement_ratio * 40
    
    def _calculate_diversification_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate investment diversification score"""
        asset_types = len(metrics['asset_types'])
        
        # More asset types = better diversification
        if asset_types >= 5:
            return 100.0
        elif asset_types >= 3:
            return 70 + (asset_types - 3) * 15
        elif asset_types >= 1:
            return 40 + (asset_types - 1) * 15
        else:
            return 20.0
    
    def _calculate_employment_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate employment stability score"""
        # For now, base on income presence
        if metrics['monthly_income'] > 0:
            return 80.0  # Has income
        else:
            return 30.0  # No income detected
    
    def _get_score_grade(self, score: int) -> Dict[str, str]:
        """Determine grade based on score"""
        if score >= 900:
            return {'grade': 'A+', 'category': 'Excellent', 'range': '900-1000'}
        elif score >= 800:
            return {'grade': 'A', 'category': 'Very Good', 'range': '800-899'}
        elif score >= 700:
            return {'grade': 'B', 'category': 'Good', 'range': '700-799'}
        elif score >= 600:
            return {'grade': 'C', 'category': 'Fair', 'range': '600-699'}
        elif score >= 500:
            return {'grade': 'D', 'category': 'Needs Improvement', 'range': '500-599'}
        else:
            return {'grade': 'F', 'category': 'Poor', 'range': '0-499'}
    
    def _format_factor_breakdown(self, factor_scores: Dict[str, float]) -> List[Dict[str, Any]]:
        """Format factor scores for display"""
        breakdown = []
        for factor, score in factor_scores.items():
            breakdown.append({
                'factor': factor.replace('_', ' ').title(),
                'score': round(score, 1),
                'weight': f"{self.weights[factor] * 100:.0f}%",
                'weighted_score': round(score * self.weights[factor], 1),
                'grade': self._get_factor_grade(score)
            })
        return breakdown
    
    def _get_factor_grade(self, score: float) -> str:
        """Get grade for individual factor"""
        if score >= 90:
            return 'A+'
        elif score >= 80:
            return 'A'
        elif score >= 70:
            return 'B'
        elif score >= 60:
            return 'C'
        elif score >= 50:
            return 'D'
        else:
            return 'F'
    
    def _generate_week_wise_analysis(self, current_score: int, factor_scores: Dict[str, float]) -> List[Dict[str, Any]]:
        """Generate simulated week-wise analysis"""
        weeks = []
        base_score = current_score - random.randint(20, 50)  # Start from a lower score
        
        for week in range(8, 0, -1):
            # Simulate gradual improvement
            week_score = base_score + (current_score - base_score) * ((8 - week + 1) / 8)
            week_score += random.randint(-10, 10)  # Add some variation
            week_score = max(0, min(1000, int(week_score)))
            
            weeks.append({
                'week': f"Week {9-week}",
                'score': week_score,
                'change': week_score - (weeks[-1]['score'] if weeks else base_score),
                'health_indicator': self._get_health_indicator(week_score)
            })
        
        return weeks
    
    def _get_health_indicator(self, score: int) -> str:
        """Get health indicator for score"""
        if score >= 800:
            return 'Excellent'
        elif score >= 700:
            return 'Healthy'
        elif score >= 600:
            return 'Stable'
        elif score >= 500:
            return 'Moderate'
        else:
            return 'Concerning'
    
    def _generate_recommendations(self, factor_scores: Dict[str, float], metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate personalized recommendations"""
        recommendations = []
        
        # Check each factor and provide recommendations for low scores
        if factor_scores['liquidity_ratio'] < 70:
            recommendations.append({
                'priority': 'High',
                'category': 'Emergency Fund',
                'recommendation': f"Build emergency fund to cover 6 months of expenses (currently {metrics['liquid_assets']/metrics['monthly_expenses']:.1f} months)",
                'impact': '+50-100 points',
                'timeline': '3-6 months'
            })
        
        if factor_scores['savings_rate'] < 70:
            recommendations.append({
                'priority': 'High',
                'category': 'Savings Rate',
                'recommendation': f"Increase monthly savings to 20% of income (currently {metrics['savings_rate']:.1f}%)",
                'impact': '+40-80 points',
                'timeline': '1-3 months'
            })
        
        if factor_scores['diversification_score'] < 70:
            recommendations.append({
                'priority': 'Medium',
                'category': 'Investment Diversification',
                'recommendation': "Diversify investments across equity, debt, and other asset classes",
                'impact': '+30-60 points',
                'timeline': '3-6 months'
            })
        
        if factor_scores['retirement_readiness'] < 70:
            recommendations.append({
                'priority': 'Medium',
                'category': 'Retirement Planning',
                'recommendation': "Increase EPF/retirement contributions to build long-term wealth",
                'impact': '+20-40 points',
                'timeline': '6-12 months'
            })
        
        return recommendations 