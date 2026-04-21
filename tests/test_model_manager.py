"""
Test suite for model_manager module
"""

import pytest
from model_manager import ModelManager


def test_model_manager_initialization():
    """Test that model manager initializes correctly"""
    manager = ModelManager()
    assert manager.current_model == "keyword"
    assert manager.model_configs is not None


def test_get_available_models():
    """Test getting available models"""
    manager = ModelManager()
    models = manager.get_available_models()
    
    assert len(models) == 10  # Updated to include all new models + DeepSeek
    model_ids = [m["id"] for m in models]
    assert "keyword" in model_ids
    assert "openai" in model_ids
    assert "anthropic" in model_ids
    assert "ollama" in model_ids
    assert "huggingface" in model_ids
    assert "cohere" in model_ids
    assert "google" in model_ids
    assert "together" in model_ids
    assert "replicate" in model_ids
    assert "deepseek" in model_ids


def test_set_model():
    """Test setting current model"""
    manager = ModelManager()
    
    assert manager.set_model("openai") == True
    assert manager.current_model == "openai"
    
    assert manager.set_model("invalid") == False
    assert manager.current_model == "openai"  # Should not change


def test_get_current_model():
    """Test getting current model"""
    manager = ModelManager()
    manager.set_model("anthropic")
    
    assert manager.get_current_model() == "anthropic"


def test_check_api_key():
    """Test API key checking"""
    manager = ModelManager()
    
    # Keyword doesn't need API key
    assert manager.check_api_key("keyword") == True
    
    # Other models would need API keys (will return False if not set)
    assert manager.check_api_key("openai") == False  # No key set


def test_keyword_analysis():
    """Test keyword-based analysis"""
    manager = ModelManager()
    
    test_paper = {
        'title': 'Test Paper',
        'summary': 'This is a test paper about AI'
    }
    
    result = manager.analyze_paper_semantic(test_paper, "keyword")
    
    assert result['model_used'] == "keyword"
    assert result['semantic_relevance'] == 0.0
    assert result['key_concepts'] == []


def test_batch_analyze():
    """Test batch analysis"""
    manager = ModelManager()
    
    papers = [
        {'title': 'Paper 1', 'summary': 'Summary 1'},
        {'title': 'Paper 2', 'summary': 'Summary 2'}
    ]
    
    results = manager.batch_analyze(papers, "keyword")
    
    assert len(results) == 2
    assert all('semantic_analysis' in p for p in results)
