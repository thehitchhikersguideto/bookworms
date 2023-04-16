import sys
from pathlib import Path

# Set the PYTHONPATH to the root directory of your project
root_directory = Path(__file__).resolve().parent
sys.path.append(str(root_directory))

# Import your main script and run it
from backend.recommender import get_recommendations

if __name__ == "__main__":
    get_recommendations()
