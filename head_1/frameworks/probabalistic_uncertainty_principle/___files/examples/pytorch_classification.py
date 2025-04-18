"""
PyTorch integration example for image classification with uncertainty quantification.

This example demonstrates how to use the PUP framework with PyTorch to:
1. Quantify uncertainty in image classification
2. Defer predictions when confidence is too low
3. Visualize uncertainty in predictions
"""

import numpy as np
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision
import torchvision.transforms as transforms
from typing import Tuple, List, Dict, Any, Optional

# Import PUP components
from ___files.core import BeliefState, ConfidenceExecutor
from ___files.integrations.pytorch import MonteCarloDropout, torch_to_belief_state


# Define a simple CNN with dropout for uncertainty estimation
class UncertaintyAwareCNN(nn.Module):
    """A CNN that can provide uncertainty estimates through MC Dropout."""
    
    def __init__(self, dropout_rate: float = 0.3):
        """
        Initialize the uncertainty-aware CNN.
        
        Args:
            dropout_rate: Dropout probability for uncertainty estimation
        """
        super().__init__()
        self.conv1 = nn.Conv2d(3, 32, 3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, 3, padding=1)
        self.conv3 = nn.Conv2d(64, 128, 3, padding=1)
        
        self.pool = nn.MaxPool2d(2, 2)
        self.dropout = nn.Dropout(dropout_rate)
        
        # 4x4 feature maps after 3 pooling operations on 32x32 input
        self.fc1 = nn.Linear(128 * 4 * 4, 512)
        self.fc2 = nn.Linear(512, 10)  # 10 classes for CIFAR-10
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass with dropout enabled for uncertainty estimation."""
        x = self.pool(F.relu(self.conv1(x)))
        x = self.dropout(x)
        
        x = self.pool(F.relu(self.conv2(x)))
        x = self.dropout(x)
        
        x = self.pool(F.relu(self.conv3(x)))
        x = self.dropout(x)
        
        x = x.view(-1, 128 * 4 * 4)
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        
        x = self.fc2(x)
        return x


def load_data() -> Tuple[torch.utils.data.DataLoader, torch.utils.data.DataLoader]:
    """
    Load CIFAR-10 dataset for training and testing.
    
    Returns:
        Tuple of (train_loader, test_loader)
    """
    # Data augmentation and normalization for training
    transform_train = transforms.Compose([
        transforms.RandomCrop(32, padding=4),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
    ])
    
    # Just normalization for testing
    transform_test = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
    ])
    
    # Load CIFAR-10 dataset
    trainset = torchvision.datasets.CIFAR10(
        root='./data', train=True, download=True, transform=transform_train
    )
    trainloader = torch.utils.data.DataLoader(
        trainset, batch_size=128, shuffle=True, num_workers=2
    )
    
    testset = torchvision.datasets.CIFAR10(
        root='./data', train=False, download=True, transform=transform_test
    )
    testloader = torch.utils.data.DataLoader(
        testset, batch_size=100, shuffle=False, num_workers=2
    )
    
    return trainloader, testloader


def train_model(model: nn.Module, trainloader: torch.utils.data.DataLoader, epochs: int = 5) -> nn.Module:
    """
    Train the model on CIFAR-10.
    
    Args:
        model: The model to train
        trainloader: DataLoader for training data
        epochs: Number of training epochs
        
    Returns:
        Trained model
    """
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model.to(device)
    
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    
    print(f"Training on {device}...")
    
    for epoch in range(epochs):
        running_loss = 0.0
        for i, data in enumerate(trainloader, 0):
            inputs, labels = data[0].to(device), data[1].to(device)
            
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            if i % 100 == 99:
                print(f'[Epoch {epoch + 1}, Batch {i + 1}] loss: {running_loss / 100:.3f}')
                running_loss = 0.0
    
    print('Finished Training')
    return model


def evaluate_with_uncertainty(
    model: nn.Module,
    testloader: torch.utils.data.DataLoader,
    confidence_threshold: float = 0.8,
    n_samples: int = 20
) -> Dict[str, float]:
    """
    Evaluate model on test data with uncertainty estimation.
    
    Args:
        model: The model to evaluate
        testloader: DataLoader for test data
        confidence_threshold: Confidence threshold for making predictions
        n_samples: Number of Monte Carlo forward passes
        
    Returns:
        Dictionary with evaluation metrics
    """
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model.to(device)
    
    # Wrap model with MC Dropout
    mc_model = MonteCarloDropout(model)
    
    # Create confidence executor
    executor = ConfidenceExecutor(threshold=confidence_threshold)
    
    # Prepare metrics
    total = 0
    correct = 0
    deferred = 0
    confidences = []
    
    # CIFAR-10 classes
    classes = ('plane', 'car', 'bird', 'cat', 'deer', 
               'dog', 'frog', 'horse', 'ship', 'truck')
    
    # Function to execute when confidence is sufficient
    def make_prediction(mean):
        return int(np.argmax(mean))
    
    # Evaluate on test data
    with torch.no_grad():
        for data in testloader:
            images, labels = data[0].to(device), data[1].to(device)
            
            # Get predictions with uncertainty
            belief_state = mc_model.predict_belief_state(images, n_samples)
            
            # Make predictions for each sample based on confidence
            for i in range(len(labels)):
                # Extract individual belief state
                sample_belief = BeliefState(
                    mean=belief_state.mean[i],
                    variance=belief_state.variance[i],
                    epistemic=True
                )
                
                # Execute prediction if confidence is sufficient
                result = executor.execute(sample_belief, make_prediction)
                
                # Record metrics
                total += 1
                confidences.append(float(sample_belief.confidence().mean()))
                
                if isinstance(result, dict) and result.get('action') == 'deferred':
                    deferred += 1
                else:
                    if result == labels[i].item():
                        correct += 1
    
    # Calculate metrics
    accuracy = correct / (total - deferred) if total - deferred > 0 else 0
    deferral_rate = deferred / total
    avg_confidence = np.mean(confidences)
    
    metrics = {
        'accuracy': accuracy,
        'deferral_rate': deferral_rate,
        'avg_confidence': avg_confidence,
        'total_samples': total,
        'correct': correct,
        'deferred': deferred
    }
    
    print(f"Evaluation results:")
    print(f"  Accuracy: {accuracy:.4f}")
    print(f"  Deferral rate: {deferral_rate:.4f}")
    print(f"  Average confidence: {avg_confidence:.4f}")
    print(f"  Total samples: {total}")
    print(f"  Correct predictions: {correct}")
    print(f"  Deferred predictions: {deferred}")
    
    return metrics


def visualize_uncertainties(
    model: nn.Module,
    testloader: torch.utils.data.DataLoader,
    n_samples: int = 20,
    n_examples: int = 5
):
    """
    Visualize uncertainties in predictions.
    
    Args:
        model: The model to visualize
        testloader: DataLoader for test data
        n_samples: Number of Monte Carlo forward passes
        n_examples: Number of examples to visualize
    """
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model.to(device)
    
    # Wrap model with MC Dropout
    mc_model = MonteCarloDropout(model)
    
    # CIFAR-10 classes
    classes = ('plane', 'car', 'bird', 'cat', 'deer', 
               'dog', 'frog', 'horse', 'ship', 'truck')
    
    # Get a batch of test images
    dataiter = iter(testloader)
    images, labels = next(dataiter)
    images, labels = images.to(device), labels.to(device)
    
    # Plot n_examples images with their uncertainties
    plt.figure(figsize=(15, 3 * n_examples))
    
    for i in range(n_examples):
        # Get predictions with uncertainty for single image
        image = images[i:i+1]
        belief_state = mc_model.predict_belief_state(image, n_samples)
        
        # Convert to probabilities
        probs = F.softmax(torch.tensor(belief_state.mean[0]), dim=0).numpy()
        uncertainties = belief_state.variance[0]
        confidences = belief_state.confidence()[0]
        
        # Get top prediction
        pred_class = np.argmax(probs)
        true_class = labels[i].item()
        
        # Plot the image
        plt.subplot(n_examples, 3, i*3 + 1)
        img = image[0].cpu().numpy().transpose((1, 2, 0))
        img = img * 0.5 + 0.5  # Unnormalize
        plt.imshow(img)
        plt.title(f"True: {classes[true_class]}\nPred: {classes[pred_class]}")
        plt.axis('off')
        
        # Plot the class probabilities
        plt.subplot(n_examples, 3, i*3 + 2)
        plt.bar(range(10), probs, yerr=np.sqrt(uncertainties), capsize=4)
        plt.xticks(range(10), classes, rotation=45)
        plt.title('Class Probabilities with Uncertainty')
        plt.grid(alpha=0.3)
        
        # Plot the uncertainties
        plt.subplot(n_examples, 3, i*3 + 3)
        plt.bar(range(10), uncertainties)
        plt.xticks(range(10), classes, rotation=45)
        plt.title('Uncertainty by Class')
        plt.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("classification_uncertainty.png")
    print("Visualization saved as 'classification_uncertainty.png'")
    plt.show()


def main():
    """Run the PyTorch integration example."""
    print("PUP Framework - PyTorch Integration Example")
    print("===========================================")
    
    # Set random seeds for reproducibility
    torch.manual_seed(42)
    np.random.seed(42)
    
    # Load data
    print("\n1. Loading CIFAR-10 dataset...")
    trainloader, testloader = load_data()
    
    # Create and train the model
    print("\n2. Creating and training the model...")
    model = UncertaintyAwareCNN(dropout_rate=0.3)
    
    # Check if pre-trained model exists
    try:
        model.load_state_dict(torch.load('uncertainty_cnn.pth'))
        print("Loaded pre-trained model")
    except:
        print("Training new model...")
        model = train_model(model, trainloader, epochs=5)
        torch.save(model.state_dict(), 'uncertainty_cnn.pth')
    
    # Evaluate with uncertainty
    print("\n3. Evaluating with uncertainty quantification...")
    metrics = evaluate_with_uncertainty(
        model, testloader, confidence_threshold=0.8, n_samples=20
    )
    
    # Visualize uncertainties
    print("\n4. Visualizing prediction uncertainties...")
    visualize_uncertainties(model, testloader, n_samples=20, n_examples=5)


if __name__ == "__main__":
    main()