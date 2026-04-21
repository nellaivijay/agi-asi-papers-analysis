"""
Model Manager Module
Supports multiple AI models for semantic analysis of papers
"""

import os
from typing import Dict, List, Optional
import requests


class ModelManager:
    """Manage multiple AI models for semantic paper analysis"""
    
    def __init__(self):
        self.current_model = "keyword"  # Default to keyword-based
        self.model_configs = {
            "keyword": {
                "name": "Keyword-Based",
                "description": "Fast keyword matching without AI models",
                "requires_api_key": False,
                "cost": "Free",
                "speed": "Fastest",
                "accuracy": "Basic"
            },
            "openai": {
                "name": "OpenAI GPT",
                "description": "GPT-4/GPT-3.5 for semantic understanding",
                "requires_api_key": True,
                "cost": "Paid",
                "speed": "Fast",
                "accuracy": "Excellent",
                "api_key_env": "OPENAI_API_KEY",
                "models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", "gpt-4o"]
            },
            "anthropic": {
                "name": "Anthropic Claude",
                "description": "Claude for advanced semantic analysis",
                "requires_api_key": True,
                "cost": "Paid",
                "speed": "Fast",
                "accuracy": "Excellent",
                "api_key_env": "ANTHROPIC_API_KEY",
                "models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku", "claude-3.5-sonnet"]
            },
            "ollama": {
                "name": "Ollama (Local)",
                "description": "Local models via Ollama (free, requires installation)",
                "requires_api_key": False,
                "cost": "Free",
                "speed": "Medium",
                "accuracy": "Good",
                "base_url": "http://localhost:11434",
                "models": ["llama2", "llama3", "mistral", "neural-chat", "codellama", "phi3", "gemma", "qwen"]
            },
            "huggingface": {
                "name": "Hugging Face Inference",
                "description": "Hugging Face inference API for various models",
                "requires_api_key": True,
                "cost": "Free tier available",
                "speed": "Medium",
                "accuracy": "Good",
                "api_key_env": "HUGGINGFACE_API_KEY",
                "models": [
                    "meta-llama/Llama-2-7b-chat-hf",
                    "meta-llama/Llama-3-8b-chat-hf",
                    "mistralai/Mistral-7B-Instruct-v0.2",
                    "google/gemma-7b-it",
                    "microsoft/Phi-3-mini-4k-instruct",
                    "Qwen/Qwen2-7B-Instruct"
                ]
            },
            "cohere": {
                "name": "Cohere Command",
                "description": "Cohere's Command models for text analysis",
                "requires_api_key": True,
                "cost": "Paid (free tier available)",
                "speed": "Fast",
                "accuracy": "Good",
                "api_key_env": "COHERE_API_KEY",
                "models": ["command", "command-light", "command-nightly"]
            },
            "google": {
                "name": "Google Gemini",
                "description": "Google's Gemini models for semantic understanding",
                "requires_api_key": True,
                "cost": "Paid (free tier available)",
                "speed": "Fast",
                "accuracy": "Excellent",
                "api_key_env": "GOOGLE_API_KEY",
                "models": ["gemini-pro", "gemini-pro-vision", "gemini-1.5-pro"]
            },
            "together": {
                "name": "Together AI",
                "description": "Together AI's hosted open-source models",
                "requires_api_key": True,
                "cost": "Paid (free tier available)",
                "speed": "Fast",
                "accuracy": "Good",
                "api_key_env": "TOGETHER_API_KEY",
                "models": [
                    "meta-llama/Llama-2-70b-chat-hf",
                    "mistralai/Mixtral-8x7B-Instruct-v0.1",
                    "togethercomputer/RedPajama-INCITE-Chat-7B"
                ]
            },
            "replicate": {
                "name": "Replicate",
                "description": "Replicate's hosted models API",
                "requires_api_key": True,
                "cost": "Pay-per-use",
                "speed": "Variable",
                "accuracy": "Good",
                "api_key_env": "REPLICATE_API_KEY",
                "models": [
                    "meta/llama-2-70b-chat",
                    "mistralai/mixtral-8x7b-instruct-v0.1",
                    "stabilityai/stable-diffusion-xl-base-1.0"
                ]
            },
            "deepseek": {
                "name": "DeepSeek-R1",
                "description": "DeepSeek-R1 with Chain of Thought reasoning for AI intelligence classification",
                "requires_api_key": False,
                "cost": "Free (Hugging Face Inference)",
                "speed": "Medium",
                "accuracy": "Excellent",
                "reasoning": True,
                "model_id": "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
            }
        }
    
    def get_available_models(self) -> List[Dict]:
        """Get list of available models with their configurations"""
        return [
            {
                "id": model_id,
                "name": config["name"],
                "description": config["description"],
                "requires_api_key": config["requires_api_key"],
                "cost": config["cost"],
                "speed": config.get("speed", "N/A"),
                "accuracy": config.get("accuracy", "N/A"),
                "reasoning": config.get("reasoning", False)
            }
            for model_id, config in self.model_configs.items()
        ]
    
    def set_model(self, model_id: str) -> bool:
        """Set the current model for analysis"""
        if model_id in self.model_configs:
            self.current_model = model_id
            return True
        return False
    
    def get_current_model(self) -> str:
        """Get the current model ID"""
        return self.current_model
    
    def check_api_key(self, model_id: str) -> bool:
        """Check if API key is available for a model"""
        config = self.model_configs.get(model_id, {})
        if not config.get("requires_api_key", False):
            return True
        
        api_key_env = config.get("api_key_env")
        if api_key_env:
            return bool(os.getenv(api_key_env))
        return False
    
    def analyze_paper_semantic(self, paper_data: Dict, model_id: Optional[str] = None) -> Dict:
        """
        Analyze a paper using semantic understanding with the specified model
        
        Args:
            paper_data: Paper dictionary with title, summary, etc.
            model_id: Model to use (defaults to current model)
            
        Returns:
            Dictionary with semantic analysis results
        """
        model_id = model_id or self.current_model
        
        if model_id == "keyword":
            # Fall back to keyword-based analysis
            return self._keyword_analysis(paper_data)
        elif model_id == "openai":
            return self._openai_analysis(paper_data)
        elif model_id == "anthropic":
            return self._anthropic_analysis(paper_data)
        elif model_id == "ollama":
            return self._ollama_analysis(paper_data)
        elif model_id == "huggingface":
            return self._huggingface_analysis(paper_data)
        elif model_id == "cohere":
            return self._cohere_analysis(paper_data)
        elif model_id == "google":
            return self._google_analysis(paper_data)
        elif model_id == "together":
            return self._together_analysis(paper_data)
        elif model_id == "replicate":
            return self._replicate_analysis(paper_data)
        elif model_id == "deepseek":
            return self._deepseek_analysis(paper_data)
        else:
            return self._keyword_analysis(paper_data)
    
    def _keyword_analysis(self, paper_data: Dict) -> Dict:
        """Keyword-based analysis (fallback)"""
        return {
            "model_used": "keyword",
            "semantic_relevance": 0.0,
            "key_concepts": [],
            "reasoning": "Keyword-based analysis only"
        }
    
    def _openai_analysis(self, paper_data: Dict) -> Dict:
        """Analyze using OpenAI API"""
        try:
            import openai
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                return self._keyword_analysis(paper_data)
            
            client = openai.OpenAI(api_key=api_key)
            
            prompt = f"""
            Analyze this AI paper for AGI (Artificial General Intelligence) and ASI (Artificial Super Intelligence) relevance.
            
            Title: {paper_data.get('title', '')}
            Summary: {paper_data.get('summary', '')}
            
            Provide:
            1. Semantic relevance score (0-100)
            2. Key concepts related to AI intelligence spectrum
            3. Brief reasoning
            
            Format as JSON with keys: semantic_relevance, key_concepts, reasoning
            """
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            result["model_used"] = "openai"
            return result
            
        except Exception as e:
            print(f"OpenAI analysis error: {e}")
            return self._keyword_analysis(paper_data)
    
    def _anthropic_analysis(self, paper_data: Dict) -> Dict:
        """Analyze using Anthropic Claude API"""
        try:
            import anthropic
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                return self._keyword_analysis(paper_data)
            
            client = anthropic.Anthropic(api_key=api_key)
            
            prompt = f"""
            Analyze this AI paper for AGI (Artificial General Intelligence) and ASI (Artificial Super Intelligence) relevance.
            
            Title: {paper_data.get('title', '')}
            Summary: {paper_data.get('summary', '')}
            
            Provide:
            1. Semantic relevance score (0-100)
            2. Key concepts related to AI intelligence spectrum
            3. Brief reasoning
            
            Format your response as JSON with keys: semantic_relevance, key_concepts, reasoning
            """
            
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            
            import json
            result = json.loads(response.content[0].text)
            result["model_used"] = "anthropic"
            return result
            
        except Exception as e:
            print(f"Anthropic analysis error: {e}")
            return self._keyword_analysis(paper_data)
    
    def _ollama_analysis(self, paper_data: Dict) -> Dict:
        """Analyze using local Ollama model"""
        try:
            base_url = self.model_configs["ollama"]["base_url"]
            prompt = f"""
            Analyze this AI paper for AGI (Artificial General Intelligence) and ASI (Artificial Super Intelligence) relevance.
            
            Title: {paper_data.get('title', '')}
            Summary: {paper_data.get('summary', '')}
            
            Provide:
            1. Semantic relevance score (0-100)
            2. Key concepts related to AI intelligence spectrum
            3. Brief reasoning
            
            Format as JSON with keys: semantic_relevance, key_concepts, reasoning
            """
            
            response = requests.post(
                f"{base_url}/api/generate",
                json={
                    "model": "llama2",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                import json
                result = json.loads(response.json()["response"])
                result["model_used"] = "ollama"
                return result
            else:
                return self._keyword_analysis(paper_data)
                
        except Exception as e:
            print(f"Ollama analysis error: {e}")
            return self._keyword_analysis(paper_data)
    
    def _huggingface_analysis(self, paper_data: Dict) -> Dict:
        """Analyze using Hugging Face Inference API"""
        try:
            api_key = os.getenv("HUGGINGFACE_API_KEY")
            if not api_key:
                return self._keyword_analysis(paper_data)
            
            model_id = "mistralai/Mistral-7B-Instruct-v0.2"
            api_url = f"https://api-inference.huggingface.co/models/{model_id}"
            
            prompt = f"""
            Analyze this AI paper for AGI (Artificial General Intelligence) and ASI (Artificial Super Intelligence) relevance.
            
            Title: {paper_data.get('title', '')}
            Summary: {paper_data.get('summary', '')}
            
            Provide:
            1. Semantic relevance score (0-100)
            2. Key concepts related to AI intelligence spectrum
            3. Brief reasoning
            
            Format as JSON with keys: semantic_relevance, key_concepts, reasoning
            """
            
            response = requests.post(
                api_url,
                headers={"Authorization": f"Bearer {api_key}"},
                json={"inputs": prompt},
                timeout=30
            )
            
            if response.status_code == 200:
                import json
                result = json.loads(response.json()[0]["generated_text"])
                result["model_used"] = "huggingface"
                return result
            else:
                return self._keyword_analysis(paper_data)
                
        except Exception as e:
            print(f"Hugging Face analysis error: {e}")
            return self._keyword_analysis(paper_data)
    
    def _cohere_analysis(self, paper_data: Dict) -> Dict:
        """Analyze using Cohere Command API"""
        try:
            import cohere
            api_key = os.getenv("COHERE_API_KEY")
            if not api_key:
                return self._keyword_analysis(paper_data)
            
            client = cohere.Client(api_key)
            
            prompt = f"""
            Analyze this AI paper for AGI (Artificial General Intelligence) and ASI (Artificial Super Intelligence) relevance.
            
            Title: {paper_data.get('title', '')}
            Summary: {paper_data.get('summary', '')}
            
            Provide:
            1. Semantic relevance score (0-100)
            2. Key concepts related to AI intelligence spectrum
            3. Brief reasoning
            
            Format your response as JSON with keys: semantic_relevance, key_concepts, reasoning
            """
            
            response = client.chat(
                message=prompt,
                model="command"
            )
            
            import json
            result = json.loads(response.text)
            result["model_used"] = "cohere"
            return result
            
        except Exception as e:
            print(f"Cohere analysis error: {e}")
            return self._keyword_analysis(paper_data)
    
    def _google_analysis(self, paper_data: Dict) -> Dict:
        """Analyze using Google Gemini API"""
        try:
            import google.generativeai as genai
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                return self._keyword_analysis(paper_data)
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = f"""
            Analyze this AI paper for AGI (Artificial General Intelligence) and ASI (Artificial Super Intelligence) relevance.
            
            Title: {paper_data.get('title', '')}
            Summary: {paper_data.get('summary', '')}
            
            Provide:
            1. Semantic relevance score (0-100)
            2. Key concepts related to AI intelligence spectrum
            3. Brief reasoning
            
            Format your response as JSON with keys: semantic_relevance, key_concepts, reasoning
            """
            
            response = model.generate_content(prompt)
            
            import json
            result = json.loads(response.text)
            result["model_used"] = "google"
            return result
            
        except Exception as e:
            print(f"Google analysis error: {e}")
            return self._keyword_analysis(paper_data)
    
    def _together_analysis(self, paper_data: Dict) -> Dict:
        """Analyze using Together AI API"""
        try:
            api_key = os.getenv("TOGETHER_API_KEY")
            if not api_key:
                return self._keyword_analysis(paper_data)
            
            model_id = "mistralai/Mixtral-8x7B-Instruct-v0.1"
            api_url = "https://api.together.xyz/v1/chat/completions"
            
            prompt = f"""
            Analyze this AI paper for AGI (Artificial General Intelligence) and ASI (Artificial Super Intelligence) relevance.
            
            Title: {paper_data.get('title', '')}
            Summary: {paper_data.get('summary', '')}
            
            Provide:
            1. Semantic relevance score (0-100)
            2. Key concepts related to AI intelligence spectrum
            3. Brief reasoning
            
            Format as JSON with keys: semantic_relevance, key_concepts, reasoning
            """
            
            response = requests.post(
                api_url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model_id,
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=30
            )
            
            if response.status_code == 200:
                import json
                result = json.loads(response.json()["choices"][0]["message"]["content"])
                result["model_used"] = "together"
                return result
            else:
                return self._keyword_analysis(paper_data)
                
        except Exception as e:
            print(f"Together AI analysis error: {e}")
            return self._keyword_analysis(paper_data)
    
    def _replicate_analysis(self, paper_data: Dict) -> Dict:
        """Analyze using Replicate API"""
        try:
            api_key = os.getenv("REPLICATE_API_KEY")
            if not api_key:
                return self._keyword_analysis(paper_data)
            
            # Using a simple text model for analysis
            model_id = "meta/llama-2-70b-chat"
            api_url = f"https://api.replicate.com/v1/models/{model_id}/predictions"
            
            prompt = f"""
            Analyze this AI paper for AGI (Artificial General Intelligence) and ASI (Artificial Super Intelligence) relevance.
            
            Title: {paper_data.get('title', '')}
            Summary: {paper_data.get('summary', '')}
            
            Provide:
            1. Semantic relevance score (0-100)
            2. Key concepts related to AI intelligence spectrum
            3. Brief reasoning
            
            Format as JSON with keys: semantic_relevance, key_concepts, reasoning
            """
            
            response = requests.post(
                api_url,
                headers={
                    "Authorization": f"Token {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "input": {
                        "prompt": prompt
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                import json
                result = json.loads(response.json()["output"])
                result["model_used"] = "replicate"
                return result
            else:
                return self._keyword_analysis(paper_data)
                
        except Exception as e:
            print(f"Replicate analysis error: {e}")
            return self._keyword_analysis(paper_data)
    
    def _deepseek_analysis(self, paper_data: Dict) -> Dict:
        """Analyze using DeepSeek-R1 with Chain of Thought reasoning"""
        try:
            from huggingface_hub import InferenceClient
            
            model_id = self.model_configs["deepseek"]["model_id"]
            client = InferenceClient(model_id)
            
            system_instruction = (
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
            
            # Combine title and summary for analysis
            title = paper_data.get('title', '')
            summary = paper_data.get('summary', '')
            user_input = f"Analyze this abstract: {title}. {summary}"
            
            response = client.chat_completion(
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=500,
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            
            # DeepSeek-R1 sometimes includes <think> tags; we strip them for JSON parsing
            if "<think>" in content:
                content = content.split("<think>")[-1].strip()
            
            import json
            result = json.loads(content)
            result["model_used"] = "deepseek"
            return result
            
        except Exception as e:
            print(f"DeepSeek analysis error: {e}")
            return self._keyword_analysis(paper_data)
    
    def batch_analyze(self, papers: List[Dict], model_id: Optional[str] = None) -> List[Dict]:
        """
        Analyze multiple papers in batch
        
        Args:
            papers: List of paper dictionaries
            model_id: Model to use
            
        Returns:
            List of papers with added semantic analysis
        """
        analyzed_papers = []
        
        for paper in papers:
            semantic_result = self.analyze_paper_semantic(paper, model_id)
            paper['semantic_analysis'] = semantic_result
            analyzed_papers.append(paper)
        
        return analyzed_papers


# Test the model manager
if __name__ == "__main__":
    manager = ModelManager()
    
    # Test available models
    print("Available Models:")
    for model in manager.get_available_models():
        print(f"- {model['id']}: {model['name']} ({model['cost']})")
    
    # Test keyword analysis
    test_paper = {
        'title': 'Neural Computers: A New Computing Paradigm',
        'summary': 'Researchers propose Neural Computers that unify computation, memory, and I/O in a single learned runtime state, potentially leading to artificial general intelligence.'
    }
    
    print("\nTesting keyword analysis:")
    result = manager.analyze_paper_semantic(test_paper, "keyword")
    print(result)
