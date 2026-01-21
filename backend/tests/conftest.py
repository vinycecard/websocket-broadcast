import sys
from pathlib import Path

# adiciona o diretório backend/ no PYTHONPATH
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
