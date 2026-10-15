"""Test configuration: keep the import-time database outside the repository."""
import os
import tempfile
from pathlib import Path

_bootstrap_db = Path(tempfile.gettempdir()) / f"tiger_pathway_pytest_bootstrap_{os.getpid()}.db"
os.environ.setdefault("TIGER_DB_PATH", str(_bootstrap_db))
