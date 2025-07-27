"""Direct MCP Data Parser and Score Calculator - Requires Valid Fi MCP Data"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import statistics


class MCPDataValidationError(Exception):
    """Raised when Fi MCP data is missing or invalid"""
    pass


class DirectMCPCalculator:
    """
    Direct calculator that parses MCP data structure and calculates scores
    using hardcoded formulas - REQUIRES valid Fi MCP data
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
    
    def calculate_fhs_from_mcp(self, mcp_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main function: Parse MCP data and calculate Financial Health Score
        REQUIRES valid Fi MCP data - will raise exception if data is missing/invalid
        """
        # Validate that we have the required MCP data sections
        self._validate_mcp_data(mcp_data)
        
        try:
            # Parse the MCP data structure
            parsed_metrics = self._parse_mcp_structure(mcp_data)
            
            # Validate parsed metrics have required values
            self._validate_parsed_metrics(parsed_metrics)
            
            # Calculate individual factor scores using hardcoded rules
            factor_scores = self._calculate_all_factors(parsed_metrics)
            
            # Calculate weighted overall score
            overall_score = self._calculate_weighted_score(factor_scores)
            
            # Generate grade and category
            grade_info = self._get_grade_category(overall_score)
            
            # Generate actionable recommendations
            recommendations = self._generate_recommendations(factor_scores, parsed_metrics)
            
            return {
                'overall_score': overall_score,
                'grade': grade_info['grade'],
                'category': grade_info['category'],
                'score_range': grade_info['range'],
                'factor_breakdown': self._format_factor_breakdown(factor_scores),
                'recommendations': recommendations,
                'parsed_metrics': parsed_metrics,
                'calculation_method': 'direct_mcp_parsing',
                'data_source': 'fi_mcp_live_data'
            }
            
        except Exception as e:
            raise MCPDataValidationError(f"Financial Health Score calculation failed: {str(e)}")
    
    def _validate_mcp_data(self, mcp_data: Dict[str, Any]) -> None:
        """Validate that required MCP data sections are present"""
        if not mcp_data:
            raise MCPDataValidationError("No Fi MCP data provided")
        
        required_sections = ['net_worth', 'transactions']
        missing_sections = [section for section in required_sections if section not in mcp_data]
        
        if missing_sections:
            raise MCPDataValidationError(f"Missing required Fi MCP data sections: {missing_sections}")
        
        # Validate net_worth data structure
        if 'netWorthResponse' not in mcp_data.get('net_worth', {}):
            raise MCPDataValidationError("Invalid net_worth data structure - missing netWorthResponse")
        
        # Validate transactions data
        if not mcp_data.get('transactions'):
            raise MCPDataValidationError("No transaction data available for income/expense calculation")
    
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
        net_worth = mcp_data['net_worth']
        nw_response = net_worth['netWorthResponse']
        
        # Extract total net worth
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
        income, expenses = self._calculate_monthly_income_expenses(mcp_data['transactions'])
        metrics['monthly_income'] = income
        metrics['monthly_expenses'] = expenses
        
        # Parse EPF data (additional to net worth EPF)
        if 'epf' in mcp_data:
            epf_balance = self._extract_epf_balance(mcp_data['epf'])
            if epf_balance > metrics['epf_balance']:  # Use higher value
                metrics['epf_balance'] = epf_balance
        
        return metrics
    
    def _validate_parsed_metrics(self, metrics: Dict[str, Any]) -> None:
        """Validate that parsed metrics contain sufficient data for calculation"""
        # Check for critical data points
        if metrics['monthly_expenses'] <= 0:
            raise MCPDataValidationError("No valid expense data found in transactions - cannot calculate liquidity or savings rate")
        
        if metrics['monthly_income'] <= 0:
            raise MCPDataValidationError("No valid income data found in transactions - cannot calculate financial health score")
        
        if metrics['total_assets'] <= 0 and metrics['total_liabilities'] <= 0:
            raise MCPDataValidationError("No valid asset or liability data found - cannot assess net worth")
    
    def _calculate_monthly_income_expenses(self, transactions_data: Dict[str, Any]) -> tuple:
        """Calculate monthly income and expenses from transaction data"""
        if not transactions_data or 'transactionResponse' not in transactions_data:
            raise MCPDataValidationError("Invalid transaction data structure")
        
        transactions = transactions_data['transactionResponse'].get('transactions', [])
        if not transactions:
            raise MCPDataValidationError("No transactions found in data")
        
        # Calculate income and expenses from last 3 months of transactions
        recent_transactions = transactions[-90:] if len(transactions) > 90 else transactions
        
        total_income = 0
        total_expenses = 0
        months_count = 1  # Default to 1 to avoid division by zero
        
        for transaction in recent_transactions:
            amount = float(transaction.get('amount', {}).get('units', 0))
            if amount > 0:
                total_income += amount
            else:
                total_expenses += abs(amount)
        
        # Calculate monthly averages
        monthly_income = total_income / max(1, len(recent_transactions) // 30)
        monthly_expenses = total_expenses / max(1, len(recent_transactions) // 30)
        
        return monthly_income, monthly_expenses
    
    def _extract_epf_balance(self, epf_data: Dict[str, Any]) -> float:
        """Extract EPF balance from EPF data structure"""
        total_epf = 0
        
        if 'uanAccounts' in epf_data:
            for account in epf_data['uanAccounts']:
                raw_details = account.get('rawDetails', {})
                overall_balance = raw_details.get('overall_pf_balance', {})
                pf_balance = float(overall_balance.get('current_pf_balance', 0))
                total_epf += pf_balance
        
        return total_epf
    
    def _calculate_all_factors(self, metrics: Dict[str, Any]) -> Dict[str, float]:
        """Calculate all 7 factor scores using hardcoded business rules"""
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
            raise MCPDataValidationError("No asset data available for net worth calculation")
        
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
            raise MCPDataValidationError("No income detected - cannot assess employment stability")
    
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
        """Format factor scores for output"""
        factor_names = {
            'liquidity_ratio': '💧 Liquidity Essence',
            'savings_rate': '💰 Savings Spirit',
            'net_worth_growth': '📈 Growth Aura',
            'spending_stability': '⚖️ Stability Force',
            'retirement_readiness': '🏛️ Future Wisdom',
            'diversification_score': '🌌 Diversification Power',
            'employment_stability': '⚡ Employment Foundation'
        }
        
        breakdown = []
        for factor, score in factor_scores.items():
            breakdown.append({
                'factor': factor_names.get(factor, factor),
                'score': round(score, 1),
                'weight': int(self.weights[factor] * 100)
            })
        
        return breakdown
    
    def _generate_recommendations(self, factor_scores: Dict[str, float], metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on scores and metrics"""
        recommendations = []
        
        # Liquidity recommendations
        if factor_scores['liquidity_ratio'] < 70:
            months_coverage = metrics['liquid_cash'] / metrics['monthly_expenses']
            target_amount = max(0, (6 - months_coverage) * metrics['monthly_expenses'])
            recommendations.append({
                'category': 'Emergency Fund',
                'priority': 'High',
                'recommendation': f"Build emergency fund by ₹{target_amount:,.0f} to reach 6 months of expenses",
                'current_status': f"{months_coverage:.1f} months coverage"
            })
        
        # Savings recommendations
        if factor_scores['savings_rate'] < 60:
            current_rate = ((metrics['monthly_income'] - metrics['monthly_expenses']) / metrics['monthly_income']) * 100
            recommendations.append({
                'category': 'Savings Rate',
                'priority': 'High',
                'recommendation': f"Increase savings rate from {current_rate:.1f}% to at least 20%",
                'current_status': f"Currently saving ₹{metrics['monthly_income'] - metrics['monthly_expenses']:,.0f}/month"
            })
        
        # Diversification recommendations
        if factor_scores['diversification_score'] < 70:
            recommendations.append({
                'category': 'Investment Diversification',
                'priority': 'Medium',
                'recommendation': f"Diversify investments across more asset classes (currently {metrics['asset_types_count']} types)",
                'current_status': f"Total investment value: ₹{metrics['investment_value']:,.0f}"
            })
        
        return recommendations


# Initialize calculator instance
direct_calculator = DirectMCPCalculator()

def calculate_fhs_direct(mcp_data: Dict[str, Any]) -> Dict[str, Any]:
    """Direct calculation function for use by agent tools"""
    return direct_calculator.calculate_fhs_from_mcp(mcp_data) 