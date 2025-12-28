from typing import Optional, List, Dict, Any
import os
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_community.llms import Ollama
import time

class LLMManager:
    """Manages multiple LLM providers with intelligent fallback."""
    
    PROVIDERS = {
        'openai': {
            'models': ['gpt-4o-mini', 'gpt-4-turbo-preview', 'gpt-3.5-turbo'],
            'cost_per_1k': 0.0001,  # Approximate
            'rate_limit': 3,  # Free tier
            'description': 'OpenAI GPT models'
        },
        'anthropic': {
            'models': ['claude-3-haiku-20240307', 'claude-3-sonnet-20240229'],
            'cost_per_1k': 0.00025,
            'rate_limit': 50,
            'description': 'Anthropic Claude models'
        },
        'groq': {
            'models': ['llama-3.1-70b-versatile', 'mixtral-8x7b-32768'],
            'cost_per_1k': 0.0,  # Free tier
            'rate_limit': 30,
            'description': 'Groq (Fast inference)'
        },
        'ollama': {
            'models': ['llama3', 'mistral', 'phi3'],
            'cost_per_1k': 0.0,  # Local - Free
            'rate_limit': 999,
            'description': 'Local Ollama models'
        }
    }
    
    def _init_(self):
        self.active_providers = self._detect_available_providers()
        self.current_provider = None
        self.request_counts = {}
        self.last_request_time = {}
    
    def _detect_available_providers(self) -> List[str]:
        """Detect which providers are configured."""
        available = []
        
        # Check OpenAI
        if os.getenv('OPENAI_API_KEY'):
            available.append('openai')
        
        # Check Anthropic
        if os.getenv('ANTHROPIC_API_KEY'):
            available.append('anthropic')
        
        # Check Groq
        if os.getenv('GROQ_API_KEY'):
            available.append('groq')
        
        # Check Ollama (local)
        try:
            import ollama
            # Test if Ollama is running
            ollama.list()
            available.append('ollama')
        except:
            pass
        
        return available
    
    def get_llm(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_retries: int = 3
    ):
        """Get LLM instance with fallback support."""
        
        # Try specified provider first
        if provider and provider in self.active_providers:
            try:
                return self._create_llm(provider, model, temperature, max_retries)
            except Exception as e:
                print(f"⚠️ Failed to initialize {provider}: {e}")
        
        # Try all available providers
        for fallback_provider in self.active_providers:
            try:
                print(f"🔄 Trying provider: {fallback_provider}")
                return self._create_llm(fallback_provider, model, temperature, max_retries)
            except Exception as e:
                print(f"⚠️ {fallback_provider} failed: {e}")
                continue
        
        # If all fail, raise error
        raise Exception(
            "❌ All LLM providers failed. Please configure at least one:\n"
            "- OpenAI: Set OPENAI_API_KEY\n"
            "- Anthropic: Set ANTHROPIC_API_KEY\n"
            "- Groq: Set GROQ_API_KEY\n"
            "- Ollama: Install and run locally"
        )
    
    def _create_llm(
        self,
        provider: str,
        model: Optional[str],
        temperature: float,
        max_retries: int
    ):
        """Create LLM instance for specific provider."""
        
        if provider == 'openai':
            return ChatOpenAI(
                model=model or os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
                temperature=temperature,
                max_retries=max_retries,
                request_timeout=60
            )
        
        elif provider == 'anthropic':
            return ChatAnthropic(
                model=model or 'claude-3-haiku-20240307',
                temperature=temperature,
                max_retries=max_retries,
                timeout=60
            )
        
        elif provider == 'groq':
            return ChatGroq(
                model=model or 'llama-3.1-70b-versatile',
                temperature=temperature,
                max_retries=max_retries,
                timeout=60
            )
        
        elif provider == 'ollama':
            return Ollama(
                model=model or 'llama3',
                temperature=temperature
            )
        
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about available providers."""
        return {
            'active_providers': self.active_providers,
            'provider_details': {
                p: self.PROVIDERS[p] for p in self.active_providers
            }
        }

# Global instance
_llm_manager = LLMManager()

def get_llm_with_fallback(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.7
):
    """Get LLM with automatic fallback."""
    return _llm_manager.get_llm(provider, model, temperature)