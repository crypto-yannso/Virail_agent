import sys
from pathlib import Path

# Ajout du chemin racine au PYTHONPATH
root_dir = Path(__file__).parent.parent.absolute()
sys.path.append(str(root_dir))

from src.database.manager import DatabaseManager

def init_test_db():
    db_path = Path(root_dir) / "data" / "test_oauth.db"
    db_url = f"sqlite:///{db_path}"
    db_manager = DatabaseManager(db_url)
    print(f"Base de données initialisée: {db_path}")

if __name__ == "__main__":
    init_test_db() 