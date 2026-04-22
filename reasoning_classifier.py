"""
Reasoning Classifier Module
Uses DeepSeek-R1 with Chain of Thought for AI intelligence classification
"""

import json
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from functools import lru_cache
import hashlib


class ReasoningClassifier:
    """Reasoning-based classifier using DeepSeek-R1 with Chain of Thought"""
    
    def __init__(self, cache_ttl: int = 86400):  # 24 hour cache
        self.cache_ttl = cache_ttl
        self.cache = {}
        self.system_instruction = (
            "You are an AI Research Scientist specializing in AGI, ASI, and ACI taxonomies. "
            "Your task is to analyze research paper abstracts and categorize them.\n\n"
            "CRITERIA:\n"
            "- AGI (Artificial General Intelligence): Focus on cross-domain reasoning, System 2 thinking, and 'generality.'\n"
            "- ASI (Artificial Superintelligence): Focus on recursive self-improvement, alignment at scale, and superhuman capabilities.\n"
            "- ACI (Artificial Collective Intelligence): Focus on multi-agent systems, swarm intelligence, and human-AI collaboration.\n"
            "- Narrow AI: Focus on specific, single-domain optimizations (e.g., just 'faster vision' or 'better LLM weights').\n\n"
            "OUTPUT FORMAT (JSON):\n"
            "{\n"
            '  "category": "AGI | ASI | ACI | Narrow AI",\n'
            '  "confidence_score": 0-100,\n'
            '  "analysis": "A brief technical justification of why this fits the category based on architectural depth.",\n'
            '  "aci_potential": "High/Low"\n'
            "}\n"
        )
    
    def _get_cache_key(self, title: str, summary: str) -> str:
        """Generate cache key from paper content"""
        content = f"{title}:{summary}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Get classification result from cache if available and not expired"""
        if cache_key in self.cache:
            result, timestamp = self.cache[cache_key]
            if (datetime.now() - timestamp).seconds < self.cache_ttl:
                return result
        return None
    
    def _set_cache(self, cache_key: str, result: Dict):
        """Store classification result in cache"""
        self.cache[cache_key] = (result, datetime.now())
    
    def classify_paper(self, paper_data: Dict, use_cache: bool = True) -> Dict:
        """
        Classify a paper using reasoning-based approach
        
        Args:
            paper_data: Dictionary containing paper information (title, summary, etc.)
            use_cache: Whether to use cached results if available
            
        Returns:
            Dictionary with classification results
        """
        title = paper_data.get('title', '')
        summary = paper_data.get('summary', '')
        
        # Check cache first
        cache_key = self._get_cache_key(title, summary)
        if use_cache:
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                cached_result['cached'] = True
                return cached_result
        
        # Perform reasoning classification
        result = self._classify_with_reasoning(title, summary)
        
        # Cache the result
        if use_cache:
            self._set_cache(cache_key, result)
        
        result['cached'] = False
        return result
    
    def _classify_with_reasoning(self, title: str, summary: str) -> Dict:
        """
        Perform actual reasoning classification using DeepSeek-R1
        
        Args:
            title: Paper title
            summary: Paper summary
            
        Returns:
            Classification result dictionary
        """
        try:
            from huggingface_hub import InferenceClient
            import os
            
            # Get API key from environment variable
            api_key = os.getenv("HUGGINGFACE_API_KEY")
            
            # Debug: Check if API key is available
            print(f"DEBUG: HUGGINGFACE_API_KEY found: {bool(api_key)}")
            if not api_key:
                print("DEBUG: HUGGINGFACE_API_KEY not set - will try without authentication (may fail)")
            
            # Initialize client with API key if available
            if api_key:
                client = InferenceClient("deepseek-ai/DeepSeek-R1-Distill-Qwen-7B", token=api_key)
            else:
                client = InferenceClient("deepseek-ai/DeepSeek-R1-Distill-Qwen-7B")
            
            user_input = f"Analyze this abstract: {title}. {summary}"
            
            response = client.chat_completion(
                messages=[
                    {"role": "system", "content": self.system_instruction},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=500,
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            
            # Strip CoT tags if present
            cot_tags = ["", ""]
            for tag in cot_tags:
                if tag in content:
                    content = content.split(tag)[-1].strip()
            
            # Parse JSON response
            result = json.loads(content)
            
            # Add metadata
            result['model_used'] = 'deepseek-r1'
            result['classification_timestamp'] = datetime.now().isoformat()
            
            return result
            
        except json.JSONDecodeError as e:
            # JSON parsing failed, return error result
            return {
                'category': 'Error',
                'confidence_score': 0,
                'analysis': f'JSON parsing error: {str(e)}',
                'aci_potential': 'Unknown',
                'model_used': 'deepseek-r1',
                'classification_timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
        except Exception as e:
            # API call failed, return error result
            error_msg = str(e)
            if "api_key" in error_msg.lower() or "api key" in error_msg.lower():
                error_msg = "HUGGINGFACE_API_KEY not configured or invalid. Please configure it in Space Settings or use keyword mode instead."
            return {
                'category': 'Error',
                'confidence_score': 0,
                'analysis': f'API error: {error_msg}',
                'aci_potential': 'Unknown',
                'model_used': 'deepseek-r1',
                'classification_timestamp': datetime.now().isoformat(),
                'error': error_msg
            }
    
    async def classify_paper_async(self, paper_data: Dict, use_cache: bool = True) -> Dict:
        """
        Async version of classify_paper for batch processing
        
        Args:
            paper_data: Dictionary containing paper information
            use_cache: Whether to use cached results if available
            
        Returns:
            Classification result dictionary
        """
        # For now, use synchronous version with asyncio wrapper
        # In future, can implement true async with aiohttp
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.classify_paper, paper_data, use_cache)
    
    async def batch_classify_async(self, papers: List[Dict], use_cache: bool = True, 
                                   max_concurrent: int = 5) -> List[Dict]:
        """
        Classify multiple papers asynchronously with concurrency control
        
        Args:
            papers: List of paper dictionaries
            use_cache: Whether to use cached results
            max_concurrent: Maximum number of concurrent API calls
            
        Returns:
            List of classification results
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def classify_with_semaphore(paper):
            async with semaphore:
                return await self.classify_paper_async(paper, use_cache)
        
        tasks = [classify_with_semaphore(paper) for paper in papers]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'category': 'Error',
                    'confidence_score': 0,
                    'analysis': f'Batch processing error: {str(result)}',
                    'aci_potential': 'Unknown',
                    'model_used': 'deepseek-r1',
                    'classification_timestamp': datetime.now().isoformat(),
                    'error': str(result)
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    def batch_classify(self, papers: List[Dict], use_cache: bool = True) -> List[Dict]:
        """
        Synchronous batch classification
        
        Args:
            papers: List of paper dictionaries
            use_cache: Whether to use cached results
            
        Returns:
            List of classification results
        """
        results = []
        for paper in papers:
            result = self.classify_paper(paper, use_cache)
            results.append(result)
        return results
    
    def clear_cache(self):
        """Clear the classification cache"""
        self.cache.clear()
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        total_entries = len(self.cache)
        valid_entries = 0
        expired_entries = 0
        
        for cache_key, (result, timestamp) in self.cache.items():
            if (datetime.now() - timestamp).seconds < self.cache_ttl:
                valid_entries += 1
            else:
                expired_entries += 1
        
        return {
            'total_entries': total_entries,
            'valid_entries': valid_entries,
            'expired_entries': expired_entries,
            'cache_ttl_hours': self.cache_ttl / 3600
        }
    
    def get_supported_categories(self) -> List[str]:
        """Get list of supported classification categories"""
        return ['AGI', 'ASI', 'ACI', 'Narrow AI', 'Not Related', 'Error']


# Test the reasoning classifier
if __name__ == "__main__":
    classifier = ReasoningClassifier()
    
    # Test with sample papers
    test_papers = [
        {
            'title': 'Neural Computers: A New Computing Paradigm',
            'summary': 'Researchers propose Neural Computers that unify computation, memory, and I/O in a single learned runtime state, potentially leading to artificial general intelligence.'
        },
        {
            'title': 'Multi-Agent Reinforcement Learning for Swarm Coordination',
            'summary': 'A novel approach to coordinating large swarms of autonomous agents using decentralized reinforcement learning and emergent collective intelligence.'
        },
        {
            'title': 'Image Classification with Deep Learning',
            'summary': 'A new approach to image classification using convolutional neural networks.'
        }
    ]
    
    print("Testing Reasoning Classifier...")
    for i, paper in enumerate(test_papers, 1):
        print(f"\nPaper {i}: {paper['title']}")
        result = classifier.classify_paper(paper)
        print(f"Category: {result['category']}")
        print(f"Confidence: {result['confidence_score']}")
        print(f"Analysis: {result['analysis']}")
        print(f"ACI Potential: {result['aci_potential']}")
        print(f"Cached: {result['cached']}")