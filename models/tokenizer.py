import json
import re
from typing import List, Dict, Tuple
import os
from collections import Counter

class DieAITokenizer:
    def __init__(self, vocab_size: int = 32000):
        self.vocab_size = vocab_size
        self.vocab = {}
        self.inverse_vocab = {}
        self.special_tokens = {
            '<PAD>': 0,
            '<UNK>': 1,
            '<BOS>': 2,
            '<EOS>': 3,
            '<MASK>': 4
        }
        self.word_freq = Counter()
        
        # Initialize with special tokens
        for token, idx in self.special_tokens.items():
            self.vocab[token] = idx
            self.inverse_vocab[idx] = token
    
    def preprocess_text(self, text: str) -> str:
        """Basic text preprocessing"""
        # Convert to lowercase
        text = text.lower()
        
        # Add spaces around punctuation
        text = re.sub(r'([.,!?;:])', r' \1 ', text)
        
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Strip whitespace
        text = text.strip()
        
        return text
    
    def build_vocab_from_corpus(self, corpus: List[str]):
        """Build vocabulary from a corpus of text"""
        print("Building vocabulary from corpus...")
        
        # Collect all words and their frequencies
        for text in corpus:
            processed_text = self.preprocess_text(text)
            words = processed_text.split()
            self.word_freq.update(words)
        
        # Get most frequent words
        most_common = self.word_freq.most_common(self.vocab_size - len(self.special_tokens))
        
        # Add words to vocabulary
        next_id = len(self.special_tokens)
        for word, freq in most_common:
            if word not in self.vocab:
                self.vocab[word] = next_id
                self.inverse_vocab[next_id] = word
                next_id += 1
        
        print(f"Vocabulary built with {len(self.vocab)} tokens")
    
    def encode(self, text: str, add_special_tokens: bool = True) -> List[int]:
        """Encode text to token IDs"""
        processed_text = self.preprocess_text(text)
        words = processed_text.split()
        
        token_ids = []
        
        if add_special_tokens:
            token_ids.append(self.special_tokens['<BOS>'])
        
        for word in words:
            if word in self.vocab:
                token_ids.append(self.vocab[word])
            else:
                # Handle unknown words with subword splitting
                token_ids.extend(self._handle_unknown_word(word))
        
        if add_special_tokens:
            token_ids.append(self.special_tokens['<EOS>'])
        
        return token_ids
    
    def _handle_unknown_word(self, word: str) -> List[int]:
        """Handle unknown words by attempting subword splitting"""
        # Try to split into known subwords
        result = []
        i = 0
        while i < len(word):
            found = False
            # Try longest possible subword first
            for j in range(len(word), i, -1):
                subword = word[i:j]
                if subword in self.vocab:
                    result.append(self.vocab[subword])
                    i = j
                    found = True
                    break
            
            if not found:
                # If no subword found, add UNK token and move to next character
                result.append(self.special_tokens['<UNK>'])
                i += 1
        
        return result
    
    def decode(self, token_ids: List[int], skip_special_tokens: bool = True) -> str:
        """Decode token IDs to text"""
        tokens = []
        
        for token_id in token_ids:
            if token_id in self.inverse_vocab:
                token = self.inverse_vocab[token_id]
                
                # Skip special tokens if requested
                if skip_special_tokens and token in self.special_tokens:
                    continue
                
                tokens.append(token)
        
        # Join tokens with spaces
        text = ' '.join(tokens)
        
        # Clean up punctuation spacing
        text = re.sub(r' ([.,!?;:])', r'\1', text)
        
        return text
    
    def encode_batch(self, texts: List[str], max_length: int = None, 
                    pad_to_max_length: bool = True) -> List[List[int]]:
        """Encode a batch of texts"""
        encoded_texts = []
        
        for text in texts:
            encoded = self.encode(text)
            
            if max_length:
                if len(encoded) > max_length:
                    encoded = encoded[:max_length]
                elif pad_to_max_length:
                    encoded.extend([self.special_tokens['<PAD>']] * (max_length - len(encoded)))
            
            encoded_texts.append(encoded)
        
        return encoded_texts
    
    def save_vocab(self, path: str):
        """Save vocabulary to file"""
        vocab_data = {
            'vocab': self.vocab,
            'vocab_size': self.vocab_size,
            'special_tokens': self.special_tokens,
            'word_freq': dict(self.word_freq)
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(vocab_data, f, ensure_ascii=False, indent=2)
        
        print(f"Vocabulary saved to {path}")
    
    def load_vocab(self, path: str):
        """Load vocabulary from file"""
        with open(path, 'r', encoding='utf-8') as f:
            vocab_data = json.load(f)
        
        self.vocab = vocab_data['vocab']
        self.vocab_size = vocab_data['vocab_size']
        self.special_tokens = vocab_data['special_tokens']
        self.word_freq = Counter(vocab_data['word_freq'])
        
        # Rebuild inverse vocabulary
        self.inverse_vocab = {v: k for k, v in self.vocab.items()}
        
        print(f"Vocabulary loaded from {path}")
    
    def get_vocab_size(self) -> int:
        """Get vocabulary size"""
        return len(self.vocab)
    
    def token_to_id(self, token: str) -> int:
        """Convert token to ID"""
        return self.vocab.get(token, self.special_tokens['<UNK>'])
    
    def id_to_token(self, token_id: int) -> str:
        """Convert ID to token"""
        return self.inverse_vocab.get(token_id, '<UNK>')
    
    def create_attention_mask(self, token_ids: List[int]) -> List[int]:
        """Create attention mask for token IDs"""
        return [1 if token_id != self.special_tokens['<PAD>'] else 0 for token_id in token_ids]

# Example usage and testing
if __name__ == "__main__":
    # Sample corpus for testing
    sample_corpus = [
        "Hello world, this is a test sentence.",
        "The quick brown fox jumps over the lazy dog.",
        "Natural language processing is fascinating.",
        "Machine learning models require large datasets.",
        "Transformers have revolutionized NLP tasks."
    ]
    
    # Create tokenizer
    tokenizer = DieAITokenizer(vocab_size=1000)
    
    # Build vocabulary
    tokenizer.build_vocab_from_corpus(sample_corpus)
    
    # Test encoding and decoding
    test_text = "Hello world, this is a test!"
    encoded = tokenizer.encode(test_text)
    decoded = tokenizer.decode(encoded)
    
    print(f"Original: {test_text}")
    print(f"Encoded: {encoded}")
    print(f"Decoded: {decoded}")
    
    # Save vocabulary
    tokenizer.save_vocab("vocab.json")
