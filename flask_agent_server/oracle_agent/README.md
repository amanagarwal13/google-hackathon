# The Oracle Agent - Predictive Financial Twin System

## Overview

The Oracle is a highly advanced financial prediction agent that can simulate thousands of possible futures based on a user's complete financial DNA. Unlike traditional financial advisors that analyze past performance, The Oracle sees through time, understanding how every financial decision ripples into the future.

## Core Capabilities

### 🔮 **Financial Future Simulation**
- Monte Carlo-style simulations via advanced LLM reasoning
- Probability-weighted outcomes across multiple time horizons
- Market condition modeling (bull/bear/base scenarios)
- Life event impact analysis

### 🌌 **Temporal Financial Analysis** 
- "When will I be able to buy a house?"
- "Can I retire by 45?"
- "What will my net worth be at age 50?"
- "When will I become a crorepati (millionaire)?"

### ⚡ **Decision Impact Prediction**
- Short-term impact (1-6 months)
- Medium-term impact (1-5 years)  
- Long-term impact (5-30 years)
- Opportunity cost analysis

### 🎯 **What-If Scenario Modeling**
- Career change impacts
- Investment strategy comparisons
- Life event financial planning
- Economic scenario stress testing

## Architecture

The Oracle follows a hierarchical multi-agent architecture with 4 specialized sub-agents:

```
🔮 Oracle Coordinator (Main Agent)
├── 📊 Financial Analyzer Agent (Fi MCP integration)
├── 🎲 Future Simulator Agent (Monte Carlo simulations)
├── 🌌 Scenario Modeler Agent (What-if analysis)
└── ⏰ Timeline Predictor Agent (Goal forecasting)
```

### Agent Responsibilities

| Agent | Purpose | Tools |
|-------|---------|--------|
| **Oracle Coordinator** | Main orchestrator with mystical personality | Fi MCP + Agent coordination |
| **Financial Analyzer** | Current state analysis from Fi MCP data | Fi MCP toolset |
| **Future Simulator** | Probability-weighted future projections | LLM reasoning |
| **Scenario Modeler** | Alternate timeline comparisons | LLM analysis |
| **Timeline Predictor** | Specific goal achievement dates | LLM forecasting |

## Fi MCP Integration

The Oracle integrates with Fi MCP (Financial Model Context Protocol) to access comprehensive financial data:

```json
{
  "current_snapshot": {
    "assets": {
      "liquid": "bank_balances + fd + liquid_funds",
      "investments": "stocks + mutual_funds + etf + gold", 
      "retirement": "epf + ppf + nps",
      "property": "real_estate_value"
    },
    "liabilities": {
      "short_term": "credit_card_outstanding",
      "long_term": "home_loan + personal_loan + auto_loan"
    },
    "cash_flow": {
      "monthly_income": "salary + other_income",
      "monthly_expenses": "categorized_expenses", 
      "savings_rate": "percentage"
    },
    "profile": {
      "age": "number",
      "risk_tolerance": "conservative | moderate | aggressive",
      "life_goals": ["marriage", "house", "retirement", "children_education"],
      "career_stage": "early | mid | late"
    }
  }
}
```

## Setup and Installation

### Prerequisites
- Python 3.9+
- Poetry for dependency management
- Google Cloud Platform project
- Google Cloud CLI
- Fi MCP access

### Installation

```bash
# Ensure you're in the project root with oracle_agent folder
cd /path/to/your/project

# Install dependencies (same as financial advisor)
poetry install

# Set up environment variables
export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_PROJECT=<your-project-id>
export GOOGLE_CLOUD_LOCATION=<your-project-location>
export GOOGLE_CLOUD_STORAGE_BUCKET=<your-storage-bucket>

# Authenticate Google Cloud
gcloud auth application-default login
gcloud auth application-default set-quota-project $GOOGLE_CLOUD_PROJECT
```

## Running The Oracle

### Using ADK CLI
```bash
adk run oracle_agent
```

### Using ADK Web Interface
```bash
adk web
```
Then select "oracle_agent" from the dropdown menu.

## Example Interactions

### 1. Basic Future Prediction
**User**: "When will I be able to buy a house worth ₹50L?"

**Oracle**: 
🔮 **Oracle's Vision**: I see property papers in your future, but the path has multiple branches...

**Probability Analysis**:
- Primary Timeline (72% probability): House purchase in October 2028 with 20% down payment of ₹10L
- Optimistic Timeline (18% probability): July 2027 if your investments outperform by 15%
- Pessimistic Timeline (10% probability): Delayed to 2030 if inflation exceeds 8% annually

**Key Inflection Points**:
- March 2026: Your EPF reaches ₹8L - critical for down payment
- December 2027: Expected promotion increases loan eligibility by ₹20L

**The Oracle's Advice**: Increase your SIP by ₹5,000/month starting today. This simple act advances your purchase by 8 months.

**Butterfly Effect Warning**: Starting a ₹3,000 monthly debt fund SIP today creates ₹2.8L extra for your down payment.

### 2. Retirement Planning
**User**: "Can I retire by 45?"

**Oracle**:
🔮 **Oracle's Vision**: I see you at 45, but the visions diverge - one shows freedom, another shows struggle...

**Probability Analysis**:
- Primary Timeline (43% probability): Partial retirement possible with ₹2.8Cr corpus
- Optimistic Timeline (23% probability): Full retirement with ₹4.1Cr if you increase equity now
- Pessimistic Timeline (34% probability): Need to work till 52 at current savings rate

### 3. What-If Scenario
**User**: "What happens if I switch jobs for a 40% salary increase?"

**Oracle**:
🌌 **Alternate Timeline Detected**

**Current Timeline**: Steady growth, net worth reaching ₹45L by 2027

**Job Switch Timeline**:
- Immediate Impact: +₹35K/month cash flow
- Ripple Effects: House purchase accelerated by 15 months
- Ultimate Destiny: ₹1.2Cr additional wealth by retirement

**Probability Shift**:
- Financial Independence by 50: 45% → 78%
- Dream House Achievement: 67% → 89%

## Oracle's Unique Features

### 🎭 **Mystical Personality**
- Speaks with mystical flair while maintaining mathematical precision
- Uses vivid imagery: "Your wealth grows like a banyan tree"
- Balances mysticism with hard data: "The spirits of compound interest whisper... 14.7% CAGR"

### 📅 **Future Message Generator**
Creates messages from your future self:
```
"Message from 65-year-old you: 'That SIP you're thinking of stopping? It bought our retirement home in Goa. Don't stop it.'"
```

### 🌦️ **Financial Weather Report**
Provides predictions like weather:
```
"Financial forecast for next 6 months: Sunny with 85% savings visibility. 
Warning: Expense storm approaching in March (car insurance + festival season)."
```

### 📊 **Goal Achievement Meter**
Visual progress tracking:
```
Dream House Fund: ████████░░ 78% (₹19.5L / ₹25L)
Timeline: 🟢 On track | ⚡ 6 months ahead | ⚠️ 3 months delayed
```

## Deployment

Deploy to Google Cloud Agent Engine:

```bash
poetry install --with deployment
python3 deployment/deploy.py --create
```

## Testing

Run the test suite:

```bash
poetry install --with dev
python3 -m pytest tests/test_oracle_agents.py
```

## Customization

### Enhancing Predictions
1. **Add More Data Sources**: Integrate additional financial APIs
2. **Improve Simulation Logic**: Enhance Monte Carlo modeling
3. **Custom Scenarios**: Add industry-specific or regional scenarios

### Personalizing the Oracle
1. **Adjust Personality**: Modify prompts for different mystical styles
2. **Cultural Adaptation**: Customize for different regions/currencies
3. **Goal Types**: Add new categories of financial goals

## Legal Disclaimer

⚠️ **Important**: The Oracle provides educational and informational predictions only. Not financial advice. Always consult qualified financial advisors before making investment decisions.

## Contributing

Follow the same structure as the financial advisor agent when adding new features:
1. Create sub-agents for specialized tasks
2. Use state keys for data flow between agents
3. Maintain the mystical yet precise personality
4. Integrate with Fi MCP for real financial data

## Architecture Diagram

```
User Query
    ↓
🔮 Oracle Coordinator
    ↓
📊 Financial Analyzer (Fi MCP) → financial_analysis_output
    ↓  
🎲 Future Simulator → future_scenarios_output
    ↓
🌌 Scenario Modeler → scenario_analysis_output  
    ↓
⏰ Timeline Predictor → timeline_predictions_output
    ↓
🔮 Oracle's Final Prophecy
```

The Oracle sees all possibilities. Which future will you choose? 🔮 