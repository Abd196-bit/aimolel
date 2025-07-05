import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import json
import os
from typing import List, Dict, Tuple
import numpy as np
from tqdm import tqdm
import logging
from datetime import datetime

from .transformer import DieAITransformer
from .tokenizer import DieAITokenizer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextDataset(Dataset):
    def __init__(self, texts: List[str], tokenizer: DieAITokenizer, 
                 max_length: int = 512, stride: int = 256):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.stride = stride
        self.examples = []
        
        # Process texts into training examples
        for text in texts:
            tokens = tokenizer.encode(text, add_special_tokens=True)
            
            # Create sliding window examples
            for i in range(0, len(tokens) - max_length + 1, stride):
                example = tokens[i:i + max_length]
                if len(example) == max_length:
                    self.examples.append(example)
    
    def __len__(self):
        return len(self.examples)
    
    def __getitem__(self, idx):
        tokens = self.examples[idx]
        
        # Input is all tokens except the last one
        input_ids = torch.tensor(tokens[:-1], dtype=torch.long)
        
        # Target is all tokens except the first one (shifted by 1)
        target_ids = torch.tensor(tokens[1:], dtype=torch.long)
        
        return input_ids, target_ids

class DieAITrainer:
    def __init__(self, model: DieAITransformer, tokenizer: DieAITokenizer,
                 device: str = 'cuda' if torch.cuda.is_available() else 'cpu'):
        self.model = model
        self.tokenizer = tokenizer
        self.device = device
        self.model.to(device)
        
        # Training components
        self.optimizer = None
        self.scheduler = None
        self.loss_fn = nn.CrossEntropyLoss(ignore_index=tokenizer.special_tokens['<PAD>'])
        
        # Training history
        self.train_losses = []
        self.val_losses = []
        self.learning_rates = []
        
    def setup_optimizer(self, learning_rate: float = 1e-4, weight_decay: float = 0.01):
        """Setup optimizer and scheduler"""
        self.optimizer = optim.AdamW(self.model.parameters(), 
                                   lr=learning_rate, 
                                   weight_decay=weight_decay)
        
        # Learning rate scheduler
        self.scheduler = optim.lr_scheduler.CosineAnnealingLR(
            self.optimizer, T_max=1000, eta_min=1e-6)
    
    def train_epoch(self, train_loader: DataLoader, epoch: int) -> float:
        """Train for one epoch"""
        self.model.train()
        total_loss = 0
        num_batches = len(train_loader)
        
        progress_bar = tqdm(train_loader, desc=f'Epoch {epoch}')
        
        for batch_idx, (input_ids, target_ids) in enumerate(progress_bar):
            input_ids = input_ids.to(self.device)
            target_ids = target_ids.to(self.device)
            
            # Forward pass
            self.optimizer.zero_grad()
            
            logits = self.model(input_ids)
            
            # Calculate loss
            loss = self.loss_fn(logits.view(-1, logits.size(-1)), target_ids.view(-1))
            
            # Backward pass
            loss.backward()
            
            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            
            # Update parameters
            self.optimizer.step()
            
            # Update learning rate
            if self.scheduler:
                self.scheduler.step()
            
            # Track loss
            total_loss += loss.item()
            
            # Update progress bar
            progress_bar.set_postfix({
                'loss': loss.item(),
                'lr': self.optimizer.param_groups[0]['lr']
            })
        
        avg_loss = total_loss / num_batches
        return avg_loss
    
    def validate(self, val_loader: DataLoader) -> float:
        """Validate the model"""
        self.model.eval()
        total_loss = 0
        num_batches = len(val_loader)
        
        with torch.no_grad():
            for input_ids, target_ids in val_loader:
                input_ids = input_ids.to(self.device)
                target_ids = target_ids.to(self.device)
                
                logits = self.model(input_ids)
                loss = self.loss_fn(logits.view(-1, logits.size(-1)), target_ids.view(-1))
                
                total_loss += loss.item()
        
        avg_loss = total_loss / num_batches
        return avg_loss
    
    def train(self, train_texts: List[str], val_texts: List[str] = None,
              epochs: int = 10, batch_size: int = 4, max_length: int = 512,
              learning_rate: float = 1e-4, save_every: int = 5,
              model_save_path: str = "models/dieai_model.pt"):
        """Main training loop"""
        logger.info(f"Starting training on {self.device}")
        
        # Setup optimizer
        self.setup_optimizer(learning_rate)
        
        # Create datasets
        train_dataset = TextDataset(train_texts, self.tokenizer, max_length)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        
        val_loader = None
        if val_texts:
            val_dataset = TextDataset(val_texts, self.tokenizer, max_length)
            val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
        
        logger.info(f"Training dataset size: {len(train_dataset)}")
        if val_loader:
            logger.info(f"Validation dataset size: {len(val_dataset)}")
        
        # Training loop
        best_val_loss = float('inf')
        
        for epoch in range(1, epochs + 1):
            # Train
            train_loss = self.train_epoch(train_loader, epoch)
            self.train_losses.append(train_loss)
            
            # Validate
            val_loss = None
            if val_loader:
                val_loss = self.validate(val_loader)
                self.val_losses.append(val_loss)
            
            # Log progress
            current_lr = self.optimizer.param_groups[0]['lr']
            self.learning_rates.append(current_lr)
            
            log_msg = f"Epoch {epoch}/{epochs} - Train Loss: {train_loss:.4f}, LR: {current_lr:.2e}"
            if val_loss is not None:
                log_msg += f", Val Loss: {val_loss:.4f}"
            logger.info(log_msg)
            
            # Save model
            if epoch % save_every == 0 or epoch == epochs:
                self.save_checkpoint(model_save_path, epoch, train_loss, val_loss)
            
            # Save best model
            if val_loss is not None and val_loss < best_val_loss:
                best_val_loss = val_loss
                best_model_path = model_save_path.replace('.pt', '_best.pt')
                self.save_checkpoint(best_model_path, epoch, train_loss, val_loss)
        
        logger.info("Training completed!")
        return self.train_losses, self.val_losses
    
    def save_checkpoint(self, path: str, epoch: int, train_loss: float, val_loss: float = None):
        """Save training checkpoint"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'train_loss': train_loss,
            'val_loss': val_loss,
            'train_losses': self.train_losses,
            'val_losses': self.val_losses,
            'learning_rates': self.learning_rates,
            'timestamp': datetime.now().isoformat()
        }
        
        torch.save(checkpoint, path)
        logger.info(f"Checkpoint saved: {path}")
    
    def load_checkpoint(self, path: str):
        """Load training checkpoint"""
        checkpoint = torch.load(path, map_location=self.device)
        
        self.model.load_state_dict(checkpoint['model_state_dict'])
        
        if self.optimizer:
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        
        self.train_losses = checkpoint.get('train_losses', [])
        self.val_losses = checkpoint.get('val_losses', [])
        self.learning_rates = checkpoint.get('learning_rates', [])
        
        logger.info(f"Checkpoint loaded: {path}")
        return checkpoint['epoch']
    
    def generate_sample(self, prompt: str, max_length: int = 100) -> str:
        """Generate a sample text during training"""
        self.model.eval()
        
        with torch.no_grad():
            # Encode prompt
            input_ids = torch.tensor(self.tokenizer.encode(prompt, add_special_tokens=True)).unsqueeze(0).to(self.device)
            
            # Generate
            generated_ids = self.model.generate(input_ids, max_length=max_length)
            
            # Decode
            generated_text = self.tokenizer.decode(generated_ids[0].tolist())
        
        return generated_text

def load_training_data(data_path: str) -> List[str]:
    """Load training data from JSON file"""
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and 'texts' in data:
        return data['texts']
    else:
        raise ValueError("Invalid data format. Expected list of strings or dict with 'texts' key.")

def main():
    """Main training function"""
    # Load configuration
    with open('config/training_config.json', 'r') as f:
        config = json.load(f)
    
    # Load model configuration
    with open('config/model_config.json', 'r') as f:
        model_config = json.load(f)
    
    # Initialize tokenizer
    tokenizer = DieAITokenizer(vocab_size=model_config['vocab_size'])
    
    # Load training data
    train_texts = load_training_data('data/sample_data.json')
    
    # Build vocabulary
    tokenizer.build_vocab_from_corpus(train_texts)
    tokenizer.save_vocab('models/vocab.json')
    
    # Create model
    model = DieAITransformer(
        vocab_size=tokenizer.get_vocab_size(),
        **model_config
    )
    
    # Initialize trainer
    trainer = DieAITrainer(model, tokenizer)
    
    # Split data (80% train, 20% validation)
    split_idx = int(0.8 * len(train_texts))
    train_data = train_texts[:split_idx]
    val_data = train_texts[split_idx:]
    
    # Train model
    trainer.train(
        train_texts=train_data,
        val_texts=val_data,
        **config
    )
    
    # Test generation
    test_prompt = "Hello, how are you?"
    generated = trainer.generate_sample(test_prompt)
    print(f"Generated text: {generated}")

if __name__ == "__main__":
    main()
