# ⚽ Football AI Prediction System

A machine learning-powered application that predicts football player performance and market value based on goals, assists, minutes played, and age.

## Features

- **Direct Input Prediction**: Enter player statistics directly (goals, assists, minutes played, age) to get predictions
- **Player Search**: Search for players in the database and get predictions
- **ML-Powered**: Uses Random Forest models trained on historical player data
- **Next Match Prediction**: Predicts goals and assists for the next match
- **Market Value Estimation**: Estimates transfer market value in millions

## Setup

1. **Create and activate the virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Linux/Mac
   # or
   venv\Scripts\activate  # On Windows
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Train the ML models** (first time only):
   ```bash
   python train_models.py
   ```
   This will train the models using the CSV data and save them in the `models/` directory.

4. **Run the application**:
   ```bash
   python main.py
   ```

## Usage

### Direct Input Mode
1. Click on the "📊 Direct Input" tab
2. Enter:
   - **Goals**: Number of goals scored
   - **Assists**: Number of assists
   - **Minutes Played**: Total minutes played in the season
   - **Age**: Player's age (16-50)
3. Click "🎯 Predict Performance & Value"
4. View the predictions for next match performance and market value

### Search Player Mode
1. Click on the "🔍 Search Player" tab
2. Enter a player name (e.g., "Messi", "Ronaldo", "Mbappé")
3. Click "🔍 Search"
4. View the player's statistics and predictions

## Requirements

All dependencies are listed in `requirements.txt`. Main packages:
- customtkinter (GUI framework)
- pandas (data manipulation)
- numpy (numerical computing)
- scikit-learn (machine learning models)
- matplotlib & seaborn (visualization)
- joblib (model serialization)

Install all dependencies with:
```bash
pip install -r requirements.txt
```

## Data

The system uses two CSV files:
- `data/All_Players.csv`: Historical player data
- `data/Season.csv`: Season-specific player data

## Model Details

- **Performance Model**: Random Forest Regressor predicting next match contribution
- **Value Model**: Random Forest Regressor predicting market value
- **Features**: Goals, Assists, Minutes Played, Age
- **Training**: Models are trained on combined historical data with synthetic targets based on performance patterns

## Notes

- Models are automatically loaded when the application starts
- If models are not found, the system uses fallback prediction methods
- First run requires training the models with `train_models.py`
