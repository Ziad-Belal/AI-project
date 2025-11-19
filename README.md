Football Player Performance Analyzer
An interactive machine learning desktop application with real-time learning visualization.
📌 Project Overview

This application analyzes real football player statistics using machine learning and visualizes how the model “learns” using an interactive animation.

Users can:

Load player data from CSV files

Train a machine learning model (K-Means clustering)

Watch a simplified animation of the training process

View clusters, graphs, and player performance insights

Interact with everything through a clean desktop UI

The project turns raw football statistics into an intelligent and visual experience.

📂 Features
✅ 1. Dataset Handling

Load CSV files using Pandas

Inspect columns and data types

Select meaningful player performance metrics

Automatically clean and preprocess data

✅ 2. Machine Learning Model

K-Means clustering

Groups players based on performance features

Shows how players are similar or different

Real-time visualization of how centroids move during training

✅ 3. Learning Animation

Matplotlib animated visualization

Shows points entering clusters

Updates centroids step-by-step

Demonstrates the “learning” process in a simple, visual way

✅ 4. Desktop GUI

Built using Tkinter / PyQt

Buttons for:

Load Dataset

Train Model

Show Animation

Analyze Player

Results displayed inside the app

✅ 5. Integration & Output

Combines ML + animations + UI

Generates visual insights about players

Can be exported as a Windows .exe

🛠️ Technologies Used

Python

Pandas → data loading & cleaning

NumPy → numeric operations

Scikit-learn (sklearn) → K-Means model

Matplotlib → graphs & animations

Tkinter / PyQt5 → GUI frontend

PyInstaller → export as .exe

📁 Project Structure
AI-Project/
│
├── data/
│   ├── All_Players.csv
│   └── Season.csv
│
├── src/
│   ├── data_loader.py
│   ├── model.py
│   ├── animation.py
│   ├── gui.py
│   └── main.py
│
├── README.md
└── requirements.txt

🚀 How to Run the Project

Install required libraries:

pip install pandas numpy matplotlib scikit-learn pyinstaller


Run the main application:

python main.py


To generate an EXE:

pyinstaller --onefile main.py

🎯 Project Goal

The goal of this project is to simulate how machine learning learns, in a way that is simple, fun, and visually impressive—making it perfect for presentations, competitions, and graduation projects.

📌 Future Improvements

Add player comparison tool

Add prediction models (e.g., expected rating)

Add team builder based on cluster similarity

Add advanced visualizations and dashboards
