import sys
from pathlib import Path

# Ajout du chemin racine au PYTHONPATH
root_dir = Path(__file__).parent.parent.absolute()
sys.path.append(str(root_dir))

# Référence au test existant 