---
title: AI Papers Intelligence Classifier
emoji: 🧠
colorFrom: purple
colorTo: red
sdk: gradio
sdk_version: 4.0.0
python_version: "3.10"
app_file: app.py
pinned: false
license: mit
---

# 🧠 AI Papers Intelligence Classifier

Analyze AI papers from [AI-Papers-of-the-Week](https://github.com/dair-ai/AI-Papers-of-the-Week) across the intelligence spectrum: ANI (Artificial Narrow Intelligence), AGI (Artificial General Intelligence), ASI (Artificial Super Intelligence), ACI (Artificial Collective Intelligence), ML (Machine Learning), and DS (Data Science) with ranking, trend analysis, and comparison tools.

## 🎯 Purpose

This tool helps researchers, students, and AI enthusiasts track and analyze AI research developments across the entire intelligence spectrum by automatically classifying and ranking AI papers from the weekly AI-Papers-of-the-Week newsletter.

## 🚀 Features

### **Multiple AI Model Support**
- **Keyword-Based** (Free): Fast pattern matching, no setup required
- **OpenAI GPT** (Paid): Advanced semantic understanding with GPT-4/GPT-3.5
- **Anthropic Claude** (Paid): Sophisticated reasoning with Claude models
- **Ollama** (Free, Local): Privacy-focused local models
- **Hugging Face** (Free Tier): Access to open-source models
- **DeepSeek-R1** (Free via HF): Chain-of-thought reasoning for accurate classification

### **Weekly Analysis**
- Analyze papers from any week (2023-2026)
- Three classification modes: Keyword, Reasoning, Hybrid
- Multi-criteria ranking (relevance, novelty, impact)
- Interactive visualizations:
  - Classification distribution pie chart
  - Ranking scores bar chart
  - Relevance vs novelty scatter plot

### **Trend Analysis**
- Track AI research trends across the intelligence spectrum
- Visualize relevance rates across weeks
- Identify periods of high activity in different AI domains
- Compare research patterns across years

### **Classification System**
- **ASI**: Direct focus on superintelligence and existential risk
- **AGI**: Direct focus on general intelligence capabilities
- **ACI**: Multi-agent systems and collective intelligence
- **ANI**: Artificial Narrow Intelligence and specialized AI systems
- **Other AI**: General AI topics not fitting specific categories
- **ML**: Machine Learning algorithms and techniques
- **DS**: Data Science methodologies and applications

### **Ranking Methodology**
Papers are ranked using a composite score:
- **Relevance** (50%): Keyword density and semantic analysis across all intelligence levels
- **Novelty** (30%): Keyword diversity and innovation potential
- **Impact** (20%): Classification level and potential impact

### **Model Comparison**
- Compare different AI models side-by-side
- Understand trade-offs between speed, accuracy, and cost
- Get recommendations for different use cases

## 📊 How It Works

1. **Data Fetching**: Automatically fetches weekly reports from AI-Papers-of-the-Week GitHub repository
2. **Model Selection**: Choose from keyword-based, AI-powered semantic analysis, or reasoning-based classification
3. **Classification Mode**: Select Keyword (fast), Reasoning (accurate), or Hybrid (balanced)
4. **Classification**: Uses keyword matching and/or AI models to identify AGI/ASI/ACI-related papers
5. **Scoring**: Calculates relevance scores based on keyword density and semantic analysis
6. **Ranking**: Ranks papers by composite score considering multiple criteria
7. **Visualization**: Provides interactive charts and detailed insights

## 📚 Documentation

### Project Planning (Spec-Driven Development)
This project follows a Spec-Driven Development approach. Planning documents are available in the `.planning/` directory:

- **[PROJECT.md](.planning/PROJECT.md)** - Project vision, scope, and objectives
- **[REQUIREMENTS.md](.planning/REQUIREMENTS.md)** - Detailed functional and non-functional requirements
- **[ROADMAP.md](.planning/ROADMAP.md)** - Implementation phases and milestones
- **[STATE.md](.planning/STATE.md)** - Current project state and progress
- **[CONTEXT.md](.planning/CONTEXT.md)** - Background and project context
- **[RESEARCH.md](.planning/RESEARCH.md)** - Research findings and technical decisions

### Technical Documentation
- **[Installation Guide](INSTALLATION.md)** - Step-by-step setup instructions
- **[Deployment Guide](DEPLOYMENT.md)** - Deployment options (Hugging Face, Docker, Cloud)
- **[Concept Guide](CONCEPT.md)** - System architecture and methodology
- **[How It Works](HOW_IT_WORKS.md)** - Detailed technical explanation
- **[Feature Ideas](FEATURES.md)** - Future enhancements and roadmap

## 🏷️ Intelligence Level Keywords

### ASI Keywords
- Superintelligence, ASI, existential risk
- AI safety, alignment problem
- Recursive self-improvement, intelligence explosion
- Singularity, transformative AI

### AGI Keywords
- General intelligence, AGI, human-level AI
- Transfer learning, few-shot learning, meta-learning
- Reasoning systems, commonsense reasoning
- Neural-symbolic integration, multi-modal learning

### ACI Keywords
- Multi-agent systems, swarm intelligence
- Collective intelligence, collaborative AI
- Distributed cognition, emergent behavior
- Human-AI collaboration, agent coordination

### ANI Keywords
- Narrow AI, specialized AI, task-specific AI
- Domain-specific systems, expert systems
- Single-purpose AI, focused AI applications
- Specialized neural networks, task optimization

### Other AI Keywords
- Artificial intelligence, AI research
- AI applications, AI systems
- Computer vision, NLP, speech recognition
- Robotics, autonomous systems

### ML Keywords
- Machine learning, deep learning
- Neural networks, CNN, RNN, Transformer
- Supervised learning, unsupervised learning
- Reinforcement learning, feature engineering

### DS Keywords
- Data science, data analysis
- Data mining, big data
- Statistical analysis, data visualization
- Data engineering, data pipelines

## 🚀 Quick Start

### Local Installation

```bash
# Clone the repository
git clone https://github.com/nellaivijay/ai-papers-intelligence-classifier.git
cd ai-papers-intelligence-classifier

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

### Using AI Models (Optional)

To use semantic analysis with AI models, set up API keys:

```bash
# OpenAI
export OPENAI_API_KEY=your_key_here

# Anthropic
export ANTHROPIC_API_KEY=your_key_here

# Hugging Face
export HUGGINGFACE_API_KEY=your_key_here
```

For Ollama (local models), install from https://ollama.ai and run:
```bash
ollama serve
ollama pull llama2
```

## 🚀 Deployment

### Hugging Face Spaces (Recommended)

1. Create a new Space at https://huggingface.co/new-space
2. Choose:
   - SDK: Gradio
   - Python: 3.10
   - License: MIT
3. Clone the Space and push your code
4. Add environment variables in Space Settings for API keys

See [Deployment Guide](DEPLOYMENT.md) for detailed instructions.

### Docker

```bash
# Build image
docker build -t agi-asi-analysis .

# Run container
docker run -p 7860:7860 \
  -e OPENAI_API_KEY=your_key \
  agi-asi-analysis
```

### Cloud Deployment

See [Deployment Guide](DEPLOYMENT.md) for AWS, GCP, Azure, and Heroku instructions.

## 🎓 Educational Purpose

This project is created for **educational purposes only** to demonstrate:
- AI research tracking and analysis across the intelligence spectrum
- Natural language processing for paper classification
- Data visualization for research trends
- Modern web application development with Gradio

The tool helps researchers and students understand the landscape of AI research and track developments across all intelligence levels from narrow AI to superintelligence.

## 📚 Data Source

All papers are sourced from the [AI-Papers-of-the-Week](https://github.com/dair-ai/AI-Papers-of-the-Week) repository by DAIR.AI, which provides curated weekly lists of top AI papers from 2023 to present.

## 🛠️ Technology Stack

- **Frontend**: Gradio 4.0.0
- **Backend**: Python 3.10
- **Data Processing**: Pandas, NumPy, scikit-learn
- **Visualization**: Plotly
- **AI Models**: OpenAI, Anthropic, Ollama, Hugging Face, DeepSeek-R1
- **Data Source**: GitHub API (AI-Papers-of-the-Week)

## 🔗 Related Resources

- [AI-Papers-of-the-Week](https://github.com/dair-ai/AI-Papers-of-the-Week)
- [Machine Intelligence Research Institute](https://intelligence.org/)
- [Center for Human-Compatible AI](https://humancompatible.ai/)
- [Future of Humanity Institute](https://www.fhi.ox.ac.uk/)

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

This is an educational project. Suggestions and improvements are welcome!

---

**Last Updated**: 2026-04-20  
**Version**: 1.0.0  
**Status**: ✅ Active Development