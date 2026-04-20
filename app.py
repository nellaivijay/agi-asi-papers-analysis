"""
AGI/ASI Papers Analysis - Main Gradio Application
Analyzes AI papers from AI-Papers-of-the-Week for AGI/ASI relevance
"""

import gradio as gr
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

from data_fetcher import AIPapersFetcher
from classifier import AGIASIClassifier
from ranker import PaperRanker
from model_manager import ModelManager
from advanced_analyzer import AdvancedAnalyzer


# Initialize components
fetcher = AIPapersFetcher()
model_manager = ModelManager()
classifier = AGIASIClassifier()
ranker = PaperRanker()
advanced_analyzer = AdvancedAnalyzer()


def analyze_week(year: str, week: str, model_id: str = "keyword", 
                use_semantic: bool = False) -> tuple:
    """
    Analyze papers from a specific week for AGI/ASI relevance
    
    Args:
        year: Year to analyze
        week: Week to analyze
        model_id: Model to use for analysis
        use_semantic: Whether to use semantic analysis
        
    Returns:
        Tuple of (summary_text, statistics_text, top_papers_text, dataframe, chart)
    """
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
            error_msg = f"No data found for {year}, week: {week}"
            return error_msg, "", "", None, None
        
        week_info = year_data[week]
        papers = week_info['papers']
        total_papers = len(papers)
        
        if total_papers == 0:
            return f"No papers found for {week}", "", "", None, None
        
        # Classify papers
        classified_papers = classifier.batch_classify(papers)
        
        # Get statistics
        stats = classifier.get_statistics(classified_papers)
        
        # Rank papers
        ranked_papers = ranker.rank_papers(classified_papers, criteria='composite')
        
        # Filter for AGI/ASI related papers
        relevant_papers = ranker.filter_by_classification(ranked_papers, min_level='Tangentially Related')
        
        # Generate summary
        summary = generate_weekly_summary(year, week, total_papers, stats, relevant_papers, model_id, use_semantic)
        
        # Generate statistics
        stats_text = generate_statistics_text(stats)
        
        # Generate top papers
        top_papers_text = generate_top_papers_text(ranked_papers[:10])
        
        # Create dataframe for display
        df_data = []
        for paper in ranked_papers:
            semantic_info = ""
            if paper.get('semantic_analysis'):
                semantic_info = f" ({paper['semantic_analysis'].get('model_used', 'N/A')})"
            
            # Get links
            paper_link = paper.get('links', {}).get('paper', '')
            tweet_link = paper.get('links', {}).get('tweet', '')
            
            # Create clickable links
            paper_link_html = f'<a href="{paper_link}" target="_blank">📄 Paper</a>' if paper_link else ''
            tweet_link_html = f'<a href="{tweet_link}" target="_blank">🐦 Tweet</a>' if tweet_link else ''
            links_html = ' | '.join(filter(None, [paper_link_html, tweet_link_html]))
            
            df_data.append({
                'Rank': paper.get('rank_position', 0),
                'Title': paper.get('title', 'Unknown'),  # Full title
                'Classification': paper['classification_result']['classification'],
                'AGI Score': paper['classification_result']['agi_score'],
                'ASI Score': paper['classification_result']['asi_score'],
                'Combined Score': paper['classification_result']['combined_score'],
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
    summary = f"# 🧠 AGI/ASI Papers Analysis: {week}, {year}\n\n"
    summary += f"## 📊 Overview\n\n"
    summary += f"- **Analysis Method**: {'Semantic AI (' + model_id + ')' if use_semantic else 'Keyword-Based'}\n"
    summary += f"- **Total Papers Analyzed**: {total_papers}\n"
    summary += f"- **AGI/ASI Related Papers**: {stats['core_agi_asi'] + stats['strongly_related'] + stats['tangentially_related']}\n"
    summary += f"- **Core AGI/ASI Papers**: {stats['core_agi_asi']}\n"
    summary += f"- **Strongly Related**: {stats['strongly_related']}\n"
    summary += f"- **Tangentially Related**: {stats['tangentially_related']}\n"
    summary += f"- **Not Related**: {stats['not_related']}\n"
    summary += f"- **Relevance Rate**: {stats['relevance_rate']}%\n\n"
    
    if relevant_papers:
        summary += f"## 🎯 Top AGI/ASI Papers\n\n"
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
    text += f"- **Core AGI/ASI**: {stats['core_agi_asi']} ({stats['core_agi_asi']/stats['total']*100:.1f}%)\n"
    text += f"- **Strongly Related**: {stats['strongly_related']} ({stats['strongly_related']/stats['total']*100:.1f}%)\n"
    text += f"- **Tangentially Related**: {stats['tangentially_related']} ({stats['tangentially_related']/stats['total']*100:.1f}%)\n"
    text += f"- **Not Related**: {stats['not_related']} ({stats['not_related']/stats['total']*100:.1f}%)\n"
    text += f"- **Overall Relevance Rate**: {stats['relevance_rate']}%\n\n"
    
    return text


def generate_top_papers_text(papers: list) -> str:
    """Generate top papers text"""
    text = "## 🏆 Top 10 Ranked Papers\n\n"
    
    for i, paper in enumerate(papers, 1):
        title = paper.get('title', 'Unknown')
        classification = paper['classification_result']['classification']
        agi_score = paper['classification_result']['agi_score']
        asi_score = paper['classification_result']['asi_score']
        combined_score = paper['classification_result']['combined_score']
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
    labels = ['Core AGI/ASI', 'Strongly Related', 'Tangentially Related', 'Not Related']
    values = [stats['core_agi_asi'], stats['strongly_related'], 
              stats['tangentially_related'], stats['not_related']]
    colors = ['#00CC96', '#EF553B', '#FFA15A', '#AB63FA']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors),
        textinfo='label+percent',
        textposition='inside',
        hole=0.3
    )])
    
    fig.update_layout(
        title='Paper Classification Distribution',
        height=400,
        showlegend=True
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
        marker=dict(color='#667eea')
    ))
    
    fig.add_trace(go.Bar(
        x=titles,
        y=combined_scores,
        name='Combined Relevance',
        marker=dict(color='#764ba2')
    ))
    
    fig.update_layout(
        title='Top 15 Papers: Ranking vs Relevance Scores',
        xaxis_title='Paper Title',
        yaxis_title='Score (0-100)',
        barmode='group',
        height=500,
        xaxis_tickangle=-45
    )
    
    return fig


def create_scatter_chart(ranked_papers: list) -> go.Figure:
    """Create a scatter plot showing relevance vs novelty"""
    papers_with_scores = [p for p in ranked_papers if p.get('ranking_scores')]
    
    relevance_scores = [p['ranking_scores']['relevance_score'] for p in papers_with_scores]
    novelty_scores = [p['ranking_scores']['novelty_score'] for p in papers_with_scores]
    classifications = [p['classification_result']['classification'] for p in papers_with_scores]
    titles = [p.get('title', 'Unknown')[:30] for p in papers_with_scores]
    
    # Color by classification
    color_map = {
        'Core AGI/ASI': '#00CC96',
        'Strongly Related': '#EF553B',
        'Tangentially Related': '#FFA15A',
        'Not Related': '#AB63FA'
    }
    colors = [color_map.get(c, '#AB63FA') for c in classifications]
    
    fig = go.Figure(data=go.Scatter(
        x=relevance_scores,
        y=novelty_scores,
        mode='markers',
        marker=dict(
            size=10,
            color=colors,
            opacity=0.7
        ),
        text=titles,
        hovertemplate='<b>%{text}</b><br>' +
                     'Relevance: %{x:.1f}<br>' +
                     'Novelty: %{y:.1f}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Relevance vs Novelty Analysis',
        xaxis_title='Relevance Score',
        yaxis_title='Novelty Score',
        height=500,
        hovermode='closest'
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
                    'core_agi_asi': stats['core_agi_asi'],
                    'strongly_related': stats['strongly_related'],
                    'tangentially_related': stats['tangentially_related'],
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
    summary = f"# 📈 AGI/ASI Research Trends - {year}\n\n"
    
    if not weekly_stats:
        summary += "No weekly data available for trend analysis.\n"
        return summary
    
    # Calculate overall statistics
    total_weeks = len(weekly_stats)
    total_papers = sum(w['total'] for w in weekly_stats)
    total_agi_asi = sum(w['core_agi_asi'] + w['strongly_related'] for w in weekly_stats)
    avg_relevance_rate = sum(w['relevance_rate'] for w in weekly_stats) / total_weeks
    
    summary += f"## 📊 Overall Statistics\n\n"
    summary += f"- **Total Weeks Analyzed**: {total_weeks}\n"
    summary += f"- **Total Papers**: {total_papers}\n"
    summary += f"- **Total AGI/ASI Papers**: {total_agi_asi}\n"
    summary += f"- **Average Relevance Rate**: {avg_relevance_rate:.1f}%\n\n"
    
    # Find weeks with highest AGI/ASI activity
    top_weeks = sorted(weekly_stats, key=lambda x: x['core_agi_asi'] + x['strongly_related'], reverse=True)[:3]
    
    summary += f"## 🏆 Top Weeks for AGI/ASI Research\n\n"
    for i, week_stat in enumerate(top_weeks, 1):
        week_name = week_stat['week'].split(' - ')[0]
        agi_asi_count = week_stat['core_agi_asi'] + week_stat['strongly_related']
        summary += f"{i}. **{week_name}**: {agi_asi_count} AGI/ASI papers ({week_stat['relevance_rate']}% relevance)\n"
    
    summary += "\n"
    
    return summary


def create_trend_chart(week_names: list, weekly_stats: list) -> go.Figure:
    """Create trend visualization chart"""
    # Prepare data
    relevance_rates = [w['relevance_rate'] for w in weekly_stats]
    agi_asi_counts = [w['core_agi_asi'] + w['strongly_related'] for w in weekly_stats]
    
    # Create figure with secondary y-axis
    fig = go.Figure()
    
    # Add relevance rate line
    fig.add_trace(go.Scatter(
        x=week_names,
        y=relevance_rates,
        mode='lines+markers',
        name='Relevance Rate (%)',
        line=dict(color='#667eea', width=3),
        marker=dict(size=8)
    ))
    
    # Add AGI/ASI paper count bars
    fig.add_trace(go.Bar(
        x=week_names,
        y=agi_asi_counts,
        name='AGI/ASI Papers',
        marker=dict(color='#764ba2'),
        yaxis='y2'
    ))
    
    # Update layout
    fig.update_layout(
        title='AGI/ASI Research Trends Over Time',
        xaxis_title='Week',
        yaxis_title='Relevance Rate (%)',
        yaxis2_title='AGI/ASI Paper Count',
        yaxis2=dict(
            title='AGI/ASI Paper Count',
            overlaying='y',
            side='right'
        ),
        legend=dict(x=0.1, y=1.1, orientation='h'),
        height=500,
        hovermode='x unified'
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
    
    with gr.Blocks(title="AGI/ASI Papers Analysis", theme=gr.themes.Soft()) as demo:
        
        # Header
        gr.Markdown("""
        # 🧠 AGI/ASI Papers Analysis
        
        Analyze AI papers from [AI-Papers-of-the-Week](https://github.com/dair-ai/AI-Papers-of-the-Week) 
        for AGI (Artificial General Intelligence) and ASI (Artificial Super Intelligence) relevance.
        
        **🎓 Educational Purpose**: This tool is created for educational purposes to demonstrate AGI/ASI research tracking and analysis.
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
                
                papers_df = gr.Dataframe(label="All Papers Ranking")
                
                advanced_output = gr.Markdown(label="Advanced Analysis")
                
                # Event handlers
                year_input.change(
                    update_week_dropdown,
                    inputs=[year_input],
                    outputs=[week_input]
                )
                
                analyze_btn.click(
                    analyze_week,
                    inputs=[year_input, week_input, model_selector, use_semantic],
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
                
                For Ollama, install from https://ollama.ai and run: `ollama serve`
                """)
            
            # Tab 4: Model Comparison
            with gr.Tab("🔬 Model Comparison"):
                gr.Markdown("## Compare Different Analysis Models")
                
                gr.Markdown("""
                ### Model Features Comparison
                
                | Model | Cost | Speed | Accuracy | Privacy | Setup |
                |-------|------|-------|----------|---------|-------|
                | Keyword | Free | ⚡⚡⚡ | ⭐⭐ | 🔒🔒🔒 | None |
                | OpenAI GPT | Paid | ⚡⚡ | ⭐⭐⭐⭐⭐ | 🔒 | API Key |
                | Anthropic Claude | Paid | ⚡⚡ | ⭐⭐⭐⭐⭐ | 🔒 | API Key |
                | Ollama | Free | ⚡ | ⭐⭐⭐⭐ | 🔒🔒🔒 | Local Install |
                | Hugging Face | Free Tier | ⚡⚡ | ⭐⭐⭐⭐ | 🔒 | API Key |
                
                ### Recommendations
                
                **For Quick Analysis**: Use Keyword-Based
                - Fastest option
                - No setup required
                - Good for high-volume screening
                
                **For Deep Analysis**: Use OpenAI GPT or Anthropic Claude
                - Best semantic understanding
                - Handles nuance well
                - Worth the cost for important research
                
                **For Privacy**: Use Ollama
                - Data stays on your machine
                - Free to use
                - Requires local setup
                
                **For Budget-Conscious**: Use Hugging Face
                - Free tier available
                - Good quality models
                - Simple API key setup
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
    demo = create_interface()
    demo.launch()