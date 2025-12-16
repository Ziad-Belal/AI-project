# Neural Network & Tree Search Implementation

## Overview

This project now includes:

1. **Neural Network Models** - Multi-layer perceptron (MLP) for predictions
2. **Improved DFS/BFS Tree Structures** - Better organized search algorithms
3. **Enhanced Code Readability** - Clear documentation and structure

## Neural Network Architecture

The neural network implementation (`src/neural_network.py`) uses a Multi-Layer Perceptron (MLP) with:

- **Input Layer**: 4 features (goals, assists, minutes played, age)
- **Hidden Layers**: [64, 32, 16] neurons with ReLU activation
- **Output Layer**: 1 neuron (for regression)
- **Learning Rate**: 0.001
- **Training**: Mini-batch gradient descent with backpropagation

### Features:

- He initialization for weights
- ReLU activation for hidden layers
- Mean Squared Error (MSE) loss function
- Support for validation data during training
- Model saving/loading functionality

## DFS and BFS Tree Structures

The search module (`src/search.py`) now includes:

### TreeNode Class

- Represents individual players in the search tree
- Stores player name, squad, and children (teammates)
- Tracks visited status for traversal

### PlayerSearchTree Class

- Builds a graph where players are nodes
- Edges connect players who are teammates (same squad)
- Provides DFS and BFS traversal methods

### DFS (Depth-First Search)

- Uses **stack** (LIFO - Last In First Out)
- Explores as far as possible along each branch before backtracking
- Good for finding deep relationships

### BFS (Breadth-First Search)

- Uses **queue** (FIFO - First In First Out)
- Explores all nodes at current depth before moving to next level
- Good for finding immediate teammates

## Usage

### Training Models

Train both Random Forest and Neural Network models:

```python
python train_models.py
```

The trainer will:

1. Load data from CSV files and Transfermarkt
2. Split data 80% training / 20% testing
3. Train Random Forest models (saved as `perf_model.pkl`, `value_model.pkl`)
4. Train Neural Network models (saved as `perf_model_nn.pkl`, `value_model_nn.pkl`)

### Using Search Trees

The search functionality automatically uses DFS/BFS trees:

```python
from src.search import PlayerSearchTree, smart_search

# Build search tree from player data
search_tree = PlayerSearchTree(df)

# Find teammates using BFS (immediate teammates first)
teammates = search_tree.find_teammates("Messi", use_bfs=True)

# Or use DFS (explore deeper relationships)
related_players = search_tree.dfs_search("Messi", max_depth=3)

# Smart search uses trees automatically
player = smart_search("teammates of Messi", df)
```

## Code Structure

### Key Files:

1. **`src/neural_network.py`**

   - `NeuralNetwork` class - Main neural network implementation
   - `train_neural_network_models()` - Training function

2. **`src/search.py`**

   - `TreeNode` class - Tree node structure
   - `PlayerSearchTree` class - Tree-based search
   - `DFS()` / `BFS()` - Legacy functions for backward compatibility
   - `smart_search()` - Main search interface

3. **`src/model_trainer.py`**

   - `train_models()` - Trains both RF and NN models
   - `prepare_data()` - Loads and merges data sources

4. **`src/predictor.py`**
   - Automatically loads neural network models if available
   - Falls back to Random Forest if NN models not found

## Model Selection

The predictor automatically selects the best available model:

1. First tries to load Neural Network models
2. Falls back to Random Forest models if NN not available
3. Uses fallback calculations if no models found

## Training Parameters

Neural Network training:

- **Epochs**: 100 (configurable)
- **Batch Size**: 32
- **Learning Rate**: 0.001
- **Architecture**: 4 → [64, 32, 16] → 1

Random Forest training:

- **Estimators**: 100
- **Max Depth**: 10
- **Random State**: 42

## Performance

Both models are evaluated on the test set with:

- **MAE** (Mean Absolute Error)
- **R²** (Coefficient of Determination)

The models are saved separately, allowing you to compare performance and choose the best one for your use case.
