# AGI/ASI Papers Analysis - Installation Guide

This guide will help you install and set up the AGI/ASI Papers Analysis tool on your local machine or development environment.

## 🎓 Educational Purpose

This tool is created for educational purposes to demonstrate AGI/ASI research tracking and analysis using modern AI techniques.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (for cloning the repository)
- (Optional) API keys for AI models (see below)

## Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/agi-asi-papers-analysis.git
cd agi-asi-papers-analysis
```

## Step 2: Create Virtual Environment

It's recommended to use a virtual environment to isolate dependencies:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

## Step 3: Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

The requirements include:
- `requests==2.31.0` - For fetching data from GitHub
- `gradio==4.0.0` - For the web interface
- `pandas==2.0.3` - For data manipulation
- `numpy==1.24.3` - For numerical operations
- `plotly==5.17.0` - For visualizations
- `markdown==3.5.1` - For markdown processing
- `openai==1.12.0` - For OpenAI API (optional)
- `anthropic==0.18.0` - For Anthropic API (optional)

## Step 4: (Optional) Set Up API Keys

To use semantic analysis with AI models, you'll need to set up API keys:

### OpenAI GPT

1. Get an API key from https://platform.openai.com/api-keys
2. Set the environment variable:
   ```bash
   export OPENAI_API_KEY=your_key_here
   ```
   Or on Windows:
   ```cmd
   set OPENAI_API_KEY=your_key_here
   ```

### Anthropic Claude

1. Get an API key from https://console.anthropic.com/
2. Set the environment variable:
   ```bash
   export ANTHROPIC_API_KEY=your_key_here
   ```

### Hugging Face

1. Get an API key from https://huggingface.co/settings/tokens
2. Set the environment variable:
   ```bash
   export HUGGINGFACE_API_KEY=your_key_here
   ```

### Ollama (Local Models)

1. Install Ollama from https://ollama.ai
2. Start the Ollama service:
   ```bash
   ollama serve
   ```
3. Download a model (e.g., Llama2):
   ```bash
   ollama pull llama2
   ```

## Step 5: Run the Application

Start the Gradio interface:

```bash
python app.py
```

The application will start and display a local URL (typically `http://127.0.0.1:7860`). Open this URL in your web browser to access the interface.

## Step 6: Verify Installation

1. Open the application in your browser
2. Select a year (e.g., "2026")
3. Select a week from the dropdown
4. Click "Analyze Week" with the default keyword-based model
5. You should see classification results and visualizations

## Troubleshooting

### Import Errors

If you encounter import errors, make sure you've installed all dependencies:

```bash
pip install --upgrade -r requirements.txt
```

### API Key Errors

If you see API key errors when using semantic analysis:
- Verify your API keys are set correctly
- Check that your API keys have sufficient credits/quotas
- Ensure you're using the correct environment variable names

### Ollama Connection Errors

If Ollama fails to connect:
- Ensure Ollama is running: `ollama serve`
- Check that Ollama is installed correctly
- Verify the model is downloaded: `ollama list`

### Port Already in Use

If port 7860 is already in use, you can specify a different port:

```bash
python app.py --port 7861
```

Or modify the `app.py` file:
```python
demo.launch(server_port=7861)
```

## Development Setup

For development, you may want to install additional tools:

```bash
# For code formatting
pip install black

# For linting
pip install flake8

# For testing
pip install pytest
```

## Next Steps

- Read the [Concept Guide](CONCEPT.md) to understand how the system works
- Check the [Deployment Guide](DEPLOYMENT.md) for deploying to production
- Explore the [Feature Ideas](FEATURES.md) for potential enhancements

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the documentation in the `docs/` directory
3. Open an issue on GitHub

---

**Note**: This tool is for educational purposes. Always verify AI model outputs and use them as a reference, not as definitive analysis.
