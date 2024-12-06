import pytest
import sys
from pathlib import Path

# Ajout du chemin du projet au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configuration de pytest-asyncio
pytest_plugins = ["pytest_asyncio"]

def pytest_configure(config):
    config.option.asyncio_mode = "auto"