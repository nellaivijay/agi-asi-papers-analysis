"""
AGI/ASI Classifier Module
Classifies AI papers by AGI (Artificial General Intelligence) and ASI (Artificial Super Intelligence) relevance
"""

from typing import Dict, List
from model_manager import ModelManager


class AGIASIClassifier:
    """Classify papers by AGI/ASI relevance using keyword analysis"""
    
    def __init__(self, use_semantic: bool = False, model_id: str = "keyword"):
        # Initialize model manager for semantic analysis
        self.model_manager = ModelManager()
        self.use_semantic = use_semantic
        self.model_id = model_id
        
        if use_semantic:
            self.model_manager.set_model(model_id)
        
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
        
        # ACI (Artificial Collective Intelligence) keywords
        self.aci_keywords = [
            "multi-agent",
            "multi-agent systems",
            "swarm intelligence",
            "collective intelligence",
            "distributed AI",
            "decentralized AI",
            "agent coordination",
            "agent collaboration",
            "emergent collective behavior",
            "human-AI collaboration",
            "human-in-the-loop",
            "crowdsourcing",
            "collaborative AI",
            "swarm robotics",
            "distributed decision making",
            "consensus algorithms",
            "federated learning",
            "distributed machine learning",
            "agent-based modeling",
            "collective behavior",
            "group intelligence",
            "hive mind",
            "distributed cognition",
            "multi-agent reinforcement learning",
            "cooperative AI",
            "swarm optimization",
            "particle swarm",
            "ant colony optimization",
            "distributed problem solving"
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
        aci_score = self.calculate_keyword_score(combined_text, self.aci_keywords)
        related_score = self.calculate_keyword_score(combined_text, self.related_keywords)
        
        # Perform semantic analysis if enabled
        semantic_result = None
        if self.use_semantic:
            semantic_result = self.model_manager.analyze_paper_semantic(paper_data, self.model_id)
        
        # Determine classification
        classification = self.determine_classification(agi_score, asi_score, aci_score, related_score, semantic_result)
        
        # Calculate combined relevance score (incorporating semantic if available)
        combined_score = self.calculate_combined_score(agi_score, asi_score, aci_score, related_score, semantic_result)
        
        return {
            'classification': classification['level'],
            'classification_reason': classification['reason'],
            'agi_score': agi_score,
            'asi_score': asi_score,
            'aci_score': aci_score,
            'related_score': related_score,
            'combined_score': combined_score,
            'matched_agi_keywords': self.find_matched_keywords(combined_text, self.agi_keywords),
            'matched_asi_keywords': self.find_matched_keywords(combined_text, self.asi_keywords),
            'matched_aci_keywords': self.find_matched_keywords(combined_text, self.aci_keywords),
            'matched_related_keywords': self.find_matched_keywords(combined_text, self.related_keywords),
            'semantic_analysis': semantic_result
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
    
    def determine_classification(self, agi_score: int, asi_score: int, aci_score: int, 
                                 related_score: int, semantic_result: Dict = None) -> Dict:
        """
        Determine classification level based on scores
        
        Returns:
            Dictionary with classification level and reasoning
        """
        max_core_score = max(agi_score, asi_score)
        
        # If semantic analysis is available, use it to enhance classification
        if semantic_result and semantic_result.get("semantic_relevance", 0) > 70:
            # Use semantic category if available
            if 'category' in semantic_result:
                return {
                    'level': semantic_result['category'],
                    'reason': f"Semantic analysis classification with {semantic_result['semantic_relevance']}% confidence"
                }
            # High semantic relevance boosts classification
            if max_core_score >= 1:
                return {
                    'level': "AGI" if agi_score >= asi_score else "ASI",
                    'reason': f"High semantic relevance ({semantic_result['semantic_relevance']}) with {max_core_score} core AGI/ASI keyword matches"
                }
        
        # ACI classification (highest priority for collective intelligence)
        if aci_score >= 2:
            return {
                'level': "ACI",
                'reason': f"Strong collective intelligence focus with {aci_score} ACI keyword matches"
            }
        elif aci_score >= 1 and related_score >= 3:
            return {
                'level': "ACI",
                'reason': f"Collective intelligence potential with {aci_score} ACI and {related_score} related keyword matches"
            }
        
        # AGI classification
        if agi_score >= 3:
            return {
                'level': "AGI",
                'reason': f"Strong general intelligence focus with {agi_score} AGI keyword matches"
            }
        elif agi_score >= 2:
            return {
                'level': "AGI",
                'reason': f"Good general intelligence relevance with {agi_score} AGI keyword matches"
            }
        
        # ASI classification
        if asi_score >= 3:
            return {
                'level': "ASI",
                'reason': f"Strong superintelligence focus with {asi_score} ASI keyword matches"
            }
        elif asi_score >= 2:
            return {
                'level': "ASI",
                'reason': f"Good superintelligence relevance with {asi_score} ASI keyword matches"
            }
        
        # Mixed or lower relevance
        if max_core_score >= 1:
            if related_score >= 4:
                return {
                    'level': "Narrow AI",
                    'reason': f"Specialized AI research with {max_core_score} core and {related_score} related keyword matches"
                }
            else:
                return {
                    'level': "Narrow AI",
                    'reason': f"Some AI relevance with {max_core_score} core keyword match"
                }
        elif related_score >= 5:
            return {
                'level': "Narrow AI",
                'reason': f"Related AI research with {related_score} related keyword matches"
            }
        else:
            return {
                'level': "Not Related",
                'reason': "No significant AI relevance detected"
            }
    
    def calculate_combined_score(self, agi_score: int, asi_score: int, aci_score: int, 
                                  related_score: int, semantic_result: Dict = None) -> float:
        """
        Calculate combined relevance score (0-100 scale)
        
        Weights:
        - AGI keywords: 3.0 (most important)
        - ASI keywords: 3.0 (most important)
        - ACI keywords: 2.5 (emerging field, high potential)
        - Related keywords: 1.0 (contextual)
        - Semantic analysis: 2.0 (if available)
        """
        weighted_score = (agi_score * 3.0) + (asi_score * 3.0) + (aci_score * 2.5) + (related_score * 1.0)
        
        # Add semantic score if available
        if semantic_result and semantic_result.get("semantic_relevance"):
            semantic_score = semantic_result["semantic_relevance"]
            weighted_score += (semantic_score / 100) * 20.0  # Add up to 20 points from semantic
        
        # Normalize to 0-100 scale (assuming max reasonable score is ~60 with semantic)
        normalized_score = min(weighted_score * 1.5, 100)
        
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
                'agi': 0,
                'asi': 0,
                'aci': 0,
                'narrow_ai': 0,
                'not_related': 0,
                'relevance_rate': 0.0
            }
        
        stats = {
            'total': total,
            'agi': 0,
            'asi': 0,
            'aci': 0,
            'narrow_ai': 0,
            'not_related': 0,
            'relevance_rate': 0.0
        }
        
        for paper in classified_papers:
            level = paper['classification_result']['classification']
            if level == "AGI":
                stats['agi'] += 1
            elif level == "ASI":
                stats['asi'] += 1
            elif level == "ACI":
                stats['aci'] += 1
            elif level == "Narrow AI":
                stats['narrow_ai'] += 1
            else:
                stats['not_related'] += 1
        
        # Calculate relevance rate (papers that are not "Not Related")
        relevant_count = stats['agi'] + stats['asi'] + stats['aci'] + stats['narrow_ai']
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