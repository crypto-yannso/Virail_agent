from pathlib import Path

# Création du dossier data s'il n'existe pas
data_dir = Path(__file__).parent.parent.parent / "data"
data_dir.mkdir(exist_ok=True) 