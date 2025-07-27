# Financial Health Score Agent 💪📊

## Overview

The **Financial Health Score Agent** is an AI-powered financial wellness assessment tool that transforms complex financial data into a single, actionable score (0-1000 scale, similar to credit scores). Unlike traditional financial advisors that focus on investments, this agent provides a holistic view of financial health across multiple dimensions.

## 🎯 Core Capabilities

### 📊 **Comprehensive Health Scoring (0-1000 Scale)**
- **Liquidity Ratio** (25% weight) - Emergency fund coverage analysis
- **Savings Rate** (20% weight) - Income management efficiency  
- **Net Worth Growth** (15% weight) - Wealth building trajectory
- **Spending Stability** (15% weight) - Financial discipline assessment
- **Retirement Readiness** (10% weight) - Long-term planning evaluation
- **Diversification Score** (10% weight) - Investment portfolio spread
- **Employment Stability** (5% weight) - Income security analysis

### 📈 **Week-wise Trend Analysis**
- Historical financial health progression (up to 8 weeks)
- Pattern recognition in spending and income behaviors
- Predictive modeling for future score trajectories
- Visual charts and graphs for trend visualization

### 🎯 **Actionable Improvement Plans**
- SMART (Specific, Measurable, Achievable, Relevant, Time-bound) recommendations
- Prioritized action items by impact potential
- Quick wins (0-3 months) vs. long-term strategies (1+ years)
- Expected score improvement quantification

## 🏗️ Architecture

### Agent Structure
```
🏆 Financial Health Score Agent (Main Coordinator)
├── 📊 Fi MCP Integration (Real-time financial data)
├── 🧮 Financial Health Calculator (Core scoring engine)
├── 📈 Trend Analyzer Sub-Agent (Week-wise analysis)
└── 🎯 Recommendation Engine Sub-Agent (Action plans)
```

### Scoring Algorithm
```python
FHS = Σ(Factor_Score × Weight) × 10  # Normalized to 1000 scale

Key Factors:
- Liquidity: liquid_assets / monthly_expenses (months coverage)
- Savings: (income - expenses) / income (percentage)
- Stability: coefficient_of_variation(weekly_expenses) 
- Growth: month_over_month_net_worth_change
- Retirement: epf_balance / (age × annual_salary)
- Diversification: count(asset_types) + risk_spread
- Employment: employment_status + income_consistency
```

## 📊 **Expected Scores by Profile**

| Score Range | Grade | Financial Health Level | Typical Profile |
|-------------|-------|----------------------|-----------------|
| 851-1000 | A+ | Excellent | High savings rate, diversified portfolio, 6+ months emergency fund |
| 701-850 | A | Very Good | Good savings, some investments, 3-6 months emergency fund |
| 501-700 | B | Good | Moderate savings, basic emergency fund, steady employment |
| 301-500 | C | Needs Improvement | Low savings, minimal emergency fund, irregular income |
| 0-300 | D | Critical | High expenses, no emergency fund, financial instability |

## 🔧 **Sample Analysis Output**

```
🏆 Your Financial Health Score: 456/1000

Grade: B (Good)
You're on the right track! With some focused improvements, 
you could reach 650+ within 6 months.

📊 Score Breakdown:
Factor                Weight    Your Score    Grade
Liquidity Ratio       25%       30/100        Poor
Savings Rate          20%       65/100        Good
Net Worth Growth      15%       60/100        Fair
Spending Stability    15%       80/100        Good
Retirement Readiness  10%       70/100        Good
Diversification       10%       25/100        Poor
Employment Stability   5%       40/100        Poor

🎯 QUICK WINS (Next 3 Months) - Score Impact: +65 points
1. Emergency Fund Sprint (+40 points)
   - Save ₹2,000/week for 12 weeks
   - Target: ₹24,000 emergency fund

2. Expense Optimization (+25 points)
   - Reduce food delivery by 50%
   - Track all expenses weekly

📈 Week-wise Trend Analysis:
Week 1: 445 ↗️ (Salary received)
Week 2: 441 ↘️ (High expenses)
Week 3: 456 ↗️ (Controlled spending)
Week 4: 451 ↘️ (Unexpected expense)

Trend: Stable with +2.5 points/week average growth
```

## 🚀 **Setup and Installation**

### Prerequisites
- Python 3.9+
- Google Cloud Platform project
- Fi MCP access credentials
- Google Cloud CLI

### Installation
```bash
# Clone the project
cd financial_health_score_agent

# Install dependencies
pip install -e .

# Set up environment variables
export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_PROJECT=<your-project-id>
export GOOGLE_CLOUD_LOCATION=<your-project-location>

# Authenticate Google Cloud
gcloud auth application-default login
```

### Running the Agent
```bash
# Using ADK CLI
adk run financial_health_score_agent

# Using ADK Web Interface
adk web
```

## 📊 **Data Sources & Requirements**

### Fi MCP Integration
The agent requires access to Fi MCP (Financial Model Context Protocol) for:

**Essential Data:**
- Net worth breakdown (assets/liabilities)
- Bank transaction history (2+ months recommended)
- EPF/retirement account details

**Optional Data (Enhances Scoring):**
- Investment portfolio details
- Credit report information
- Insurance coverage details

**Sample Data Structure:**
```json
{
  "net_worth": {
    "totalNetWorthValue": {"currencyCode": "INR", "units": "250750"},
    "assetValues": [
      {"netWorthAttribute": "ASSET_TYPE_SAVINGS_ACCOUNTS", "value": {"units": "15750"}},
      {"netWorthAttribute": "ASSET_TYPE_EPF", "value": {"units": "235000"}}
    ]
  },
  "transactions": {
    "bankTransactions": [{
      "bank": "Punjab National Bank",
      "txns": [
        ["2500", "UPI-PAYMENT", "2024-07-02", 1, "FT", "16500"]
      ]
    }]
  }
}
```

## 🎯 **Handling Limited Data**

The agent is designed to work effectively even with limited financial data:

### With Basic Data (Net Worth + Some Transactions)
- **Confidence Level**: Medium
- **Available Features**: Core scoring, basic recommendations
- **Limitations**: Limited trend analysis, conservative projections

### With Comprehensive Data (2+ Months Transactions)
- **Confidence Level**: High  
- **Available Features**: Full scoring, detailed trends, precise recommendations
- **Enhanced Accuracy**: Week-wise analysis, pattern recognition

### Data Quality Indicators
```python
def assess_data_quality(financial_data):
    if transaction_months >= 2 and has_complete_net_worth:
        return "HIGH_CONFIDENCE"
    elif has_basic_transactions and has_net_worth:
        return "MEDIUM_CONFIDENCE"  
    else:
        return "LOW_CONFIDENCE"
```

## 🔮 **Week-wise Graph Generation**

### With Limited Data Strategy

**1. Transaction-based Reconstruction:**
```python
# Extract weekly patterns from available transaction data
weekly_balances = extract_balance_progression(transactions)
weekly_expenses = calculate_weekly_expenses(transactions)
weekly_scores = [calculate_weekly_fhs(balance, expense) for balance, expense in zip(weekly_balances, weekly_expenses)]
```

**2. Intelligent Interpolation:**
- Use transaction patterns to fill data gaps
- Apply smoothing algorithms for outliers
- Maintain realistic score variations (±5-15% weekly)

**3. Visual Representation:**
```
Financial Health Score Trend (8 weeks)

Score
 500 ┤    ●
 475 ┤  ●   ●
 450 ┤●       ●
 425 ┤         ○ (projected)
 400 ┤           ○
     └─────────────────────────
     W1 W2 W3 W4 W5 W6 W7 W8

Legend: ● Actual  ○ Projected
Trend: Stable (+2.5 pts/week)
```

## 🚀 **Future Enhancements**

### Planned Features
- **Credit Score Integration**: Incorporate credit bureau data
- **Goal-based Scoring**: Customize weights based on user financial goals  
- **Peer Comparison**: Anonymous benchmarking against similar profiles
- **Automated Alerts**: Proactive notifications for score changes
- **Mobile App Integration**: Real-time score tracking

### Advanced Analytics
- **Machine Learning Models**: Predictive scoring using historical patterns
- **Behavioral Analysis**: Spending categorization and insights
- **Scenario Planning**: "What-if" analysis for major financial decisions

## 📝 **Contributing**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 **License**

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## 🤝 **Support**

For questions or support:
- 📧 Email: financial-health-support@example.com
- 📖 Documentation: [Link to detailed docs]
- 🐛 Issues: [GitHub Issues page]

---

**Disclaimer**: This tool provides educational financial insights and should not be considered as professional financial advice. Always consult with qualified financial advisors for important financial decisions. 