
import torch
import json
import os
from typing import List, Dict
import logging
from datetime import datetime, timedelta
import threading
import time

from models.training import DieAITrainer, TextDataset
from models.transformer import DieAITransformer
from models.tokenizer import DieAITokenizer
from services.database import DatabaseManager

logger = logging.getLogger(__name__)

class LearningService:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.model_path = "models/dieai_model_best.pt"
        self.vocab_path = "models/vocab.json"
        self.learning_threshold = 50  # Minimum conversations before retraining
        self.learning_interval = 3600  # Check for learning every hour
        self.is_learning = False
        
        # Start background learning thread
        self.learning_thread = threading.Thread(target=self._learning_loop, daemon=True)
        self.learning_thread.start()
    
    def collect_conversation_data(self, user_message: str, ai_response: str, 
                                session_id: str, api_key: str = None) -> bool:
        """Collect conversation data for learning"""
        try:
            # Store conversation
            conversation_id = self.db_manager.log_conversation(
                session_id, user_message, ai_response, api_key
            )
            
            # Add to learning data with basic quality assessment
            quality_score = self._assess_quality(user_message, ai_response)
            
            if quality_score > 0.5:  # Only store decent quality conversations
                self.db_manager.add_learning_data(
                    user_message, ai_response, 'conversation', quality_score
                )
            
            return True
        except Exception as e:
            logger.error(f"Error collecting conversation data: {e}")
            return False
    
    def _assess_quality(self, user_message: str, ai_response: str) -> float:
        """Basic quality assessment for conversations"""
        score = 1.0
        
        # Penalize very short responses
        if len(ai_response.split()) < 3:
            score -= 0.3
        
        # Penalize repetitive responses
        if ai_response.lower() in ["i don't know", "sorry", "error"]:
            score -= 0.4
        
        # Reward longer, more detailed responses
        if len(ai_response.split()) > 20:
            score += 0.2
        
        # Check for proper grammar indicators
        if ai_response.endswith('.') or ai_response.endswith('!') or ai_response.endswith('?'):
            score += 0.1
        
        return max(0.0, min(2.0, score))
    
    def _learning_loop(self):
        """Background learning loop"""
        while True:
            try:
                time.sleep(self.learning_interval)
                
                if not self.is_learning:
                    learning_data = self.db_manager.get_learning_data(limit=1000)
                    
                    if len(learning_data) >= self.learning_threshold:
                        logger.info(f"Starting incremental learning with {len(learning_data)} examples")
                        self._perform_incremental_learning(learning_data)
                
            except Exception as e:
                logger.error(f"Error in learning loop: {e}")
    
    def _perform_incremental_learning(self, learning_data: List[Dict]):
        """Perform incremental learning with new data"""
        if self.is_learning:
            return
        
        self.is_learning = True
        
        try:
            # Load current model and tokenizer
            tokenizer = DieAITokenizer()
            if os.path.exists(self.vocab_path):
                tokenizer.load_vocab(self.vocab_path)
            
            model = None
            if os.path.exists(self.model_path):
                try:
                    model = DieAITransformer.load_model(self.model_path)
                except Exception as e:
                    logger.error(f"Error loading model for learning: {e}")
                    return
            
            if model is None:
                logger.warning("No model found for incremental learning")
                return
            
            # Prepare learning texts
            learning_texts = []
            for data in learning_data:
                # Format as conversation
                text = f"Human: {data['input_text']}\nAssistant: {data['target_text']}"
                learning_texts.append(text)
            
            # Update vocabulary with new words
            new_words = set()
            for text in learning_texts:
                words = text.lower().split()
                for word in words:
                    if word not in tokenizer.vocab:
                        new_words.add(word)
            
            if new_words:
                logger.info(f"Adding {len(new_words)} new words to vocabulary")
                for word in new_words:
                    tokenizer.add_word(word)
                tokenizer.save_vocab(self.vocab_path)
            
            # Incremental training with small learning rate
            trainer = DieAITrainer(model, tokenizer)
            trainer.setup_optimizer(learning_rate=1e-5)  # Very small learning rate
            
            # Train for few epochs
            trainer.train(
                train_texts=learning_texts,
                epochs=2,
                batch_size=2,
                max_length=256,
                learning_rate=1e-5,
                save_every=1,
                model_save_path=self.model_path
            )
            
            # Mark data as used
            data_ids = [data['id'] for data in learning_data]
            self.db_manager.mark_data_used_for_training(data_ids)
            
            logger.info("Incremental learning completed successfully")
            
        except Exception as e:
            logger.error(f"Error during incremental learning: {e}")
        finally:
            self.is_learning = False
    
    def process_feedback(self, conversation_id: int, user_message: str, 
                        ai_response: str, feedback_type: str, 
                        correction_text: str = None, api_key: str = None) -> bool:
        """Process user feedback for learning"""
        try:
            success = self.db_manager.store_feedback(
                conversation_id, user_message, ai_response,
                feedback_type, correction_text, api_key
            )
            
            if success and feedback_type == 'correction' and correction_text:
                # Immediate learning from corrections
                self._learn_from_correction(user_message, correction_text)
            
            return success
        except Exception as e:
            logger.error(f"Error processing feedback: {e}")
            return False
    
    def _learn_from_correction(self, user_message: str, correction: str):
        """Learn immediately from user corrections"""
        try:
            # Add high-priority learning data
            self.db_manager.add_learning_data(
                user_message, correction, 'correction', 2.0
            )
            
            # If we have enough corrections, trigger immediate learning
            corrections = self.db_manager.get_learning_data(limit=10, min_quality=1.5)
            if len(corrections) >= 5:
                threading.Thread(
                    target=self._perform_incremental_learning,
                    args=(corrections,),
                    daemon=True
                ).start()
        except Exception as e:
            logger.error(f"Error learning from correction: {e}")
    
    def get_learning_stats(self) -> Dict:
        """Get learning statistics"""
        try:
            # Get total learning data
            all_data = self.db_manager.get_learning_data(limit=10000)
            used_data = [d for d in all_data if d['used_for_training']]
            
            return {
                'total_learning_examples': len(all_data),
                'used_for_training': len(used_data),
                'pending_training': len(all_data) - len(used_data),
                'is_currently_learning': self.is_learning,
                'learning_threshold': self.learning_threshold
            }
        except Exception as e:
            logger.error(f"Error getting learning stats: {e}")
            return {}
