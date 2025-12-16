import sys
import os

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
        print("✅ Model training completed!")
        print("Run main.py to use the prediction system.")
        print("=" * 60)
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ Error: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        sys.exit(1)
