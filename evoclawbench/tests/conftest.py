import sys
from pathlib import Path

# Add scripts/ to path so we can import the modules
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
