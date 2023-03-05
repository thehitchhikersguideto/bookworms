import pytest 
from pytest_ipynb import Notebook

def test_notebook():
    notebook = Notebook('notebooks/initial_eda.ipynb')
    notebook.run()
    assert notebook.errors == []

