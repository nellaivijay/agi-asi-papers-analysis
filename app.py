"""
AI Papers Intelligence Classifier - Main Gradio Application
Analyzes AI papers from AI-Papers-of-the-Week across the intelligence spectrum
"""

import gradio as gr
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

from data_fetcher import AIPapersFetcher
from classifier import AIPapersIntelligenceClassifier
from ranker import PaperRanker
from model_manager import ModelManager
from advanced_analyzer import AdvancedAnalyzer
from reasoning_classifier import ReasoningClassifier


# Initialize components
fetcher = AIPapersFetcher()
model_manager = ModelManager()
classifier = AIPapersIntelligenceClassifier()
reasoning_classifier = ReasoningClassifier()
ranker = PaperRanker()
advanced_analyzer = AdvancedAnalyzer()


def analyze_week(year: str, week: str, model_id: str = "keyword", 
                classification_mode: str = "keyword", use_semantic: bool = False) -> tuple:
    """
    Analyze papers from a specific week across the intelligence spectrum
    
    Args:
        year: Year to analyze
        week: Week to analyze
        model_id: Model to use for analysis
        classification_mode: Classification mode ('keyword', 'reasoning', 'hybrid')
        use_semantic: Whether to use semantic analysis
        
    Returns:
        Tuple of (summary_text, statistics_text, top_papers_text, dataframe, chart)
    """
    print(f"DEBUG: analyze_week called with year={year}, week={week}, model_id={model_id}, classification_mode={classification_mode}, use_semantic={use_semantic}")
    
    try:
        # Update classifier with selected model
        if use_semantic:
            classifier.use_semantic = True
            classifier.model_id = model_id
            classifier.model_manager.set_model(model_id)
        else:
            classifier.use_semantic = False
        
        # Fetch data
        year_data = fetcher.fetch_year_data(year)
        if not year_data or week not in year_data:
            available_weeks = list(year_data.keys()) if year_data else []
            error_msg = f"No data found for {year}, week: {week}. Available weeks: {available_weeks[:5]}..."
            return error_msg, "", "", None, None, None, None, ""
        
        week_info = year_data[week]
        papers = week_info['papers']
        total_papers = len(papers)
        
        # Debug: Check if papers have required fields
        if total_papers > 0:
            first_paper = papers[0]
            if 'title' not in first_paper or 'summary' not in first_paper:
                error_msg = f"Paper data structure error. Paper fields: {list(first_paper.keys())}"
                return error_msg, "", "", None, None, None, None, ""
        
        if total_papers == 0:
            return f"No papers found for {week}", "", "", None, None, None, None, None, ""
        
        # Handle classification mode
        if classification_mode == "reasoning":
            # Use reasoning-based classification for all papers
            classified_papers = []
            for paper in papers:
                reasoning_result = reasoning_classifier.classify_paper(paper)
                # Convert reasoning result to classification format
                classification_level = reasoning_result.get('category', 'Not Related')
                paper['classification_result'] = {
                    'classification': classification_level,
                    'classification_reason': reasoning_result.get('analysis', ''),
                    'agi_score': 0,
                    'asi_score': 0,
                    'aci_score': 0,
                    'ani_score': 0,  # Added missing key
                    'related_score': 0,
                    'other_ai_score': 0,  # Added missing key
                    'ml_score': 0,  # Added missing key
                    'ds_score': 0,  # Added missing key
                    'combined_score': reasoning_result.get('confidence_score', 0),
                    'matched_agi_keywords': [],
                    'matched_asi_keywords': [],
                    'matched_aci_keywords': [],
                    'matched_ani_keywords': [],  # Added missing key
                    'matched_other_ai_keywords': [],  # Added missing key
                    'matched_ml_keywords': [],  # Added missing key
                    'matched_ds_keywords': [],  # Added missing key
                    'matched_related_keywords': [],
                    'semantic_analysis': reasoning_result
                }
                classified_papers.append(paper)
        elif classification_mode == "hybrid":
            # Use keyword classification first, then reasoning for top candidates
            keyword_classified = classifier.batch_classify(papers)
            # Get top 10 papers by keyword score
            top_keyword = sorted(keyword_classified, 
                                 key=lambda x: x['classification_result']['combined_score'], 
                                 reverse=True)[:10]
            
            # Apply reasoning to top papers
            for paper in keyword_classified:
                if paper in top_keyword:
                    reasoning_result = reasoning_classifier.classify_paper(paper)
                    # Override with reasoning result if confidence is high
                    if reasoning_result.get('confidence_score', 0) > 70:
                        paper['classification_result']['classification'] = reasoning_result.get('category', paper['classification_result']['classification'])
                        paper['classification_result']['classification_reason'] = reasoning_result.get('analysis', paper['classification_result']['classification_reason'])
                        paper['classification_result']['combined_score'] = reasoning_result.get('confidence_score', paper['classification_result']['combined_score'])
                        paper['classification_result']['semantic_analysis'] = reasoning_result
            
            classified_papers = keyword_classified
        else:
            # Use keyword classification (default)
            classified_papers = classifier.batch_classify(papers)
        
        # Debug: Check first paper classification
        if classified_papers:
            first_paper = classified_papers[0]
            print(f"DEBUG: First paper title: {first_paper.get('title', 'Unknown')}")
            print(f"DEBUG: First paper has classification_result: {'classification_result' in first_paper}")
            if 'classification_result' in first_paper:
                print(f"DEBUG: First paper classification: {first_paper.get('classification_result', {})}")
            else:
                print(f"DEBUG: First paper keys: {list(first_paper.keys())}")
        else:
            print("DEBUG: No classified papers found!")
        
        # Get statistics
        stats = classifier.get_statistics(classified_papers)
        
        # Rank papers
        ranked_papers = ranker.rank_papers(classified_papers, criteria='composite')
        
        # Debug: Check first paper after ranking
        if ranked_papers:
            first_ranked = ranked_papers[0]
            print(f"DEBUG: After ranking - First paper title: {first_ranked.get('title', 'Unknown')}")
            print(f"DEBUG: After ranking - First paper has classification_result: {'classification_result' in first_ranked}")
            if 'classification_result' in first_ranked:
                print(f"DEBUG: After ranking - First paper classification: {first_ranked.get('classification_result', {})}")
            else:
                print(f"DEBUG: After ranking - First paper keys: {list(first_ranked.keys())}")
        else:
            print("DEBUG: No ranked papers found!")
        
        # Filter for AGI/ASI related papers
        relevant_papers = ranker.filter_by_classification(ranked_papers, min_level='Narrow AI')
        
        # Generate summary
        summary = generate_weekly_summary(year, week, total_papers, stats, relevant_papers, model_id, use_semantic)
        
        # Generate statistics
        stats_text = generate_statistics_text(stats)
        
        # Generate top papers
        top_papers_text = generate_top_papers_text(ranked_papers[:10])
        
        # Create dataframe for display
        df_data = []
        for paper in ranked_papers:
            # Debug: Check if classification_result exists
            if 'classification_result' not in paper:
                print(f"DEBUG: Paper missing classification_result: {paper.get('title', 'Unknown')}")
                continue
                
            classification_result = paper['classification_result']
            if 'classification' not in classification_result:
                print(f"DEBUG: Paper missing classification in result: {paper.get('title', 'Unknown')}")
                print(f"DEBUG: classification_result keys: {list(classification_result.keys())}")
                continue
            
            semantic_info = ""
            if paper.get('semantic_analysis'):
                semantic_info = f" ({paper['semantic_analysis'].get('model_used', 'N/A')})"
            
            # Get links
            paper_link = paper.get('links', {}).get('paper', '')
            tweet_link = paper.get('links', {}).get('tweet', '')
            
            # Create clickable links
            paper_link_html = f'<a href="{paper_link}" target="_blank" style="color: #6366F1; text-decoration: none; font-weight: 500;">📄 Paper</a>' if paper_link else ''
            tweet_link_html = f'<a href="{tweet_link}" target="_blank" style="color: #EC4899; text-decoration: none; font-weight: 500;">🐦 Tweet</a>' if tweet_link else ''
            links_html = ' | '.join(filter(None, [paper_link_html, tweet_link_html]))
            
            # Add color-coded classification badge
            classification = classification_result['classification']
            classification_colors = {
                'ASI': '#7C3AED',
                'AGI': '#00D4AA',
                'ACI': '#F59E0B',
                'ANI': '#64748B',
                'Other AI': '#3B82F6',
                'ML': '#10B981',
                'DS': '#F97316',
                'Not Related': '#EF4444'
            }
            color = classification_colors.get(classification, '#64748B')
            classification_html = f'<span style="background-color: {color}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">{classification}</span>'
            
            df_data.append({
                'Rank': paper.get('rank_position', 0),
                'Title': paper.get('title', 'Unknown'),  # Full title
                'Classification': classification_html,
                'ASI Score': classification_result.get('asi_score', 0),
                'AGI Score': classification_result.get('agi_score', 0),
                'ACI Score': classification_result.get('aci_score', 0),
                'ANI Score': classification_result.get('ani_score', 0),
                'Other AI Score': classification_result.get('other_ai_score', 0),
                'ML Score': classification_result.get('ml_score', 0),
                'DS Score': classification_result.get('ds_score', 0),
                'Combined Score': classification_result.get('combined_score', 0),
                'Final Rank': paper.get('final_rank', 0),
                'Model': semantic_info,
                'Links': links_html
            })
        
        df = pd.DataFrame(df_data)
        
        # Create visualization charts
        classification_chart = create_classification_chart(stats)
        ranking_chart = create_ranking_chart(ranked_papers)
        scatter_chart = create_scatter_chart(ranked_papers)
        
        # Generate advanced analysis report
        advanced_report = advanced_analyzer.generate_analysis_report(ranked_papers)
        
        return summary, stats_text, top_papers_text, df, classification_chart, ranking_chart, scatter_chart, advanced_report
        
    except Exception as e:
        error_msg = f"Error analyzing week: {str(e)}"
        return error_msg, "", "", None, None, None, None, ""


def generate_weekly_summary(year: str, week: str, total_papers: int, 
                           stats: dict, relevant_papers: list, model_id: str, 
                           use_semantic: bool) -> str:
    """Generate summary text for weekly analysis"""
    summary = f"# 🧠 AI Papers Intelligence Classifier: {week}, {year}\n\n"
    summary += f"## 📊 Overview\n\n"
    summary += f"- **Analysis Method**: {'Semantic AI (' + model_id + ')' if use_semantic else 'Keyword-Based'}\n"
    summary += f"- **Total Papers Analyzed**: {total_papers}\n"
    summary += f"- **AGI/ASI Related Papers**: {stats['agi'] + stats['asi'] + stats['aci']}\n"
    summary += f"- **AGI Papers**: {stats['agi']}\n"
    summary += f"- **ASI Papers**: {stats['asi']}\n"
    summary += f"- **ACI Papers**: {stats['aci']}\n"
    summary += f"- **ANI Papers**: {stats['ani']}\n"
    summary += f"- **Other AI Papers**: {stats['other_ai']}\n"
    summary += f"- **ML Papers**: {stats['ml']}\n"
    summary += f"- **DS Papers**: {stats['ds']}\n"
    summary += f"- **Not Related**: {stats['not_related']}\n"
    summary += f"- **Relevance Rate**: {stats['relevance_rate']}%\n\n"
    
    if relevant_papers:
        summary += f"## 🎯 Top Intelligence Papers\n\n"
        for i, paper in enumerate(relevant_papers[:5], 1):
            title = paper.get('title', 'Unknown')
            classification = paper['classification_result']['classification']
            combined_score = paper['classification_result']['combined_score']
            summary += f"{i}. **{title}**\n"
            summary += f"   - Classification: {classification}\n"
            summary += f"   - Relevance Score: {combined_score}/100\n\n"
    else:
        summary += "## 🎯 Top AGI/ASI Papers\n\n"
        summary += "No AGI/ASI related papers found in this week.\n\n"
    
    return summary


def generate_statistics_text(stats: dict) -> str:
    """Generate statistics text"""
    text = "## 📈 Classification Statistics\n\n"
    text += f"- **Total Papers**: {stats['total']}\n"
    text += f"- **ASI**: {stats['asi']} ({stats['asi']/stats['total']*100:.1f}%)\n"
    text += f"- **AGI**: {stats['agi']} ({stats['agi']/stats['total']*100:.1f}%)\n"
    text += f"- **ACI**: {stats['aci']} ({stats['aci']/stats['total']*100:.1f}%)\n"
    text += f"- **ANI**: {stats['ani']} ({stats['ani']/stats['total']*100:.1f}%)\n"
    text += f"- **Other AI**: {stats['other_ai']} ({stats['other_ai']/stats['total']*100:.1f}%)\n"
    text += f"- **ML**: {stats['ml']} ({stats['ml']/stats['total']*100:.1f}%)\n"
    text += f"- **DS**: {stats['ds']} ({stats['ds']/stats['total']*100:.1f}%)\n"
    text += f"- **Not Related**: {stats['not_related']} ({stats['not_related']/stats['total']*100:.1f}%)\n"
    text += f"- **Overall Relevance Rate**: {stats['relevance_rate']}%\n\n"
    
    return text


def generate_top_papers_text(papers: list) -> str:
    """Generate top papers text"""
    text = "## 🏆 Top 10 Ranked Papers\n\n"
    
    for i, paper in enumerate(papers, 1):
        title = paper.get('title', 'Unknown')
        
        # Defensive: Check if classification_result exists
        if 'classification_result' not in paper:
            text += f"### {i}. {title}\n"
            text += "- **Classification**: Error - Missing classification result\n\n"
            continue
            
        classification_result = paper['classification_result']
        classification = classification_result.get('classification', 'Error')
        agi_score = classification_result.get('agi_score', 0)
        asi_score = classification_result.get('asi_score', 0)
        combined_score = classification_result.get('combined_score', 0)
        final_rank = paper.get('final_rank', 0)
        
        # Get links
        paper_link = paper.get('links', {}).get('paper', '')
        tweet_link = paper.get('links', {}).get('tweet', '')
        
        text += f"### {i}. {title}\n"
        text += f"- **Classification**: {classification}\n"
        text += f"- **AGI Keywords**: {agi_score}\n"
        text += f"- **ASI Keywords**: {asi_score}\n"
        text += f"- **Combined Score**: {combined_score}/100\n"
        text += f"- **Final Rank**: {final_rank}/100\n"
        
        if paper_link:
            text += f"- **📄 Paper**: [{paper_link}]({paper_link})\n"
        if tweet_link:
            text += f"- **🐦 Tweet**: [{tweet_link}]({tweet_link})\n"
        
        text += "\n"
    
    return text


def create_classification_chart(stats: dict) -> go.Figure:
    """Create a pie chart showing classification distribution"""
    labels = ['ASI', 'AGI', 'ACI', 'ANI', 'Other AI', 'ML', 'DS', 'Not Related']
    values = [stats['asi'], stats['agi'], stats['aci'], 
              stats['ani'], stats['other_ai'], stats['ml'], stats['ds'],
              stats['not_related']]
    
    # Modern color palette
    colors = ['#7C3AED', '#00D4AA', '#F59E0B', '#64748B', '#3B82F6', '#10B981', '#F97316', '#EF4444']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(
            colors=colors,
            line=dict(color='white', width=2)
        ),
        textinfo='label+percent',
        textposition='inside',
        textfont=dict(size=14, family='Arial'),
        hole=0.4,
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title=dict(
            text='Paper Classification Distribution',
            font=dict(size=20, family='Arial', color='#1E293B')
        ),
        height=450,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=12)
        ),
        paper_bgcolor='rgba(255,255,255,0.95)',
        plot_bgcolor='rgba(255,255,255,0.95)',
        margin=dict(t=80, b=20, l=20, r=20)
    )
    
    return fig


def create_ranking_chart(ranked_papers: list) -> go.Figure:
    """Create a bar chart showing ranking scores for top papers"""
    top_papers = ranked_papers[:15]
    
    titles = [p.get('title', 'Unknown')[:50] + '...' for p in top_papers]
    final_ranks = [p.get('final_rank', 0) for p in top_papers]
    combined_scores = [p['classification_result']['combined_score'] for p in top_papers]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=titles,
        y=final_ranks,
        name='Final Rank Score',
        marker=dict(
            color='#6366F1',
            line=dict(color='#4F46E5', width=1)
        ),
        text=final_ranks,
        textposition='outside',
        textfont=dict(size=10, color='#4F46E5'),
        hovertemplate='<b>%{x}</b><br>Final Rank: %{y:.1f}<extra></extra>'
    ))
    
    fig.add_trace(go.Bar(
        x=titles,
        y=combined_scores,
        name='Combined Relevance',
        marker=dict(
            color='#EC4899',
            line=dict(color='#DB2777', width=1)
        ),
        text=combined_scores,
        textposition='outside',
        textfont=dict(size=10, color='#DB2777'),
        hovertemplate='<b>%{x}</b><br>Combined Score: %{y:.1f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text='Top 15 Papers: Ranking vs Relevance Scores',
            font=dict(size=20, family='Arial', color='#1E293B')
        ),
        xaxis_title=dict(
            text='Paper Title',
            font=dict(size=14, family='Arial')
        ),
        yaxis_title=dict(
            text='Score (0-100)',
            font=dict(size=14, family='Arial')
        ),
        barmode='group',
        height=550,
        xaxis_tickangle=-45,
        xaxis=dict(
            tickfont=dict(size=10),
            showgrid=False
        ),
        yaxis=dict(
            gridcolor='rgba(0,0,0,0.1)',
            zerolinecolor='rgba(0,0,0,0.2)',
            range=[0, 100]
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=12)
        ),
        paper_bgcolor='rgba(255,255,255,0.95)',
        plot_bgcolor='rgba(255,255,255,0.95)',
        margin=dict(t=80, b=100, l=60, r=20)
    )
    
    return fig


def create_scatter_chart(ranked_papers: list) -> go.Figure:
    """Create a scatter plot showing relevance vs novelty"""
    papers_with_scores = [p for p in ranked_papers if p.get('ranking_scores')]
    
    relevance_scores = [p['ranking_scores']['relevance_score'] for p in papers_with_scores]
    novelty_scores = [p['ranking_scores']['novelty_score'] for p in papers_with_scores]
    classifications = [p['classification_result']['classification'] for p in papers_with_scores]
    titles = [p.get('title', 'Unknown')[:40] + '...' for p in papers_with_scores]
    
    # Modern color palette for classifications
    color_map = {
        'ASI': '#7C3AED',
        'AGI': '#00D4AA',
        'ACI': '#F59E0B',
        'ANI': '#64748B',
        'Other AI': '#3B82F6',
        'ML': '#10B981',
        'DS': '#F97316',
        'Not Related': '#EF4444'
    }
    colors = [color_map.get(c, '#64748B') for c in classifications]
    
    # Size based on impact score
    impact_scores = [p['ranking_scores']['impact_score'] for p in papers_with_scores]
    sizes = [max(8, min(25, s / 4)) for s in impact_scores]
    
    fig = go.Figure(data=go.Scatter(
        x=relevance_scores,
        y=novelty_scores,
        mode='markers',
        marker=dict(
            size=sizes,
            color=colors,
            opacity=0.7,
            line=dict(color='white', width=1.5)
        ),
        text=titles,
        customdata=classifications,
        hovertemplate='<b>%{text}</b><br>' +
                     'Relevance: %{x:.1f}<br>' +
                     'Novelty: %{y:.1f}<br>' +
                     'Classification: %{customdata}<extra></extra>',
        showlegend=False
    ))
    
    # Add legend manually
    for classification, color in color_map.items():
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=12, color=color, opacity=0.8),
            name=classification,
            showlegend=True
        ))
    
    fig.update_layout(
        title=dict(
            text='Relevance vs Novelty Analysis',
            font=dict(size=20, family='Arial', color='#1E293B')
        ),
        xaxis_title=dict(
            text='Relevance Score',
            font=dict(size=14, family='Arial')
        ),
        yaxis_title=dict(
            text='Novelty Score',
            font=dict(size=14, family='Arial')
        ),
        height=500,
        hovermode='closest',
        xaxis=dict(
            gridcolor='rgba(0,0,0,0.1)',
            zerolinecolor='rgba(0,0,0,0.2)',
            range=[0, 100]
        ),
        yaxis=dict(
            gridcolor='rgba(0,0,0,0.1)',
            zerolinecolor='rgba(0,0,0,0.2)',
            range=[0, 100]
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=12)
        ),
        paper_bgcolor='rgba(255,255,255,0.95)',
        plot_bgcolor='rgba(255,255,255,0.95)',
        margin=dict(t=80, b=60, l=60, r=20)
    )
    
    return fig


def analyze_trends(year: str) -> tuple:
    """
    Analyze AGI/ASI research trends across all weeks in a year
    
    Args:
        year: Year to analyze
        
    Returns:
        Tuple of (trend_summary, trend_chart)
    """
    try:
        # Fetch all weekly data for the year
        year_data = fetcher.fetch_year_data(year)
        if not year_data:
            return "No data available for this year", None
        
        # Analyze each week
        weekly_stats = []
        week_names = []
        
        for week, week_info in year_data.items():
            papers = week_info['papers']
            if papers:
                classified = classifier.batch_classify(papers)
                stats = classifier.get_statistics(classified)
                
                week_names.append(week.split(' - ')[0])  # Use date range as label
                weekly_stats.append({
                    'week': week,
                    'total': stats['total'],
                    'asi': stats['asi'],
                    'agi': stats['agi'],
                    'aci': stats['aci'],
                    'ani': stats['ani'],
                    'other_ai': stats['other_ai'],
                    'ml': stats['ml'],
                    'ds': stats['ds'],
                    'relevance_rate': stats['relevance_rate']
                })
        
        # Generate summary
        trend_summary = generate_trend_summary(year, weekly_stats)
        
        # Create trend chart
        chart = create_trend_chart(week_names, weekly_stats)
        
        return trend_summary, chart
        
    except Exception as e:
        return f"Error analyzing trends: {str(e)}", None


def generate_trend_summary(year: str, weekly_stats: list) -> str:
    """Generate trend analysis summary"""
    summary = f"# 📈 AI Research Trends - {year}\n\n"
    
    if not weekly_stats:
        summary += "No weekly data available for trend analysis.\n"
        return summary
    
    # Calculate overall statistics
    total_weeks = len(weekly_stats)
    total_papers = sum(w['total'] for w in weekly_stats)
    total_intelligence = sum(w['asi'] + w['agi'] + w['aci'] + w['ani'] + w['other_ai'] + w['ml'] + w['ds'] for w in weekly_stats)
    avg_relevance_rate = sum(w['relevance_rate'] for w in weekly_stats) / total_weeks
    
    summary += f"## 📊 Overall Statistics\n\n"
    summary += f"- **Total Weeks Analyzed**: {total_weeks}\n"
    summary += f"- **Total Papers**: {total_papers}\n"
    summary += f"- **Total Intelligence Papers**: {total_intelligence}\n"
    summary += f"- **Average Relevance Rate**: {avg_relevance_rate:.1f}%\n\n"
    
    # Find weeks with highest intelligence activity
    top_weeks = sorted(weekly_stats, key=lambda x: x['asi'] + x['agi'] + x['aci'], reverse=True)[:3]
    
    summary += f"## 🏆 Top Weeks for High-Level Intelligence Research\n\n"
    for i, week_stat in enumerate(top_weeks, 1):
        week_name = week_stat['week'].split(' - ')[0]
        high_level_count = week_stat['asi'] + week_stat['agi'] + week_stat['aci']
        summary += f"{i}. **{week_name}**: {high_level_count} high-level intelligence papers ({week_stat['relevance_rate']}% relevance)\n"
    
    summary += "\n"
    
    return summary


def create_trend_chart(week_names: list, weekly_stats: list) -> go.Figure:
    """Create trend visualization chart"""
    # Prepare data
    relevance_rates = [w['relevance_rate'] for w in weekly_stats]
    intelligence_counts = [w['asi'] + w['agi'] + w['aci'] + w['ani'] + w['other_ai'] + w['ml'] + w['ds'] for w in weekly_stats]
    
    # Create figure with secondary y-axis
    fig = go.Figure()
    
    # Add relevance rate line with area fill
    fig.add_trace(go.Scatter(
        x=week_names,
        y=relevance_rates,
        mode='lines+markers',
        name='Relevance Rate (%)',
        line=dict(color='#6366F1', width=3),
        marker=dict(size=8, color='#6366F1', line=dict(color='white', width=1)),
        fill='tozeroy',
        fillcolor='rgba(99, 102, 241, 0.1)',
        hovertemplate='<b>%{x}</b><br>Relevance Rate: %{y:.1f}%<extra></extra>'
    ))
    
    # Add intelligence paper count bars
    fig.add_trace(go.Bar(
        x=week_names,
        y=intelligence_counts,
        name='Intelligence Papers',
        marker=dict(
            color='#EC4899',
            line=dict(color='#DB2777', width=1)
        ),
        hovertemplate='<b>%{x}</b><br>Intelligence Papers: %{y}<extra></extra>',
        yaxis='y2'
    ))
    
    # Update layout with modern styling
    fig.update_layout(
        title=dict(
            text='AGI/ASI Research Trends Over Time',
            font=dict(size=20, family='Arial', color='#1E293B')
        ),
        xaxis_title=dict(
            text='Week',
            font=dict(size=14, family='Arial')
        ),
        yaxis_title=dict(
            text='Relevance Rate (%)',
            font=dict(size=14, family='Arial')
        ),
        yaxis2_title=dict(
            text='AGI/ASI Paper Count',
            font=dict(size=14, family='Arial')
        ),
        yaxis2=dict(
            title='AGI/ASI Paper Count',
            overlaying='y',
            side='right',
            gridcolor='rgba(0,0,0,0.1)',
            zerolinecolor='rgba(0,0,0,0.2)'
        ),
        yaxis=dict(
            gridcolor='rgba(0,0,0,0.1)',
            zerolinecolor='rgba(0,0,0,0.2)',
            range=[0, 100]
        ),
        xaxis=dict(
            gridcolor='rgba(0,0,0,0.1)',
            zerolinecolor='rgba(0,0,0,0.2)',
            tickangle=-45,
            tickfont=dict(size=10)
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=12)
        ),
        height=550,
        hovermode='x unified',
        paper_bgcolor='rgba(255,255,255,0.95)',
        plot_bgcolor='rgba(255,255,255,0.95)',
        margin=dict(t=80, b=100, l=60, r=60)
    )
    
    return fig


def update_week_dropdown(year: str):
    """Update week dropdown based on selected year"""
    weeks = fetcher.get_available_weeks(year)
    if weeks:
        return gr.Dropdown(choices=weeks, value=weeks[0])
    return gr.Dropdown(choices=["No weeks available"], value="No weeks available")


# Create Gradio interface
def create_interface():
    """Create the main Gradio interface"""
    
    # Custom theme with modern colors (simplified for compatibility)
    custom_theme = gr.themes.Soft(
        primary_hue="indigo",
        secondary_hue="pink",
    )
    
    with gr.Blocks(title="AI Papers Intelligence Classifier", theme=custom_theme, css="""
        .gradio-container {
            max-width: 1400px !important;
        }
        .plot-container {
            background: white !important;
            border-radius: 12px !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
        }
        .markdown h1 {
            color: #1E293B !important;
            font-size: 2.5rem !important;
            font-weight: 700 !important;
            margin-bottom: 1rem !important;
        }
        .markdown h2 {
            color: #334155 !important;
            font-size: 1.8rem !important;
            font-weight: 600 !important;
            margin-top: 1.5rem !important;
        }
        .markdown h3 {
            color: #475569 !important;
            font-size: 1.4rem !important;
            font-weight: 600 !important;
        }
        .tab-nav {
            border-radius: 12px !important;
        }
        .tab-button {
            font-weight: 500 !important;
        }
    """) as demo:
        
        # Header with enhanced styling
        gr.Markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="font-size: 3rem; font-weight: 700; color: #1E293B; margin-bottom: 0.5rem;">
                🧠 AI Papers Intelligence Classifier
            </h1>
            <p style="font-size: 1.2rem; color: #64748B; margin-bottom: 1.5rem;">
                Analyze AI papers from <a href="https://github.com/dair-ai/AI-Papers-of-the-Week" target="_blank" style="color: #6366F1; text-decoration: none; font-weight: 500;">AI-Papers-of-the-Week</a> 
                across the intelligence spectrum: ANI, AGI, ASI, ACI, ML, and DS.
            </p>
            <div style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(236, 72, 153, 0.1)); 
                        padding: 1rem; border-radius: 12px; border-left: 4px solid #6366F1;">
                <strong style="color: #6366F1;">🎓 Educational Purpose:</strong> This tool is created for educational purposes to demonstrate AI research tracking and analysis across the intelligence spectrum.
            </div>
        </div>
        """)
        
        with gr.Tabs():
            # Tab 1: Weekly Analysis
            with gr.Tab("📊 Weekly Analysis"):
                gr.Markdown("## Analyze papers from a specific week")
                
                with gr.Row():
                    year_input = gr.Dropdown(
                        choices=["2026", "2025", "2024", "2023"],
                        value="2026",
                        label="Year"
                    )
                    week_input = gr.Dropdown(
                        choices=["Select year first"],
                        value="Select year first",
                        label="Week"
                    )
                
                with gr.Row():
                    model_selector = gr.Dropdown(
                        choices=[m["id"] for m in model_manager.get_available_models()],
                        value="keyword",
                        label="Analysis Model",
                        info="Select AI model for semantic analysis"
                    )
                    classification_mode_selector = gr.Radio(
                        choices=["keyword", "reasoning", "hybrid"],
                        value="keyword",
                        label="Classification Mode",
                        info="keyword: Fast (<1s), reasoning: Accurate (5-10s), hybrid: Balanced"
                    )
                    use_semantic = gr.Checkbox(
                        label="Enable Semantic Analysis",
                        value=False,
                        info="Use AI models for deeper understanding (requires API keys)"
                    )
                
                analyze_btn = gr.Button("🔍 Analyze Week", variant="primary")
                
                with gr.Row():
                    summary_output = gr.Markdown(label="Summary")
                    stats_output = gr.Markdown(label="Statistics")
                
                with gr.Row():
                    classification_chart_output = gr.Plot(label="Classification Distribution")
                    ranking_chart_output = gr.Plot(label="Ranking Scores")
                
                with gr.Row():
                    scatter_chart_output = gr.Plot(label="Relevance vs Novelty")
                    top_papers_output = gr.Markdown(label="Top Papers")
                
                papers_df = gr.Dataframe(
            label="All Papers Ranking",
            datatype=["number", "str", "markdown", "number", "number", "number", "number", "number", "number", "number", "number", "number", "str", "markdown"],
            wrap=True,
            column_widths=["80px", "400px", "150px", "80px", "80px", "80px", "80px", "80px", "80px", "80px", "80px", "80px", "100px", "120px"],
            headers=["Rank", "Title", "Classification", "ASI Score", "AGI Score", "ACI Score", "ANI Score", "Other AI Score", "ML Score", "DS Score", "Combined Score", "Final Rank", "Model", "Links"],
            interactive=False
        )
                
                advanced_output = gr.Markdown(label="Advanced Analysis")
                
                # Event handlers
                year_input.change(
                    update_week_dropdown,
                    inputs=[year_input],
                    outputs=[week_input]
                )
                
                analyze_btn.click(
                    analyze_week,
                    inputs=[year_input, week_input, model_selector, classification_mode_selector, use_semantic],
                    outputs=[summary_output, stats_output, top_papers_output, papers_df, 
                             classification_chart_output, ranking_chart_output, scatter_chart_output, advanced_output]
                )
            
            # Tab 2: Trend Analysis
            with gr.Tab("📈 Trend Analysis"):
                gr.Markdown("## Analyze AGI/ASI research trends over time")
                
                trend_year_input = gr.Dropdown(
                    choices=["2026", "2025", "2024", "2023"],
                    value="2026",
                    label="Year"
                )
                
                trend_analyze_btn = gr.Button("📊 Analyze Trends", variant="primary")
                
                trend_summary_output = gr.Markdown(label="Trend Summary")
                trend_chart_output = gr.Plot(label="Trend Chart")
                
                trend_analyze_btn.click(
                    analyze_trends,
                    inputs=[trend_year_input],
                    outputs=[trend_summary_output, trend_chart_output]
                )
            
            # Tab 3: About
            with gr.Tab("ℹ️ About"):
                gr.Markdown("""
                ## About This Tool
                
                ### 🎯 Purpose
                This tool analyzes AI papers from the weekly AI-Papers-of-the-Week newsletter 
                to identify and rank papers related to AGI (Artificial General Intelligence) 
                and ASI (Artificial Super Intelligence).
                
                ### 🤖 Analysis Models
                This tool supports multiple analysis methods:
                
                **Keyword-Based (Free)**
                - Fast pattern matching against AGI/ASI keywords
                - No API keys required
                - Good for initial screening
                
                **OpenAI GPT (Paid)**
                - Advanced semantic understanding
                - Requires OPENAI_API_KEY
                - Best for nuanced analysis
                
                **Anthropic Claude (Paid)**
                - Sophisticated reasoning capabilities
                - Requires ANTHROPIC_API_KEY
                - Excellent for complex papers
                
                **Ollama (Free, Local)**
                - Run models locally on your machine
                - Requires Ollama installation
                - Privacy-focused, no data leaves your machine
                
                **Hugging Face Inference (Free Tier)**
                - Access to various open-source models
                - Requires HUGGINGFACE_API_KEY
                - Good balance of quality and cost
                
                **Cohere Command (Paid, Free Tier)**
                - Cohere's Command models for text analysis
                - Requires COHERE_API_KEY
                - Fast and reliable performance
                
                **Google Gemini (Paid, Free Tier)**
                - Google's Gemini models for semantic understanding
                - Requires GOOGLE_API_KEY
                - Cutting-edge multimodal capabilities
                
                **Together AI (Paid, Free Tier)**
                - Together AI's hosted open-source models
                - Requires TOGETHER_API_KEY
                - Access to latest open-source models
                
                **Replicate (Pay-per-use)**
                - Replicate's hosted models API
                - Requires REPLICATE_API_KEY
                - Wide variety of models available
                
                ### 🔍 Methodology
                - **Keyword Analysis**: Papers are classified using AGI/ASI keyword matching
                - **Semantic Scoring**: AI models provide deeper understanding when enabled
                - **Multi-Criteria Ranking**: Papers are ranked by relevance, novelty, and impact
                - **Trend Analysis**: Track AGI/ASI research patterns over time
                
                ### 📊 Classification Levels
                - **Core AGI/ASI**: Direct focus on AGI/ASI topics (3+ keyword matches)
                - **Strongly Related**: Significant AGI/ASI implications (2 keyword matches)
                - **Tangentially Related**: Some AGI/ASI relevance (1+ keyword matches)
                - **Not Related**: No clear AGI/ASI connection
                
                ### 🏆 Ranking System
                Papers are ranked using a composite score that considers:
                - **Relevance** (50%): AGI/ASI keyword matches and semantic analysis
                - **Novelty** (30%): Keyword diversity and innovation potential
                - **Impact** (20%): Classification level and potential impact
                
                ### 📚 Data Source
                All papers are sourced from the [AI-Papers-of-the-Week](https://github.com/dair-ai/AI-Papers-of-the-Week) 
                repository by DAIR.AI, which provides curated weekly lists of top AI papers.
                
                ### 🎓 Educational Use
                This tool is intended for educational purposes to help researchers and students 
                understand the landscape of AGI/ASI research and track developments in this important field.
                
                ### 🔑 API Key Setup
                To use semantic analysis, set the following environment variables:
                - OpenAI: `export OPENAI_API_KEY=your_key_here`
                - Anthropic: `export ANTHROPIC_API_KEY=your_key_here`
                - Hugging Face: `export HUGGINGFACE_API_KEY=your_key_here`
                - Cohere: `export COHERE_API_KEY=your_key_here`
                - Google: `export GOOGLE_API_KEY=your_key_here`
                - Together AI: `export TOGETHER_API_KEY=your_key_here`
                - Replicate: `export REPLICATE_API_KEY=your_key_here`
                
                For Ollama, install from https://ollama.ai and run: `ollama serve`
                """)
            
            # Tab 4: Model Comparison
            with gr.Tab("🔬 Model Comparison"):
                gr.Markdown("## Compare Different Analysis Models")
                
                gr.Markdown("""
                ### Model Features Comparison
                
                | Model | Cost | Speed | Accuracy | Privacy | API Key Required | Available Models |
                |-------|------|-------|----------|---------|------------------|------------------|
                | Keyword | Free | ⚡⚡⚡ | ⭐⭐ | 🔒🔒🔒 | No | N/A |
                | OpenAI GPT | Paid | ⚡⚡ | ⭐⭐⭐⭐⭐ | 🔒 | Yes | GPT-4, GPT-4 Turbo, GPT-3.5, GPT-4o |
                | Anthropic Claude | Paid | ⚡⚡ | ⭐⭐⭐⭐⭐ | 🔒 | Yes | Claude Opus, Sonnet, Haiku, 3.5 Sonnet |
                | Ollama | Free | ⚡ | ⭐⭐⭐⭐ | 🔒🔒🔒 | No | Llama2, Llama3, Mistral, Phi3, Gemma, Qwen |
                | Hugging Face | Free Tier | ⚡⚡ | ⭐⭐⭐⭐ | 🔒 | Yes | Llama 2/3, Mistral, Gemma, Phi-3, Qwen |
                | Cohere Command | Paid (Free Tier) | ⚡⚡ | ⭐⭐⭐⭐ | 🔒 | Yes | Command, Command Light, Command Nightly |
                | Google Gemini | Paid (Free Tier) | ⚡⚡ | ⭐⭐⭐⭐⭐ | 🔒 | Yes | Gemini Pro, Gemini Pro Vision, Gemini 1.5 |
                | Together AI | Paid (Free Tier) | ⚡⚡ | ⭐⭐⭐⭐ | 🔒 | Yes | Llama 2 70B, Mixtral 8x7B, RedPajama |
                | Replicate | Pay-per-use | ⚡ | ⭐⭐⭐⭐ | 🔒 | Yes | Llama 2 70B, Mixtral 8x7B, Stable Diffusion |
                
                ### Recommendations
                
                **For Quick Analysis**: Use Keyword-Based
                - Fastest option
                - No setup required
                - Good for high-volume screening
                - Best for initial paper triage
                
                **For Deep Analysis**: Use OpenAI GPT or Anthropic Claude
                - Best semantic understanding
                - Handles nuance well
                - Worth the cost for important research
                - Excellent for complex technical papers
                
                **For Privacy**: Use Ollama
                - Data stays on your machine
                - Free to use
                - Requires local setup
                - Best for sensitive research
                
                **For Budget-Conscious**: Use Hugging Face or Cohere
                - Free tier available
                - Good quality models
                - Simple API key setup
                - Good balance of cost and quality
                
                **For Latest Models**: Use Google Gemini
                - Cutting-edge capabilities
                - Multimodal support
                - Free tier available
                - Excellent for modern research
                
                **For Open-Source**: Use Together AI or Replicate
                - Access to latest open-source models
                - Pay-per-use pricing
                - Wide model selection
                - Best for experimentation
                
                ### API Key Setup
                
                To use semantic analysis, set the following environment variables:
                
                ```bash
                # OpenAI
                export OPENAI_API_KEY=your_key_here
                
                # Anthropic
                export ANTHROPIC_API_KEY=your_key_here
                
                # Hugging Face
                export HUGGINGFACE_API_KEY=your_key_here
                
                # Cohere
                export COHERE_API_KEY=your_key_here
                
                # Google
                export GOOGLE_API_KEY=your_key_here
                
                # Together AI
                export TOGETHER_API_KEY=your_key_here
                
                # Replicate
                export REPLICATE_API_KEY=your_key_here
                ```
                
                For Ollama (local models), install from https://ollama.ai and run:
                ```bash
                ollama serve
                ollama pull llama3
                ```
                """)
        
        # Footer
        gr.Markdown("""
        ---
        **Built with**: Gradio, Python, Plotly  
        **Data Source**: [AI-Papers-of-the-Week](https://github.com/dair-ai/AI-Papers-of-the-Week)  
        **Last Updated**: 2026-04-20
        """)
    
    return demo


if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("🧠 AI Papers Intelligence Classifier - Application Startup")
    print("=" * 60)
    print(f"📅 Starting at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python Version: {sys.version.split()[0]}")
    print(f"📦 Gradio Version: 4.0.0")
    print("=" * 60)
    print()
    
    try:
        demo = create_interface()
        print("✅ Interface created successfully")
    except Exception as e:
        print(f"❌ Error creating interface: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("🚀 Starting web server...")
    print()
    print("🎓 Educational Purpose: AGI/ASI research tracking and analysis")
    print("=" * 60)
    print()
    
    try:
        demo.launch(
            server_name="0.0.0.0",
            server_port=7860,
            show_error=True
        )
    except Exception as e:
        print(f"❌ Error launching application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)