"""Data preprocessor to summarize financial data for token limit compliance"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
import json


class FinancialDataPreprocessor:
    """Preprocesses and summarizes financial data to reduce token count"""
    
    def __init__(self):
        self.max_transactions_per_bank = 50  # Limit transactions per bank
        self.transaction_window_days = 60    # Focus on recent 60 days
        
    def preprocess_financial_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess financial data to reduce size while maintaining essential information
        """
        processed_data = {}
        
        # Process net worth data
        if 'net_worth' in raw_data:
            processed_data['net_worth'] = self._summarize_net_worth(raw_data['net_worth'])
            
        # Process transactions
        if 'transactions' in raw_data:
            processed_data['transactions'] = self._summarize_transactions(raw_data['transactions'])
            
        # Process EPF data
        if 'epf' in raw_data:
            processed_data['epf'] = self._summarize_epf(raw_data['epf'])
            
        return processed_data
    
    def _summarize_net_worth(self, net_worth_data: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize net worth data to essential information"""
        summary = {
            'total_net_worth': 0,
            'total_assets': 0,
            'total_liabilities': 0,
            'asset_breakdown': {},
            'liability_breakdown': {},
            'account_summary': {
                'total_accounts': 0,
                'savings_accounts': {'count': 0, 'total_balance': 0},
                'current_accounts': {'count': 0, 'total_balance': 0},
                'investment_accounts': {'count': 0, 'total_value': 0}
            }
        }
        
        # Extract net worth response
        if 'netWorthResponse' in net_worth_data:
            nw_response = net_worth_data['netWorthResponse']
            
            # Total net worth
            if 'totalNetWorthValue' in nw_response:
                summary['total_net_worth'] = float(nw_response['totalNetWorthValue'].get('units', 0))
            
            # Asset values
            if 'assetValues' in nw_response:
                for asset in nw_response['assetValues']:
                    asset_type = asset.get('netWorthAttribute', '').replace('ASSET_TYPE_', '')
                    value = float(asset.get('value', {}).get('units', 0))
                    summary['asset_breakdown'][asset_type] = value
                    summary['total_assets'] += value
            
            # Liability values
            if 'liabilityValues' in nw_response:
                for liability in nw_response['liabilityValues']:
                    liability_type = liability.get('netWorthAttribute', '').replace('LIABILITY_TYPE_', '')
                    value = float(liability.get('value', {}).get('units', 0))
                    summary['liability_breakdown'][liability_type] = value
                    summary['total_liabilities'] += value
        
        # Process account details
        if 'accountDetailsBulkResponse' in net_worth_data:
            accounts_map = net_worth_data['accountDetailsBulkResponse'].get('accountDetailsMap', {})
            
            for account_id, account_data in accounts_map.items():
                account_details = account_data.get('accountDetails', {})
                account_type = account_details.get('accountType', {})
                
                summary['account_summary']['total_accounts'] += 1
                
                # Process deposit accounts
                if 'depositAccountType' in account_type:
                    deposit_summary = account_data.get('depositSummary', {})
                    balance = float(deposit_summary.get('currentBalance', {}).get('units', 0))
                    
                    if account_type['depositAccountType'] == 'DEPOSIT_ACCOUNT_TYPE_SAVINGS':
                        summary['account_summary']['savings_accounts']['count'] += 1
                        summary['account_summary']['savings_accounts']['total_balance'] += balance
                    elif account_type['depositAccountType'] == 'DEPOSIT_ACCOUNT_TYPE_CURRENT':
                        summary['account_summary']['current_accounts']['count'] += 1
                        summary['account_summary']['current_accounts']['total_balance'] += balance
                
                # Process investment accounts (equity, ETF, etc.)
                elif any(key in account_data for key in ['equitySummary', 'etfSummary', 'reitSummary']):
                    summary['account_summary']['investment_accounts']['count'] += 1
                    
                    # Get current value from appropriate summary
                    for summary_key in ['equitySummary', 'etfSummary', 'reitSummary']:
                        if summary_key in account_data:
                            value = float(account_data[summary_key].get('currentValue', {}).get('units', 0))
                            summary['account_summary']['investment_accounts']['total_value'] += value
        
        # Process mutual fund data
        if 'mfSchemeAnalytics' in net_worth_data:
            mf_data = net_worth_data['mfSchemeAnalytics']
            if 'schemeAnalytics' in mf_data:
                total_mf_value = 0
                total_mf_invested = 0
                
                for scheme in mf_data['schemeAnalytics']:
                    analytics = scheme.get('enrichedAnalytics', {}).get('analytics', {}).get('schemeDetails', {})
                    current_value = float(analytics.get('currentValue', {}).get('units', 0))
                    invested_value = float(analytics.get('investedValue', {}).get('units', 0))
                    
                    total_mf_value += current_value
                    total_mf_invested += invested_value
                
                summary['mutual_fund_summary'] = {
                    'total_current_value': total_mf_value,
                    'total_invested_value': total_mf_invested,
                    'total_returns': total_mf_value - total_mf_invested,
                    'return_percentage': ((total_mf_value - total_mf_invested) / total_mf_invested * 100) if total_mf_invested > 0 else 0
                }
        
        return summary
    
    def _summarize_transactions(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize transaction data to reduce size"""
        summary = {
            'bank_summaries': {},
            'overall_summary': {
                'total_income': 0,
                'total_expenses': 0,
                'average_monthly_income': 0,
                'average_monthly_expenses': 0,
                'net_monthly_cashflow': 0
            }
        }
        
        if 'bankTransactions' in transaction_data:
            cutoff_date = datetime.now() - timedelta(days=self.transaction_window_days)
            
            for bank_data in transaction_data['bankTransactions']:
                bank_name = bank_data.get('bank', 'Unknown')
                transactions = bank_data.get('txns', [])
                
                # Process only recent transactions
                recent_transactions = []
                bank_income = 0
                bank_expenses = 0
                
                for txn in transactions[-self.max_transactions_per_bank:]:  # Limit number of transactions
                    try:
                        amount = float(txn[0])
                        txn_date = datetime.strptime(txn[2], '%Y-%m-%d')
                        txn_type = int(txn[3])  # 1=CREDIT, 2=DEBIT
                        
                        if txn_date >= cutoff_date:
                            if txn_type == 1:  # CREDIT
                                bank_income += amount
                            elif txn_type == 2:  # DEBIT
                                bank_expenses += amount
                            
                            recent_transactions.append({
                                'amount': amount,
                                'date': txn[2],
                                'type': 'CREDIT' if txn_type == 1 else 'DEBIT',
                                'narration': txn[1][:50]  # Limit narration length
                            })
                    except (ValueError, IndexError):
                        continue
                
                summary['bank_summaries'][bank_name] = {
                    'total_income': bank_income,
                    'total_expenses': bank_expenses,
                    'net_cashflow': bank_income - bank_expenses,
                    'transaction_count': len(recent_transactions),
                    'recent_transactions': recent_transactions[:10]  # Keep only 10 most recent
                }
                
                summary['overall_summary']['total_income'] += bank_income
                summary['overall_summary']['total_expenses'] += bank_expenses
        
        # Calculate monthly averages (assuming 2 months of data)
        months = self.transaction_window_days / 30
        summary['overall_summary']['average_monthly_income'] = summary['overall_summary']['total_income'] / months
        summary['overall_summary']['average_monthly_expenses'] = summary['overall_summary']['total_expenses'] / months
        summary['overall_summary']['net_monthly_cashflow'] = (
            summary['overall_summary']['average_monthly_income'] - 
            summary['overall_summary']['average_monthly_expenses']
        )
        
        return summary
    
    def _summarize_epf(self, epf_data: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize EPF data"""
        summary = {
            'total_epf_balance': 0,
            'pension_balance': 0,
            'employer_details': []
        }
        
        if 'uanAccounts' in epf_data:
            for account in epf_data['uanAccounts']:
                raw_details = account.get('rawDetails', {})
                
                # Get overall PF balance
                overall_balance = raw_details.get('overall_pf_balance', {})
                pf_balance = float(overall_balance.get('current_pf_balance', 0))
                pension_balance = float(overall_balance.get('pension_balance', 0))
                
                summary['total_epf_balance'] += pf_balance
                summary['pension_balance'] += pension_balance
                
                # Get employer details (simplified)
                if 'est_details' in raw_details:
                    for est in raw_details['est_details']:
                        employer_info = {
                            'employer_name': est.get('est_name', 'Unknown'),
                            'pf_balance': float(est.get('pf_balance', {}).get('net_balance', 0))
                        }
                        summary['employer_details'].append(employer_info)
        
        return summary


# Create a global preprocessor instance
preprocessor = FinancialDataPreprocessor()

def preprocess_financial_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """Global function to preprocess financial data"""
    return preprocessor.preprocess_financial_data(raw_data) 