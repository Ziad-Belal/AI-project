"""
Neural Network Model for Football Player Predictions
Implements a Multi-Layer Perceptron (MLP) for performance and market value prediction
"""
import numpy as np
import os
import pickle
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score


class NeuralNetwork:
    """
    Multi-Layer Perceptron Neural Network
    
    Architecture:
    - Input Layer: 4 features (goals, assists, minutes, age)
    - Hidden Layers: Configurable number of layers with configurable neurons
    - Output Layer: 1 neuron (for regression)
    """
    
    def __init__(self, input_size=4, hidden_layers=[64, 32, 16], output_size=1, learning_rate=0.001):
        """
        Initialize the neural network
        
        Args:
            input_size: Number of input features (default: 4)
            hidden_layers: List of neurons per hidden layer (default: [64, 32, 16])
            output_size: Number of output neurons (default: 1)
            learning_rate: Learning rate for gradient descent (default: 0.001)
        """
        self.input_size = input_size
        self.hidden_layers = hidden_layers
        self.output_size = output_size
        self.learning_rate = learning_rate
        
        # Build network architecture
        self.weights = []
        self.biases = []
        
        # Input to first hidden layer
        layer_sizes = [input_size] + hidden_layers + [output_size]
        
        # Initialize weights and biases using He initialization
        for i in range(len(layer_sizes) - 1):
            # He initialization: weights ~ N(0, sqrt(2/n))
            w = np.random.randn(layer_sizes[i], layer_sizes[i+1]) * np.sqrt(2.0 / layer_sizes[i])
            b = np.zeros((1, layer_sizes[i+1]))
            self.weights.append(w)
            self.biases.append(b)
    
    def _sigmoid(self, x):
        """Sigmoid activation function"""
        # Clip values to prevent overflow
        x = np.clip(x, -500, 500)
        return 1 / (1 + np.exp(-x))
    
    def _relu(self, x):
        """ReLU activation function"""
        return np.maximum(0, x)
    
    def _relu_derivative(self, x):
        """Derivative of ReLU"""
        return (x > 0).astype(float)
    
    def _forward_pass(self, X):
        """
        Forward propagation through the network
        
        Args:
            X: Input features (batch_size, input_size)
        
        Returns:
            activations: List of activations for each layer
        """
        activations = [X]
        current_input = X
        
        # Forward through hidden layers
        for i in range(len(self.weights) - 1):
            z = np.dot(current_input, self.weights[i]) + self.biases[i]
            a = self._relu(z)  # ReLU for hidden layers
            activations.append(a)
            current_input = a
        
        # Output layer (no activation for regression, or linear)
        z_output = np.dot(current_input, self.weights[-1]) + self.biases[-1]
        activations.append(z_output)
        
        return activations
    
    def predict(self, X):
        """
        Make predictions using the trained network
        
        Args:
            X: Input features (batch_size, input_size)
        
        Returns:
            predictions: Predicted values
        """
        activations = self._forward_pass(X)
        return activations[-1]
    
    def _backward_pass(self, activations, y_true):
        """
        Backward propagation to compute gradients
        
        Args:
            activations: List of activations from forward pass
            y_true: True target values
        
        Returns:
            weight_gradients: List of weight gradients
            bias_gradients: List of bias gradients
        """
        m = y_true.shape[0]  # Number of samples
        
        # Initialize gradients
        weight_gradients = [np.zeros_like(w) for w in self.weights]
        bias_gradients = [np.zeros_like(b) for b in self.biases]
        
        # Output layer error (MSE derivative)
        output_error = activations[-1] - y_true.reshape(-1, 1)
        delta = output_error / m
        
        # Backpropagate through layers
        for i in range(len(self.weights) - 1, -1, -1):
            # Gradient for weights
            weight_gradients[i] = np.dot(activations[i].T, delta)
            # Gradient for biases
            bias_gradients[i] = np.sum(delta, axis=0, keepdims=True)
            
            # Propagate error to previous layer (if not input layer)
            if i > 0:
                delta = np.dot(delta, self.weights[i].T)
                # Apply ReLU derivative
                delta *= self._relu_derivative(activations[i])
        
        return weight_gradients, bias_gradients
    
    def train(self, X, y, epochs=100, batch_size=32, validation_data=None, verbose=True):
        """
        Train the neural network using mini-batch gradient descent
        
        Args:
            X: Training features (n_samples, input_size)
            y: Training targets (n_samples,)
            epochs: Number of training epochs (default: 100)
            batch_size: Size of mini-batches (default: 32)
            validation_data: Tuple (X_val, y_val) for validation (optional)
            verbose: Whether to print training progress (default: True)
        
        Returns:
            history: Dictionary with training history
        """
        history = {'loss': [], 'val_loss': []}
        n_samples = X.shape[0]
        
        for epoch in range(epochs):
            # Shuffle data
            indices = np.random.permutation(n_samples)
            X_shuffled = X[indices]
            y_shuffled = y[indices]
            
            epoch_loss = 0
            
            # Mini-batch training
            for i in range(0, n_samples, batch_size):
                X_batch = X_shuffled[i:i+batch_size]
                y_batch = y_shuffled[i:i+batch_size]
                
                # Forward pass
                activations = self._forward_pass(X_batch)
                predictions = activations[-1].flatten()
                
                # Compute loss (MSE)
                loss = np.mean((predictions - y_batch) ** 2)
                epoch_loss += loss
                
                # Backward pass
                weight_grads, bias_grads = self._backward_pass(activations, y_batch)
                
                # Update weights and biases
                for j in range(len(self.weights)):
                    self.weights[j] -= self.learning_rate * weight_grads[j]
                    self.biases[j] -= self.learning_rate * bias_grads[j]
            
            epoch_loss /= (n_samples // batch_size + 1)
            history['loss'].append(epoch_loss)
            
            # Validation
            if validation_data is not None:
                X_val, y_val = validation_data
                val_predictions = self.predict(X_val).flatten()
                val_loss = np.mean((val_predictions - y_val) ** 2)
                history['val_loss'].append(val_loss)
                
                if verbose and (epoch + 1) % 10 == 0:
                    print(f"Epoch {epoch+1}/{epochs} - Loss: {epoch_loss:.4f}, Val Loss: {val_loss:.4f}")
            elif verbose and (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch+1}/{epochs} - Loss: {epoch_loss:.4f}")
        
        return history
    
    def save(self, filepath):
        """Save the neural network model to a file"""
        model_data = {
            'weights': self.weights,
            'biases': self.biases,
            'input_size': self.input_size,
            'hidden_layers': self.hidden_layers,
            'output_size': self.output_size,
            'learning_rate': self.learning_rate
        }
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
    
    @classmethod
    def load(cls, filepath):
        """Load a neural network model from a file"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        model = cls(
            input_size=model_data['input_size'],
            hidden_layers=model_data['hidden_layers'],
            output_size=model_data['output_size'],
            learning_rate=model_data['learning_rate']
        )
        model.weights = model_data['weights']
        model.biases = model_data['biases']
        return model


def train_neural_network_models(X_train, y_perf_train, y_value_train, X_test, y_perf_test, y_value_test, 
                                scaler, models_dir, epochs=100, batch_size=32):
    """
    Train neural network models for performance and value prediction
    
    Args:
        X_train: Training features
        y_perf_train: Training performance targets
        y_value_train: Training value targets
        X_test: Test features
        y_perf_test: Test performance targets
        y_value_test: Test value targets
        scaler: StandardScaler fitted to training data
        models_dir: Directory to save models
        epochs: Number of training epochs
        batch_size: Mini-batch size
    
    Returns:
        perf_model: Trained performance prediction model
        value_model: Trained value prediction model
    """
    print("\n" + "="*60)
    print("Training Neural Network Models")
    print("="*60)
    
    # Scale features
    X_train_scaled = scaler.transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Prepare validation data
    val_data_perf = (X_test_scaled, y_perf_test)
    val_data_value = (X_test_scaled, y_value_test)
    
    # Train Performance Model
    print("\nTraining Performance Prediction Neural Network...")
    print(f"Architecture: {X_train.shape[1]} -> [64, 32, 16] -> 1")
    perf_model = NeuralNetwork(
        input_size=X_train.shape[1],
        hidden_layers=[64, 32, 16],
        output_size=1,
        learning_rate=0.001
    )
    perf_history = perf_model.train(
        X_train_scaled, y_perf_train,
        epochs=epochs,
        batch_size=batch_size,
        validation_data=val_data_perf,
        verbose=True
    )
    
    # Evaluate performance model
    perf_pred = perf_model.predict(X_test_scaled).flatten()
    perf_mae = mean_absolute_error(y_perf_test, perf_pred)
    perf_r2 = r2_score(y_perf_test, perf_pred)
    print(f"\nPerformance Model Results:")
    print(f"  MAE: {perf_mae:.3f}, R²: {perf_r2:.3f}")
    
    # Train Value Model
    print("\nTraining Market Value Prediction Neural Network...")
    print(f"Architecture: {X_train.shape[1]} -> [64, 32, 16] -> 1")
    value_model = NeuralNetwork(
        input_size=X_train.shape[1],
        hidden_layers=[64, 32, 16],
        output_size=1,
        learning_rate=0.001
    )
    value_history = value_model.train(
        X_train_scaled, y_value_train,
        epochs=epochs,
        batch_size=batch_size,
        validation_data=val_data_value,
        verbose=True
    )
    
    # Evaluate value model
    value_pred = value_model.predict(X_test_scaled).flatten()
    value_mae = mean_absolute_error(y_value_test, value_pred)
    value_r2 = r2_score(y_value_test, value_pred)
    print(f"\nValue Model Results:")
    print(f"  MAE: ${value_mae:.2f}M, R²: {value_r2:.3f}")
    
    # Save models
    perf_model_path = os.path.join(models_dir, "perf_model_nn.pkl")
    value_model_path = os.path.join(models_dir, "value_model_nn.pkl")
    perf_model.save(perf_model_path)
    value_model.save(value_model_path)
    print(f"\nNeural network models saved to {models_dir}")
    
    return perf_model, value_model

