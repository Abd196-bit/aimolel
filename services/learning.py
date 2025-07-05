import torch
import json
import os
from typing import List, Dict
import logging
from datetime import datetime, timedelta
import threading
import time
import requests
from bs4 import BeautifulSoup
import re
import hashlib

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

        # Web learning configurations
        self.web_learning_enabled = True
        self.learning_topics = [
            "artificial intelligence",
            "machine learning",
            "natural language processing",
            "computer vision"
        ]
        self.web_learning_interval = 7200  # Every 2 hours
        self.max_web_pages_per_session = 10
        self.web_content_cache = {}  # Cache extracted web content

        # Search service (replace with actual implementation)
        class DummySearchService:
            def search(self, query, max_results=5):
                # Placeholder for search results
                results = []
                for i in range(max_results):
                    results.append({
                        'title': f"Result {i+1} for '{query}'",
                        'url': f"http://example.com/{query.replace(' ', '_')}_{i+1}"
                    })
                return results
        self.search_service = DummySearchService()

        # Start background learning threads
        self.learning_thread = threading.Thread(target=self._learning_loop, daemon=True)
        self.learning_thread.start()
        self.web_learning_thread = threading.Thread(target=self._web_learning_loop, daemon=True)
        self.web_learning_thread.start()

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

    def _web_learning_loop(self):
        """Background web learning loop"""
        while True:
            try:
                time.sleep(self.web_learning_interval)

                if not self.is_learning and self.web_learning_enabled:
                    logger.info("Starting web learning session")
                    self._learn_from_web()

            except Exception as e:
                logger.error(f"Error in web learning loop: {e}")

    def _learn_from_web(self):
        """Learn from web content by searching and scraping"""
        try:
            import random

            # Select random topics for this learning session
            selected_topics = random.sample(self.learning_topics, 
                                          min(3, len(self.learning_topics)))

            web_content = []

            for topic in selected_topics:
                try:
                    # Search for content on this topic
                    search_results = self.search_service.search(topic, max_results=5)

                    for result in search_results:
                        if len(web_content) >= self.max_web_pages_per_session:
                            break

                        # Extract content from web page
                        content = self._extract_web_content(result['url'])
                        if content and len(content) > 200:  # Only use substantial content
                            web_content.append({
                                'content': content,
                                'source': result['url'],
                                'topic': topic,
                                'title': result['title']
                            })

                    if len(web_content) >= self.max_web_pages_per_session:
                        break

                except Exception as e:
                    logger.error(f"Error learning from topic '{topic}': {e}")

            # Process web content for learning
            if web_content:
                self._process_web_content_for_learning(web_content)
                logger.info(f"Learned from {len(web_content)} web pages")

        except Exception as e:
            logger.error(f"Error in web learning: {e}")

    def _extract_web_content(self, url: str) -> str:
        """Extract clean text content from a web page"""
        try:
            # Check cache first
            url_hash = hashlib.md5(url.encode()).hexdigest()
            if url_hash in self.web_content_cache:
                cached_content = self.web_content_cache[url_hash]
                # Check if cache is still valid (24 hours)
                if time.time() - cached_content['timestamp'] < 86400:
                    return cached_content['content']

            # Set headers to appear as a real browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }

            # Fetch the page with timeout
            response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
            response.raise_for_status()

            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 
                               'aside', 'iframe', 'noscript', 'form']):
                element.decompose()

            # Extract main content
            content_selectors = [
                'article', 'main', '.content', '#content', '.post', '.article',
                '.entry', '.story', '.text', 'p'
            ]

            content_text = ""
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    for element in elements:
                        text = element.get_text(strip=True)
                        if len(text) > 50:  # Only substantial text blocks
                            content_text += text + "\n\n"
                    break

            # Fallback: get all paragraph text
            if not content_text:
                paragraphs = soup.find_all('p')
                content_text = "\n\n".join([p.get_text(strip=True) for p in paragraphs 
                                          if len(p.get_text(strip=True)) > 30])

            # Clean up the text
            content_text = self._clean_web_text(content_text)

            # Cache the content
            if content_text and len(content_text) > 100:
                self.web_content_cache[url_hash] = {
                    'content': content_text,
                    'timestamp': time.time()
                }

            return content_text

        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return ""

    def _clean_web_text(self, text: str) -> str:
        """Clean and normalize web text"""
        if not text:
            return ""

        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove common web artifacts
        text = re.sub(r'(Subscribe|Newsletter|Cookie Policy|Privacy Policy|Terms of Service)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'(Click here|Read more|Continue reading)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\[.*?\]', '', text)  # Remove square bracket content
        text = re.sub(r'Advertisement', '', text, flags=re.IGNORECASE)

        # Fix common encoding issues
        text = text.replace("'", "'").replace(""", '"').replace(""", '"')
        text = text.replace('–', '-').replace('—', '-')

        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)

        # Limit length and clean up
        text = text.strip()
        if len(text) > 5000:  # Limit content length
            sentences = text.split('.')
            text = '.'.join(sentences[:50]) + '.'  # Keep first 50 sentences

        return text

    def _process_web_content_for_learning(self, web_content: List[Dict]):
        """Process web content and add to learning database"""
        try:
            for content_item in web_content:
                content = content_item['content']
                source = content_item['source']
                topic = content_item['topic']
                title = content_item['title']

                # Split content into learning chunks
                chunks = self._split_content_into_chunks(content)

                for chunk in chunks:
                    if len(chunk.split()) > 10:  # Only meaningful chunks
                        # Create learning examples from web content
                        learning_examples = self._create_learning_examples_from_text(chunk, topic, title)

                        for example in learning_examples:
                            # Add to learning database with web source
                            quality_score = self._assess_web_content_quality(example['input'], example['output'])

                            if quality_score > 0.6:  # Higher threshold for web content
                                self.db_manager.add_learning_data(
                                    example['input'], 
                                    example['output'], 
                                    'web_content', 
                                    quality_score,
                                    source_url=source
                                )

        except Exception as e:
            logger.error(f"Error processing web content for learning: {e}")

    def _split_content_into_chunks(self, content: str, max_chunk_size: int = 500) -> List[str]:
        """Split content into manageable chunks"""
        sentences = content.split('.')
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            if len(current_chunk + sentence) < max_chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def _create_learning_examples_from_text(self, text: str, topic: str, title: str) -> List[Dict]:
        """Create question-answer learning examples from text content"""
        examples = []

        # Extract key information and create Q&A pairs
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]

        for i, sentence in enumerate(sentences):
            # Create different types of learning examples

            # 1. Direct information questions
            if any(keyword in sentence.lower() for keyword in ['is', 'are', 'was', 'were', 'has', 'have']):
                # Create a "What is..." question
                words = sentence.split()
                if len(words) > 5:
                    subject = ' '.join(words[:3])
                    examples.append({
                        'input': f"What can you tell me about {subject.lower()}?",
                        'output': sentence
                    })

            # 2. Topic-based questions
            examples.append({
                'input': f"Tell me about {topic}",
                'output': sentence
            })

            # 3. How-to questions from procedural content
            if any(keyword in sentence.lower() for keyword in ['how to', 'steps', 'process', 'method']):
                examples.append({
                    'input': f"How do I {topic.replace('artificial intelligence', 'use AI').replace('machine learning', 'implement ML')}?",
                    'output': sentence
                })

            # 4. Definition questions
            if any(keyword in sentence.lower() for keyword in ['define', 'definition', 'means', 'refers to']):
                examples.append({
                    'input': f"Can you explain {topic}?",
                    'output': sentence
                })

        # Limit examples per text to avoid overfit
        return examples[:5]

    def _assess_web_content_quality(self, input_text: str, output_text: str) -> float:
        """Assess quality of web-derived learning content"""
        score = 1.0

        # Basic quality checks
        if len(output_text.split()) < 5:
            score -= 0.4

        # Check for educational/informative content
        if any(word in output_text.lower() for word in ['learn', 'understand', 'explain', 'example', 'important']):
            score += 0.2

        # Penalize commercial content
        if any(word in output_text.lower() for word in ['buy', 'purchase', 'sale', 'discount', 'price']):
            score -= 0.3

        # Reward well-structured content
        if output_text.count('.') > 0 and len(output_text) > 100:
            score += 0.1

        # Check for factual content indicators
        if any(word in output_text.lower() for word in ['research', 'study', 'data', 'evidence', 'according to']):
            score += 0.2

        return max(0.0, min(2.0, score))

    def add_learning_topic(self, topic: str):
        """Add a new topic for web learning"""
        if topic not in self.learning_topics:
            self.learning_topics.append(topic)
            logger.info(f"Added new learning topic: {topic}")

    def remove_learning_topic(self, topic: str):
        """Remove a topic from web learning"""
        if topic in self.learning_topics:
            self.learning_topics.remove(topic)
            logger.info(f"Removed learning topic: {topic}")

    def get_web_learning_stats(self) -> Dict:
        """Get web learning statistics"""
        try:
            # Get web learning data from database
            web_data = self.db_manager.get_learning_data(source_type='web_content', limit=10000)

            return {
                'web_learning_enabled': self.web_learning_enabled,
                'learning_topics': self.learning_topics,
                'web_content_learned': len(web_data),
                'cache_size': len(self.web_content_cache),
                'learning_interval_hours': self.web_learning_interval / 3600,
                'max_pages_per_session': self.max_web_pages_per_session
            }
        except Exception as e:
            logger.error(f"Error getting web learning stats: {e}")
            return {}