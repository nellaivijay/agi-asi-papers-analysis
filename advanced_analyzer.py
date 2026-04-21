"""
Advanced Analysis Module
Provides additional analysis features for AI papers across the intelligence spectrum
"""

from typing import Dict, List
from collections import Counter
import pandas as pd


class AdvancedAnalyzer:
    """Advanced analysis for AGI/ASI papers"""
    
    def __init__(self):
        pass
    
    def analyze_keyword_frequency(self, papers: List[Dict]) -> Dict:
        """
        Analyze frequency of AGI/ASI keywords across all papers
        
        Args:
            papers: List of classified papers
            
        Returns:
            Dictionary with keyword frequency statistics
        """
        agi_keywords = []
        asi_keywords = []
        related_keywords = []
        
        for paper in papers:
            if 'classification_result' in paper:
                agi_keywords.extend(paper['classification_result'].get('matched_agi_keywords', []))
                asi_keywords.extend(paper['classification_result'].get('matched_asi_keywords', []))
                related_keywords.extend(paper['classification_result'].get('matched_related_keywords', []))
        
        return {
            'agi_keyword_frequency': dict(Counter(agi_keywords).most_common(20)),
            'asi_keyword_frequency': dict(Counter(asi_keywords).most_common(20)),
            'related_keyword_frequency': dict(Counter(related_keywords).most_common(20)),
            'total_agi_keywords': len(agi_keywords),
            'total_asi_keywords': len(asi_keywords),
            'total_related_keywords': len(related_keywords)
        }
    
    def analyze_paper_length(self, papers: List[Dict]) -> Dict:
        """
        Analyze paper title and summary length statistics
        
        Args:
            papers: List of papers
            
        Returns:
            Dictionary with length statistics
        """
        title_lengths = [len(p.get('title', '')) for p in papers]
        summary_lengths = [len(p.get('summary', '')) for p in papers]
        
        return {
            'title_length': {
                'mean': sum(title_lengths) / len(title_lengths) if title_lengths else 0,
                'min': min(title_lengths) if title_lengths else 0,
                'max': max(title_lengths) if title_lengths else 0,
                'median': sorted(title_lengths)[len(title_lengths)//2] if title_lengths else 0
            },
            'summary_length': {
                'mean': sum(summary_lengths) / len(summary_lengths) if summary_lengths else 0,
                'min': min(summary_lengths) if summary_lengths else 0,
                'max': max(summary_lengths) if summary_lengths else 0,
                'median': sorted(summary_lengths)[len(summary_lengths)//2] if summary_lengths else 0
            }
        }
    
    def analyze_score_distribution(self, papers: List[Dict]) -> Dict:
        """
        Analyze distribution of different scores
        
        Args:
            papers: List of classified papers
            
        Returns:
            Dictionary with score distribution statistics
        """
        combined_scores = []
        agi_scores = []
        asi_scores = []
        final_ranks = []
        
        for paper in papers:
            if 'classification_result' in paper:
                combined_scores.append(paper['classification_result']['combined_score'])
                agi_scores.append(paper['classification_result']['agi_score'])
                asi_scores.append(paper['classification_result']['asi_score'])
            if 'final_rank' in paper:
                final_ranks.append(paper['final_rank'])
        
        def calculate_stats(scores):
            if not scores:
                return {'mean': 0, 'min': 0, 'max': 0, 'std': 0}
            return {
                'mean': sum(scores) / len(scores),
                'min': min(scores),
                'max': max(scores),
                'std': (sum((x - sum(scores)/len(scores))**2 for x in scores) / len(scores))**0.5
            }
        
        return {
            'combined_score_distribution': calculate_stats(combined_scores),
            'agi_score_distribution': calculate_stats(agi_scores),
            'asi_score_distribution': calculate_stats(asi_scores),
            'final_rank_distribution': calculate_stats(final_ranks)
        }
    
    def analyze_classification_patterns(self, papers: List[Dict]) -> Dict:
        """
        Analyze patterns in classifications
        
        Args:
            papers: List of classified papers
            
        Returns:
            Dictionary with classification patterns
        """
        classifications = []
        papers_with_both_agi_asi = 0
        papers_with_only_agi = 0
        papers_with_only_asi = 0
        papers_with_neither = 0
        
        for paper in papers:
            if 'classification_result' in paper:
                classification = paper['classification_result']['classification']
                classifications.append(classification)
                
                agi_count = len(paper['classification_result'].get('matched_agi_keywords', []))
                asi_count = len(paper['classification_result'].get('matched_asi_keywords', []))
                
                if agi_count > 0 and asi_count > 0:
                    papers_with_both_agi_asi += 1
                elif agi_count > 0:
                    papers_with_only_agi += 1
                elif asi_count > 0:
                    papers_with_only_asi += 1
                else:
                    papers_with_neither += 1
        
        return {
            'classification_counts': dict(Counter(classifications)),
            'papers_with_both_agi_asi': papers_with_both_agi_asi,
            'papers_with_only_agi': papers_with_only_agi,
            'papers_with_only_asi': papers_with_only_asi,
            'papers_with_neither': papers_with_neither
        }
    
    def generate_analysis_report(self, papers: List[Dict]) -> str:
        """
        Generate comprehensive analysis report
        
        Args:
            papers: List of classified papers
            
        Returns:
            Formatted markdown report
        """
        report = "# 🔬 Advanced Analysis Report\n\n"
        
        # Keyword frequency analysis
        keyword_freq = self.analyze_keyword_frequency(papers)
        report += "## 📊 Keyword Frequency Analysis\n\n"
        report += f"**Total AGI Keywords Found**: {keyword_freq['total_agi_keywords']}\n"
        report += f"**Total ASI Keywords Found**: {keyword_freq['total_asi_keywords']}\n"
        report += f"**Total Related Keywords Found**: {keyword_freq['total_related_keywords']}\n\n"
        
        report += "### Top AGI Keywords\n"
        for keyword, count in list(keyword_freq['agi_keyword_frequency'].items())[:10]:
            report += f"- {keyword}: {count} occurrences\n"
        report += "\n"
        
        report += "### Top ASI Keywords\n"
        for keyword, count in list(keyword_freq['asi_keyword_frequency'].items())[:10]:
            report += f"- {keyword}: {count} occurrences\n"
        report += "\n"
        
        # Score distribution
        score_dist = self.analyze_score_distribution(papers)
        report += "## 📈 Score Distribution\n\n"
        report += f"**Combined Score**: Mean={score_dist['combined_score_distribution']['mean']:.2f}, "
        report += f"Std={score_dist['combined_score_distribution']['std']:.2f}\n"
        report += f"**AGI Score**: Mean={score_dist['agi_score_distribution']['mean']:.2f}\n"
        report += f"**ASI Score**: Mean={score_dist['asi_score_distribution']['mean']:.2f}\n"
        report += f"**Final Rank**: Mean={score_dist['final_rank_distribution']['mean']:.2f}\n\n"
        
        # Classification patterns
        patterns = self.analyze_classification_patterns(papers)
        report += "## 🎯 Classification Patterns\n\n"
        report += f"**Papers with both AGI and ASI keywords**: {patterns['papers_with_both_agi_asi']}\n"
        report += f"**Papers with only AGI keywords**: {patterns['papers_with_only_agi']}\n"
        report += f"**Papers with only ASI keywords**: {patterns['papers_with_only_asi']}\n"
        report += f"**Papers with neither**: {patterns['papers_with_neither']}\n\n"
        
        # Paper length analysis
        length_analysis = self.analyze_paper_length(papers)
        report += "## 📝 Paper Length Analysis\n\n"
        report += f"**Average Title Length**: {length_analysis['title_length']['mean']:.1f} characters\n"
        report += f"**Average Summary Length**: {length_analysis['summary_length']['mean']:.1f} characters\n\n"
        
        return report


# Test the analyzer
if __name__ == "__main__":
    analyzer = AdvancedAnalyzer()
    
    # Test with sample papers
    test_papers = [
        {
            'title': 'Neural Computers: A New Computing Paradigm',
            'summary': 'Researchers propose Neural Computers that unify computation and memory, potentially leading to artificial general intelligence.',
            'classification_result': {
                'classification': 'Core AGI/ASI',
                'combined_score': 85.0,
                'agi_score': 3,
                'asi_score': 0,
                'matched_agi_keywords': ['general intelligence', 'AGI'],
                'matched_asi_keywords': [],
                'matched_related_keywords': ['deep learning']
            },
            'final_rank': 75.0
        },
        {
            'title': 'AI Safety Research',
            'summary': 'Analysis of existential risks from superintelligent AI systems.',
            'classification_result': {
                'classification': 'Strongly Related',
                'combined_score': 60.0,
                'agi_score': 0,
                'asi_score': 2,
                'matched_agi_keywords': [],
                'matched_asi_keywords': ['AI safety', 'existential risk'],
                'matched_related_keywords': ['reinforcement learning']
            },
            'final_rank': 50.0
        }
    ]
    
    print("Testing advanced analyzer...")
    report = analyzer.generate_analysis_report(test_papers)
    print(report)
