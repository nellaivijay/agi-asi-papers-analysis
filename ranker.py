"""
Paper Ranking Module
Ranks papers by relevance, impact, and novelty for AI research across the intelligence spectrum
"""

from typing import Dict, List


class PaperRanker:
    """Rank papers by multiple criteria for AI research across the intelligence spectrum"""
    
    def __init__(self):
        # Weights for different ranking criteria
        self.weights = {
            'relevance': 0.5,      # Intelligence spectrum relevance score
            'novelty': 0.3,        # Novelty/innovation potential
            'impact': 0.2         # Potential impact
        }
    
    def rank_papers(self, papers: List[Dict], criteria: str = 'composite') -> List[Dict]:
        """
        Rank papers by specified criteria
        
        Args:
            papers: List of classified papers
            criteria: Ranking criteria ('relevance', 'composite', 'all')
            
        Returns:
            List of papers sorted by ranking score
        """
        # Calculate ranking scores for each paper
        ranked_papers = []
        
        for paper in papers:
            if 'classification_result' not in paper:
                continue
                
            ranking_scores = self.calculate_ranking_scores(paper)
            paper['ranking_scores'] = ranking_scores
            
            if criteria == 'relevance':
                paper['final_rank'] = ranking_scores['relevance_score']
            elif criteria == 'composite':
                paper['final_rank'] = ranking_scores['composite_score']
            elif criteria == 'all':
                paper['final_rank'] = ranking_scores['composite_score']
            
            ranked_papers.append(paper)
        
        # Sort by final rank (descending)
        ranked_papers.sort(key=lambda x: x['final_rank'], reverse=True)
        
        # Add rank positions
        for i, paper in enumerate(ranked_papers, 1):
            paper['rank_position'] = i
        
        return ranked_papers
    
    def calculate_ranking_scores(self, paper: Dict) -> Dict:
        """
        Calculate ranking scores for a paper
        
        Args:
            paper: Paper dictionary with classification results
            
        Returns:
            Dictionary with various ranking scores
        """
        classification = paper.get('classification_result', {})
        
        # Relevance score (from classifier)
        relevance_score = classification.get('combined_score', 0)
        
        # Novelty score (based on keyword diversity and uniqueness)
        novelty_score = self.calculate_novelty_score(paper)
        
        # Impact score (based on classification level and keyword strength)
        impact_score = self.calculate_impact_score(paper)
        
        # Composite score (weighted combination)
        composite_score = (
            (relevance_score * self.weights['relevance']) +
            (novelty_score * self.weights['novelty']) +
            (impact_score * self.weights['impact'])
        )
        
        return {
            'relevance_score': relevance_score,
            'novelty_score': novelty_score,
            'impact_score': impact_score,
            'composite_score': round(composite_score, 2)
        }
    
    def calculate_novelty_score(self, paper: Dict) -> float:
        """
        Calculate novelty score based on keyword diversity and uniqueness
        
        Args:
            paper: Paper dictionary
            
        Returns:
            Novelty score (0-100)
        """
        classification = paper.get('classification_result', {})
        
        # Count matched keywords
        agi_matches = len(classification.get('matched_agi_keywords', []))
        asi_matches = len(classification.get('matched_asi_keywords', []))
        related_matches = len(classification.get('matched_related_keywords', []))
        
        total_matches = agi_matches + asi_matches + related_matches
        
        if total_matches == 0:
            return 0.0
        
        # Diversity bonus: papers with both AGI and ASI keywords get higher novelty
        diversity_bonus = 0
        if agi_matches > 0 and asi_matches > 0:
            diversity_bonus = 20.0
        
        # Base score from keyword count (capped at 80)
        base_score = min(total_matches * 5.0, 80.0)
        
        novelty_score = min(base_score + diversity_bonus, 100.0)
        
        return round(novelty_score, 2)
    
    def calculate_impact_score(self, paper: Dict) -> float:
        """
        Calculate impact score based on classification level and keyword strength
        
        Args:
            paper: Paper dictionary
            
        Returns:
            Impact score (0-100)
        """
        classification = paper.get('classification_result', {})
        level = classification.get('classification', 'Not Related')
        
        # Base score from classification level
        level_scores = {
            'ASI': 95.0,      # Highest impact - superintelligence
            'AGI': 90.0,      # Very high impact - general intelligence
            'ACI': 85.0,      # High impact - collective intelligence
            'ANI': 70.0,      # Medium-high impact - narrow intelligence
            'Other AI': 60.0,  # Medium impact - general AI
            'ML': 50.0,       # Medium impact - machine learning
            'DS': 40.0,       # Lower impact - data science
            'Not Related': 10.0
        }
        
        base_score = level_scores.get(level, 10.0)
        
        # Bonus for ASI keywords (highest potential impact)
        asi_matches = len(classification.get('matched_asi_keywords', []))
        asi_bonus = min(asi_matches * 5.0, 10.0)
        
        # Bonus for AGI keywords (high potential impact)
        agi_matches = len(classification.get('matched_agi_keywords', []))
        agi_bonus = min(agi_matches * 5.0, 10.0)
        
        # Bonus for ACI keywords (emerging field potential)
        aci_matches = len(classification.get('matched_aci_keywords', []))
        aci_bonus = min(aci_matches * 5.0, 10.0)
        
        # Bonus for ANI keywords (specialized AI impact)
        ani_matches = len(classification.get('matched_ani_keywords', []))
        ani_bonus = min(ani_matches * 3.0, 5.0)
        
        impact_score = min(base_score + asi_bonus + agi_bonus + aci_bonus + ani_bonus, 100.0)
        
        return round(impact_score, 2)
    
    def get_top_papers(self, papers: List[Dict], top_n: int = 10, 
                      criteria: str = 'composite') -> List[Dict]:
        """
        Get top N papers by ranking criteria
        
        Args:
            papers: List of papers
            top_n: Number of top papers to return
            criteria: Ranking criteria
            
        Returns:
            Top N papers
        """
        ranked = self.rank_papers(papers, criteria)
        return ranked[:top_n]
    
    def filter_by_classification(self, papers: List[Dict], 
                                  min_level: str = 'Other AI') -> List[Dict]:
        """
        Filter papers by minimum classification level
        
        Args:
            papers: List of papers
            min_level: Minimum classification level
            
        Returns:
            Filtered papers
        """
        level_hierarchy = {
            'Not Related': 0,
            'DS': 1,           # Data Science
            'ML': 2,           # Machine Learning
            'Other AI': 3,     # General AI topics
            'ANI': 4,          # Artificial Narrow Intelligence
            'ACI': 5,          # Artificial Collective Intelligence
            'AGI': 6,          # Artificial General Intelligence
            'ASI': 7           # Artificial Super Intelligence (Highest)
        }
        
        min_level_value = level_hierarchy.get(min_level, 0)
        
        filtered = []
        for paper in papers:
            classification = paper.get('classification_result', {})
            level = classification.get('classification', 'Not Related')
            level_value = level_hierarchy.get(level, 0)
            
            if level_value >= min_level_value:
                filtered.append(paper)
        
        return filtered


# Test the ranker
if __name__ == "__main__":
    ranker = PaperRanker()
    
    # Test with sample classified papers
    test_papers = [
        {
            'title': 'Neural Computers',
            'classification_result': {
                'classification': 'Core AGI/ASI',
                'combined_score': 85.0,
                'matched_agi_keywords': ['general intelligence', 'AGI'],
                'matched_asi_keywords': [],
                'matched_related_keywords': ['deep learning']
            }
        },
        {
            'title': 'Standard ML Paper',
            'classification_result': {
                'classification': 'Not Related',
                'combined_score': 5.0,
                'matched_agi_keywords': [],
                'matched_asi_keywords': [],
                'matched_related_keywords': ['deep learning']
            }
        },
        {
            'title': 'AI Safety Research',
            'classification_result': {
                'classification': 'Strongly Related',
                'combined_score': 60.0,
                'matched_agi_keywords': [],
                'matched_asi_keywords': ['AI safety', 'existential risk'],
                'matched_related_keywords': ['reinforcement learning']
            }
        }
    ]
    
    print("Testing paper ranker...")
    ranked = ranker.rank_papers(test_papers, criteria='composite')
    
    print("\nRanked Papers:")
    for paper in ranked:
        print(f"Rank {paper['rank_position']}: {paper['title']}")
        print(f"  Final Score: {paper['final_rank']}")
        print(f"  Classification: {paper['classification_result']['classification']}")
        print()