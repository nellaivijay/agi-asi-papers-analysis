"""
AGI/ASI Classifier Module
Classifies AI papers by AGI (Artificial General Intelligence) and ASI (Artificial Super Intelligence) relevance
"""

from typing import Dict, List


class AGIASIClassifier:
    """Classify papers by AGI/ASI relevance using keyword analysis"""
    
    def __init__(self):
        # AGI (Artificial General Intelligence) keywords
        self.agi_keywords = [
            "general intelligence",
            "artificial general intelligence",
            "AGI",
            "human-level AI",
            "human-level artificial intelligence",
            "universal intelligence",
            "transfer learning",
            "few-shot learning",
            "one-shot learning",
            "zero-shot learning",
            "meta-learning",
            "learning to learn",
            "reasoning systems",
            "commonsense reasoning",
            "causal reasoning",
            "symbolic reasoning",
            "neural-symbolic integration",
            "neuro-symbolic",
            "multi-modal learning",
            "cross-domain adaptation",
            "domain adaptation",
            "few-shot adaptation",
            "continual learning",
            "lifelong learning",
            "autonomous agents",
            "self-improving AI",
            "recursive improvement",
            "broad capabilities",
            "general-purpose AI",
            "versatile AI",
            "flexible intelligence",
            "adaptive intelligence"
        ]
        
        # ASI (Artificial Super Intelligence) keywords
        self.asi_keywords = [
            "superintelligence",
            "artificial superintelligence",
            "ASI",
            "existential risk",
            "AI safety",
            "AI alignment",
            "alignment problem",
            "value alignment",
            "recursive self-improvement",
            "intelligence explosion",
            "singularity",
            "technological singularity",
            "transformative AI",
            "transformative artificial intelligence",
            "AI control problem",
            "safe AI",
            "beneficial AI",
            "friendly AI",
            "long-term AI futures",
            "AI governance",
            "AI policy",
            "AI ethics",
            "machine ethics",
            "superintelligent systems",
            "post-human AI",
            "superhuman intelligence",
            "god-like AI",
            "omniscient AI",
            "omnipotent AI",
            "AI risk",
            "x-risk",
            "global catastrophic risk",
            "existential catastrophe",
            "AI takeover",
            "AI rebellion",
            "paperclip maximizer",
            "instrumental convergence",
            "orthogonality thesis",
            "treacherous turn"
        ]
        
        # Related but not core keywords (for broader context)
        self.related_keywords = [
            "deep learning",
            "neural networks",
            "machine learning",
            "reinforcement learning",
            "large language models",
            "LLM",
            "foundation models",
            "transformer models",
            "attention mechanisms",
            "emergent behavior",
            "scaling laws",
            "compute scaling",
            "data scaling",
            "emergent abilities",
            "reasoning capabilities",
            "planning",
            "decision making",
            "autonomy",
            "agency",
            "goal-directed behavior",
            "optimization",
            "search algorithms"
        ]
    
    def classify_paper(self, paper_data: Dict) -> Dict:
        """
        Classify a paper by AGI/ASI relevance
        
        Args:
            paper_data: Dictionary containing paper information (title, summary, etc.)
            
        Returns:
            Dictionary with classification results and scores
        """
        title = paper_data.get('title', '').lower()
        summary = paper_data.get('summary', '').lower()
        full_entry = paper_data.get('full_entry', '').lower()
        
        # Combine all text for analysis
        combined_text = f"{title} {summary} {full_entry}"
        
        # Calculate scores
        agi_score = self.calculate_keyword_score(combined_text, self.agi_keywords)
        asi_score = self.calculate_keyword_score(combined_text, self.asi_keywords)
        related_score = self.calculate_keyword_score(combined_text, self.related_keywords)
        
        # Determine classification
        classification = self.determine_classification(agi_score, asi_score, related_score)
        
        # Calculate combined relevance score
        combined_score = self.calculate_combined_score(agi_score, asi_score, related_score)
        
        return {
            'classification': classification['level'],
            'classification_reason': classification['reason'],
            'agi_score': agi_score,
            'asi_score': asi_score,
            'related_score': related_score,
            'combined_score': combined_score,
            'matched_agi_keywords': self.find_matched_keywords(combined_text, self.agi_keywords),
            'matched_asi_keywords': self.find_matched_keywords(combined_text, self.asi_keywords),
            'matched_related_keywords': self.find_matched_keywords(combined_text, self.related_keywords)
        }
    
    def calculate_keyword_score(self, text: str, keywords: List[str]) -> int:
        """
        Calculate keyword relevance score
        
        Args:
            text: Text to analyze
            keywords: List of keywords to search for
            
        Returns:
            Number of keyword matches
        """
        score = 0
        for keyword in keywords:
            if keyword.lower() in text:
                score += 1
        return score
    
    def find_matched_keywords(self, text: str, keywords: List[str]) -> List[str]:
        """Find which keywords matched in the text"""
        matched = []
        for keyword in keywords:
            if keyword.lower() in text:
                matched.append(keyword)
        return matched
    
    def determine_classification(self, agi_score: int, asi_score: int, related_score: int) -> Dict:
        """
        Determine classification level based on scores
        
        Returns:
            Dictionary with classification level and reasoning
        """
        max_core_score = max(agi_score, asi_score)
        
        if max_core_score >= 3:
            return {
                'level': "Core AGI/ASI",
                'reason': f"High relevance with {max_core_score} core AGI/ASI keyword matches"
            }
        elif max_core_score >= 2:
            return {
                'level': "Strongly Related",
                'reason': f"Good relevance with {max_core_score} core AGI/ASI keyword matches"
            }
        elif max_core_score >= 1:
            if related_score >= 3:
                return {
                    'level': "Tangentially Related",
                    'reason': f"Some AGI/ASI relevance with {max_core_score} core and {related_score} related keyword matches"
                }
            else:
                return {
                    'level': "Tangentially Related",
                    'reason': f"Minimal AGI/ASI relevance with {max_core_score} core keyword match"
                }
        elif related_score >= 4:
            return {
                'level': "Tangentially Related",
                'reason': f"Related AI research with {related_score} related keyword matches"
            }
        else:
            return {
                'level': "Not Related",
                'reason': "No significant AGI/ASI relevance detected"
            }
    
    def calculate_combined_score(self, agi_score: int, asi_score: int, related_score: int) -> float:
        """
        Calculate combined relevance score (0-100 scale)
        
        Weights:
        - AGI keywords: 3.0 (most important)
        - ASI keywords: 3.0 (most important)
        - Related keywords: 1.0 (contextual)
        """
        weighted_score = (agi_score * 3.0) + (asi_score * 3.0) + (related_score * 1.0)
        
        # Normalize to 0-100 scale (assuming max reasonable score is ~30)
        normalized_score = min(weighted_score * 3.33, 100)
        
        return round(normalized_score, 2)
    
    def batch_classify(self, papers: List[Dict]) -> List[Dict]:
        """
        Classify multiple papers in batch
        
        Args:
            papers: List of paper dictionaries
            
        Returns:
            List of papers with added classification results
        """
        classified_papers = []
        
        for paper in papers:
            classification = self.classify_paper(paper)
            paper['classification_result'] = classification
            classified_papers.append(paper)
        
        return classified_papers
    
    def get_statistics(self, classified_papers: List[Dict]) -> Dict:
        """
        Get classification statistics for a batch of papers
        
        Args:
            classified_papers: List of classified papers
            
        Returns:
            Dictionary with classification statistics
        """
        total = len(classified_papers)
        
        if total == 0:
            return {
                'total': 0,
                'core_agi_asi': 0,
                'strongly_related': 0,
                'tangentially_related': 0,
                'not_related': 0
            }
        
        stats = {
            'total': total,
            'core_agi_asi': 0,
            'strongly_related': 0,
            'tangentially_related': 0,
            'not_related': 0,
            'relevance_rate': 0.0
        }
        
        for paper in classified_papers:
            level = paper['classification_result']['classification']
            if level == "Core AGI/ASI":
                stats['core_agi_asi'] += 1
            elif level == "Strongly Related":
                stats['strongly_related'] += 1
            elif level == "Tangentially Related":
                stats['tangentially_related'] += 1
            else:
                stats['not_related'] += 1
        
        # Calculate relevance rate (papers that are not "Not Related")
        relevant_count = stats['core_agi_asi'] + stats['strongly_related'] + stats['tangentially_related']
        stats['relevance_rate'] = round((relevant_count / total) * 100, 2)
        
        return stats


# Test the classifier
if __name__ == "__main__":
    classifier = AGIASIClassifier()
    
    # Test with sample papers
    test_papers = [
        {
            'title': 'Neural Computers: A New Computing Paradigm',
            'summary': 'Researchers propose Neural Computers that unify computation, memory, and I/O in a single learned runtime state, potentially leading to artificial general intelligence.',
            'full_entry': 'Neural Computers: A New Computing Paradigm - This could be a step toward AGI'
        },
        {
            'title': 'Image Classification with Deep Learning',
            'summary': 'A new approach to image classification using convolutional neural networks.',
            'full_entry': 'Image Classification with Deep Learning - Standard ML research'
        },
        {
            'title': 'AI Safety and Alignment Problem',
            'summary': 'Analysis of existential risks from superintelligent AI systems and alignment challenges.',
            'full_entry': 'AI Safety and Alignment Problem - Critical for ASI development'
        }
    ]
    
    print("Testing AGI/ASI classifier...")
    for i, paper in enumerate(test_papers, 1):
        result = classifier.classify_paper(paper)
        print(f"\nPaper {i}: {paper['title']}")
        print(f"Classification: {result['classification']}")
        print(f"AGI Score: {result['agi_score']}")
        print(f"ASI Score: {result['asi_score']}")
        print(f"Combined Score: {result['combined_score']}")
        print(f"Reason: {result['classification_reason']}")