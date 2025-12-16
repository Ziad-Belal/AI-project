# Football AI Prediction System

Simple machine learning app to predict football player performance and market value.

## Quick Start

1. **Activate virtual environment:**

   ```bash
   source venv/bin/activate
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Train models (first time only):**

   ```bash
   python train_models.py
   ```

4. **Run the app:**
   ```bash
   python main.py
   ```

## How to Use

- **Direct Input Tab**: Enter goals, assists, minutes, and age to get predictions
- **Search Player Tab**: Search for a player by name to get their predictions

## Files

- `main.py` - Main GUI application
- `train_models.py` - Train ML models
- `src/` - Source code
  - `model_trainer.py` - Train Random Forest models
  - `predictor.py` - Make predictions
  - `data_loader.py` - Load CSV data
  - `search.py` - Search players (uses DFS/BFS)
  - `ui_components.py` - GUI components

## Data

Place `All_Players.csv` and `Season.csv` in the `data/` folder.
