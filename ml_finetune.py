#!/usr/bin/env python
# -*- coding: utf-8 -*-
""""""

import os
import sys
import json
import time
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import Counter

import torch
import torch.nn as nn
import torch.optim as optim
from torch.cuda.amp import autocast, GradScaler
from torch.utils.data import DataLoader, Dataset, random_split
import torchvision.transforms as transforms
import torchvision.models as models
from sklearn.metrics import f1_score, confusion_matrix, classification_report, roc_auc_score
import matplotlib.pyplot as plt
import seaborn as sns

# Output messages for terminal display

MESSAGES = {
    'start_training': 'EfficientNetB0 Fine-tuning starting...',
    'loading_data': 'Loading data...',
    'data_loaded': 'Data loaded successfully',
    'initializing_model': 'Initializing model...',
    'model_ready': 'Model ready',
    'training_epoch': 'Epoch {epoch}/{total_epochs} - {phase}',
    'warmup_notice': 'Training classifier only (2 epoch warmup)',
    'unfreezing': 'Unfreezing all layers (end-to-end training)',
    'training_batch': '   Batch {batch}/{total_batches}',
    'training_loss': '   Training loss: {loss:.4f}',
    'validation': '   Accuracy: {acc:.2f}% | F1-Score: {f1:.4f}',
    'best_model': 'Best model! Accuracy: {acc:.2f}% (saved)',
    'early_stopping': 'Early stopping - no improvement ({patience} epochs)',
    'training_complete': 'Training complete!',
    'testing': 'Evaluating test set...',
    'model_saved': 'Best model saved: {path}',
    'test_results': 'Test Set Results',
    'test_accuracy': '   Accuracy: {acc:.2f}%',
    'test_f1': '   F1-Score: {f1:.4f}',
    'test_auc': '   AUC-ROC: {auc:.4f}',
    'class_labels': '   Classes: 0=Normal, 1=Pneumonia',
    'training_summary': 'Training Summary',
    'total_epochs': '   Total Epochs: {epochs}',
    'best_epoch': '   Best Epoch: {epoch} (Accuracy: {acc:.2f}%)',
    'total_time': '   Total time: {time:.2f} minutes',
    'error': 'Error: {error}',
    'class_distribution': 'Class Distribution',
    'train_distribution': '   Training: Normal={normal}, Pneumonia={pneumonia}',
    'val_distribution': '   Validation: Normal={normal}, Pneumonia={pneumonia}',
    'learning_rate': 'Learning rate: {lr:.6f}',
    'epoch_summary': '   Epoch {epoch}: Loss={loss:.4f}, Val_Acc={acc:.2f}%, F1={f1:.4f}',
}

# Custom PyTorch Dataset for loading Chest X-Ray images

class ChestXRayDataset(Dataset):
    """
    Chest X-Ray Dataset from Kaggle Paul Mooney
    Loads images from NORMAL and PNEUMONIA subdirectories
    """
    def __init__(self, data_dir, transform=None):
        """
        Initialize dataset with directory containing NORMAL and PNEUMONIA folders
        """
        self.data_dir = Path(data_dir)
        self.transform = transform
        self.images = []
        self.labels = []
        
        # Normal class (label 0)
        normal_dir = self.data_dir / 'NORMAL'
        if normal_dir.exists():
            for img_path in normal_dir.glob('*.jpeg'):
                self.images.append(str(img_path))
                self.labels.append(0)
        
        # Pneumonia class (label 1)
        pneumonia_dir = self.data_dir / 'PNEUMONIA'
        if pneumonia_dir.exists():
            for img_path in pneumonia_dir.glob('*.jpeg'):
                self.images.append(str(img_path))
                self.labels.append(1)
    
    def __len__(self):
        return len(self.images)
    
    def __getitem__(self, idx):
        from PIL import Image
        
        image = Image.open(self.images[idx]).convert('RGB')
        label = self.labels[idx]
        
        if self.transform:
            image = self.transform(image)
        
        return image, label

# ============================================================================
# Class Weights Calculator
# ============================================================================

def calculate_class_weights(dataset):
    """
    Calculate class weights to handle severe class imbalance
    """
    labels = np.array(dataset.labels)
    class_counts = Counter(labels)
    
    total = len(labels)
    num_classes = len(class_counts)
    
    # Formula: weight = (total / (num_classes * class_count))
    weights = torch.tensor(
        [total / (num_classes * class_counts[i]) for i in range(num_classes)],
        dtype=torch.float32
    )
    
    # Normalize class weights
    weights = weights / weights.sum() * num_classes
    
    return weights

# ============================================================================
# Data Augmentation Pipeline
# ============================================================================

def get_transforms():
    """
    Create data augmentation pipelines for training and validation
    """
    
    # ImageNet normalization statistics
    normalize = transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
    
    # Training - Heavy augmentation to prevent overfitting
    train_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomRotation(degrees=20),
        transforms.RandomAffine(degrees=0, translate=(0.1, 0.1), scale=(0.9, 1.1)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.3),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
        transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),
        transforms.GaussianBlur(kernel_size=3, sigma=(0.1, 2.0)),
        transforms.RandomInvert(p=0.1),
        transforms.ToTensor(),
        normalize
    ])
    
    # Validation/Test - Standard transforms without augmentation
    val_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        normalize
    ])
    
    return train_transforms, val_transforms

# ============================================================================
# Model Architecture
# ============================================================================

def create_model(num_classes=2, freeze_backbone=True):
    """
    Create EfficientNetB0 model with custom 2-class classifier
    """
    # Load pretrained EfficientNetB0 from ImageNet
    model = models.efficientnet_b0(pretrained=True)
    
    # Freeze backbone for warmup phase to preserve ImageNet weights
    if freeze_backbone:
        for param in model.features.parameters():
            param.requires_grad = False
    
    # Replace classifier for 2-class pneumonia detection
    num_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.5),
        nn.Linear(num_features, 256),
        nn.BatchNorm1d(256),
        nn.ReLU(inplace=True),
        nn.Dropout(p=0.3),
        nn.Linear(256, num_classes)
    )
    
    return model

def unfreeze_model(model):
    """
    Unfreeze all layers for end-to-end fine-tuning
    """
    for param in model.parameters():
        param.requires_grad = True

# ============================================================================
# Training & Validation Functions
# ============================================================================

def train_epoch(model, dataloader, criterion, optimizer, scaler, device):
    """
    Train model for one epoch with automatic mixed precision
    """
    model.train()
    total_loss = 0.0
    correct = 0
    total = 0
    all_preds = []
    all_labels = []
    
    for batch_idx, (images, labels) in enumerate(dataloader):
        images, labels = images.to(device), labels.to(device)
        
        optimizer.zero_grad()
        
        # Automatic Mixed Precision for speed and memory efficiency
        with autocast():
            outputs = model(images)
            loss = criterion(outputs, labels)
        
        # Backward pass
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()
        
        # Track metrics
        total_loss += loss.item()
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()
        
        all_preds.extend(predicted.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())
        
        # Print progress
        if (batch_idx + 1) % 10 == 0:
            print(f"   {MESSAGES['training_batch'].format(batch_idx=batch_idx+1, total_batches=len(dataloader))}")
    
    accuracy = 100.0 * correct / total
    avg_loss = total_loss / len(dataloader)
    f1 = f1_score(all_labels, all_preds, zero_division=0)
    
    return avg_loss, accuracy, f1

def validate(model, dataloader, criterion, device):
    """
    Validate model on validation set
    """
    model.eval()
    total_loss = 0.0
    correct = 0
    total = 0
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for images, labels in dataloader:
            images, labels = images.to(device), labels.to(device)
            
            with autocast():
                outputs = model(images)
                loss = criterion(outputs, labels)
            
            total_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    
    accuracy = 100.0 * correct / total
    avg_loss = total_loss / len(dataloader)
    f1 = f1_score(all_labels, all_preds, zero_division=0)
    
    return avg_loss, accuracy, f1, all_preds, all_labels

def test(model, dataloader, device):
    """
    Evaluate model on test set
    """
    model.eval()
    correct = 0
    total = 0
    all_preds = []
    all_labels = []
    all_probs = []
    
    with torch.no_grad():
        for images, labels in dataloader:
            images, labels = images.to(device), labels.to(device)
            
            with autocast():
                outputs = model(images)
            
            # Get class probabilities
            probs = torch.softmax(outputs, dim=1)
            _, predicted = outputs.max(1)
            
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            all_probs.extend(probs[:, 1].cpu().numpy())
    
    accuracy = 100.0 * correct / total
    f1 = f1_score(all_labels, all_preds, zero_division=0)
    auc = roc_auc_score(all_labels, all_probs)
    
    return accuracy, f1, auc, all_preds, all_labels

# ============================================================================
# Early Stopping Class
# ============================================================================

class EarlyStopping:
    """
    Early stopping mechanism to prevent overfitting
    """
    def __init__(self, patience=7, verbose=False, delta=0):
        self.patience = patience
        self.verbose = verbose
        self.delta = delta
        self.counter = 0
        self.best_score = None
        self.best_epoch = None
        self.early_stop = False
    
    def __call__(self, val_loss, epoch):
        score = -val_loss
        
        if self.best_score is None:
            self.best_score = score
            self.best_epoch = epoch
        elif score < self.best_score + self.delta:
            self.counter += 1
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            self.best_score = score
            self.best_epoch = epoch
            self.counter = 0

# Main training orchestration
def main():
    """
    Main training pipeline with all phases
    """
    
    # Hyperparameters
    BATCH_SIZE = 32
    NUM_EPOCHS = 50
    LEARNING_RATE = 1e-3
    DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    SEED = 42
    
    # Set random seeds for reproducibility
    torch.manual_seed(SEED)
    np.random.seed(SEED)
    
    print(f"\n{MESSAGES['start_training']}\n")
    print(f"Device: {DEVICE}")
    print(f"Batch Size: {BATCH_SIZE}")
    print(f"Total Epochs: {NUM_EPOCHS}\n")
    
    
    # Kaggle dataset paths
    BASE_DIR = Path('/kaggle/input/datasets/paultimothymooney/chest-xray-pneumonia/chest_xray/chest_xray')
    SAVE_DIR = Path('/kaggle/working')
    SAVE_DIR.mkdir(exist_ok=True)
    
    # Phase 1: Load and prepare data
    print(f"{MESSAGES['loading_data']}\n")
    
    train_transform, val_transform = get_transforms()
    
    # Load full training dataset
    full_train_dataset = ChestXRayDataset(BASE_DIR / 'train', transform=train_transform)
    
    # Create 90/10 train/validation split from training data
    train_size = int(0.9 * len(full_train_dataset))
    val_size = len(full_train_dataset) - train_size
    train_dataset, val_dataset = random_split(
        full_train_dataset,
        [train_size, val_size],
        generator=torch.Generator().manual_seed(SEED)
    )
    
    # Apply validation transform to validation split
    val_dataset.dataset.transform = val_transform
    
    # Load test dataset from test folder
    test_dataset = ChestXRayDataset(BASE_DIR / 'test', transform=val_transform)
    
    # Calculate class distribution
    train_labels = train_dataset.dataset.labels
    train_indices = train_dataset.indices
    train_normal = sum(1 for i in train_indices if train_labels[i] == 0)
    train_pneumonia = sum(1 for i in train_indices if train_labels[i] == 1)
    
    val_labels = val_dataset.dataset.labels
    val_indices = val_dataset.indices
    val_normal = sum(1 for i in val_indices if val_labels[i] == 0)
    val_pneumonia = sum(1 for i in val_indices if val_labels[i] == 1)
    
    print(f"{MESSAGES['data_loaded']}")
    print(f"{MESSAGES['class_distribution']}")
    print(f"{MESSAGES['train_distribution'].format(normal=train_normal, pneumonia=train_pneumonia)}")
    print(f"{MESSAGES['val_distribution'].format(normal=val_normal, pneumonia=val_pneumonia)}\n")
    
    # DataLoaders
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)
    
    # Phase 2: Initialize model
    print(f"{MESSAGES['initializing_model']}\n")
    
    model = create_model(num_classes=2, freeze_backbone=True).to(DEVICE)
    print(f"{MESSAGES['model_ready']}\n")
    
    # Calculate class weights to handle imbalance
    class_weights = calculate_class_weights(train_dataset).to(DEVICE)
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    
    # Optimizer
    optimizer = optim.AdamW(model.parameters(), lr=LEARNING_RATE, weight_decay=1e-5)
    
    # LR Scheduler
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='max', factor=0.5, patience=3, verbose=True, min_lr=1e-6
    )
    
    # AMP Scaler
    scaler = GradScaler()
    
    # Early Stopping
    early_stopping = EarlyStopping(patience=7, verbose=True)
    
    # Phase 3: Start training loop
    best_val_acc = 0.0
    best_epoch = 0
    history = {'train_loss': [], 'val_loss': [], 'val_acc': [], 'val_f1': []}
    
    start_time = time.time()
    
    for epoch in range(NUM_EPOCHS):
        # Warmup phase: First 2 epochs train classifier only
        if epoch == 2:
            print(f"\n{MESSAGES['unfreezing']}\n")
            unfreeze_model(model)
            # Use reduced learning rate for backbone
            for param_group in optimizer.param_groups:
                param_group['lr'] = LEARNING_RATE / 10
        
        # Warmup کے دوران
        if epoch < 2:
            print(f"{MESSAGES['warmup_notice']}")
        
        print(f"{MESSAGES['training_epoch'].format(epoch=epoch+1, total_epochs=NUM_EPOCHS, phase='تربیت')}")
        
        # تربیت کریں
        train_loss, train_acc, train_f1 = train_epoch(
            model, train_loader, criterion, optimizer, scaler, DEVICE
        )
        
        print(f"\n   Training loss: {train_loss:.4f}")
        
        # تصدیق کریں
        print(f"{MESSAGES['training_epoch'].format(epoch=epoch+1, total_epochs=NUM_EPOCHS, phase='تصدیق')}")
        val_loss, val_acc, val_f1, _, _ = validate(model, val_loader, criterion, DEVICE)
        
        print(f"{MESSAGES['validation'].format(acc=val_acc, f1=val_f1)}\n")
        
        # ہسٹری میں شامل کریں
        history['train_loss'].append(train_loss)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)
        history['val_f1'].append(val_f1)
        
        # بہترین ماڈل محفوظ کریں
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_epoch = epoch + 1
            print(f"{MESSAGES['best_model'].format(acc=val_acc)}\n")
            
            # ماڈل محفوظ کریں
            model_path = SAVE_DIR / 'best_pneumonia_model.pth'
            torch.save(model.state_dict(), str(model_path))
            print(f"{MESSAGES['model_saved'].format(path=model_path)}\n")
        
        # LR Scheduler اپ ڈیٹ کریں
        scheduler.step(val_acc)
        
        # جلدی روکنے چیک کریں
        early_stopping(val_loss, epoch + 1)
        if early_stopping.early_stop:
            print(f"\n{MESSAGES['early_stopping'].format(patience=early_stopping.patience)}\n")
            break
        
        print(f"{MESSAGES['epoch_summary'].format(epoch=epoch+1, loss=train_loss, acc=val_acc, f1=val_f1)}\n")
    
        # Phase 4: Test set evaluation
    print(f"\n{MESSAGES['testing']}")
    print(f"{MESSAGES['test_results']}\n")
    
    # Load best model for final evaluation
    model_path = SAVE_DIR / 'best_pneumonia_model.pth'
    model.load_state_dict(torch.load(str(model_path)))
    
    test_acc, test_f1, test_auc, test_preds, test_labels = test(model, test_loader, DEVICE)
    
    print(f"{MESSAGES['test_accuracy'].format(acc=test_acc)}")
    print(f"{MESSAGES['test_f1'].format(f1=test_f1)}")
    print(f"{MESSAGES['test_auc'].format(auc=test_auc)}")
    print(f"{MESSAGES['class_labels']}\n")
    
    
    # Phase 5: Training summary
    elapsed_time = (time.time() - start_time) / 60  # منٹوں میں
    
    print(f"{MESSAGES['training_summary']}")
    print(f"{MESSAGES['total_epochs'].format(epochs=epoch+1)}")
    print(f"{MESSAGES['best_epoch'].format(epoch=best_epoch, acc=best_val_acc)}")
    print(f"{MESSAGES['total_time'].format(time=elapsed_time)}\n")
    
    # ہسٹری محفوظ کریں
    history_path = SAVE_DIR / 'training_history.json'
    history_dict = {
        'train_loss': history['train_loss'],
        'val_loss': history['val_loss'],
        'val_acc': history['val_acc'],
        'val_f1': history['val_f1'],
        'best_epoch': best_epoch,
        'best_val_acc': best_val_acc,
        'test_accuracy': test_acc,
        'test_f1': test_f1,
        'test_auc': test_auc,
        'total_epochs_trained': epoch + 1,
        'training_time_minutes': elapsed_time
    }
    
    with open(str(history_path), 'w') as f:
        json.dump(history_dict, f, indent=4)
    
    print("Training and testing complete!")
    print("Model and history saved\n")
    
    # Phase 6: Generate training visualization
    try:
        fig, axes = plt.subplots(1, 2, figsize=(12, 4))
        
        # Loss Curve
        axes[0].plot(history['train_loss'], label='ٹریننگ', linewidth=2)
        axes[0].plot(history['val_loss'], label='تصدیق', linewidth=2)
        axes[0].set_xlabel('Epoch')
        axes[0].set_ylabel('Loss')
        axes[0].set_title('نقصان (Loss)')
        axes[0].legend()
        axes[0].grid(True)
        
        # Accuracy Curve
        axes[1].plot(history['val_acc'], label='درستگی', linewidth=2)
        axes[1].plot(history['val_f1'], label='F1-Score', linewidth=2)
        axes[1].set_xlabel('Epoch')
        axes[1].set_ylabel('Score')
        axes[1].set_title('درستگی اور F1-Score')
        axes[1].legend()
        axes[1].grid(True)
        
        plt.tight_layout()
        curves_path = SAVE_DIR / 'training_curves.png'
        plt.savefig(str(curves_path), dpi=100)
        print(f"Training curves محفوظ ہیں: {curves_path}\n")
    except Exception as e:
        print(f"⚠️  Curves بنانے میں خرابی: {e}\n")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n{MESSAGES['error'].format(error=str(e))}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)

