"""Financial Health Score Visualization Engine"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
import base64
import io
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class FinancialHealthVisualizer:
    """Generate visual charts and graphs for Financial Health Score analysis"""
    
    def __init__(self):
        plt.style.use('default')
        sns.set_palette("husl")
        
    def generate_chart(self, chart_type: str, data: Dict[str, Any], title: str = None, save_path: str = None) -> Dict[str, Any]:
        """Generate chart based on type - works with direct calculator output"""
        
        try:
            if chart_type == "weekly_trend":
                return self._create_weekly_trend_chart(data, title)
            elif chart_type == "factor_breakdown":
                return self._create_factor_breakdown_chart(data, title)
            elif chart_type == "improvement_projection":
                return self._create_improvement_projection_chart(data, title)
            elif chart_type == "score_distribution":
                return self._create_score_distribution_chart(data, title)
            else:
                raise ValueError(f"Unknown chart type: {chart_type}")
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Chart generation failed: {str(e)}",
                'chart_type': chart_type,
                'image_base64': None
            }
    
    def _create_weekly_trend_chart(self, score_data: Dict[str, Any], title: str = None) -> Dict[str, Any]:
        """Create weekly trend chart from direct calculator output"""
        
        # Extract week-wise data
        week_wise = score_data.get('week_wise_analysis', [])
        if not week_wise:
            return {'success': False, 'error': 'No week-wise data available'}
        
        # Prepare data
        weeks = [w['week'] for w in week_wise]
        scores = [w['score'] for w in week_wise]
        indicators = [w['health_indicator'] for w in week_wise]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Color mapping for health indicators
        color_map = {
            'Excellent': '#2E8B57',
            'Healthy': '#32CD32', 
            'Stable': '#FFD700',
            'Moderate': '#FF8C00',
            'Concerning': '#DC143C'
        }
        
        # Plot line with markers
        ax.plot(weeks, scores, marker='o', linewidth=3, markersize=8, color='#1f77b4')
        
        # Color background zones
        ax.axhspan(800, 1000, alpha=0.1, color='green', label='Excellent (800+)')
        ax.axhspan(700, 800, alpha=0.1, color='lightgreen', label='Good (700-799)')
        ax.axhspan(600, 700, alpha=0.1, color='yellow', label='Fair (600-699)')
        ax.axhspan(500, 600, alpha=0.1, color='orange', label='Needs Improvement (500-599)')
        ax.axhspan(0, 500, alpha=0.1, color='red', label='Poor (<500)')
        
        # Annotations
        for i, (week, score, indicator) in enumerate(zip(weeks, scores, indicators)):
            ax.annotate(f'{score}', (i, score), textcoords="offset points", 
                       xytext=(0,10), ha='center', fontweight='bold')
        
        # Formatting
        ax.set_title(title or 'Financial Health Score - 8 Week Trend', fontsize=16, fontweight='bold')
        ax.set_xlabel('Time Period', fontsize=12)
        ax.set_ylabel('Financial Health Score', fontsize=12)
        ax.set_ylim(0, 1000)
        ax.grid(True, alpha=0.3)
        
        # Current score highlight
        current_score = score_data.get('overall_score', scores[-1])
        ax.axhline(y=current_score, color='red', linestyle='--', alpha=0.7, 
                  label=f'Current Score: {current_score}')
        
        ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return self._save_chart_to_base64(fig, 'weekly_trend')
    
    def _create_factor_breakdown_chart(self, score_data: Dict[str, Any], title: str = None) -> Dict[str, Any]:
        """Create factor breakdown chart from direct calculator output"""
        
        # Extract factor breakdown
        factor_breakdown = score_data.get('factor_breakdown', [])
        if not factor_breakdown:
            return {'success': False, 'error': 'No factor breakdown data available'}
        
        # Prepare data
        factors = [f['factor'] for f in factor_breakdown]
        scores = [f['score'] for f in factor_breakdown]
        weights = [f['weight'] for f in factor_breakdown]
        grades = [f['grade'] for f in factor_breakdown]
        
        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 8))
        
        # Color mapping for grades
        grade_colors = {'A+': '#2E8B57', 'A': '#32CD32', 'B': '#FFD700', 
                       'C': '#FF8C00', 'D': '#FF6347', 'F': '#DC143C'}
        colors = [grade_colors.get(grade, '#808080') for grade in grades]
        
        # Chart 1: Factor Scores
        bars1 = ax1.barh(factors, scores, color=colors, alpha=0.8)
        ax1.set_title('Factor Scores (0-100)', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Score')
        ax1.set_xlim(0, 100)
        
        # Add score labels and grades
        for i, (bar, score, grade) in enumerate(zip(bars1, scores, grades)):
            ax1.text(score + 1, bar.get_y() + bar.get_height()/2, 
                    f'{score:.1f} ({grade})', va='center', fontweight='bold')
        
        # Chart 2: Weighted Contributions
        weighted_scores = [f['weighted_contribution'] for f in factor_breakdown]
        bars2 = ax2.barh(factors, weighted_scores, color=colors, alpha=0.8)
        ax2.set_title('Weighted Contribution to Overall Score', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Weighted Points')
        
        # Add weight labels
        for i, (bar, weighted, weight) in enumerate(zip(bars2, weighted_scores, weights)):
            ax2.text(weighted + 0.5, bar.get_y() + bar.get_height()/2, 
                    f'{weighted:.1f} ({weight})', va='center', fontweight='bold')
        
        # Overall formatting
        fig.suptitle(title or 'Financial Health Score - Factor Breakdown', 
                    fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        return self._save_chart_to_base64(fig, 'factor_breakdown')
    
    def _create_improvement_projection_chart(self, score_data: Dict[str, Any], title: str = None) -> Dict[str, Any]:
        """Create improvement projection chart"""
        
        current_score = score_data.get('overall_score', 0)
        recommendations = score_data.get('recommendations', [])
        
        # Create timeline projections
        timeline_data = [
            {'period': 'Current', 'score': current_score, 'improvement': 0},
            {'period': '3 Months', 'score': min(1000, current_score + 50), 'improvement': 50},
            {'period': '6 Months', 'score': min(1000, current_score + 100), 'improvement': 100},
            {'period': '12 Months', 'score': min(1000, current_score + 150), 'improvement': 150}
        ]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        periods = [d['period'] for d in timeline_data]
        scores = [d['score'] for d in timeline_data]
        
        # Plot projection line
        ax.plot(periods, scores, marker='o', linewidth=4, markersize=10, 
               color='#2E8B57', label='Projected Score')
        
        # Add current score marker
        ax.scatter([0], [current_score], color='red', s=150, zorder=5, 
                  label=f'Current Score: {current_score}')
        
        # Color zones
        ax.axhspan(800, 1000, alpha=0.1, color='green', label='Excellent Zone')
        ax.axhspan(700, 800, alpha=0.1, color='lightgreen', label='Good Zone')
        ax.axhspan(600, 700, alpha=0.1, color='yellow', label='Fair Zone')
        
        # Annotations
        for i, (period, score) in enumerate(zip(periods, scores)):
            improvement = score - current_score
            if improvement > 0:
                ax.annotate(f'{score}\n(+{improvement})', (i, score), 
                           textcoords="offset points", xytext=(0,15), 
                           ha='center', fontweight='bold', color='green')
            else:
                ax.annotate(f'{score}', (i, score), textcoords="offset points", 
                           xytext=(0,15), ha='center', fontweight='bold')
        
        # Formatting
        ax.set_title(title or 'Financial Health Score - Improvement Projection', 
                    fontsize=16, fontweight='bold')
        ax.set_ylabel('Financial Health Score')
        ax.set_ylim(max(0, current_score - 100), min(1000, current_score + 200))
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        plt.tight_layout()
        
        return self._save_chart_to_base64(fig, 'improvement_projection')
    
    def _create_score_distribution_chart(self, score_data: Dict[str, Any], title: str = None) -> Dict[str, Any]:
        """Create score distribution and percentile chart"""
        
        current_score = score_data.get('overall_score', 0)
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Chart 1: Score Categories Distribution
        categories = ['Poor\n(0-499)', 'Needs Improvement\n(500-599)', 
                     'Fair\n(600-699)', 'Good\n(700-799)', 'Very Good\n(800-899)', 
                     'Excellent\n(900-1000)']
        percentages = [5, 15, 25, 30, 20, 5]  # Typical distribution
        colors = ['#DC143C', '#FF6347', '#FFD700', '#32CD32', '#2E8B57', '#006400']
        
        # Highlight user's category
        user_category_idx = min(5, max(0, (current_score // 100) - (1 if current_score >= 500 else 0)))
        if current_score < 500:
            user_category_idx = 0
        elif current_score < 600:
            user_category_idx = 1
        elif current_score < 700:
            user_category_idx = 2
        elif current_score < 800:
            user_category_idx = 3
        elif current_score < 900:
            user_category_idx = 4
        else:
            user_category_idx = 5
        
        explode = [0.1 if i == user_category_idx else 0 for i in range(len(categories))]
        
        ax1.pie(percentages, labels=categories, colors=colors, autopct='%1.1f%%', 
               explode=explode, shadow=True)
        ax1.set_title('Population Distribution by Score Range\n(Your category highlighted)', 
                     fontsize=12, fontweight='bold')
        
        # Chart 2: Percentile Ranking
        score_ranges = np.arange(0, 1001, 50)
        percentiles = np.cumsum([2, 3, 5, 8, 12, 15, 18, 15, 12, 8, 5, 3, 2, 2, 2, 2, 2, 2, 2, 2])
        
        ax2.plot(score_ranges, percentiles, linewidth=3, color='blue')
        ax2.axvline(x=current_score, color='red', linestyle='--', linewidth=2, 
                   label=f'Your Score: {current_score}')
        
        # Calculate percentile
        user_percentile = np.interp(current_score, score_ranges, percentiles)
        ax2.axhline(y=user_percentile, color='red', linestyle=':', alpha=0.7)
        ax2.text(current_score + 20, user_percentile, 
                f'{user_percentile:.0f}th percentile', fontweight='bold')
        
        ax2.set_title('Your Percentile Ranking', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Financial Health Score')
        ax2.set_ylabel('Percentile')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        plt.tight_layout()
        
        return self._save_chart_to_base64(fig, 'score_distribution')
    
    def _save_chart_to_base64(self, fig, chart_type: str) -> Dict[str, Any]:
        """Convert matplotlib figure to base64 string"""
        try:
            buffer = io.BytesIO()
            fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            buffer.close()
            plt.close(fig)
            
            return {
                'success': True,
                'chart_type': chart_type,
                'image_base64': image_base64,
                'timestamp': datetime.now().isoformat(),
                'format': 'png'
            }
        except Exception as e:
            plt.close(fig)
            return {
                'success': False,
                'error': f"Failed to convert chart to base64: {str(e)}",
                'chart_type': chart_type
            } 