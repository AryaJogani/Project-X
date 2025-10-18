"""
Model Router for intelligent LLM selection
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ModelRouter:
    """
    Intelligent model routing based on task characteristics
    """
    
    # Task-based model mapping
    TASK_MODEL_MAP = {
        # Complex reasoning tasks → Most capable models
        "gap_analysis_deep": {
            "primary": {
                "provider": "azure_openai",
                "model": "gpt-4-turbo-preview",
                "cost_tier": "premium"
            },
            "fallback": {
                "provider": "openai",
                "model": "gpt-4-turbo-preview",
                "cost_tier": "premium"
            }
        },
        
        # Question generation → Balance quality and cost
        "question_generation": {
            "primary": {
                "provider": "azure_openai",
                "model": "gpt-4-turbo-preview",
                "cost_tier": "balanced"
            },
            "fallback": {
                "provider": "openai",
                "model": "gpt-4-turbo-preview",
                "cost_tier": "balanced"
            }
        },
        
        # Simple classification → Fast and cheap
        "gap_classification": {
            "primary": {
                "provider": "azure_openai",
                "model": "gpt-3.5-turbo",
                "cost_tier": "economy"
            },
            "fallback": {
                "provider": "openai",
                "model": "gpt-3.5-turbo",
                "cost_tier": "economy"
            }
        },
        
        # Semantic analysis → Specialized models
        "semantic_embedding": {
            "primary": {
                "provider": "azure_openai",
                "model": "text-embedding-3-large",
                "cost_tier": "economy"
            },
            "fallback": {
                "provider": "openai",
                "model": "text-embedding-3-large",
                "cost_tier": "economy"
            }
        },
        
        # Long document processing → Large context
        "document_analysis": {
            "primary": {
                "provider": "azure_openai",
                "model": "gpt-4-turbo-preview",  # 128k context
                "cost_tier": "premium"
            },
            "fallback": {
                "provider": "anthropic",
                "model": "claude-3-opus-20240229",  # 200k context
                "cost_tier": "premium"
            }
        },
        
        # Answer processing → Balanced approach
        "answer_processing": {
            "primary": {
                "provider": "azure_openai",
                "model": "gpt-4-turbo-preview",
                "cost_tier": "balanced"
            },
            "fallback": {
                "provider": "openai",
                "model": "gpt-4-turbo-preview",
                "cost_tier": "balanced"
            }
        }
    }
    
    def select_model(
        self,
        task_type: str,
        prompt_length: int,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Select appropriate model based on task characteristics
        
        Args:
            task_type: Type of task
            prompt_length: Length of prompt
            context: Additional context
            
        Returns:
            Model configuration
        """
        
        # Get base configuration
        config = self.TASK_MODEL_MAP.get(task_type, self.TASK_MODEL_MAP["gap_classification"])
        
        # Adjust based on prompt complexity
        complexity_score = self._estimate_complexity(prompt_length, context)
        
        # Downgrade to cheaper model if task is simple
        if complexity_score < 0.3 and config["primary"]["cost_tier"] == "premium":
            # Use economy model for simple tasks
            return {
                "provider": "openai",
                "model": "gpt-3.5-turbo",
                "cost_tier": "economy"
            }
        
        # Use primary model
        return config["primary"]
    
    def get_fallback(self, model_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get fallback model configuration
        
        Args:
            model_config: Current model configuration
            
        Returns:
            Fallback model configuration
        """
        
        # Find fallback for current task type
        for task_type, config in self.TASK_MODEL_MAP.items():
            if config["primary"] == model_config:
                return config["fallback"]
        
        # Default fallback
        return {
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "cost_tier": "economy"
        }
    
    def _estimate_complexity(
        self,
        prompt_length: int,
        context: Optional[Dict] = None
    ) -> float:
        """
        Estimate task complexity (0.0 to 1.0)
        
        Args:
            prompt_length: Length of prompt
            context: Additional context
            
        Returns:
            Complexity score
        """
        
        # Base complexity from prompt length
        length_score = min(prompt_length / 2000, 1.0)  # Normalize to 0-1
        
        # Context complexity
        context_score = 0.0
        if context:
            if "document_length" in context:
                context_score += min(context["document_length"] / 10000, 0.5)
            if "gap_count" in context:
                context_score += min(context["gap_count"] / 20, 0.3)
            if "requires_reasoning" in context:
                context_score += 0.2
        
        # Combine scores
        complexity = (length_score * 0.6) + (context_score * 0.4)
        
        return min(complexity, 1.0)
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """
        Get list of available models by provider
        
        Returns:
            Dictionary of provider -> models
        """
        return {
            "azure_openai": [
                "gpt-4-turbo-preview",
                "gpt-4",
                "gpt-3.5-turbo",
                "gpt-3.5-turbo-16k",
                "text-embedding-3-large",
                "text-embedding-ada-002"
            ],
            "openai": [
                "gpt-4-turbo-preview",
                "gpt-4",
                "gpt-3.5-turbo",
                "gpt-3.5-turbo-16k",
                "text-embedding-3-large",
                "text-embedding-ada-002"
            ],
            "anthropic": [
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307"
            ],
            "google": [
                "gemini-pro",
                "gemini-pro-vision"
            ]
        }
