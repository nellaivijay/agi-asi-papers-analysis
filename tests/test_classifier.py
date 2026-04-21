"""
Test suite for classifier module
"""

import pytest
from classifier import AIPapersIntelligenceClassifier


def test_classifier_initialization():
    """Test that classifier initializes correctly"""
    classifier = AIPapersIntelligenceClassifier()
    assert classifier.agi_keywords is not None
    assert classifier.asi_keywords is not None
    assert classifier.aci_keywords is not None
    assert classifier.ani_keywords is not None
    assert classifier.other_ai_keywords is not None
    assert classifier.ml_keywords is not None
    assert classifier.ds_keywords is not None


def test_classifier_with_semantic():
    """Test classifier with semantic analysis enabled"""
    classifier = AIPapersIntelligenceClassifier(use_semantic=True, model_id="keyword")
    assert classifier.use_semantic == True
    assert classifier.model_id == "keyword"


def test_classify_paper():
    """Test paper classification"""
    classifier = AIPapersIntelligenceClassifier()
    
    test_paper = {
        'title': 'Neural Computers: A New Computing Paradigm',
        'summary': 'Researchers propose Neural Computers that unify computation and memory, potentially leading to artificial general intelligence.',
        'full_entry': 'Neural Computers: A New Computing Paradigm - This could be a step toward AGI'
    }
    
    result = classifier.classify_paper(test_paper)
    
    assert 'classification' in result
    assert 'classification_reason' in result
    assert 'asi_score' in result
    assert 'agi_score' in result
    assert 'aci_score' in result
    assert 'ani_score' in result
    assert 'other_ai_score' in result
    assert 'ml_score' in result
    assert 'ds_score' in result
    assert 'combined_score' in result
    assert 'matched_agi_keywords' in result
    assert 'matched_asi_keywords' in result
    assert 'matched_aci_keywords' in result
    assert 'matched_ani_keywords' in result
    assert 'matched_other_ai_keywords' in result
    assert 'matched_ml_keywords' in result
    assert 'matched_ds_keywords' in result


def test_classify_paper_agi():
    """Test classification of AGI paper"""
    classifier = AIPapersIntelligenceClassifier()
    
    agi_paper = {
        'title': 'General Intelligence in AI Systems',
        'summary': 'This paper discusses artificial general intelligence and transfer learning capabilities.',
        'full_entry': 'AGI paper content'
    }
    
    result = classifier.classify_paper(agi_paper)
    
    assert result['agi_score'] >= 1
    assert result['classification'] in ['ASI', 'AGI', 'ACI', 'ANI', 'Other AI', 'ML', 'DS']


def test_classify_paper_asi():
    """Test classification of ASI paper"""
    classifier = AIPapersIntelligenceClassifier()
    
    asi_paper = {
        'title': 'AI Safety and Alignment Problem',
        'summary': 'Analysis of existential risks from superintelligent AI systems and alignment challenges.',
        'full_entry': 'ASI safety paper'
    }
    
    result = classifier.classify_paper(asi_paper)
    
    assert result['asi_score'] >= 1
    assert result['classification'] in ['ASI', 'AGI', 'ACI', 'ANI', 'Other AI', 'ML', 'DS']


def test_classify_paper_not_related():
    """Test classification of non-related paper"""
    classifier = AIPapersIntelligenceClassifier()
    
    unrelated_paper = {
        'title': 'Image Classification with CNNs',
        'summary': 'A standard convolutional neural network for image classification.',
        'full_entry': 'Standard ML paper'
    }
    
    result = classifier.classify_paper(unrelated_paper)
    
    assert result['classification'] in ['ASI', 'AGI', 'ACI', 'ANI', 'Other AI', 'ML', 'DS', 'Not Related']


def test_batch_classify():
    """Test batch classification"""
    classifier = AIPapersIntelligenceClassifier()
    
    papers = [
        {'title': 'AGI Paper', 'summary': 'About general intelligence', 'full_entry': 'AGI'},
        {'title': 'ML Paper', 'summary': 'About machine learning', 'full_entry': 'ML'},
    ]
    
    results = classifier.batch_classify(papers)
    
    assert len(results) == 2
    assert all('classification_result' in p for p in results)


def test_get_statistics():
    """Test statistics calculation"""
    classifier = AIPapersIntelligenceClassifier()
    
    classified_papers = [
        {'classification_result': {'classification': 'ASI'}},
        {'classification_result': {'classification': 'AGI'}},
        {'classification_result': {'classification': 'ACI'}},
        {'classification_result': {'classification': 'ANI'}},
        {'classification_result': {'classification': 'Other AI'}},
        {'classification_result': {'classification': 'ML'}},
        {'classification_result': {'classification': 'DS'}},
        {'classification_result': {'classification': 'Not Related'}},
    ]
    
    stats = classifier.get_statistics(classified_papers)
    
    assert stats['total'] == 8
    assert stats['asi'] == 1
    assert stats['agi'] == 1
    assert stats['aci'] == 1
    assert stats['ani'] == 1
    assert stats['other_ai'] == 1
    assert stats['ml'] == 1
    assert stats['ds'] == 1
    assert stats['not_related'] == 1


def test_get_statistics_empty():
    """Test statistics with empty list"""
    classifier = AIPapersIntelligenceClassifier()
    
    stats = classifier.get_statistics([])
    
    assert stats['total'] == 0
    assert stats['asi'] == 0
    assert stats['agi'] == 0
    assert stats['aci'] == 0
    assert stats['ani'] == 0
    assert stats['other_ai'] == 0
    assert stats['ml'] == 0
    assert stats['ds'] == 0
    assert stats['not_related'] == 0
