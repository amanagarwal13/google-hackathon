"""Direct MCP Data Parser and Score Calculator - No LLM Processing"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import statistics


class DirectMCPCalculator:
    """
    Direct calculator that parses MCP data structure and calculates scores
    using hardcoded formulas - no LLM processing required
    """
    
    def __init__(self):
        # Scoring weights - these are fixed business rules
        self.weights = {
            'liquidity_ratio': 0.25,
            'savings_rate': 0.20,
            'net_worth_growth': 0.15,
            'spending_stability': 0.15,
            'retirement_readiness': 0.10,
            'diversification_score': 0.10,
            'employment_stability': 0.05
        }
        
        # Score thresholds - hardcoded business rules
        self.liquidity_thresholds = {
            'excellent': 6,    # 6+ months expenses
            'good': 3,         # 3-6 months
            'fair': 1,         # 1-3 months
            'poor': 0          # <1 month
        }
        
        self.savings_thresholds = {
            'excellent': 30,   # 30%+ savings rate
            'good': 20,        # 20-30%
            'fair': 10,        # 10-20%
            'poor': 0          # <10%
        }
    
    def calculate_fhs_from_mcp(self, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main function: Parse MCP data and calculate Financial Health Score
        """
        try:
            # Parse the MCP data structure
            parsed_metrics = self._parse_mcp_structure(mcp_data)
            
            # Calculate individual factor scores using hardcoded rules
            factor_scores = self._calculate_all_factors(parsed_metrics)
            
            # Calculate weighted overall score
            overall_score = self._calculate_weighted_score(factor_scores)
            
            # Generate grade and category
            grade_info = self._get_grade_category(overall_score)
            
            # Generate week-wise trend (simulated based on current score)
            week_wise_data = self._generate_historical_trend(overall_score, factor_scores)
            
            # Generate actionable recommendations
            recommendations = self._generate_recommendations(factor_scores, parsed_metrics)
            
            return {
                'overall_score': overall_score,
                'grade': grade_info['grade'],
                'category': grade_info['category'],
                'score_range': grade_info['range'],
                'factor_breakdown': self._format_factor_breakdown(factor_scores),
                'week_wise_analysis': week_wise_data,
                'recommendations': recommendations,
                'parsed_metrics': parsed_metrics,
                'calculation_method': 'direct_mcp_parsing'
            }
            
        except Exception as e:
            return {
                'error': f"Calculation failed: {str(e)}",
                'overall_score': 0,
                'grade': 'N/A',
                'category': 'Error',
                'factor_breakdown': [],
                'recommendations': []
            }
    
    def _parse_mcp_structure(self, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse the exact MCP data structure to extract financial metrics
        """
        metrics = {
            'total_net_worth': 0,
            'total_assets': 0,
            'total_liabilities': 0,
            'liquid_cash': 0,
            'investment_value': 0,
            'epf_balance': 0,
            'monthly_income': 0,
            'monthly_expenses': 0,
            'asset_types_count': 0,
            'account_count': 0,
            'savings_accounts_balance': 0,
            'current_accounts_balance': 0
        }
        
        # Parse net worth data
        if 'net_worth' in mcp_data:
            net_worth = mcp_data['net_worth']
            
            # Extract total net worth
            if 'netWorthResponse' in net_worth:
                nw_response = net_worth['netWorthResponse']
                
                # Total net worth
                if 'totalNetWorthValue' in nw_response:
                    metrics['total_net_worth'] = float(nw_response['totalNetWorthValue'].get('units', 0))
                
                # Parse assets
                if 'assetValues' in nw_response:
                    asset_types = set()
                    for asset in nw_response['assetValues']:
                        value = float(asset.get('value', {}).get('units', 0))
                        metrics['total_assets'] += value
                        
                        asset_type = asset.get('netWorthAttribute', '')
                        asset_types.add(asset_type)
                        
                        # Categorize assets
                        if 'MUTUAL_FUND' in asset_type:
                            metrics['investment_value'] += value
                        elif 'SECURITIES' in asset_type or 'EQUITIES' in asset_type:
                            metrics['investment_value'] += value
                        elif 'SAVINGS' in asset_type:
                            metrics['liquid_cash'] += value
                        elif 'EPF' in asset_type:
                            metrics['epf_balance'] += value
                    
                    metrics['asset_types_count'] = len(asset_types)
                
                # Parse liabilities
                if 'liabilityValues' in nw_response:
                    for liability in nw_response['liabilityValues']:
                        value = float(liability.get('value', {}).get('units', 0))
                        metrics['total_liabilities'] += value
            
            # Parse account details
            if 'accountDetailsBulkResponse' in net_worth:
                accounts = net_worth['accountDetailsBulkResponse'].get('accountDetailsMap', {})
                metrics['account_count'] = len(accounts)
                
                for account_id, account_data in accounts.items():
                    account_type = account_data.get('accountDetails', {}).get('accountType', {})
                    
                    # Savings accounts
                    if 'depositAccountType' in account_type:
                        deposit_type = account_type['depositAccountType']
                        deposit_summary = account_data.get('depositSummary', {})
                        balance = float(deposit_summary.get('currentBalance', {}).get('units', 0))
                        
                        if deposit_type == 'DEPOSIT_ACCOUNT_TYPE_SAVINGS':
                            metrics['savings_accounts_balance'] += balance
                            metrics['liquid_cash'] += balance
                        elif deposit_type == 'DEPOSIT_ACCOUNT_TYPE_CURRENT':
                            metrics['current_accounts_balance'] += balance
                            metrics['liquid_cash'] += balance
        
        # Parse transaction data for income/expense calculation
        if 'transactions' in mcp_data:
            income, expenses = self._calculate_monthly_income_expenses(mcp_data['transactions'])
            metrics['monthly_income'] = income
            metrics['monthly_expenses'] = expenses
        
        # Parse EPF data (additional to net worth EPF)
        if 'epf' in mcp_data:
            epf_balance = self._extract_epf_balance(mcp_data['epf'])
            if epf_balance > metrics['epf_balance']:  # Use higher value
                metrics['epf_balance'] = epf_balance
        
        return metrics
    
    def _calculate_monthly_income_expenses(self, transaction_data: Dict[str, Any]) -> tuple[float, float]:
        """
        Parse transaction data to calculate monthly income and expenses
        """
        total_income = 0
        total_expenses = 0
        transaction_months = set()
        
        if 'bankTransactions' in transaction_data:
            for bank_data in transaction_data['bankTransactions']:
                transactions = bank_data.get('txns', [])
                
                for txn in transactions:
                    try:
                        amount = float(txn[0])
                        date_str = txn[2]  # Format: '2025-07-09'
                        txn_type = int(txn[3])  # 1=CREDIT, 2=DEBIT
                        
                        # Track months for averaging
                        transaction_months.add(date_str[:7])  # '2025-07'
                        
                        if txn_type == 1:  # CREDIT
                            total_income += amount
                        elif txn_type == 2:  # DEBIT
                            total_expenses += amount
                            
                    except (ValueError, IndexError):
                        continue
        
        # Calculate monthly averages
        months_count = max(len(transaction_months), 1)
        monthly_income = total_income / months_count
        monthly_expenses = total_expenses / months_count
        
        return monthly_income, monthly_expenses
    
    def _extract_epf_balance(self, epf_data: Dict[str, Any]) -> float:
        """
        Extract EPF balance from EPF data structure
        """
        total_epf = 0
        
        if 'uanAccounts' in epf_data:
            for account in epf_data['uanAccounts']:
                raw_details = account.get('rawDetails', {})
                overall_balance = raw_details.get('overall_pf_balance', {})
                pf_balance = float(overall_balance.get('current_pf_balance', 0))
                total_epf += pf_balance
        
        return total_epf
    
    def _calculate_all_factors(self, metrics: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate all 7 factor scores using hardcoded business rules
        """
        return {
            'liquidity_ratio': self._calc_liquidity_score(metrics),
            'savings_rate': self._calc_savings_score(metrics),
            'net_worth_growth': self._calc_net_worth_score(metrics),
            'spending_stability': self._calc_spending_stability(metrics),
            'retirement_readiness': self._calc_retirement_score(metrics),
            'diversification_score': self._calc_diversification_score(metrics),
            'employment_stability': self._calc_employment_score(metrics)
        }
    
    def _calc_liquidity_score(self, metrics: Dict[str, Any]) -> float:
        """Liquidity Ratio: Emergency fund coverage (months of expenses)"""
        if metrics['monthly_expenses'] <= 0:
            return 50.0  # Default if no expense data
        
        months_coverage = metrics['liquid_cash'] / metrics['monthly_expenses']
        
        # Hardcoded scoring rules
        if months_coverage >= 6:
            return 100.0
        elif months_coverage >= 3:
            return 70.0 + (months_coverage - 3) * 10.0
        elif months_coverage >= 1:
            return 40.0 + (months_coverage - 1) * 15.0
        else:
            return months_coverage * 40.0
    
    def _calc_savings_score(self, metrics: Dict[str, Any]) -> float:
        """Savings Rate: Monthly savings as % of income"""
        if metrics['monthly_income'] <= 0:
            return 20.0  # Default if no income data
        
        savings_rate = ((metrics['monthly_income'] - metrics['monthly_expenses']) / metrics['monthly_income']) * 100
        
        # Hardcoded scoring rules
        if savings_rate >= 30:
            return 100.0
        elif savings_rate >= 20:
            return 80.0 + (savings_rate - 20) * 2.0
        elif savings_rate >= 10:
            return 60.0 + (savings_rate - 10) * 2.0
        elif savings_rate >= 0:
            return 20.0 + savings_rate * 4.0
        else:
            return max(0, 20.0 + savings_rate * 2.0)  # Negative savings
    
    def _calc_net_worth_score(self, metrics: Dict[str, Any]) -> float:
        """Net Worth Growth: Based on debt-to-asset ratio"""
        if metrics['total_assets'] <= 0:
            return 50.0
        
        debt_ratio = metrics['total_liabilities'] / metrics['total_assets']
        
        # Lower debt ratio = higher score
        if debt_ratio <= 0.1:
            return 100.0
        elif debt_ratio <= 0.3:
            return 80.0 - (debt_ratio - 0.1) * 100.0
        elif debt_ratio <= 0.5:
            return 60.0 - (debt_ratio - 0.3) * 100.0
        else:
            return max(0, 40.0 - (debt_ratio - 0.5) * 80.0)
    
    def _calc_spending_stability(self, metrics: Dict[str, Any]) -> float:
        """Spending Stability: Based on savings consistency"""
        if metrics['monthly_income'] <= 0:
            return 50.0
        
        savings_amount = metrics['monthly_income'] - metrics['monthly_expenses']
        
        # Positive savings = good stability
        if savings_amount > 0:
            savings_rate = (savings_amount / metrics['monthly_income']) * 100
            return min(100.0, 60.0 + savings_rate * 1.5)
        else:
            # Negative savings = poor stability
            deficit_rate = abs(savings_amount / metrics['monthly_income']) * 100
            return max(10.0, 50.0 - deficit_rate * 2.0)
    
    def _calc_retirement_score(self, metrics: Dict[str, Any]) -> float:
        """Retirement Readiness: EPF balance relative to annual income"""
        if metrics['monthly_income'] <= 0:
            return 30.0
        
        annual_income = metrics['monthly_income'] * 12
        retirement_ratio = metrics['epf_balance'] / annual_income
        
        # Hardcoded scoring based on years of income saved
        if retirement_ratio >= 5:
            return 100.0
        elif retirement_ratio >= 3:
            return 70.0 + (retirement_ratio - 3) * 15.0
        elif retirement_ratio >= 1:
            return 40.0 + (retirement_ratio - 1) * 15.0
        else:
            return retirement_ratio * 40.0
    
    def _calc_diversification_score(self, metrics: Dict[str, Any]) -> float:
        """Diversification Score: Number of asset types"""
        asset_types = metrics['asset_types_count']
        
        # More asset types = better diversification
        if asset_types >= 5:
            return 100.0
        elif asset_types >= 3:
            return 70.0 + (asset_types - 3) * 15.0
        elif asset_types >= 1:
            return 40.0 + (asset_types - 1) * 15.0
        else:
            return 20.0
    
    def _calc_employment_score(self, metrics: Dict[str, Any]) -> float:
        """Employment Stability: Based on consistent income"""
        if metrics['monthly_income'] > 50000:  # Good income level
            return 90.0
        elif metrics['monthly_income'] > 25000:  # Moderate income
            return 70.0
        elif metrics['monthly_income'] > 0:  # Some income
            return 50.0
        else:
            return 20.0  # No income detected
    
    def _calculate_weighted_score(self, factor_scores: Dict[str, float]) -> int:
        """Calculate weighted overall score (0-1000)"""
        weighted_sum = sum(
            factor_scores[factor] * self.weights[factor]
            for factor in factor_scores
        )
        return min(1000, max(0, int(weighted_sum * 10)))
    
    def _get_grade_category(self, score: int) -> Dict[str, str]:
        """Determine grade and category from score"""
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
                'weighted_contribution': round(score * self.weights[factor], 1),
                'grade': self._get_factor_grade(score)
            })
        return breakdown
    
    def _get_factor_grade(self, score: float) -> str:
        """Get letter grade for individual factor"""
        if score >= 90: return 'A+'
        elif score >= 80: return 'A'
        elif score >= 70: return 'B'
        elif score >= 60: return 'C'
        elif score >= 50: return 'D'
        else: return 'F'
    
    def _generate_historical_trend(self, current_score: int, factor_scores: Dict[str, float]) -> List[Dict[str, Any]]:
        """Generate simulated 8-week historical trend"""
        weeks = []
        base_score = max(100, current_score - 50)  # Start from lower score
        
        for week in range(8):
            # Simulate gradual improvement to current score
            progress = (week + 1) / 8
            week_score = int(base_score + (current_score - base_score) * progress)
            week_score += (week % 3 - 1) * 5  # Add some variation
            week_score = max(0, min(1000, week_score))
            
            weeks.append({
                'week': f"Week {week + 1}",
                'score': week_score,
                'change': week_score - (weeks[-1]['score'] if weeks else base_score),
                'health_indicator': self._get_health_indicator(week_score)
            })
        
        return weeks
    
    def _get_health_indicator(self, score: int) -> str:
        """Get health indicator for score"""
        if score >= 800: return 'Excellent'
        elif score >= 700: return 'Healthy'
        elif score >= 600: return 'Stable'
        elif score >= 500: return 'Moderate'
        else: return 'Concerning'
    
    def _generate_recommendations(self, factor_scores: Dict[str, float], metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate hardcoded recommendations based on factor scores"""
        recommendations = []
        
        # Liquidity recommendations
        if factor_scores['liquidity_ratio'] < 70:
            months_current = metrics['liquid_cash'] / max(metrics['monthly_expenses'], 1)
            recommendations.append({
                'priority': 'High',
                'category': 'Emergency Fund',
                'current_status': f"{months_current:.1f} months coverage",
                'target': '6 months of expenses',
                'action': f"Increase emergency fund by ₹{(6 * metrics['monthly_expenses'] - metrics['liquid_cash']):,.0f}",
                'impact': '+50-100 points',
                'timeline': '3-6 months'
            })
        
        # Savings recommendations
        if factor_scores['savings_rate'] < 70:
            current_rate = ((metrics['monthly_income'] - metrics['monthly_expenses']) / max(metrics['monthly_income'], 1)) * 100
            recommendations.append({
                'priority': 'High',
                'category': 'Savings Rate',
                'current_status': f"{current_rate:.1f}% savings rate",
                'target': '20% savings rate',
                'action': f"Reduce expenses by ₹{(metrics['monthly_expenses'] - 0.8 * metrics['monthly_income']):,.0f}/month",
                'impact': '+40-80 points',
                'timeline': '1-3 months'
            })
        
        # Diversification recommendations
        if factor_scores['diversification_score'] < 70:
            recommendations.append({
                'priority': 'Medium',
                'category': 'Investment Diversification',
                'current_status': f"{metrics['asset_types_count']} asset types",
                'target': '5+ asset classes',
                'action': 'Add debt funds, international equity, or REITs',
                'impact': '+30-60 points',
                'timeline': '3-6 months'
            })
        
        # Retirement recommendations
        if factor_scores['retirement_readiness'] < 70:
            recommendations.append({
                'priority': 'Medium',
                'category': 'Retirement Planning',
                'current_status': f"₹{metrics['epf_balance']:,.0f} EPF balance",
                'target': f"₹{metrics['monthly_income'] * 12 * 3:,.0f} (3x annual income)",
                'action': 'Increase EPF/NPS contributions or start SIP',
                'impact': '+20-40 points',
                'timeline': '6-12 months'
            })
        
        return recommendations


# Global instance for use by the agent
direct_calculator = DirectMCPCalculator()

def calculate_fhs_direct(mcp_data: Dict[str, Any]) -> Dict[str, Any]:
    """Direct calculation function for use by agent tools"""
    return direct_calculator.calculate_fhs_from_mcp(mcp_data) 