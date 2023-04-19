
from recommender.utils import load_model

def test_load_model():
    """Test load model function."""
    model = load_model()
    assert model is not None

