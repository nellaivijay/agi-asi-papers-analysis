"""
Test suite for ranker module
"""

import pytest
from ranker import PaperRanker


def test_ranker_initialization():
    """Test that ranker initializes correctly"""
    ranker = PaperRanker()
    assert ranker.weights is not None
    assert ranker.weights['relevance'] == 0.5
    assert ranker.weights['novelty'] == 0.3
    assert ranker.weights['impact'] == 0.2


def test_rank_papers():
    """Test paper ranking"""
    ranker = PaperRanker()
    
    papers = [
        {
            'title': 'High Impact Paper',
            'classification_result': {
                'classification': 'AGI',
                'combined_score': 90,
                'matched_agi_keywords': ['AGI', 'general intelligence'],
                'matched_asi_keywords': [],
                'matched_related_keywords': ['deep learning']
            }
        },
        {
            'title': 'Low Impact Paper',
            'classification_result': {
                'classification': 'Not Related',
                'combined_score': 10,
                'matched_agi_keywords': [],
                'matched_asi_keywords': [],
                'matched_related_keywords': ['neural networks']
            }
        }
    ]
    
    ranked = ranker.rank_papers(papers)
    
    assert len(ranked) == 2
    assert ranked[0]['title'] == 'High Impact Paper'
    assert ranked[1]['title'] == 'Low Impact Paper'
    assert ranked[0]['rank_position'] == 1
    assert ranked[1]['rank_position'] == 2


def test_calculate_ranking_scores():
    """Test ranking score calculation"""
    ranker = PaperRanker()
    
    paper = {
        'classification_result': {
            'classification': 'AGI',
            'combined_score': 80,
            'matched_agi_keywords': ['AGI'],
            'matched_asi_keywords': [],
            'matched_related_keywords': ['deep learning']
        }
    }
    
    scores = ranker.calculate_ranking_scores(paper)
    
    assert 'relevance_score' in scores
    assert 'novelty_score' in scores
    assert 'impact_score' in scores
    assert 'composite_score' in scores
    assert scores['relevance_score'] == 80


def test_calculate_novelty_score():
    """Test novelty score calculation"""
    ranker = PaperRanker()
    
    paper = {
        'classification_result': {
            'matched_agi_keywords': ['AGI', 'general intelligence'],
            'matched_asi_keywords': ['AI safety'],
            'matched_related_keywords': ['deep learning', 'neural networks']
        }
    }
    
    novelty_score = ranker.calculate_novelty_score(paper)
    
    assert 0 <= novelty_score <= 100


def test_calculate_impact_score():
    """Test impact score calculation"""
    ranker = PaperRanker()
    
    core_paper = {
        'classification_result': {
            'classification': 'ASI',
            'matched_asi_keywords': ['AI safety', 'alignment']
        }
    }
    
    impact_score = ranker.calculate_impact_score(core_paper)
    
    assert impact_score >= 70  # ASI papers should have high impact


def test_get_top_papers():
    """Test getting top papers"""
    ranker = PaperRanker()
    
    papers = [
        {
            'title': f'Paper {i}',
            'classification_result': {
                'classification': 'AGI' if i < 5 else 'Not Related',
                'combined_score': 100 - i * 10,
                'matched_agi_keywords': [],
                'matched_asi_keywords': [],
                'matched_related_keywords': []
            }
        }
        for i in range(10)
    ]
    
    top_papers = ranker.get_top_papers(papers, top_n=3)
    
    assert len(top_papers) == 3
    assert top_papers[0]['title'] == 'Paper 0'


def test_filter_by_classification():
    """Test filtering by classification level"""
    ranker = PaperRanker()
    
    papers = [
        {
            'classification_result': {'classification': 'ASI'}
        },
        {
            'classification_result': {'classification': 'AGI'}
        },
        {
            'classification_result': {'classification': 'ACI'}
        },
        {
            'classification_result': {'classification': 'ANI'}
        },
        {
            'classification_result': {'classification': 'Other AI'}
        },
        {
            'classification_result': {'classification': 'ML'}
        },
        {
            'classification_result': {'classification': 'DS'}
        },
        {
            'classification_result': {'classification': 'Not Related'}
        }
    ]
    
    # Filter for AGI level and above (AGI, ASI)
    filtered = ranker.filter_by_classification(papers, min_level='AGI')
    
    assert len(filtered) == 2
    assert all(p['classification_result']['classification'] in ['AGI', 'ASI'] for p in filtered)
