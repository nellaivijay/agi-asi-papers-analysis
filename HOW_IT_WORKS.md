# AI Papers Intelligence Classifier - How It Works

This guide explains the inner workings of the AI Papers Intelligence Classifier tool, from data fetching to visualization.

## 🎓 Educational Purpose

This tool is created for educational purposes to demonstrate how to build an AI-powered research analysis system across the intelligence spectrum.

## System Overview

The tool follows this pipeline:

```
User Input → Data Fetching → Classification → Ranking → Visualization → Output
```

Let's explore each component in detail.

## 1. Data Fetching (`data_fetcher.py`)

### Purpose
Fetches weekly AI papers from the AI-Papers-of-the-Week GitHub repository.

### How It Works

#### GitHub API Integration
```python
url = f"{base_url}/{year}.md"
response = requests.get(url, timeout=10)
```

The tool fetches markdown files directly from GitHub's raw content URL:
- Base URL: `https://raw.githubusercontent.com/dair-ai/AI-Papers-of-the-Week/main/years`
- File pattern: `{year}.md` (e.g., `2026.md`)

#### Markdown Parsing
The markdown files contain weekly paper listings in this format:

```markdown
## Top AI Papers of the Week (April 6 - April 12) - 2026

| 1) **Neural Computers: A New Computing Paradigm** - Researchers propose Neural Computers...
| [Paper](https://arxiv.org/abs/xxxx) [Tweet](https://twitter.com/xxx)
| 2) **Another Paper Title** - Description...
```

The parser uses regular expressions to extract:
1. **Week Information**: Date range and year
   ```python
   pattern = r'\(([^)]+)\)\s*-\s*(\d{4})'
   ```

2. **Paper Entries**: Individual papers with metadata
   ```python
   paper_match = re.match(r'^\|?\s*\d+\)\s*\*\*(.+?)\*\*', line)
   ```

3. **Links**: Paper URLs and social media links
   ```python
   paper_match = re.search(r'\[Paper\]\(([^)]+)\)', line)
   tweet_match = re.search(r'\[Tweet\]\(([^)]+)\)', line)
   ```

#### Caching Strategy
To reduce API calls and improve performance:
- Cache duration: 1 hour
- Cache key: `year_{year}`
- Automatic cache invalidation after TTL

```python
if cache_key in self.cache:
    cached_data, timestamp = self.cache[cache_key]
    if (datetime.now() - timestamp).seconds < self.cache_ttl:
        return cached_data
```

### Data Structure
The fetched data is structured as:

```python
{
    "April 6 - April 12 - 2026": {
        "date_range": "April 6 - April 12",
        "papers": [
            {
                "title": "Neural Computers: A New Computing Paradigm",
                "summary": "Researchers propose...",
                "links": {
                    "paper": "https://arxiv.org/abs/xxxx",
                    "tweet": "https://twitter.com/xxx"
                },
                "full_entry": "..."
            },
            # ... more papers
        ],
        "total_papers": 10
    },
    # ... more weeks
}
```

## 2. Model Management (`model_manager.py`)

### Purpose
Manages multiple AI models for semantic analysis of papers.

### Supported Models

#### 1. Keyword-Based (Default)
- **How it works**: Pattern matching against keyword lists
- **Speed**: Fastest (⚡⚡⚡)
- **Cost**: Free
- **Use case**: Quick screening, high-volume analysis

#### 2. OpenAI GPT
- **How it works**: Uses OpenAI's GPT-4 or GPT-3.5 for semantic understanding
- **API**: OpenAI Chat Completions API
- **Prompt engineering**: Structured prompt for JSON output
```python
prompt = f"""
Analyze this AI paper for AGI/ASI relevance.
Title: {title}
Summary: {summary}

Provide:
1. Semantic relevance score (0-100)
2. Key concepts related to AGI/ASI
3. Brief reasoning

Format as JSON with keys: semantic_relevance, key_concepts, reasoning
"""
```

#### 3. Anthropic Claude
- **How it works**: Uses Claude models for advanced reasoning
- **API**: Anthropic Messages API
- **Model**: claude-3-haiku-20240307 (cost-effective)
- **Features**: Excellent for complex, nuanced analysis

#### 4. Ollama (Local)
- **How it works**: Runs models locally on your machine
- **API**: Ollama's local HTTP API
- **Endpoint**: `http://localhost:11434/api/generate`
- **Privacy**: Data never leaves your machine
```python
response = requests.post(
    f"{base_url}/api/generate",
    json={
        "model": "llama2",
        "prompt": prompt,
        "stream": False
    }
)
```

#### 5. Hugging Face Inference
- **How it works**: Uses Hugging Face's inference API
- **API**: Hugging Face Inference Endpoints
- **Model**: mistralai/Mistral-7B-Instruct-v0.2
- **Cost**: Free tier available with rate limits

### Model Selection Flow

```python
def analyze_paper_semantic(paper_data, model_id):
    if model_id == "keyword":
        return _keyword_analysis(paper_data)
    elif model_id == "openai":
        return _openai_analysis(paper_data)
    elif model_id == "anthropic":
        return _anthropic_analysis(paper_data)
    # ... etc
```

### Fallback Mechanism
If an AI model fails (API error, timeout, missing key), the system automatically falls back to keyword-based analysis:
```python
except Exception as e:
    print(f"OpenAI analysis error: {e}")
    return self._keyword_analysis(paper_data)
```

## 3. Classification (`classifier.py`)

### Purpose
Classifies papers by AGI/ASI relevance using hybrid keyword + semantic analysis.

### Classification Process

#### Step 1: Text Preprocessing
```python
title = paper_data.get('title', '').lower()
summary = paper_data.get('summary', '').lower()
full_entry = paper_data.get('full_entry', '').lower()
combined_text = f"{title} {summary} {full_entry}"
```

#### Step 2: Keyword Scoring
Counts matches against three keyword lists:

**AGI Keywords** (weighted 3.0x):
- "general intelligence", "AGI", "human-level AI"
- "transfer learning", "few-shot learning", "meta-learning"
- "reasoning systems", "neuro-symbolic integration"
- ... 46 total keywords

**ASI Keywords** (weighted 3.0x):
- "superintelligence", "ASI", "existential risk"
- "AI safety", "AI alignment", "value alignment"
- "recursive self-improvement", "singularity"
- ... 40 total keywords

**Related Keywords** (weighted 1.0x):
- "deep learning", "neural networks", "LLM"
- "emergent behavior", "scaling laws"
- "reasoning capabilities", "autonomy"
- ... 20 total keywords

```python
agi_score = self.calculate_keyword_score(combined_text, self.agi_keywords)
asi_score = self.calculate_keyword_score(combined_text, self.asi_keywords)
related_score = self.calculate_keyword_score(combined_text, self.related_keywords)
```

#### Step 3: Semantic Analysis (Optional)
If semantic analysis is enabled:
```python
if self.use_semantic:
    semantic_result = self.model_manager.analyze_paper_semantic(paper_data, self.model_id)
```

The semantic result includes:
- `semantic_relevance`: 0-100 score from AI model
- `key_concepts`: List of identified concepts
- `reasoning`: Explanation of classification
- `model_used`: Which AI model was used

#### Step 4: Classification Determination
Based on scores and semantic analysis:

```python
def determine_classification(agi_score, asi_score, related_score, semantic_result):
    max_core_score = max(agi_score, asi_score)
    
    # Semantic boost
    if semantic_result and semantic_result["semantic_relevance"] > 70:
        if max_core_score >= 1:
            return "Core AGI/ASI"
    
    # Keyword-based rules
    if max_core_score >= 3:
        return "Core AGI/ASI"
    elif max_core_score >= 2:
        return "Strongly Related"
    elif max_core_score >= 1:
        return "Tangentially Related"
    elif related_score >= 4:
        return "Tangentially Related"
    else:
        return "Not Related"
```

#### Step 5: Combined Score Calculation
```python
def calculate_combined_score(agi_score, asi_score, related_score, semantic_result):
    weighted_score = (agi_score * 3.0) + (asi_score * 3.0) + (related_score * 1.0)
    
    # Add semantic boost
    if semantic_result:
        semantic_score = semantic_result["semantic_relevance"]
        weighted_score += (semantic_score / 100) * 20.0
    
    # Normalize to 0-100
    normalized_score = min(weighted_score * 2.0, 100)
    return round(normalized_score, 2)
```

### Classification Result Structure
```python
{
    "classification": "Core AGI/ASI",
    "classification_reason": "High relevance with 3 core AGI/ASI keyword matches",
    "agi_score": 3,
    "asi_score": 0,
    "related_score": 2,
    "combined_score": 85.0,
    "matched_agi_keywords": ["general intelligence", "AGI", "transfer learning"],
    "matched_asi_keywords": [],
    "matched_related_keywords": ["deep learning", "neural networks"],
    "semantic_analysis": {
        "model_used": "openai",
        "semantic_relevance": 85,
        "key_concepts": ["general intelligence", "transfer learning"],
        "reasoning": "Paper directly addresses AGI capabilities..."
    }
}
```

## 4. Ranking (`ranker.py`)

### Purpose
Ranks papers by multiple criteria to identify most important research.

### Ranking Criteria

#### 1. Relevance Score (50% weight)
- Based on classification combined score
- Higher for papers with more keyword matches
- Boosted by semantic analysis if enabled

#### 2. Novelty Score (30% weight)
- Measures keyword diversity and uniqueness
- Calculated as:
```python
total_matches = agi_matches + asi_matches + related_matches
base_score = min(total_matches * 5.0, 80.0)

# Diversity bonus for papers with both AGI and ASI keywords
if agi_matches > 0 and asi_matches > 0:
    diversity_bonus = 20.0

novelty_score = min(base_score + diversity_bonus, 100.0)
```

#### 3. Impact Score (20% weight)
- Based on classification level
- Base scores:
  - Core AGI/ASI: 90.0
  - Strongly Related: 70.0
  - Tangentially Related: 40.0
  - Not Related: 10.0
- Bonus for ASI keywords (up to 10 points)

```python
def calculate_impact_score(paper):
    level = paper['classification_result']['classification']
    base_score = level_scores[level]
    
    asi_matches = len(paper['classification_result']['matched_asi_keywords'])
    asi_bonus = min(asi_matches * 5.0, 10.0)
    
    return min(base_score + asi_bonus, 100.0)
```

### Composite Score Calculation
```python
composite_score = (
    (relevance_score * 0.5) +
    (novelty_score * 0.3) +
    (impact_score * 0.2)
)
```

### Ranking Process
```python
def rank_papers(papers, criteria='composite'):
    # Calculate scores for each paper
    for paper in papers:
        ranking_scores = calculate_ranking_scores(paper)
        paper['ranking_scores'] = ranking_scores
        paper['final_rank'] = ranking_scores['composite_score']
    
    # Sort by final rank (descending)
    ranked_papers.sort(key=lambda x: x['final_rank'], reverse=True)
    
    # Add rank positions
    for i, paper in enumerate(ranked_papers, 1):
        paper['rank_position'] = i
    
    return ranked_papers
```

### Filtering
Can filter papers by minimum classification level:
```python
def filter_by_classification(papers, min_level='Tangentially Related'):
    level_hierarchy = {
        'Not Related': 0,
        'Tangentially Related': 1,
        'Strongly Related': 2,
        'Core AGI/ASI': 3
    }
    
    min_level_value = level_hierarchy[min_level]
    filtered = [p for p in papers if level_hierarchy[p['classification']] >= min_level_value]
    return filtered
```

## 5. Visualization (`app.py`)

### Purpose
Creates interactive charts to help users understand the data.

### Chart Types

#### 1. Classification Distribution (Pie Chart)
Shows proportion of papers in each classification level:
```python
fig = go.Figure(data=[go.Pie(
    labels=['Core AGI/ASI', 'Strongly Related', 'Tangentially Related', 'Not Related'],
    values=[stats['core_agi_asi'], stats['strongly_related'], 
            stats['tangentially_related'], stats['not_related']],
    marker=dict(colors=['#00CC96', '#EF553B', '#FFA15A', '#AB63FA']),
    textinfo='label+percent',
    hole=0.3  # Donut chart style
)])
```

#### 2. Ranking Scores (Bar Chart)
Compares final rank vs combined relevance for top papers:
```python
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
```

#### 3. Relevance vs Novelty (Scatter Plot)
Shows relationship between relevance and innovation:
```python
fig = go.Figure(data=go.Scatter(
    x=relevance_scores,
    y=novelty_scores,
    mode='markers',
    marker=dict(
        size=10,
        color=colors,  # Color by classification
        opacity=0.7
    ),
    text=titles,
    hovertemplate='<b>%{text}</b><br>Relevance: %{x:.1f}<br>Novelty: %{y:.1f}'
))
```

#### 4. Trend Analysis (Line Chart)
Tracks AGI/ASI research patterns over time:
```python
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=week_names,
    y=relevance_rates,
    mode='lines+markers',
    name='Relevance Rate (%)',
    line=dict(color='#667eea', width=3)
))
fig.add_trace(go.Bar(
    x=week_names,
    y=agi_asi_counts,
    name='AGI/ASI Papers',
    marker=dict(color='#764ba2'),
    yaxis='y2'
))
```

## 6. User Interface (`app.py`)

### Gradio Interface Structure

#### Main Components
```python
with gr.Blocks(title="AGI/ASI Papers Analysis", theme=gr.themes.Soft()) as demo:
    # Header with description
    gr.Markdown("# 🧠 AGI/ASI Papers Analysis")
    
    with gr.Tabs():
        # Tab 1: Weekly Analysis
        with gr.Tab("📊 Weekly Analysis"):
            # Year and week selectors
            # Model selector
            # Semantic analysis toggle
            # Analyze button
            # Outputs: summary, stats, charts, dataframe
        
        # Tab 2: Trend Analysis
        with gr.Tab("📈 Trend Analysis"):
            # Year selector
            # Trend analysis button
            # Outputs: trend summary, trend chart
        
        # Tab 3: About
        with gr.Tab("ℹ️ About"):
            # Documentation and methodology
        
        # Tab 4: Model Comparison
        with gr.Tab("🔬 Model Comparison"):
            # Model comparison table
            # Recommendations
```

### Event Handlers
```python
# Update week dropdown when year changes
year_input.change(
    update_week_dropdown,
    inputs=[year_input],
    outputs=[week_input]
)

# Run analysis when button clicked
analyze_btn.click(
    analyze_week,
    inputs=[year_input, week_input, model_selector, use_semantic],
    outputs=[summary_output, stats_output, top_papers_output, 
             papers_df, classification_chart, ranking_chart, scatter_chart]
)
```

### Dynamic Week Loading
```python
def update_week_dropdown(year):
    weeks = fetcher.get_available_weeks(year)
    if weeks:
        return gr.Dropdown(choices=weeks, value=weeks[0])
    return gr.Dropdown(choices=["No weeks available"], value="No weeks available")
```

## Complete Workflow Example

### User Action
1. User selects "2026" for year
2. Week dropdown populates with available weeks
3. User selects "April 6 - April 12 - 2026"
4. User selects "openai" model
5. User enables "Semantic Analysis"
6. User clicks "Analyze Week"

### System Response
1. **Data Fetching**
   - Fetcher retrieves 2026 data from GitHub
   - Parses markdown to extract papers
   - Returns 10 papers for the selected week

2. **Classification**
   - Classifier initializes with OpenAI model
   - For each paper:
     - Calculates keyword scores (AGI: 2, ASI: 1, Related: 3)
     - Calls OpenAI API for semantic analysis
     - Receives semantic relevance: 75
     - Determines classification: "Strongly Related"
     - Calculates combined score: 82.5

3. **Ranking**
   - Ranker calculates:
     - Relevance: 82.5
     - Novelty: 65.0 (diversity bonus applied)
     - Impact: 75.0 (Strongly Related base)
     - Composite: 76.25

4. **Visualization**
   - Creates classification pie chart
   - Creates ranking bar chart (top 15)
   - Creates relevance vs novelty scatter plot

5. **Output**
   - Summary markdown with statistics
   - Statistics breakdown
   - Top 10 papers with rankings
   - Dataframe with all papers
   - Three interactive charts

## Performance Characteristics

### Response Times (Approximate)

| Operation | Keyword Only | With Semantic |
|-----------|--------------|---------------|
| Data Fetching | 0.5-1s | 0.5-1s |
| Classification (10 papers) | 0.1s | 10-30s |
| Ranking | 0.05s | 0.05s |
| Visualization | 0.5s | 0.5s |
| **Total** | **1.5-2s** | **11-32s** |

### Resource Usage

**Memory**: ~100-200MB (typical)
**CPU**: Low for keyword, moderate for semantic
**Network**: ~1-5MB per analysis (data fetching + API calls)

### Scalability

**Keyword-only**: Can handle 100+ papers easily
**With semantic**: Limited by API rate limits and costs
**Recommended**: 10-20 papers per analysis with semantic

## Error Handling

### Common Error Scenarios

1. **GitHub API Failure**
   - Falls back to cached data if available
   - Returns error message if no cache

2. **AI Model API Failure**
   - Falls back to keyword analysis
   - Logs error for debugging

3. **Missing Data**
   - Returns "No data found" message
   - Suggests trying different week/year

4. **Invalid Input**
   - Validates year and week selections
   - Provides helpful error messages

## Educational Takeaways

This project demonstrates:

1. **Hybrid AI Systems**: Combining rule-based and ML approaches
2. **API Integration**: Working with multiple AI providers
3. **Data Pipelines**: From raw data to actionable insights
4. **Interactive Visualization**: Creating user-friendly data exploration
5. **Error Resilience**: Graceful degradation when components fail
6. **Performance Optimization**: Caching, batching, and efficient algorithms

---

**Note**: This tool is for educational purposes. Always verify AI outputs and use them as a reference, not as definitive analysis.
