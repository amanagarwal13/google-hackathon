/**
 * Timeline Visualization JavaScript
 */

let timelineData = null;
let currentNodeHover = null;

// Initialize timeline on page load
async function initializeTimeline() {
    try {
        // Show loading state
        showLoading();
        
        // Fetch parallel universe data
        const response = await fetch('/api/parallel-universe-data');
        const result = await response.json();
        
        console.log('API Response:', result);
        
        if (result.status === 'completed' && result.data) {
            // Check if data has the expected structure
            if (result.data.parallel_universe_analysis) {
                timelineData = result.data.parallel_universe_analysis;
            } else {
                timelineData = result.data;
            }
            
            console.log('Timeline Data:', timelineData);
            
            // Verify required data exists
            if (timelineData.financial_timeline && timelineData.alternative_universes) {
                renderTimeline();
                hideLoading();
                showMainContent();
            } else {
                console.error('Invalid data structure:', timelineData);
                showError('Invalid data format received from analysis');
            }
        } else if (result.status === 'pending' || result.status === 'processing') {
            // Show processing message
            document.querySelector('.loading-text').textContent = 
                'Processing your financial data... This may take a moment.';
            // Retry after a delay
            setTimeout(initializeTimeline, 3000);
        } else if (result.status === 'error') {
            showError(result.error || 'Failed to load timeline data');
        } else {
            // If no analysis has been started, show the trigger button
            document.querySelector('.loading-text').textContent = 
                'No analysis found. Click below to start.';
            document.getElementById('loadingRetryButton').style.display = 'inline-flex';
        }
    } catch (error) {
        console.error('Error loading timeline:', error);
        showError('Failed to load timeline data. Please try again.');
    }
}

// Load test data for debugging
function loadTestData() {
    timelineData = {
        "metadata": {
            "analysis_date": "2024-01-15",
            "data_period": "2018-08-07 to 2025-07-15",
            "total_decisions_analyzed": 4,
            "universes_generated": 5,
            "currency": "INR"
        },
        "financial_timeline": {
            "actual_journey": {
                "start_date": "2018-08-07",
                "end_date": "2025-07-15",
                "starting_net_worth": "N/A",
                "current_net_worth": "₹12,97,285",
                "wealth_created": "₹12,97,285 (based on available data)",
                "cagr": "N/A"
            },
            "key_decisions": [
                {
                    "decision_id": "dp_20210324_job_change",
                    "date": "2021-03-24",
                    "description": "Started New Job at KARZA TECHNOLOGIES",
                    "category": "Career",
                    "amount": "₹0",
                    "current_value": "N/A",
                    "roi": "N/A",
                    "decision_quality_score": 8.5,
                    "market_context": "Foundational career move that enabled future financial actions."
                },
                {
                    "decision_id": "dp_20220309_investment",
                    "date": "2022-03-09",
                    "description": "Invested in ICICI Prudential Nifty 50 Index Fund",
                    "category": "Investment",
                    "amount": "₹10,027",
                    "current_value": "₹1,77,605",
                    "roi": "1671%",
                    "decision_quality_score": 9.8,
                    "market_context": "Post-COVID recovery phase."
                }
            ]
        },
        "alternative_universes": [
            {
                "universe_id": "conservative",
                "name": "The Conservative Path",
                "description": "A universe where decisions focused on capital preservation and low risk.",
                "final_net_worth": "₹11,31,764",
                "wealth_difference": "-₹1,65,521 (-12.76%)",
                "key_characteristics": [
                    "Invested in Fixed Deposits instead of equity funds",
                    "Held cash instead of buying stocks"
                ]
            }
        ],
        "summary_insights": {
            "overall_performance": "Good (7.5/10)",
            "transformation_potential": {
                "from_current": "₹12,97,285",
                "to_optimal": "₹18,00,000+",
                "improvement": "+₹5,00,000+ (+38.5%)",
                "timeline": "Next 5 years with a disciplined, diversified strategy."
            }
        }
    };
    
    renderTimeline();
    hideLoading();
    showMainContent();
}

// Show loading state
function showLoading() {
    document.getElementById('loadingContainer').style.display = 'flex';
    document.getElementById('errorContainer').style.display = 'none';
    document.getElementById('mainContainer').style.display = 'none';
}

// Hide loading state
function hideLoading() {
    document.getElementById('loadingContainer').style.display = 'none';
}

// Show main content
function showMainContent() {
    document.getElementById('mainContainer').style.display = 'block';
}

// Show error state
function showError(message) {
    document.getElementById('loadingContainer').style.display = 'none';
    document.getElementById('errorContainer').style.display = 'flex';
    document.getElementById('errorMessage').textContent = message;
}

// Retry analysis
async function retryAnalysis() {
    try {
        const response = await fetch('/api/trigger-parallel-analysis', {
            method: 'POST'
        });
        
        if (response.ok) {
            initializeTimeline();
        }
    } catch (error) {
        console.error('Error triggering analysis:', error);
    }
}

// Trigger new analysis
async function triggerNewAnalysis() {
    document.getElementById('loadingRetryButton').style.display = 'none';
    document.querySelector('.loading-text').textContent = 'Starting analysis...';
    
    try {
        const response = await fetch('/api/trigger-parallel-analysis', {
            method: 'POST'
        });
        
        if (response.ok) {
            setTimeout(initializeTimeline, 2000);
        } else {
            showError('Failed to start analysis. Please try again.');
        }
    } catch (error) {
        console.error('Error triggering analysis:', error);
        showError('Failed to start analysis. Please try again.');
    }
}

// Refresh analysis
function refreshAnalysis() {
    retryAnalysis();
}

// Render timeline
function renderTimeline() {
    if (!timelineData) return;
    
    // Update header stats
    updateHeaderStats();
    
    // Render timeline nodes
    renderTimelineNodes();
    
    // Render comparison panel
    renderComparisonPanel();
    
    // Auto-scroll to show timeline
    setTimeout(() => {
        const container = document.querySelector('.timeline-container');
        if (container) {
            container.scrollTo({
                left: 100,
                behavior: 'smooth'
            });
        }
    }, 500);
}

// Update header statistics
function updateHeaderStats() {
    const actual = timelineData.financial_timeline.actual_journey;
    const summary = timelineData.summary_insights;
    
    // Current net worth
    document.getElementById('currentNetWorth').textContent = 
        formatCurrency(actual.current_net_worth);
    
    // Best alternative (from transformation potential)
    if (summary.transformation_potential) {
        document.getElementById('bestAlternative').textContent = 
            formatCurrency(summary.transformation_potential.to_optimal);
    } else {
        document.getElementById('bestAlternative').textContent = '-';
    }
    
    // Optimization score
    const performance = summary.overall_performance;
    if (performance) {
        const score = performance.match(/(\d+\.?\d*\/10)/);
        if (score) {
            const value = parseFloat(score[1].split('/')[0]);
            document.getElementById('optimizationScore').textContent = 
                `${Math.round(value * 10)}%`;
        }
    }
}

// Render timeline nodes
function renderTimelineNodes() {
    const wrapper = document.getElementById('timelineWrapper');
    const decisions = timelineData.financial_timeline.key_decisions;
    const alternatives = timelineData.alternative_universes;
    
    // Clear existing nodes (except main timeline)
    const existingNodes = wrapper.querySelectorAll('.timeline-node');
    existingNodes.forEach(node => node.remove());
    
    // Calculate timeline width based on number of decisions
    const nodeSpacing = 400;
    const totalWidth = (decisions.length + 1) * nodeSpacing + 200;
    wrapper.style.width = `${totalWidth}px`;
    
    // Update main timeline width
    const mainTimeline = wrapper.querySelector('.main-timeline');
    mainTimeline.style.width = `${totalWidth - 200}px`;
    
    // Render each decision node
    decisions.forEach((decision, index) => {
        const node = createTimelineNode(decision, index, decisions.length, alternatives);
        wrapper.appendChild(node);
    });
    
    // Add current position node
    const currentNode = createCurrentPositionNode(decisions.length);
    wrapper.appendChild(currentNode);
}

// Create timeline node
function createTimelineNode(decision, index, totalDecisions, alternatives) {
    const node = document.createElement('div');
    node.className = 'timeline-node animate-in';
    node.style.left = `${(index + 1) * 400}px`;
    node.style.animationDelay = `${index * 0.1}s`;
    
    // Node marker
    const marker = document.createElement('div');
    marker.className = 'node-marker';
    node.appendChild(marker);
    
    // Node content
    const content = document.createElement('div');
    content.className = 'node-content';
    content.innerHTML = `
        <div class="node-date">${formatDate(decision.date)}</div>
        <div class="node-title">${decision.description}</div>
        <div class="node-amount">${formatAmount(decision.amount)}</div>
        <div class="node-category">${decision.category}</div>
    `;
    node.appendChild(content);
    
    // Branches (alternatives)
    const branches = createBranches(decision, alternatives);
    if (branches) {
        node.appendChild(branches);
    }
    
    return node;
}

// Create current position node
function createCurrentPositionNode(decisionCount) {
    const node = document.createElement('div');
    node.className = 'timeline-node animate-in';
    node.style.left = `${(decisionCount + 1) * 400}px`;
    node.style.animationDelay = `${decisionCount * 0.1}s`;
    
    const marker = document.createElement('div');
    marker.className = 'node-marker current';
    node.appendChild(marker);
    
    const content = document.createElement('div');
    content.className = 'node-content';
    content.innerHTML = `
        <div class="node-date">Today</div>
        <div class="node-title">Current Position</div>
        <div class="node-amount">${formatCurrency(timelineData.financial_timeline.actual_journey.current_net_worth)}</div>
    `;
    node.appendChild(content);
    
    return node;
}

// Create branches for alternatives
function createBranches(decision, alternatives) {
    const branches = document.createElement('div');
    branches.className = 'branches';
    
    let branchCount = 0;
    
    // Find alternatives that affected this decision
    alternatives.forEach(universe => {
        const relevantDiff = universe.key_characteristics.find(char => 
            char.toLowerCase().includes(decision.description.toLowerCase()) ||
            char.toLowerCase().includes(decision.category.toLowerCase())
        );
        
        if (relevantDiff && branchCount < 3) {
            const branch = document.createElement('div');
            branch.className = 'branch';
            
            const label = document.createElement('div');
            label.className = 'branch-label';
            
            const universeName = document.createElement('div');
            universeName.className = 'branch-universe';
            universeName.textContent = universe.name;
            label.appendChild(universeName);
            
            const impact = document.createElement('div');
            impact.className = 'branch-impact';
            impact.textContent = universe.wealth_difference;
            
            if (universe.wealth_difference.startsWith('-')) {
                impact.classList.add('negative');
            }
            
            label.appendChild(impact);
            branch.appendChild(label);
            branches.appendChild(branch);
            
            branchCount++;
        }
    });
    
    return branchCount > 0 ? branches : null;
}

// Render comparison panel
function renderComparisonPanel() {
    const grid = document.getElementById('comparisonGrid');
    grid.innerHTML = '';
    
    // Add actual timeline
    const actualItem = createComparisonItem(
        'Your Path',
        timelineData.financial_timeline.actual_journey.current_net_worth,
        '100%',
        null
    );
    grid.appendChild(actualItem);
    
    // Add top alternatives
    const alternatives = timelineData.alternative_universes
        .filter(u => u.universe_id !== 'actual_timeline')
        .sort((a, b) => {
            const aValue = parseCurrency(a.final_net_worth);
            const bValue = parseCurrency(b.final_net_worth);
            return bValue - aValue;
        })
        .slice(0, 3);
    
    alternatives.forEach(universe => {
        const item = createComparisonItem(
            universe.name,
            universe.final_net_worth,
            calculateProgressPercentage(universe.final_net_worth),
            universe.wealth_difference
        );
        grid.appendChild(item);
    });
}

// Create comparison item
function createComparisonItem(title, value, progressPercent, difference) {
    const item = document.createElement('div');
    item.className = 'comparison-item';
    
    let differenceHtml = '';
    if (difference) {
        const diffClass = difference.startsWith('-') ? 'negative' : 'positive';
        differenceHtml = `<div class="comparison-difference ${diffClass}">${difference}</div>`;
    }
    
    const progressClass = progressPercent === '100%' ? '' : 
                         (difference && difference.startsWith('-') ? 'negative' : '');
    
    item.innerHTML = `
        <div class="comparison-title">${title}</div>
        <div class="comparison-value">${value}</div>
        ${differenceHtml}
        <div class="progress-bar">
            <div class="progress-fill ${progressClass}" style="width: ${progressPercent};"></div>
        </div>
    `;
    
    return item;
}

// Helper functions
function formatCurrency(value) {
    if (!value || value === 'N/A') return '-';
    
    // Remove currency symbol and parse
    const numValue = parseCurrency(value);
    
    // Format based on magnitude
    if (numValue >= 10000000) { // 1 Crore+
        return `₹${(numValue / 10000000).toFixed(1)}Cr`;
    } else if (numValue >= 100000) { // 1 Lakh+
        return `₹${(numValue / 100000).toFixed(1)}L`;
    } else if (numValue >= 1000) { // 1000+
        return `₹${(numValue / 1000).toFixed(1)}K`;
    } else {
        return `₹${numValue.toFixed(0)}`;
    }
}

function parseCurrency(value) {
    if (!value || value === 'N/A') return 0;
    
    // Remove all non-numeric characters except decimal point
    const cleaned = value.toString().replace(/[^0-9.-]/g, '');
    return parseFloat(cleaned) || 0;
}

function formatAmount(amount) {
    if (!amount || amount === '₹0') return '-';
    return amount.toString();
}

function formatDate(dateStr) {
    if (!dateStr) return '';
    
    const date = new Date(dateStr);
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    
    return `${months[date.getMonth()]} ${date.getFullYear()}`;
}

function calculateProgressPercentage(value) {
    const current = parseCurrency(timelineData.financial_timeline.actual_journey.current_net_worth);
    const target = parseCurrency(value);
    
    if (current === 0) return '0%';
    
    const percentage = (target / current) * 100;
    return `${Math.min(100, Math.max(0, percentage))}%`;
}

// Add hover effects
document.addEventListener('mouseover', function(e) {
    if (e.target.closest('.timeline-node')) {
        const node = e.target.closest('.timeline-node');
        if (currentNodeHover !== node) {
            currentNodeHover = node;
            // Additional hover effects can be added here
        }
    }
});

document.addEventListener('mouseout', function(e) {
    if (!e.target.closest('.timeline-node')) {
        currentNodeHover = null;
    }
});