#!/usr/bin/env python3
"""
Script to train ML models for football player prediction
Run this script first to train the models before using the GUI
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.model_trainer import train_models

if __name__ == "__main__":
    print("=" * 60)
    print("Football AI - Model Training")
    print("=" * 60)
    print()
    
    try:
        train_models()
        print()
        print("=" * 60)
        print("✅ Model training completed successfully!")
        print("You can now run main.py to use the prediction system.")
        print("=" * 60)
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ Error during training: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        sys.exit(1)

