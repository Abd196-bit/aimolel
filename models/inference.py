import torch
import torch.nn.functional as F
from typing import List, Dict, Optional
import json
import os
from datetime import datetime
import logging

from .transformer import DieAITransformer
from .tokenizer import DieAITokenizer
from services.search import SearchService

logger = logging.getLogger(__name__)

class InferenceEngine:
    def __init__(self, model_path: str = "models/dieai_model_best.pt", 
                 vocab_path: str = "models/vocab.json",
                 device: str = 'cuda' if torch.cuda.is_available() else 'cpu'):
        self.model_path = model_path
        self.vocab_path = vocab_path
        self.device = device
        
        self.model = None
        self.tokenizer = None
        self.search_service = SearchService()
        
        # Generation parameters
        self.max_length = 512
        self.temperature = 0.8
        self.top_k = 50
        self.top_p = 0.95
        self.repetition_penalty = 1.1
        
        # Context management
        self.conversation_history = []
        self.max_history_length = 5
    
    def load_model(self):
        """Load the trained model and tokenizer"""
        try:
            # Load tokenizer
            from models.tokenizer import DieAITokenizer
            self.tokenizer = DieAITokenizer()
            if os.path.exists(self.vocab_path):
                self.tokenizer.load_vocab(self.vocab_path)
                logger.info(f"Tokenizer loaded from {self.vocab_path}")
            else:
                logger.warning(f"Vocabulary file not found: {self.vocab_path}")
                logger.info("Using default vocabulary")
                # Use default vocabulary if file doesn't exist
                self.tokenizer = DieAITokenizer()
            
            # Load model
            if os.path.exists(self.model_path) and os.path.getsize(self.model_path) > 1000:
                try:
                    from models.transformer import DieAITransformer
                    self.model = DieAITransformer.load_model(self.model_path)
                    self.model.to(self.device)
                    self.model.eval()
                    logger.info(f"Model loaded successfully from {self.model_path}")
                except Exception as e:
                    logger.error(f"Error loading model file: {e}")
                    self.model = None
            else:
                # Model file not found or too small, use fallback
                logger.warning(f"Model file not found or invalid: {self.model_path}")
                logger.info("Model will use fallback response system")
                self.model = None
                
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.model = None
            self.tokenizer = None
    
    def generate_response(self, prompt: str, use_search: bool = False, 
                         context: Optional[str] = None) -> str:
        """Generate a response to the given prompt"""
        if self.model is None or self.tokenizer is None:
            logger.warning("Model not loaded, using fallback response generation")
            return self._generate_fallback_response(prompt, use_search, context)
        
        try:
            # Prepare input with context and search results
            full_prompt = self._prepare_prompt(prompt, use_search, context)
            
            # Generate response
            response = self._generate_text(full_prompt)
            
            # Post-process response
            response = self._post_process_response(response, prompt)
            
            # Update conversation history
            self._update_conversation_history(prompt, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"I apologize, but I encountered an error while generating a response: {str(e)}"
    
    def _prepare_prompt(self, prompt: str, use_search: bool = False, 
                       context: Optional[str] = None) -> str:
        """Prepare the full prompt with context and search results"""
        full_prompt = ""
        
        # Add context if provided
        if context:
            full_prompt += f"Context: {context}\n\n"
        
        # Add search results if requested
        if use_search:
            search_results = self.search_service.search(prompt, max_results=3)
            if search_results:
                full_prompt += "Search Results:\n"
                for i, result in enumerate(search_results, 1):
                    full_prompt += f"{i}. {result['title']}: {result['snippet']}\n"
                full_prompt += "\n"
        
        # Add conversation history
        if self.conversation_history:
            full_prompt += "Previous conversation:\n"
            for entry in self.conversation_history[-self.max_history_length:]:
                full_prompt += f"Human: {entry['prompt']}\n"
                full_prompt += f"Assistant: {entry['response']}\n"
            full_prompt += "\n"
        
        # Add current prompt
        full_prompt += f"Human: {prompt}\nAssistant:"
        
        return full_prompt
    
    def _generate_text(self, prompt: str) -> str:
        """Generate text using the model"""
        # Encode the prompt
        input_ids = self.tokenizer.encode(prompt, add_special_tokens=True)
        input_tensor = torch.tensor([input_ids]).to(self.device)
        
        # Generate with advanced sampling
        with torch.no_grad():
            generated_ids = self._advanced_generate(
                input_tensor, 
                max_length=self.max_length,
                temperature=self.temperature,
                top_k=self.top_k,
                top_p=self.top_p,
                repetition_penalty=self.repetition_penalty
            )
        
        # Decode the response
        generated_text = self.tokenizer.decode(generated_ids[0].tolist(), skip_special_tokens=True)
        
        # Extract only the assistant's response
        if "Assistant:" in generated_text:
            response = generated_text.split("Assistant:")[-1].strip()
        else:
            response = generated_text.strip()
        
        return response
    
    def _advanced_generate(self, input_ids: torch.Tensor, max_length: int = 512,
                          temperature: float = 0.8, top_k: int = 50, top_p: float = 0.95,
                          repetition_penalty: float = 1.1) -> torch.Tensor:
        """Advanced text generation with various sampling strategies"""
        self.model.eval()
        
        generated = input_ids.clone()
        past_tokens = set()
        
        with torch.no_grad():
            for _ in range(max_length - input_ids.size(1)):
                # Get logits
                logits = self.model(generated)
                next_token_logits = logits[:, -1, :] / temperature
                
                # Apply repetition penalty
                if repetition_penalty != 1.0:
                    for token_id in past_tokens:
                        if next_token_logits[0, token_id] < 0:
                            next_token_logits[0, token_id] *= repetition_penalty
                        else:
                            next_token_logits[0, token_id] /= repetition_penalty
                
                # Apply top-k filtering
                if top_k > 0:
                    values, indices = torch.topk(next_token_logits, top_k)
                    next_token_logits[next_token_logits < values[:, -1, None]] = -float('inf')
                
                # Apply top-p filtering
                if top_p < 1.0:
                    sorted_logits, sorted_indices = torch.sort(next_token_logits, descending=True)
                    cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
                    
                    sorted_indices_to_remove = cumulative_probs > top_p
                    sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
                    sorted_indices_to_remove[..., 0] = 0
                    
                    indices_to_remove = sorted_indices_to_remove.scatter(1, sorted_indices, sorted_indices_to_remove)
                    next_token_logits[indices_to_remove] = -float('inf')
                
                # Sample next token
                probs = F.softmax(next_token_logits, dim=-1)
                next_token = torch.multinomial(probs, num_samples=1)
                
                # Check for end of sequence
                if next_token.item() == self.tokenizer.special_tokens.get('<EOS>', 3):
                    break
                
                # Add to generated sequence
                generated = torch.cat([generated, next_token], dim=1)
                past_tokens.add(next_token.item())
                
                # Stop if we hit maximum length
                if generated.size(1) >= max_length:
                    break
        
        return generated
    
    def _post_process_response(self, response: str, original_prompt: str) -> str:
        """Post-process the generated response"""
        # Remove any remaining prompt artifacts
        response = response.strip()
        
        # Remove repetitive patterns
        response = self._remove_repetitive_patterns(response)
        
        # Ensure proper capitalization
        if response and response[0].islower():
            response = response[0].upper() + response[1:]
        
        # Add proper punctuation if missing
        if response and response[-1] not in '.!?':
            response += '.'
        
        return response
    
    def _remove_repetitive_patterns(self, text: str) -> str:
        """Remove repetitive patterns from generated text"""
        words = text.split()
        if len(words) <= 3:
            return text
        
        # Check for repeated phrases
        for length in range(2, min(6, len(words) // 2 + 1)):
            for i in range(len(words) - length * 2 + 1):
                phrase = words[i:i + length]
                next_phrase = words[i + length:i + length * 2]
                
                if phrase == next_phrase:
                    # Remove the repetition
                    words = words[:i + length] + words[i + length * 2:]
                    break
        
        return ' '.join(words)
    
    def _update_conversation_history(self, prompt: str, response: str):
        """Update conversation history"""
        self.conversation_history.append({
            'prompt': prompt,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only recent history
        if len(self.conversation_history) > self.max_history_length:
            self.conversation_history = self.conversation_history[-self.max_history_length:]
    
    def clear_conversation_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def set_generation_parameters(self, max_length: int = None, temperature: float = None,
                                 top_k: int = None, top_p: float = None,
                                 repetition_penalty: float = None):
        """Set generation parameters"""
        if max_length is not None:
            self.max_length = max_length
        if temperature is not None:
            self.temperature = temperature
        if top_k is not None:
            self.top_k = top_k
        if top_p is not None:
            self.top_p = top_p
        if repetition_penalty is not None:
            self.repetition_penalty = repetition_penalty
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model"""
        if self.model is None:
            return {"error": "Model not loaded"}
        
        return {
            "model_name": "DieAI Transformer",
            "version": "1.0",
            "vocab_size": self.tokenizer.get_vocab_size() if self.tokenizer else 0,
            "parameters": sum(p.numel() for p in self.model.parameters()),
            "device": self.device,
            "generation_params": {
                "max_length": self.max_length,
                "temperature": self.temperature,
                "top_k": self.top_k,
                "top_p": self.top_p,
                "repetition_penalty": self.repetition_penalty
            }
        }
    
    def batch_generate(self, prompts: List[str], use_search: bool = False) -> List[str]:
        """Generate responses for multiple prompts"""
        responses = []
        
        for prompt in prompts:
            try:
                response = self.generate_response(prompt, use_search=use_search)
                responses.append(response)
            except Exception as e:
                logger.error(f"Error generating response for prompt '{prompt}': {e}")
                responses.append(f"Error: {str(e)}")
        
        return responses
    
    def _generate_fallback_response(self, prompt: str, use_search: bool = False, 
                                   context: Optional[str] = None) -> str:
        """Generate a fallback response when model is not loaded"""
        import random
        
        # Simple rule-based responses for common patterns
        prompt_lower = prompt.lower()
        
        if any(greeting in prompt_lower for greeting in ['hello', 'hi', 'hey']):
            return "Hello! I'm DieAI, your AI assistant. How can I help you today?"
        
        if any(word in prompt_lower for word in ['help', 'assist', 'support']):
            return "I'm here to help! I can answer questions, provide information, and assist with various tasks. What would you like to know?"
        
        if any(word in prompt_lower for word in ['what', 'how', 'why', 'when', 'where']):
            responses = [
                "That's an interesting question! I'd be happy to help you explore that topic.",
                "I understand you're looking for information about that. Let me help you.",
                "That's a great question! I'll do my best to provide you with helpful information.",
                "I can help you with that! Let me share what I know."
            ]
            return random.choice(responses)
        
        if any(word in prompt_lower for word in ['transformer', 'ai', 'model', 'neural', 'machine learning']):
            return "I'm a custom transformer-based AI model called DieAI. I use advanced neural networks to understand and generate human-like text responses. Is there something specific about AI or transformers you'd like to know?"
        
        if any(word in prompt_lower for word in ['search', 'find', 'look up']):
            return "I can help you search for information! My search capabilities allow me to find relevant information on the web. What would you like me to search for?"
        
        if any(word in prompt_lower for word in ['api', 'key', 'endpoint']):
            return "I provide API access for developers! You can generate API keys from your dashboard and use them to integrate my capabilities into your applications. Would you like to know more about the API features?"
        
        if any(word in prompt_lower for word in ['thank', 'thanks']):
            return "You're welcome! I'm glad I could help. Feel free to ask me anything else!"
        
        if any(word in prompt_lower for word in ['goodbye', 'bye', 'see you']):
            return "Goodbye! Thank you for using DieAI. Have a great day!"
        
        # Default responses for other prompts
        default_responses = [
            "I understand you're asking about that. While my full model is still being trained, I can still help you with many questions and tasks.",
            "That's an interesting topic! I'm continuously learning and improving my responses. What specific aspect would you like to explore?",
            "I appreciate your question! My knowledge spans many topics, and I'm here to help you find the information you need.",
            "Thank you for your question! I'm designed to be helpful and informative. Is there a particular way I can assist you better?",
            "I'm here to help! While I'm still developing my full capabilities, I can provide useful information and assistance on many topics."
        ]
        
        return random.choice(default_responses)
