a
# ⚽ Football AI Prediction System

A **Python-based GUI application** that predicts football player performance and market value using **Machine Learning models**, and provides interactive **team and match analysis** with animated visualizations.

---

## 📌 Project Overview

This project is a CAI3101 Artificial Intelligence course assignment. It demonstrates the **end-to-end workflow of a machine learning project**, including:

- Data preprocessing and feature engineering
- Training and applying predictive models
- GUI-based visualization of results
- Interactive team and match analysis animations

The goal is to help football managers and analysts **explore player performance, market value, and match strategies** efficiently.

---

## 🛠 Features

### 1. Player Performance Prediction
- Predict goals, assists, and overall performance score based on **current season statistics**.
- Estimate **market value** using trained ML models or fallback heuristic methods.

### 2. Search Player
- Search for a player by name.
- Retrieve detailed statistics from connected CSV datasets.
- Handles missing data and inactive players gracefully.

### 3. Direct Input Prediction
- Enter custom player stats (goals, assists, minutes, age) to predict **next match performance and market value**.

### 4. Team & Match Analysis (Animated Demo)
- Visualizes a football pitch with players and ball movements.
- Demonstrates **possession, counter-attacks, and tactical patterns** with animations.
- Can be expanded with real match data for in-depth tactical analysis.

---

## 💻 Installation

1. Clone the repository:

```bash
git clone https://github.com/<your-username>/football-ai-prediction.git
cd football-ai-prediction

2. Install dependencies:



pip install -r requirements.txt

3. Run the application:



python main.py


---

🗂 Project Structure

football-ai-prediction/
│
├─ main.py                 # Main GUI application
├─ requirements.txt        # Python dependencies
├─ README.md
│
├─ src/
│   ├─ data_loader.py      # Load and combine CSV datasets
│   ├─ search.py           # Player search logic
│   ├─ status_check.py     # Check player activity status
│   ├─ predictor.py        # ML-based performance and market value predictions
│   └─ model_trainer.py    # Model loading and helper functions
│
└─ datasets/
    ├─ players.csv         # Player stats dataset
    └─ teams.csv           # Team and match data (optional)


---

🔧 How to Use

1. Direct Input Tab

Enter goals, assists, minutes played, and age.

Click Predict Performance & Value.

View detailed predictions in the results frame.



2. Search Player Tab

Type the player name in the search box.

Click Search.

If the player exists in the dataset, detailed stats and predictions will be displayed.



3. Team & Match Analysis Tab

View animated visualizations of counter-attacks, possession, and tactical movements.

Expand by connecting real match data from CSVs.





---

📊 Models Used

Random Forest Regressor for predicting market value.

Random Forest Regressor for performance score.

Fallback heuristic calculations if models are unavailable.
