Football Player Performance Analyzer
Overview

This project is a desktop application that analyzes football player statistics using machine learning.
The application loads data from CSV files, processes the data, trains a clustering model, and provides visualizations that help explain how the model learns.

The main idea is to make the machine learning process understandable by showing a step-by-step animation of the learning phase, rather than only showing the final result.

Objectives

Load and prepare football player datasets.

Train a simple machine learning model (K-Means).

Display player clusters and basic analysis.

Show an animated visualization of how the model learns.

Provide a simple graphical interface for users to interact with the system.

Features

Dataset Handling

Reads CSV files using Pandas.

Checks available columns.

Selects numerical performance features.

Prepares the dataset for machine learning.

Machine Learning

Uses K-Means clustering to group players.

Allows the user to trigger model training from the GUI.

Clusters are displayed after training.

Learning Visualization

Shows how the algorithm moves centroids during training.

Helps the user understand the learning process visually.

Desktop Application (GUI)

Built with Tkinter or PyQt.

Options include:

Load dataset

Train model

Show learning animation

View analysis results

Integration

Connects the dataset, model, animation, and GUI into one working application.

Can be exported as a Windows executable using PyInstaller.

Technologies Used

Python

Pandas

NumPy

Scikit-learn

Matplotlib

Tkinter or PyQt5

PyInstaller

Project Structure
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

How to Run

Install the required packages:

pip install pandas numpy matplotlib scikit-learn pyinstaller


Run the application:

python main.py


To create an executable:

pyinstaller --onefile main.py

Purpose of the Project

The project demonstrates how machine learning models can analyze real-world football data, while also focusing on making the learning process visible and easy to understand.
It is designed to be both practical and educational.

Possible Future Additions

Player comparison mode

More advanced analysis and metrics

Improved animations

Additional model types
